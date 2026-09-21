"""Run the offline experiment and preserve timestamped evidence separately."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.datacontext.context import load_installation_config, load_schema
from src.datacontext.validation import validate_telemetry
from src.evaluation.m6_cases import M6_QUERY_CASES
from src.evaluation.m6_runner import run_m6_evaluation, write_m6_report
from src.evaluation.runner import write_report
from src.generator.simulate import main as generate
from src.interface.status_card import current_status
from src.reasoning.agent import fallback_answer
from src.storage.local_store import load_telemetry


def main() -> None:
    started = datetime.now(timezone.utc)
    output = ROOT / "reports" / "runs" / started.strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True)

    def save(name, value):
        (output / name).write_text(json.dumps(value, indent=2), encoding="utf-8")

    print(f"Saving experiment evidence to {output}", flush=True)
    generate()
    telemetry = load_telemetry()
    validation = validate_telemetry(telemetry, load_installation_config(), load_schema())
    save("physical_validation.json", validation)
    write_report(output)
    report = run_m6_evaluation()
    write_m6_report(output, report)
    save("status_card.json", current_status())
    save("offline_walkthrough.json", [
        {"question": case.question, "answer": fallback_answer(case.question)}
        for case in M6_QUERY_CASES
    ])
    passed = (
        validation["status"] == "PASS"
        and len(report["scenario_results"]) == 6
        and all(r["overall"] == "PASS" for r in report["scenario_results"])
        and len(report["canonical_query_results"]) == 11
        and all(r["status"] == "PASS" for r in report["canonical_query_results"])
    )
    files = [ROOT / "config/installation.yaml", ROOT / "data/ground_truth.json"]
    files += sorted((ROOT / "src").rglob("*.py"))
    files += sorted((ROOT / "tests").rglob("*.py"))
    files += [Path(__file__).resolve(), ROOT / "requirements.txt", ROOT / "requirements-dev.txt",
              ROOT / "src/datacontext/schema.yaml", ROOT / "data/processed/telemetry.csv"]
    save("run_manifest.json", {
        "started_utc": started.isoformat(),
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "offline deterministic; no live LLM calls",
        "synthetic_data": True,
        "python": platform.python_version(),
        "packages": {name: version(name) for name in
                     ("pandas", "numpy", "PyYAML", "python-dotenv", "pytest")},
        "rows": len(telemetry),
        "first_timestamp": str(telemetry.timestamp.min()),
        "last_timestamp": str(telemetry.timestamp.max()),
        "physical_validation": validation["status"],
        "m6_passed": passed,
        "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in files},
    })
    print(json.dumps({"passed": passed, "rows": len(telemetry),
                      "output": str(output)}, indent=2), flush=True)
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
