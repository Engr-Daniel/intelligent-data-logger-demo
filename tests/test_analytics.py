import pandas as pd

from src.analytics.battery import battery_runway
from src.analytics.energy_balance import instantaneous_balance_residual_w
from src.analytics.financial import financial_metrics
from src.analytics.generation_drop import analyze_generation_drop
from src.analytics.root_cause import diagnose_overload
from src.generator.simulate import load_config, simulate
from src.reasoning.tools import TOOL_DEFINITIONS, execute_tool


def test_generator_contains_overload_alarm():
    df, gt = simulate(load_config())
    assert (df["inverter_alarm_code"] == "OVERLOAD_02").any()
    assert any(event["event_type"] == "customer_overload" for event in gt["events"])


def test_overload_is_diagnosed():
    cfg = load_config()
    df, _ = simulate(cfg)
    result = diagnose_overload(df, cfg["installation"]["inverter_rating_w"])
    assert result["candidate_cause"] == "overload"
    assert result["confidence"] == "high"


def test_alternative_causes_are_computed_with_evidence():
    cfg = load_config()
    df, _ = simulate(cfg)
    result = diagnose_overload(df, cfg["installation"]["inverter_rating_w"])
    alternatives = {item["cause"]: item for item in result["alternatives_checked"]}
    assert alternatives["grid_outage"]["supported"] is False
    assert "grid_available_fraction" in alternatives["grid_outage"]["evidence"]
    assert alternatives["weather_related_generation_drop_only"]["supported"] is False
    assert "median_irradiance_wm2" in alternatives["weather_related_generation_drop_only"]["evidence"]


def test_power_balance_invariant_default_scenario():
    df, _ = simulate(load_config())
    assert instantaneous_balance_residual_w(df).abs().max() < 1e-6


def test_power_balance_invariant_with_daytime_derate():
    cfg = load_config()
    daytime_overload = pd.Timestamp("2026-08-08 13:00", tz=cfg["installation"]["timezone"])
    df, _ = simulate(cfg, overload_start=daytime_overload)
    derated = df[df["inverter_operating_state"] == "derated"]
    assert not derated.empty
    assert derated["pv_ac_power_w"].max() > 0  # proves this regression test exercises daytime PV derating
    assert instantaneous_balance_residual_w(df).abs().max() < 1e-6


def test_soc_and_battery_power_bounds():
    cfg = load_config()
    df, _ = simulate(cfg)
    inst = cfg["installation"]
    battery = df.dropna(subset=["battery_soc_pct", "battery_charge_w", "battery_discharge_w"])
    assert battery["battery_soc_pct"].between(inst["battery_soc_min_pct"] - 1e-9, inst["battery_soc_max_pct"] + 1e-9).all()
    assert (battery["battery_charge_w"] <= inst["battery_max_charge_w"] + 1e-9).all()
    assert (battery["battery_discharge_w"] <= inst["battery_max_discharge_w"] + 1e-9).all()


def test_battery_runway_exposes_assumptions():
    result = battery_runway(60, 9.0, 1000, 10)
    assert result["estimated_runway_hours"] == 4.5
    assert result["assumptions"]["load_assumed_constant"] is True


def test_financial_metrics_distinguish_roi_and_payback():
    result = financial_metrics(1000, 200, 1_000_000, period_days=365)
    assert result["simple_roi_pct"] == 20.0
    assert result["simple_payback_years"] == 5.0


def test_generator_contains_cloudy_day_ground_truth():
    _, gt = simulate(load_config())
    event_types = {event["event_type"] for event in gt["events"]}
    assert "cloudy_day_generation_drop" in event_types


def test_cloudy_day_drop_is_diagnosed_as_weather_related():
    cfg = load_config()
    df, _ = simulate(cfg)
    result = analyze_generation_drop(df, "2026-08-05")
    assert result["candidate_cause"] == "weather_related_low_irradiance"
    assert result["confidence"] == "high"
    alternatives = {item["cause"]: item for item in result["alternatives_checked"]}
    assert alternatives["weather_related_low_irradiance"]["supported"] is True
    assert alternatives["inverter_fault_or_derating"]["supported"] is False


