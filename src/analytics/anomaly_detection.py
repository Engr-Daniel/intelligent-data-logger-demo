from __future__ import annotations

import numpy as np
import pandas as pd


def detect_anomalies(series: pd.Series, method: str = "iqr", z_threshold: float = 3.0) -> dict:
    values = pd.to_numeric(series, errors="coerce")
    valid = values.dropna()
    if len(valid) < 8:
        return {"status": "INSUFFICIENT_DATA", "anomaly_indices": [], "count": 0}
    if method == "zscore":
        std = float(valid.std(ddof=0))
        mask = pd.Series(False, index=values.index) if std == 0 else ((values - valid.mean()).abs() / std > z_threshold)
    elif method == "iqr":
        q1, q3 = valid.quantile([0.25, 0.75])
        iqr = q3 - q1
        mask = (values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr)
    else:
        raise ValueError("method must be 'iqr' or 'zscore'")
    indices = [int(i) if isinstance(i, (int, np.integer)) else str(i) for i in values.index[mask.fillna(False)]]
    return {"status": "PASS", "method": method, "anomaly_indices": indices, "count": len(indices), "valid_samples": int(len(valid))}


def summarize_inverter_anomalies(df: pd.DataFrame, inverter_rating_w: float) -> dict:
    """Summarize inverter events without inferring overload unless the event window supports it.

    This function is deliberately narrower than a general root-cause engine.  It
    may identify an overload-related event only when the alarm-associated window
    contains sustained above-rating load and an overload-coded alarm.  Otherwise
    it reports the observed alarm/derating descriptively and leaves cause
    undetermined.
    """
    required = {
        "timestamp",
        "load_power_w",
        "inverter_alarm_code",
        "inverter_operating_state",
        "inverter_temp_c",
    }
    missing_columns = sorted(required - set(df.columns))
    if missing_columns:
        return {
            "finding": "Insufficient telemetry for inverter anomaly analysis.",
            "candidate_cause": None,
            "confidence": "low",
            "measurements": [],
            "alternatives_checked": [],
            "data_quality": {
                "sufficient": False,
                "warnings": [f"Missing columns: {', '.join(missing_columns)}"],
            },
        }

    work = df.copy()
    work["timestamp"] = pd.to_datetime(work["timestamp"])
    alarms = work[work["inverter_alarm_code"].fillna("").astype(str).str.len() > 0]
    abnormal = work[work["inverter_operating_state"].fillna("normal") != "normal"]

    if alarms.empty and abnormal.empty:
        return {
            "finding": "No inverter alarms or abnormal operating states were observed.",
            "candidate_cause": "no_material_inverter_anomaly",
            "confidence": "medium",
            "data_window": {
                "start": work["timestamp"].min().isoformat(),
                "end": work["timestamp"].max().isoformat(),
            },
            "measurements": [
                {"name": "alarm_rows", "value": 0, "unit": "rows"},
                {"name": "abnormal_state_rows", "value": 0, "unit": "rows"},
            ],
            "alternatives_checked": [],
            "data_quality": {"sufficient": True, "warnings": []},
        }

    # Anchor diagnosis to the first observed alarm.  If there is only an
    # abnormal state, use its first row and remain descriptive rather than
    # inventing an alarm-associated cause.
    anchor = alarms.iloc[0] if not alarms.empty else abnormal.iloc[0]
    anchor_time = anchor["timestamp"]
    start = anchor_time - pd.Timedelta(minutes=30)
    end = anchor_time + pd.Timedelta(minutes=10)
    window = work[(work["timestamp"] >= start) & (work["timestamp"] <= end)].copy()

    deltas = window["timestamp"].sort_values().diff().dropna().dt.total_seconds().div(60)
    interval_min = float(deltas.median()) if not deltas.empty else 5.0
    above = window[window["load_power_w"] > inverter_rating_w]
    duration_above = float(len(above) * interval_min)
    peak_load = float(window["load_power_w"].max()) if not window.empty else float("nan")
    max_temp = float(window["inverter_temp_c"].max()) if not window.empty else float("nan")
    alarm_codes = sorted({str(x) for x in window["inverter_alarm_code"].dropna() if str(x)})
    overload_alarm_present = any(code.startswith("OVERLOAD") for code in alarm_codes)
    overload_supported = overload_alarm_present and duration_above >= 10.0
    missing_cells = int(window[list(required - {"timestamp", "inverter_alarm_code"})].isna().sum().sum())

    alternatives = [
        {
            "cause": "thermal_event_without_overload",
            "supported": bool(max_temp >= 75.0 and not overload_supported),
            "evidence": {"max_inverter_temp_c": round(max_temp, 1), "overload_supported": overload_supported},
        },
        {
            "cause": "alarm_or_derating_without_overload_evidence",
            "supported": bool((not alarms.empty or not abnormal.empty) and not overload_supported),
            "evidence": {
                "alarm_codes": alarm_codes,
                "duration_above_rating_min": round(duration_above, 1),
            },
        },
        {
            "cause": "missing_or_incomplete_data",
            "supported": missing_cells > 0,
            "evidence": {"missing_cells_in_window": missing_cells},
        },
    ]

    data_sufficient = missing_cells == 0
    if overload_supported and data_sufficient:
        finding = "Inverter alarm/derating was observed with sustained load above the inverter rating in the alarm window."
        cause = "overload_related_inverter_event"
        confidence = "high"
    elif not data_sufficient:
        finding = "An inverter alarm/abnormal state was observed, but missing telemetry prevents a reliable causal summary."
        cause = "undetermined"
        confidence = "low"
    else:
        finding = "An inverter alarm/abnormal state was observed, but the alarm window does not support an overload-related cause."
        cause = "undetermined"
        confidence = "medium"

    return {
        "finding": finding,
        "candidate_cause": cause,
        "confidence": confidence,
        "data_window": {"start": start.isoformat(), "end": end.isoformat()},
        "measurements": [
            {"name": "alarm_rows", "value": int(len(alarms)), "unit": "rows"},
            {"name": "abnormal_state_rows", "value": int(len(abnormal)), "unit": "rows"},
            {"name": "rows_above_inverter_rating_in_event_window", "value": int(len(above)), "unit": "rows"},
            {"name": "duration_above_rating_min", "value": round(duration_above, 1), "unit": "min"},
            {"name": "peak_load_w", "value": round(peak_load, 1), "unit": "W"},
            {"name": "inverter_rating_w", "value": float(inverter_rating_w), "unit": "W"},
            {"name": "alarm_codes", "value": alarm_codes, "unit": "categorical"},
        ],
        "alternatives_checked": alternatives,
        "data_quality": {
            "sufficient": data_sufficient,
            "warnings": [] if data_sufficient else ["Missing telemetry exists in the diagnostic window"],
        },
    }
