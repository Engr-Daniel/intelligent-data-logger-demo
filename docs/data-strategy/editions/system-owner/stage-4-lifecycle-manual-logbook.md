# Stage 4: Data Lifecycle Mapping. System-owner edition

**Flow: the monthly energy report, as it happened at the radio station** (C14, reported). Status: ◐ provisional. Walk the same flow with 2–3 owners and mark each row confirmed, revised or broken.

| Stage | What happens today | Who | Tools | Gap | With the IDL (designed) |
|---|---|---|---|---|---|
| **Capture** | Someone reads the inverter, the meter and the generator hour counter, and writes them down | The energy manager | Eyes, notebook | **G11:** readings are missed when the person is busy; the fault between readings is invisible | The logger records every few minutes, across all components |
| **Store** | Notebook, then a spreadsheet | The energy manager | Excel | The record lives with one person | One store with a schema |
| **Prepare** | Re-typing; fixing missing days; matching generator hours to fuel receipts | The energy manager | Excel | **G12:** hours of manual work; errors in re-typing | Validation; gaps shown as gaps |
| **Analyse** | Working out solar contribution, consumption and ROI by hand | The energy manager | Excel formulas | **G13:** ROI depends on assumptions nobody writes down | Tools with an assumptions receipt (O2 split: I02) |
| **Visualise** | A report for management | The energy manager | Word, slides | Monthly at best | Ask in plain language, any day |
| **Act** | Buy fuel; call the installer when something fails | Management, the installer | Phone | **G14:** action comes after the failure, not before (C15) | O1 and O4 warn early |
| **Learn** | Rarely. Last month's lessons are not compared with this month's. | — | — | **G15:** no loop | The record and the installer's findings stay together (I01) |

**The highest-impact gap: G14, acting after the failure.** For a radio station, a failure means dead air. G11 (capture depends on a person) is its root cause.

**Done checks:** [x] the flow is visible end to end · [x] the breaks are identified · [ ] owners agree · [x] shortlist

**The question this raises next.** What would an owner actually want built, and would they notice if it disappeared?
