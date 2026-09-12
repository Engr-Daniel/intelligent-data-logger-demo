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
DB = ROOT / "data" / "processed" / "datalodger.sqlite"


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


def simulate(
    config: dict,
    overload_start: pd.Timestamp | None = None,
    cloudy_day: str | pd.Timestamp | None = None,
) -> tuple[pd.DataFrame, dict]:
    inst = config["installation"]
    sim = config["simulation"]
    rng = np.random.default_rng(sim["seed"])
    freq = f"{sim['interval_minutes']}min"
    periods = int(sim["days"] * 24 * 60 / sim["interval_minutes"])
    idx = pd.date_range(sim.get("start", "2026-08-01"), periods=periods, freq=freq, tz=inst["timezone"])

    irradiance = _irradiance_profile(idx, rng)

    # M1 scenario: a weather-driven production drop. The irradiance reduction is
    # applied before PV conversion, so PV output follows the same physical chain
    # as ordinary weather variability.
    if cloudy_day is None:
        cloudy_day_ts = pd.Timestamp(sim.get("scenarios", {}).get("cloudy_day", "2026-08-05"), tz=inst["timezone"])
    else:
        cloudy_day_ts = pd.Timestamp(cloudy_day)
        if cloudy_day_ts.tzinfo is None:
            cloudy_day_ts = cloudy_day_ts.tz_localize(inst["timezone"])
        else:
            cloudy_day_ts = cloudy_day_ts.tz_convert(inst["timezone"])
    cloudy_mask = (idx.date == cloudy_day_ts.date()) & (idx.hour >= 9) & (idx.hour < 16)
    # Smooth, substantial cloud attenuation during the analysis window.
    irradiance[cloudy_mask] *= 0.38

    hours = idx.hour.to_numpy() + idx.minute.to_numpy() / 60
    temp = 27 + 6 * np.clip(np.sin(np.pi * (hours - 7) / 12), 0, None)
    pv_dc_ideal = inst["pv_kwp"] * 1000 * (irradiance / 1000) * (1 - 0.004 * np.maximum(temp - 25, 0))

    # M1 scenario: gradual multi-week PV performance decline (e.g. soiling).
    # This is applied as a smooth derating factor rather than an abrupt fault.
    scenarios = sim.get("scenarios", {})
    decline_start = pd.Timestamp(scenarios.get("efficiency_decline_start", "2026-08-20"), tz=inst["timezone"])
    decline_end = pd.Timestamp(scenarios.get("efficiency_decline_end", "2026-11-15"), tz=inst["timezone"])
    decline_fraction = float(scenarios.get("efficiency_decline_fraction", 0.08))
    decline_duration = decline_end - decline_start
    if decline_duration <= pd.Timedelta(0):
        raise ValueError("efficiency_decline_end must be after efficiency_decline_start")
    progress = np.asarray((idx - decline_start) / decline_duration, dtype=float)
    progress = np.clip(progress, 0.0, 1.0)
    performance_factor = 1.0 - decline_fraction * progress
    pv_dc = pv_dc_ideal * performance_factor
    nominal_eff = float(inst.get("inverter_nominal_efficiency", 0.965))
    pv_ac = np.minimum(pv_dc * nominal_eff, inst["inverter_rating_w"])
    load = _load_profile(idx, rng)

    # Fault effects are applied before the battery/grid energy-balance loop.
    pv_ac, load, state, alarm, overload_start, overload_end, alarm_time = _apply_overload_event(
        idx, pv_ac, load, inst["timezone"], overload_start
    )

    # Synthetic but explicit diagnostic channels for alternative-cause checks.
    grid_available = np.ones(len(idx), dtype=bool)

    # Required Scenario 6: utility-grid outage followed by backup/islanded operation.
    # The event is injected before dispatch so battery/grid flows are solved from the
    # actual grid state rather than edited after the fact. A configured backup
    # reserve is held while the grid is available and may be used during an outage.
    grid_outage_start = pd.Timestamp(scenarios.get("grid_outage_start", "2026-10-10T21:30:00"))
    if grid_outage_start.tzinfo is None:
        grid_outage_start = grid_outage_start.tz_localize(inst["timezone"])
    else:
        grid_outage_start = grid_outage_start.tz_convert(inst["timezone"])
    grid_outage_end = grid_outage_start + pd.Timedelta(minutes=int(scenarios.get("grid_outage_minutes", 60)))
    grid_outage_mask = (idx >= grid_outage_start) & (idx < grid_outage_end)
    grid_available[grid_outage_mask] = False
    state[grid_outage_mask] = "islanded"

    # ``load`` is requested customer demand before any islanded load shedding.
    # ``pv_ac`` is the available inverter AC output before any islanded curtailment.
    requested_load = load.copy()
    served_load = load.copy()
    unmet_load = np.zeros(len(idx))
    pv_available_ac = pv_ac.copy()
    pv_curtailed = np.zeros(len(idx))

    # Additional device-context channels from the experiment brief.
    daylight = np.clip(np.sin(np.pi * (hours - 6) / 12), 0, None)
    clear_sky_irradiance = 950 * daylight
    irradiance_ratio = np.divide(
        irradiance, clear_sky_irradiance, out=np.zeros_like(irradiance), where=clear_sky_irradiance > 1e-6
    )
    cloud_cover_pct = np.where(
        clear_sky_irradiance > 1e-6,
        100 * (1 - np.clip(irradiance_ratio, 0, 1)),
        100.0,
    )
    inverter_dc_voltage_v = np.where(pv_dc > 1, 330 + 25 * daylight, 0.0)
    inverter_dc_current_a = np.divide(
        pv_dc, inverter_dc_voltage_v, out=np.zeros_like(pv_dc), where=inverter_dc_voltage_v > 1e-9
    )

    dt_h = sim["interval_minutes"] / 60
    initial_usable_wh = inst["battery_nominal_kwh"] * inst["battery_usable_fraction"] * 1000
    degradation_start = pd.Timestamp(scenarios.get("battery_degradation_start", "2026-08-15"), tz=inst["timezone"])
    degradation_end = pd.Timestamp(scenarios.get("battery_degradation_end", "2026-11-28"), tz=inst["timezone"])
    capacity_loss = float(scenarios.get("battery_capacity_loss_fraction", 0.06))
    degradation_duration = degradation_end - degradation_start
    if degradation_duration <= pd.Timedelta(0):
        raise ValueError("battery_degradation_end must be after battery_degradation_start")
    degradation_progress = np.asarray((idx - degradation_start) / degradation_duration, dtype=float)
    degradation_progress = np.clip(degradation_progress, 0.0, 1.0)
    usable_capacity = initial_usable_wh * (1.0 - capacity_loss * degradation_progress)

    soc = np.empty(len(idx))
    stored_energy = np.empty(len(idx))
    charge = np.zeros(len(idx))
    discharge = np.zeros(len(idx))
    grid_import = np.zeros(len(idx))
    grid_export = np.zeros(len(idx))
    cycle_count = np.zeros(len(idx))

    stored = initial_usable_wh * inst["initial_soc_pct"] / 100
    cumulative_throughput_wh = 0.0

    for i in range(len(idx)):
        usable_wh = usable_capacity[i]
        min_wh = usable_wh * inst["battery_soc_min_pct"] / 100
        max_wh = usable_wh * inst["battery_soc_max_pct"] / 100
        # Capacity fade can lower the physical ceiling between intervals.
        stored = min(max(stored, min_wh), max_wh)

        # Dispatch is solved against requested demand and available PV. During
        # islanded operation, any supply shortfall is recorded explicitly as
        # unmet load, while surplus PV that cannot serve load or charge the
        # battery is curtailed. ``load_power_w`` and ``pv_ac_power_w`` therefore
        # represent power actually served/delivered, keeping the power-balance
        # identity valid for all outage parameterizations.
        net = pv_available_ac[i] - requested_load[i]
        if net >= 0:
            max_possible = (max_wh - stored) / (dt_h * inst["battery_charge_efficiency"])
            p = max(0, min(net, inst["battery_max_charge_w"], max_possible))
            charge[i] = p
            stored += p * dt_h * inst["battery_charge_efficiency"]
            if grid_available[i]:
                grid_export[i] = max(0, net - p)
            else:
                pv_curtailed[i] = max(0, net - p)
                pv_ac[i] = pv_available_ac[i] - pv_curtailed[i]
        else:
            demand = -net
            reserve_pct = float(inst.get("battery_backup_reserve_pct", inst["battery_soc_min_pct"]))
            discharge_floor_wh = min_wh if not grid_available[i] else usable_wh * reserve_pct / 100
            discharge_floor_wh = max(min_wh, min(discharge_floor_wh, max_wh))
            max_possible = (stored - discharge_floor_wh) * inst["battery_discharge_efficiency"] / dt_h
            p = max(0, min(demand, inst["battery_max_discharge_w"], max_possible))
            discharge[i] = p
            stored -= p * dt_h / inst["battery_discharge_efficiency"]
            if grid_available[i]:
                grid_import[i] = max(0, demand - p)
            else:
                unmet_load[i] = max(0, demand - p)
                served_load[i] = max(0, requested_load[i] - unmet_load[i])


        cumulative_throughput_wh += (charge[i] + discharge[i]) * dt_h
        cycle_count[i] = cumulative_throughput_wh / (2 * initial_usable_wh)
        stored_energy[i] = stored
        soc[i] = 100 * stored / usable_wh

    battery_temp = temp + 2.0 + 0.0012 * (charge + discharge)
    inverter_temp = temp + 8 + 0.0009 * served_load
    alarm_mask = alarm == "OVERLOAD_02"
    inverter_temp[alarm_mask] += 4

    df = pd.DataFrame(
        {
            "timestamp": idx,
            "irradiance_wm2": irradiance,
            "ambient_temp_c": temp,
            "cloud_cover_pct": cloud_cover_pct,
            "inverter_temp_c": inverter_temp,
            "inverter_dc_voltage_v": inverter_dc_voltage_v,
            "inverter_dc_current_a": inverter_dc_current_a,
            "pv_dc_power_w": pv_dc,
            "pv_available_ac_power_w": pv_available_ac,
            "pv_ac_power_w": pv_ac,
            "pv_curtailed_w": pv_curtailed,
            "inverter_efficiency": np.divide(pv_ac, pv_dc, out=np.zeros_like(pv_ac), where=pv_dc > 1e-9),
            "load_requested_power_w": requested_load,
            "load_power_w": served_load,
            "unmet_load_w": unmet_load,
            "battery_soc_pct": soc,
            "battery_stored_energy_wh": stored_energy,
            "battery_usable_capacity_wh": usable_capacity,
            "battery_charge_w": charge,
            "battery_discharge_w": discharge,
            "battery_cycle_count": cycle_count,
            "battery_temp_c": battery_temp,
            "grid_available": grid_available,
            "grid_import_w": grid_import,
            "grid_export_w": grid_export,
            "inverter_operating_state": state,
            "inverter_alarm_code": alarm,
        }
    )

    # M1 scenario: sensor dropout. Preserve the timeline but blank selected
    # telemetry fields so downstream data-quality checks can detect insufficiency.
    dropout_start = pd.Timestamp(scenarios.get("sensor_dropout_start", "2026-09-18T12:00:00"))
    if dropout_start.tzinfo is None:
        dropout_start = dropout_start.tz_localize(inst["timezone"])
    else:
        dropout_start = dropout_start.tz_convert(inst["timezone"])
    dropout_end = dropout_start + pd.Timedelta(minutes=int(scenarios.get("sensor_dropout_minutes", 45)))
    dropout_mask = (df["timestamp"] >= dropout_start) & (df["timestamp"] < dropout_end)
    dropout_fields = [
        "irradiance_wm2", "cloud_cover_pct", "inverter_temp_c", "inverter_dc_voltage_v",
        "inverter_dc_current_a", "pv_dc_power_w", "pv_ac_power_w", "inverter_efficiency",
        "battery_soc_pct", "battery_stored_energy_wh", "battery_temp_c",
        "battery_charge_w", "battery_discharge_w", "grid_import_w", "grid_export_w",
    ]
    df.loc[dropout_mask, dropout_fields] = np.nan

    gt = {
        "schema_version": 1,
        "synthetic": True,
        "events": [
            {
                "event_type": "cloudy_day_generation_drop",
                "start": pd.Timestamp(cloudy_day_ts.date(), tz=inst["timezone"]).replace(hour=9).isoformat(),
                "end": pd.Timestamp(cloudy_day_ts.date(), tz=inst["timezone"]).replace(hour=15, minute=55).isoformat(),
                "affected_device": "pv_inverter",
                "true_cause": "weather-driven irradiance reduction caused lower PV production without an inverter fault",
            },
            {
                "event_type": "customer_overload",
                "start": overload_start.isoformat(),
                "end": overload_end.isoformat(),
                "alarm_time": alarm_time.isoformat(),
                "affected_device": "inverter",
                "true_cause": "sustained load above inverter rating preceded overload alarm and derating",
                "alarm_code": "OVERLOAD_02",
            },
            {
                "event_type": "gradual_efficiency_decline",
                "start": decline_start.isoformat(),
                "end": decline_end.isoformat(),
                "affected_device": "pv_array",
                "true_cause": "smooth PV performance-factor decline simulating soiling/degradation",
                "injected_final_loss_fraction": decline_fraction,
            },
            {
                "event_type": "battery_degradation_signature",
                "start": degradation_start.isoformat(),
                "end": degradation_end.isoformat(),
                "affected_device": "battery",
                "true_cause": "usable battery capacity declines gradually over the simulation",
                "injected_capacity_loss_fraction": capacity_loss,
            },
            {
                "event_type": "sensor_dropout",
                "start": dropout_start.isoformat(),
                "end": dropout_end.isoformat(),
                "affected_device": "telemetry_pipeline",
                "true_cause": "intentional missing sensor readings for data-quality/abstention testing",
                "fields_affected": dropout_fields,
            },
            {
                "event_type": "grid_outage_islanding",
                "start": grid_outage_start.isoformat(),
                "end": grid_outage_end.isoformat(),
                "affected_device": "grid_inverter_battery",
                "true_cause": "utility grid became unavailable; inverter entered islanded backup operation and local dispatch explicitly accounts for served load, unmet demand, and PV curtailment",
                "backup_reserve_pct": float(inst.get("battery_backup_reserve_pct", inst["battery_soc_min_pct"])),
                "load_shedding_modeled": True,
                "pv_curtailment_modeled": True,
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
    from src.storage.local_store import write_store
    write_store(df, DB)
    print(f"Wrote {len(df):,} rows to {OUT}")
    print(f"Wrote persistent SQLite store to {DB}")
    print(f"Wrote ground truth to {GT}")


if __name__ == "__main__":
    main()
