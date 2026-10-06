# Exploratory detection-delay results

Synthetic automated checks; no installer comparator or field validation. Protocol specified after seeing
unverified co-author claims. Existing policy and thresholds unchanged. No paid API calls.

Intervals resample installations (2,000 draws). Periodic phases are averaged within installation.
Delay is relative to the first daily mean latent loss >=5%, not physical onset.

| Stress | Access | Rule | Period | Detection % | Mean delay among detected (days) | Any control alert % | Waiting score (days) |
|---|---|---:|---:|---:|---:|---:|---:|
| clean | full_cross | 1 | 1 | 95.0 | 4.79 | 0.0 | 5.05 |
| clean | full_cross | 1 | 7 | 94.3 | 7.74 | 0.0 | 7.90 |
| clean | full_cross | 1 | 14 | 86.4 | 10.61 | 0.0 | 11.00 |
| clean | full_cross | 1 | 30 | 71.2 | 16.50 | 0.0 | 16.78 |
| clean | full_cross | 3 | 1 | 95.0 | 6.79 | 0.0 | 6.95 |
| clean | full_cross | 3 | 7 | 65.7 | 20.54 | 0.0 | 19.14 |
| clean | full_cross | 3 | 14 | 23.2 | 34.48 | 0.0 | 27.59 |
| clean | full_cross | 3 | 30 | 0.0 | nan | 0.0 | 28.75 |
| clean | full_inverter | 1 | 1 | 75.0 | 7.13 | 100.0 | 9.65 |
| clean | full_inverter | 1 | 7 | 67.1 | 11.46 | 95.8 | 14.45 |
| clean | full_inverter | 1 | 14 | 56.8 | 14.56 | 90.8 | 18.11 |
| clean | full_inverter | 1 | 30 | 39.8 | 18.44 | 80.7 | 22.42 |
| clean | full_inverter | 3 | 1 | 70.0 | 9.43 | 95.8 | 12.25 |
| clean | full_inverter | 3 | 7 | 32.1 | 21.44 | 73.8 | 24.76 |
| clean | full_inverter | 3 | 14 | 11.1 | 25.35 | 42.0 | 27.78 |
| clean | full_inverter | 3 | 30 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_cross | 1 | 1 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_cross | 1 | 7 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_cross | 1 | 14 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_cross | 1 | 30 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_cross | 3 | 1 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_cross | 3 | 7 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_cross | 3 | 14 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_cross | 3 | 30 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_inverter | 1 | 1 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_inverter | 1 | 7 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_inverter | 1 | 14 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_inverter | 1 | 30 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_inverter | 3 | 1 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_inverter | 3 | 7 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_inverter | 3 | 14 | 0.0 | nan | 0.0 | 28.75 |
| clean | recent_inverter | 3 | 30 | 0.0 | nan | 0.0 | 28.75 |
| moderate | full_cross | 1 | 1 | 95.0 | 3.16 | 0.0 | 3.85 |
| moderate | full_cross | 1 | 7 | 91.4 | 6.98 | 0.0 | 7.67 |
| moderate | full_cross | 1 | 14 | 87.5 | 10.38 | 0.0 | 11.00 |
| moderate | full_cross | 1 | 30 | 71.5 | 16.29 | 0.0 | 16.82 |
| moderate | full_cross | 3 | 1 | 95.0 | 5.05 | 0.0 | 5.65 |
| moderate | full_cross | 3 | 7 | 63.6 | 20.07 | 0.0 | 19.14 |
| moderate | full_cross | 3 | 14 | 27.9 | 32.03 | 0.0 | 27.29 |
| moderate | full_cross | 3 | 30 | 0.0 | nan | 0.0 | 28.75 |
| moderate | full_inverter | 1 | 1 | 75.0 | 6.87 | 100.0 | 9.45 |
| moderate | full_inverter | 1 | 7 | 67.1 | 11.73 | 97.0 | 14.58 |
| moderate | full_inverter | 1 | 14 | 55.0 | 14.30 | 92.0 | 18.13 |
| moderate | full_inverter | 1 | 30 | 39.5 | 18.36 | 81.7 | 22.36 |
| moderate | full_inverter | 3 | 1 | 70.0 | 9.36 | 100.0 | 12.20 |
| moderate | full_inverter | 3 | 7 | 30.7 | 20.12 | 74.4 | 24.59 |
| moderate | full_inverter | 3 | 14 | 11.4 | 25.44 | 42.0 | 27.71 |
| moderate | full_inverter | 3 | 30 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_cross | 1 | 1 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_cross | 1 | 7 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_cross | 1 | 14 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_cross | 1 | 30 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_cross | 3 | 1 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_cross | 3 | 7 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_cross | 3 | 14 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_cross | 3 | 30 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_inverter | 1 | 1 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_inverter | 1 | 7 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_inverter | 1 | 14 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_inverter | 1 | 30 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_inverter | 3 | 1 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_inverter | 3 | 7 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_inverter | 3 | 14 | 0.0 | nan | 0.0 | 28.75 |
| moderate | recent_inverter | 3 | 30 | 0.0 | nan | 0.0 | 28.75 |
| severe | full_cross | 1 | 1 | 95.0 | 3.63 | 54.2 | 4.15 |
| severe | full_cross | 1 | 7 | 85.0 | 8.87 | 21.4 | 9.92 |
| severe | full_cross | 1 | 14 | 74.6 | 12.28 | 10.7 | 13.81 |
| severe | full_cross | 1 | 30 | 58.3 | 17.44 | 5.3 | 19.07 |
| severe | full_cross | 3 | 1 | 90.0 | 7.56 | 16.7 | 8.35 |
| severe | full_cross | 3 | 7 | 47.1 | 18.11 | 0.0 | 20.25 |
| severe | full_cross | 3 | 14 | 25.0 | 27.76 | 0.0 | 26.52 |
| severe | full_cross | 3 | 30 | 0.0 | nan | 0.0 | 28.75 |
| severe | full_inverter | 1 | 1 | 80.0 | 6.38 | 100.0 | 8.90 |
| severe | full_inverter | 1 | 7 | 67.1 | 10.60 | 95.8 | 14.44 |
| severe | full_inverter | 1 | 14 | 56.8 | 13.69 | 90.8 | 18.12 |
| severe | full_inverter | 1 | 30 | 38.0 | 17.24 | 80.3 | 22.53 |
| severe | full_inverter | 3 | 1 | 75.0 | 9.33 | 95.8 | 12.15 |
| severe | full_inverter | 3 | 7 | 28.6 | 21.43 | 73.2 | 24.78 |
| severe | full_inverter | 3 | 14 | 8.9 | 23.76 | 45.2 | 27.69 |
| severe | full_inverter | 3 | 30 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_cross | 1 | 1 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_cross | 1 | 7 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_cross | 1 | 14 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_cross | 1 | 30 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_cross | 3 | 1 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_cross | 3 | 7 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_cross | 3 | 14 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_cross | 3 | 30 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_inverter | 1 | 1 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_inverter | 1 | 7 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_inverter | 1 | 14 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_inverter | 1 | 30 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_inverter | 3 | 1 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_inverter | 3 | 7 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_inverter | 3 | 14 | 0.0 | nan | 0.0 | 28.75 |
| severe | recent_inverter | 3 | 30 | 0.0 | nan | 0.0 | 28.75 |

## Interpretation and reproducibility

- Detection coverage uses only reference-crossing declines. Below-threshold declines and pre-reference alerts are separate in summary.csv.
- Conditional delay excludes misses; never infer a paired benefit by subtracting conditional means across schedules.
- Waiting score assigns 61 minus reference day to misses; paired_schedule_effects.csv compares the same installations.
- Any-control alert is a union across stable, changing-weather and static-low-efficiency controls.
- Rule 3 requires three consecutive scheduled positives; unknown or normal resets it. It is exploratory, not tuned.
- Recent-only conditions can abstain because the unchanged trend policy requires 14 valid days.
- phase_outcomes.csv retains every installation, phase and rule. daily_predictions.csv and receipts.jsonl.gz preserve decisions.
- manifest.json records source snapshots, input equivalence and all output hashes.
- This analysis shares the original simulator and assumptions and does not reproduce or certify an unavailable co-author analysis.
