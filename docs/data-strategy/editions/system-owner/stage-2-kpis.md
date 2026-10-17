# Stage 2: Data & KPI Mapping. System-owner edition

*How do we know our energy is working?* Status: ◐ provisional · Last updated: 17 Oct 2026

These are the questions an owner already asks, written as numbers the logger can answer. Each one names the decision it changes. "In the demo" means the answer exists today on synthetic data (C05, C08); none has been tested on a real system.

| ID | The question, in the owner's words | The number | The decision it changes | In the demo? |
|---|---|---|---|---|
| **O1** | "Is it working as it should?" | Energy made ÷ what the sun allowed on the same days, weekly | Call the installer, or wait | Yes (PV decline, weather vs. fault) |
| **O2** | "What is it saving us?" | ₦ not spent this month, **split into grid-on hours (tariff) and grid-off hours (generator fuel)** | Budget; whether to expand | Partly: the grid-only version (C08); the split is I02 |
| **O3** | "How much fuel did we not buy?" | Litres avoided during grid-off hours | Fuel purchasing | No (I02) |
| **O4** | "Is the battery getting weaker?" | Usable capacity trend | Plan a replacement before it fails on air | Yes (C05) |
| **O5** | "How long can we run tonight?" | Battery runway at the current load | Shed load or start the generator | Yes |
| **O6** | "How much of our power came from solar?" | Solar share of consumption | Shift loads to midday | Yes (74.6% in the demo) |
| **O7** | "What have we avoided for the environment?" | kg CO₂ avoided, with the factor and what was displaced shown | Sustainability report to management or partners | Yes, with the placeholder factor (X05) |

**North Star for an owner: O2, money saved, split by what it replaced.** It is the number management asks for, and it is the one the current model most often gets wrong (C09).

**The one to watch first: O1.** A system that is quietly failing makes every other number wrong.

**Removed by the vanity test:**
- *Total kWh generated:* it always rises and changes no decision.
- *Instantaneous power on the app:* it describes this minute, not the month.

**Data gaps:**
- generator hours and fuel bought are not recorded by the inverter (they stay manual, or need a sensor);
- the tariff band and the date it changed;
- what the installer found when they came.

**Done checks:** [x] every block has a measure · [ ] agreed with real owners · [x] vanity removed · [x] gaps documented

**The question this raises next.** Is a typical owner able to collect and act on these numbers today?
