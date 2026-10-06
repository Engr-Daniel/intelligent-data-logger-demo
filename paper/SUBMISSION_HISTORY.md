# Current submission files - 6 October 2026 (v6)

Use this matching manuscript pair:

- [Word manuscript](submission/NASEF2026_Full_Paper_Oyewale_Meyer-Petgrave_v6.docx)
- [Matching PDF](submission/NASEF2026_Full_Paper_Oyewale_Meyer-Petgrave_v6.pdf)
- [Supplement S1 PDF](submission/NASEF2026_Timing_Supplement_v6.pdf)
- [Supplement S1 Word](submission/NASEF2026_Timing_Supplement_v6.docx)
- [Email draft](submission/NASEF2026_Full_Paper_Submission_Email.md)
- [Overleaf project](submission/NASEF2026_Overleaf_v6.zip)
- [Timing reproducibility files](submission/NASEF2026_Timing_Reproducibility.zip)

The main paper is 19 pages, including the requested contents, lists and abbreviations;
it contains seven figures and four research tables. Supplement S1 is two pages.
The separate Overleaf PDF is also 19 pages, with its own layout and bibliography order.
Use the matching Word-exported PDF when sending both main-paper formats.

The v6 revision restores v4's methodological focus and care-loop/evidence-boundary
figures, retains v5's question-to-evidence flowchart, and removes unevaluated product
architecture from the manuscript. That material remains in docs/architecture.
Timing is a brief secondary post-hoc analysis, not a fourth primary research question;
its full methods, table, plot and limitations are preserved in Supplement S1.
Fitzroy's Nigerian aftercare motivation, primary results, pilot failures and accepted
abstract are preserved. Title-page conference details follow correspondence details.

Content, figure provenance, references, contents/list fields and PDF bounds checked;
all pages in both main layouts and the supplement visually reviewed. No experiment,
paid API call, remote push or conference submission was performed for this revision.
Earlier versioned and unversioned files are historical drafts.

---

# Current submission files - 6 October 2026 (v5)

Submit these matching files from paper/submission/:

- [Word manuscript](submission/NASEF2026_Full_Paper_Oyewale_Meyer-Petgrave_v5.docx)
- [Matching PDF](submission/NASEF2026_Full_Paper_Oyewale_Meyer-Petgrave_v5.pdf)
- [Email draft](submission/NASEF2026_Full_Paper_Submission_Email.md)

The unversioned Word manuscript is an older draft. The v5 PDF was exported directly
from Microsoft Word after updating the contents and list fields. It has 21 pages,
eight figures, five research tables and one abbreviation table (14 entries).
Conference/Sub-theme V heading, table of contents, list of figures, list of tables
and list of abbreviations are included. Short tables remain together on one page.

Fitzroy's monitoring-gap, unnoticed-fault and trust motivation is retained in the
opening, framed as a hypothesis where it is not measured by this study. The proposed
plain-language, evidence-citing conversation remains a design objective; pilot failures
are still reported. All experimental values and the accepted abstract source are preserved.

The editable alternative is NASEF2026_Overleaf_v5.zip (XeLaTeX). Its separate PDF is
NASEF2026_Full_Paper_Overleaf_v5.pdf. Use the matching Word-exported PDF above for the
requested two-format submission. No email, conference submission or remote push occurred.

The v5 architecture revision adds four original vector engineering diagrams: installation and telemetry blueprint, layered system architecture, question-to-evidence flowchart, and synthetic evaluation workflow. The original brief and Useful Figures.docx informed their structure; their third-party graphics were not copied. Proposed hardware and field functions are distinguished from evaluated software. The Overleaf PDF is 22 pages; its ZIP contains 24 files including four editable SVGs. All figures and document pages were visually reviewed, and automated provenance, reference and PDF-boundary checks passed.

---

# Current full-paper package - 6 October 2026 (v3)

The accepted abstract is for oral presentation. No full-paper template or page limit
was supplied. The current manuscript is paper/FULL_PAPER.md; the editable Overleaf
project is paper/overleaf/main.tex, references.bib and figs/.

Current files in paper/submission/:

- NASEF2026_Full_Paper_Overleaf_v3.pdf - reviewed 16-page paper.
- NASEF2026_Overleaf_v3.zip - self-contained upload project (18 files).
- NASEF2026_Timing_Reproducibility.zip - code, protocol and timing evidence overlay.
- overleaf_validation_v3.json - compilation and package checks.

