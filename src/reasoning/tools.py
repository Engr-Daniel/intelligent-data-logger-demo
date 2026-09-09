from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.analytics.generation_drop import analyze_generation_drop
from src.analytics.root_cause import diagnose_overload
from src.evidence.models import EvidenceObject

ROOT = Path(__file__).resolve().parents[2]


def load_demo_context() -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(ROOT / "data" / "processed" / "telemetry.csv", parse_dates=["timestamp"])
    cfg = yaml.safe_load((ROOT / "config" / "installation.yaml").read_text())
    return df, cfg


def investigate_inverter_failure(question: str) -> dict:
    df, cfg = load_demo_context()
    result = diagnose_overload(df, cfg["installation"]["inverter_rating_w"])
    evidence = EvidenceObject(
        question=question,
        finding=result["finding"],
        candidate_cause=result.get("candidate_cause"),
        confidence=result.get("confidence", "unknown"),
        data_window=result.get("data_window"),
        measurements=result.get("measurements", []),
        alternatives_checked=result.get("alternatives_checked", []),
        data_quality=result.get("data_quality", {}),
        assumptions=[],
        supporting_tools=["diagnose_overload"],
    )
    return evidence.to_dict()


def investigate_generation_drop(question: str, target_date: str | None = None) -> dict:
    df, _ = load_demo_context()
    result = analyze_generation_drop(df, target_date=target_date)
    evidence = EvidenceObject(
        question=question,
        finding=result["finding"],
        candidate_cause=result.get("candidate_cause"),
        confidence=result.get("confidence", "unknown"),
        data_window=result.get("data_window"),
        measurements=result.get("measurements", []),
        alternatives_checked=result.get("alternatives_checked", []),
        data_quality=result.get("data_quality", {}),
        assumptions=[
            {
                "name": "comparison_baseline",
                "value": "same daytime hours on surrounding days",
            }
        ],
        supporting_tools=["analyze_generation_drop"],
    )
    return evidence.to_dict()


TOOL_DEFINITIONS = [
    {
        "name": "investigate_inverter_failure",
        "description": (
            "Investigate an inverter shutdown, failure, overload alarm, derating event, or question about what happened "
            "around an inverter fault. Returns structured evidence from load, battery, inverter, weather, grid, and temperature telemetry."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "The user's original inverter/fault question."}
            },
            "required": ["question"],
            "additionalProperties": False,
        },
    },
    {
        "name": "investigate_generation_drop",
        "description": (
            "Investigate why solar/PV energy production or generation dropped on a day. Distinguishes weather/low irradiance "
            "from inverter fault or derating using a surrounding-day baseline and returns structured evidence."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "The user's original production-drop question."},
                "target_date": {
                    "type": "string",
                    "description": "Optional ISO date such as 2026-08-05 when the user names a specific day. Omit if unknown.",
                },
            },
            "required": ["question"],
            "additionalProperties": False,
        },
    },
]


def execute_tool(name: str, inputs: dict[str, Any]) -> dict:
    if name == "investigate_inverter_failure":
        return investigate_inverter_failure(question=str(inputs.get("question", "")))
    if name == "investigate_generation_drop":
        return investigate_generation_drop(
            question=str(inputs.get("question", "")),
            target_date=inputs.get("target_date"),
        )
    raise ValueError(f"Unknown tool: {name}")
