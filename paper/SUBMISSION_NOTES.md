# NASEF submission notes

Checked 23 September 2026 against the [official conference page](https://www.sesn.com.ng/SolarEnergyConference.aspx)
and [SESN homepage](https://www.sesn.com.ng/).

- Listed conference: 21–23 October 2026, AUST Abuja.
- The important-dates section lists abstract deadline 30 September and full paper
  submission 5 October. The abstract paragraph separately says 5 October, so the
  official page is internally inconsistent. Plan against the earlier abstract date
  and confirm with the organizers before relying on the later date.
- The call specifies a title of no more than 20 words, abstract no more than 300 words,
  3–5 keywords, and a Word document in 12-point Times New Roman, double spaced.
- The digitalization/AI/smart-energy sub-theme appears relevant. Exact full-paper
  template, page limit and reference style still need confirmation.
- No submission, email, registration or payment has been made by this repository work.

## Before submitting the full paper

- Complete and verify related work from primary publications; audit the supplied draft's
  broad novelty statements rather than repeating them as established facts.
- Confirm authors, affiliations, correspondence, acknowledgements and venue requirements.
- Obtain domain review of simulator assumptions and inspect unresolved/incorrect cases.
- Present synthetic conditional results prominently; avoid claims of field accuracy,
  customer liability, real-world battery health or an evaluated physical device.
- Complete the live pilot if live conversational claims are included. Current failure
  requires workspace configuration; the implemented pathway alone is not a result.
- Cite the final code commit and archive the exact experiment artifacts used in the paper.
- Decide whether to include further independent baseline models/data before making
  stronger comparative claims; the current four arms are information-access ablations.

## API configuration

For a multi-workspace API key, add `ANTHROPIC_WORKSPACE_ID` to local `.env`. It is sent
as the `anthropic-workspace-id` header by the dashboard, original reasoning path and
research live runner. Alternatively use a workspace-scoped API key. Workspace IDs
are available in Claude Console → Settings → Workspaces.
[Anthropic authentication documentation](https://platform.claude.com/docs/en/manage-claude/authentication)

The archived failed live pilot attempted one request; an additional 32-output-token
diagnostic request was also rejected with the same workspace-header error. Neither
returned generated output or usage counters. No successful model results are inferred.
