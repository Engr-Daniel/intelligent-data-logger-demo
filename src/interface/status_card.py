from __future__ import annotations
import pandas as pd
from src.storage.local_store import load_telemetry
from src.datacontext.context import load_installation_config
from src.analytics.decision_support import battery_runway_summary

def current_status()->dict:
    df=load_telemetry(); cfg=load_installation_config(); row=df.dropna(subset=["pv_ac_power_w","load_power_w","battery_soc_pct"]).iloc[-1]
    runway=battery_runway_summary(df,cfg)
    alarms=df[df["inverter_alarm_code"].fillna("").astype(str).str.len()>0]
    return {"timestamp":str(row["timestamp"]),"synthetic_data":True,"pv_generation_w":round(float(row["pv_ac_power_w"]),1),"load_w":round(float(row["load_power_w"]),1),"battery_soc_pct":round(float(row["battery_soc_pct"]),1),"estimated_battery_runway_hours":runway.get("estimated_runway_hours"),"grid_import_w":round(float(row["grid_import_w"]),1),"grid_export_w":round(float(row["grid_export_w"]),1),"inverter_state":str(row["inverter_operating_state"]),"active_alarm":None if pd.isna(row["inverter_alarm_code"]) or str(row["inverter_alarm_code"])=="" else str(row["inverter_alarm_code"]),"historical_alarm_events":int(len(alarms))}
if __name__=="__main__":
    for k,v in current_status().items(): print(f"{k}: {v}")
