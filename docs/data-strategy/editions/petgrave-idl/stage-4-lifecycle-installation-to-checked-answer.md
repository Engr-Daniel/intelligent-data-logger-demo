# Stage 4: Data Lifecycle Mapping. Petgrave.io IDL edition

**Flow: a real installation → a checked answer.** Status: ◐ **provisional.** This flow has not run for real. It is mapped from the implementation, the paper's Fig 7 and Suny's field assumptions. Re-map it after the first pilot month.

| Stage | What happens (as built or planned) | Who | Tools | Gap | Impact on decisions |
|---|---|---|---|---|---|
| **Capture** | Synthetic only. In the field, most systems show a lifetime-kWh counter on the inverter screen; some have Wi-Fi monitoring (C17) | Owner or installer, by hand | Inverter screen, vendor app | **G01:** no real capture route chosen; device interfaces assumed (X03) | No field answer is possible |
| **Store** | SQLite operational store with a versioned schema (C01) | System | `src/datacontext/` | — (strong) | — |
| **Prepare** | Schema mapping and physical validation; missing data shown as gaps (C01, C05) | System | `validation.py` | **G03:** no device-to-schema mapping for any real inverter | Real readings can't enter |
| **Analyse** | Deterministic tools: generation, overload, decline, battery, data quality, grid events, ROI, carbon (C03) | System | `src/analytics/` | **G04:** ROI and carbon assume grid displacement and a placeholder factor (X04, X05) | Money and carbon answers can be off by 4–6× |
| **Visualise** | Answers in plain language with an evidence receipt; status-first dashboard (C03, C07) | Claude / offline engine | `src/reasoning/`, dashboard | **G05:** strict output contract 0/24; citations 15/24 (C06) | Conversational answers can't yet be scored or fully trusted |
| **Act** | *(designed)* Owner calls the installer, shifts loads or buys fuel; installer visits | Owner, installer | — | **G06:** no route from an answer to an action exists (no alert, no hand-off to an installer) | An answer that nobody acts on creates no value |
| **Learn** | Synthetic answers are scored against evaluation-only labels (C04) | Research | `src/evaluation/` | **G02:** in the field, **nothing records what the installer actually found**, so no diagnosis can be checked (C16) | We can never know if the IDL is right |

**Break patterns matched:**
- **No feedback loop (Learn):** G02.
- **Data exists but is invisible (Capture):** the inverter counter is read by nobody (G01).
- **Decisions made outside the data (Act):** owners find faults when the power goes off (C15).

## Prioritised gaps

| ID | Gap | Root cause | Decision it blocks | Priority |
|---|---|---|---|---|
| G02 | No record of what installers find on call-backs | Nobody asked; it isn't anyone's job | Whether the IDL works at all (M01) | **High** |
| G01 | No real capture route | Device-interface assumption (X03) | Pilot design (M02) | **High** |
| G04 | ROI and carbon counterfactual | Model shortcut; generator cost left `null` | Every money and carbon answer | **High** (cheap to fix) |
| G05 | Output contract and citation fidelity | Free-text final reply | Scoring and trust in prose | Medium |
| G03 | No device-to-schema mapping | No real device yet | Field ingestion | Medium (after G01) |
| G06 | No answer → action route | Product not yet designed | Value for owners | Medium (pilot will show it) |

**Done checks:** [x] the flow is visible end to end · [x] the breaks are identified · [ ] teams agree (check with Fitzroy) · [x] a high-impact shortlist

**The question this raises next.** Which of these gaps are worth fixing first, and for whom?
