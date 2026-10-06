# Running and reading the exploratory timing experiment

This extension uses only local synthetic data and deterministic analytics. It does
not need an Anthropic key or incur API charges. The [analysis protocol](DETECTION_DELAY_PROTOCOL.md)
is exploratory: it was specified after seeing unverified numbers in a co-author draft.

## Commands

From the repository root, using the project's Python environment:

```powershell
python -m pytest tests/test_research.py tests/test_detection_delay.py -q
python scripts/analyze_detection_delay.py
python scripts/verify_detection_delay.py reports/research/<timestamp>_detection_delay
python scripts/summarize_detection_delay.py reports/research/<timestamp>_detection_delay
```

The runner creates a fresh archive and refuses to overwrite an existing directory.
Keep the printed run path. The summary generator creates a separate interpretation
folder with a readable report, vector PDF and 300-dpi PNG, leaving the raw run intact.
The audit verifies original-baseline fingerprints as well as the new archive.

## What is measured

- Four trend episodes for each of the 24 original evaluation installations.
- All four access conditions and three observation-corruption levels.
- Daily decisions at the end of days 14 through 60: 54,144 tool calls in total.
- Daily, weekly, fortnightly and 30-day checks, covering every schedule phase.
- Primary one-positive rule; exploratory three-consecutive-positive sensitivity.
- Detection after a defined loss reference, early alerts, misses, abstentions and
  false trend alerts on three control episodes.

There are 119,808 phase/episode/condition/rule records, not that many independent
installations. The sampling unit remains the installation. The recent-only arms
cannot satisfy the unchanged trend policy's minimum of 14 historical days.

## Read these quantities together

**Detection coverage** is the fraction of reference-crossing trajectories flagged
on or after the first day with mean injected loss at least 5%. Fractional periodic
counts reflect averaging over possible check phases.

**Conditional delay** describes only detected installation-phase combinations.
Two schedules can have different detected subsets, so subtracting their conditional
means is not a paired comparison.

**Waiting score** counts days without a qualifying detection within the fixed
observation horizon. A missed case receives 61 minus its reference day. Paired
schedule contrasts average phases within each installation before calculating
uncertainty. This is not an estimate of how long an undetected fault would eventually
remain undetected.

**Any-control alert probability** is the fraction of installations receiving at
least one false trend alert across stable, changing-weather and static-low-efficiency
controls. Per-check alert rate is a different quantity; both appear in the archive.

**Early alerts** precede the 5% reference, not necessarily the start of physical
loss. Below-threshold decline trajectories are reported separately. The reference
uses latent injected loss only in scoring; the tool uses observed telemetry only.

Three monthly checks cannot occur in this short horizon. Report that constraint
rather than treating the corresponding zero coverage as a useful competing design.
No installer, physical intervention, avoided incident or economic benefit is tested.

## Outputs and provenance

- `manifest.json`: run status, source/environment details, input and output hashes.
- `source/`: exact analysis protocol, runner, tests, configuration and policy snapshots.
- `daily_predictions.csv`, `receipts.jsonl.gz`: every rolling diagnosis and its evidence.
- `references.csv`: evaluation-only reference days and injected loss parameters.
- `dataset_hashes.csv`, `physical_checks.csv`, `day60_equivalence.csv`: integrity checks.
- `phase_outcomes.csv`: complete scheduled-check and persistence scoring.
- `summary.csv`: installation-level estimates and bootstrap intervals.
- `paired_schedule_effects.csv`: finite-horizon paired comparisons against daily checks.
- `REPORT.md`: complete tabulation with definitions and limitations.

The script reruns the existing policy; it does not tune thresholds or silently
replace frozen benchmark results. Similarity to proposed draft numbers is not
proof that an unavailable earlier analysis used the same definitions.

For the one-positive rule, daily checks include every periodic check by construction.
Earlier or equal detection is therefore expected. The experiment quantifies the
size of delays, misses and false-alert exposure; it is not an independent proof
that the diagnostic algorithm improves when checked more frequently.
