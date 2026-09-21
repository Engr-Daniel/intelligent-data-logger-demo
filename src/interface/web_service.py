"""Status-first presentation and session-scoped, evidence-capturing conversation."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from src.datacontext.context import load_installation_config
from src.reasoning.agent import SYSTEM, fallback_answer
from src.reasoning.tools import TOOL_DEFINITIONS, execute_tool
from src.storage.local_store import DEFAULT_DB, load_telemetry

ROOT = Path(__file__).resolve().parents[2]
SUGGESTIONS = [
    ("Generation", "Why did production drop on 2026-08-05?"),
    ("Battery health", "Is battery capacity degrading over time?"),
    ("Inverter event", "What happened around the inverter failure?"),
    ("Grid outage", "What happened when the grid went down on 2026-10-10?"),
    ("Missing data", "Do we have enough data to tell what happened on 2026-09-18?"),
    ("Energy use", "How much of our consumption came from solar this month?"),
    ("Battery runway", "How long will my battery last at current usage?"),
    ("Financials", "What's our ROI so far?"),
]


def dashboard(day: str | None = None) -> dict:
    if not DEFAULT_DB.exists():
        raise ValueError("Generate the demo data first: python -m src.generator.simulate")
    df = load_telemetry()
    if df.empty:
        raise ValueError("The telemetry store is empty.")
    cfg = load_installation_config()
    required = ["pv_ac_power_w", "load_power_w", "battery_soc_pct", "grid_import_w", "grid_export_w"]
    complete = df.dropna(subset=required)
    if complete.empty:
        raise ValueError("No complete system snapshot is available.")
    row = complete.iloc[-1]
    status = execute_tool("get_system_status", {"question": "Current system status"})
    values = {m["name"]: m["value"] for m in status["measurements"]}
    chosen = day or str(df.timestamp.iloc[-1].date())
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", chosen):
        raise ValueError("Choose a date in YYYY-MM-DD format.")
    selected = df[df.timestamp.dt.strftime("%Y-%m-%d") == chosen]
    columns = ["timestamp", *required, "battery_charge_w", "battery_discharge_w"]
    chart = selected[columns].copy()
    chart["timestamp"] = chart.timestamp.astype(str)
    chart = json.loads(chart.to_json(orient="records"))
    load_dotenv(ROOT / ".env")
    return {
        "installation": cfg["installation"]["name"],
        "equipment": {key: cfg["installation"][key] for key in
                      ("pv_kwp", "inverter_rating_w", "battery_nominal_kwh")},
        "timestamp": str(row.timestamp), "latest_received": str(df.timestamp.iloc[-1]),
        "snapshot_is_latest": bool(row.timestamp == df.timestamp.iloc[-1]),
        "values": values, "status_evidence": status,
        "inverter_state": str(row.inverter_operating_state),
        "grid_export_w": float(row.grid_export_w),
        "first_day": str(df.timestamp.iloc[0].date()),
        "last_day": str(df.timestamp.iloc[-1].date()), "selected_day": chosen,
        "missing_rows": int(selected[required].isna().any(axis=1).sum()),
        "chart": chart, "suggestions": SUGGESTIONS,
        "live_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
        "model": os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-4-5",
        "synthetic_data": True,
    }


class Conversation:
    def __init__(self):
        self.turns = []
        self.history = []
        self.mode = None

    def ask(self, question: str, mode: str = "offline", client=None) -> dict:
        if not isinstance(question, str) or not question.strip() or len(question) > 2000:
            raise ValueError("Enter a question between 1 and 2,000 characters.")
        if mode not in ("offline", "live"):
            raise ValueError("Choose offline or live mode.")
        if len(self.turns) >= 20:
            raise ValueError("Export this session and start a new conversation (20-turn limit).")
        if self.mode is not None and self.mode != mode:
            raise ValueError("Start a new conversation before changing mode.")
        self.mode = mode
        started = time.perf_counter()
        record = {"question": question.strip(), "mode": mode, "synthetic_data": True,
                  "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                  "tools": [], "usage": [], "status": "complete", "model": None}

        def receipt(name, inputs):
            entry = {"name": name, "inputs": inputs}
            record["tools"].append(entry)
            try:
                result = execute_tool(name, inputs)
                entry["evidence"] = result
                return result
            except Exception:
                entry["error"] = "Tool could not complete with these inputs."
                raise ValueError(entry["error"]) from None

        try:
            if mode == "offline":
                # The frozen router defaults unmatched input to an inverter diagnosis.
                # The public interface must instead make its limited coverage explicit.
                supported = re.search(
                    r"status|current state|state of my system|production|generation|solar output|"
                    r"irradiance|battery.*(?:health|degrad|capacity|last|runtime)|runway|"
                    r"inverter|overload|responsible|blame|warranty|enough data|dropout|missing data|"
                    r"telemetry available|grid outage|grid went down|grid failure|utility outage|"
                    r"island|backup mode|power outage|roi|payback|saving|financial|sustainable|"
                    r"carbon|emission|renewable fraction|consumption came from solar|"
                    r"self-sufficiency|energy balance|grid dependency|forecast|unusual|"
                    r"behaviour|behavior|gradual|decline trend|performance trend", question.lower())
                if not supported:
                    record["answer"] = ("Offline mode handles the suggested investigation topics, "
                        "with each question independent. Choose a suggestion or start a new "
                        "conversation in Claude mode for open-ended follow-up questions.")
                    record["status"] = "unsupported"
                else:
                    record["answer"] = fallback_answer(question, executor=receipt)
            else:
                load_dotenv(ROOT / ".env")
                key = os.getenv("ANTHROPIC_API_KEY")
                if client is None:
                    if not key:
                        raise ValueError("Configure ANTHROPIC_API_KEY in your local .env file first.")
                    from anthropic import Anthropic
                    client = Anthropic(api_key=key, timeout=60, max_retries=0)
                record["model"] = os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-4-5"
                # Explicit snapshot anchor resolves relative dates without simulator ground truth.
                current = dashboard()
                system = SYSTEM + "\nLatest stored telemetry timestamp: " + current["timestamp"]
                system += (". Interpret current/today/yesterday relative to that synthetic timestamp. "
                           "Use prior conversation only as context; use tools for new factual claims.")
                record["system_prompt"] = system
                messages = copy.deepcopy(self.history)
                messages.append({"role": "user", "content": question})
                record["transcript"] = messages
                record["answer"] = "The analysis reached its six-round limit. Try a narrower question."
                record["status"] = "round_limit"
                for _ in range(6):
                    response = client.messages.create(model=record["model"], max_tokens=1200,
                        system=system, tools=TOOL_DEFINITIONS, messages=messages)
                    record["usage"].append(response.usage.model_dump())
                    record.setdefault("response_models", []).append(response.model)
                    blocks = [b.model_dump() for b in response.content]
                    messages.append({"role": "assistant", "content": blocks})
                    calls = [b for b in blocks if b["type"] == "tool_use"]
                    if not calls:
                        record["answer"] = "\n".join(b["text"] for b in blocks if b["type"] == "text")
                        record["status"] = "complete" if response.stop_reason == "end_turn" else "incomplete"
                        if record["status"] == "complete":
                            self.history = messages
                        break
                    results = []
                    for call in calls:
                        try:
                            value = receipt(call["name"], call["input"])
                            results.append({"type": "tool_result", "tool_use_id": call["id"],
                                            "content": json.dumps(value)})
                        except ValueError:
                            results.append({"type": "tool_result", "tool_use_id": call["id"],
                                            "content": "Tool failed; correct inputs or abstain.", "is_error": True})
                    messages.append({"role": "user", "content": results})
                record["transcript"] = messages
        except Exception as exc:
            # Never send upstream error bodies, credentials or tracebacks to the browser/export.
            record["status"] = "error"
            safe_messages = {"Configure ANTHROPIC_API_KEY in your local .env file first.",
                             "Tool could not complete with these inputs."}
            record["answer"] = (str(exc) if str(exc) in safe_messages else
                "The analysis could not complete. Check the telemetry store or, in Claude mode, your API key, model, credits and connection.")
            record["error_type"] = type(exc).__name__
        record["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        self.turns.append(record)
        return record

    def export(self):
        paths = [ROOT / "config/installation.yaml", ROOT / "src/reasoning/agent.py",
                 ROOT / "src/reasoning/tools.py", Path(__file__), DEFAULT_DB]
        return {"format_version": 1, "synthetic_data": True,
                "evaluation_status": "Interactive demonstration; not a scored research experiment",
                "exported_utc": datetime.now(timezone.utc).isoformat(),
                "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in paths if p.exists()},
                "turns": self.turns}
