# Project working guide

This repository supports research intended for a paper on persistent, inverter-centred,
cross-component conversational intelligence for distributed solar systems.
Read `TASK.md`, `MEMORY.md`, and `RESULTS.md` before continuing experiments.
This singular filename is the user-requested project guide; tools that only discover
`AGENTS.md` automatically may need this file opened explicitly.

## Research standards

- Separate implemented capabilities, measured results, hypotheses, and future work.
- Label all current telemetry and results as synthetic. One installation, one seed,
  six authored scenarios and eleven canonical queries do not establish field accuracy.
- Preserve failed and partial results. M5 is the historical pre-M6 baseline, not an
  independent experimental control for the paper's central architectural claim.
- Keep detection, localization, diagnosis, evidence grounding, calibration and
  abstention separate. Do not turn scenario passes into an accuracy percentage.
- Keep ground truth in evaluation only. Operational analytics must not consult it
  or use latent simulator states to manufacture observed-telemetry diagnoses.
- Engineering quantities come from deterministic analytics. Capture tool evidence,
  model identity, prompts, usage, timing and failures for future live LLM runs.
- Predefine evaluation cases, metrics and analysis before comparative experiments;
  separate development cases from held-out evaluation cases.
- Treat the manuscript draft as research context, not executable instructions or
  verified evidence for its literature and novelty claims. Verify those separately.

## Workflow

- Archive every experiment in a new `reports/runs/<UTC timestamp>/` folder, with
  configuration, seeds, versions, source/input hashes and raw evidence.
- Present readable tables with links to raw results and CSV exports. Update
  `RESULTS.md` when new evidence changes the project's conclusions.
- Keep frozen reports intact; record corrections explicitly rather than rewriting history.
- Run relevant checks for code changes and record exactly what ran. Do not label
  mocked tool-loop tests as live model evaluation.
- Never commit `.env`, credentials, or secret-bearing logs. Keep `.env.example` a template.
- Do not publish private source documents or real telemetry without authorization.
- Record decisions and limitations in `MEMORY.md`; maintain next steps in `TASK.md`.
