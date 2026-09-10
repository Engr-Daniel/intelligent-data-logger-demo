from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "data" / "processed" / "datalodger.sqlite"


def write_store(df: pd.DataFrame, path: Path = DEFAULT_DB) -> Path:
    """Persist operational telemetry to the local Datalodger stand-in.

    Experiment ground truth is intentionally excluded from this database and
    remains in ``data/ground_truth.json`` for scoring/evaluation only.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    telemetry = df.copy()
    timestamps = pd.to_datetime(telemetry["timestamp"])
    timezone = str(timestamps.dt.tz) if timestamps.dt.tz is not None else ""
    telemetry["timestamp"] = timestamps.astype(str)
    with sqlite3.connect(path) as conn:
        telemetry.to_sql("telemetry", conn, if_exists="replace", index=False)
        conn.execute("DROP TABLE IF EXISTS ground_truth_events")
        conn.execute("CREATE TABLE IF NOT EXISTS store_metadata (key TEXT PRIMARY KEY, value TEXT)")
        conn.execute("INSERT OR REPLACE INTO store_metadata(key, value) VALUES (?, ?)", ("timezone", timezone))
        conn.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry(timestamp)")
    return path


def load_telemetry(path: Path = DEFAULT_DB, start: str | None = None, end: str | None = None) -> pd.DataFrame:
    """Load telemetry from the persistent local store, optionally constrained by time."""
    query = "SELECT * FROM telemetry"
    params: list[str] = []
    clauses: list[str] = []
    if start is not None:
        clauses.append("timestamp >= ?")
        params.append(str(pd.Timestamp(start)))
    if end is not None:
        clauses.append("timestamp <= ?")
        params.append(str(pd.Timestamp(end)))
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY timestamp"
    with sqlite3.connect(path) as conn:
        df = pd.read_sql_query(query, conn, params=params)
        try:
            row = conn.execute("SELECT value FROM store_metadata WHERE key = ?", ("timezone",)).fetchone()
        except sqlite3.OperationalError:
            row = None  # backward compatibility with stores created before metadata was added
    if not df.empty:
        parsed = pd.to_datetime(df["timestamp"], utc=True)
        timezone = row[0] if row and row[0] else None
        df["timestamp"] = parsed.dt.tz_convert(timezone) if timezone else parsed.dt.tz_localize(None)
        if "grid_available" in df:
            df["grid_available"] = df["grid_available"].astype(bool)
    return df
