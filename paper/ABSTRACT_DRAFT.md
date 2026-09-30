# A reproducible methodology for evidence-grounded conversational diagnostics of solar PV–battery systems: implementation and synthetic evaluation

Oyewale, D.O.¹ and Meyer-Petgrave, F.¹

¹Petgrave.io Technologies Ltd, Nigeria

## Abstract

Conversational diagnostics for solar PV–battery installations require reproducible methods to constrain diagnostic access, preserve engineering evidence, expose uncertainty and separately evaluate diagnostic and conversational outputs. This paper presents an implemented methodology separating telemetry preparation, controlled historical and cross-component access, deterministic diagnostic tools, structured evidence receipts, conversational reporting and separate scoring against evaluation-only reference labels. A proposed field-acquisition workflow maps observations to inverter interfaces, battery monitoring, energy meters, environmental sensors and installation records; no field data were collected.

A controlled synthetic evaluation comprises twelve matched episodes for each of 24 evaluation installations, separate from eight development installations. A 2 × 2 design varies historical access (60 days versus 24 hours) and measurement access (cross-component versus inverter-only). Three observation-quality levels produce 3,456 paired predictions under a shared deterministic policy. With clean observations, full historical and cross-component access resolved 233/240 identifiable cases (97.1%; 95% installation-cluster bootstrap interval: 95.4–98.8%), compared with 53.8% for historical inverter-only access and 40.0% for recent cross-component access. Severe corruption reduced full-access accuracy to 90.0%; restricted conditions frequently abstained when evidence was insufficient.

A separate 24-conversation Claude development pilot selected the intended tool throughout but failed the prespecified strict JSON output contract in every response. Post-hoc removal of Markdown fences recovered 24 receipt-consistent labels; 15 responses satisfied the predefined measurement-name citation rule. The evaluation distinguishes evidence-access limitations, diagnostic outcomes, abstention and conversational-interface failures. The contribution is a reproducible methodology, reference implementation and controlled worked evaluation. Shared simulator–policy assumptions and the absence of field validation limit generalization. Application to real installations requires verified device-to-schema mappings, independent fault references and a new field evaluation protocol.

Keywords: solar diagnostics, reproducible methodology, evidence grounding, conversational diagnostics, synthetic evaluation
