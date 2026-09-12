# Intelligent Data Logger — Demo Experiment Brief

**Project:** Intelligent Data Logger (Datalodger Intelligence)
**Organisation:** Petgrave.io Technologies Ltd.
**Authors:** Daniel Oyewale (daniel.oyewale@petgrave.io), Fitzroy Meyer-Petgrave (fitzroy@petgrave.io)
**Document type:** Demo / experiment brief (engineering companion to the research proposal)
**Status:** Draft — for internal review and GitHub publication

---

## 1. Purpose of This Document

The research proposal and paper brief describe the *target* architecture for the Intelligent Data Logger: a persistent, inverter-centred, cross-component intelligence layer that reasons over an installation's full operational history. That architecture assumes a live Datalodger deployment with months or years of real telemetry.

We do not yet have that. This document specifies a **standalone demo** that proves the *reasoning and orchestration concept* end-to-end — from raw device telemetry to an evidence-grounded natural-language answer — using **synthetic data engineered to be realistic enough to exercise every stage of the pipeline**, including faults, anomalies, and a specific "customer overload, undisclosed to installer" scenario.

The demo is explicitly **illustrative, not evaluative**. It is not the rigorous benchmark-and-expert-panel evaluation described in Section VI of the research proposal. Its job is to let anyone — a co-founder, an investor, an installer, a reviewer — open a notebook, ask a question in plain English, and watch the system pull real numbers from synthetic telemetry, run the right calculation, and answer with receipts.

---

## 2. What the Demo Must Prove

| # | Claim from the proposal | How the demo shows it |
|---|---|---|
| 1 | The inverter can serve as the integration anchor for multi-device telemetry | Synthetic inverter, battery, load, meter, and weather streams are joined on a single installation timeline |
| 2 | Natural-language questions can be resolved by *orchestrating* analytics, not by free-form LLM guessing | The reasoning layer selects and calls specific Python analytics functions, never sees raw time series directly |
| 3 | Answers are evidence-grounded and traceable | Every answer cites the specific function output(s) and data window used to produce it |
| 4 | The system can do cross-component root-cause diagnosis | A scripted "battery fault caused by undisclosed customer overload" scenario is diagnosed correctly from load + inverter + battery signals, without a self-report |
| 5 | The system can support owner-facing decision questions | ROI, carbon savings, battery runway, and self-consumption queries are answered on demand |
| 6 | The interface can be status-first, then conversational | A minimal "open → summary card → ask a follow-up" flow is demonstrated, even in a notebook/CLI form |

---

## 3. Scope and Non-Goals

**In scope for this demo:**
- One synthetic installation, ~90–180 days of 5-minute-resolution telemetry
- 4–6 injected fault/anomaly scenarios with known ground truth
- A working analytics function library (forecasting, anomaly detection, energy balance, performance ratio, root-cause heuristics, sustainability metrics)
- An LLM reasoning layer (Claude, via the Anthropic API) using tool-use/function-calling to orchestrate those functions
- A notebook-driven walkthrough answering the four example questions from the original brief, plus the installer overload scenario
- A minimal "status card" view alongside the conversational interface

**Explicitly out of scope for this demo:**
- Real device connectivity, IP-based pairing, or a live gateway
- A production mobile app (a thin CLI/notebook chat loop stands in for it)
- Multi-installation / fleet-level analysis
- The full statistical evaluation protocol (query benchmark, expert panel, significance testing) — that comes later, once the architecture is validated conceptually and, ideally, against real Datalodger data
- Model fine-tuning; the demo uses prompting and tool-use only

---

## 4. Why Synthetic Data, and How We Keep It Honest

Without a live logger, every number in the demo is generated, not measured. To keep the demo credible rather than a toy:

