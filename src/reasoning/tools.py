from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

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
