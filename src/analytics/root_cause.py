from __future__ import annotations

import pandas as pd


def _evidence(name: str, value, unit: str | None = None) -> dict:
    item = {"name": name, "value": value}
    if unit:
        item["unit"] = unit
    return item


def diagnose_overload(df: pd.DataFrame, inverter_rating_w: float) -> dict:
    required = {
        "timestamp",
        "load_power_w",
        "battery_discharge_w",
        "inverter_alarm_code",
        "irradiance_wm2",
        "grid_available",
        "inverter_temp_c",
    }
    missing_columns = sorted(required - set(df.columns))
    if missing_columns:
        return {
            "finding": "The selected telemetry is missing fields required for a defensible diagnosis.",
            "candidate_cause": None,
            "confidence": "low",
            "measurements": [],
            "alternatives_checked": [],
            "data_quality": {"sufficient": False, "warnings": [f"Missing columns: {', '.join(missing_columns)}"]},
        }

    alarm_series = df["inverter_alarm_code"].fillna("").astype(str)
    alarm_rows = df[alarm_series.str.len() > 0]
    if alarm_rows.empty:
        return {
            "finding": "No inverter alarm was found in the selected data.",
            "candidate_cause": None,
            "confidence": "low",
            "measurements": [],
            "alternatives_checked": [],
            "data_quality": {"sufficient": True, "warnings": []},
        }

    alarm_row = alarm_rows.iloc[0]
    alarm_time = alarm_row["timestamp"]
    start = alarm_time - pd.Timedelta(minutes=30)
    end = alarm_time + pd.Timedelta(minutes=10)
    window = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)].copy()
    if window.empty:
        return {
            "finding": "The alarm was found, but the surrounding diagnostic window is unavailable.",
            "candidate_cause": "undetermined",
            "confidence": "low",
            "measurements": [],
            "alternatives_checked": [],
            "data_quality": {"sufficient": False, "warnings": ["Empty diagnostic window"]},
        }

    deltas = window["timestamp"].sort_values().diff().dropna().dt.total_seconds().div(60)
    interval_min = float(deltas.median()) if not deltas.empty else 5.0
    above = window[window["load_power_w"] > inverter_rating_w]
    duration = float(len(above) * interval_min)
    peak_load = float(window["load_power_w"].max())
    peak_discharge = float(window["battery_discharge_w"].max())
    alarm_code = str(alarm_row["inverter_alarm_code"])
    median_irradiance = float(window["irradiance_wm2"].median())
    grid_available_fraction = float(window["grid_available"].astype(float).mean())
    max_inverter_temp = float(window["inverter_temp_c"].max())
    diagnostic_value_columns = list(required - {"timestamp", "inverter_alarm_code"})
    missing_cells = int(window[diagnostic_value_columns].isna().sum().sum())

    overload_supported = duration >= 10 and alarm_code.startswith("OVERLOAD")
    grid_outage_supported = grid_available_fraction < 0.5
    low_irradiance = median_irradiance < 100.0
    weather_only_supported = low_irradiance and duration < 10 and not alarm_code.startswith("OVERLOAD")
    thermal_supported = max_inverter_temp >= 75.0 and not overload_supported
    missing_data_supported = missing_cells > 0

    alternatives = [
        {
            "cause": "grid_outage",
            "supported": grid_outage_supported,
            "evidence": {"grid_available_fraction": round(grid_available_fraction, 3)},
        },
        {
            "cause": "weather_related_generation_drop_only",
            "supported": weather_only_supported,
            "evidence": {
                "median_irradiance_wm2": round(median_irradiance, 1),
                "duration_above_rating_min": round(duration, 1),
                "alarm_code": alarm_code,
            },
        },
        {
            "cause": "thermal_event_without_overload",
            "supported": thermal_supported,
            "evidence": {"max_inverter_temp_c": round(max_inverter_temp, 1), "overload_supported": overload_supported},
        },
        {
            "cause": "missing_or_incomplete_data",
            "supported": missing_data_supported,
            "evidence": {"missing_cells_in_window": missing_cells},
        },
    ]

    data_sufficient = not missing_data_supported
    supported = overload_supported and data_sufficient
    return {
        "finding": "Sustained overload preceded the inverter alarm." if supported else "An inverter alarm occurred, but overload evidence is incomplete.",
        "candidate_cause": "overload" if supported else "undetermined",
        "confidence": "high" if supported else "medium",
        "data_window": {"start": start.isoformat(), "end": end.isoformat()},
        "measurements": [
            _evidence("peak_load_w", round(peak_load, 1), "W"),
            _evidence("inverter_rating_w", inverter_rating_w, "W"),
            _evidence("duration_above_rating_min", round(duration, 1), "min"),
            _evidence("peak_battery_discharge_w", round(peak_discharge, 1), "W"),
            _evidence("max_inverter_temp_c", round(max_inverter_temp, 1), "degC"),
            _evidence("alarm_code", alarm_code, "categorical"),
        ],
        "alternatives_checked": alternatives,
        "data_quality": {
            "sufficient": data_sufficient,
            "warnings": [] if data_sufficient else ["Missing telemetry exists in the diagnostic window"],
        },
    }
