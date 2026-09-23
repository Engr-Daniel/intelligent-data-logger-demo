# Research task tracker

## NASEF full-paper upgrade — 23 September 2026

- [x] Create branch `research/nasef2026-synthetic-benchmark`.
- [x] Read the working draft; narrow empirical claims to a synthetic information-access study.
- [x] Write v1 protocol, disjoint seeds, four conditions, stress levels and outcome definitions.
- [x] Implement isolated plant simulator, physical checks and oracle-free access boundary.
- [x] Run development (8 installations) and evaluation (24 installations) without evaluation tuning.
- [x] Export case evidence, cluster intervals, paired effects, failure tables and PNG/SVG figures.
- [x] Implement a capped live-Claude pilot with structured outputs, usage records and tests.
- [x] Draft paper methods/results, a bounded abstract and venue notes.
- [ ] Complete live pilot: set the required workspace ID or use a workspace-scoped API key.
- [ ] Complete verified related work, domain review and full-paper venue formatting.
- [ ] Review weak baselines/task-mix limitations before making broader comparative claims.
- [ ] Obtain external-data or independent simulator validation in subsequent research.

The earlier real-data and expert-panel plan below remains future work for the broader
vision. The current submission can only report the narrower synthetic study actually run.

## Completed

- [x] Implement the synthetic M1–M6 demonstration.
- [x] Run the offline experiment on 21 September 2026: 34,560 rows, physical
  validation PASS, six M6 scenarios PASS, eleven canonical query checks PASS.
- [x] Run the regression suite: 80 tests passed.
- [x] Preserve timestamped evidence and original milestone reports.
- [x] Create project guidance, research memory, a results overview and CSV exports.

## Next: live conversational pilot

- [x] Build a local status-first dashboard with historical charts, evidence inspection,
  offline investigations, session export and a Claude follow-up conversation path.
- [ ] Record a user-led walkthrough of the interface; review usability and presentation.

- [ ] Verify local API configuration without exposing credentials.
- [ ] Fix the model, prompt, question set, repeat count and spending limit before the run.
- [ ] Capture full questions, answers, tool calls/results, model identifier, token usage,
  latency and errors in a separate run folder.
- [ ] Assess tool selection, evidence traceability, numerical fidelity, uncertainty,
  missing-data abstention and refusal of unsupported blame using a stated rubric.
- [ ] Report live outcomes separately from deterministic and mocked-test outcomes.

## Paper evaluation: protocol to define before collecting results

- [ ] Formalize research questions about the incremental value of operational history
  and cross-component evidence.
- [ ] Define comparable full-history/cross-component, no-history, single-component,
  and manual-dashboard conditions where feasible; specify precisely what each can access.
- [ ] Select real or independently sourced representative PV/battery data with documented
  provenance, access permissions and ground-truth/annotation procedures.
- [ ] Separate development and held-out installations/events/questions; include normal
  cases, alternative causes, missingness and cases the system should decline to diagnose.
- [ ] Predefine metrics, repeats, independent sampling units, uncertainty reporting and
  statistical analysis. Do not treat correlated telemetry rows as independent trials.
- [ ] Arrange installer/owner assessment with a scoring rubric and disagreement procedure.
- [ ] Evaluate forecasting and battery-health estimators against appropriate baselines.
- [ ] Produce paper tables/figures from archived evidence and report all limitations.
- [ ] Verify related-work references and novelty claims; select venue and author details.

The manuscript's proposed comparisons and field claims have not yet been evaluated.
See `RESULTS.md` for the evidence currently available.
