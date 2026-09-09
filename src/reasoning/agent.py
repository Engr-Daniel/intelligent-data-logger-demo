from __future__ import annotations

import json
import os
import re
from typing import Any

from dotenv import load_dotenv

from src.reasoning.tools import TOOL_DEFINITIONS, execute_tool, investigate_generation_drop, investigate_inverter_failure

SYSTEM = """You are the conversational interface for a solar energy intelligence system.
Choose the appropriate analytics tool for the user's question. Engineering facts must come only from tool/evidence outputs.
Do not calculate engineering quantities yourself. Distinguish observed evidence from inference. Never assign blame or claim
certainty beyond the evidence. If data are insufficient, say so. After using a tool, answer concisely and mention the main
measurements that support the conclusion.
"""


def _measurements(evidence: dict) -> dict[str, Any]:
    return {m["name"]: m.get("value") for m in evidence.get("measurements", [])}


def _extract_explicit_date(question: str) -> str | None:
    """Extract a simple explicit calendar date from an offline-demo question.

    The real Claude tool-use path can supply ``target_date`` directly. This
    helper exists only so the deterministic fallback does not silently ignore
    dates such as 2026-08-05 when no API key is configured.
    """
    match = re.search(r"(?<!\d)(\d{4})[-/](\d{1,2})[-/](\d{1,2})(?!\d)", question)
    if not match:
        return None

    year, month, day = (int(part) for part in match.groups())
    try:
        # Import locally to keep the fallback helper lightweight and use the
        # same date semantics as the analytics layer.
        import pandas as pd

        return pd.Timestamp(year=year, month=month, day=day).date().isoformat()
    except ValueError:
        return None


def fallback_answer(question: str) -> str:
    """Deterministic offline router used only when no Anthropic key is available."""
    q = question.lower()
    if any(term in q for term in ("production", "generation", "solar output", "pv output", "irradiance")):
        target_date = _extract_explicit_date(question)
        evidence = investigate_generation_drop(question, target_date=target_date)
        ms = _measurements(evidence)
        if evidence.get("candidate_cause") == "weather_related_low_irradiance":
            return (
                f"The strongest supported explanation is lower solar irradiance rather than an inverter fault. "
                f"Mean PV output was {ms.get('target_mean_pv_power_w')} W versus {ms.get('baseline_mean_pv_power_w')} W on surrounding days, "
                f"while irradiance was lower by about {ms.get('irradiance_drop_pct_vs_surrounding_days')}%. "
                "No inverter alarm or abnormal operating state was needed to explain the drop."
            )
        if evidence.get("candidate_cause") == "inverter_event_limited_energy_impact":
            return (
                "An inverter alarm or abnormal operating state occurred during the selected day, so the event should not be ignored. "
                f"However, full-day PV production was only {ms.get('pv_drop_pct_vs_surrounding_days')}% below the surrounding-day baseline, "
                "which is below the material-drop threshold. The event is operationally relevant, but its daily energy impact appears limited."
            )
        return evidence.get("finding", "The production-drop evidence is inconclusive.")

    evidence = investigate_inverter_failure(question)
    ms = _measurements(evidence)
    if evidence.get("candidate_cause") == "overload":
        return (
            f"The strongest supported explanation is a sustained overload before the inverter alarm. "
            f"Peak load reached {ms.get('peak_load_w')} W against a {ms.get('inverter_rating_w')} W rating, "
            f"and load stayed above the rating for about {ms.get('duration_above_rating_min')} minutes before "
            f"alarm {ms.get('alarm_code')}. This supports overload as the leading candidate cause, but the telemetry "
            "alone does not prove customer responsibility or establish a warranty conclusion."
        )
    return evidence.get("finding", "The available telemetry does not support a confident diagnosis.")


def _tool_result_block(tool_use_id: str, result: dict) -> dict:
    return {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": json.dumps(result),
    }


def answer(question: str, max_tool_rounds: int = 4) -> str:
    """Answer with genuine Claude tool-use when configured.

    Claude receives both analytics tools and chooses which one to call. Tool
    outputs are then returned to Claude as tool_result blocks. The loop supports
    more than one tool call, while a small round cap prevents accidental loops.
    """
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return fallback_answer(question)

    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    model = os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-4-5"
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]

    for _ in range(max_tool_rounds):
        response = client.messages.create(
            model=model,
            max_tokens=700,
            system=SYSTEM,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        tool_uses = [block for block in response.content if getattr(block, "type", None) == "tool_use"]
        if not tool_uses:
            return "".join(block.text for block in response.content if getattr(block, "type", None) == "text").strip()

        # Preserve Claude's entire assistant content before returning tool results.
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for tool_use in tool_uses:
            try:
                result = execute_tool(tool_use.name, dict(tool_use.input))
                results.append(_tool_result_block(tool_use.id, result))
            except Exception as exc:  # tool errors are returned to the model rather than hidden
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "is_error": True,
                        "content": f"Tool execution failed: {exc}",
                    }
                )
        messages.append({"role": "user", "content": results})

    return "I could not complete the analysis within the allowed tool-use rounds."


if __name__ == "__main__":
    questions = [
        "The customer says the inverter just failed on its own — what actually happened around that time?",
        "Why did our solar energy production drop on 2026-08-05?",
    ]
    for q in questions:
        print(f"\nQ: {q}\nA: {answer(q)}")
