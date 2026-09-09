from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config" / "installation.yaml"
OUT = ROOT / "data" / "processed" / "telemetry.csv"
GT = ROOT / "data" / "ground_truth.json"


def load_config(path: Path = CONFIG) -> dict:
    return yaml.safe_load(path.read_text())


def _irradiance_profile(index: pd.DatetimeIndex, rng: np.random.Generator) -> np.ndarray:
    hours = index.hour.to_numpy() + index.minute.to_numpy() / 60
    daylight = np.clip(np.sin(np.pi * (hours - 6) / 12), 0, None)
    cloud = np.clip(rng.normal(0.9, 0.12, len(index)), 0.45, 1.0)
    return 950 * daylight * cloud


def _load_profile(index: pd.DatetimeIndex, rng: np.random.Generator) -> np.ndarray:
    hours = index.hour.to_numpy() + index.minute.to_numpy() / 60
    base = 450 + rng.normal(0, 40, len(index))
    morning = 700 * np.exp(-0.5 * ((hours - 7.0) / 1.2) ** 2)
    evening = 1200 * np.exp(-0.5 * ((hours - 20.0) / 2.0) ** 2)
    midday = 300 * np.exp(-0.5 * ((hours - 13.0) / 2.5) ** 2)
    return np.clip(base + morning + evening + midday, 150, None)


def _apply_overload_event(
    idx: pd.DatetimeIndex,
    pv_ac: np.ndarray,
    load: np.ndarray,
    timezone: str,
    overload_start: pd.Timestamp | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, pd.Timestamp, pd.Timestamp, pd.Timestamp]:
    """Inject load + inverter effects before downstream energy balancing.

    Keeping inverter derating here (before the battery/grid loop) ensures all
    downstream flows are computed from the actually recorded inverter output.
    """
    if overload_start is None:
        overload_start = pd.Timestamp("2026-08-08 19:30", tz=timezone)
    elif overload_start.tzinfo is None:
        overload_start = overload_start.tz_localize(timezone)
    else:
        overload_start = overload_start.tz_convert(timezone)

    overload_end = overload_start + pd.Timedelta(minutes=35)
    overload_mask = (idx >= overload_start) & (idx <= overload_end)
    load = load.copy()
    pv_ac = pv_ac.copy()
    load[overload_mask] += 4700

    alarm_time = overload_start + pd.Timedelta(minutes=25)
    alarm_mask = (idx >= alarm_time) & (idx <= overload_end)
    state = np.array(["normal"] * len(idx), dtype=object)
    alarm = np.array([""] * len(idx), dtype=object)
    state[alarm_mask] = "derated"
    alarm[alarm_mask] = "OVERLOAD_02"
    pv_ac[alarm_mask] *= 0.85

    return pv_ac, load, state, alarm, overload_start, overload_end, alarm_time


def simulate(config: dict, overload_start: pd.Timestamp | None = None) -> tuple[pd.DataFrame, dict]:
    inst = config["installation"]
    sim = config["simulation"]
    rng = np.random.default_rng(sim["seed"])
    freq = f"{sim['interval_minutes']}min"
    periods = int(sim["days"] * 24 * 60 / sim["interval_minutes"])
    idx = pd.date_range("2026-08-01", periods=periods, freq=freq, tz=inst["timezone"])

    irradiance = _irradiance_profile(idx, rng)
    hours = idx.hour.to_numpy() + idx.minute.to_numpy() / 60
    temp = 27 + 6 * np.clip(np.sin(np.pi * (hours - 7) / 12), 0, None)
    pv_dc = inst["pv_kwp"] * 1000 * (irradiance / 1000) * (1 - 0.004 * np.maximum(temp - 25, 0))
    pv_ac = np.minimum(pv_dc * 0.965, inst["inverter_rating_w"])
    load = _load_profile(idx, rng)

    # Fault effects are applied before the battery/grid energy-balance loop.
    pv_ac, load, state, alarm, overload_start, overload_end, alarm_time = _apply_overload_event(
        idx, pv_ac, load, inst["timezone"], overload_start
    )

    # Synthetic but explicit diagnostic channels for alternative-cause checks.
    grid_available = np.ones(len(idx), dtype=bool)
    inverter_temp = temp + 8 + 0.0009 * load
    alarm_mask = alarm == "OVERLOAD_02"
    inverter_temp[alarm_mask] += 4

    dt_h = sim["interval_minutes"] / 60
    usable_kwh = inst["battery_nominal_kwh"] * inst["battery_usable_fraction"]
    usable_wh = usable_kwh * 1000
    soc = np.empty(len(idx))
    charge = np.zeros(len(idx))
    discharge = np.zeros(len(idx))
    grid_import = np.zeros(len(idx))
    grid_export = np.zeros(len(idx))

    stored = usable_wh * inst["initial_soc_pct"] / 100
    min_wh = usable_wh * inst["battery_soc_min_pct"] / 100
    max_wh = usable_wh * inst["battery_soc_max_pct"] / 100

    for i in range(len(idx)):
        net = pv_ac[i] - load[i]
        if net >= 0:
            max_possible = (max_wh - stored) / (dt_h * inst["battery_charge_efficiency"])
            p = max(0, min(net, inst["battery_max_charge_w"], max_possible))
            charge[i] = p
            stored += p * dt_h * inst["battery_charge_efficiency"]
            grid_export[i] = max(0, net - p) if grid_available[i] else 0.0
        else:
            demand = -net
            max_possible = (stored - min_wh) * inst["battery_discharge_efficiency"] / dt_h
            p = max(0, min(demand, inst["battery_max_discharge_w"], max_possible))
            discharge[i] = p
            stored -= p * dt_h / inst["battery_discharge_efficiency"]
            grid_import[i] = max(0, demand - p) if grid_available[i] else 0.0
        soc[i] = 100 * stored / usable_wh

    df = pd.DataFrame(
        {
            "timestamp": idx,
            "irradiance_wm2": irradiance,
            "ambient_temp_c": temp,
            "inverter_temp_c": inverter_temp,
            "pv_ac_power_w": pv_ac,
            "load_power_w": load,
            "battery_soc_pct": soc,
            "battery_charge_w": charge,
            "battery_discharge_w": discharge,
            "grid_available": grid_available,
            "grid_import_w": grid_import,
            "grid_export_w": grid_export,
            "inverter_operating_state": state,
            "inverter_alarm_code": alarm,
        }
    )

    gt = {
        "events": [
            {
                "event_type": "customer_overload",
                "start": overload_start.isoformat(),
                "end": overload_end.isoformat(),
                "alarm_time": alarm_time.isoformat(),
                "affected_device": "inverter",
                "true_cause": "sustained load above inverter rating preceded overload alarm and derating",
                "alarm_code": "OVERLOAD_02",
            }
        ]
    }
    return df, gt


def main() -> None:
    cfg = load_config()
    df, gt = simulate(cfg)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    GT.write_text(json.dumps(gt, indent=2))
    print(f"Wrote {len(df):,} rows to {OUT}")
    print(f"Wrote ground truth to {GT}")


if __name__ == "__main__":
    main()
