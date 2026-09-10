from __future__ import annotations
from pathlib import Path
from typing import Any
import pandas as pd

from src.analytics.generation_drop import analyze_generation_drop
from src.analytics.root_cause import diagnose_overload
from src.analytics.performance import detect_gradual_performance_decline
from src.analytics.anomaly_detection import summarize_inverter_anomalies
from src.analytics.data_quality import assess_data_availability
from src.analytics.decision_support import energy_summary, financial_summary, sustainability_summary, battery_runway_summary
from src.analytics.forecasting import forecast_generation
from src.evidence.models import EvidenceObject
from src.datacontext.context import load_installation_config
from src.storage.local_store import load_telemetry

ROOT = Path(__file__).resolve().parents[2]

def load_demo_context(): return load_telemetry(), load_installation_config()

def _ev(question, result, tool, assumptions=None):
    return EvidenceObject(question=question, finding=result.get("finding", "Analysis completed."), candidate_cause=result.get("candidate_cause"), confidence=result.get("confidence", "medium"), data_window=result.get("data_window"), measurements=result.get("measurements", []), alternatives_checked=result.get("alternatives_checked", []), data_quality=result.get("data_quality", {"sufficient": True, "warnings": []}), assumptions=assumptions if assumptions is not None else result.get("assumptions", []), supporting_tools=[tool]).to_dict()

def investigate_inverter_failure(question: str) -> dict:
    df,cfg=load_demo_context(); return _ev(question, diagnose_overload(df,cfg["installation"]["inverter_rating_w"]), "diagnose_overload")

def investigate_generation_drop(question: str,target_date: str|None=None)->dict:
    df,_=load_demo_context(); r=analyze_generation_drop(df,target_date); return _ev(question,r,"analyze_generation_drop",[{"name":"comparison_baseline","value":"same daytime hours on surrounding days"}])

def investigate_performance_trend(question: str)->dict:
    df,cfg=load_demo_context(); r=detect_gradual_performance_decline(df,cfg["installation"]["pv_kwp"],cfg["installation"]["inverter_rating_w"]); a=[{"name":k,"value":v} for k,v in r.pop("assumptions",{}).items()]; return _ev(question,r,"detect_gradual_performance_decline",a)

def investigate_inverter_anomalies(question: str)->dict:
    df,cfg=load_demo_context(); return _ev(question,summarize_inverter_anomalies(df,cfg["installation"]["inverter_rating_w"]),"summarize_inverter_anomalies")

def get_energy_summary(question: str,days:int=30)->dict:
    df,cfg=load_demo_context(); r=energy_summary(df,cfg["simulation"]["interval_minutes"],days); ms=[{"name":k,"value":v,"unit":"kWh" if k.endswith("kwh") else "%"} for k,v in r.items() if k.endswith("kwh") or k=="self_sufficiency_pct"]
    return _ev(question,{"finding":f"Energy balance for the latest {days} days was calculated from stored telemetry.","candidate_cause":None,"confidence":"high","data_window":r["data_window"],"measurements":ms,"data_quality":{"sufficient":True,"warnings":[]}},"energy_balance")

def get_battery_runway(question: str)->dict:
    df,cfg=load_demo_context(); r=battery_runway_summary(df,cfg); ms=[{"name":"estimated_runway_hours","value":r.get("estimated_runway_hours"),"unit":"hours"}]
    return _ev(question,{"finding":"Battery runtime was estimated at the latest complete observation using a constant-load assumption.","candidate_cause":None,"confidence":"medium","data_window":r.get("data_window"),"measurements":ms,"data_quality":r.get("data_quality",{})},"battery_runway",[{"name":k,"value":v} for k,v in r.get("assumptions",{}).items()])

def get_sustainability_summary(question: str,days:int=30)->dict:
    df,cfg=load_demo_context(); r=sustainability_summary(df,cfg,days); ms=[{"name":"renewable_fraction_pct","value":r["renewable_fraction_pct"],"unit":"%"},{"name":"estimated_avoided_emissions_kgco2e","value":r["estimated_avoided_emissions_kgco2e"],"unit":"kgCO2e"},{"name":"solar_self_consumed_kwh","value":r["solar_self_consumed_kwh"],"unit":"kWh"}]
    return _ev(question,{"finding":f"Sustainability metrics for the latest {days} days were calculated using the configured grid-displacement assumption.","candidate_cause":None,"confidence":"medium","data_window":r["data_window"],"measurements":ms,"data_quality":{"sufficient":True,"warnings":[]}},"sustainability_metrics",[{"name":k,"value":v} for k,v in r["assumptions"].items()])