def test_m1_exposes_two_distinct_claude_tools():
    names = {tool["name"] for tool in TOOL_DEFINITIONS}
    assert {"investigate_inverter_failure", "investigate_generation_drop"}.issubset(names)


def test_tool_executor_returns_grounded_evidence_for_both_query_families():
    fault = execute_tool("investigate_inverter_failure", {"question": "Why did the inverter fail?"})
    drop = execute_tool(
        "investigate_generation_drop",
        {"question": "Why did generation drop?", "target_date": "2026-08-05"},
    )
    assert fault["candidate_cause"] == "overload"
    assert fault["supporting_tools"] == ["diagnose_overload"]
    assert drop["candidate_cause"] == "weather_related_low_irradiance"
    assert drop["supporting_tools"] == ["analyze_generation_drop"]



def test_brief_daytime_inverter_event_is_reported_even_without_material_daily_drop():
    cfg = load_config()
    daytime_overload = pd.Timestamp("2026-08-08 13:00", tz=cfg["installation"]["timezone"])
    df, _ = simulate(cfg, overload_start=daytime_overload)
    result = analyze_generation_drop(df, "2026-08-08")
    alternatives = {item["cause"]: item for item in result["alternatives_checked"]}

    assert result["candidate_cause"] == "inverter_event_limited_energy_impact"
    assert result["confidence"] == "high"
    assert alternatives["weather_related_low_irradiance"]["supported"] is False
    assert alternatives["inverter_fault_or_derating"]["supported"] is False
    assert alternatives["inverter_event_limited_energy_impact"]["supported"] is True
    assert alternatives["inverter_event_limited_energy_impact"]["evidence"]["inverter_alarm_present"] is True


def test_material_fault_related_drop_is_not_misdiagnosed_as_weather():
    cfg = load_config()
    daytime_overload = pd.Timestamp("2026-08-08 13:00", tz=cfg["installation"]["timezone"])
    df, _ = simulate(cfg, overload_start=daytime_overload)

    # Isolate the production-drop classifier: create a material target-day PV loss
    # while leaving irradiance unchanged and retaining the independently generated
    # inverter alarm/derated state.
    target = pd.to_datetime(df["timestamp"]).dt.date == pd.Timestamp("2026-08-08").date()
    daytime = pd.to_datetime(df["timestamp"]).dt.hour.between(9, 15)
    df.loc[target & daytime, "pv_ac_power_w"] *= 0.55

    result = analyze_generation_drop(df, "2026-08-08")
    alternatives = {item["cause"]: item for item in result["alternatives_checked"]}

    assert result["candidate_cause"] == "inverter_fault_or_derating"
    assert result["confidence"] == "high"
    assert alternatives["weather_related_low_irradiance"]["supported"] is False
    assert alternatives["inverter_fault_or_derating"]["supported"] is True


def test_normal_day_reports_no_material_generation_anomaly():
    cfg = load_config()
    df, _ = simulate(cfg)
    result = analyze_generation_drop(df, "2026-08-06")

    assert result["candidate_cause"] == "no_material_generation_anomaly"
    assert result["confidence"] == "medium"
    assert not any(item["supported"] for item in result["alternatives_checked"])


def test_m1_full_generator_contains_all_required_scenarios():
    _, gt = simulate(load_config())
    event_types = {event["event_type"] for event in gt["events"]}
    assert {
        "cloudy_day_generation_drop",
        "customer_overload",
        "gradual_efficiency_decline",
        "battery_degradation_signature",
        "sensor_dropout",
    } <= event_types


