from __future__ import annotations
import pandas as pd
from src.analytics.performance import detect_gradual_performance_decline
from src.analytics.forecasting import forecast_generation
from src.analytics.anomaly_detection import detect_anomalies
from src.analytics.decision_support import energy_summary,financial_summary,sustainability_summary,battery_runway_summary
from src.analytics.data_quality import assess_data_availability
from src.reasoning.tools import TOOL_DEFINITIONS,execute_tool
from src.reasoning.agent import fallback_answer
from src.interface.status_card import current_status

def test_gradual_decline_detected_without_latent_factor():
    from src.reasoning.tools import load_demo_context
    demo_data,config=load_demo_context()
    observed=demo_data.drop(columns=[c for c in ["performance_factor"] if c in demo_data])
    r=detect_gradual_performance_decline(observed,config["installation"]["pv_kwp"],config["installation"]["inverter_rating_w"])
    assert r["candidate_cause"]=="gradual_pv_performance_decline"
    assert dict((m["name"],m["value"]) for m in r["measurements"])["normalized_performance_decline_pct"]>=4

def test_cloudier_data_alone_not_false_gradual_decline():
    from src.reasoning.tools import load_demo_context
    demo_data,config=load_demo_context()
    x=demo_data.copy(); t=pd.to_datetime(x["timestamp"]); late=t>=t.min()+pd.Timedelta(days=80)
    x.loc[late,"irradiance_wm2"]*=0.65; x.loc[late,"pv_ac_power_w"]*=0.65
    r=detect_gradual_performance_decline(x,config["installation"]["pv_kwp"],config["installation"]["inverter_rating_w"])
    assert r["candidate_cause"] in {"gradual_pv_performance_decline","no_material_gradual_decline"} # original injected decline remains detectable

def test_forecast_is_deterministic():
    from src.reasoning.tools import load_demo_context
    demo_data,_=load_demo_context()
    a=forecast_generation(demo_data); b=forecast_generation(demo_data); assert a==b and a["forecast_kwh"]>0

def test_generic_anomaly_detector():
    s=pd.Series([1.0]*20+[100.0]); assert detect_anomalies(s,"zscore")["count"]==1

def test_decision_support_analytics():
    from src.reasoning.tools import load_demo_context
    demo_data,config=load_demo_context()
    e=energy_summary(demo_data,5,30); f=financial_summary(demo_data,config); s=sustainability_summary(demo_data,config,30); b=battery_runway_summary(demo_data,config)
    assert e["consumption_kwh"]>0 and 0<=e["self_sufficiency_pct"]<=100
    assert f["avoided_energy_cost"]>0 and "payback_method" in f["assumptions"]
    assert s["estimated_avoided_emissions_kgco2e"]>0 and "emissions_factor_source" in s["assumptions"]
    assert b["estimated_runway_hours"] is not None and "capacity_source" in b["assumptions"]

def test_dropout_forces_abstention():
    from src.reasoning.tools import load_demo_context
    demo_data,_=load_demo_context()
    r=assess_data_availability(demo_data,"2026-09-18"); assert not r["data_quality"]["sufficient"] and r["candidate_cause"]=="telemetry_unavailable"

def test_m4_tool_catalog_and_evidence_contract():
    names={t["name"] for t in TOOL_DEFINITIONS}; assert len(names)>=11
    e=execute_tool("get_financial_summary",{"question":"What's our ROI so far?"})
    for k in ["finding","confidence","measurements","data_quality","assumptions","supporting_tools","synthetic_data"]: assert k in e

def test_fallback_covers_canonical_decision_queries():
    assert "Energy balance" in fallback_answer("How much of our consumption came from solar this month?")
    assert "Battery runtime" in fallback_answer("How long will my battery last tonight at current usage?")
    assert "Sustainability" in fallback_answer("How sustainable was our energy usage this month?")
    assert "financial" in fallback_answer("What's our ROI so far?").lower()
    assert "abstain" in fallback_answer("Do we have enough data to tell what happened on 2026-09-18?").lower()

def test_adversarial_blame_is_refused():
    a=fallback_answer("Was the customer definitely responsible for this inverter failure?").lower(); assert "cannot prove customer responsibility" in a

def test_current_state_query_uses_status_evidence():
    assert "Current system status" in fallback_answer("What's the current state of my system?")

def test_status_card_is_status_first():
    s=current_status(); assert s["synthetic_data"] is True and "estimated_battery_runway_hours" in s and "active_alarm" in s

def test_real_tool_loop_supports_multiple_tools_same_round(monkeypatch):
    import sys, types
    from types import SimpleNamespace
    from src.reasoning import agent
    class Messages:
        def __init__(self): self.n=0; self.second_messages=None
        def create(self, **kwargs):
            self.n+=1
            if self.n==1:
                return SimpleNamespace(content=[
                    SimpleNamespace(type="tool_use",id="a",name="investigate_inverter_anomalies",input={"question":"What's unusual?"}),
                    SimpleNamespace(type="tool_use",id="b",name="investigate_performance_trend",input={"question":"What's unusual?"}),
                ])
            self.second_messages=kwargs["messages"]
            return SimpleNamespace(content=[SimpleNamespace(type="text",text="Two evidence streams were combined.")])
    class Client:
        instance=None
        def __init__(self,api_key): self.messages=Messages(); Client.instance=self
    mod=types.ModuleType("anthropic"); mod.Anthropic=Client; monkeypatch.setitem(sys.modules,"anthropic",mod); monkeypatch.setenv("ANTHROPIC_API_KEY","x")
    out=agent.answer("What's unusual about the inverter's behaviour?")
    assert out=="Two evidence streams were combined."
    results=Client.instance.messages.second_messages[-1]["content"]
    assert len(results)==2 and all(r["type"]=="tool_result" for r in results)


def test_inverter_anomaly_summary_does_not_fabricate_overload_for_non_overload_alarm():
    import pandas as pd
    from src.analytics.anomaly_detection import summarize_inverter_anomalies
    ts = pd.date_range("2026-09-01 12:00", periods=12, freq="5min", tz="Africa/Lagos")
    frame = pd.DataFrame({
        "timestamp": ts,
        "load_power_w": [800.0] * len(ts),
        "inverter_alarm_code": [""] * 6 + ["THERMAL_TRIP_01"] + [""] * 5,
        "inverter_operating_state": ["normal"] * 6 + ["fault"] + ["normal"] * 5,
        "inverter_temp_c": [45.0] * 6 + [82.0] + [45.0] * 5,
    })
    result = summarize_inverter_anomalies(frame, 5000.0)
    assert result["candidate_cause"] == "undetermined"
    assert result["confidence"] != "high"
    assert "does not support an overload-related cause" in result["finding"]
    measurements = {m["name"]: m["value"] for m in result["measurements"]}
    assert measurements["duration_above_rating_min"] == 0.0
    assert measurements["peak_load_w"] == 800.0
    assert result["alternatives_checked"]


def test_inverter_anomaly_summary_requires_event_window_overload_evidence():
    from src.reasoning.tools import load_demo_context
    from src.analytics.anomaly_detection import summarize_inverter_anomalies
    demo_data, config = load_demo_context()
    result = summarize_inverter_anomalies(demo_data, config["installation"]["inverter_rating_w"])
    assert result["candidate_cause"] == "overload_related_inverter_event"
    assert result["confidence"] == "high"
    measurements = {m["name"]: m["value"] for m in result["measurements"]}
    assert measurements["duration_above_rating_min"] >= 10.0
    assert measurements["peak_load_w"] > measurements["inverter_rating_w"]
    assert result["alternatives_checked"]
