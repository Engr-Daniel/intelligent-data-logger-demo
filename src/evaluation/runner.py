from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.evaluation.cases import CANONICAL_QUERY_CASES, SCENARIO_CASES
from src.evaluation.scoring import score_query, score_scenario
from src.reasoning.agent import fallback_answer
from src.reasoning.tools import execute_tool

ROOT = Path(__file__).resolve().parents[2]
GROUND_TRUTH_PATH = ROOT / "data" / "ground_truth.json"


def load_ground_truth(path: Path = GROUND_TRUTH_PATH) -> dict[str, Any]:
    """Evaluation-only oracle. Never imported by operational reasoning/analytics."""
    return json.loads(path.read_text(encoding="utf-8"))


def _truth_by_type(gt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {event["event_type"]: event for event in gt.get("events", [])}


def run_scenario_evaluation() -> list[dict[str, Any]]:
    truth = _truth_by_type(load_ground_truth())
    results = []
    for case in SCENARIO_CASES:
        if case.event_type not in truth:
            results.append({"event_type": case.event_type, "label": case.label, "overall": "GROUND_TRUTH_MISSING", "dimensions": {}, "evidence": None})
            continue
        evidence = execute_tool(case.tool_name, dict(case.tool_args)) if case.tool_name else None
        results.append(score_scenario(case, truth[case.event_type], evidence))
    return results


def run_query_evaluation() -> list[dict[str, Any]]:
    results = []
    for case in CANONICAL_QUERY_CASES:
        evidences = [execute_tool(name, dict(args)) for name, args in case.evidence_calls]
        results.append(score_query(case, evidences, fallback_answer(case.question)))
    return results


def run_m5_evaluation() -> dict[str, Any]:
    scenarios = run_scenario_evaluation()
    queries = run_query_evaluation()
    return {
        "milestone": "M5",
        "synthetic_data": True,
        "evaluation_type": "controlled functional demonstration; not statistical validation",
        "aggregation_policy": "No accuracy percentage or statistical significance is reported. Dimensions remain separate PASS/PARTIAL/FAIL/N/A judgments.",
        "scenario_results": scenarios,
        "canonical_query_results": queries,
        "scope_notes": [
            "The experiment brief labels grid outage/islanding as an optional stretch scenario in Section 5.3 even though a later success-criteria line says all six scenarios. The frozen, reviewer-approved M1 baseline contains the five non-stretch scenarios; M5 evaluates that frozen scope and does not retroactively add the optional sixth scenario.",
            "For canonical query 2, the evaluator binds the relative word 'yesterday' to the controlled cloudy-day scenario date (2026-08-05) so scoring is reproducible and independent of wall-clock date.",
            "M5 scores deterministic tool/evidence behaviour rather than grading nondeterministic LLM prose. The live Claude tool-use path remains available in notebook 04 when an API key is supplied and was already closed in M4.",
        ],
        "known_capability_gaps": [
            {
                "id": "battery_degradation_diagnosis",
                "description": "The M3/M4 baseline has no observed-telemetry battery capacity-degradation diagnostic. M5 records the gap; M6 may address it without changing the M5 scoring rules retroactively."
            }
        ],
        "deferred_non_defects": [
            "Forecasting is a transparent median recent-generation persistence baseline.",
            "Battery runway uses configured nominal usable capacity and constant-load assumptions.",
            "Production-grade timestamp jitter/retry handling remains out of demo scope.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# M5 Controlled Evaluation Report",
        "",
        "> **Synthetic demo only.** This is a controlled functional evaluation of authored scenarios, not evidence of field accuracy or statistical validation.",
        "",
        "## Scenario scoring",
        "",
        "| Scenario | Detection | Localization | Diagnosis | Evidence | Calibration | Abstention | Overall |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in report["scenario_results"]:
        d = r.get("dimensions", {})
        def s(name): return d.get(name, {}).get("status", "N/A")
        lines.append(f"| {r['label']} | {s('detection')} | {s('localization')} | {s('diagnosis')} | {s('evidence_grounding')} | {s('calibration')} | {s('abstention')} | **{r['overall']}** |")
    lines += ["", "### Scenario notes", ""]
    for r in report["scenario_results"]:
        if r.get("note") or r["overall"] != "PASS":
            lines.append(f"- **{r['label']} ({r['overall']}):** {r.get('note') or 'See dimension rationales in the JSON report.'}")
    lines += ["", "## Ten canonical queries", "", "| # | Query purpose | Status | Supporting analytics |", "|---:|---|---|---|"]
    for q in report["canonical_query_results"]:
        lines.append(f"| {q['id']} | {q['purpose']} | **{q['status']}** | {', '.join(q['supporting_tools'])} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- Results are deliberately **not aggregated into an accuracy percentage**.",
        "- A scenario can be detected but only partially localized; those dimensions remain separate.",
        "- Ground truth is read only by `src/evaluation/` and is never passed into operational analytics/reasoning.",
        "- The battery-degradation scenario is an explicit current capability gap: the evaluator refuses to manufacture a diagnosis from latent ground truth.",
        "- M6 is the appropriate milestone for fixing any diagnosis/evidence/calibration mismatch revealed here while keeping the scoring rubric fixed.",
        "- The frozen M1 scope contains the five non-stretch scenarios; optional grid outage/islanding is not retroactively added by M5.",
        "- Canonical query 2 resolves 'yesterday' to 2026-08-05 for deterministic scenario scoring.",
        "- M5 scores tool/evidence correctness rather than nondeterministic LLM prose; notebook 04 can exercise the live Claude loop when an API key is supplied.",
        "",
    ]
    return "\n".join(lines)


def write_report(output_dir: Path = ROOT / "reports") -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    report = run_m5_evaluation()
    json_path = output_dir / "m5_evaluation.json"
    md_path = output_dir / "m5_evaluation.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


if __name__ == "__main__":
    j, m = write_report()
    print(f"Wrote {j.relative_to(ROOT)}")
    print(f"Wrote {m.relative_to(ROOT)}")
