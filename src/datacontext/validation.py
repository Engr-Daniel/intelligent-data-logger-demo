from __future__ import annotations

import numpy as np
import pandas as pd

from src.analytics.energy_balance import instantaneous_balance_residual_w


def _summary(values: pd.Series, tolerance: float) -> dict:
    values = values.dropna().abs()
    if values.empty:
        return {"max": None, "median": None, "p95": None, "violations": 0, "violation_pct": None}
    return {
        "max": float(values.max()),
        "median": float(values.median()),
        "p95": float(values.quantile(0.95)),
        "violations": int((values > tolerance).sum()),
        "violation_pct": float((values > tolerance).mean() * 100),
    }


def validate_telemetry(df: pd.DataFrame, config: dict, schema: dict) -> dict:
    """Run operational M2 schema, data-quality and physical sanity checks.

    This validator deliberately has no access to experiment ground truth. Missing
    telemetry is detected from observations. Physics checks report their coverage
    and may return ``INSUFFICIENT_DATA`` rather than silently treating excluded
    rows as validated.
    """
    fields = schema["fields"]
    required = [name for name, meta in fields.items() if meta.get("required", False)]
    missing_columns = sorted(set(required) - set(df.columns))
    total_rows = len(df)

    ts = pd.to_datetime(df["timestamp"]) if "timestamp" in df else pd.Series(dtype="datetime64[ns]")
    interval = int(schema.get("frequency_minutes", config["simulation"]["interval_minutes"]))
    duplicate_timestamps = int(ts.duplicated().sum()) if len(ts) else 0
    cadence_breaks = 0
    if len(ts) > 1:
        cadence_breaks = int((ts.sort_values().diff().dropna() != pd.Timedelta(minutes=interval)).sum())

    if missing_columns:
        missing_mask = pd.Series(True, index=df.index)
    else:
        missing_mask = df[required].isna().any(axis=1)
    missing_rows = int(missing_mask.sum())
    missing_by_field = {name: int(df[name].isna().sum()) for name in required if name in df and df[name].isna().any()}

    range_violations: dict[str, int] = {}
    for name, meta in fields.items():
        if name not in df or "normal_range" not in meta:
            continue
        low, high = meta["normal_range"]
        series = pd.to_numeric(df[name], errors="coerce")
        count = int(((series < low) | (series > high)).fillna(False).sum())
        if count:
            range_violations[name] = count

    power_fields = ["pv_ac_power_w", "grid_import_w", "battery_discharge_w", "load_power_w", "battery_charge_w", "grid_export_w"]
    complete = df.dropna(subset=power_fields) if all(c in df for c in power_fields) else df.iloc[0:0]
    residual = instantaneous_balance_residual_w(complete) if len(complete) else pd.Series(dtype=float)
    tolerance = float(config["simulation"].get("energy_balance_tolerance_w", 1e-6))
    power_summary = _summary(residual, tolerance)
    power_eligible = len(complete)
    power_excluded = total_rows - power_eligible
    power_coverage = (power_eligible / total_rows * 100) if total_rows else 0.0

    minimum_coverage = float(schema.get("validation", {}).get("minimum_physics_coverage_pct", 95.0))
    power_sufficient = power_coverage >= minimum_coverage and power_eligible > 0

    # Explicit islanded bookkeeping invariants. Requested demand must equal
    # served load plus unmet load, and available PV must equal delivered PV
    # plus curtailment. These checks make outage physics parameter-independent
    # instead of relying on a specific event duration or demand level.
    load_accounting_fields = ["load_requested_power_w", "load_power_w", "unmet_load_w"]
    load_rows = df.dropna(subset=load_accounting_fields) if all(c in df for c in load_accounting_fields) else df.iloc[0:0]
    load_accounting_residual = (
        load_rows["load_requested_power_w"] - load_rows["load_power_w"] - load_rows["unmet_load_w"]
    ) if len(load_rows) else pd.Series(dtype=float)
    load_accounting_summary = _summary(load_accounting_residual, tolerance)
    load_accounting_sufficient = (len(load_rows) / total_rows * 100 >= minimum_coverage) if total_rows else False

    pv_accounting_fields = ["pv_available_ac_power_w", "pv_ac_power_w", "pv_curtailed_w"]
    pv_rows = df.dropna(subset=pv_accounting_fields) if all(c in df for c in pv_accounting_fields) else df.iloc[0:0]
    pv_accounting_residual = (
        pv_rows["pv_available_ac_power_w"] - pv_rows["pv_ac_power_w"] - pv_rows["pv_curtailed_w"]
    ) if len(pv_rows) else pd.Series(dtype=float)
    pv_accounting_summary = _summary(pv_accounting_residual, tolerance)
    pv_accounting_sufficient = (len(pv_rows) / total_rows * 100 >= minimum_coverage) if total_rows else False

    inst = config["installation"]
    battery_fields = ["battery_soc_pct", "battery_charge_w", "battery_discharge_w", "battery_stored_energy_wh", "battery_usable_capacity_wh"]
    battery_rows = df.dropna(subset=battery_fields) if all(c in df for c in battery_fields) else df.iloc[0:0]
    battery_coverage = (len(battery_rows) / total_rows * 100) if total_rows else 0.0
    battery_sufficient = battery_coverage >= minimum_coverage and len(battery_rows) > 0
    soc_ok = bool(len(battery_rows) and battery_rows["battery_soc_pct"].between(inst["battery_soc_min_pct"] - 1e-9, inst["battery_soc_max_pct"] + 1e-9).all())
    charge_ok = bool(len(battery_rows) and (battery_rows["battery_charge_w"] <= inst["battery_max_charge_w"] + 1e-9).all())
    discharge_ok = bool(len(battery_rows) and (battery_rows["battery_discharge_w"] <= inst["battery_max_discharge_w"] + 1e-9).all())
    stored_ok = bool(len(battery_rows) and (battery_rows["battery_stored_energy_wh"] <= battery_rows["battery_usable_capacity_wh"] + 1e-6).all())

    transition_fields = ["battery_stored_energy_wh", "battery_usable_capacity_wh", "battery_charge_w", "battery_discharge_w"]
    transition = df[transition_fields].copy() if all(c in df for c in transition_fields) else pd.DataFrame(columns=transition_fields)
    dt_h = interval / 60
    prev_stored = transition["battery_stored_energy_wh"].shift(1)
    prev_capacity = transition["battery_usable_capacity_wh"].shift(1)
    expected = prev_stored + transition["battery_charge_w"] * dt_h * inst["battery_charge_efficiency"] - transition["battery_discharge_w"] * dt_h / inst["battery_discharge_efficiency"]
    transition_residual = transition["battery_stored_energy_wh"] - expected
    complete_transition = transition.notna().all(axis=1) & prev_stored.notna()
    capacity_boundary = complete_transition & (prev_stored >= prev_capacity - 1e-4)
    interior = complete_transition & ~capacity_boundary
    transition_summary = _summary(transition_residual[interior], 1e-6)
    transition_excluded_capacity_boundary = int(capacity_boundary.sum())
    transition_missing = int((~complete_transition).sum())
    transition_eligible = int(interior.sum())
    transition_input_coverage_pct = (int(complete_transition.sum()) / max(total_rows - 1, 1) * 100) if total_rows else 0.0
    # Capacity-boundary transitions are structurally non-evaluable by this M2 flow-only
    # equation because the simulator permits the usable-capacity ceiling to move.
    # They are not missing-data exclusions. Sufficiency therefore depends on input
    # telemetry coverage; equation applicability is reported separately.
    transition_equation_applicability_pct = (transition_eligible / max(total_rows - 1, 1) * 100) if total_rows else 0.0
    transition_sufficient = transition_input_coverage_pct >= minimum_coverage and transition_eligible > 0

    checks = {
        "required_columns_present": not missing_columns,
        "timestamps_unique": duplicate_timestamps == 0,
        "cadence_continuous": cadence_breaks == 0,
        "missing_telemetry_detected": missing_rows > 0,
        "schema_ranges_respected": not range_violations,
        "energy_balance_within_tolerance": power_sufficient and power_summary["violations"] == 0,
        "load_demand_accounting_consistent": load_accounting_sufficient and load_accounting_summary["violations"] == 0,
        "pv_curtailment_accounting_consistent": pv_accounting_sufficient and pv_accounting_summary["violations"] == 0,
        "battery_soc_bounds": battery_sufficient and soc_ok,
        "battery_charge_power_limit": battery_sufficient and charge_ok,
        "battery_discharge_power_limit": battery_sufficient and discharge_ok,
        "battery_stored_energy_within_capacity": battery_sufficient and stored_ok,
        "battery_energy_transition_consistent": transition_sufficient and transition_summary["violations"] == 0,
    }

    hard_fail = any([
        bool(missing_columns), duplicate_timestamps > 0, cadence_breaks > 0, bool(range_violations),
        power_sufficient and power_summary["violations"] > 0,
        load_accounting_sufficient and load_accounting_summary["violations"] > 0,
        pv_accounting_sufficient and pv_accounting_summary["violations"] > 0,
        battery_sufficient and not (soc_ok and charge_ok and discharge_ok and stored_ok),
        transition_sufficient and transition_summary["violations"] > 0,
    ])
    insufficient = not (
        power_sufficient and load_accounting_sufficient and pv_accounting_sufficient
        and battery_sufficient and transition_sufficient
    )
    status = "FAIL" if hard_fail else ("INSUFFICIENT_DATA" if insufficient else "PASS")

    return {
        "status": status,
        "passed": status == "PASS",
        "checks": checks,
        "data_quality_events": ([{
            "event_type": "telemetry_unavailable",
            "rows_affected": missing_rows,
            "fields_affected": sorted(missing_by_field),
            "detected_from": "observed_missing_values",
        }] if missing_rows else []),
        "coverage": {
            "total_rows": total_rows,
            "minimum_physics_coverage_pct": minimum_coverage,
            "power_balance": {"eligible_rows": power_eligible, "excluded_rows": power_excluded, "coverage_pct": power_coverage},
            "load_demand_accounting": {"eligible_rows": len(load_rows), "excluded_rows": total_rows - len(load_rows), "coverage_pct": (len(load_rows) / total_rows * 100) if total_rows else 0.0},
            "pv_curtailment_accounting": {"eligible_rows": len(pv_rows), "excluded_rows": total_rows - len(pv_rows), "coverage_pct": (len(pv_rows) / total_rows * 100) if total_rows else 0.0},
            "battery_state": {"eligible_rows": len(battery_rows), "excluded_rows": total_rows - len(battery_rows), "coverage_pct": battery_coverage},
            "battery_transition": {
                "evaluated_rows": transition_eligible,
                "excluded_missing_rows": transition_missing,
                "structural_non_evaluable_rows": transition_excluded_capacity_boundary,
                "input_coverage_pct": transition_input_coverage_pct,
                "equation_applicability_pct": transition_equation_applicability_pct,
                "sufficiency_basis": "input_coverage_pct",
                "pass_meaning": "Sufficient input telemetry was available and no violations were found among transitions to which the M2 flow-only equation applies.",
            },
        },
        "details": {
            "missing_columns": missing_columns,
            "missing_rows": missing_rows,
            "missing_by_field": missing_by_field,
            "duplicate_timestamps": duplicate_timestamps,
            "cadence_breaks": cadence_breaks,
            "range_violations": range_violations,
            "power_balance_residual_w": power_summary,
            "load_demand_accounting_residual_w": load_accounting_summary,
            "pv_curtailment_accounting_residual_w": pv_accounting_summary,
            "energy_balance_tolerance_w": tolerance,
            "battery_transition_residual_wh": transition_summary,
        },
    }
