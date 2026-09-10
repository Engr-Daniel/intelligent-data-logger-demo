# Intelligent Data Logger — Demo Experiment

A reproducible feasibility demo for a conversational intelligence layer over solar PV, inverter, battery, load, grid, and weather telemetry.

> **Important:** all telemetry in this repository is synthetic. This repo demonstrates architecture and reasoning/orchestration, not real-world accuracy or field validation.

## What this repo proves

**M0** demonstrates the flagship installer scenario: a customer reports that an inverter "failed on its own," while the telemetry contains a sustained overload immediately before an inverter overload alarm and derating event. The system computes the diagnosis with deterministic analytics, packages the result as structured evidence, and then presents it conversationally.

**M1** completes the required 120-day synthetic generator with weather-driven generation drop, customer overload/inverter derating, gradual PV efficiency decline, battery usable-capacity degradation, and sensor dropout ground truth. The previously completed reasoning proof remains intact: when an API key is configured, Claude receives both inverter-failure and generation-drop tools and must select the appropriate routine before answering.

The LLM is **not** the source of engineering truth. Calculations and diagnoses come from tested Python functions. Claude selects/orchestrates those functions and explains their structured evidence outputs.

## Architecture

```text
Synthetic telemetry -> local SQLite store -> data context/config -> Claude tool selection -> deterministic analytics -> evidence object -> grounded answer
```

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
python -m src.generator.simulate
python -m src.datacontext.validate_demo
python -m src.interface.status_card
python -m src.reasoning.agent
pytest -q
```

Without an `ANTHROPIC_API_KEY`, `src.reasoning.agent` uses a deterministic fallback response so the demo remains runnable end-to-end. To use Claude, copy `.env.example` to `.env` and provide a key. `ANTHROPIC_MODEL` is optional so the live model identifier can be configured without changing source code.

## Current implemented slice (M0 + M1 + M2)

- Weather-driven cloudy-day PV production-drop scenario with ground truth
- Production-drop analytics comparing target-day PV/irradiance with surrounding-day baselines and checking inverter/thermal/data-quality alternatives
- Separate diagnostic outcomes for weather-driven material loss, fault-related material loss, brief inverter events with limited daily energy impact, and normal/no-material-anomaly days
- Real Claude tool-use loop with two registered tools: `investigate_inverter_failure` and `investigate_generation_drop`
- Offline deterministic routing fallback when no Anthropic key is configured; explicit ISO-style dates are honored, while date-free queries retain anomaly auto-selection
- Physically constrained PV/load/battery/grid simulation with derating applied before downstream energy balancing
- Energy-conserving battery state update
- Injected sustained overload scenario and ground truth
- Overload root-cause analytics with evidence-backed alternative-cause checks (grid availability, irradiance, thermal conditions, data completeness)
- Structured evidence object
- Conversational response layer with conservative certainty language
- Status-card view
- Starter energy-balance, battery-runway, financial, and sustainability analytics
- Physical-invariant and diagnostic regression tests, including forced daytime derating, fault-vs-weather discrimination, brief-fault/limited-impact reporting, normal-day behavior, SOC/power bounds, and power-balance closure
- Financial metrics that distinguish simple ROI from annualized simple payback

## M1 completion and M2 storage/context layer

The generator now covers the five required synthetic scenarios: cloudy-day generation drop, customer overload leading to inverter derating/alarm, gradual PV efficiency decline, battery usable-capacity degradation, and intentional sensor dropout. The optional grid-outage/islanding scenario remains a stretch goal. The simulation spans 120 days at 5-minute resolution and records scoring-only event ground truth separately.

M2 adds a persistent SQLite Datalodger stand-in at `data/processed/datalodger.sqlite`, while retaining CSV as a convenient export. `src/datacontext/schema.yaml` is the versioned telemetry contract for fields, units, types, expected ranges, cadence, and missing-data policy. `config/installation.yaml` separately records technical, financial, sustainability, and simulation assumptions. Analytics/reasoning and the status card now read telemetry through the local-store boundary rather than directly from generator internals.

`src/datacontext/validation.py` performs machine-testable sanity checks for required fields, timestamp uniqueness/cadence, observed missingness, schema ranges, interval power balance, SOC and battery power limits, stored energy vs usable capacity, and battery energy-state transitions. It does not consult experiment ground truth: missing telemetry is detected from observations and reported with physics-validation coverage. Validation can return `PASS`, `FAIL`, or `INSUFFICIENT_DATA`. Strict 5-minute cadence is a synthetic-demo assumption, not a claim about production telemetry behavior. For battery-transition validation, `input_coverage_pct` measures telemetry completeness and governs sufficiency, while `equation_applicability_pct` reports the fraction of possible transitions to which the current M2 flow-only equation applies. Capacity-boundary transitions are explicitly classified as `structural_non_evaluable_rows`, not as missing data. A battery-transition `PASS` means sufficient input telemetry was available and no violations were found among transitions to which that equation applies; it does not claim that every transition was evaluated.

Experiment truth is deliberately separated from operational storage: `data/processed/datalodger.sqlite` contains telemetry only, while `data/ground_truth.json` is reserved for scoring/evaluation. `battery_usable_capacity_wh` is a simulated latent health state used to construct the degradation scenario; the demo does not imply that ordinary inverter telemetry directly measures usable battery capacity.

The next milestone from the experiment brief is M3: complete the analytics function library and its unit tests, including performance/trend analytics and full financial/sustainability assumption handling.

See [`DEMO_EXPERIMENT_BRIEF.md`](DEMO_EXPERIMENT_BRIEF.md) for the complete experimental design and limitations.

## Repository layout

```text
intelligent-data-logger-demo/
├── config/installation.yaml
├── data/
├── notebooks/
├── src/
│   ├── analytics/
│   ├── datacontext/
│   ├── evidence/
│   ├── generator/
│   ├── interface/
│   └── reasoning/
├── tests/
├── DEMO_EXPERIMENT_BRIEF.md
├── requirements.txt
└── requirements-dev.txt
```

## M3 + M4 implemented slice

M3 completes the deterministic analytics layer used by the demo: energy balance, normalized PV performance/trend detection, generic anomaly detection, inverter anomaly summary, simple generation persistence forecasting, battery runway, financial metrics, sustainability metrics, and observed-telemetry data-availability assessment. The gradual-decline detector uses observed PV/irradiance/temperature telemetry, excludes clipping samples, and does not read the simulator's latent performance factor.

M4 expands the evidence/tool boundary to eleven approved tools. Claude receives structured evidence objects rather than raw telemetry and may call multiple tools in one reasoning round. The system prompt prohibits independent engineering/financial calculation and unsupported blame. Missing telemetry forces an evidence-level abstention. The offline deterministic router covers the ten canonical demo questions, and the status card now includes battery runway and alert context.

The M3/M4 implementation remains a synthetic feasibility demonstration. The generation forecast is a transparent median-persistence baseline, not a weather-informed production model; battery runway uses configured nominal usable capacity rather than claiming a field-calibrated health estimate; and ROI/carbon outputs depend on the versioned assumptions in `config/installation.yaml`.

## Safety and interpretation

This demo is read-only. It does not control an inverter, battery, or load. Synthetic temporal associations should not be treated as proof of customer responsibility, warranty liability, or real-world fault causality. M1 also separates the existence of an inverter event from its estimated full-day energy impact, so brief alarms are not silently discarded merely because daily production loss is small.

Current automated test suite: **32 passing tests**.
