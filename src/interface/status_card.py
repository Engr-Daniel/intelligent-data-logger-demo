from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def current_status() -> dict:
    df = pd.read_csv(ROOT / "data" / "processed" / "telemetry.csv", parse_dates=["timestamp"])
    row = df.iloc[-1]
    return {
        "timestamp": str(row["timestamp"]),
        "pv_generation_w": round(float(row["pv_ac_power_w"]), 1),
        "load_w": round(float(row["load_power_w"]), 1),
        "battery_soc_pct": round(float(row["battery_soc_pct"]), 1),
        "grid_import_w": round(float(row["grid_import_w"]), 1),
        "grid_export_w": round(float(row["grid_export_w"]), 1),
        "inverter_state": str(row["inverter_operating_state"]),
        "active_alarm": None if pd.isna(row["inverter_alarm_code"]) or str(row["inverter_alarm_code"]) == "" else str(row["inverter_alarm_code"]),
    }


if __name__ == "__main__":
    for k, v in current_status().items():
        print(f"{k}: {v}")
