from __future__ import annotations

import pandas as pd

from src.analytics.energy_balance import energy_balance
from src.analytics.financial import financial_metrics
from src.analytics.sustainability import sustainability_metrics
from src.analytics.battery import battery_runway


def _window(df: pd.DataFrame, days: int | None = 30) -> pd.DataFrame:
    if not days or df.empty: return df.copy()
    ts = pd.to_datetime(df["timestamp"]); end = ts.max(); return df[ts >= end - pd.Timedelta(days=days)].copy()


def energy_summary(df: pd.DataFrame, interval_minutes: int, days: int = 30) -> dict:
    w = _window(df, days); result = energy_balance(w, interval_minutes)
    result["data_window"] = {"start": pd.to_datetime(w["timestamp"]).min().isoformat(), "end": pd.to_datetime(w["timestamp"]).max().isoformat()}
    return result


def financial_summary(df: pd.DataFrame, config: dict) -> dict:
    sim, fin = config["simulation"], config["financial"]; w = df.copy()
    eb = energy_balance(w, sim["interval_minutes"])
    days = (pd.to_datetime(w["timestamp"]).max() - pd.to_datetime(w["timestamp"]).min()).total_seconds()/86400 + sim["interval_minutes"]/1440
    result = financial_metrics(eb["solar_self_consumed_kwh"], fin["import_tariff_per_kwh"], fin["capex"], fin.get("maintenance_cost_to_date", 0), days)
    result["assumptions"].update({"currency": fin["currency"], "export_tariff_per_kwh": fin.get("export_tariff_per_kwh", 0), "avoided_grid_energy_proxy": "PV generation minus grid export; synthetic-demo estimate"})
    result["data_window"] = {"start": pd.to_datetime(w["timestamp"]).min().isoformat(), "end": pd.to_datetime(w["timestamp"]).max().isoformat()}
    return result


def sustainability_summary(df: pd.DataFrame, config: dict, days: int = 30) -> dict:
    sim, sus = config["simulation"], config["sustainability"]; w = _window(df, days); eb = energy_balance(w, sim["interval_minutes"])
    s = sustainability_metrics(eb["solar_self_consumed_kwh"], sus["grid_emissions_factor_kg_per_kwh"])
    s.update({"renewable_fraction_pct": round(100*eb["solar_self_consumed_kwh"]/eb["consumption_kwh"],1) if eb["consumption_kwh"] else None, "solar_self_consumed_kwh": eb["solar_self_consumed_kwh"], "consumption_kwh": eb["consumption_kwh"]})
    s["assumptions"].update({"emissions_factor_source": sus.get("emissions_factor_source"), "emissions_factor_year": sus.get("emissions_factor_year"), "baseline": sus.get("baseline")})
    s["data_window"] = {"start": pd.to_datetime(w["timestamp"]).min().isoformat(), "end": pd.to_datetime(w["timestamp"]).max().isoformat()}
    return s


def battery_runway_summary(df: pd.DataFrame, config: dict) -> dict:
    complete = df.dropna(subset=["battery_soc_pct", "load_power_w"])
    if complete.empty: return {"estimated_runway_hours": None, "data_quality": {"sufficient": False}}
    row = complete.iloc[-1]; inst = config["installation"]
    usable = inst["battery_nominal_kwh"] * inst["battery_usable_fraction"]
    r = battery_runway(float(row["battery_soc_pct"]), usable, float(row["load_power_w"]), inst["battery_soc_min_pct"])
    r["data_window"] = {"start": pd.to_datetime(row["timestamp"]).isoformat(), "end": pd.to_datetime(row["timestamp"]).isoformat()}
    r["assumptions"]["capacity_source"] = "configured nominal usable capacity; no battery-health estimator is claimed"
    r["data_quality"] = {"sufficient": True, "warnings": []}
    return r
