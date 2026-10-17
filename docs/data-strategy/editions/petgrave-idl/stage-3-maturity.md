# Stage 3: Data Maturity Assessment. Petgrave.io IDL edition

Status: ◐ provisional · Last updated: 17 Oct 2026 · Scores reflect **operating** maturity on **real installation data**. The synthetic research pipeline is recorded as a designed head start, not as a score.

| Pillar | Score | Evidence | Designed head start | Constraint to the next level | Next target, and what reaching it looks like |
|---|---|---|---|---|---|
| People & Culture | 2 | Evidence changes our decisions: the paper was reframed when the evidence did not support validation (X01). But this runs through two people. | — | Depends on Daniel and Fitzroy | **3:** an installer or owner, outside the team, challenges an IDL answer with their own evidence |
| Processes | **1** | No real installation's data has ever flowed through the IDL (C02). Where records exist in practice, a person writes them by hand (C14, C17). | **3:** frozen protocol, versioned runs, hashes, verification script (S02) | Nothing has run for real | **2:** three pilot sites send readings every week for a month, and someone reviews them |
| Technology | 2 | The pipeline runs end to end on synthetic data; no device integration or edge deployment exists (C01, C02) | **3–4:** schema, physical validation, 14 tools, receipts | No real feed | **3:** one real feed (manual, export or API) maps to the schema and passes validation |
| Governance | 2 | Strong research governance: evaluation-only labels, provenance hashes, credentials kept server-side. No consent or data-sharing terms for field data (Q06). | Research protocol | No field data terms (NDPA 2023) | **3:** a one-page consent and data-use note signed by each pilot site |
| Strategy & Impact | **1** | No decision outside the research has yet changed because of an IDL answer; no funding (C21) | The rationale and this strategy | No user, no funder | **2:** one owner or installer decision changes because of an IDL answer, recorded in the decision log |

**Limiting constraint: Processes.** It ties with Strategy & Impact, and Strategy & Impact depends on it: no decision can change until real data flows. One finding is easy to miss. The Learn step has no labelled outcomes: even a perfect feed could not show whether a diagnosis was right (Stage 4, G02).

**Not yet feasible (feeds the Stage 6 boundaries):**
- claims of field accuracy;
- our own edge hardware;
- automated actions (dispatch, shutdown, ordering);
- carbon-credit claims;
- extension to mini-grids, wind or buildings (C13);
- any statement that the IDL speeds up adoption.

**Failure patterns present:**
- **High Technology, low Process: yes.** The pipeline is ahead of any real data flow.
- **KPIs unused:** not yet applicable.
- **No ownership:** partly. Who owns field data is undecided (Q06).
- **Dashboards = maturity:** a risk. The public dashboard looks finished but runs on synthetic data.

**Done checks:** [x] evidence-backed · [x] one limiting constraint · [ ] agreement on what's not feasible (check with Fitzroy) · [x] next-level targets

**The question this raises next.** Where exactly does the flow break between a real installation and a checked answer?
