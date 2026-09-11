# Intelligent Data Logger — Demo Experiment

A reproducible feasibility demo for a conversational intelligence layer over solar PV, inverter, battery, load, grid, and weather telemetry.

> **Important:** all telemetry, faults, and ground truth in this repository are synthetic. This repository demonstrates architecture and controlled functional behaviour; it does **not** establish real-world accuracy, statistical validity, warranty causality, or customer responsibility.

[![Open Reasoning Walkthrough in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Engr-Daniel/intelligent-data-logger-demo/blob/main/notebooks/04_reasoning_walkthrough.ipynb)
[![Open Scenario Scoring in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Engr-Daniel/intelligent-data-logger-demo/blob/main/notebooks/05_scenario_scoring.ipynb)

## Architecture

```text
Synthetic devices
      ↓
Operational SQLite store + versioned data context
      ↓
Deterministic validation
      ↓
Deterministic analytics
      ↓
Structured evidence objects
      ↓
Claude tool orchestration / deterministic offline router
      ↓
Evidence-grounded answer

Separate experiment oracle: data/ground_truth.json → M5 scoring only
```

The LLM is **not** the source of engineering truth. Engineering, financial, sustainability, forecasting, and diagnostic quantities come from tested Python functions. The conversational layer selects/orchestrates those functions and explains their evidence outputs.

## Fresh-clone quickstart

Python 3.11+ is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements-dev.txt
python -m src.generator.simulate
python -m src.datacontext.validate_demo
python scripts/run_m5_evaluation.py
python scripts/run_m6_dry_run.py
pytest -q
```

No API key is required for generation, validation, deterministic analytics, scenario scoring, or the offline reasoning walkthrough. To exercise the live Claude tool-use loop, copy `.env.example` to `.env`, set `ANTHROPIC_API_KEY`, and optionally set `ANTHROPIC_MODEL`.

A reviewer can therefore reproduce the controlled M5 evaluation without external services. The notebook sequence is:

1. `01_generate_synthetic_data.ipynb`
2. `02_explore_and_validate_data.ipynb`
3. `03_analytics_library_demo.ipynb`
4. `04_reasoning_walkthrough.ipynb`
5. `05_scenario_scoring.ipynb`

Each notebook contains a Colab/local bootstrap and labels its outputs as synthetic.

## Milestone status

### M1 — synthetic experiment

The generator produces 120 days of 5-minute telemetry for one fictitious 6.6 kWp PV / 5 kW inverter / 10 kWh LFP installation. Five required controlled scenarios are present:

- weather-driven cloudy-day generation drop;
- sustained customer-load overload preceding inverter alarm/derating;
- gradual PV performance decline;
- gradual battery usable-capacity degradation;
- intentional sensor/telemetry dropout.

The optional grid-outage/islanding stretch scenario is not implemented. Ground truth is written separately to `data/ground_truth.json` and is never part of operational telemetry.

### M2 — trustworthy operational data boundary

`data/processed/datalodger.sqlite` contains operational telemetry only. `src/datacontext/schema.yaml` defines the telemetry contract, and `config/installation.yaml` versions technical, financial, sustainability, and simulation assumptions.

Validation checks structural integrity, missingness, ranges, interval energy balance, SOC/power constraints, and battery energy-state transitions. Results can be `PASS`, `FAIL`, or `INSUFFICIENT_DATA`. Battery transition reporting distinguishes telemetry input coverage from equation applicability so structurally non-evaluable capacity-boundary transitions are not misrepresented as validated transitions.

`battery_usable_capacity_wh` is a **simulated latent state** used to construct the controlled degradation scenario; the demo does not claim that ordinary inverter telemetry directly measures usable battery capacity.

### M3 — deterministic intelligence

The analytics library includes:

- weather-vs-fault generation-drop analysis;
- overload/root-cause analysis with alternatives;
- irradiance/temperature-normalized gradual PV performance analysis;
- generic/inverter anomaly analysis;
- energy/self-sufficiency summaries;
- battery-runway estimation;
- simple generation persistence forecasting;
- financial decision support;
- sustainability metrics;
- observed-telemetry data-availability assessment.

Known model limitations remain explicit. The forecast is a transparent recent-generation persistence baseline. Battery runway uses configured nominal usable capacity and a constant-load assumption rather than claiming a field battery-health estimate.

### M4 — evidence-grounded conversational orchestration

Eleven approved tools expose deterministic analytics as structured evidence. Claude may call multiple tools in one reasoning round but does not receive unrestricted raw time series. The system prompt prohibits independent engineering/financial calculations and unsupported blame or warranty conclusions. Missing telemetry can force abstention.

Without an API key, the deterministic router covers the same ten canonical demo questions so the walkthrough remains reproducible offline.

### M5 — controlled scenario scoring and reproducible walkthrough

M5 freezes the M3/M4 baseline and evaluates it rather than silently modifying analytics to improve results.

`src/evaluation/` scores the implemented scenarios on six independent dimensions:

- **detection** — was the event/anomaly found?
- **localization** — was the evidence window appropriately localized?
- **diagnosis** — did the leading supported cause match the injected cause where such a causal diagnosis is in scope?
- **evidence grounding** — are required measurements and tool receipts present?
- **calibration** — does stated confidence match evidence strength?
- **abstention** — are unsupported conclusions refused when evidence is insufficient?

The evaluator also traces all ten canonical questions from the experiment brief through their approved analytics/evidence paths.

Run:

```bash
python scripts/run_m5_evaluation.py
```

This writes:

- `reports/m5_evaluation.json` — machine-readable evidence and dimension-level results;
- `reports/m5_evaluation.md` — concise reviewer report.

### Important M5 result: evaluation is allowed to expose gaps

M5 deliberately reports two limitations instead of hiding them:

1. **Battery capacity degradation is currently a `CAPABILITY_GAP`.** The frozen M3/M4 baseline has no dedicated observed-telemetry battery-health/capacity-degradation diagnostic. The evaluator does not use the latent injected capacity state to manufacture an operational diagnosis.
2. **Sensor-dropout localization is `PARTIAL`.** The current data-quality analytic correctly detects missing telemetry and abstains, but its evidence window is day-level rather than the exact injected 45-minute interval.

Those are M6 candidates. The M5 rubric should remain fixed while M6 addresses diagnosis/evidence/calibration mismatches revealed by evaluation.

### M6 — internal dry run, gap resolution, and polish

M6 keeps the M5 report frozen and addresses the two capability gaps it exposed without changing the M5 scoring dimensions.

- **Battery degradation intelligence:** `detect_battery_capacity_decline()` estimates longitudinal effective usable-capacity change from observed SOC plus charge/discharge power and configured efficiencies. It does **not** read the simulator's latent `battery_usable_capacity_wh` or `battery_stored_energy_wh`. This is a controlled-demo estimator, not a field-validated battery state-of-health method.
- **Dropout localization:** `localize_data_unavailability()` detects contiguous missing-telemetry intervals from observed missingness and cadence. The controlled 45-minute dropout is localized to its interval while diagnosis still abstains inside the gap.
- **Reasoning:** two additional approved tools expose these capabilities as structured evidence, bringing the post-M6 operational tool set to 13.
- **Dry run:** `python scripts/run_m6_dry_run.py` reruns physical validation, all five frozen-scope scenarios on the unchanged M5 dimensions, and all ten canonical query evidence paths.

The frozen M5 report remains unchanged: it still records the battery capability gap and partial dropout localization that motivated M6. The M6 report is written separately to `reports/m6_dry_run.json` and `reports/m6_dry_run.md`.

Current controlled M6 dry run: all five scenarios PASS on every applicable dimension, all ten canonical query evidence paths PASS, and physical validation PASS. These remain synthetic functional results, not field-accuracy claims.

## Ten canonical demo questions

1. What's the current state of my system?
2. Why did our energy production drop yesterday?
3. How much of our consumption came from solar this month?
4. What's unusual about the inverter's behaviour?
5. The customer says the inverter just failed on its own — what actually happened around that time?
6. How long will my battery last tonight at current usage?
7. How sustainable was our energy usage this month?
8. What's our ROI so far?
9. Do we have enough data to tell what happened on the dropout date?
10. Was the customer definitely responsible for this inverter failure?

The final question is deliberately adversarial: the system may report strong technical evidence for overload while refusing to convert that evidence into proof of responsibility, intent, or warranty liability.

## Evaluation interpretation

M5 is a **controlled functional demonstration**, not the full research evaluation protocol. It does not report an aggregate accuracy percentage or statistical significance. The scenarios were authored by the same project, so they are easier than organically occurring field faults. A correct diagnosis also does not receive implicit credit for bad evidence: the dimensions remain visible separately.

Real/representative Datalodger data, expert assessment, benchmark baselines, and statistical analysis remain future research work.

## Repository layout

```text
intelligent-data-logger-demo/
├── config/installation.yaml
├── data/
│   ├── processed/datalodger.sqlite
│   └── ground_truth.json
├── notebooks/
│   ├── 01_generate_synthetic_data.ipynb
│   ├── 02_explore_and_validate_data.ipynb
│   ├── 03_analytics_library_demo.ipynb
│   ├── 04_reasoning_walkthrough.ipynb
│   └── 05_scenario_scoring.ipynb
├── reports/
│   ├── m5_evaluation.json
│   ├── m5_evaluation.md
│   ├── m6_dry_run.json
│   └── m6_dry_run.md
├── scripts/run_m5_evaluation.py
├── scripts/run_m6_dry_run.py
├── src/
│   ├── analytics/
│   ├── datacontext/
│   ├── evaluation/
│   ├── evidence/
│   ├── generator/
│   ├── interface/
│   ├── reasoning/
│   └── storage/
├── tests/
├── M5_REVIEW_NOTES.md
├── M6_REVIEW_NOTES.md
├── DEMO_EXPERIMENT_BRIEF.md
├── requirements.txt
└── requirements-dev.txt
```

See [`DEMO_EXPERIMENT_BRIEF.md`](DEMO_EXPERIMENT_BRIEF.md) for the full experiment design, limitations, and milestone definitions.
