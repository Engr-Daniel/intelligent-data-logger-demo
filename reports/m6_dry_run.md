# M6 Internal Dry-Run Report

> **Synthetic demo only.** M6 reruns the frozen M5 dimensions after targeted capability-gap fixes; it is not a statistical or field validation.

## Scenario results

| Scenario | Detection | Localization | Diagnosis | Evidence | Calibration | Abstention | Overall |
|---|---|---|---|---|---|---|---|
| Weather-driven PV production drop | PASS | PASS | PASS | PASS | PASS | N/A | **PASS** |
| Customer overload preceding inverter alarm/derating | PASS | PASS | PASS | PASS | PASS | N/A | **PASS** |
| Gradual irradiance/temperature-normalized PV performance decline | PASS | PASS | PASS | PASS | PASS | N/A | **PASS** |
| Battery usable-capacity degradation signature | PASS | PASS | PASS | PASS | PASS | N/A | **PASS** |
| Sensor/telemetry dropout | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| Utility-grid outage with islanded backup operation | PASS | PASS | PASS | PASS | PASS | N/A | **PASS** |

## M5 gap resolution

- **Battery degradation:** now inferred from observed SOC + charge/discharge flows; the operational diagnostic does not read `battery_usable_capacity_wh` or `battery_stored_energy_wh`.
- **Sensor dropout:** now localized to the contiguous missing interval from observed missingness/cadence; ground truth is used only afterward by evaluation scoring.

## Final required Scenario 6

- **Grid outage/islanding:** generated before dispatch, diagnosed from observed grid/inverter/battery/load telemetry, and evaluated on the unchanged six M5 dimensions. Zero grid import alone is explicitly not sufficient evidence of an outage.

## Eleven canonical queries

| # | Purpose | Status | Supporting analytics |
|---:|---|---|---|
| 1 | Status-first snapshot | **PASS** | current_system_status |
| 2 | Weather-vs-fault discrimination | **PASS** | analyze_generation_drop |
| 3 | Energy/self-sufficiency decision support | **PASS** | energy_balance |
| 4 | Multi-tool anomaly + trend orchestration | **PASS** | summarize_inverter_anomalies, detect_gradual_performance_decline |
| 5 | Cross-component root-cause diagnosis | **PASS** | diagnose_overload |
| 6 | Battery-runway estimate with assumptions | **PASS** | battery_runway |
| 7 | Sustainability decision support | **PASS** | sustainability_metrics |
| 8 | Financial decision support | **PASS** | financial_metrics |
| 9 | Data-quality-aware abstention | **PASS** | localize_data_unavailability |
| 10 | Adversarial certainty/blame calibration | **PASS** | diagnose_overload |
| 11 | Grid-outage and backup-operation reasoning | **PASS** | diagnose_grid_outage |

## Remaining declared limitations

- Battery capacity estimation is a controlled-demo analytic and is not a field-validated SOH estimator.
- Forecasting remains a transparent recent-generation persistence baseline.
- Battery runway remains a constant-load estimate using configured nominal usable capacity.
- Production telemetry jitter/retry handling, fleet analysis, and real-device connectivity remain out of demo scope.
- Grid-outage/islanding behaviour is a controlled synthetic backup model, not validation against a specific inverter vendor or protection scheme.

## Interpretation

- The M5 scoring dimensions/rubric were not changed after seeing M5 results.
- M6 changes operational capabilities, then applies the same dimension-level scoring logic.
- No aggregate accuracy percentage or statistical-significance claim is made.
- Ground truth remains evaluation-only and is not an input to the new operational diagnostics.
