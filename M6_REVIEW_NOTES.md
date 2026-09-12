# M6 Review Notes

## Scope and freeze policy

M6 is the brief's **internal dry run, diagnosis-mismatch repair, and polish** milestone. M5 remains the frozen evaluation baseline: its report still records battery degradation as `CAPABILITY_GAP` and sensor-dropout localization as `PARTIAL`. M6 does not rewrite those results or alter the six scoring dimensions.

M6 addresses the two capability boundaries exposed by M5 and completes the practical grid-interaction scope required for the final experiment:

1. infer a battery usable-capacity decline from operationally observable SOC and charge/discharge power rather than the simulator's latent capacity state;
2. localize a missing-telemetry interval rather than returning only a day-level window;
3. add required Scenario 6: utility-grid outage with islanded backup operation and restoration.

The frozen M5 baseline is not rewritten: it still contains the original five-scenario scope and ten canonical queries. Scenario 6 is introduced only in the final M6 experiment, while reusing the same six scoring dimensions.

## Battery degradation diagnostic

`src/analytics/battery_health.py` estimates effective usable capacity from interval energy throughput and SOC movement:

- inputs: timestamp, battery SOC, battery charge power, battery discharge power, configured interval and charge/discharge efficiencies;
- explicitly not inputs: `battery_usable_capacity_wh`, `battery_stored_energy_wh`, or `ground_truth.json`;
- interval estimates are filtered for meaningful SOC movement, flow/SOC direction agreement, and broad physical plausibility;
- daily medians are compared longitudinally;
- the output is labelled a controlled-demo estimator, **not** a field-validated state-of-health estimator.

On the bundled synthetic telemetry it estimates approximately 9.00 kWh early versus 8.49 kWh late, a ~5.66% decline, close to but not copied from the injected 6% capacity fade.

Counterfactual regression coverage verifies that a regenerated constant-capacity battery is not falsely diagnosed as degrading and that insufficient cycling data causes abstention.

## Dropout localization

`localize_data_unavailability()` derives missingness from observed telemetry only, groups contiguous missing rows using the observed cadence, and reports the half-open missing interval `[start, end)`. On the controlled dropout it independently returns `2026-09-18 12:00` to `12:45` Africa/Lagos.

The legacy day-level `assess_data_availability()` remains in place so the frozen M5 baseline can still be reproduced. M6 adds the refined capability rather than retroactively changing M5's evidence receipt.


## Required grid-outage/islanding scenario

Scenario 6 is now mandatory for final experiment acceptance. The simulator injects a 60-minute utility outage on `2026-10-10 21:35–22:35` Africa/Lagos before dispatch is solved. The installation uses a configured 30% battery backup reserve while the grid is available; during the outage the physical discharge floor reverts to the battery minimum SOC so backup energy can be used.

Observed event behaviour in the bundled dataset includes:

- `grid_available=False` for the exact outage interval;
- `grid_import_w=0` and `grid_export_w=0` throughout the outage;
- `inverter_operating_state='islanded'`;
- immediate battery-discharge increase of about 377 W relative to the preceding interval, replacing the lost grid contribution;
- battery SOC decline of about 12.8 percentage points;
- zero local power-balance residual within numerical tolerance;
- explicit demand accounting (`requested = served + unmet`) when islanded local supply is insufficient;
- explicit PV accounting (`available = delivered + curtailed`) when islanded PV surplus cannot be absorbed;
- automatic return to grid-connected `normal` operation after restoration.

`diagnose_grid_outage()` uses only observed telemetry. It does not read `ground_truth.json`. Its negative-control logic explicitly demonstrates that zero grid import while `grid_available=True` is ordinary self-sufficient operation, not evidence of an outage. If explicit `unmet_load_w` is present during a physically balanced outage, it reports `grid_outage_with_load_shedding` rather than falsely claiming that all requested load was maintained.

## M6 evaluation

`src/evaluation/m6_runner.py` applies the same dimension-level scoring logic used by M5 to the improved operational evidence. The M5 rubric is not changed after observing its results.

Current M6 dry-run outcome:

- all six required final scenarios: PASS on every applicable M5 dimension;
- sensor dropout: PASS on detection, localization, diagnosis/evidence, calibration and abstention;
- all eleven canonical query evidence paths: PASS;
- physical validation: PASS;
- automated suite: 80/80 tests pass when run across the test modules; the final dry-run script also passes end-to-end.

These are controlled synthetic results, not an accuracy percentage or field-validation claim.

## Reviewer focus

Please verify especially:

- the battery diagnostic never reads latent capacity/stored-energy fields or ground truth;
- the no-degradation counterfactual does not false-positive;
- the battery diagnostic abstains with insufficient observed transitions;
- dropout localization is derived from observed missingness/cadence rather than the oracle;
- `reports/m5_evaluation.*` remains a frozen record of the pre-M6 baseline;
- M6 reuses the M5 scoring dimensions rather than moving the rubric;
- the fresh-clone quickstart and `scripts/run_m6_dry_run.py` complete cleanly;
- grid-outage diagnosis does not treat zero grid import alone as outage evidence;
- the grid event is generated before dispatch and still passes physical energy-balance validation;
- outage demand above battery power capacity is recorded as explicit unmet load rather than disappearing from the balance;
- long outages that deplete the battery to its SOC floor preserve the same accounting invariant;
- islanded daytime PV surplus is explicitly curtailed rather than disappearing from the balance;
- README limitations remain explicit and do not imply real-world battery-health accuracy.
