# Research results

**Current evidence: a controlled synthetic feasibility demonstration.** The offline
run completed on 21 September 2026. Live Claude evaluation and the manuscript's
comparative research study have not yet been performed.

## Experiment conditions

| Item | Recorded value |
|---|---|
| Run | `20260921T055826825005Z` |
| Installations / seeds | One synthetic installation / seed 42 |
| Telemetry | 34,560 rows; five-minute cadence; 120 simulated days |
| Simulated dates | 1 August–28 November 2026, Africa/Lagos |
| Equipment | 6.6 kWp PV; 5 kW inverter; 10 kWh nominal battery |
| Physical validation | PASS |
| M6 scenarios | Six PASS on all applicable dimensions |
| Canonical query checks | Eleven PASS, deterministic offline answers |
| Regression tests | 80 passed; no errors, failures or skipped tests |

The dates above are simulator dates, not observations collected through November.
Rows, scenarios and query checks are different units; none is an independent field trial.

## Scenario results and measured evidence

Values below are copied from the archived structured evidence, not new estimates.

| Scenario | M5 outcome | M6 outcome | Selected M6 evidence |
|---|---|---|---|
| Weather-driven generation drop | PASS | PASS | PV power drop 61.0%; irradiance drop 62.1% against surrounding-day baseline |
| Overload preceding inverter alarm | PASS | PASS | Peak load 6,403.9 W vs 5,000 W inverter rating; 40 minutes above rating; `OVERLOAD_02` |
| Gradual PV performance decline | PASS | PASS | Normalized decline 8.0%; early/late median performance ratio 0.9650 / 0.8878 |
| Battery capacity degradation | CAPABILITY_GAP | PASS | Estimated usable capacity 9,000.0 to 8,490.7 Wh; estimated decline 5.66% |
| Telemetry dropout | PARTIAL | PASS | Nine affected rows; 45-minute gap localized; insufficient-data diagnosis abstains |
| Grid outage / islanding | Not evaluated in M5 | PASS | 60-minute outage; mean grid import 0 W; SOC drop 12.76 percentage points; unmet load 0 Wh |

Battery values are outputs of a controlled-demo SOC/power estimator, not measured
field state of health. Overload evidence supports a technical explanation, not proof
of customer responsibility. M5 and M6 are development milestones; their comparison
does not isolate the causal benefit of history or cross-component reasoning.

## Inspect and reuse the results

- [Run summary and exact execution commands](reports/runs/20260921T055826825005Z/README.md)
- [M6 dimension-by-dimension table and eleven query checks](reports/runs/20260921T055826825005Z/m6_dry_run.md)
- [Full M6 evidence and scoring rationales](reports/runs/20260921T055826825005Z/m6_dry_run.json)
- [M5 outcomes, including gaps](reports/runs/20260921T055826825005Z/m5_evaluation.md)
- [Eleven questions and offline answers](reports/runs/20260921T055826825005Z/offline_walkthrough.json)
- [Physical validation](reports/runs/20260921T055826825005Z/physical_validation.json)
- [Versions and source/input hashes](reports/runs/20260921T055826825005Z/run_manifest.json)
- [Regression-test record](reports/runs/20260921T055826825005Z/tests.xml)

CSV exports derived directly from that run's M6 JSON:

- [Scenario dimensions and rationales](reports/runs/20260921T055826825005Z/scenario_dimensions.csv)
- [All scenario measurements, units and evidence windows](reports/runs/20260921T055826825005Z/scenario_measurements.csv)
- [Canonical query outcomes](reports/runs/20260921T055826825005Z/query_results.csv)

## Interpretation for the paper

A supported preliminary result is: *In one controlled synthetic installation, the
implemented deterministic pipeline passed physical validation and the predefined
checks for six authored scenarios and eleven canonical questions.*

These results do not establish live LLM reliability, generalization to unseen faults,
field diagnostic accuracy, statistical significance, expert-rated usefulness or
superiority over single-component/no-history baselines. The scenarios were authored
within the project and used during development; they are not a held-out benchmark.
Calibration here is rubric consistency, not empirical probabilistic calibration.

The manuscript's central hypothesis—incremental value from persistent history and
cross-component reasoning—requires a separately specified comparison. Track that
work in [TASK.md](TASK.md). Preserve this run as preliminary evidence rather than
presenting six passes as a research accuracy percentage.
