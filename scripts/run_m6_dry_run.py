from __future__ import annotations
import json, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from src.evaluation.m6_runner import write_m6_report, run_m6_evaluation
from src.datacontext.validation import validate_telemetry
from src.datacontext.context import load_installation_config, load_schema
from src.storage.local_store import load_telemetry

start=time.perf_counter()
validation=validate_telemetry(load_telemetry(),load_installation_config(),load_schema())
report=run_m6_evaluation()
scenario_ok=all(r["overall"]=="PASS" for r in report["scenario_results"])
queries_ok=all(q["status"]=="PASS" for q in report["canonical_query_results"])
validation_ok=validation["status"]=="PASS"
j,m=write_m6_report()
summary={"physical_validation":validation["status"],"all_scenarios_pass":scenario_ok,"all_canonical_queries_pass":queries_ok,"elapsed_seconds":round(time.perf_counter()-start,2),"report":str(m.relative_to(ROOT))}
print(json.dumps(summary,indent=2))
if not (scenario_ok and queries_ok and validation_ok): raise SystemExit(1)
