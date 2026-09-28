# Publication and site guide

The public experiment explorer is built from a strict allowlist with
`python scripts/build_public_site.py`. Output is `.site/` (ignored). It includes
HTML/CSS/JavaScript, the verified six-scenario snapshot, archived benchmark metrics,
the live pilot summary and a verified five-minute synthetic outage trace. It never
copies `.env`, the Python server, local logs, contact details or the workspace tree.

## GitHub Pages

The `Publish research explorer` workflow verifies the frozen evaluation and publishes
only `.site/` on pushes to `main`. Set repository Settings → Pages → Source to
**GitHub Actions**. No API key, paid host or external frontend dependency is required.

- Public explorer: https://Engr-Daniel.github.io/intelligent-data-logger-demo/
- Comparative study: https://Engr-Daniel.github.io/intelligent-data-logger-demo/research.html
- Direct scenario: append `?scenario=grid_outage_islanding` to the explorer root.

GitHub Pages serves static results. Claude conversation stays on the local Python
server: `python scripts/serve_dashboard.py`, then http://127.0.0.1:8501/.
The explorer is also available at /explorer/ and /explorer/research.html locally.

## Rebuild submission documents

Install `python-docx==1.2.0` in addition to the project dependencies. Put the
corresponding author's `name`, `email` and `phone` in a local JSON file, then run:

```text
python scripts/build_paper_figure.py
python scripts/build_submission.py --contact path/to/private-contact.json
```

Outputs are in ignored `paper/submission/` so the correspondence phone number is
not automatically published in the repository. The public manuscript source is
`paper/FULL_PAPER.md`; the abstract source is `paper/ABSTRACT_DRAFT.md`.
The Word documents use A4, 12-point Times New Roman and double-spaced body text.
Full-paper template/page-limit requirements have not been supplied by the venue;
this is a readable provisional layout, not a claim of template compliance.

The author submits the documents. No email, registration or payment is automated.

## Evidence boundaries

The original M1–M6 demo, the 24-installation benchmark and the one-installation live
pilot have different denominators. They are displayed separately. Strict live JSON
compliance is 0/24. Post-hoc removal of Markdown fences is exploratory and does not
rewrite the original scores. The site links both analyses and shows all raw replies.

Archived research results are immutable. A future model/prompt/parser revision must
use a new run and explicitly state protocol changes. Do not tune the frozen study
against evaluation seeds. The website is a presentation artifact, not validation of
hardware, field diagnosis, user usefulness or every statement in model prose.

## Optional browser validation

Install `requirements-publication.txt` and a Playwright browser, then run
`python scripts/check_publication_browser.py --base-url http://127.0.0.1:8503`.
On Windows, `--browser` accepts the installed Edge executable path. The script
checks both local views and regenerates the README screenshots. It uses no paid API.
