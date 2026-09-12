from __future__ import annotations

import pandas as pd


def instantaneous_balance_residual_w(df: pd.DataFrame) -> pd.Series:
    """Power-balance residual: sources minus sinks for every telemetry row."""
    return (
        df["pv_ac_power_w"]
        + df["grid_import_w"]
        + df["battery_discharge_w"]
        - df["load_power_w"]
        - df["battery_charge_w"]
        - df["grid_export_w"]
    )


def energy_balance(df: pd.DataFrame, interval_minutes: int = 5) -> dict:
    dt_h = interval_minutes / 60
    pv_kwh = df["pv_ac_power_w"].sum() * dt_h / 1000
    load_kwh = df["load_power_w"].sum() * dt_h / 1000
    requested_load_kwh = (
        df["load_requested_power_w"].sum() * dt_h / 1000
        if "load_requested_power_w" in df else load_kwh
    )
    unmet_load_kwh = (
        df["unmet_load_w"].sum() * dt_h / 1000
        if "unmet_load_w" in df else max(0.0, requested_load_kwh - load_kwh)
    )
    imp_kwh = df["grid_import_w"].sum() * dt_h / 1000
    exp_kwh = df["grid_export_w"].sum() * dt_h / 1000
    solar_used_kwh = max(0.0, pv_kwh - exp_kwh)
    residual = instantaneous_balance_residual_w(df)
    return {
        "pv_generation_kwh": round(pv_kwh, 2),
        "consumption_kwh": round(load_kwh, 2),
        "requested_consumption_kwh": round(requested_load_kwh, 2),
        "unmet_load_kwh": round(unmet_load_kwh, 2),
        "load_served_pct": round(100 * load_kwh / requested_load_kwh, 2) if requested_load_kwh else None,
        "grid_import_kwh": round(imp_kwh, 2),
        "grid_export_kwh": round(exp_kwh, 2),
        "solar_self_consumed_kwh": round(solar_used_kwh, 2),
        "self_sufficiency_pct": round(100 * solar_used_kwh / load_kwh, 1) if load_kwh else None,
        "max_abs_power_balance_residual_w": float(residual.abs().max()),
    }
