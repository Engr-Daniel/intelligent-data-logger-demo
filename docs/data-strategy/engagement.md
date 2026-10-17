# Engagement: Intelligent Data Logger (Petgrave.io Technologies)

*Prepared with the Petgrave.io™ Data Strategy Blueprint · Started 17 October 2026 · Facilitator: Claude (Blueprint skills), with Daniel Oyewale*

## Framing

- **Subject:** the Intelligent Data Logger (IDL). It is a conversational layer over solar PV, inverter, battery, load, grid and weather data. It analyses the data, answers questions in plain language, and shows the evidence behind each answer. **Stage:** building. A reference implementation and a synthetic evaluation exist; no field deployment, no edge device and no funding yet (C01, C02, C21).
- **Use-case playbooks:**
  - `research-innovation` (primary): the NASEF 2026 paper, positioned as a methodology;
  - `ai-integration`: Claude chooses tools and explains results, while deterministic analytics do the engineering.
- **Decisions this informs:**
  1. How the NASEF 2026 paper presentation is arranged (Wednesday 21 October 2026).
  2. What to build and test next, with no funding: which field pilot, which data, which installers.
  3. How Petgrave.io teaches the Blueprint to business owners and leaders after the conference, using this engagement as the worked example.
- **Division of work:** Daniel leads the IDL; Fitzroy leads Suny (C22).

## People

| Name | Role | Knows about | Edition(s) |
|---|---|---|---|
| Daniel Oyewale | IDL lead; corresponding author; ran manual energy records at a radio station (solar, grid, generator) | The paper, the code, the installer survey, the owner's reality | both |
| Fitzroy Meyer-Petgrave | Founder; co-author; leads Suny | Business model, partners, Suny's installed-system data | petgrave-idl |
| *(installers from the Suny survey)* | Contacts who could host a pilot | What they find on call-backs; which inverters their customers have | system-owner (via pilot) |
| *(system owners, to be recruited)* | Households, small businesses, institutions | Their energy decisions | system-owner |

## Editions

| Slug | Audience | The decisions they make | Owner |
|---|---|---|---|
| `petgrave-idl` | The Petgrave.io team running the IDL research and product | What to present · what to build next · which pilot · which data to collect · when the IDL is ready to show owners or installers · how to teach with it | Daniel |
| `system-owner` | People responsible for a solar system's energy: an owner, or an energy manager at a business or institution. The worked case is a radio station running solar, grid and generator. | Is it working? When to call the installer · what to buy (fuel, battery) · when to shift loads · what to report to management on ROI, solar contribution and sustainability | Daniel |
| `installer` *(planned)* | Installers who would act on remote diagnoses | Which site to visit · how to settle "your equipment vs. your load" · how to prove work | — |

## Stage status

✓ done · ◐ provisional · ⚠ needs rework · ○ not started

| Edition | 1 Model | 2 KPIs | 3 Maturity | 4 Lifecycle | 5 Value | 6 Vision | Compiled |
|---|---|---|---|---|---|---|---|
| petgrave-idl | ◐ | ◐ (RQ1–RQ6 · M01–M08) | ◐ (P&C 2 · Proc 1 · Tech 2 · Gov 2 · S&I 1) | ◐ (real installation → checked answer) | ◐ (I01–I06 + screen) | ◐ | ◐ |
| system-owner | ◐ (radio-station case) | ◐ (O1–O7) | ◐ (L1; constraint: Processes) | ◐ (the manual logbook) | ◐ (I07) | ◐ | ◐ |
| installer | ○ | ○ | ○ | ○ | ○ | ○ | ○ |

Everything is provisional. The owner edition rests on one reported case (S09) and small installer samples (S10). It must be checked with 2–3 real owners.

## What we found (lead with this)

1. **The problem is not storing data. It is that a person still has to read it, write it down and work it out.** At the radio station, Daniel recorded solar, grid and generator readings by hand, then analysed them by hand to report ROI, solar contribution and consumption (C14). Suny's own code assumes most systems have no internet monitoring, so it collects lifetime-kWh readings by meter photo or by hand (C17). Logging exists; answering does not.
2. **The constraint is labelled outcomes, not the AI and not the hardware.** On synthetic data, full history plus all components gave 233 of 240 correct diagnoses (C04). In the field, we could not tell whether a diagnosis was right: nobody records what an installer actually found when they go back. 6 of 7 installers asked had 1–2 jobs a year needing a return visit (C16). **Those visits are the cheapest ground truth available.** The first thing to collect is the installer's finding, not more telemetry.
3. **ROI and carbon depend on one question the model never asks: was the grid on?** With the same 1,851 kWh of solar used on site, simple payback is 5.1 years if solar replaced the grid, and 0.9 years if it replaced a petrol generator. CO₂ avoided is 883 kg vs. 3,481 kg over 120 days (C09, C10). The logger already records grid presence.
4. **The conversational layer is the weakest operating part.** Strict output-contract compliance was 0/24; citations were valid in 15/24 (C06). The deterministic engine is strong; the reply format and prose fidelity are not yet.

## Run plan

1. **Intake** ✓ (17 Oct): sources S01–S17, claims C01–C24, contradictions X01–X05.
2. ◐ **petgrave-idl, Stages 1–6**, from the repo, the paper and the Drive folder.
3. ◐ **system-owner, Stages 1–6**, from the radio-station case (reported) and the installer research. Check with 2–3 owners.
4. **Instruments, ready to send:** `instruments/pack-installers-2026-10-17.md` (WhatsApp, 10 min) and `instruments/field-pilot-data-spec.md`.
5. **Compile** both editions, plus the NASEF slide plan (`../../paper/presentation/`) and teaching notes (`teaching-notes.md`).
6. **After NASEF:** send the installer pack; run `blueprint-evidence` on the answers; start the `installer` edition if 3+ installers agree to host.

## Change log

| Date | Who | What changed | Why |
|---|---|---|---|
| 2026-10-17 | Claude (intake) | Workspace created in the repo at Daniel's request. Read the repo, the paper and abstract, the Drive folder (executive summary, Sep technical deck, figure list), the rationale, the Blueprint skills, and Suny's installer research and code. | Start of the engagement; NASEF on 21 Oct |
| 2026-10-17 | Claude (stages 1–6, compile) | Drafted both editions to ◐, the questions, two instruments, the figures, compiled strategies, the slide plan and teaching notes. | Daniel: start the work before NASEF; use it to arrange the slides and to teach the Blueprint |
