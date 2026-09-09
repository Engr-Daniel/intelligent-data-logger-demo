from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class EvidenceObject:
    question: str
    finding: str
    candidate_cause: str | None
    confidence: str
    data_window: dict[str, str] | None = None
    measurements: list[dict[str, Any]] = field(default_factory=list)
    alternatives_checked: list[dict[str, Any]] = field(default_factory=list)
    data_quality: dict[str, Any] = field(default_factory=dict)
    assumptions: list[dict[str, Any]] = field(default_factory=list)
    supporting_tools: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
