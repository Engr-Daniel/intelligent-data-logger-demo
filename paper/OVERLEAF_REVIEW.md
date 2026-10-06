# Full-paper revision and figure decisions — 5 October 2026

The user reports that the abstract was accepted for oral presentation. They confirmed that the acceptance email supplied no full-paper template or page limit. This record is an editorial response to the supplied advisory review, not a claim of independent scientific validation.

## Adopted

- Clarify the integration problem without claiming an exhaustive gap in all prior work.
- Define the benchmark evidence receipt against `src/research/policy.py`: label, reason, measurement dictionary, available columns/rows, window and thresholds. Assumptions live in protocol/tool definitions, not a separate benchmark receipt field.
- Distinguish solar-specific schemas/rules from reusable access and reporting components; cross-domain transfer remains untested.
- Clarify bundled-channel interpretation, performance interaction and RQ answers.
- State that 24 evaluation installations were fixed in the archived protocol and no formal power-analysis rationale was recorded. Do not invent a retrospective motivation.
- Explain whole-installation bootstrap dependence and preserve the primary/post-hoc split.
- Rename the reporting pilot and compress prospective field acquisition.
- Add two focused application references: Utama et al. (2023), DOI 10.1016/j.solener.2022.11.018, verified through publisher-indexed metadata and institutional records; Sairam et al. (2020), arXiv:2011.09843, verified from the primary author preprint and explicitly labelled as such. Neither becomes a measured baseline.

## Qualified or not adopted

- “Independent evaluation” means separated scoring, not an external evaluator; the text and figures use the latter description.
- The review's broad claims of methodological usefulness/validity are not themselves evidence. No independent replication or installer-usefulness study has occurred.
- The accepted abstract file is preserved; only the full-paper wording is clarified.
- Seven graphics are not required for seven subsections. The architecture incorporates the reusable workflow; the field mapping table carries the prospective acquisition details. Five figures avoid redundant diagrams and excessive page count.
- Cost/latency remain a short, explicitly qualified implementation statement.

## Supplied figure assessment

All eight supplied PNGs and the text in `Useful Figures.docx` were inspected. The DOCX contains broad enterprise/AI illustration headings rather than additional solar experimental evidence.

| Supplied idea | Publication treatment |
|---|---|
| Methodology boundary + end-to-end workflow | Combined into one newly drawn vector diagram; no external-independence implication or invented assumptions field |
| Installation split and 2×2 design | Compact matrix; weather inputs explicit in caption; no arrow implying development data enter evaluation data |
| Clean-data bar chart | Regenerated as correctness/coverage interval plots from `metrics.csv` |
| Corruption chart | Regenerated from all 12 metric rows, with bootstrap intervals and distinct markers/line styles |
| Conversation failure decomposition | Regenerated from both archived summary files; all numbers have denominator 24; strict and post-hoc panels stay separate |
| Physical installation architecture | Not reproduced: equipment artwork and additional health/appliance channels could imply capabilities outside this benchmark; field-source table states proposed scope |
| Dashboard screenshot | Kept as a public demonstration, not a research result figure; linked in availability section |

Figures are PDF vectors with embedded fonts and tightly fitted bounding boxes; PNG previews are 300 dpi. Their provenance records input/output SHA-256 hashes. The archived metrics are not modified.

## Completed verification

- Frozen evaluation verifier: 288 episodes, 3,456 predictions, all hashes and physical checks passed.
- All seven public repository/archive/demo URLs returned HTTP 200 without authentication.
- Final 13-page PDF compiled with Tectonic 0.17.0 (XeTeX engine), BibTeX and standard TeX packages. The initial compiler setup downloaded fonts/packages; this is not required by the uploaded Overleaf project.
- Five figures are vector-only PDF pages with font resources; plot input/output hashes match provenance. No screenshot is used as a quantitative plot.
- Ten citation keys and all cross-references resolve. Four tables and five figures are present. No overfull boxes, missing glyphs, undefined references or LaTeX errors remain in the final log.
- Every PDF page was rendered and visually inspected. A diagram label extending outside its box was shortened; widow/orphan control and consistent condition order were added. Captions, tables and bibliography were checked again after correction.
- An isolated extraction of the 14-file upload ZIP compiled to a 13-page PDF with identical extracted text and no unresolved references or overflow. This establishes package portability under the tested XeTeX build; an actual Overleaf account upload was not performed.
- Accepted abstract and experimental archives were not changed. Scientific interpretation still warrants co-author review; these checks are not peer review or a guarantee of venue-format acceptance.

Deliverables: `paper/submission/NASEF2026_Overleaf.zip` and `paper/submission/NASEF2026_Full_Paper_Overleaf.pdf`. Machine-readable checks: `paper/submission/overleaf_validation.json`.

## Current v3 revision - 6 October 2026

Retained Fitzroy's care-after-installation motivation, Nigerian application setting,
owner's low-output question and measure-record-diagnose-explain-act-verify loop.
Kept the accepted methodology title. Used GSC's primary 803 MW additions figure
instead of combining differently sourced annual/cumulative estimates. Attributed
the 58% training statistic to the reported Lagos survey; did not generalize it to
Nigeria or infer safety prevalence. Omitted an unverified fire-incidence trend.

