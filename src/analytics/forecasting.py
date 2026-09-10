from __future__ import annotations

import pandas as pd


def forecast_generation(df: pd.DataFrame, horizon_days: int = 1, lookback_days: int = 7) -> dict:
    """Simple transparent persistence forecast from recent complete daily PV energy."""
    required = {"timestamp", "pv_ac_power_w"}
    if not required.issubset(df.columns) or df.empty:
        return {"status": "INSUFFICIENT_DATA", "forecast_kwh": None, "data_quality": {"sufficient": False}}
    x = df[list(required)].copy(); x["timestamp"] = pd.to_datetime(x["timestamp"]); x = x.dropna()
    if len(x) < 2:
        return {"status": "INSUFFICIENT_DATA", "forecast_kwh": None, "data_quality": {"sufficient": False}}
    dt_h = x["timestamp"].sort_values().diff().dropna().dt.total_seconds().median() / 3600
    daily = (x.assign(e=x["pv_ac_power_w"] * dt_h / 1000).groupby(x["timestamp"].dt.date)["e"].sum())
    recent = daily.iloc[-lookback_days:]
    if len(recent) < 3:
        return {"status": "INSUFFICIENT_DATA", "forecast_kwh": None, "data_quality": {"sufficient": False}}
    per_day = float(recent.median())
    return {
        "status": "PASS", "forecast_kwh": round(per_day * horizon_days, 2), "daily_persistence_kwh": round(per_day, 2),
        "horizon_days": horizon_days, "lookback_days_used": int(len(recent)),
        "method": "median daily persistence; no weather forecast", "data_quality": {"sufficient": True, "warnings": []},
    }
