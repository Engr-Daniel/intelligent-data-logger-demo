from __future__ import annotations

import json
from pathlib import Path
import pytest

from src.evaluation.cases import CANONICAL_QUERY_CASES, SCENARIO_CASES
from src.evaluation.runner import render_markdown, run_m5_evaluation

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def m5_report():
    return run_m5_evaluation()


def _scenario(report, event_type):
    return next(r for r in report["scenario_results"] if r["event_type"] == event_type)


def test_m5_covers_all_five_implemented_ground_truth_scenarios(m5_report):
    report = m5_report
    expected = {
        "cloudy_day_generation_drop",
        "customer_overload",
        "gradual_efficiency_decline",
        "battery_degradation_signature",
        "sensor_dropout",
    }
    assert {r["event_type"] for r in report["scenario_results"]} == expected
    assert len(SCENARIO_CASES) == 5


def test_m5_scores_required_dimensions_separately(m5_report):
    report = m5_report
    required = {"detection", "localization", "diagnosis", "evidence_grounding", "calibration", "abstention"}
    for result in report["scenario_results"]:
        assert set(result["dimensions"]) == required


def test_weather_overload_and_gradual_decline_score_as_supported(m5_report):
    report = m5_report
    for event in ["cloudy_day_generation_drop", "customer_overload", "gradual_efficiency_decline"]:
        r = _scenario(report, event)
        assert r["overall"] == "PASS"
        assert r["dimensions"]["detection"]["status"] == "PASS"
        assert r["dimensions"]["diagnosis"]["status"] == "PASS"
        assert r["dimensions"]["evidence_grounding"]["status"] == "PASS"


def test_sensor_dropout_requires_abstention_and_does_not_claim_full_localization(m5_report):
    report = m5_report
    r = _scenario(report, "sensor_dropout")
    assert r["dimensions"]["abstention"]["status"] == "PASS"
    assert r["dimensions"]["localization"]["status"] == "PARTIAL"
    assert r["evidence"]["data_quality"]["sufficient"] is False


def test_battery_degradation_gap_is_exposed_not_manufactured(m5_report):
    report = m5_report
    r = _scenario(report, "battery_degradation_signature")
    assert r["overall"] == "CAPABILITY_GAP"
    assert r["evidence"] is None
    assert r["dimensions"]["diagnosis"]["status"] == "FAIL"
    assert r["dimensions"]["abstention"]["status"] == "PASS"


def test_m5_has_exactly_ten_canonical_queries_and_all_trace_cleanly(m5_report):
    report = m5_report
    assert len(CANONICAL_QUERY_CASES) == 10
    assert [r["id"] for r in report["canonical_query_results"]] == list(range(1, 11))
    assert all(r["status"] == "PASS" for r in report["canonical_query_results"])


def test_adversarial_query_refuses_unsupported_blame(m5_report):
    report = m5_report
    q10 = next(r for r in report["canonical_query_results"] if r["id"] == 10)
    assert q10["checks"]["no_unsupported_blame"] is True
    assert "cannot prove customer responsibility" in q10["offline_answer"].lower()


def test_financial_sustainability_and_runway_queries_expose_assumptions(m5_report):
    report = m5_report
    for qid in [6, 7, 8]:
        q = next(r for r in report["canonical_query_results"] if r["id"] == qid)
        assert q["checks"]["assumptions_exposed_when_material"] is True
        assert all(e["assumptions"] for e in q["evidence"])


def test_report_explicitly_avoids_accuracy_percentage_claims(m5_report):
    report = m5_report
    assert "No accuracy percentage" in report["aggregation_policy"]
    md = render_markdown(report)
    assert "not aggregated into an accuracy percentage" in md
    assert "statistical validation" in md


def test_ground_truth_access_is_confined_to_evaluation_package():
    import ast
    operational_dirs = [ROOT / "src" / p for p in ["analytics", "reasoning", "interface", "datacontext", "storage"]]
    for directory in operational_dirs:
        for path in directory.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    assert not (node.module or "").startswith("src.evaluation"), f"Operational code imports evaluator: {path}"
                if isinstance(node, ast.Import):
                    assert all(not alias.name.startswith("src.evaluation") for alias in node.names), f"Operational code imports evaluator: {path}"
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "load_ground_truth":
                    raise AssertionError(f"Operational code calls evaluation oracle: {path}")


def test_m5_notebooks_are_real_and_label_synthetic_data():
    for name in [
        "01_generate_synthetic_data.ipynb",
        "02_explore_and_validate_data.ipynb",
        "03_analytics_library_demo.ipynb",
        "04_reasoning_walkthrough.ipynb",
        "05_scenario_scoring.ipynb",
    ]:
        path = ROOT / "notebooks" / name
        nb = json.loads(path.read_text(encoding="utf-8"))
        sources = "\n".join("".join(c.get("source", [])) if isinstance(c.get("source"), list) else c.get("source", "") for c in nb["cells"])
        assert "SYNTHETIC DATA DEMO" in sources
        assert "github.com/Engr-Daniel/intelligent-data-logger-demo.git" in sources
        assert len(nb["cells"]) >= 4


def test_scenario_scoring_notebook_calls_final_real_evaluator():
    nb = json.loads((ROOT / "notebooks" / "05_scenario_scoring.ipynb").read_text(encoding="utf-8"))
    sources = "\n".join("".join(c.get("source", [])) if isinstance(c.get("source"), list) else c.get("source", "") for c in nb["cells"])
    assert "run_m6_evaluation" in sources
    assert "write_m6_report" in sources
    assert "M5 report remains frozen" in sources


def test_executed_notebooks_contain_no_error_outputs():
    import json
    for path in sorted((ROOT / "notebooks").glob("0*.ipynb")):
        nb = json.loads(path.read_text(encoding="utf-8"))
        for cell in nb.get("cells", []):
            for output in cell.get("outputs", []):
                assert output.get("output_type") != "error", f"Notebook contains an execution error: {path}"
