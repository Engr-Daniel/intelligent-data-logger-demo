# Experiment explorer

The local interface has two linked views. The [operational dashboard](../src/interface/static/index.html)
shows the latest complete stored **synthetic** snapshot, its history and an interactive
investigation. The [experiment explorer](../src/interface/static/explorer/index.html)
explains what the original M1–M6 evaluation recorded. Its six scenario details include
the injected condition, relevant telemetry, separate ground truth, diagnostic evidence,
expected reasoning and the frozen M5 versus M6 result.

Run `python scripts/serve_dashboard.py` from the repository root. Open
`http://127.0.0.1:8501/` for the dashboard or `http://127.0.0.1:8501/explorer/`
for the explorer. The latter loads without regenerating telemetry. Generate the
demo data before using the dashboard's live status and investigation APIs.

## Files and evidence boundary

| File | Purpose |
|---|---|
| `src/interface/static/explorer/index.html` | Layout, scenario rail, timeline and M1–M6 steps |
| `src/interface/static/explorer/styles.css` | Explorer presentation and responsive layout |
| `src/interface/static/explorer/app.js` | Scenario and timeline selection, evidence panels |
| `src/interface/static/explorer/data/experiment.json` | Static snapshot of the archived demo run |
| `scripts/serve_dashboard.py` | Serves both views and their fixed local assets |

The JSON snapshot identifies run `20260921T055826825005Z` and copies the six
M6 scenario evidence objects, rubric dimensions and outcomes from
`reports/runs/20260921T055826825005Z/m6_dry_run.json`. The frozen M5 comparisons
come from that run's `m5_evaluation.json`; ground truth is from `data/ground_truth.json`.
The explorer's short injection descriptions, selected metrics and expected-reasoning
steps are explanatory presentation, not additional model output. Ground truth is
visibly labeled as an evaluation oracle and is not passed to operational analytics.

This is one authored, single-seed feasibility demo, not the separate 24-installation
NASEF information-access benchmark in `reports/research/`. Six scenario passes are
functional checks, not an accuracy estimate. The explorer does not execute Python,
read a live device, or run a live Claude evaluation. A new `scripts/run_experiment.py`
execution creates a new timestamped report; this snapshot remains tied to its named
archived run until explicitly rebuilt and verified against the new archive. Do not
silently replace the M5 baseline or blend these results with the later benchmark.

## Publication upgrade — 28 September 2026

The supplied ZIP was integrated selectively; its copies of README, MEMORY, TASK and
the dashboard were not used to overwrite newer work. All six evidence/dimension/
outcome/ground-truth objects were checked against the original archived data.
The local server uses a fixed asset allowlist and its original strict CSP. Inline
style attributes were replaced by SVG geometry or CSS classes.

A separate `research.html` page now reads archive-derived metrics, supports three
observation-stress selections, shows primary and post-hoc live results separately,
and links failures and raw artifacts. The original outage scenario includes actual
five-minute samples whose input-file SHA-256 matches the original run manifest.
All bars show scales and units. [Publication guide](PUBLICATION.md).