- **Physically grounded generation model.** PV output is driven by a diurnal irradiance curve (clear-sky model modulated by a stochastic cloud-cover factor), panel derating by temperature, and a rated system size — not arbitrary noise.
- **Energy-conserving battery model.** Battery state evolves from explicit energy balance rather than independently generated SOC values. The model enforces nominal/usable capacity, SOC bounds, maximum charge/discharge power, charge/discharge efficiency, and configurable degradation. At each interval, stored energy is updated from charge and discharge power so that battery runway, degradation, and overload analyses remain internally consistent.
- **Explicit assumptions/configuration.** Financial and sustainability outputs are calculated from versioned installation assumptions (CAPEX, tariffs, export compensation, maintenance cost, emissions factors, and baseline/counterfactual), not inferred by the LLM.
- **Behaviourally grounded load model.** Household load is built from a base load plus appliance-shaped bumps (morning/evening peaks, weekend deviation, occasional high-draw events) rather than a flat random walk.
- **Explicit fault injection with ground truth.** Every anomaly is inserted programmatically with a known timestamp, cause, and affected device, stored in a separate `ground_truth.json`/`events.csv`. This is what lets us check whether the reasoning layer's diagnosis is *actually correct*, not just fluent.
- **Labelled as synthetic everywhere.** The README, the notebook headers, and every plot title state that data is synthetic. No output from this demo will be presented as real-world validation.

---

## 5. Synthetic Data Specification

### 5.1 Installation profile
A single fictitious residential installation:
- 6.6 kWp PV array, single string inverter (rated 5 kW), 10 kWh nominal LFP battery, grid-tied with net metering
- Battery parameters include usable-capacity fraction, minimum/maximum SOC, maximum charge/discharge power, charge/discharge efficiency, initial usable capacity, and a configurable degradation trajectory
- Location parameterised with a latitude/timezone for a plausible irradiance curve (no real address)
- A separate installation configuration defines CAPEX, electricity import tariff, export tariff/net-metering assumption, maintenance costs, currency, grid emissions factor, and the baseline used for avoided-cost/carbon calculations

### 5.2 Data streams (5-minute resolution unless noted)

| Stream | Fields | Notes |
|---|---|---|
| PV / Inverter | `dc_power`, `pv_available_ac_power_w`, `pv_ac_power_w`, `pv_curtailed_w`, `voltage`, `current`, `temperature_c`, `efficiency`, `operating_state`, `alarm_code` | Available versus delivered AC power is explicit so islanded PV curtailment is physically accounted for |
| Battery | `soc_pct`, `stored_energy_wh`, `usable_capacity_wh`, `charge_rate_w`, `discharge_rate_w`, `temperature_c`, `cycle_count` | Energy-conserving model coupled to PV surplus/deficit and load, with SOC/power limits and efficiency losses |
| Load / Smart meter | `load_requested_power_w`, `load_power_w`, `unmet_load_w`, `grid_import_w`, `grid_export_w` | Requested demand, actually served load, and any islanded shortfall are explicit; behavioural model includes the injected overload event |
| Weather | `irradiance_wm2`, `ambient_temp_c`, `cloud_cover_pct` | Synthetic clear-sky + stochastic cloud model |
| Events (ground truth only, not seen by the model) | `timestamp`, `event_type`, `affected_device`, `true_cause`, `description` | Used only for scoring, never fed to the reasoning layer |

### 5.3 Injected scenarios (six required)

1. **Cloudy-day generation drop** — a genuine weather-caused production dip, to test the system doesn't over-attribute drops to faults.
2. **Customer overload → inverter derate/fault** — load spikes past a safe threshold for a sustained period, inverter logs a derate/alarm shortly after, battery shows unusual discharge; customer "self-report" is deliberately withheld from the system. This is the key installer scenario.
3. **Gradual efficiency decline** — a slow multi-week drift in performance ratio (simulating soiling/degradation), to test trend-level anomaly detection vs. point anomalies.
4. **Battery degradation signature** — usable capacity drifts down over the simulated period, cycling pattern shifts.
5. **Sensor dropout** — a short gap of missing/garbled readings, to test that the system flags data-insufficiency instead of fabricating an answer.
6. **Grid outage / islanding event** — the utility grid becomes unavailable while the installation is operating with a configured battery backup reserve. Grid exchange falls to zero and the inverter enters an islanded state. PV and battery serve local demand subject to their physical power/energy limits; if local supply is insufficient, the shortfall is recorded explicitly as `unmet_load_w`, and if islanded PV surplus cannot be absorbed, it is recorded as `pv_curtailed_w`. Normal grid-connected operation resumes after restoration. This tests grid interaction, cross-component temporal reasoning, load-shedding awareness, and physically complete islanded bookkeeping.

