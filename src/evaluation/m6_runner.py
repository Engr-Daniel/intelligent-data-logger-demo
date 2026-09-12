from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.evaluation.m6_cases import M6_QUERY_CASES, M6_SCENARIO_CASES
from src.evaluation.runner import load_ground_truth, _truth_by_type
from src.evaluation.scoring import score_query, score_scenario
from src.reasoning.agent import fallback_answer
from src.reasoning.tools import execute_tool

ROOT = Path(__file__).resolve().parents[2]


def run_m6_evaluation() -> dict[str, Any]:
    truth = _truth_by_type(load_ground_truth())
    scenarios=[]
    for case in M6_SCENARIO_CASES:
        evidence=execute_tool(case.tool_name,dict(case.tool_args))
        scenarios.append(score_scenario(case,truth[case.event_type],evidence))
    queries=[]
    for case in M6_QUERY_CASES:
        evidences=[execute_tool(name,dict(args)) for name,args in case.evidence_calls]
        queries.append(score_query(case,evidences,fallback_answer(case.question)))
    return {
        "milestone":"M6", "synthetic_data":True,
        "evaluation_type":"internal dry-run against the frozen M5 rubric; not statistical validation",
        "m5_rubric_changed":False,
        "scenario_results":scenarios,
        "canonical_query_results":queries,
        "m5_gap_resolution":{
            "battery_degradation_diagnosis":"addressed with observed-SOC/power capacity-trend estimator",
            "sensor_dropout_localization":"addressed with contiguous missing-interval localization",
        },
        "final_scope_completion":{
            "grid_outage_islanding":"required Scenario 6 implemented and evaluated from observed grid/inverter/battery/load telemetry",
            "required_scenario_count":6,
            "canonical_query_count":11,
        },
        "remaining_declared_limitations":[
            "Battery capacity estimation is a controlled-demo analytic and is not a field-validated SOH estimator.",
            "Forecasting remains a transparent recent-generation persistence baseline.",
            "Battery runway remains a constant-load estimate using configured nominal usable capacity.",
            "Production telemetry jitter/retry handling, fleet analysis, and real-device connectivity remain out of demo scope.",
            "Grid-outage/islanding behaviour is a controlled synthetic backup model, not validation against a specific inverter vendor or protection scheme.",
        ],
    }


def render_markdown(report:dict[str,Any])->str:
    lines=[
        "# M6 Internal Dry-Run Report","",
        "> **Synthetic demo only.** M6 reruns the frozen M5 dimensions after targeted capability-gap fixes; it is not a statistical or field validation.","",
        "## Scenario results","",
        "| Scenario | Detection | Localization | Diagnosis | Evidence | Calibration | Abstention | Overall |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in report["scenario_results"]:
        d=r["dimensions"]; g=lambda k:d.get(k,{}).get("status","N/A")
        lines.append(f"| {r['label']} | {g('detection')} | {g('localization')} | {g('diagnosis')} | {g('evidence_grounding')} | {g('calibration')} | {g('abstention')} | **{r['overall']}** |")
    lines += ["","## M5 gap resolution","",
              "- **Battery degradation:** now inferred from observed SOC + charge/discharge flows; the operational diagnostic does not read `battery_usable_capacity_wh` or `battery_stored_energy_wh`.",
              "- **Sensor dropout:** now localized to the contiguous missing interval from observed missingness/cadence; ground truth is used only afterward by evaluation scoring.",
              "","## Final required Scenario 6","",
              "- **Grid outage/islanding:** generated before dispatch, diagnosed from observed grid/inverter/battery/load telemetry, and evaluated on the unchanged six M5 dimensions. Zero grid import alone is explicitly not sufficient evidence of an outage.",
              "","## Eleven canonical queries","","| # | Purpose | Status | Supporting analytics |","|---:|---|---|---|"]
    for q in report["canonical_query_results"]:
        lines.append(f"| {q['id']} | {q['purpose']} | **{q['status']}** | {', '.join(q['supporting_tools'])} |")
    lines += ["","## Remaining declared limitations",""]+[f"- {x}" for x in report["remaining_declared_limitations"]]
    lines += ["","## Interpretation","",
              "- The M5 scoring dimensions/rubric were not changed after seeing M5 results.",
              "- M6 changes operational capabilities, then applies the same dimension-level scoring logic.",
              "- No aggregate accuracy percentage or statistical-significance claim is made.",
              "- Ground truth remains evaluation-only and is not an input to the new operational diagnostics.",""]
    return "\n".join(lines)


def write_m6_report(output_dir:Path=ROOT/"reports", report:dict[str,Any]|None=None):
    output_dir.mkdir(parents=True,exist_ok=True); r=report if report is not None else run_m6_evaluation()
    jp=output_dir/"m6_dry_run.json"; mp=output_dir/"m6_dry_run.md"
    jp.write_text(json.dumps(r,indent=2),encoding="utf-8"); mp.write_text(render_markdown(r),encoding="utf-8")
    return jp,mp

if __name__=="__main__":
    j,m=write_m6_report(); print(f"Wrote {j.relative_to(ROOT)}"); print(f"Wrote {m.relative_to(ROOT)}")
