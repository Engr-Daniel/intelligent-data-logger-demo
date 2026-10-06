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

## Overleaf full-paper preparation (5 October 2026)

User reports oral-presentation acceptance. Acceptance email supplied no full-paper
format or page limit. Prepared provisional A4/11-point Times-style manuscript under
paper/overleaf with main.tex, references.bib and figs/. Preserved accepted abstract
source; full-paper abstract only clarifies correctly diagnosed terminology. Reviewed
all eight proposed PNGs and the DOCX headings. Redrew five vector figures; combined
workflow/architecture and retained the field mapping table instead of duplicating it.
Quantitative figures read archived metrics and strict/post-hoc summaries directly.
Added focused PV-XAI references with bounded verified claims; clarified receipt fields,
bundled access, factorial interpretation, bootstrap unit, sample-size documentation,
RQ answers and prospective field acquisition. No experiment, threshold or archive edits.

Full-paper Markdown and generated LaTeX are aligned. Direct Overleaf edits must be
reconciled before rerunning the generator. Previous Word full paper is now historical;
current full-paper deliverables are the PDF and Overleaf ZIP in paper/submission/.
Portable Tectonic and PyMuPDF were installed only in ignored .venv for local review.

Overleaf validation completed: 13 pages, five vector figures, four tables and ten
references; every page visually inspected; figure-label and widow/orphan issues fixed.
No unresolved references, missing glyphs or overflowing text boxes remain. Isolated ZIP
compile produced identical extracted PDF text. All seven cited public resource links
returned 200. Frozen evaluation verifier passed. PDF/ZIP and validation JSON are in
ignored paper/submission/. No actual Overleaf upload or conference submission occurred.
Accepted abstract and previous Word documents remain unchanged. Source edits are local.

## Exploratory detection-delay extension (6 October 2026)

User authorized implementing and running the timing experiment after the supplied
Fitzroy v2 ZIP proved to contain manuscript/figure assets but no analysis script or
raw timing outputs. Specified docs/DETECTION_DELAY_PROTOCOL.md before this run,
explicitly after seeing proposed results; no claim of preregistration or independence.
Implemented analyze_detection_delay.py, separate verify_detection_delay.py,
summarize_detection_delay.py, five boundary tests and a usage guide.

Archive: reports/research/20261006T022136185304Z_detection_delay; separate interpretation folder contains vector PDF,
300-dpi PNG, readable report and validation.json. 54,144 daily decisions, 119,808
phase/rule outcomes, 96 physical trajectories. All 288 fingerprints and 1,152 final
labels match frozen benchmark. Original source/config unchanged. All receipts and
phase outcomes independently audited; 24 relevant tests passed; figure inspected.

