from __future__ import annotations
import json, os, re
from typing import Any
from dotenv import load_dotenv
from src.reasoning.tools import TOOL_DEFINITIONS, execute_tool

SYSTEM="""You are the conversational interface for a synthetic solar-energy intelligence demo.
Use approved analytics tools for every engineering, financial, sustainability, forecasting, or diagnostic factual claim.
Never calculate those quantities yourself and never request or reason over raw time-series telemetry. Tool outputs are the evidence receipts.
Distinguish observations from analytical inference. Never assign customer blame, warranty liability, or causal certainty beyond the evidence.
If a tool reports insufficient data, abstain from the unsupported conclusion and explain what evidence is unavailable.
When multiple tools are needed, call them. Mention the supporting tool evidence and material assumptions in the answer. All demo data are synthetic.
"""

def _date(q):
    m=re.search(r"(?<!\d)(\d{4})[-/](\d{1,2})[-/](\d{1,2})(?!\d)",q)
    if not m:return None
    import pandas as pd
    try:return pd.Timestamp(year=int(m[1]),month=int(m[2]),day=int(m[3])).date().isoformat()
    except ValueError:return None

def _measurements(e): return {m["name"]:m.get("value") for m in e.get("measurements",[])}
def _fmt(e):
    if not e.get("data_quality",{}).get("sufficient",True): return e.get("finding","There is insufficient evidence to answer reliably.")
    ms=_measurements(e); finding=e.get("finding","Analysis completed.")
    vals=", ".join(f"{k}={v}" for k,v in list(ms.items())[:4])
    return finding + (f" Evidence: {vals}." if vals else "")

def fallback_answer(question:str)->str:
    q=question.lower(); calls=[]
    if any(x in q for x in ("current state","system status","current status","state of my system")): return _fmt(execute_tool("get_system_status",{"question":question}))
    if any(x in q for x in ("definitely responsible","customer responsible","blame","warranty")):
        e=execute_tool("investigate_inverter_failure",{"question":question}); return _fmt(e)+" The telemetry supports a leading technical explanation, but it cannot prove customer responsibility, intent, or warranty liability."
    if any(x in q for x in ("enough data","dropout","missing data","telemetry available")):
        d=_date(question); return _fmt(execute_tool("investigate_data_gap",{"question":question,"target_date":d or "2026-09-18"}))
    if any(x in q for x in ("grid outage","grid went down","grid failure","utility outage","islanded","islanding","backup mode","power outage")):
        d=_date(question); return _fmt(execute_tool("investigate_grid_event",{"question":question,"target_date":d or "2026-10-10"}))
    if any(x in q for x in ("battery health","battery degradation","battery capacity decline","battery capacity degrading")):
        return _fmt(execute_tool("investigate_battery_health",{"question":question}))
    if any(x in q for x in ("roi","payback","saving","financial")): return _fmt(execute_tool("get_financial_summary",{"question":question}))
    if any(x in q for x in ("sustainable","carbon","emission","renewable fraction")): return _fmt(execute_tool("get_sustainability_summary",{"question":question,"days":30}))
    if any(x in q for x in ("battery last","runway","battery runtime")): return _fmt(execute_tool("get_battery_runway",{"question":question}))
    if any(x in q for x in ("consumption came from solar","self-sufficiency","energy balance","grid dependency")): return _fmt(execute_tool("get_energy_summary",{"question":question,"days":30}))
    if any(x in q for x in ("forecast","tomorrow generation","predict generation")): return _fmt(execute_tool("get_generation_forecast",{"question":question,"horizon_days":1}))
    if any(x in q for x in ("unusual","behaviour","behavior","gradual","decline trend","performance trend")):
        e1=execute_tool("investigate_inverter_anomalies",{"question":question}); e2=execute_tool("investigate_performance_trend",{"question":question}); return _fmt(e1)+" "+_fmt(e2)
    if any(x in q for x in ("production","generation","solar output","pv output","irradiance")):
        e=execute_tool("investigate_generation_drop",{"question":question,"target_date":_date(question)})
        text=_fmt(e)
        return ("The strongest supported explanation is lower solar irradiance. "+text) if e.get("candidate_cause")=="weather_related_low_irradiance" else text
    return _fmt(execute_tool("investigate_inverter_failure",{"question":question}))

def _tool_result_block(i,r): return {"type":"tool_result","tool_use_id":i,"content":json.dumps(r)}
def answer(question:str,max_tool_rounds:int=6)->str:
    load_dotenv(); key=os.getenv("ANTHROPIC_API_KEY")
    if not key:return fallback_answer(question)
    from anthropic import Anthropic
    client=Anthropic(api_key=key); model=os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-4-5"; messages=[{"role":"user","content":question}]
    for _ in range(max_tool_rounds):
        response=client.messages.create(model=model,max_tokens=900,system=SYSTEM,tools=TOOL_DEFINITIONS,messages=messages)
        uses=[b for b in response.content if getattr(b,"type",None)=="tool_use"]
        if not uses:return "".join(b.text for b in response.content if getattr(b,"type",None)=="text").strip()
        messages.append({"role":"assistant","content":response.content}); results=[]
        for u in uses:
            try: results.append(_tool_result_block(u.id,execute_tool(u.name,dict(u.input))))
            except Exception as exc: results.append({"type":"tool_result","tool_use_id":u.id,"is_error":True,"content":f"Tool execution failed: {exc}"})
        messages.append({"role":"user","content":results})
    return "I could not complete the analysis within the allowed tool-use rounds."

if __name__=="__main__":
    for q in ["What's unusual about the inverter's behaviour?","How sustainable was our energy usage this month?","Do we have enough data to tell what happened on 2026-09-18?"]:
        print(f"\nQ: {q}\nA: {answer(q)}")
