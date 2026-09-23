# Research experiment index

The benchmark isolates historical and cross-component data access. Start with the
[protocol](../../docs/RESEARCH_PROTOCOL.md), then read the evaluation report below.

| Run | Role | Outcome |
|---|---|---|
| [Development](20260923T190055526477Z_development/REPORT.md) | 8 seeds, 96 episodes, 1,152 predictions | Complete; clean physical checks passed |
| [Evaluation](20260923T190318100907Z_evaluation/REPORT.md) | 24 disjoint seeds, 288 episodes, 3,456 predictions | Complete; clean physical checks passed |
| [Live development pilot](20260923T190500485533Z_live_development/REPORT.md) | Planned 24 conversations | Incomplete: first request rejected; workspace ID required |

## Paper artifacts

- [Clean-data accuracy figure (PNG)](20260923T190318100907Z_evaluation/accuracy.png)
  / [SVG](20260923T190318100907Z_evaluation/accuracy.svg)
- [Noise/missingness sensitivity figure (PNG)](20260923T190318100907Z_evaluation/robustness.png)
  / [SVG](20260923T190318100907Z_evaluation/robustness.svg)
- [Metric estimates and intervals](20260923T190318100907Z_evaluation/metrics.csv)
- [Paired effects](20260923T190318100907Z_evaluation/paired_effects.csv)
- [Task-specific results](20260923T190318100907Z_evaluation/task_metrics.csv)
- [Confusion counts](20260923T190318100907Z_evaluation/confusion.csv)
- [Every unresolved/incorrect prediction](20260923T190318100907Z_evaluation/unresolved_or_incorrect.csv)
- [Raw predictions](20260923T190318100907Z_evaluation/predictions.csv)
- [Evidence receipts](20260923T190318100907Z_evaluation/receipts.jsonl)
- [Provenance manifest](20260923T190318100907Z_evaluation/manifest.json)

The primary clean full-condition result is 233/240 identifiable cases correct (97.1%).
Its seven failures are five missed gradual declines, one normal day called weather loss,
and one normal day left unresolved. Do not suppress them or tune v1 against these seeds.

The original M5/M6 evaluation remains under `reports/runs/`. Its pass/fail rubric and
this benchmark's per-case diagnostic-label metrics answer different questions.
