# NASEF 2026 paper presentation: slide plan and template

*Draft of 17 October 2026 · For Daniel Oyewale (presenter) and Fitzroy Meyer-Petgrave · Talk on Wednesday 21 October*

**Paper:** *A reproducible methodology for evidence-grounded conversational diagnostics of solar PV–battery systems: implementation and synthetic evaluation.*

**Template deck:** [NASEF2026_IDL_slide_template.pptx](NASEF2026_IDL_slide_template.pptx). Each slide carries its working title, layout, placeholders and speaker notes. Build on that file.

## The storyline

The talk follows the line Daniel set out: **a problem we noticed → a solution → how it works → how we built and tested it → a demo → what it does and doesn't show → what's next.** The data strategy ([docs/data-strategy/](../../docs/data-strategy/README.md)) shaped four choices:

1. **Open with a case, not the architecture** (Blueprint rule 3). The radio-station logbook makes the problem concrete before any diagram appears.
2. **State the solution as an outcome before naming the AI** (Stage 5 safety check). Say "answers you can check" first and "Claude" later.
3. **Put the limits on their own slide** (Stage 6 boundaries). The audience should hear the boundaries from us before they raise them.
4. **End with the next step as a request.** There is no funding; we need installers and pilot sites, and the room may include them.

**Title style:** every slide title is a full-sentence takeaway, not a topic. Write "History across components is what makes diagnosis work", not "Results".

## Timing

The slot length is not yet confirmed (Q01). This plan assumes **15 minutes of talk** and runs 14 main slides plus backups. For a **10-minute slot**, use the cuts marked ✂.

| # | Section | Working title (the takeaway) | Layout | Content and figures | Time |
|---|---|---|---|---|---|
| 1 | Opening | *(paper title)* | **Title**: dark background; title, authors, affiliation, NASEF 2026; demo link and QR at bottom right | Petgrave.io logo; demo link | 0:20 |
| 2 | Problem | "The system already keeps a diary. Somebody still has to read it." | **Story**: half-slide image on the left (a logbook photo, or a drawing of a notebook beside an inverter screen); three short lines on the right | Radio station: solar, grid and generator, read by hand, analysed by hand for ROI, solar share and consumption. *Needs Q02.* | 1:00 |
| 3 | Problem | "Solar is spreading fast; checking on it is not" | **Three stat cards** in a row, big numbers with small labels | 1,721 MW of panels imported in a year, with installed performance not tracked (Ember) · 6 of 7 installers had 1–2 return visits a year (Suny survey) · installers report low maintenance habits (n of N, Q03) | 1:00 |
| 4 | Problem ✂ | "Getting the answer wrong costs money, uptime and trust" | **Two columns**: left, the payback figure; right, three consequences | `payback.png`: 5.1 vs. 0.9 years from the same readings · faults found when the power goes off · one failure teaches a street that solar is a gamble | 1:00 |
| 5 | Solution | "Ask the system a question; get an answer you can check" | **Question → answer → receipt**: a speech bubble on the left, the answer in the middle, the evidence receipt card on the right | Dashboard screenshot. The receipt shows finding, data window, measurements, alternatives, assumptions. Mention Claude only in the notes. | 1:15 |
| 6 | How it works | "The model chooses tools and explains; engineering truth comes from deterministic analytics" | **Full-width diagram** | **Fig2** End-to-End Evidence-Grounded Workflow (Drive/Figs) | 1:15 |
| 7 | Method | "A method, not just a system: six separations keep the evaluation honest" | **Diagram left, six numbered steps right** | **Fig1** Evidence-Grounded Diagnostic Methodology. Steps: telemetry preparation · controlled access · deterministic tools · evidence receipts · conversational reporting · separate scoring against evaluation-only labels | 1:15 |
| 8 | Experiment | "We tested what each kind of access makes possible" | **2 × 2 grid** on the left (history × components); design numbers on the right | **Fig3** Information-Access Design · 24 evaluation installations (8 development, kept apart) · 12 episodes each · 3 stress levels · 3,456 paired predictions | 1:00 |
| 9 | Result | "History across components is what makes diagnosis work" | **Chart with one highlighted bar** and a one-line caption | `access.png` (or **Fig4**): 97.1% (233 of 240; 95.4–98.8%) vs. 53.8 / 40.0 / 20.0% | 1:00 |
| 10 | Result ✂ | "Under heavy corruption it degrades, and it says when it doesn't know" | **Chart on the left; abstention callout on the right** | **Fig5** robustness: 90.0% under severe corruption · restricted conditions abstain when evidence is insufficient | 0:45 |
| 11 | Result | "The conversational layer chose the right tool every time, and broke the output contract every time" | **Funnel of counts** (unit chart, 24 dots per row) | **Fig6**: tool 24/24 · strict JSON 0/24 · labels 24/24 after fence removal · valid citations 15/24 | 1:00 |
| 12 | Demo | "See it work: three questions" | **Full-bleed screen**, live or video | Live dashboard, or the recorded `IDL interface Record.mp4` as fallback. Q1: why did generation drop on 5 Aug? (weather vs. fault) · Q2: what's our ROI? (open the receipt and its assumptions) · Q3: what happened during the data gap? (it declines to diagnose) | 1:30 |
| 13 | Limits | "What this shows, and what it does not" | **Two columns**: "Shows" (solid) and "Does not show" (dashed outline) | Shows: a reproducible method, a reference implementation, a controlled evaluation. Does not show: field accuracy, generalisation beyond shared simulator–policy assumptions, live reliability. ROI and carbon currently assume grid displacement. | 1:00 |
| 14 | Next | "Next: three real sites, and installers who write down what they find" | **Diagram plus request**: Fig 7 on the left; the ask on the right | **Fig7** Field Data Acquisition · the pilot uses data that already exists (inverter counters, exports) · installer findings become the reference labels · **Ask:** installers and sites to host a pilot; contact details | 1:00 |
| 15 | Close | *"No answer without evidence; no claim without a field check."* | **Dark closing slide**: one line, contact, links, QR | Demo link · repository · daniel.oyewale@petgrave.io | 0:20 |

