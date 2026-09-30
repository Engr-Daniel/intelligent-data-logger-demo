# Project memory

## NASEF upgrade — 23 September 2026

The user clarified that this is for a full paper, hardware cannot be built in time,
synthetic experiments must be strengthened, and both offline and online paths are needed.
The user explicitly requested a new branch and said Claude API credit was purchased.
Active work branch: `research/nasef2026-synthetic-benchmark`.

The v1 protocol focuses on historical/cross-component information access, with a shared
diagnostic policy, 8 development and 24 disjoint evaluation installation seeds, twelve
matched episodes, four access conditions and three observation-stress levels. It is an
internally frozen protocol, not an external preregistration. Do not change its thresholds
against the recorded evaluation; create a new version and seeds for later changes.

Evaluation archive: `reports/research/20260923T190318100907Z_evaluation/`.
All 288 clean episodes passed physics checks; 3,456 paired predictions were evaluated.
Clean full-history/cross-component accuracy: 233/240 identifiable cases, 97.1%
(installation-cluster 95% interval 95.4–98.8). Severe corruption: 90.0%.
All comparisons are same-simulator, shared-policy ablations, not independent competitors.
Original demo datasets and frozen reports were preserved.

A bounded live pilot was attempted and stopped on the first HTTP 400 response because
the key is not workspace-scoped. One additional capped diagnostic request confirmed that
error. No generated outputs/usage counters were returned. Optional
`ANTHROPIC_WORKSPACE_ID` header support is now implemented across the API paths.
The user has been asked to configure it; never copy their key into reports or messages.

`paper/METHODS_AND_RESULTS.md` and `paper/ABSTRACT_DRAFT.md` contain evidence-based draft
material, not a finished submission or verified novelty claim. Official conference pages
list 30 September abstract / 5 October full-paper deadlines but have conflicting abstract
wording; see `paper/SUBMISSION_NOTES.md` and confirm the earlier date with organizers.

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

## Dashboard visual polish (2026-09-23)

