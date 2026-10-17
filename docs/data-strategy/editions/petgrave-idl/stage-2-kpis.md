# Stage 2: Data & KPI Mapping. Petgrave.io IDL edition

*How do we know it is working?* Status: ◐ provisional · Last updated: 17 Oct 2026

Following the research-innovation playbook, **research questions** (what the study answers) are kept apart from **programme metrics** (decisions about the programme). The AI-integration playbook adds three kinds of metric for each AI use: outcome, quality and guardrail.

## Research questions (from the rationale, R1–R6)

| ID | Question | The decision its answer informs |
|---|---|---|
| RQ1 | How often do real systems underperform, and for how long before anyone notices? | Whether early detection is worth building for |
| RQ2 | What share of solar energy displaces a generator vs. the grid? | How ROI and carbon must be computed |
| RQ3 | Does field diagnosis approach the synthetic result? | Whether the method transfers |
| RQ4 | Do owners act on the answers? | Whether the product has a customer |
| RQ5 | Does a verified record help sell the next system? | The adoption claim |
| RQ6 | Does performance data change financing terms? | Whether financiers are a segment |

## Programme metrics

**North Star: M01, field-confirmed diagnoses.** These are diagnoses whose cause matches what the installer recorded on site. The IDL's whole claim rests on a diagnosis being right, and only an installer's recorded finding can confirm that in the field.

| ID | Kind | Metric | Data today | Decision it informs | Owner | Cadence |
|---|---|---|---|---|---|---|
| M01 | Outcome | Field-confirmed diagnoses: matches ÷ diagnoses with a recorded installer finding (counts while n < 30) | **gap**: no finding is recorded anywhere | Whether the method works in the field | Daniel | Monthly during the pilot |
| M02 | Outcome | Sites with a usable feed: sites with ≥ 28 of 30 days of readings ÷ sites enrolled | **gap** | Whether the data route (manual, export, API) is viable | Daniel | Weekly |
| M03 | Quality | Correct abstention: declined when data was insufficient ÷ cases requiring abstention | exists (synthetic, C04) | Whether the system can be trusted to say "I don't know" | Daniel | Per release |
| M04 | Quality | Output-contract pass: replies parsed as the required structure ÷ replies | exists: **0/24** (C06) | Whether conversational answers can be scored and shown | Daniel | Per release |
| M05 | Quality | Valid citations: replies naming only measurements that exist in the receipt ÷ replies | exists: **15/24** (C06) | Whether the prose can be trusted | Daniel | Per release |
| M06 | Outcome | Days from fault onset to detection | synthetic only (timing supplement); field **gap** | Whether early detection is real (RQ1) | Daniel | Monthly |
| M07 | Programme | Installers agreeing to host a site ÷ installers contacted | **gap** (pack ready) | Pilot size and timing | Daniel | Weekly until 3 sites |
| M08 | Guardrail | Cost per site per month (connectivity + model + visits) | partial: model about USD 0.21 / 24 conversations | Whether the product is affordable without funding | Daniel | Monthly |

**Removed by the vanity test** ("what would we do differently if this changed?"): number of tools (14), rows generated (34,560), regression tests passed (120), dashboard visits. These describe the build, not whether anyone is helped.

**Gaps whose fix is instrumentation:** M01 and M07 need the installer pack and call-back log (`../../instruments/`). M02 needs the field-pilot data spec.

**Done checks:** [x] every block has a health measure · [ ] shared agreement on success (check with Fitzroy) · [x] vanity metrics removed · [x] gaps documented

**The question this raises next.** Are we capable of collecting and acting on these numbers today?
