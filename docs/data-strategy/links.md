# Links between editions: petgrave-idl ↔ system-owner (↔ installer, planned)

Status: ◐ provisional · Last updated: 17 Oct 2026

## Roll-ups

| Owner or site metric | Programme metric | Rule | Basis |
|---|---|---|---|
| A diagnosis at a site + the installer's finding there (I01) | **M01** field-confirmed diagnoses | Matches ÷ diagnoses with a recorded finding, counted across pilot sites; counts while n < 30 | Pilot consent note |
| Weeks with a complete record at a site | **M02** sites with a usable feed | Sites with ≥ 28 of 30 days ÷ enrolled | Pilot consent note |
| O2 grid-on vs. grid-off split at each site | **RQ2** share of solar displacing the generator | Σ grid-off self-consumed kWh ÷ Σ self-consumed kWh, by site | Aggregate only |
| Statement opened + decision recorded (I07) | **RQ4** do owners act? | Sites with ≥ 1 recorded decision a month ÷ sites | Aggregate only |

## Shared flows and hand-offs

| Flow | Hand-off | Where it usually breaks |
|---|---|---|
| Reading → answer → action | The IDL's answer (petgrave-idl) → the owner's decision (system-owner) | **G06 / G14:** an answer nobody acts on |
| Fault → call-back → finding → check | The installer's visit → the research label | **G02:** the finding is never written down |

## Data rights (check against the NDPA 2023, Q06)

- The site's energy record belongs to the owner. Petgrave.io may use it for the pilot and for research **only in aggregate**, with written consent.
- Energy data reveals when people are present. It is never published per site or with a location finer than the city.
- Installer findings belong to the installer. They are used as anonymised labels.
- Nothing is sent to the model beyond the measurements needed for the question. No names, phone numbers or addresses go in prompts.

## Value exchange

| Data flowing to Petgrave.io | What the giver gets back |
|---|---|
| The owner's weekly readings | **I07** monthly energy statement, free during the pilot |
| The installer's call-back findings | A diagnosis before the visit, and a record of faults found and fixed that they can show customers |

A flow that gives nothing back will be abandoned. If installers don't value the diagnosis, I01 needs a different return.

## Vision consistency

The programme vision needs owners to share data and installers to log findings. The owner vision offers the statement in return. The installer return is not yet tested, so the installer edition is the gap. **Flag:** start it when 3 installers have answered the pack.
