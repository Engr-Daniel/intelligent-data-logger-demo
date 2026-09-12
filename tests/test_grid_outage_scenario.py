from __future__ import annotations

from copy import deepcopy
import pandas as pd

from src.analytics.grid_events import diagnose_grid_outage
from src.datacontext.context import load_installation_config, load_schema
from src.datacontext.validation import validate_telemetry
from src.evaluation.m6_runner import run_m6_evaluation
from src.generator.simulate import simulate
from src.reasoning.agent import fallback_answer
from src.reasoning.tools import execute_tool, load_demo_context


def _measurements(result):
    return {item["name"]: item.get("value") for item in result.get("measurements", [])}


def test_required_scenario_6_is_generated_before_dispatch_and_physically_balanced():
    cfg = load_installation_config()
    df, gt = simulate(cfg)
    events = {event["event_type"]: event for event in gt["events"]}
    assert len(events) == 6
    assert "grid_outage_islanding" in events

    truth = events["grid_outage_islanding"]
    start, end = pd.Timestamp(truth["start"]), pd.Timestamp(truth["end"])
    event = df[(df["timestamp"] >= start) & (df["timestamp"] < end)]
    assert len(event) == 12
    assert event["grid_available"].eq(False).all()
    assert event["grid_import_w"].eq(0).all()
    assert event["grid_export_w"].eq(0).all()
    assert event["inverter_operating_state"].eq("islanded").all()
    assert event["battery_soc_pct"].iloc[-1] < event["battery_soc_pct"].iloc[0]

    report = validate_telemetry(df, cfg, load_schema())
    assert report["status"] == "PASS"
    assert report["checks"]["energy_balance_within_tolerance"] is True


def test_grid_outage_diagnostic_recovers_exact_interval_without_ground_truth_input():
    df, _ = load_demo_context()
    r = diagnose_grid_outage(df, "2026-10-10")
    assert r["candidate_cause"] == "grid_outage_with_backup_operation"
    assert r["confidence"] == "high"
    assert r["data_window"] == {
        "start": "2026-10-10T21:35:00+01:00",
        "end": "2026-10-10T22:35:00+01:00",
    }
    m = _measurements(r)
    assert m["outage_duration_minutes"] == 60.0
    assert m["mean_outage_grid_import_w"] == 0.0
    assert m["immediate_battery_discharge_increase_w"] > 0
    assert m["battery_soc_drop_pct"] > 0
    assert m["islanded_state_fraction"] == 1.0
    assert m["grid_restored_after_event"] is True
    assert m["max_local_power_balance_residual_w"] == 0.0


def test_zero_grid_import_while_grid_is_available_is_not_misdiagnosed_as_outage():
    df, _ = load_demo_context()
    r = diagnose_grid_outage(df, "2026-10-11")
    assert r["candidate_cause"] == "no_grid_outage_detected"
    assert r["data_quality"]["sufficient"] is True
    m = _measurements(r)
    assert m["grid_unavailable_intervals"] == 0
    assert m["zero_import_while_grid_available_intervals"] > 0


def test_grid_outage_diagnostic_abstains_when_required_grid_signal_is_missing():
    df, _ = load_demo_context()
    r = diagnose_grid_outage(df.drop(columns=["grid_available"]), "2026-10-10")
    assert r["candidate_cause"] is None
    assert r["data_quality"]["sufficient"] is False


def test_grid_outage_tool_and_offline_router_use_approved_evidence_path():
    e = execute_tool("investigate_grid_event", {"question": "What happened when the grid went down?", "target_date": "2026-10-10"})
    assert e["candidate_cause"] == "grid_outage_with_backup_operation"
    assert e["supporting_tools"] == ["diagnose_grid_outage"]
    assert e["synthetic_data"] is True
    answer = fallback_answer("What happened when the grid went down on 2026-10-10?")
    assert "islanded backup operation" in answer.lower()


def test_grid_outage_counterfactual_with_no_injected_outage_has_no_false_positive():
    cfg = deepcopy(load_installation_config())
    cfg["simulation"]["scenarios"]["grid_outage_minutes"] = 0
    df, gt = simulate(cfg)
    r = diagnose_grid_outage(df, "2026-10-10")
    assert r["candidate_cause"] == "no_grid_outage_detected"
    assert not df["grid_available"].eq(False).any()