20/24 declines crossed the chosen reference. Clean full-cross daily: 19/20 detected,
4.79-day conditional mean; monthly: phase-average14.23/20, 16.50-day pooled conditional
mean (not the draft's 15.9). Paired finite-horizon waiting difference11.73 days,
95% cluster interval9.88?13.35. Severe daily three-positive rule reduces any-control
false-alert installations13/24 to4/24, post-reference detections19/20 to18/20.
Pre-reference alerts are separate; physical loss can exist before the5% reference.
Daily includes periodic checks by construction, so results quantify schedule effects,
not independent diagnostic superiority. Three monthly positives infeasible in window.
No paid calls, original archive changes, paper/abstract edits, commits or push.

## Full-paper v3 integration - 6 October 2026

User requested paper revision preserving Fitzroy's clearer motivation and Nigerian
story. Retained aftercare/trust motivation, owner's low-output question and proposed
measure-record-diagnose-explain-act-verify loop with accurate implementation boundary.
Verified GSC primary 803 MW addition figure; bounded the Lagos training statistic as
secondary reporting. No unsupported fire trend or national monitoring estimate.
Accepted methodology title and ABSTRACT_DRAFT.md remain unchanged. Revised full-paper
abstract (268 words), timing methods/results/RQ4, discussion, field plan, disclosure
and data availability. Seven vector figures, five tables, twelve citations, 16 pages.

Versioned v3 PDF and Overleaf ZIP plus timing reproducibility supplement are in ignored
paper/submission. Exact 18-file upload ZIP compiled independently, matching PDF text;
no missing glyphs, overflow or unresolved references. All pages visually reviewed.
The supplement has 32 source/evidence files plus README and hash manifest. Source
updates remain local; no push, actual Overleaf upload, submission or paid model call.

## Full-paper v4 and two-format submission (6 October 2026)

User requested stronger use of Fitzroy's motivation, exact conference/Sub-theme V
heading, contents, figure/table lists, abbreviations and an email draft. Revised
full-paper opening with monitoring/trust hypotheses distinguished from measured
findings. Added shared front_matter.json and front matter to Word and LaTeX.
Generated new v4 Word and directly exported matching PDF using hidden Word automation;
three contents/list fields updated, 20 pages, seven figures, five research tables,
fourteen abbreviations. Tables kept together; every source paragraph verified in DOCX,
PDF bounds checked and pages visually inspected. Accepted abstract unchanged.
Email draft saved in ignored paper/submission; nothing sent. Earlier open unversioned
Word file is historical. New builder reads private local contact config. Overleaf v4
also updated, with separate layout/bibliography ordering; source changes remain local.

Title-page correction: conference and Sub-theme V now follow the corresponding-author details, before the abstract. Regenerated v4 Word, matching PDF and Overleaf package; both PDFs remain 20 pages.

## Architecture revision v5 - 6 October 2026

Reviewed the original working draft and all six graphics embedded in the supplied Useful Figures.docx. Replaced simplistic opening schematics with original vector installation, layered architecture and experimental workflow diagrams; added an explicit question-to-receipt flowchart. Restored inverter-centred identity, persistent installation memory and status-first interaction in the methodology narrative. Physical gateways, authorized remote access and verified service feedback remain proposed. No new experimental result or field-validation claim was introduced.

Generated v5 Word and matching PDF (21 pages), separate Overleaf PDF (22 pages), and self-contained 24-file Overleaf ZIP. Eight vector PDF figures, four editable SVGs, 300 dpi Word images, five research tables and fourteen abbreviations. Checked all source paragraphs in Word, title-page order, updated contents/lists, figure/input hashes, references, LaTeX diagnostics and PDF boundaries; visually reviewed every page of both layouts. Updated email attachment names. Accepted abstract and frozen experimental archives unchanged; nothing submitted, emailed or pushed.

## Focused submission revision v6 - 6 October 2026

Adopted user-approved editorial synthesis: restored v4 care loop, evidence boundary and compact access matrix; retained v5 question-to-evidence flowchart. Moved broader physical/product architecture into docs/architecture. Removed RQ4 framing and timing numbers from the main abstract/conclusion; retained concise secondary timing methods/results. Preserved the full timing methods, results, table and plot in paper/TIMING_SUPPLEMENT.md and a two-page Word/PDF supplement, with an expanded verified reproducibility ZIP. All primary experimental values and failed pilot results unchanged. No new experiments.

V6 main Word/PDF and Overleaf PDF are 19 pages, seven figures, four research tables, twelve references and fourteen abbreviations. Exporter encoding issue fixed; clean exports rerun. Checked source paragraphs, title-page order, contents/list fields, references, figure hashes, PDF boundaries and all rendered pages. Overleaf ZIP contains 21 files. Email draft and submission links updated. Accepted abstract unchanged; no push or external submission.

## Final submission packaging and publication - 6 October 2026

User selected the focused paper and authorized repository organization and remote updates. Installed stable, unversioned submission filenames; the main Word/PDF are byte-identical to the selected manuscript. Removed the internal revision label from Supplement S1. Preserved old documents in the ignored local submission archive. Added paper/README.md, clean submission notes, an email draft and file-hash manifest; moved detailed editorial notes to SUBMISSION_HISTORY.md. Only approved final deliverables are allowlisted for Git. Credentials, contact configuration, editor settings, original supplied reference documents and prior drafts remain excluded.

Verified 288 benchmark episodes / 3,456 predictions, 54,144 timing decisions / 119,808 schedule outcomes, all checked archive hashes, seven vector manuscript figures and twelve references. Static site builds 135 reviewed assets. Full pytest suite: 120 passed; added testpaths=tests to avoid collecting frozen snapshot copies. Checked final-file hashes, PDF bounds, archive integrity and credential exclusion. Email remains a draft for the author to send; no conference submission performed.
