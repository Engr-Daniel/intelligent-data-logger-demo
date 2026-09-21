# Project memory

## User direction

- This is research work intended for a paper. Results must be clear, traceable and
  useful for scientific reporting, not just software pass/fail output.
- On 21 September 2026 the user requested a GitHub update before further live work,
  and explicitly requested `AGENT.md`, `TASK.md` and `MEMORY.md`.
- Repository: https://github.com/Engr-Daniel/intelligent-data-logger-demo

## Research context

The user supplied `Intelligent_Data_Logger_brief_workingdraft.pdf`, a three-page
working manuscript. It proposes persistent installation history, cross-component
reasoning, status-first interaction, installer diagnosis and owner decision support.
Its empirical programme proposes comparisons with single-component/no-history
conditions and manual analysis, using real or representative data and expert judgement.
The PDF was read as context and has not been copied into this public repository.
Its literature and novelty statements have not been independently verified here.

## Recorded evidence

- Source checkout before experiment: `e57ba12af24b28e3db4909bdf20f69e9a337675e`.
- Run: `reports/runs/20260921T055826825005Z/`.
- One synthetic installation; seed 42; 120 days; five-minute cadence; 34,560 rows.
- Synthetic interval: 1 August–28 November 2026, Africa/Lagos. These simulated dates
  extend beyond the execution date and are not field observations.
- Physical validation PASS; all six M6 scenarios and eleven query checks PASS.
- Regression suite: 80 passed in 173.92 seconds, recorded in `tests.xml`.
- M5 retains battery `CAPABILITY_GAP` and dropout-localization `PARTIAL` outcomes.
- Original M5/M6 reports were unchanged; regeneration changed ground-truth line
  endings only. No live Claude requests were made during the offline run.

## Environment and reproducibility

Windows PowerShell; available Python 3.10.0 (README recommends 3.11+).
The virtual-environment launcher failed. Dependencies were installed into
`.venv/Lib/site-packages` and loaded by the working Python through `PYTHONPATH`.
Exact commands and versions are in the archived run README and manifest.
Git works outside the sandbox with the per-command setting
`-c safe.directory=C:/intelligent-data-logger-demo`; no global trust change is needed.
The local `.env` exists; credential validity and live API readiness are unverified.
Never record its contents in project memory or reports.

## Interactive interface

The user requested a polished interface for screen recordings, with current system state
shown first and owner/installer questions afterward. The local custom web interface starts
with `python scripts/serve_dashboard.py` at `http://127.0.0.1:8501`.
Status means the latest complete stored synthetic snapshot, not a live solar installation.
Historical chart selection is independent of the status snapshot and conversation date anchor.
Offline is the default and treats questions independently; Claude mode supports session-scoped
follow-up history and requires explicit mode selection. No live API calls were made to test it.
Session exports contain actual tool receipts, timing, usage and provenance, but are not scored
paper experiments. Browser sessions are memory-only and should be exported before reset or
server shutdown. Public deployment and API budget controls remain future work.
Interface validation: 87 regression tests passed; browser interaction checks covered
date selection, evidence, exports, reset and mobile width. See `reports/interface_validation.md`.

## Interpretation to preserve

Current evidence establishes controlled synthetic functionality, not field accuracy,
statistical significance, model answer quality or superiority over research baselines.
The M5-to-M6 comparison documents implementation changes on development scenarios.
Longitudinal/cross-component benefit remains a hypothesis requiring controlled comparison.
Keep overload evidence distinct from proof of customer responsibility or warranty liability.
