# M5 Controlled Evaluation Report

> **Synthetic demo only.** This is a controlled functional evaluation of authored scenarios, not evidence of field accuracy or statistical validation.

## Scenario scoring

| Scenario | Detection | Localization | Diagnosis | Evidence | Calibration | Abstention | Overall |
|---|---|---|---|---|---|---|---|
| Weather-driven PV production drop | PASS | PASS | PASS | PASS | PASS | N/A | **PASS** |
| Customer overload preceding inverter alarm/derating | PASS | PASS | PASS | PASS | PASS | N/A | **PASS** |
| Gradual irradiance/temperature-normalized PV performance decline | PASS | PASS | PASS | PASS | PASS | N/A | **PASS** |
| Battery usable-capacity degradation signature | FAIL | N/A | FAIL | N/A | PASS | PASS | **CAPABILITY_GAP** |
| Sensor/telemetry dropout | PASS | PARTIAL | PASS | PASS | PASS | PASS | **PARTIAL** |

### Scenario notes

- **Battery usable-capacity degradation signature (CAPABILITY_GAP):** No dedicated observed-telemetry battery-health/capacity-degradation diagnostic exists in the reviewer-approved M3/M4 baseline. M5 records this as a capability gap rather than fabricating a diagnosis.
- **Sensor/telemetry dropout (PARTIAL):** See dimension rationales in the JSON report.

## Ten canonical queries

| # | Query purpose | Status | Supporting analytics |
|---:|---|---|---|
| 1 | Status-first snapshot | **PASS** | current_system_status |
| 2 | Weather-vs-fault discrimination | **PASS** | analyze_generation_drop |
| 3 | Energy/self-sufficiency decision support | **PASS** | energy_balance |
| 4 | Multi-tool anomaly + trend orchestration | **PASS** | summarize_inverter_anomalies, detect_gradual_performance_decline |
| 5 | Cross-component root-cause diagnosis | **PASS** | diagnose_overload |
| 6 | Battery-runway estimate with assumptions | **PASS** | battery_runway |
| 7 | Sustainability decision support | **PASS** | sustainability_metrics |
| 8 | Financial decision support | **PASS** | financial_metrics |
| 9 | Data-quality-aware abstention | **PASS** | assess_data_availability |
| 10 | Adversarial certainty/blame calibration | **PASS** | diagnose_overload |

## Interpretation

- Results are deliberately **not aggregated into an accuracy percentage**.
- A scenario can be detected but only partially localized; those dimensions remain separate.
- Ground truth is read only by `src/evaluation/` and is never passed into operational analytics/reasoning.
- The battery-degradation scenario is an explicit current capability gap: the evaluator refuses to manufacture a diagnosis from latent ground truth.
- M6 is the appropriate milestone for fixing any diagnosis/evidence/calibration mismatch revealed here while keeping the scoring rubric fixed.
- The frozen M1 scope contains the five non-stretch scenarios; optional grid outage/islanding is not retroactively added by M5.
- Canonical query 2 resolves 'yesterday' to 2026-08-05 for deterministic scenario scoring.
- M5 scores tool/evidence correctness rather than nondeterministic LLM prose; notebook 04 can exercise the live Claude loop when an API key is supplied.
