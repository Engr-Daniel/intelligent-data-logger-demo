from __future__ import annotations

import pandas as pd


def assess_data_availability(df: pd.DataFrame, target_date: str, required_fields: list[str] | None = None) -> dict:
    work = df.copy(); work["timestamp"] = pd.to_datetime(work["timestamp"])
    day = pd.Timestamp(target_date).date(); target = work[work["timestamp"].dt.date == day]
    if target.empty:
        return {"finding": f"No telemetry is available for {day}.", "candidate_cause": None, "confidence": "high", "measurements": [], "data_quality": {"sufficient": False, "warnings": ["No rows for requested date"]}}
    fields = required_fields or [c for c in target.columns if c != "timestamp"]
    fields = [c for c in fields if c in target]
    missing_rows = int(target[fields].isna().any(axis=1).sum())
    missing_cells = int(target[fields].isna().sum().sum())
    affected = sorted([c for c in fields if target[c].isna().any()])
    sufficient = missing_rows == 0
    return {
        "finding": (f"Telemetry for {day} is complete for the requested analysis." if sufficient else f"Telemetry is unavailable for part of {day}; a causal diagnosis should abstain for the affected interval."),
        "candidate_cause": "telemetry_unavailable" if not sufficient else "data_available",
        "confidence": "high",
        "data_window": {"start": target["timestamp"].min().isoformat(), "end": target["timestamp"].max().isoformat()},
        "measurements": [
            {"name": "rows_on_date", "value": int(len(target)), "unit": "rows"},
            {"name": "rows_with_missing_telemetry", "value": missing_rows, "unit": "rows"},
            {"name": "missing_cells", "value": missing_cells, "unit": "cells"},
            {"name": "affected_fields", "value": affected, "unit": "fields"},
        ],
        "alternatives_checked": [], "data_quality": {"sufficient": sufficient, "warnings": [] if sufficient else ["Missing telemetry prevents a complete diagnosis"]},
    }


def localize_data_unavailability(df: pd.DataFrame, target_date: str, required_fields: list[str] | None = None) -> dict:
    """Detect and localize contiguous missing-telemetry intervals from observations only."""
    work = df.copy()
    work["timestamp"] = pd.to_datetime(work["timestamp"])
    day = pd.Timestamp(target_date).date()
    target = work[work["timestamp"].dt.date == day].sort_values("timestamp").copy()
    if target.empty:
        return {
            "finding": f"No telemetry is available for {day}.", "candidate_cause": "telemetry_unavailable",
            "confidence": "high", "measurements": [],
            "data_quality": {"sufficient": False, "warnings": ["No rows for requested date"]},
        }
    fields = required_fields or [c for c in target.columns if c != "timestamp"]
    fields = [c for c in fields if c in target.columns]
    missing_mask = target[fields].isna().any(axis=1)
    missing = target.loc[missing_mask]
    if missing.empty:
        return {
            "finding": f"Telemetry for {day} is complete for the requested analysis.",
            "candidate_cause": "data_available", "confidence": "high",
            "data_window": {"start": target["timestamp"].min().isoformat(), "end": target["timestamp"].max().isoformat()},
            "measurements": [{"name": "rows_with_missing_telemetry", "value": 0, "unit": "rows"}],
            "alternatives_checked": [], "data_quality": {"sufficient": True, "warnings": []},
        }

    # Identify contiguous missing runs using the observed cadence. We report the
    # union window for this demo; run_count makes multiple gaps explicit.
    diffs = target["timestamp"].diff().dropna()
    cadence = diffs.mode().iloc[0] if not diffs.empty else pd.Timedelta(minutes=5)
    run_id = (missing["timestamp"].diff().fillna(cadence) > cadence * 1.5).cumsum()
    runs = missing.groupby(run_id)["timestamp"].agg(["min", "max", "count"])
    first_start = runs["min"].min()
    last_observed_missing = runs["max"].max()
    # End is the first expected timestamp after the final missing sample, matching
    # the half-open [start, end) convention used by the synthetic injection.
    inferred_end = last_observed_missing + cadence
    affected = sorted([c for c in fields if target[c].isna().any()])
    missing_cells = int(target[fields].isna().sum().sum())
    return {
        "finding": f"Telemetry is unavailable from {first_start.isoformat()} to {inferred_end.isoformat()}; causal diagnosis should abstain for that interval.",
        "candidate_cause": "telemetry_unavailable", "confidence": "high",
        "data_window": {"start": first_start.isoformat(), "end": inferred_end.isoformat()},
        "measurements": [
            {"name": "rows_with_missing_telemetry", "value": int(missing_mask.sum()), "unit": "rows"},
            {"name": "missing_cells", "value": missing_cells, "unit": "cells"},
            {"name": "affected_fields", "value": affected, "unit": "fields"},
            {"name": "gap_start", "value": first_start.isoformat(), "unit": "timestamp"},
            {"name": "gap_end", "value": inferred_end.isoformat(), "unit": "timestamp"},
            {"name": "gap_duration_minutes", "value": round((inferred_end-first_start).total_seconds()/60, 1), "unit": "minutes"},
            {"name": "contiguous_gap_count", "value": int(len(runs)), "unit": "gaps"},
        ],
        "alternatives_checked": [],
        "data_quality": {"sufficient": False, "warnings": ["Missing telemetry prevents diagnosis inside the localized interval"]},
    }
