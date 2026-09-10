# M3 + M4 Review Notes

## Scope
This build intentionally combines M3 (deterministic analytics) and M4 (evidence/tool orchestration + status-first interface). It does not implement M5 notebooks/scoring or M6 polish.

## M3 acceptance gate
- Analytics remain callable without an LLM.
- Gradual PV decline is detected from observed telemetry only; the latent simulator performance factor is not an input.
- Irradiance and ambient-temperature normalization are explicit; clipping samples are excluded from the trend calculation.
- Energy balance, battery runway, financial, sustainability, anomaly, forecasting and data-availability routines are independently testable.
- Financial, sustainability, forecast and runway outputs carry material assumptions.
- Sensor-dropout analysis abstains when required observations are unavailable.

## M4 acceptance gate
- Eleven approved tools expose analytics through structured evidence objects.
- Ground truth is not loaded by the operational reasoning path.
- Claude can select one tool or multiple tools in a round; a mocked Anthropic test verifies multi-tool orchestration without requiring a live API call.
- The system prompt prohibits independent engineering/financial calculation, raw-time-series reasoning, unsupported blame and over-certainty.
- The deterministic offline router covers all ten canonical demo questions.
- The adversarial responsibility query refuses to turn overload evidence into proof of customer responsibility.
- Status-first output includes PV, load, battery SOC, estimated runway, grid flow and active alarm.

## Deliberate limitations / backlog
- Forecasting is a simple recent-median persistence baseline; weather-informed forecasting is later work.
- Battery runway uses configured nominal usable capacity and constant current load; no battery-capacity estimator is claimed.
- Gradual-decline analytics are a controlled-demo detector, not field-validated degradation estimation.
- Canonical UTC/epoch storage for cross-timezone SQL queries remains a production backlog item.
- M5 owns notebooks, multidimensional scenario scoring, README/Colab walkthrough completion.


## Reviewer hardening follow-up
- Replaced resolution-sensitive `.asi8`/`Timestamp.value` epoch arithmetic in both gradual PV decline and battery degradation with pandas `Timedelta` division. This is robust to nanosecond vs microsecond `DatetimeIndex` resolution and has an explicit regression test using a microsecond-resolution index.
- Relaxed the SQLite timestamp round-trip assertion to compare timestamp values rather than dtype metadata; the store contract is value/timezone fidelity, not identical pandas resolution tags.
- Hardened `summarize_inverter_anomalies`: overload is asserted only when the alarm-associated window contains sustained above-rating load and an overload-coded alarm. Non-overload alarms remain descriptive/undetermined, and alternatives are populated with checked evidence. Added a thermal-trip counterfactual regression test.