Grid import now uses deep blue (#1746a2), shared by the chart and legend.
The battery card uses a native responsive progress bar, with the estimated runway
and constant-load assumption on separate lines. Metric spacing and the tablet grid
were adjusted to prevent cramped cards. Headless Edge checks passed at 1440, 1024,
850, 390 and 320 px: no horizontal overflow, bar contained within the card, 13 px
clearance before the runway text, correct chart colour, repeated refreshes and no
JavaScript errors. Desktop and mobile screenshots were visually inspected.
These were local UI checks; no Claude API calls or research experiments were run.

## Publication preparation — 28 September 2026

The user supplied an explorer ZIP and requested GitHub Pages, README screenshots and
completed abstract/full-paper Word files for self-submission today. Confirmed public
byline: Oyewale, D.O. and Meyer-Petgrave, F.; Petgrave.io Technologies Ltd, Nigeria.
Correspondence details are in ignored local configuration and submission documents.
The ZIP's shared README/MEMORY/TASK/server/dashboard copies were not blindly overlaid.
Its six evidence/dimension/outcome/ground-truth objects match the archived original demo.

Live pilot `20260928T072728456454Z_live_development` failed on APIConnectionError before
any generated response/usage. A non-generating authenticated connectivity check succeeded.
A fresh `20260928T072939445717Z_live_development` run completed 24 conversations / 48
requests, estimated USD 0.213009. Intended tool selection 24/24; strict JSON 0/24 because
all replies were Markdown fenced. Primary scores remain immutable. Separate post-hoc
analysis `20260928_live_format_sensitivity` removes one fence and obtains 24/24 label
fidelity, 15/24 valid measurement-name citation sets and 16/24 oracle agreement including
required abstentions. Assistant qualitative prose review is not independent human scoring.

`paper/FULL_PAPER.md` integrates this evidence, six checked primary references and
explicit synthetic/model-policy/coverage limitations. Abstract is 228 words; Word
files are generated under ignored `paper/submission/`. The user will submit personally.
No emails, registration or payment were sent. Full-paper template/page limit and
organizer recipient details still require author confirmation. No acceptance claim.

Public site build uses a strict eight-asset allowlist and manifest; no API credentials
or Python backend are deployed. Pages workflow publishes `.site/` from main. Explorer
includes separate original-demo and comparative-study views plus a telemetry-hash-
verified outage trace. Regression suite: 115 passed in 113.95 seconds. Both offline
archives verified. Browser checks cover all six scenarios, stress selections, primary/
post-hoc distinction, the dashboard and 320–1440 px layouts with no JS/CSP errors.

Publication completed: main and the research branch include the release and the newer
remote README prototype link. GitHub Pages workflow run 36395722747 succeeded for
commit 01e9522. Public URL: https://engr-daniel.github.io/intelligent-data-logger-demo/.
All eight hosted assets matched publication.json hashes. Public browser checks passed
for outage deep link/trace, research navigation, severe stress, strict pilot disclosure
and 320 px layout; .env and backend routes returned 404. Repository website metadata
points to the site. Submission remains the user's responsibility.
Word package integrity/font/spacing/authorship checks passed. Optional Word PDF export
stalled and its task-owned automation process was stopped; no PDF or complete visual
pagination review is claimed. The saved .docx files are the requested deliverables.

## Public offline dashboard upgrade (2026-09-28)

User chose GitHub-only offline demonstration first; hosted Claude backend is deferred.
The /dashboard/ static build reuses the original solar UI with 120 verified synthetic
days and nine precomputed deterministic answers, explicitly labelled as replay.
The public adapter has no keys/model calls; arbitrary follow-ups are unsupported.
Session export carries replay provenance. Browser-tab storage persists through reload;
New conversation resets without native dialogs. Local mode switching resets the
conversation rather than permanently disabling the mode selector after the first turn.

Validation: 11 publication/web-interface tests passed. Edge checked all eight suggested
questions, status, receipts, unsupported questions, export, reset, reload persistence,
date gaps, refresh, snapshot modal, both explorer views and widths 320/390/850/1440.
Local offline/Claude/offline switches were mocked UI checks, with no paid model calls.
README includes an actual dashboard screenshot. Existing research archives are unchanged.

Public deployment verified: GitHub Pages run 36451096702 succeeded for ecd8a45.
The first build caught Git newline normalization; explicit byte-preserving attributes
and re-staging fixed it. All 135 deployed assets match publication hashes. Public Edge
checks passed for the dashboard controls, exported provenance, receipts, saved tab
session, chart gaps, navigation and responsive layouts. A transient network timeout
required retry; no application errors remained. Repository homepage now opens
https://engr-daniel.github.io/intelligent-data-logger-demo/dashboard/.
User ground_truth.json line-ending changes and .vscode settings remain uncommitted.

## Methodology manuscript revision (2026-09-30)

User approved presenting the contribution as a reproducible methodology supported by
implementation and a synthetic worked evaluation, including where/how real data would
be acquired. Abstract and full paper now use that framing. Added a six-stage workflow,
field-source mapping, proposed recruitment/collection/storage/quality procedures and
independent fault-reference/field-evaluation requirements. Field acquisition remains
proposed; no hardware, site partnership or field validation is claimed. Added bounded
SunSpec and NREL acquisition references. Frozen v1 protocol, archived metrics and
strict-versus-post-hoc Claude results are preserved. Revised abstract: 238 words;
title: 15 words. Word package regenerated; earlier Word versions retained locally.

Revision checks passed: matching abstract text in both Markdown sources and Word files;
238-word abstract and 15-word title; result section unchanged except table numbering;
sequential section/table numbers; Word ZIP integrity, corresponding-author presence,
12-point Times New Roman, double-spaced body, four tables and three embedded figures.
Full visual pagination was not checked; author review of Word layout remains required.
No experiments or paid model calls were run for this editorial revision.

Final abstract refinement (2026-09-30): user approved tightening their supplied version. Updated both manuscript abstracts to 263 words, five comma-separated keywords and the existing sentence-case title. Replaced potentially misleading independent-scoring wording with separate scoring against evaluation-only reference labels, including the conclusion. Retained all numerical outcomes and the shared simulator-policy/field-validation limitations.
Validation passed: 263-word abstract matches both Markdown sources and both regenerated Word files; five keywords; unchanged results section; Word package, title, font and figure/table checks. Final visual pagination remains for author review.
