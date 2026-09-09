from __future__ import annotations

import json
import os

from dotenv import load_dotenv

from src.reasoning.tools import investigate_inverter_failure

SYSTEM = """You are the conversational interface for a solar energy intelligence system.
Engineering facts must come only from tool/evidence outputs. Distinguish observed evidence from inference.
Never assign blame or claim certainty beyond the evidence. If data are insufficient, say so.
"""


def fallback_answer(question: str) -> str:
    evidence = investigate_inverter_failure(question)
    ms = {m["name"]: m["value"] for m in evidence["measurements"]}
    if evidence["candidate_cause"] == "overload":
        return (
            f"The strongest supported explanation is a sustained overload before the inverter alarm. "
            f"Peak load reached {ms.get('peak_load_w')} W against a {ms.get('inverter_rating_w')} W rating, "
            f"and load stayed above the rating for about {ms.get('duration_above_rating_min')} minutes before "
            f"alarm {ms.get('alarm_code')}. This supports overload as the leading candidate cause, but the telemetry "
            "alone does not prove customer responsibility or establish a warranty conclusion."
        )
    return "The available telemetry does not support a confident overload diagnosis."


def answer(question: str) -> str:
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return fallback_answer(question)

    from anthropic import Anthropic

    evidence = investigate_inverter_failure(question)
    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model=os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-4-5",
        max_tokens=500,
        system=SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Question: {question}\nEvidence object:\n{json.dumps(evidence, indent=2)}",
            }
        ],
    )
    return "".join(block.text for block in message.content if getattr(block, "type", None) == "text")


if __name__ == "__main__":
    q = "The customer says the inverter just failed on its own — what actually happened around that time?"
    print(answer(q))