def get_financial_summary(question: str)->dict:
    df,cfg=load_demo_context(); r=financial_summary(df,cfg); units={"avoided_energy_cost":cfg["financial"]["currency"],"net_savings":cfg["financial"]["currency"],"simple_roi_pct":"%","annualized_net_savings":cfg["financial"]["currency"]+"/year","simple_payback_years":"years"}; ms=[{"name":k,"value":r[k],"unit":units[k]} for k in units]
    return _ev(question,{"finding":"Simple financial metrics were calculated from synthetic telemetry and configured tariff/CAPEX assumptions.","candidate_cause":None,"confidence":"medium","data_window":r["data_window"],"measurements":ms,"data_quality":{"sufficient":True,"warnings":[]}},"financial_metrics",[{"name":k,"value":v} for k,v in r["assumptions"].items()])

def assess_data_quality(question: str,target_date:str)->dict:
    df,_=load_demo_context(); return _ev(question,assess_data_availability(df,target_date),"assess_data_availability")

def get_generation_forecast(question:str,horizon_days:int=1)->dict:
    df,_=load_demo_context(); r=forecast_generation(df,horizon_days); ms=[{"name":"forecast_generation_kwh","value":r.get("forecast_kwh"),"unit":"kWh"}]
    return _ev(question,{"finding":("A simple persistence forecast was calculated." if r["status"]=="PASS" else "There is insufficient data for the requested forecast."),"candidate_cause":None,"confidence":"low" if r["status"]=="PASS" else "low","measurements":ms,"data_quality":r.get("data_quality",{})},"forecast_generation",[{"name":"method","value":r.get("method")},{"name":"horizon_days","value":horizon_days}])

def get_system_status(question: str)->dict:
    df,cfg=load_demo_context(); complete=df.dropna(subset=["pv_ac_power_w","load_power_w","battery_soc_pct","grid_import_w","grid_export_w"]); row=complete.iloc[-1]; runway=battery_runway_summary(df,cfg); alarm=None if pd.isna(row["inverter_alarm_code"]) or str(row["inverter_alarm_code"])=="" else str(row["inverter_alarm_code"]); ms=[{"name":"pv_generation_w","value":round(float(row["pv_ac_power_w"]),1),"unit":"W"},{"name":"load_w","value":round(float(row["load_power_w"]),1),"unit":"W"},{"name":"battery_soc_pct","value":round(float(row["battery_soc_pct"]),1),"unit":"%"},{"name":"estimated_battery_runway_hours","value":runway.get("estimated_runway_hours"),"unit":"hours"},{"name":"grid_import_w","value":round(float(row["grid_import_w"]),1),"unit":"W"},{"name":"active_alarm","value":alarm,"unit":"categorical"}]; r={"finding":"Current system status was read from the latest complete telemetry interval.","candidate_cause":None,"confidence":"high","data_window":{"start":pd.to_datetime(row["timestamp"]).isoformat(),"end":pd.to_datetime(row["timestamp"]).isoformat()},"measurements":ms,"data_quality":{"sufficient":True,"warnings":[]}}; return _ev(question,r,"current_system_status",[{"name":"battery_runway_method","value":"constant load; configured nominal usable capacity"}])

TOOL_DEFINITIONS=[]
def _tool(name,description,props=None,required=None):
    TOOL_DEFINITIONS.append({"name":name,"description":description,"input_schema":{"type":"object","properties":{"question":{"type":"string"}} | (props or {}),"required":["question"]+(required or []),"additionalProperties":False}})
_tool("get_system_status","Return the latest status-first system snapshot: PV, load, battery, grid, runway and active alarm.")
_tool("investigate_inverter_failure","Investigate inverter shutdown/failure/overload and return cross-component evidence.")
_tool("investigate_generation_drop","Investigate a solar production drop on a day; distinguishes weather from inverter events.",{"target_date":{"type":"string"}})
_tool("investigate_performance_trend","Assess unusual long-term inverter/PV behaviour and gradual normalized performance decline.")
_tool("investigate_inverter_anomalies","Summarize inverter alarms, derating states and overload-related anomalies.")
_tool("get_energy_summary","Calculate solar contribution, self-sufficiency, consumption and grid energy for a recent period.",{"days":{"type":"integer","minimum":1,"maximum":120}})
_tool("get_battery_runway","Estimate battery runtime at current usage with explicit assumptions.")
_tool("get_sustainability_summary","Calculate renewable fraction and avoided emissions using configured assumptions.",{"days":{"type":"integer","minimum":1,"maximum":120}})
_tool("get_financial_summary","Calculate avoided cost, simple ROI and simple payback from configured assumptions.")
_tool("assess_data_quality","Check whether enough telemetry exists on a specific date and abstain when it does not.",{"target_date":{"type":"string"}},["target_date"])
_tool("get_generation_forecast","Produce a transparent simple generation persistence forecast.",{"horizon_days":{"type":"integer","minimum":1,"maximum":7}})

EXECUTORS={k:v for k,v in globals().items() if k in {t["name"] for t in TOOL_DEFINITIONS}}
def execute_tool(name:str,inputs:dict[str,Any])->dict:
    if name not in EXECUTORS: raise ValueError(f"Unknown tool: {name}")
    return EXECUTORS[name](**inputs)
