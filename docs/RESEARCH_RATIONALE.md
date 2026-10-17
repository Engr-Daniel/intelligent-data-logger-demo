# Why build the Intelligent Data Logger? Research and product rationale

*Prepared 17 October 2026 · Daniel Oyewola Oyewale, with Claude · Status: rationale for decision, before any field deployment*

This document answers one question before more is built: **is this project worth doing?** It asks what problem the system solves, whether that problem is real, whether it is important, and whether solving it could speed up solar adoption. It also says what we do not yet know, and what evidence would prove us wrong.

Every claim carries one of four labels:

| Label | Meaning |
|---|---|
| **Built** | Runs in this repository today, and is covered by tests or archived runs |
| **Sourced** | Taken from a published external source, listed in [Sources](#sources) |
| **Assumption** | A value or belief we chose, not yet tested |
| **Unknown** | Nobody has measured it yet; we say what would measure it |

All telemetry in this repository is synthetic. Nothing here is a field result.

---

## 1. The short answer

The obvious problem statement is "solar owners lack data". That is not quite true. Most modern hybrid inverters already record power, battery and grid readings, and many ship with a vendor app.

**The real problem is that the data does not turn into answers that an owner, installer or financier can act on, check, or trust.** Four questions go unanswered:

1. **Is my system working as it should?** If not, why, and whose problem is it?
2. **What is it saving me?** That means money, and payback against what I would otherwise have spent.
3. **What has it avoided?** That means fuel burned and CO₂ released, as a record someone else could check.
4. **Can a stranger believe any of this?** That includes a new customer, a lender or a programme.

The Intelligent Data Logger is a conversational layer over solar, inverter, battery, load, grid and weather telemetry. It answers these questions in plain language, with an **evidence receipt** for each answer: the measurements, the time window, the assumptions and the alternative explanations.

Our own benchmark supports the core idea. Diagnosis depends on **history across components**, not on a snapshot from one device:

| Information available to the same diagnostic policy | Correct diagnosis, identifiable cases |
|---|---:|
| Full history + all components | **97.1%** (233/240; 95% cluster interval 95.4–98.8%) |
| Full history + inverter only | 53.8% |
| Last 24 hours + all components | 40.0% |
| Last 24 hours + inverter only | 20.0% |

*Built.* These figures come from 24 synthetic installations, 288 episodes and 3,456 paired predictions ([RESULTS.md](../RESULTS.md)). A typical vendor app shows something close to the bottom row: recent readings from one device. Because the data is synthetic, this shows the mechanism, not field accuracy.

---

## 2. What problem are we solving, and for whom?

| Who | The decision they face | What is missing today |
|---|---|---|
| **System owner** (household or small business) | Is it working? Was it worth it? Should I add battery, add panels or change my habits? | Readings without meaning. Savings and payback are guessed, not computed. A fault shows up only when the lights go off. |
| **Installer** | Which site needs a visit? Was it my installation or the customer's load? How do I prove my work to the next customer? | No remote, evidenced diagnosis. Disputes are word against word. Proof of good work stays private. |
| **Financier, programme or regulator** | Is the asset performing? Will the loan be repaid? What did this programme actually avoid? | Little independent performance data after installation. Impact claims rest on sizing assumptions, not measurement. |

The project's working hypothesis: *if each of these people could ask a plain question and get an answer they can check, systems would fail less silently, savings would be visible, and trust in solar would grow faster than it does by word of mouth alone.*

---

## 3. Is it a real problem?

### Nigeria is adopting solar fast, and mostly without oversight

- **Nigeria has the largest population without electricity in the world:** about 87 million people in 2024, according to the 2026 *Tracking SDG7* report. *(Sourced [1])*
- **Self-generation is enormous.** The Power Minister cited a 2023 study putting spending on diesel, petrol, generators and servicing at ₦16.5 trillion. Separate estimates differ by a factor of two or more and use different scopes, so we use this only to show scale. *(Sourced, with that caveat [2])*
- **Solar is arriving at speed.** Nigeria imported 1,721 MW of Chinese solar panels in the 12 months to June 2025. That made it Africa's second-largest importer. Ember notes there is no data on how many of those panels have been installed. *(Sourced [3])*

The third point matters most. Gigawatts of solar are going onto Nigerian roofs, mostly through small installers. Nobody systematically records how those systems perform after installation.

### Installed solar often fails or underperforms, and nobody notices in time

- A West Africa quality-assurance framework for public-facility solar (Schatz Energy Research Center with ECREEE, via Lighting Global) says failures have historically come from poor design and installation, or lack of maintenance. It proposes **remote monitoring** as part of the fix. *(Sourced [4])*
- A SolarAid survey of 24 rural health facilities in Malawi reported that 87.5% had solar systems that had failed or were underperforming, mostly due to battery failure. The sample is small, and we have not been able to check the figure in the original report, so it is indicative only. *(Sourced as reported [5])*
- A Nigerian study observed that PV systems do not reach their expected 10–25-year life without good maintenance. *(Sourced [6])*

We have **no measured Nigerian figure** for the share of rooftop systems that underperform, or for how long faults go unnoticed. *(Unknown.)* Measuring it is one of the first things a field deployment should do (Section 9).

### What this system has already shown it can detect

On synthetic data, the system detected and explained six fault types, each with an evidence receipt ([RESULTS.md](../RESULTS.md)). *(Built)*

| Fault | Evidence in the receipt |
|---|---|
| Weather vs. equipment | A 61.0% PV drop matched a 62.1% irradiance drop, so the cause was weather, not a fault |
| Overload | Peak load 6,404 W against a 5,000 W inverter, for 40 minutes before the alarm. This is technical evidence, not proof the customer was responsible. |
| Gradual PV decline | Performance ratio fell from 0.965 to 0.888 (an 8.0% decline) |
| Battery fade | Estimated usable capacity fell from 9.0 kWh to 8.49 kWh (5.66%) |
| Missing data | A 45-minute gap was found, and the system **declined to diagnose** rather than guess |
| Grid outage | A 60-minute outage was carried by the battery, with no unmet load |

Weather vs. equipment and overload are the two questions that settle disputes between owners and installers. Gradual decline and battery fade are slow faults that no owner sees until it is too late.

**So yes, the problem is real.** Adoption is fast and largely unmonitored. Failures are common and often silent. The technology to explain them from data exists in this repository, at least in simulation.

---

## 4. Is it an important problem? What makes it important?

A problem can be real but small. Five things make this one large.

1. **The money at stake is large for each owner.** The demo system is 6.6 kWp of PV, a 5 kW inverter and a 10 kWh battery, configured at ₦6.5 million. For a household or small business, that is one of its largest purchases. A system that silently loses 8% a year, or a battery fading early, erodes that investment unseen. *(Assumption: the demo price. Suny's sourced price tiers would be a better reference [7].)*
2. **Savings change livelihoods, not just bills.** A 2024 *Energy Policy* study of 700 small businesses in Lagos, Kano and Ondo associated solar adoption with **23–27% higher monthly earnings**. Businesses on grid plus generator cut energy spending by **36.6%**. If systems underperform, those gains are not realised. *(Sourced [8])*
3. **Trust is the adoption bottleneck, and failures destroy it.** In the Suny installer research, only 2 of 12 surveyed installers get most of their work other than by referral. Of 9 completed jobs coded in interviews, none could be confirmed as having evidence a stranger could check. *(Reported research, small samples [9])* Solar spreads by people believing their neighbours. One failed system that nobody can explain teaches a whole street that solar is a gamble.
4. **The climate case depends on solar actually displacing fuel.** Every litre of petrol not burned avoids 2.35 kg of CO₂. *(Sourced [10])* A panel that is installed but failing avoids nothing, while the generator quietly comes back.
5. **There is a measurement gap at the national level.** Imports are counted, but installed, working capacity is not (Section 3). Programmes, lenders and policymakers have to plan with very little information about what was installed and whether it works.

---

## 5. ROI: knowing what the installed system is worth

### What the system does today *(Built)*

An owner can type **"What's our ROI so far?"** (a suggested question on the dashboard). The system calls `get_financial_summary` ([src/analytics/financial.py](../src/analytics/financial.py)) and returns:

- avoided energy cost and net savings;
- simple ROI to date;
- annualised savings and simple payback;
- an assumptions receipt: tariff, capital cost, maintenance, period, and the payback method ("no discount rate or financing effects").

On the 120-day synthetic dataset, the answer is:

| Output | Value |
|---|---:|
| Solar energy used on site | 1,851 kWh |
| Avoided cost at ₦225/kWh | ₦416,572 |
| Simple ROI to date | 6.41% |
| Annualised savings | ₦1,267,072 / year |
| Simple payback | **5.1 years** |

### The less obvious finding: ROI depends on what the solar replaced

The current calculation assumes solar replaced **grid electricity only** (`counterfactual: grid_displacement`). The configured avoided generator cost is `null`. In Nigeria, much of the time, solar actually replaces a **petrol or diesel generator**, because the grid is off.

We re-ran the same 1,851 kWh with Suny's sourced factors [7][10][11]:

| What the solar replaced | Saving over 120 days | Annualised | Simple payback |
|---|---:|---:|---:|
| Grid only, at ₦225/kWh (current model) | ₦416,572 | ₦1.27 m | **5.1 years** |
| Petrol generator only, 0.8 L/kWh at ₦1,596.25/L (1,481 L) | ₦2,364,276 | ₦7.19 m | **0.9 years** |

The same system, with the same readings, has a payback somewhere between **under a year and five years**. That depends entirely on a question the current model never asks.

The petrol row is an upper bound. It assumes every self-consumed kWh replaced generator power, and it ignores generator purchase and servicing. The true answer lies between the two rows. It **can be measured**, because the logger already records when grid supply is present. Solar used during grid-off hours displaced the generator, or loss of service. Solar used during grid-on hours displaced the tariff.

### Value is also leaking from the demo system

Over the 120 days, the demo exported **2,668 of 4,519 kWh generated (59%)** to the grid. The configuration pays nothing for exports (`export_treatment: no_compensation`). *(Built, synthetic)* In a real system, that would prompt questions: is the battery strategy right, should loads move to midday, or was the array oversized? A logger that shows "you are giving away more than half your solar for free" changes a decision. That is the test the Blueprint applies to any metric.

### What ROI needs before it can be trusted *(not yet built)*

1. **Split the counterfactual:** grid-on vs. grid-off hours, with the generator type and fuel price recorded and dated.
2. **Use a sourced tariff band.** The ₦225/kWh tariff is a demo configuration value, not checked against the current NERC order.
3. **Use full lifetime economics:** 0.5%/year panel degradation [7], battery replacement, discounting and financing cost.
4. **Track live maintenance cost**, which is currently zero in the configuration.

---

## 6. Carbon: environmental sustainability records you can ask for

### What the system does today *(Built)*

An owner can ask **"How much carbon have we avoided?"** The system calls `get_sustainability_summary` ([src/analytics/sustainability.py](../src/analytics/sustainability.py)) and returns:

- avoided emissions;
- renewable fraction;
- solar energy used on site;
- the emission factor, its source and year, and the counterfactual it assumed.

Each answer carries a receipt and can be exported with the session as JSON with provenance hashes. That makes it a **record**, not just a number on a screen.

On the demo data: **833 kg CO₂e avoided in 120 days**, with 74.6% of consumption met by solar.

### The same counterfactual issue, larger

The demo uses a placeholder grid factor of 0.45 kg/kWh, labelled `synthetic_demo_assumption`. With sourced factors:

| What the solar replaced | CO₂ avoided, 120 days | Annualised |
|---|---:|---:|
| Placeholder grid factor, 0.45 kg/kWh (current) | 833 kg | — |
| Nigerian grid, 0.477 kg/kWh (IFI harmonised factor for intermittent sources [10]) | 883 kg | ≈ 2.7 t |
| Petrol generator, 1,481 L × 2.35 kg/L [10][11] | 3,481 kg | ≈ 10.6 t |

Once again, the answer changes **about fourfold** depending on what was displaced. A sustainability record is only as good as its counterfactual. That is why the logger, which can see when the grid was off, is better placed to report it than a sizing spreadsheet.

### What would make these records credible *(not yet built)*

- Replace the placeholder with the sourced Nigerian factor, and make the counterfactual measured rather than assumed (Section 5).
- Follow a conservative rule: when sources disagree, use the value that makes the claim **smaller**. Suny's research notes adopt the same rule [7].
- Keep records tamper-evident and aggregated across many systems. Programme reporting, ESG disclosure or any future carbon-credit methodology would need this.

**We make no claim that these records qualify for carbon credits today.** Qualifying requires an approved methodology, metering standards and independent verification, none of which this project has.

---

## 7. Will it speed up solar adoption?

Honestly: **possibly, through four specific mechanisms. None of them has been tested yet.** Each is listed with the evidence that would confirm it or overturn it.

| Mechanism | Why it could work | What would test it |
|---|---|---|
| **1. Proof a stranger can check** | Adoption runs on referrals, and referrals rest on private proof (Section 4, point 3). A shareable record ("this system has saved ₦X and avoided Y kg CO₂ over Z months, and here are the readings") turns one owner's experience into evidence for the next buyer. | Do prospective buyers who see a verified performance record convert more often than those who hear a referral alone? |
| **2. Fewer silent failures** | Early detection of decline, battery fade and overload keeps systems working. Working systems protect solar's reputation. | Time from fault onset to detection, and to repair, on monitored vs. unmonitored sites |
| **3. Visible economics** | If payback measured against the generator is under two years, that should be shown to every undecided buyer, with real numbers. | Do owners who see their measured payback recommend solar more, or expand their system? |
| **4. Lower risk for lenders and pay-as-you-go** | Performance data could lower the risk of financing solar. Monitoring vendors and UNDP-listed platforms argue this. | Would a lender change terms with performance data? **We found no independent evidence that it lowers financing cost** [12]. This is the weakest link. |

### The case against, stated plainly

- **Vendor apps already exist.** Our answer is that they show readings, not explained, cross-component, historical diagnosis with receipts (Section 1 table). But owners may decide the free app is "good enough".
- **Cost and connectivity.** A logger, a SIM or Wi-Fi link and the AI calls cost money. The live pilot cost about USD 0.21 for 24 conversations (Built). Hardware and connectivity costs in the field are unknown.
- **Output format.** In the live pilot, strict JSON compliance was 0/24, because every reply was wrapped in a Markdown fence. After removing the fences, receipt labels matched 24/24, but only 15/24 replies cited valid measurement names. The model sometimes overreached in its prose. Trustworthy answers need more work.
- **Privacy.** Energy data reveals when people are home. Any shared record must aggregate, and consent must be explicit.

---

## 8. So, is it worth it?

**Yes, as a staged research project with a field test as the next step, provided we keep three conditions:**

1. **Measure before claiming.** Every ROI, carbon or adoption claim stays labelled until field data confirms it.
2. **Fix the counterfactual first.** It is cheap, and it changes the answers by four to six times. It is the single most valuable improvement to ROI and carbon reporting.
3. **Stop or change course if the field test shows:**
   - owners do not ask or act on the answers;
   - faults are already caught quickly without the system;
   - field accuracy falls far below the synthetic benchmark.

The question this raises next: **which real installations, owners and installers will host the first field test, and what will each of them decide differently because of it?**

---

## 9. Open research questions and what to measure first

| # | Question | Measure | Status |
|---|---|---|---|
| R1 | How often do Nigerian rooftop systems underperform, and for how long unnoticed? | Share of sites below 85% of expected yield over 14+ days; days from onset to detection | Unknown |
| R2 | What share of solar energy displaces generator vs. grid? | Self-consumed kWh during grid-off vs. grid-on hours, per site | Unknown, and measurable with the current schema |
| R3 | Does field diagnosis accuracy approach the synthetic 97.1%? | Agreement with installer-confirmed root causes | Unknown |
| R4 | Do owners act on the answers? | Questions asked per month; actions taken (load shift, repair, expansion) | Unknown |
| R5 | Does a verified record help sell the next system? | Conversion of prospects shown a record vs. not | Unknown |
| R6 | Does performance data change financing terms? | Lender interviews, then one pilot | Unknown, weakest evidence |

---

## 10. Limitations of this rationale

- All system results are synthetic. The field acquisition plan is in [paper/](../paper/README.md).
- National figures on self-generation spending vary widely. We use them only to show scale.
- Failure-rate evidence comes from small samples outside Nigeria. Nigerian rooftop data does not exist yet.
- The petrol-displacement figures are an upper bound (Section 5).
- The adoption mechanisms are hypotheses, not findings.

---

## Sources

1. IEA, IRENA, UNSD, World Bank, WHO, *Tracking SDG 7: The Energy Progress Report 2026*, as summarised in "SDG 7 progress slows as global energy access gaps and funding challenges deepen", SolarQuarter, 25 June 2026. https://solarquarter.com/2026/06/25/sdg-7-progress-slows-as-global-energy-access-gaps-and-funding-challenges-deepen-report/amp/ ; see also "Nigeria now has largest population without electricity globally", Africa Sustainability Matters. https://africasustainabilitymatters.com/nigeria-now-has-largest-population-without-electricity-globally/ (accessed 17 Oct 2026).
2. "Nigerians spend N16.5trn on diesel, petrol, generators for self-generated power in 2023 — report", Prime Business Africa. https://primebusiness.africa/?p=129105 ; "Nigerians spend $10 billion annually on petrol, generator maintenance", The Guardian (via IPP Media), Oct 2024. https://ippmedia.com/the-guardian/business/read/nigerians-spend-10-billion-annually-on-petrol-generator-maintenance-2024-10-12-043805 (accessed 17 Oct 2026).
3. Ember, "Africa's solar imports surge 60%, giving the first evidence of a take-off in solar in Africa", 26 Aug 2025. https://ember-energy.org/latest-updates/africas-solar-imports-surge-60-giving-the-first-evidence-of-a-take-off-in-solar-in-africa/ (accessed 17 Oct 2026).
4. Lighting Global / Schatz Energy Research Center and ECREEE, *A Quality Assurance Framework for Solar System Installations at Public Facilities in West Africa*. https://www.lightingglobal.org/quality-assurance-framework-solar-system-installations-public-facilities-west-africa/ (accessed 17 Oct 2026).
5. SolarAid, *Powering Healthcare: Malawi* (mini report, March 2022). https://solar-aid.org/wp-content/uploads/2022/04/Powering-Healthcare-Malawi-March-2022.pdf . Figures as reported in search summaries; not checked against the report text.
6. Adetona et al. (2020), study of PV system maintenance in Nigeria, *European Journal of Engineering and Technology Research* 5(11). https://econpapers.repec.org/RePEc:epw:ejeng0:v:5:y:2020:i:11:id:62233 (accessed 17 Oct 2026).
7. Suny research notes, `docs/research/` in https://github.com/sunyenergy/suny : 04 (performance ratio 0.75, degradation 0.5%/yr) and 05 (petrol ₦1,596.25/L, NBS May 2026; NERC bands), researched 7 Oct 2026.
8. Owusu-Sekyere, E., Cissé, F. N., & Achandi, E. L. (2024). Impact of solar energy subscription on the market performance of micro, small & medium enterprises in Nigeria. *Energy Policy*, 188, 114063. https://doi.org/10.1016/j.enpol.2024.114063
9. Suny data strategy, admin edition (14 Oct 2026): installer survey n = 12 (two internal tests excluded); 7 interviews, 22 requests. https://github.com/sunyenergy/suny/tree/main/docs/data-strategy
10. Suny research note 01, emission factors: US EPA (petrol 2.35 kg CO₂/L, diesel 2.69 kg CO₂/L); IFI Technical Working Group, *Harmonised Grid Emission Factor dataset v2.0* (2019), Nigeria intermittent 0.477 kg CO₂/kWh. https://unfccc.int/sites/default/files/resource/Harmonized_Grid_Emission_factor_data_set.pdf
11. Suny research note 02, generator fuel use: petrol 0.8 L/kWh (Honda EU2200i specifications; Zaichenko et al. 2022), diesel 0.35 L/kWh, adopted as conservative.
12. UNDP Digital X, REMOT remote-monitoring platform listing. https://digitalx.undp.org/remot_1.html ; Dauenhauer et al., "Remote monitoring of off-grid renewable energy: case studies", IEEE GHTC 2013. https://strathprints.strath.ac.uk/56102/ . Neither quantifies an effect on financing cost.

Repository evidence: [RESULTS.md](../RESULTS.md), [reports/research/](../reports/research/README.md), [config/installation.yaml](../config/installation.yaml), [src/analytics/financial.py](../src/analytics/financial.py), [src/analytics/sustainability.py](../src/analytics/sustainability.py).
