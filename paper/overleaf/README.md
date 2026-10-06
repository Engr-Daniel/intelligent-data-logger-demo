# NASEF 2026 Overleaf project

Upload `NASEF2026_Overleaf.zip` using Overleaf > New Project > Upload Project.
Set `main.tex` as the main document and select XeLaTeX; BibTeX runs automatically.
The package contains the complete editable manuscript, `references.bib`, vector PDF
figures, PNG previews and a figure provenance manifest. No repository, API key or
external image download is needed to compile it.

## Scope and layout

The paper presents a reproducible methodology and controlled synthetic evaluation.
Seven manuscript figures show the proposed care loop, evidence/evaluation boundary,
question-to-evidence workflow, access design and quantitative results. The additional
`06_detection_delay` asset supports the separately supplied exploratory timing
supplement. Reference labels are evaluation-only; physical acquisition and verified
maintenance outcomes remain proposed. Primary pilot failures are preserved.

The provisional author layout uses A4, 11-point Times-style text, 23 mm margins,
numbered citations, contents, figure/table lists and fourteen abbreviations. No
full-paper template or page limit was supplied. The conference and Sub-theme V follow
the correspondence details. The correspondence phone is omitted from the LaTeX source.

## Regenerate

From the repository, run `python scripts/build_latex_figures.py`, then
`python scripts/build_overleaf.py`. Compile `main.tex`, then use
`python scripts/check_overleaf.py` to validate and package it. Reconcile direct
Overleaf edits into `paper/FULL_PAPER.md` before regenerating. Figure data come from
frozen archives; regeneration does not run experiments or call Claude.

The separate Word/PDF pair is the matching two-format conference submission.
Supplement S1 and the timing reproducibility ZIP accompany the paper. Actual upload
and submission are performed by the authors.
