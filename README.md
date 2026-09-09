# Intelligent Data Logger — Demo Experiment

A reproducible feasibility demo for a conversational intelligence layer over solar PV, inverter, battery, load, grid, and weather telemetry.

> **Important:** all telemetry in this repository is synthetic. This repo demonstrates architecture and reasoning/orchestration, not real-world accuracy or field validation.

## What this repo proves

**M0** demonstrates the flagship installer scenario: a customer reports that an inverter "failed on its own," while the telemetry contains a sustained overload immediately before an inverter overload alarm and derating event. The system computes the diagnosis with deterministic analytics, packages the result as structured evidence, and then presents it conversationally.

**M1** adds a second, materially different query family: a cloudy-day PV production drop. It also introduces genuine Claude tool use: when an API key is configured, Claude receives both the inverter-failure and generation-drop analytics tools and must select the appropriate routine before producing an answer.

The LLM is **not** the source of engineering truth. Calculations and diagnoses come from tested Python functions. Claude selects/orchestrates those functions and explains their structured evidence outputs.

## Architecture

```text
Synthetic telemetry -> local CSV store -> Claude tool selection -> deterministic analytics -> evidence object -> grounded answer
```

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
python -m src.generator.simulate
python -m src.interface.status_card
python -m src.reasoning.agent
pytest -q
```

Without an `ANTHROPIC_API_KEY`, `src.reasoning.agent` uses a deterministic fallback response so the demo remains runnable end-to-end. To use Claude, copy `.env.example` to `.env` and provide a key. `ANTHROPIC_MODEL` is optional so the live model identifier can be configured without changing source code.

## Current implemented slice (M0 + M1)

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

## Planned expansion from the experiment brief

With the overload and cloudy-day scenarios implemented, the remaining planned scenarios include gradual efficiency decline, battery degradation, sensor dropout, optional grid outage/islanding, broader financial and sustainability queries, richer scenario scoring, and executable notebook walkthroughs.

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

## Safety and interpretation

This demo is read-only. It does not control an inverter, battery, or load. Synthetic temporal associations should not be treated as proof of customer responsibility, warranty liability, or real-world fault causality. M1 also separates the existence of an inverter event from its estimated full-day energy impact, so brief alarms are not silently discarded merely because daily production loss is small.

Current automated test suite: **19 passing tests**.
