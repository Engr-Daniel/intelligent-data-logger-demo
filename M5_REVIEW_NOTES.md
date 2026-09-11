# M5 Review Notes

## Scope

M5 evaluates the frozen, reviewer-approved M3/M4 baseline. It does **not** silently improve analytics in order to make the evaluation look better.

The milestone adds:

- five executable notebooks for generation, validation, analytics, reasoning, and scoring;
- a deterministic evaluation package under `src/evaluation/`;
- the ten canonical demo queries from the experiment brief;
- multidimensional scenario scoring for detection, localization, diagnosis, evidence grounding, calibration, and abstention;
- machine-readable and reviewer-readable M5 reports;
- Colab/local bootstrap cells and a fresh-clone quickstart;
- regression tests protecting the scoring contract and the ground-truth/operational boundary.

## Important evaluation design choices

1. **No accuracy percentage is reported.** This is a controlled synthetic functional demonstration, not a statistical benchmark.
2. **Ground truth is an evaluation oracle only.** `ground_truth.json` is read by `src/evaluation/runner.py`; operational analytics/reasoning do not import it.
3. **Scoring dimensions remain separate.** A correct diagnosis cannot hide weak localization or unsupported evidence.
4. **A capability gap is allowed to remain a gap.** The frozen M3/M4 baseline has no observed-telemetry diagnostic for battery usable-capacity degradation. M5 therefore records `CAPABILITY_GAP` rather than reading the injected latent capacity state and pretending the operational system inferred it.
5. **Sensor-dropout localization is intentionally PARTIAL.** The current data-quality analytic identifies the affected date and missing fields but returns a day-level evidence window, broader than the injected 45-minute dropout. Abstention itself is correct.
6. **M6 may fix mismatches, but M5's rubric should remain stable.** This prevents evaluation criteria from being changed after seeing results.
7. **The optional sixth scenario is not added retroactively.** Section 5.3 of the brief labels grid outage/islanding as an optional stretch scenario, while a later success-criteria line says "all six scenarios." The reviewer-approved M1 baseline froze the five non-stretch scenarios; M5 evaluates that baseline and documents the discrepancy rather than reopening M1.
8. **Relative time is bound for reproducibility.** Canonical query 2 says "yesterday"; the evaluator explicitly binds that phrase to the controlled cloudy-day date (`2026-08-05`) rather than depending on the wall clock.
9. **M5 scores evidence, not LLM writing style.** The live Claude orchestration path was closed in M4 and remains available in notebook 04 with an API key. M5's deterministic scoring evaluates tool selection/evidence contracts and avoids grading nondeterministic prose.

## Current controlled results

- Cloudy-day generation drop: PASS across the applicable dimensions.
- Customer overload/inverter event: PASS across the applicable dimensions.
- Gradual PV performance decline: PASS across the applicable dimensions.
- Battery capacity degradation: CAPABILITY_GAP (no dedicated observed-telemetry diagnostic in frozen M3/M4).
- Sensor dropout: correct detection/diagnosis/evidence/calibration/abstention; PARTIAL localization because the evidence window is day-level.
- All ten canonical query evidence paths pass the M5 deterministic traceability checks.

These are **scenario-specific controlled results**, not accuracy estimates and not evidence of real-world performance.

## Reviewer focus

Please verify:

- the evaluator does not leak ground truth into operational code;
- scenario scoring actually checks evidence objects rather than prose fluency;
- the six dimensions are scored independently;
- the battery degradation capability gap is reported rather than hidden;
- the dropout localization score is not inflated;
- the ten canonical queries use the intended tools and expose assumptions where material;
- notebooks execute from a fresh clone/Colab-style environment without requiring an API key for deterministic evaluation;
- README language does not overclaim evaluation validity.
