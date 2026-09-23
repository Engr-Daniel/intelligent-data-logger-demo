# Abstract draft — author review required

## Title

Evaluating historical and cross-component evidence for conversational solar-system diagnostics: a synthetic study

## Abstract

Solar monitoring telemetry can support diagnostic explanations, but the value of
combining installation history with measurements from multiple components requires
explicit evaluation. This study presents an evidence-producing diagnostic architecture
for the Intelligent Data Logger and evaluates information access through controlled
synthetic experiments. A physically checked PV–battery–load simulator generated twelve
matched episodes for each of 24 evaluation installations, separate from eight development
installations. Episodes included normal operation, weather-related production loss,
conversion loss, overload, thermal alarms, gradual performance decline and insufficient
evidence. A shared deterministic policy was evaluated under four combinations of
historical/recent-only and cross-component/inverter-only access, with clean and corrupted
observations. The study produced 3,456 paired predictions. On identifiable clean-data
cases, full historical and cross-component access achieved 97.1% correct diagnoses
(95% installation-cluster bootstrap interval: 95.4–98.8%), compared with 53.8% for
historical inverter-only access and 40.0% for recent-only cross-component access.
Accuracy decreased to 90.0% under severe observation corruption. Recent-only conditions
retained acute diagnostic capabilities but frequently abstained on longitudinal tasks,
demonstrating the importance of reporting coverage alongside correctness. The findings
support a task-dependent role for persistent, cross-component evidence in this controlled
setting. The comparison evaluates information ablations rather than independently
optimized competing systems. Project-authored synthetic data, shared modelling
assumptions and the absence of field or successful live-model evaluation limit
generalization. Physical deployment and independent-data validation remain future work.

**Keywords:** solar diagnostics, synthetic telemetry, operational history, evidence grounding

Add confirmed author names, affiliations and corresponding-author contact details.
This abstract deliberately makes no successful Claude or hardware-validation claim.