def test_gradual_efficiency_decline_reaches_configured_loss():
    cfg = load_config()
    df, _ = simulate(cfg)
    inst = cfg["installation"]
    scenario = cfg["simulation"]["scenarios"]
    nominal_eff = inst["inverter_nominal_efficiency"]
    # Reconstruct the temperature-corrected ideal DC output on non-clipped, daytime rows.
    ideal = inst["pv_kwp"] * 1000 * (df["irradiance_wm2"] / 1000) * (
        1 - 0.004 * (df["ambient_temp_c"] - 25).clip(lower=0)
    )
    factor = df["pv_dc_power_w"] / ideal
    ts = pd.to_datetime(df["timestamp"])
    early = factor[(ts < pd.Timestamp(scenario["efficiency_decline_start"], tz=inst["timezone"])) & (ideal > 500)].dropna()
    late = factor[(ts >= pd.Timestamp(scenario["efficiency_decline_end"], tz=inst["timezone"])) & (ideal > 500)].dropna()
    assert abs(early.median() - 1.0) < 1e-6
    assert abs(late.median() - (1 - scenario["efficiency_decline_fraction"])) < 1e-6
    assert nominal_eff > 0  # documents that array decline is distinct from inverter conversion efficiency


def test_battery_degradation_reduces_usable_capacity_without_breaking_soc_bounds():
    cfg = load_config()
    df, _ = simulate(cfg)
    clean = df.dropna(subset=["battery_usable_capacity_wh", "battery_soc_pct"])
    expected_initial = cfg["installation"]["battery_nominal_kwh"] * cfg["installation"]["battery_usable_fraction"] * 1000
    expected_final = expected_initial * (1 - cfg["simulation"]["scenarios"]["battery_capacity_loss_fraction"])
    assert abs(clean["battery_usable_capacity_wh"].iloc[0] - expected_initial) < 1e-6
    assert abs(clean["battery_usable_capacity_wh"].iloc[-1] - expected_final) < 1e-3
    assert clean["battery_soc_pct"].between(cfg["installation"]["battery_soc_min_pct"] - 1e-9, cfg["installation"]["battery_soc_max_pct"] + 1e-9).all()


def test_sensor_dropout_is_explicit_and_limited_to_ground_truth_window():
    cfg = load_config()
    df, gt = simulate(cfg)
    event = next(e for e in gt["events"] if e["event_type"] == "sensor_dropout")
    ts = pd.to_datetime(df["timestamp"])
    mask = (ts >= pd.Timestamp(event["start"])) & (ts < pd.Timestamp(event["end"]))
    assert mask.sum() == cfg["simulation"]["scenarios"]["sensor_dropout_minutes"] // cfg["simulation"]["interval_minutes"]
    assert df.loc[mask, "pv_ac_power_w"].isna().all()
    assert not df.loc[~mask, "pv_ac_power_w"].isna().any()


def test_generator_scenarios_are_resolution_independent_under_microsecond_datetimeindex(monkeypatch):
    import pandas as pd
    import src.generator.simulate as simmod

    original_date_range = pd.date_range

    def microsecond_date_range(*args, **kwargs):
        return original_date_range(*args, **kwargs).as_unit("us")

    monkeypatch.setattr(simmod.pd, "date_range", microsecond_date_range)
    cfg = simmod.load_config()
    df, _ = simmod.simulate(cfg)

    assert df["battery_usable_capacity_wh"].min() < df["battery_usable_capacity_wh"].max()

    daylight = df["irradiance_wm2"] > 100
    ideal_dc = (
        cfg["installation"]["pv_kwp"]
        * 1000
        * (df.loc[daylight, "irradiance_wm2"] / 1000)
        * (1 - 0.004 * (df.loc[daylight, "ambient_temp_c"] - 25).clip(lower=0))
    )
    implied_factor = df.loc[daylight, "pv_dc_power_w"] / ideal_dc
    assert implied_factor.min() <= 1 - cfg["simulation"]["scenarios"]["efficiency_decline_fraction"] + 1e-9
    assert implied_factor.max() <= 1.0 + 1e-9
