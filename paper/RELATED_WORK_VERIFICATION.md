# Related-work verification record — 28 September 2026

This is a targeted primary-source check, not a systematic literature review or an
exhaustive novelty search. Bibliographic identities and the specific claims used in
`FULL_PAPER.md` were checked against the following primary records. No claim is made
that the project is the first conversational solar diagnostic system.

| Ref. | Verified primary record | Claim supported | Boundary |
|---|---|---|---|
| 1 | [Sandia report, SAND2004-3535](https://www.osti.gov/biblio/919131), DOI 10.2172/919131 | PV modelling includes environmental/electrical/thermal effects and expected/measured comparisons | Our simplified simulator is not an implementation or validation of Sandia's model |
| 2 | [Holmgren et al., JOSS 3(29), 884, 2018](https://joss.theoj.org/papers/10.21105/joss.00884) | Reusable solar-energy modelling software exists | pvlib is related work, not a dependency or measured baseline in this experiment |
| 3 | [Jordan et al., IEEE JPV 8(2), 525–531, 2018](https://research-hub.nlr.gov/en/publications/robust-pv-degradation-methodology-and-application-2/) | Robust degradation analysis addresses confounders and uses year-over-year/clear-sky methods; 486-system study | Our synthetic 60-day signature is not an annual field degradation estimate |
| 4 | [Yao et al., ReAct, ICLR camera-ready version](https://arxiv.org/abs/2210.03629) | Language models can combine reasoning/actions and external information | Our forced two-request tool flow is not a reproduction of ReAct benchmarks |
| 5 | [Schick et al., Toolformer, arXiv:2302.04761](https://arxiv.org/abs/2302.04761) | Learned API selection/use is prior work | Our project does not train a tool-use model |
| 6 | [Geifman and El-Yaniv, NeurIPS 2017](https://papers.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html) | Reject-option performance trades off coverage | Our descriptive abstention metrics do not inherit risk guarantees |

The accessible abstracts/metadata support these bounded descriptions. No performance
number from these works is used as a competing result for this study. A domain expert
has not independently assessed the simulator or this manuscript. Do not describe
assistant-assisted checking as peer review, blinded annotation or external validation.

## Field-acquisition sources checked 30 September 2026

- [7] [SunSpec Information Model Reference](https://sunspec.org/sunspec-information-model-reference-sunspec-alliance/), SunSpec Alliance, 15 February 2018. The primary page identifies information models for inverters, batteries and meters. Supports using a compatible documented interface as a proposed source; it does not establish compatibility with any selected device or implementation in this repository.
- [8] [Sengupta et al., 2024, NREL/TP-5D00-88300](https://doi.org/10.2172/2448063), fourth-edition solar-resource handbook. Primary bibliographic record and indexed report passages confirm the title, editors, date and coverage of measurement practice and data quality. Cited as guidance for future sensor acquisition and quality assessment, not evidence that our simulator or prototype meets a monitoring standard.

The one-minute polling proposal, 15-minute field aggregation procedure, site recruitment
and field evaluation plan are author-proposed design choices. These references do not
validate those choices or constitute a completed field trial.
