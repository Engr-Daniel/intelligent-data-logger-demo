from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from src.datacontext.context import field_context, load_installation_config, load_schema
from src.datacontext.validation import validate_telemetry
from src.generator.simulate import load_config, simulate
from src.storage.local_store import load_telemetry, write_store


def test_sqlite_round_trip_preserves_operational_telemetry_only(tmp_path: Path):
    cfg = load_config()
    df, _ = simulate(cfg)
    db = tmp_path / "datalodger.sqlite"
    write_store(df, db)
    loaded = load_telemetry(db)
    assert len(loaded) == len(df)
    assert loaded["timestamp"].is_monotonic_increasing
    with sqlite3.connect(db) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "telemetry" in tables
    assert "ground_truth_events" not in tables


def test_sqlite_round_trip_preserves_null_boolean_numeric_and_timestamp_fidelity(tmp_path: Path):
    cfg = load_config()
    df, _ = simulate(cfg)
    db = tmp_path / "datalodger.sqlite"
    write_store(df, db)
    loaded = load_telemetry(db)
    original_ts = pd.to_datetime(df["timestamp"]).reset_index(drop=True)
    loaded_ts = pd.to_datetime(loaded["timestamp"]).reset_index(drop=True)
    assert (loaded_ts == original_ts).all()
    assert loaded["grid_available"].dtype == bool
    assert loaded["grid_available"].tolist() == df["grid_available"].astype(bool).tolist()
    assert loaded["pv_ac_power_w"].isna().sum() == df["pv_ac_power_w"].isna().sum()
    np.testing.assert_allclose(loaded["load_power_w"], df["load_power_w"], rtol=0, atol=1e-10, equal_nan=True)


def test_sqlite_time_window_query_uses_inclusive_exact_boundaries(tmp_path: Path):
    cfg = load_config()
    df, _ = simulate(cfg)
    db = tmp_path / "datalodger.sqlite"
    write_store(df, db)
    start = pd.Timestamp(df.iloc[100]["timestamp"])
    end = pd.Timestamp(df.iloc[105]["timestamp"])
    window = load_telemetry(db, start=start.isoformat(), end=end.isoformat())
    assert len(window) == 6
    assert window.iloc[0]["timestamp"] == start
    assert window.iloc[-1]["timestamp"] == end


def test_data_context_schema_documents_units_ranges_and_required_fields():
    schema = load_schema()
    assert schema["schema_version"] == 1
    assert schema["frequency_minutes"] == 5
    assert field_context("pv_ac_power_w", schema)["unit"] == "W"
    assert field_context("battery_soc_pct", schema)["normal_range"] == [10, 100]
    assert field_context("timestamp", schema)["required"] is True
    assert field_context("battery_usable_capacity_wh", schema)["observability"] == "simulated_latent_state"


def test_installation_config_separates_technical_financial_and_sustainability_assumptions():
    cfg = load_installation_config()
    assert {"installation", "financial", "sustainability", "simulation"} <= set(cfg)
    assert cfg["financial"]["currency"] == "NGN"
    assert "tariff_effective_date" in cfg["financial"]
    assert "emissions_factor_source" in cfg["sustainability"]
    assert cfg["sustainability"]["baseline"]


def test_m2_validation_detects_dropout_without_ground_truth_and_reports_coverage():
    cfg = load_config()
    schema = load_schema()
    df, _ = simulate(cfg)
    report = validate_telemetry(df, cfg, schema)
    assert report["status"] == "PASS", json.dumps(report, indent=2)
    assert report["checks"]["energy_balance_within_tolerance"] is True
    assert report["details"]["missing_rows"] > 0
    assert report["data_quality_events"][0]["event_type"] == "telemetry_unavailable"
    assert report["data_quality_events"][0]["detected_from"] == "observed_missing_values"
    assert report["coverage"]["power_balance"]["excluded_rows"] > 0
    assert report["coverage"]["power_balance"]["coverage_pct"] < 100
    assert report["details"]["power_balance_residual_w"]["violations"] == 0


def test_m2_validation_fails_on_physical_violation():
    cfg = load_config()
    schema = load_schema()
    df, _ = simulate(cfg)
    idx = df["pv_ac_power_w"].first_valid_index()
    df.loc[idx, "grid_import_w"] += 100.0
    report = validate_telemetry(df, cfg, schema)
    assert report["status"] == "FAIL"
    assert report["checks"]["energy_balance_within_tolerance"] is False
    assert report["details"]["power_balance_residual_w"]["violations"] >= 1


def test_m2_validation_reports_insufficient_data_when_physics_coverage_is_too_low():
    cfg = load_config()
    schema = load_schema()
    df, _ = simulate(cfg)
    df.loc[df.index[: int(len(df) * 0.10)], "pv_ac_power_w"] = np.nan
    report = validate_telemetry(df, cfg, schema)
    assert report["status"] == "INSUFFICIENT_DATA"
    assert report["passed"] is False
    assert report["coverage"]["power_balance"]["coverage_pct"] < schema["validation"]["minimum_physics_coverage_pct"]


def test_battery_transition_input_coverage_and_equation_applicability_are_distinct():
    cfg = load_config()
    schema = load_schema()
    df, _ = simulate(cfg)
    report = validate_telemetry(df, cfg, schema)
    transition = report["coverage"]["battery_transition"]
    assert "input_coverage_pct" in transition
    assert "equation_applicability_pct" in transition
    assert "structural_non_evaluable_rows" in transition
    assert transition["sufficiency_basis"] == "input_coverage_pct"
    assert transition["input_coverage_pct"] > transition["equation_applicability_pct"]
    assert transition["structural_non_evaluable_rows"] > 0
    assert transition["input_coverage_pct"] >= schema["validation"]["minimum_physics_coverage_pct"]
    assert report["status"] == "PASS"


def test_battery_transition_missing_input_can_make_validation_insufficient():
    cfg = load_config()
    schema = load_schema()
    df, _ = simulate(cfg)
    df.loc[df.index[: int(len(df) * 0.10)], "battery_stored_energy_wh"] = np.nan
    report = validate_telemetry(df, cfg, schema)
    transition = report["coverage"]["battery_transition"]
    assert transition["input_coverage_pct"] < schema["validation"]["minimum_physics_coverage_pct"]
    assert report["status"] == "INSUFFICIENT_DATA"
