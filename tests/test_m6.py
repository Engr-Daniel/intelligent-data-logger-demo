from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pandas as pd
import pytest

from src.analytics.battery_health import detect_battery_capacity_decline
from src.analytics.data_quality import localize_data_unavailability
from src.datacontext.context import load_installation_config
from src.evaluation.m6_runner import run_m6_evaluation
from src.generator.simulate import simulate
from src.reasoning.tools import execute_tool
from src.storage.local_store import load_telemetry

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture(scope="module")
def m6_report():
    return run_m6_evaluation()


def _battery_args(cfg):
    i=cfg["installation"]
    return dict(interval_minutes=cfg["simulation"]["interval_minutes"], nominal_usable_capacity_kwh=i["battery_nominal_kwh"]*i["battery_usable_fraction"], charge_efficiency=i["battery_charge_efficiency"], discharge_efficiency=i["battery_discharge_efficiency"])


def test_m6_battery_degradation_is_inferred_from_observed_flows_not_latent_capacity():
    df=load_telemetry(); cfg=load_installation_config()
    observed=df.drop(columns=["battery_usable_capacity_wh","battery_stored_energy_wh"])
    r=detect_battery_capacity_decline(observed,**_battery_args(cfg))
    assert r["candidate_cause"]=="battery_capacity_degradation"
    m={x["name"]:x["value"] for x in r["measurements"]}
    assert 4.5 <= m["estimated_capacity_decline_pct"] <= 7.0
    assert m["early_estimated_usable_capacity_wh"] > m["late_estimated_usable_capacity_wh"]


def test_m6_battery_detector_does_not_invent_degradation_when_capacity_is_constant():
    cfg=deepcopy(load_installation_config()); cfg["simulation"]["scenarios"]["battery_capacity_loss_fraction"]=0.0
    df,_=simulate(cfg)
    observed=df.drop(columns=["battery_usable_capacity_wh","battery_stored_energy_wh"])
    r=detect_battery_capacity_decline(observed,**_battery_args(cfg))
    assert r["candidate_cause"]=="no_material_battery_capacity_decline"
    m={x["name"]:x["value"] for x in r["measurements"]}
    assert abs(m["estimated_capacity_decline_pct"]) < 0.5


def test_m6_battery_detector_abstains_when_observed_battery_data_are_insufficient():
    df=load_telemetry().iloc[:100].copy(); cfg=load_installation_config()
    r=detect_battery_capacity_decline(df,**_battery_args(cfg))
    assert r["candidate_cause"] is None
    assert r["data_quality"]["sufficient"] is False


def test_m6_dropout_localization_matches_observed_gap_without_ground_truth_input():
    r=localize_data_unavailability(load_telemetry(),"2026-09-18")
    assert r["candidate_cause"]=="telemetry_unavailable"
    assert r["data_window"]=={"start":"2026-09-18T12:00:00+01:00","end":"2026-09-18T12:45:00+01:00"}
    m={x["name"]:x["value"] for x in r["measurements"]}
    assert m["gap_duration_minutes"]==45.0
    assert m["contiguous_gap_count"]==1
    assert r["data_quality"]["sufficient"] is False


def test_m6_dropout_localizer_reports_complete_day_without_false_gap():
    r=localize_data_unavailability(load_telemetry(),"2026-09-17")
    assert r["candidate_cause"]=="data_available"
    assert r["data_quality"]["sufficient"] is True


def test_m6_tools_expose_new_capabilities_as_evidence_objects():
    b=execute_tool("investigate_battery_health",{"question":"Is battery capacity degrading?"})
    d=execute_tool("investigate_data_gap",{"question":"Where is telemetry missing?","target_date":"2026-09-18"})
    assert b["supporting_tools"]==["detect_battery_capacity_decline"]
    assert d["supporting_tools"]==["localize_data_unavailability"]
    assert b["synthetic_data"] is True and d["synthetic_data"] is True


def test_m6_rerun_closes_the_two_m5_gaps_without_changing_scoring_dimensions(m6_report):
    report=m6_report
    assert report["m5_rubric_changed"] is False
    assert all(r["overall"]=="PASS" for r in report["scenario_results"])
    battery=next(r for r in report["scenario_results"] if r["event_type"]=="battery_degradation_signature")
    dropout=next(r for r in report["scenario_results"] if r["event_type"]=="sensor_dropout")
    assert battery["dimensions"]["diagnosis"]["status"]=="PASS"
    assert battery["dimensions"]["evidence_grounding"]["status"]=="PASS"
    assert dropout["dimensions"]["localization"]["status"]=="PASS"
    assert set(battery["dimensions"])=={"detection","localization","diagnosis","evidence_grounding","calibration","abstention"}


def test_m6_all_ten_canonical_queries_still_trace_cleanly(m6_report):
    report=m6_report
    assert len(report["canonical_query_results"])==10
    assert all(q["status"]=="PASS" for q in report["canonical_query_results"])
    q9=next(q for q in report["canonical_query_results"] if q["id"]==9)
    assert q9["supporting_tools"]==["localize_data_unavailability"]


def test_m5_report_artifact_remains_frozen_with_original_gap_results():
    frozen=json.loads((ROOT/"reports"/"m5_evaluation.json").read_text())
    b=next(r for r in frozen["scenario_results"] if r["event_type"]=="battery_degradation_signature")
    d=next(r for r in frozen["scenario_results"] if r["event_type"]=="sensor_dropout")
    assert b["overall"]=="CAPABILITY_GAP"
    assert d["overall"]=="PARTIAL"