def test_final_m6_evaluation_contains_six_required_scenarios_and_eleven_queries():
    report = run_m6_evaluation()
    assert report["final_scope_completion"]["required_scenario_count"] == 6
    assert report["final_scope_completion"]["canonical_query_count"] == 11
    assert len(report["scenario_results"]) == 6
    assert all(r["overall"] == "PASS" for r in report["scenario_results"])
    grid = next(r for r in report["scenario_results"] if r["event_type"] == "grid_outage_islanding")
    assert grid["dimensions"]["localization"]["status"] == "PASS"
    assert grid["dimensions"]["evidence_grounding"]["status"] == "PASS"
    assert len(report["canonical_query_results"]) == 11
    assert all(q["status"] == "PASS" for q in report["canonical_query_results"])


def test_outage_overlapping_overload_records_unmet_load_and_preserves_balance():
    """Regression: islanded demand above battery power must not vanish from bookkeeping."""
    cfg = deepcopy(load_installation_config())
    cfg["simulation"]["scenarios"]["grid_outage_start"] = "2026-08-08T19:30:00"
    cfg["simulation"]["scenarios"]["grid_outage_minutes"] = 35
    df, _ = simulate(cfg)

    event = df[(df["timestamp"] >= pd.Timestamp("2026-08-08T19:30:00", tz=cfg["installation"]["timezone"])) &
               (df["timestamp"] < pd.Timestamp("2026-08-08T20:05:00", tz=cfg["installation"]["timezone"]))]
    assert event["unmet_load_w"].max() > 2000
    assert event["battery_discharge_w"].max() <= cfg["installation"]["battery_max_discharge_w"] + 1e-9
    assert ((event["load_requested_power_w"] - event["load_power_w"] - event["unmet_load_w"]).abs().max() < 1e-6)

    from src.analytics.energy_balance import instantaneous_balance_residual_w
    assert instantaneous_balance_residual_w(event).abs().max() < 1e-6

    report = validate_telemetry(df, cfg, load_schema())
    assert report["status"] == "PASS"
    assert report["checks"]["load_demand_accounting_consistent"] is True

    diagnosis = diagnose_grid_outage(df, "2026-08-08")
    assert diagnosis["candidate_cause"] == "grid_outage_with_load_shedding"
    m = _measurements(diagnosis)
    assert m["max_unmet_load_w"] > 2000
    assert m["max_local_power_balance_residual_w"] == 0.0


def test_long_outage_energy_depletion_records_unmet_load_and_preserves_balance():
    """Regression: battery reaching its SOC floor must create explicit unmet load."""
    cfg = deepcopy(load_installation_config())
    cfg["simulation"]["scenarios"]["grid_outage_start"] = "2026-10-10T21:35:00"
    cfg["simulation"]["scenarios"]["grid_outage_minutes"] = 300
    df, _ = simulate(cfg)
    start = pd.Timestamp("2026-10-10T21:35:00", tz=cfg["installation"]["timezone"])
    end = start + pd.Timedelta(minutes=300)
    event = df[(df["timestamp"] >= start) & (df["timestamp"] < end)]

    assert event["unmet_load_w"].max() > 0
    assert event["battery_soc_pct"].min() >= cfg["installation"]["battery_soc_min_pct"] - 1e-9
    assert ((event["load_requested_power_w"] - event["load_power_w"] - event["unmet_load_w"]).abs().max() < 1e-6)

    from src.analytics.energy_balance import instantaneous_balance_residual_w
    assert instantaneous_balance_residual_w(event).abs().max() < 1e-6
    assert validate_telemetry(df, cfg, load_schema())["status"] == "PASS"


def test_daytime_islanded_surplus_is_explicitly_curtailed_and_balanced():
    """Regression: islanded PV surplus with nowhere to go must be curtailed, not disappear."""
    cfg = deepcopy(load_installation_config())
    cfg["installation"]["battery_max_charge_w"] = 0
    cfg["simulation"]["scenarios"]["grid_outage_start"] = "2026-10-10T12:00:00"
    cfg["simulation"]["scenarios"]["grid_outage_minutes"] = 60
    df, _ = simulate(cfg)
    start = pd.Timestamp("2026-10-10T12:00:00", tz=cfg["installation"]["timezone"])
    end = start + pd.Timedelta(minutes=60)
    event = df[(df["timestamp"] >= start) & (df["timestamp"] < end)]

    assert event["pv_curtailed_w"].max() > 0
    assert ((event["pv_available_ac_power_w"] - event["pv_ac_power_w"] - event["pv_curtailed_w"]).abs().max() < 1e-6)

    from src.analytics.energy_balance import instantaneous_balance_residual_w
    assert instantaneous_balance_residual_w(event).abs().max() < 1e-6
    report = validate_telemetry(df, cfg, load_schema())
    assert report["status"] == "PASS"
    assert report["checks"]["pv_curtailment_accounting_consistent"] is True
