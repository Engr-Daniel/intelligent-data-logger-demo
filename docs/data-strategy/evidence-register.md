# Evidence register: Intelligent Data Logger

Status: **designed** (specified or planned) · **operating** (running, here only on synthetic or demo data) · **measured** (operating, with numbers someone reviews) · **reported** (someone said so, unverified). "Synthetic" marks results from simulated installations: they show the method, not field performance.

## Sources

| ID | Source | Type | Date | Location | Notes |
|---|---|---|---|---|---|
| S01 | Repository code and test suite | code | 17 Oct 2026 | this repo, branch `research/nasef2026-synthetic-benchmark` | 120 tests pass (run 17 Oct) |
| S02 | Results and research archives | dataset | 21–28 Sep 2026 | [RESULTS.md](../../RESULTS.md), [reports/research/](../../reports/research/README.md) | All synthetic |
| S03 | Full paper (submitted) | doc | 16 Oct 2026 | [paper/FULL_PAPER.md](../../paper/FULL_PAPER.md); Drive: Submitted_NASEF2026_Full_Paper | — |
| S04 | NASEF abstract | doc | 30 Sep 2026 | Drive: NASEF2026_Abstract_Oyewale_Meyer-Petgrave.docx | Accepted for oral presentation |
| S05 | Executive summary, "Datalodger Intelligence" | doc | 14 Aug 2026 | Drive: Executive Summary | Earliest statement of intent |
| S06 | Technical presentation | deck | 14 Sep 2026 | Drive: Intelligent_Data_Logger_Experiment_Technical_Presentation.pptx | 22 slides, from before the comparative study |
| S07 | Research and product rationale | doc | 17 Oct 2026 | [docs/RESEARCH_RATIONALE.md](../RESEARCH_RATIONALE.md) | External sources listed there |
| S08 | Live Claude development pilot | dataset | 28 Sep 2026 | [reports/research/](../../reports/research/README.md) | 24 conversations, one development seed |
| S09 | Daniel Oyewale, in conversation | person | 17 Oct 2026 | — | Radio-station experience; installer feedback; funding; roles |
| S10 | Suny data strategy, installer edition, Stage 1 | doc | 14 Oct 2026 | github.com/sunyenergy/suny `docs/data-strategy/` | Survey n = 12 (2 internal tests excluded); call-back question n = 7 |
| S11 | Suny code: `packages/solar/src/measured.ts`, `generation_readings` | code | 10 Oct 2026 | github.com/sunyenergy/suny | Designed for Suny; not this project |
| S12 | External evidence: Ember, Tracking SDG7, Energy Policy (2024), IFI grid factors | sourced | 2024–2026 | [RESEARCH_RATIONALE.md, Sources](../RESEARCH_RATIONALE.md#sources) | — |
| S13 | Petgrave.io™ Data Strategy Blueprint: PDF and skills | method | 2026 | Drive and github.com/fitzroypet/petgrave-data-strategy | — |
| S14 | Paper figures Fig1–Fig7 | figures | 5 Oct 2026 | Drive: Intelligent Data Logger / Figs | For the slides |
| S15 | Public offline dashboard | operating | Oct 2026 | engr-daniel.github.io/intelligent-data-logger-demo/dashboard/ | No API calls |
| S16 | Literature matrix | dataset | 14 Sep 2026 | Drive: Datalogger_Intelligence_Literature_Matrix.xlsx | **Not read this session** |
| S17 | Paper proposal, working draft | doc | 14 Aug 2026 | Drive: Paper Proposal working Draft.pdf | **Not read this session** |

## Claims

| ID | Claim | Status | Source(s) | Edition(s) | Stage(s) |
|---|---|---|---|---|---|
| C01 | A reference implementation exists: telemetry store, schema, physical validation, deterministic analytics, 14 tools, evidence receipts, offline and Claude modes | operating (synthetic) | S01, S06 | petgrave-idl | 1, 3 |
| C02 | No field data has been collected and nothing runs on an edge device | reported | S03, S04, S09 | both | 1, 3, 4 |
| C03 | Each answer carries an evidence receipt: finding, cause, confidence, data window, measurements, alternatives, data quality, assumptions, tools | operating (synthetic) | S01, S06 | both | 2, 4 |
| C04 | With clean data, full history + all components resolved 233/240 cases (97.1%; 95% cluster interval 95.4–98.8%). Inverter-only scored 53.8%, recent-only 40.0%, both restricted 20.0%. Severe corruption cut full access to 90.0%. | measured (synthetic) | S02, S03 | both | 2, 3 |
| C05 | The demo detected six fault types (weather drop, overload, PV decline, battery fade, data gap, grid outage), and declined to diagnose during the data gap | measured (synthetic) | S02 | both | 2, 4 |
| C06 | In the live pilot, the right tool was chosen 24/24 times; strict JSON 0/24 (every reply fenced); 24/24 labels after removing fences; citations valid 15/24; cost about USD 0.21 | measured | S08 | petgrave-idl | 2, 3, 4 |
| C07 | A public offline dashboard offers 120 days of synthetic charts and nine precomputed answers | operating | S15 | both | 5 |
| C08 | The ROI tool computes simple ROI and payback against the grid only. Avoided generator cost is `null`; ₦225/kWh is a demo value | operating (demo) | S01 | system-owner | 2, 4 |
| C09 | On the same 1,851 kWh, payback is 5.1 years against the grid and 0.9 years against a petrol generator (0.8 L/kWh, ₦1,596.25/L; an upper bound) | derived (synthetic) | S07 | system-owner | 2, 5 |
| C10 | CO₂ avoided in 120 days is 833 kg (placeholder 0.45 kg/kWh), 883 kg (sourced 0.477) or 3,481 kg (petrol generator) | derived (synthetic) | S07 | both | 2, 6 |
| C11 | The demo system exported 2,668 of 4,519 kWh (59%) with no payment | measured (synthetic) | S07 | system-owner | 4 |
| C12 | The paper is a methodology; a field-acquisition workflow is proposed, mapping inverter interfaces, battery monitoring, meters, sensors and records (Fig 7) | designed | S03, S04, S14 | petgrave-idl | 1, 4 |
| C13 | The August intent was to turn Datalodger into an intelligent layer, validate on real or representative data, and later extend to batteries, mini-grids, wind and buildings | designed | S05 | petgrave-idl | 1, 6 |
| C14 | At a radio station, Daniel managed solar, grid and generator energy. He recorded readings by hand and analysed them by hand to report ROI, solar contribution and energy consumption. | reported | S09 | system-owner | 1, 3, 4 |
| C15 | Installers in the survey said customers' maintenance and check-up habits are low | reported (counts unknown, Q03) | S09 | both | 1, 3 |
| C16 | Call-backs are common: 6 of 7 installers asked had 1–2 jobs a year needing a return visit | measured (small sample) | S10 | both | 1, 4 |
| C17 | Suny assumes most systems have no internet monitoring; it takes lifetime-kWh readings by meter photo, by hand or from a monitoring API | designed | S11 | both | 3, 4 |
| C18 | Suny flags a system producing under 85% of what the sun allowed over 14+ days | designed | S11 | petgrave-idl | 5 |
| C19 | About 87 million Nigerians lacked electricity in 2024. Nigeria imported 1,721 MW of panels in the year to June 2025, and installed capacity is not tracked. | sourced | S12 | petgrave-idl | 1 |
| C20 | Solar adoption by 700 small businesses was associated with 23–27% higher monthly earnings, and 36.6% lower energy spend for grid-plus-generator users | sourced | S12 | system-owner | 1 |
| C21 | No funding exists for the IDL now | reported | S09 | petgrave-idl | 1, 3 |
| C22 | Daniel leads the IDL; Fitzroy leads Suny | reported | S09 | petgrave-idl | 1 |
| C23 | Installer contacts from the Suny survey can be approached | reported | S09, S10 | both | 4, 5 |
| C24 | After NASEF, Petgrave.io will use this engagement to teach the Blueprint to business owners and leaders | reported | S09 | petgrave-idl | 5, 6 |

## Contradictions

| ID | Version A (source) | Version B (source) | Decision it affects | Resolved? |
|---|---|---|---|---|
| X01 | Validate on real or representative data and expert judgement, aiming at a Q1 contribution (S05, Aug) | A methodology with a synthetic worked evaluation; no field data (S03, S04, Oct) | What the NASEF talk claims | **Yes:** the talk claims a methodology (Daniel, 17 Oct). The Aug aim becomes the field phase. |
| X02 | "Datalodger" / "Datalodger Intelligence" (S05) | "Intelligent Data Logger" (S01, S03) | What audiences hear; whether a Datalodger product exists | No (Q04) |
| X03 | Field data comes from inverter interfaces, battery monitoring and meters (S03, Fig 7) | Most target systems have no internet monitoring; the counter on the inverter screen is often all there is (S11) | Pilot data design | No: I04 starts from manual and exported readings |
| X04 | ROI assumes solar displaced the grid (S01) | In Nigeria, solar often displaces a generator; payback 5.1 vs 0.9 years (S07) | Every ROI answer | No: I02 |
| X05 | Grid factor 0.45 kg/kWh, a placeholder (S01) | 0.477 kg/kWh, IFI harmonised factor for intermittent sources (S12) | Every carbon answer | No: I02 |
