from __future__ import annotations

import pandas as pd


def _measurement(name: str, value, unit: str | None = None) -> dict:
    item = {"name": name, "value": value}
    if unit is not None:
        item["unit"] = unit
    return item


def diagnose_grid_outage(df: pd.DataFrame, target_date: str | None = None) -> dict:
    """Diagnose a utility-grid outage and backup/islanded operation from observed telemetry.

    Operational inputs are limited to timestamped telemetry. Ground truth is never
    consulted. A zero grid-import value is not treated as an outage by itself;
    ``grid_available=False`` and corroborating inverter/grid/battery behaviour are
    required for a positive diagnosis.
    """
    required = {
        "timestamp",
        "grid_available",
        "grid_import_w",
        "grid_export_w",
        "battery_discharge_w",
        "battery_charge_w",
        "battery_soc_pct",
        "pv_ac_power_w",
        "load_requested_power_w",
        "load_power_w",
        "unmet_load_w",
        "inverter_operating_state",
        "inverter_alarm_code",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        return {
            "finding": "Grid-event diagnosis is unavailable because required telemetry fields are missing.",
            "candidate_cause": None,
            "confidence": "low",
            "measurements": [],
            "alternatives_checked": [],
            "data_quality": {"sufficient": False, "warnings": [f"Missing columns: {', '.join(missing)}"]},
        }

    work = df[list(required)].copy()
    work["timestamp"] = pd.to_datetime(work["timestamp"])
    work = work.sort_values("timestamp").reset_index(drop=True)
    if target_date:
        try:
            day = pd.Timestamp(target_date).date()
        except Exception:
            return {
                "finding": "The requested grid-event date could not be interpreted.",
                "candidate_cause": None,
                "confidence": "low",
                "measurements": [],
                "alternatives_checked": [],
                "data_quality": {"sufficient": False, "warnings": [f"Invalid target_date: {target_date}"]},
            }
        work = work[work["timestamp"].dt.date == day].copy()

    if work.empty:
        return {
            "finding": "No telemetry is available for the requested grid-event window.",
            "candidate_cause": None,
            "confidence": "low",
            "measurements": [],
            "alternatives_checked": [],
            "data_quality": {"sufficient": False, "warnings": ["No telemetry in requested window"]},
        }

    # Detect contiguous intervals where the grid-availability telemetry is false.
    unavailable = work["grid_available"].eq(False)
    if not unavailable.any():
        zero_import_while_available = int(((work["grid_available"] == True) & (work["grid_import_w"].fillna(0) == 0)).sum())
        return {
            "finding": "No utility-grid outage is detected in the requested telemetry window.",
            "candidate_cause": "no_grid_outage_detected",
            "confidence": "medium",
            "data_window": {"start": work["timestamp"].iloc[0].isoformat(), "end": work["timestamp"].iloc[-1].isoformat()},
            "measurements": [
                _measurement("grid_unavailable_intervals", 0, "intervals"),
                _measurement("zero_import_while_grid_available_intervals", zero_import_while_available, "intervals"),
            ],
            "alternatives_checked": [
                {
                    "cause": "self_sufficient_zero_grid_import",
                    "supported": zero_import_while_available > 0,
                    "evidence": {"zero_import_while_grid_available_intervals": zero_import_while_available},
                }
            ],
            "data_quality": {"sufficient": True, "warnings": []},
        }

    group = unavailable.ne(unavailable.shift(fill_value=False)).cumsum()
    spans = []
    for _, block in work[unavailable].groupby(group[unavailable]):
        spans.append(block)
    event = max(spans, key=len).copy()

    diffs = work["timestamp"].diff().dropna()
    interval = diffs.mode().iloc[0] if not diffs.empty else pd.Timedelta(minutes=5)
    start = event["timestamp"].iloc[0]
    end = event["timestamp"].iloc[-1] + interval
    duration_min = float((end - start).total_seconds() / 60)

    pre = work[(work["timestamp"] >= start - pd.Timedelta(minutes=30)) & (work["timestamp"] < start)].copy()
    post = work[(work["timestamp"] >= end) & (work["timestamp"] < end + pd.Timedelta(minutes=15))].copy()

    critical = [
        "grid_import_w", "grid_export_w", "battery_discharge_w", "battery_charge_w",
        "battery_soc_pct", "pv_ac_power_w", "load_requested_power_w", "load_power_w", "unmet_load_w", "inverter_operating_state",
    ]
    missing_cells = int(event[critical].isna().sum().sum())
    if missing_cells:
        return {
            "finding": "A grid-unavailable interval is visible, but telemetry inside the event is incomplete.",
            "candidate_cause": "undetermined_grid_event",
            "confidence": "low",
            "data_window": {"start": start.isoformat(), "end": end.isoformat()},
            "measurements": [
                _measurement("grid_unavailable_intervals", len(event), "intervals"),
                _measurement("missing_cells_in_event", missing_cells, "cells"),
            ],
            "alternatives_checked": [],
            "data_quality": {"sufficient": False, "warnings": ["Missing telemetry within grid-unavailable interval"]},
        }

    first = event.iloc[0]
    last = event.iloc[-1]
    pre_last = pre.iloc[-1] if not pre.empty else None

    mean_grid_import = float(event["grid_import_w"].mean())
    mean_grid_export = float(event["grid_export_w"].mean())
    islanded_fraction = float((event["inverter_operating_state"].astype(str) == "islanded").mean())
    alarm_present = bool(event["inverter_alarm_code"].fillna("").astype(str).str.len().gt(0).any())
    soc_drop = float(first["battery_soc_pct"] - last["battery_soc_pct"])
    pre_import = float(pre["grid_import_w"].mean()) if not pre.empty else 0.0
    pre_batt = float(pre["battery_discharge_w"].mean()) if not pre.empty else 0.0
    outage_batt = float(event["battery_discharge_w"].mean())
    immediate_battery_increase = float(first["battery_discharge_w"] - pre_last["battery_discharge_w"]) if pre_last is not None else 0.0
    immediate_grid_import_drop = float(pre_last["grid_import_w"] - first["grid_import_w"]) if pre_last is not None else 0.0

    # Local power balance during an outage should be satisfied without grid exchange.
    local_residual = (
        event["pv_ac_power_w"] + event["battery_discharge_w"]
        - event["load_power_w"] - event["battery_charge_w"]
    ).abs()
    max_local_balance_residual = float(local_residual.max())
    max_unmet_load = float(event["unmet_load_w"].max())
    unmet_energy_wh = float(event["unmet_load_w"].sum() * interval.total_seconds() / 3600)
    requested_energy_wh = float(event["load_requested_power_w"].sum() * interval.total_seconds() / 3600)
    served_fraction = (
        max(0.0, 1.0 - unmet_energy_wh / requested_energy_wh)
        if requested_energy_wh > 0 else 1.0
    )

    grid_loss_supported = event["grid_available"].eq(False).all() and abs(mean_grid_import) < 1e-6 and abs(mean_grid_export) < 1e-6
    islanding_supported = islanded_fraction >= 0.95
    physics_supported = max_local_balance_residual <= 1e-6
    full_load_supported = max_unmet_load <= 1e-6
    restored = bool(not post.empty and post["grid_available"].eq(True).all())
    full_backup_supported = grid_loss_supported and islanding_supported and physics_supported and full_load_supported
    load_shedding_supported = grid_loss_supported and islanding_supported and physics_supported and not full_load_supported

    zero_import_available = int(((work["grid_available"] == True) & (work["grid_import_w"].fillna(0) == 0)).sum())
    if full_backup_supported:
        finding = "Utility grid loss was followed by islanded backup operation; local PV/battery supply maintained the requested load until grid restoration."
        candidate_cause = "grid_outage_with_backup_operation"
    elif load_shedding_supported:
        finding = "Utility grid loss was followed by islanded operation, but available PV/battery supply could not meet all requested demand; the shortfall is explicitly recorded as unmet load."
        candidate_cause = "grid_outage_with_load_shedding"
    else:
        finding = "A grid-unavailable interval was detected, but the full backup/islanding interpretation is only partially supported."
        candidate_cause = "grid_outage"

    return {
        "finding": finding,
        "candidate_cause": candidate_cause,
        "confidence": "high" if (full_backup_supported or load_shedding_supported) and restored and not alarm_present else "medium",
        "data_window": {"start": start.isoformat(), "end": end.isoformat()},
        "measurements": [
            _measurement("outage_start", start.isoformat(), "timestamp"),
            _measurement("outage_end", end.isoformat(), "timestamp"),
            _measurement("outage_duration_minutes", round(duration_min, 1), "min"),
            _measurement("mean_pre_event_grid_import_w", round(pre_import, 1), "W"),
            _measurement("mean_outage_grid_import_w", round(mean_grid_import, 1), "W"),
            _measurement("mean_pre_event_battery_discharge_w", round(pre_batt, 1), "W"),
            _measurement("mean_outage_battery_discharge_w", round(outage_batt, 1), "W"),
            _measurement("immediate_battery_discharge_increase_w", round(immediate_battery_increase, 1), "W"),
            _measurement("immediate_grid_import_drop_w", round(immediate_grid_import_drop, 1), "W"),
            _measurement("battery_soc_drop_pct", round(soc_drop, 2), "%"),
            _measurement("islanded_state_fraction", round(islanded_fraction, 3), "fraction"),
            _measurement("max_local_power_balance_residual_w", round(max_local_balance_residual, 6), "W"),
            _measurement("max_unmet_load_w", round(max_unmet_load, 2), "W"),
            _measurement("unmet_load_energy_wh", round(unmet_energy_wh, 2), "Wh"),
            _measurement("requested_load_served_fraction", round(served_fraction, 6), "fraction"),
            _measurement("grid_restored_after_event", restored, "boolean"),
        ],
        "alternatives_checked": [
            {
                "cause": "self_sufficient_zero_grid_import",
                "supported": False,
                "evidence": {
                    "grid_available_false_during_event": True,
                    "zero_import_while_grid_available_intervals_elsewhere": zero_import_available,
                    "interpretation": "Zero import alone is not used as outage evidence.",
                },
            },
            {
                "cause": "inverter_fault",
                "supported": alarm_present,
                "evidence": {"alarm_present_during_event": alarm_present, "islanded_state_fraction": round(islanded_fraction, 3)},
            },
            {
                "cause": "insufficient_local_backup_capacity",
                "supported": load_shedding_supported,
                "evidence": {
                    "max_unmet_load_w": round(max_unmet_load, 2),
                    "unmet_load_energy_wh": round(unmet_energy_wh, 2),
                    "requested_load_served_fraction": round(served_fraction, 6),
                },
            },
            {
                "cause": "missing_or_incomplete_telemetry",
                "supported": False,
                "evidence": {"missing_cells_in_event": missing_cells},
            },
        ],
        "data_quality": {"sufficient": True, "warnings": []},
        "assumptions": {
            "grid_available_semantics": "False means the local installation telemetry reports utility-grid unavailability.",
            "islanding_semantics": "inverter_operating_state='islanded' represents the controlled demo's local backup operating state.",
            "load_continuity_check": "During the outage, PV plus battery discharge must balance served load plus battery charging with no grid exchange.",
            "load_shedding_semantics": "Requested demand is load_requested_power_w; load_power_w is actual served load; any shortfall is explicit in unmet_load_w.",
        },
    }