This version retains the accepted methodology title and Fitzroy's Nigerian aftercare
motivation, introduces the six-step care loop with explicit implementation limits,
and reports the audited exploratory timing study. Seven vector figures, five tables,
twelve references; A4, 11-point Times-style type and 23 mm margins. The full-paper
abstract is 268 whitespace-delimited words. Previously accepted abstract sources and
Word files remain unchanged; older full-paper PDF/Word files are historical.

The original benchmark and Claude pilot are preserved. Timing is explicitly post-hoc,
with prior exposure to proposed results; no field effectiveness or installer comparison
is claimed. Current timings replace unsupported draft values under documented scoring.

Upload the v3 ZIP as a new Overleaf project and select XeLaTeX. The exact ZIP was
compiled in an isolated directory with identical PDF text. No actual Overleaf upload,
GitHub publication of this revision, conference submission or email occurred.
See OVERLEAF_REVIEW.md for decisions and validation.

---

# Submission package — 30 September 2026

The author will submit the documents personally. No submission, registration,
email or payment has been sent by this project.

## Prepared files

Run `python scripts/build_submission.py --contact path/to/private-contact.json` to
produce the abstract and full paper in `paper/submission/`. The local package contains
confirmed authors Oyewale, D.O. and Meyer-Petgrave, F., both at Petgrave.io Technologies
Ltd, Nigeria, and Daniel Oyewale's supplied correspondence details. The contact config
and generated correspondence-bearing files are ignored by Git. Public manuscript
sources contain names and affiliation but not the phone number.

The revised title is 15 whitespace-delimited words; the abstract is 263. There are five
keywords. Word files use Times New Roman 12 pt and double-spaced body text. The full
paper has four tables and three figures. No unverified funding, conflict-of-interest,
contribution or ethics declaration has been invented; authors should add any declarations
required by the venue and verify their accuracy.

## Official instructions checked 28 September

Source: [SESN conference page](https://www.sesn.com.ng/SolarEnergyConference.aspx).
The page requests a title no longer than 20 words, author surnames/initials and
superscript affiliations, corresponding-author phone/email, an abstract up to 300
words, 3–5 keywords, and a Word attachment in 12-point Times New Roman, double spaced.
The listed important dates give 30 September for abstracts and 5 October for full
papers; the abstract paragraph separately says 5 October. Use the earlier date.

The published recipient list contains inconsistent-looking `qmail.com` addresses;
confirm the recipients directly with the organizer rather than silently correcting
them or sending to an assumed address. The user is handling submission.
A definitive full-paper template, page limit and reference style were not available
in the checked call. The manuscript uses a provisional scholarly layout; reformat if
the organizer supplies a template. Do not claim venue-format approval.

## Evidence ready for author review

- The offline evaluation is preserved: 233/240 identifiable clean cases for full access.
- A live pilot now completed 24 conversations and 48 requests. Strict JSON acceptance
  was 0/24; all responses were fenced Markdown. This failure is included in both abstract
  and manuscript. The post-hoc analysis is explicitly identified and separate.
- Six bounded related-work descriptions and two field-acquisition references were checked against primary records; see
  [verification log](RELATED_WORK_VERIFICATION.md). This is not an exhaustive search.
- No physical logger, field data, human usability trial, blinded prose rating or
  independent domain validation is claimed. Domain review remains desirable and has
  not been performed by an outside expert.
- Public demonstration and result links appear in the data/code availability section.
  The public website is a static evidence presentation, not a hosted Claude chat.

Read both Word files before uploading. In particular, confirm the author ordering,
affiliation, correspondence details, scientific interpretation and venue instructions.

## Methodology revision — 30 September 2026

The abstract and full manuscript now lead with the reproducible methodology, with
existing experiments retained as the synthetic worked evaluation. Section 3.2 sets
out the reusable workflow and implemented/proposed boundary. Section 3.3 identifies
proposed field sites, equipment sources, channel mappings, collection and storage,
quality controls, independent fault references and requirements for a new field study.
No site agreement, device integration, real-data collection or field validation is claimed.
The acquisition proposal was added after the experiments; frozen protocols and results
are unchanged. The public offline dashboard link is included alongside both explorers.

The Word files have been regenerated. Previous versions are retained locally in
`paper/submission/previous_20260928/`. The provisional layout and requirement for
final author review still apply; this revision does not assert venue acceptance.

Final abstract refinement: adopted the author-supplied formulation, shortened to 263 whitespace-delimited words, with five comma-separated keywords and a sentence-case title. Scoring is described as separate from diagnosis, without implying independent external evaluation. Both Word documents use this same abstract.

Title-page correction: conference and Sub-theme V now follow the corresponding-author details, before the abstract. Regenerated v4 Word, matching PDF and Overleaf package; both PDFs remain 20 pages.
