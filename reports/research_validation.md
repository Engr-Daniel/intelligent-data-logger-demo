# Research upgrade validation — 23 September 2026

- Full regression suite: **110 passed in 247.56 seconds**, recorded in
  `research_regression_tests.xml` (before the final workspace-header test was added).
- Follow-up API/interface verification after workspace-header support: **16 passed
  in 12.04 seconds**, including the additional optional-header test.
- Tests cover clean physical trajectories for all twelve episode types, data-access
  allowlists, future-row exclusion, generic alarms without cause labels, reproducible
  corruption, oracle isolation, abstention scoring, cluster pairing, disjoint seeds,
  live request budgets, output parsing and credential-error redaction.
- Development archive verified: 96 episodes and 1,152 predictions.
- Evaluation archive verified: 288 episodes and 3,456 predictions.
- Archived source and artifact hashes, case counts, physical outcomes and scoring
  consistency checked with `scripts/verify_research_run.py`.
- Paper primary numerator independently checked: 233/240 identifiable clean cases
  correct under `full_cross`.
- Abstract body: 214 whitespace-delimited words; title is below the venue's 20-word limit.
- Figure generation completed; the clean-data accuracy figure was visually inspected.
- No successful live-Claude output: the pilot and one diagnostic request were rejected
  because the API key needs a workspace header. This is recorded, not treated as a pass.

The original dashboard dataset and original milestone reports were not regenerated
by the research runner. No hardware, field data or human-study result is implied.
