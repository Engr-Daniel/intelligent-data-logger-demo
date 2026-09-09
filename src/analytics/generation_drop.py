from __future__ import annotations

import pandas as pd


def _measurement(name: str, value, unit: str | None = None) -> dict:
    item = {"name": name, "value": value}
    if unit:
        item["unit"] = unit
    return item


def analyze_generation_drop(
    df: pd.DataFrame,
    target_date: str | pd.Timestamp | None = None,
    minimum_drop_fraction: float = 0.20,
) -> dict:
    """Diagnose a daytime PV production drop using weather and inverter evidence.

    The target day is compared with the same daytime hours on surrounding days.
    The routine intentionally separates a weather-driven generation drop from an
    inverter/fault-driven drop and returns a structured, auditable result.
    """
    required = {
        "timestamp",
        "pv_ac_power_w",
        "irradiance_wm2",
        "inverter_alarm_code",
        "inverter_operating_state",
        "inverter_temp_c",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        return {
            "finding": "Telemetry is missing fields required to diagnose a production drop.",
            "candidate_cause": None,
            "confidence": "low",
            "measurements": [],
            "alternatives_checked": [],
            "data_quality": {"sufficient": False, "warnings": [f"Missing columns: {', '.join(missing)}"]},
        }

    work = df.copy()
    work["timestamp"] = pd.to_datetime(work["timestamp"])
    if work.empty:
        return {
            "finding": "No telemetry is available.",
            "candidate_cause": None,
            "confidence": "low",
            "measurements": [],
            "alternatives_checked": [],
            "data_quality": {"sufficient": False, "warnings": ["Empty telemetry"]},
        }

    if target_date is None:
        # Select the date with the lowest median daytime irradiance among days
        # having meaningful daylight, which makes the synthetic demo query
        # "why did production drop?" deterministic without ground-truth access.
        daylight = work[work["irradiance_wm2"] > 100].copy()
        if daylight.empty:
            return {
                "finding": "There is not enough daylight telemetry to evaluate PV production.",
                "candidate_cause": None,
                "confidence": "low",
                "measurements": [],
                "alternatives_checked": [],
                "data_quality": {"sufficient": False, "warnings": ["No daylight samples above 100 W/m²"]},
            }
        daily_irr = daylight.groupby(daylight["timestamp"].dt.date)["irradiance_wm2"].median()
        target_day = pd.Timestamp(daily_irr.idxmin()).date()
    else:
        target_day = pd.Timestamp(target_date).date()

    target = work[work["timestamp"].dt.date == target_day].copy()
    target = target[(target["timestamp"].dt.hour >= 9) & (target["timestamp"].dt.hour < 16)]
    if target.empty:
        return {
            "finding": f"No daytime telemetry is available for {target_day}.",
            "candidate_cause": None,
            "confidence": "low",
            "measurements": [],
            "alternatives_checked": [],
            "data_quality": {"sufficient": False, "warnings": ["Missing target-day daytime telemetry"]},
        }

    day = pd.Timestamp(target_day)
    baseline_dates = {(day + pd.Timedelta(days=d)).date() for d in (-3, -2, -1, 1, 2, 3)}
    baseline = work[work["timestamp"].dt.date.isin(baseline_dates)].copy()
    baseline = baseline[(baseline["timestamp"].dt.hour >= 9) & (baseline["timestamp"].dt.hour < 16)]
    baseline = baseline[baseline["irradiance_wm2"] > 100]

    if baseline.empty:
        return {
            "finding": "A production drop is suspected, but there is insufficient surrounding-day baseline data.",
            "candidate_cause": "undetermined",
            "confidence": "low",
            "measurements": [],
            "alternatives_checked": [],
            "data_quality": {"sufficient": False, "warnings": ["Insufficient baseline days"]},
        }

    target_pv = float(target["pv_ac_power_w"].mean())
    baseline_pv = float(baseline["pv_ac_power_w"].mean())
    target_irr = float(target["irradiance_wm2"].mean())
    baseline_irr = float(baseline["irradiance_wm2"].mean())
    pv_drop_fraction = max(0.0, 1.0 - target_pv / baseline_pv) if baseline_pv > 0 else 0.0
    irr_drop_fraction = max(0.0, 1.0 - target_irr / baseline_irr) if baseline_irr > 0 else 0.0

    alarms = target["inverter_alarm_code"].fillna("").astype(str)
    has_alarm = bool((alarms.str.len() > 0).any())
    abnormal_state = bool((target["inverter_operating_state"].fillna("normal") != "normal").any())
    max_temp = float(target["inverter_temp_c"].max())
    missing_cells = int(target[list(required - {"timestamp", "inverter_alarm_code"})].isna().sum().sum())

    significant_drop = pv_drop_fraction >= minimum_drop_fraction
    operational_event_present = has_alarm or abnormal_state
    weather_supported = significant_drop and irr_drop_fraction >= minimum_drop_fraction and not operational_event_present
    inverter_fault_supported = significant_drop and operational_event_present and irr_drop_fraction < minimum_drop_fraction
    limited_impact_event_supported = operational_event_present and not significant_drop
    thermal_supported = significant_drop and max_temp >= 75 and not weather_supported
    missing_supported = missing_cells > 0

    alternatives = [
        {
            "cause": "weather_related_low_irradiance",
            "supported": weather_supported,
            "evidence": {
                "pv_drop_pct_vs_surrounding_days": round(100 * pv_drop_fraction, 1),
                "irradiance_drop_pct_vs_surrounding_days": round(100 * irr_drop_fraction, 1),
                "inverter_alarm_present": has_alarm,
            },
        },
        {
            "cause": "inverter_fault_or_derating",
            "supported": inverter_fault_supported,
            "evidence": {
                "inverter_alarm_present": has_alarm,
                "abnormal_operating_state_present": abnormal_state,
                "irradiance_drop_pct_vs_surrounding_days": round(100 * irr_drop_fraction, 1),
                "pv_drop_pct_vs_surrounding_days": round(100 * pv_drop_fraction, 1),
            },
        },
        {
            "cause": "inverter_event_limited_energy_impact",
            "supported": limited_impact_event_supported,
            "evidence": {
                "inverter_alarm_present": has_alarm,
                "abnormal_operating_state_present": abnormal_state,
                "pv_drop_pct_vs_surrounding_days": round(100 * pv_drop_fraction, 1),
                "material_daily_drop_threshold_pct": round(100 * minimum_drop_fraction, 1),
            },
        },
        {
            "cause": "thermal_derating",
            "supported": thermal_supported,
            "evidence": {"max_inverter_temp_c": round(max_temp, 1)},
        },
        {
            "cause": "missing_or_incomplete_data",
            "supported": missing_supported,
            "evidence": {"missing_cells_in_target_window": missing_cells},
        },
    ]

    if missing_supported:
        finding = "The target window contains missing telemetry, so the available evidence is insufficient for a confident production-drop diagnosis."
        cause = "undetermined"
        confidence = "low"
    elif weather_supported:
        finding = "PV production was materially lower and the drop closely tracked lower irradiance, with no inverter alarm or abnormal operating state."
        cause = "weather_related_low_irradiance"
        confidence = "high"
    elif inverter_fault_supported:
        finding = "PV production fell without a comparable irradiance reduction, while inverter fault/derating evidence was present."
        cause = "inverter_fault_or_derating"
        confidence = "high"
    elif limited_impact_event_supported:
        finding = (
            "An inverter alarm or abnormal operating state occurred during the selected day, but the day does not show a material "
            "production reduction versus surrounding days. The operational event should be reported, while its full-day energy impact appears limited."
        )
        cause = "inverter_event_limited_energy_impact"
        confidence = "high"
    elif significant_drop:
        finding = "PV production was lower than surrounding days, but the available evidence does not isolate one cause confidently."
        cause = "undetermined"
        confidence = "medium"
    else:
        finding = "The selected day does not show a material PV production drop versus surrounding days, and no inverter alarm or abnormal operating state was detected in the analysis window."
        cause = "no_material_generation_anomaly"
        confidence = "medium"

    return {
        "finding": finding,
        "candidate_cause": cause,
        "confidence": confidence,
        "data_window": {
            "start": target["timestamp"].min().isoformat(),
            "end": target["timestamp"].max().isoformat(),
        },
        "measurements": [
            _measurement("target_mean_pv_power_w", round(target_pv, 1), "W"),
            _measurement("baseline_mean_pv_power_w", round(baseline_pv, 1), "W"),
            _measurement("pv_drop_pct_vs_surrounding_days", round(100 * pv_drop_fraction, 1), "%"),
            _measurement("target_mean_irradiance_wm2", round(target_irr, 1), "W/m2"),
            _measurement("baseline_mean_irradiance_wm2", round(baseline_irr, 1), "W/m2"),
            _measurement("irradiance_drop_pct_vs_surrounding_days", round(100 * irr_drop_fraction, 1), "%"),
            _measurement("max_inverter_temp_c", round(max_temp, 1), "degC"),
        ],
        "alternatives_checked": alternatives,
        "data_quality": {
            "sufficient": not missing_supported,
            "warnings": [] if not missing_supported else ["Missing telemetry exists in the target window"],
        },
    }