Total: about 15 minutes. With ✂ cuts and a 60-second demo video, about 10.5 minutes.

## Backup slides (for Q&A)

| B# | Likely question | Slide |
|---|---|---|
| B1 | "Why synthetic data?" | No field data or edge device yet; synthetic data gives known ground truth, disjoint seeds and a frozen protocol. That is the methodology claim. |
| B2 | "How do you know ROI or carbon?" | `payback.png` + `carbon.png`: the counterfactual split (grid on vs. off); sourced factors (0.477 kg/kWh grid; petrol 2.35 kg/L) |
| B3 | "How fast does it detect faults?" | Timing supplement (secondary, exploratory) |
| B4 | "Isn't this just the inverter's app?" | The access chart: an inverter-only view of the last day is the bottom bar (20.0%) |
| B5 | "Can I reproduce it?" | Commands from the README; frozen protocol; verification script |
| B6 | "What about privacy?" | Data rights from `links.md`: aggregate only, consent, no personal data in prompts |

## Visual rules (Petgrave.io brand)

- **Colour:** one deep blue `#1E2A44` plus white and cool greys (`#4A5878`, `#7E8AA3`, `#AEB6C6`, `#D5DAE3`, `#EEF0F3`). Meaning comes from strength:
  - solid = the point;
  - ash = present but secondary;
  - dashed outline = not yet, or unknown.
- **Type:** Calibri. Titles 32–36 pt, body 16–18 pt, captions 11–12 pt.
- **Layout:** one idea and one figure per slide. Number labels go on the figures, not in legends. No accent bars, no pie charts.
- **Numbers:** small samples as counts ("6 of 7"); synthetic results labelled "synthetic" on the slide.
- **Footer:** "Oyewale & Meyer-Petgrave · NASEF 2026 · Petgrave.io" and the slide number.

## Before Wednesday

- [ ] Q01: confirm the slot length and any organiser template.
- [ ] Q02: approve the radio-station story; add one or two real numbers if you have them.
- [ ] Q03: the installer maintenance count (n of N), or drop that card.
- [ ] Put Fig1–Fig7 from Drive/Figs into slides 6–8, 10, 11 and 14.
- [ ] Take a dashboard screenshot for slide 5. Test the live demo on the venue network; load the video as a fallback.
- [ ] Rehearse once against the clock; cut ✂ slides if over time.
