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
