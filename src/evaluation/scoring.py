from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import pandas as pd

PASS = "PASS"
PARTIAL = "PARTIAL"
FAIL = "FAIL"
NA = "N/A"
GAP = "CAPABILITY_GAP"


@dataclass(frozen=True)
class DimensionResult:
    status: str
    rationale: str

    def to_dict(self) -> dict[str, str]:
        return {"status": self.status, "rationale": self.rationale}


def _timestamp(value: str | None) -> pd.Timestamp | None:
    if not value:
        return None
    return pd.Timestamp(value)


def interval_overlap(evidence_window: dict[str, str] | None, truth: dict[str, Any]) -> tuple[bool, bool]:
    """Return (overlaps, tightly_localized).

    Tight localization is deliberately conservative: the evidence interval must overlap
    ground truth and be no more than 2x the truth interval plus 10 minutes. For long-term
    trend detectors that operate on the full observation horizon, overlap is real but
    localization is only partial.
    """
    if not evidence_window or not truth.get("start") or not truth.get("end"):
        return False, False
    es, ee = _timestamp(evidence_window.get("start")), _timestamp(evidence_window.get("end"))
    ts, te = _timestamp(truth.get("start")), _timestamp(truth.get("end"))
    if None in (es, ee, ts, te):
        return False, False
    overlaps = bool(es <= te and ee >= ts)
    if not overlaps:
        return False, False
    truth_duration = max(te - ts, pd.Timedelta(minutes=5))
    evidence_duration = max(ee - es, pd.Timedelta(minutes=5))
    tightly = evidence_duration <= truth_duration * 2 + pd.Timedelta(minutes=10)
    return True, bool(tightly)


def measurement_names(evidence: dict[str, Any]) -> set[str]:
    return {str(m.get("name")) for m in evidence.get("measurements", []) if m.get("name")}


def score_scenario(case, truth: dict[str, Any], evidence: dict[str, Any] | None) -> dict[str, Any]:
    if case.tool_name is None:
        dims = {
            "detection": DimensionResult(FAIL, "No approved M3/M4 diagnostic currently detects this scenario from observed telemetry."),
            "localization": DimensionResult(NA, "No diagnostic evidence window exists because the capability is not implemented."),
            "diagnosis": DimensionResult(FAIL, "No approved diagnostic currently identifies battery capacity degradation from observed telemetry."),
            "evidence_grounding": DimensionResult(NA, "No diagnosis was produced, so no diagnostic evidence can be scored."),
            "calibration": DimensionResult(PASS, "M5 records the missing capability explicitly instead of manufacturing confidence."),
            "abstention": DimensionResult(PASS, "The evaluation abstains from claiming battery degradation rather than using latent ground truth operationally."),
        }
        return {
            "event_type": case.event_type,
            "label": case.label,
            "overall": GAP,
            "note": case.note,
            "dimensions": {k: v.to_dict() for k, v in dims.items()},
            "evidence": None,
        }

    candidate = evidence.get("candidate_cause") if evidence else None
    detection_ok = candidate in case.expected_causes
    detection = DimensionResult(PASS if detection_ok else FAIL, f"candidate_cause={candidate!r}; expected one of {case.expected_causes!r}.")

    overlaps, tightly = interval_overlap(evidence.get("data_window") if evidence else None, truth)
    if tightly:
        localization = DimensionResult(PASS, "Evidence window overlaps and is tightly localized to the injected event window.")
    elif overlaps:
        localization = DimensionResult(PARTIAL, "Evidence window overlaps ground truth but is broader than the injected event window.")
    else:
        localization = DimensionResult(FAIL, "Evidence window does not overlap the injected event window.")

    diagnosis = DimensionResult(PASS if detection_ok else FAIL, "Leading diagnosis matches injected cause alias." if detection_ok else "Leading diagnosis does not match the injected cause alias.")

    names = measurement_names(evidence or {})
    missing = sorted(set(case.required_measurements) - names)
    grounded = bool(evidence and evidence.get("supporting_tools") and evidence.get("synthetic_data") is True and not missing)
    evidence_grounding = DimensionResult(
        PASS if grounded else FAIL,
        "Required measurements and supporting tool receipts are present." if grounded else f"Missing required evidence fields: {missing!r}.",
    )

    confidence = (evidence or {}).get("confidence")
    calibration_ok = confidence in case.expected_confidence
    calibration = DimensionResult(PASS if calibration_ok else PARTIAL, f"confidence={confidence!r}; expected {case.expected_confidence!r} for this controlled scenario.")

    if case.abstention_expected:
        dq = (evidence or {}).get("data_quality", {})
        abstain_ok = dq.get("sufficient") is False and candidate == "telemetry_unavailable"
        abstention = DimensionResult(PASS if abstain_ok else FAIL, "Insufficient telemetry is surfaced and causal diagnosis is withheld." if abstain_ok else "Expected an explicit insufficient-data abstention.")
    else:
        abstention = DimensionResult(NA, "No abstention is required for this scenario when sufficient evidence exists.")

    dims = {
        "detection": detection,
        "localization": localization,
        "diagnosis": diagnosis,
        "evidence_grounding": evidence_grounding,
        "calibration": calibration,
        "abstention": abstention,
    }
    statuses = [d.status for d in dims.values() if d.status != NA]
    overall = FAIL if FAIL in statuses else PARTIAL if PARTIAL in statuses else PASS
    return {
        "event_type": case.event_type,
        "label": case.label,
        "overall": overall,
        "note": case.note,
        "dimensions": {k: v.to_dict() for k, v in dims.items()},
        "evidence": evidence,
    }


def score_query(case, evidences: list[dict[str, Any]], offline_answer: str) -> dict[str, Any]:
    tools = tuple(tool for e in evidences for tool in e.get("supporting_tools", []))
    expected_tools_present = all(t in tools for t in case.expected_tools)
    traceable = all(e.get("supporting_tools") and e.get("synthetic_data") is True for e in evidences)
    material_assumptions_required = case.id in {6, 7, 8}
    assumptions_ok = (not material_assumptions_required) or all(bool(e.get("assumptions")) for e in evidences)
    abstention_ok = True
    if case.requires_abstention:
        abstention_ok = any(e.get("data_quality", {}).get("sufficient") is False for e in evidences) and "abstain" in offline_answer.lower()
    no_blame_ok = True
    if case.requires_no_blame:
        lower = offline_answer.lower()
        no_blame_ok = "cannot prove customer responsibility" in lower and "warranty" in lower

    checks = {
        "expected_tools": expected_tools_present,
        "evidence_traceable": traceable,
        "assumptions_exposed_when_material": assumptions_ok,
        "abstention_when_required": abstention_ok,
        "no_unsupported_blame": no_blame_ok,
    }
    return {
        "id": case.id,
        "question": case.question,
        "purpose": case.purpose,
        "scenario": case.scenario,
        "status": PASS if all(checks.values()) else FAIL,
        "checks": checks,
        "supporting_tools": list(tools),
        "offline_answer": offline_answer,
        "evidence": evidences,
    }
