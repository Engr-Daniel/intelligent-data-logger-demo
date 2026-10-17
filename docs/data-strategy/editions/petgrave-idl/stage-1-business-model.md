# Stage 1: Business Model Mapping. Petgrave.io IDL edition

*How does the IDL programme really work today?* Status: ◐ provisional · Last updated: 17 Oct 2026

The IDL is a research and innovation programme with a product inside it, so this canvas is a **value model** (research-innovation playbook). "Revenue" means the resources that keep it going.

> **The thing to see first.** In August the plan was a product: turn a data logger into an intelligent layer (C13). In October the deliverable is a method: a way to build and test such a layer honestly (C12). That is not a retreat. It is the only claim the evidence supports today, and it is the claim that can earn the field data the product needs.

| Block | As-is today | Evidence | Who would disagree? |
|---|---|---|---|
| **Customer segments** | *Now:* the NASEF research community (reviewers, engineers, academics). *Next:* installers, who act on diagnoses, and system owners and energy managers, who ask the questions. *Later:* programmes and financiers who need performance evidence. | C04, C12, C19 | — |
| **Value proposition** | *Research:* a reproducible method that keeps an AI's answers tied to engineering evidence, and an honest worked evaluation. *Product (designed):* "ask your solar system a question and get an answer you can check" | C03, C04, C12 | Users may want answers, not methods |
| **Channels** | The paper and talk (NASEF, 21 Oct); the public offline dashboard; this GitHub repository; the Suny installer network | C07, C23 | — |
| **Relationships** | Peer review now. With owners and installers, none yet: no field user has used the IDL. | C02 | — |
| **Revenue streams** | **None.** No funding (C21). Petgrave.io carries the work. Model cost is small (about USD 0.21 for 24 conversations, C06). | C06, C21 | — |
| **Key resources** | The reference implementation and test suite · the frozen protocol and archives · Daniel's energy-management experience · the installer contacts · Claude | C01, C14, C23 | — |
| **Key activities** | Building and testing the method on synthetic data · writing and presenting · *(not yet)* collecting field data · *(not yet)* recording what installers find | C01, C02 | — |
| **Key partnerships** | Anthropic (model) · installers from the Suny survey (potential pilot hosts) · Suny (overlap: it already takes meter readings and flags underperformance) · NASEF | C17, C18, C23 | — |
| **Cost structure** | People's time (dominant) · small model costs · no hardware spend yet. A field pilot adds connectivity, travel and possibly loggers. | C06, C21 | — |

**What has changed since August (X01):** the claim moved from validation to methodology. The executive summary's aims (real data, expert judgement, other energy systems) are now the field phase and later horizons, not this paper.

**Disagreements surfaced:** the name, "Datalodger" vs. "Intelligent Data Logger" (X02, Q04). The paper's field workflow assumes device interfaces; Suny's code assumes most systems have none (X03).

**Done checks:** [x] one picture · [x] a visual reference (this table, the Fig 7 architecture) · [x] every block evidenced or marked unknown

**The question this raises next.** Which few numbers would tell us the IDL is working, in research terms and for the people it is meant to serve?