All **six scenarios are required** for final demo acceptance. Each must be logged separately in `ground_truth.json`, simulated through physically consistent telemetry rather than post-hoc label editing, and evaluated with the same ground-truth separation, evidence-grounding, calibration, and physical-validation rules.

### 5.4 Generation approach
Python, `numpy`/`pandas`, seeded for reproducibility (`--seed` flag). No external data purchase is required; an optional stretch goal is to swap the synthetic weather model for a real historical weather API (e.g., Open-Meteo) to add realism without needing real PV telemetry.

The generator must preserve basic physical consistency. In particular, battery stored energy is updated from interval charge/discharge energy with efficiency losses and bounded by usable capacity and SOC limits. PV, served load, battery, grid import, and grid export must satisfy an interval-level power-balance check within a documented numerical tolerance. Requested demand must equal served load plus explicit unmet load, and available PV must equal delivered PV plus explicit curtailment. These invariants must remain valid even when islanded demand exceeds battery power/energy capacity or islanded PV surplus exceeds local absorption capacity.

### 5.5 Financial and sustainability assumptions

Financial and carbon outputs are **derived estimates**, not directly measured telemetry. The demo therefore stores their assumptions separately (for example in `config/installation.yaml`) and returns those assumptions alongside every result.

Minimum financial parameters:
- Initial installed-system CAPEX
- Electricity import tariff and effective date
- Export tariff/net-metering treatment
- Estimated or configured maintenance expenditure
- Currency
- Optional avoided-generator cost, only if a generator baseline is explicitly configured

The demo should distinguish **avoided energy cost**, **net savings**, **simple ROI**, and **simple payback period**. It should not label simple payback as ROI.

Minimum sustainability parameters:
- Grid emissions factor (with source/year recorded in configuration when real factors are later used)
- Defined counterfactual/baseline
- Renewable energy consumed on-site
- Exported renewable energy, reported separately

`carbon_avoided` is therefore presented as an **estimated avoided-emissions metric under the configured baseline**, not as a directly measured quantity.

---

## 6. Demo Architecture (Scaled-Down Pipeline)

```
Synthetic Devices  →  Local Store  →  Data Context  →  Analytics Library  →  Evidence Object  →  LLM Orchestrator  →  Answer
(generator script)    (SQLite/Parquet)   (schema/config)   (deterministic tools)    (structured facts)   (tool use)          (text + receipts)
```

This mirrors the seven-stage architecture from the proposal, compressed for a single-machine demo:

- **Datalodger stand-in:** a local SQLite database or Parquet files under `data/processed/`, populated once by the generator script. This plays the role of "persistent storage" without needing a real logger.
- **Data context:** a small YAML/JSON schema describing device fields, units, and normal operating ranges — the minimum needed for the analytics functions and the LLM to interpret values correctly.
- **Analytics library (`src/analytics/`):** plain Python functions, independently testable, e.g.:
  - `forecast_generation(window)`
  - `detect_anomalies(series, method="zscore"|"iqr")`
  - `energy_balance(window)` → self-consumption / self-sufficiency / grid dependency
  - `performance_ratio(window)`
  - `root_cause_candidates(fault_window)` → cross-references load/battery/inverter/weather around an event
  - `sustainability_metrics(window)` → renewable fraction, on-site solar use, estimated avoided emissions under configured assumptions
  - `financial_metrics(window)` → avoided cost, net savings, simple ROI, simple payback
  - `battery_runway(current_load)` → deterministic estimate with assumptions and uncertainty bounds where appropriate