Kept physical acquisition, action and intervention verification prospective. Reporting
is implemented but failed its strict contract. Added the audited exploratory timing
methods, Table 4, Figure 6 and bounded RQ4/discussion/conclusion. Original benchmark
and pilot numbers remain unchanged. Monthly conditional delay is 16.50 days under the
specified scoring; the paired waiting score, not a subtraction of conditional means,
is used for the schedule contrast. Preserved misses, pre-reference and false alerts.
Added the affiliation/project-development disclosure and prospective field outcomes.

Current layout: 16 pages, seven vector figures, five tables and twelve references.
Care-loop and timing plots were redrawn for readable print sizing. Floats are kept
with their sections. All pages visually reviewed; no clipped figure text, unresolved
citations, missing glyphs or overflowing text boxes detected. An isolated extraction
of the exact 18-file v3 ZIP compiled with exit code 0 and identical extracted PDF text.
The new timing supplement passed ZIP integrity and per-file hash verification.

Current deliverables: NASEF2026_Full_Paper_Overleaf_v3.pdf, NASEF2026_Overleaf_v3.zip,
NASEF2026_Timing_Reproducibility.zip and overleaf_validation_v3.json in paper/submission/.
Prior 5 October files and review details above are historical. Accepted abstract
source unchanged. The 268-word full-paper abstract was revised for the expanded paper.
No experiment reruns, paid calls, external submission or remote publication in this revision.

## v4 front matter and Word/PDF pair (6 October 2026)

User requested Fitzroy's monitoring-gap/trust motivation and additional front matter.
Opening retains these as motivating hypotheses, with no unmeasured national prevalence
or causal trust finding. Exact conference/Sub-theme V appears in the title area.
Added contents, figure/table lists and fourteen abbreviations. Word fields updated by
Microsoft Word; direct PDF export gives a matching 20-page submission pair. Seven
figures, five research tables and one abbreviation table. All source paragraphs found
in DOCX; PDF page bounds passed; final pages and table placement visually reviewed.
The parallel Overleaf v4 has 20 pages, seven vector figures, five research tables and
12 references; no overflow, unresolved citations or missing glyphs. Older v3 review
above is historical. Email draft prepared only; no actual submission.

## Architecture revision v5 - 6 October 2026

Reviewed the original working draft and all six graphics embedded in the supplied Useful Figures.docx. Replaced simplistic opening schematics with original vector installation, layered architecture and experimental workflow diagrams; added an explicit question-to-receipt flowchart. Restored inverter-centred identity, persistent installation memory and status-first interaction in the methodology narrative. Physical gateways, authorized remote access and verified service feedback remain proposed. No new experimental result or field-validation claim was introduced.

Generated v5 Word and matching PDF (21 pages), separate Overleaf PDF (22 pages), and self-contained 24-file Overleaf ZIP. Eight vector PDF figures, four editable SVGs, 300 dpi Word images, five research tables and fourteen abbreviations. Checked all source paragraphs in Word, title-page order, updated contents/lists, figure/input hashes, references, LaTeX diagnostics and PDF boundaries; visually reviewed every page of both layouts. Updated email attachment names. Accepted abstract and frozen experimental archives unchanged; nothing submitted, emailed or pushed.

## Focused submission revision v6 - 6 October 2026

Adopted user-approved editorial synthesis: restored v4 care loop, evidence boundary and compact access matrix; retained v5 question-to-evidence flowchart. Moved broader physical/product architecture into docs/architecture. Removed RQ4 framing and timing numbers from the main abstract/conclusion; retained concise secondary timing methods/results. Preserved the full timing methods, results, table and plot in paper/TIMING_SUPPLEMENT.md and a two-page Word/PDF supplement, with an expanded verified reproducibility ZIP. All primary experimental values and failed pilot results unchanged. No new experiments.

V6 main Word/PDF and Overleaf PDF are 19 pages, seven figures, four research tables, twelve references and fourteen abbreviations. Exporter encoding issue fixed; clean exports rerun. Checked source paragraphs, title-page order, contents/list fields, references, figure hashes, PDF boundaries and all rendered pages. Overleaf ZIP contains 21 files. Email draft and submission links updated. Accepted abstract unchanged; no push or external submission.

## Final submission packaging and publication - 6 October 2026

User selected the focused paper and authorized repository organization and remote updates. Installed stable, unversioned submission filenames; the main Word/PDF are byte-identical to the selected manuscript. Removed the internal revision label from Supplement S1. Preserved old documents in the ignored local submission archive. Added paper/README.md, clean submission notes, an email draft and file-hash manifest; moved detailed editorial notes to SUBMISSION_HISTORY.md. Only approved final deliverables are allowlisted for Git. Credentials, contact configuration, editor settings, original supplied reference documents and prior drafts remain excluded.

Verified 288 benchmark episodes / 3,456 predictions, 54,144 timing decisions / 119,808 schedule outcomes, all checked archive hashes, seven vector manuscript figures and twelve references. Static site builds 135 reviewed assets. Full pytest suite: 120 passed; added testpaths=tests to avoid collecting frozen snapshot copies. Checked final-file hashes, PDF bounds, archive integrity and credential exclusion. Email remains a draft for the author to send; no conference submission performed.