- **Evidence layer (`src/evidence/`):** analytics tools return or are normalized into a structured evidence object before any natural-language response is produced. A typical object contains the user question/intent, finding, measurements, candidate cause, confidence, alternative explanations checked, data-quality flags, assumptions, and exact data window.
- **Reasoning layer (`src/reasoning/`):** a Claude tool-use loop where approved analytics functions are exposed as callable tools with JSON schemas. The model is instructed never to calculate engineering/financial quantities itself, never to answer from raw time series, and to distinguish observed evidence from inferred cause. It must cite the evidence object/tool outputs supporting each factual claim and abstain when evidence is insufficient.
- **Interface:** a simple CLI/notebook chat loop for the demo; a short "status card" cell that prints/plots current generation, consumption, battery %, runway estimate, and active alerts before the conversational loop starts, echoing the intended "open app → see status → ask more" UX.

---

## 7. Demo Query Set

These are asked interactively in the walkthrough notebook, each checked against `ground_truth.json` where applicable:

1. "What's the current state of my system?" *(status-card style, no LLM needed)*
2. "Why did our energy production drop yesterday?" *(should distinguish weather vs. fault, scenario 1)*
3. "How much of our consumption came from solar this month?" *(energy balance)*
4. "What's unusual about the inverter's behaviour?" *(should surface scenario 2 and/or 3)*
5. **Installer framing:** "The customer says the inverter just failed on its own — what actually happened around that time?" *(should surface the overload event from load data, independent of customer's account — scenario 2)*
6. "How long will my battery last tonight at current usage?" *(battery runway)*
7. "How sustainable was our energy usage this month?" *(carbon/renewable fraction)*
8. "What's our ROI so far?" *(financial decision support)*
9. "Do we have enough data to tell what happened on [dropout date]?" *(should correctly decline/caveat, scenario 5)*
10. **Adversarial/certainty check:** "Was the customer definitely responsible for this inverter failure?" *(should separate evidence from inference, report the overload as the strongest supported candidate when appropriate, consider alternatives, and avoid claiming certainty or blame that the telemetry cannot establish)*
11. **Grid interaction:** "What happened when the grid went down on 2026-10-10?" *(should detect and localize scenario 6, identify islanded backup operation, explain the grid/battery/load transition from approved evidence, and avoid treating zero grid import alone as proof of an outage)*

---

## 8. Repository Structure (GitHub)

```
intelligent-data-logger-demo/
├── README.md                     # setup, quickstart, disclaimer that data is synthetic
├── requirements.txt
├── .env.example                  # ANTHROPIC_API_KEY placeholder
├── data/
│   ├── raw/                      # generator output (gitignored if large)
│   ├── processed/                # SQLite/Parquet "Datalodger" store
│   └── ground_truth.json         # injected event log, used only for scoring
├── src/
│   ├── generator/                # synthetic data generation
│   │   ├── pv_model.py
│   │   ├── load_model.py
│   │   ├── battery_model.py
│   │   ├── weather_model.py
│   │   └── fault_injection.py
│   ├── datacontext/
│   │   └── schema.yaml
│   ├── config/
│   │   └── installation.yaml       # technical, financial, tariff, emissions assumptions
│   ├── analytics/
│   │   ├── forecasting.py
│   │   ├── anomaly_detection.py
│   │   ├── energy_balance.py
│   │   ├── performance.py
│   │   ├── root_cause.py
│   │   ├── grid_events.py
│   │   └── sustainability.py
│   ├── reasoning/
│   │   ├── tools.py               # tool/function schemas for the LLM
│   │   └── agent.py               # Claude tool-use orchestration loop
│   └── interface/
│       └── status_card.py
├── notebooks/
│   ├── 01_generate_synthetic_data.ipynb
│   ├── 02_explore_and_validate_data.ipynb
│   ├── 03_analytics_library_demo.ipynb
│   ├── 04_reasoning_walkthrough.ipynb   # the main "ask questions" demo
│   └── 05_scenario_scoring.ipynb        # compares answers to ground_truth.json
├── tests/
│   └── test_analytics.py
└── LICENSE
```

Notebooks are designed to run in **VSCode** (with the Jupyter extension) for development, and to open cleanly in **Google Colab** for sharing — data generation is self-contained (no external services required beyond an optional weather API), and the reasoning notebook only needs an `ANTHROPIC_API_KEY` supplied via Colab secrets or a local `.env`.

---

## 9. Environment and Tooling

- **Python** 3.11+
- **Core:** `pandas`, `numpy`, `pyarrow` (or `sqlite3` stdlib)
- **Plotting:** `matplotlib` (kept simple/static for Colab compatibility)
- **LLM:** `anthropic` Python SDK, Claude Sonnet (tool-use)
- **Dev:** `python-dotenv`, `pytest`, `ruff`/`black` for formatting
- **Optional:** `requests` for the Open-Meteo stretch goal

`requirements.txt` will pin versions; `README.md` will include a "Run in Colab" badge alongside VSCode setup instructions (venv + `pip install -r requirements.txt` + `.env`).

---

## 10. Success Criteria for This Demo

The demo is considered successful if, running end-to-end on a fresh clone:

1. The generator produces a reproducible synthetic dataset containing **all six required scenarios (Section 5.3)**, with every injected scenario logged in `ground_truth.json`.
2. Every analytics function runs independently and returns sane values against the synthetic data (sanity-checked in notebook 03).
3. The reasoning layer answers all eleven demo queries (Section 7) using only approved tool/evidence outputs, with every factual claim traceable to a specific tool call and data window.
4. Scenario scoring records separate checks for **detection** (event found), **localization** (correct time window), **diagnosis** (injected cause identified where supported), **evidence grounding** (correct measurements cited), **calibration** (certainty matches evidence strength), and **abstention** (unsupported conclusions refused).
5. For scenarios with causal ground truth (2, 3, 4, 6), the leading diagnosis matches the injected cause and the supporting evidence comes from the appropriate cross-component signals. A correct diagnosis must not receive full credit if its evidence is wrong or fabricated.
6. For scenario 5 (sensor dropout), the system explicitly flags insufficient data rather than fabricating an explanation.
7. For the adversarial certainty query, the system distinguishes correlation/temporal evidence from proof of customer responsibility and does not make unsupported blame or warranty claims.
8. Battery, PV, load, and grid telemetry passes documented physical sanity checks, including interval power balance, requested-demand = served-load + unmet-load accounting, and available-PV = delivered-PV + curtailed-PV accounting.
9. Financial and sustainability answers expose the configured assumptions used in their calculation and distinguish measured telemetry from derived estimates.
10. A reviewer with no prior context can clone the repo, follow the README, and reproduce the walkthrough in under 15 minutes.

This is a **functional demonstration**, not a statistical validation — no claims of accuracy percentages or statistical significance should be drawn from it. That evaluation remains the job of the full research programme (Section VI–VIII of the research proposal) once real Datalodger data is available.

---

## 11. Explicit Limitations

- All numbers are synthetic; nothing here demonstrates real-world model accuracy.
- Fault signatures are authored by us, so the diagnosis task is easier than it would be on organically occurring real faults with messier, overlapping causes.
- No multi-installation, multi-tenant, or fleet-level behaviour is demonstrated.
- No real device connectivity, authentication, or mobile app is built — the CLI/notebook interface is a stand-in.
- The reasoning layer's correctness is checked against our own injected ground truth, not independent expert judgement.
- A causal chain encoded by the generator is intentionally easier to diagnose than ambiguous real-world failures; the demo must not imply legal, warranty, or customer-blame conclusions from synthetic correlations.
- Battery-health, remaining-runtime, ROI/payback, and carbon outputs depend on configured model assumptions. They demonstrate the analytics pathway, not field-calibrated accuracy.
- No historical KruzzFM dataset or other prior operational dataset is available to this project; the demo therefore does not rely on it as an intermediate validation source.

These limitations should be stated up front in the GitHub README so the demo is never mistaken for validation evidence.

---

## 12. Suggested Build Timeline

| Milestone | Deliverable | Est. effort |
|---|---|---|
| M0 | Thin vertical slice: overload scenario only, end-to-end from generated telemetry → analytics → evidence object → conversational answer | 2–3 days |
| M1 | Full synthetic data generator (PV, load, physically consistent battery, weather, remaining fault injections) + `ground_truth.json` | 3–4 days |
| M2 | Local storage layer + data-context/config schemas + physical sanity checks | 1–2 days |
| M3 | Analytics function library + unit tests, including financial/sustainability assumptions | 3–4 days |
| M4 | Evidence layer + reasoning/tool-use loop + status card | 3–4 days |
| M5 | Notebooks (walkthrough + multidimensional scenario scoring) + README + Colab compatibility pass | 2–3 days |
| M6 | Internal dry run, fix diagnosis/evidence/calibration mismatches, polish | 2 days |

Total: roughly 3 weeks of focused build time for one engineer, depending on how much physical realism is included. The overload vertical slice is intentionally built first so architecture mistakes are discovered before all scenarios are implemented.

---

## 13. Relationship to the Research Proposal

This demo is a **feasibility and communication artefact**, sitting between Phase 1 (literature review) and Phase 3 (prototype implementation) of the research methodology described in the proposal. A successful demo:

- Validates the orchestration pattern (tool-constrained LLM reasoning over verified analytics outputs) before committing to full Datalodger integration.
- Produces a reusable analytics function library that can later be pointed at real telemetry with minimal rework.
- Gives installers, investors, and reviewers something concrete to react to ahead of real-data availability.

It does **not** replace the evaluation plan in the proposal (query benchmark, baselines, expert panel, statistical analysis) — that remains necessary once real or representative Datalodger data is accessible.


---

## 14. Implementation Principles for the Demo

1. **Deterministic calculations are the source of truth.** Engineering, financial, and sustainability quantities are computed by tested functions. The LLM explains and orchestrates; it does not invent or independently calculate them.
2. **Raw telemetry is not the conversational interface.** The LLM receives compact tool outputs/evidence objects rather than unrestricted raw time series.
3. **Evidence, inference, and uncertainty are separate.** Answers must clearly distinguish measured/generated observations (e.g., peak load and alarm timestamp), analytical inferences (e.g., overload is the strongest candidate cause), and what cannot be established.
4. **Data quality is first-class.** Missing, stale, contradictory, or insufficient telemetry is surfaced explicitly and can force abstention.
5. **Assumptions travel with derived metrics.** Battery runway, financial savings, ROI/payback, and carbon estimates return the assumptions that materially determine the result.
6. **The analytics library is interface-independent.** The same functions should be callable from notebooks, a future API/dashboard, automated alerts, or an LLM interface without rewriting the underlying calculations.
7. **Read-only by default.** This demo is an observational and analytical system. It does not issue control commands to the inverter, battery, or loads.

### 14.1 Recommended evidence-object contract

A diagnosis-oriented evidence object should support fields equivalent to:

```json
{
  "question": "Why did the inverter shut down?",
  "finding": "Sustained overload preceded the shutdown.",
  "data_window": {"start": "...", "end": "..."},
  "measurements": [
    {"name": "peak_load_w", "value": 5840, "unit": "W"},
    {"name": "inverter_rating_w", "value": 5000, "unit": "W"},
    {"name": "duration_above_threshold_min", "value": 8, "unit": "min"}
  ],
  "candidate_cause": "overload",
  "confidence": "high",
  "alternatives_checked": [
    {"cause": "grid_outage", "supported": false},
    {"cause": "weather_generation_drop", "supported": false}
  ],
  "data_quality": {"sufficient": true, "warnings": []},
  "assumptions": [],
  "supporting_tools": ["root_cause_candidates"]
}
```

The exact implementation may differ, but the contract should remain structured and machine-testable.

---

## 15. Build Order

The first implementation target should be a **thin vertical slice of the overload/fault scenario**, not the full required scenario set at once:

1. Generate a short physically consistent telemetry window containing normal operation and one overload event.
2. Store it and validate energy balance/data quality.
3. Implement the minimum root-cause analytics needed to identify the overload sequence.
4. Produce a structured evidence object.
5. Ask the installer-framed question through the LLM tool-use loop.
6. Verify that the answer cites the correct measurements, uses calibrated language, and does not overclaim customer responsibility.
7. Only then expand the generator and analytics library to the remaining scenarios.

This order tests the defining product idea — cross-component, evidence-grounded conversational diagnosis — as early as possible while keeping failure modes easy to isolate.
