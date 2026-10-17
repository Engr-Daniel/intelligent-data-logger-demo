# Field pilot data spec (I04): three sites, one month, no new hardware

Status: designed, 17 Oct 2026 · Feeds M01, M02, RQ1, RQ2, RQ4 · Owner: Daniel

The pilot tests the method on data that already exists. Each row says what is collected, how, and which question it serves. **No personal data:** sites have IDs; locations are recorded only to city level.

| # | Item | How it is captured (cheapest first) | Frequency | Lands in | Feeds |
|---|---|---|---|---|---|
| 1 | Inverter lifetime kWh (and battery %, if shown) | Photo of the inverter screen by the owner (as Suny does, C17) · or the vendor app's export | Weekly; daily if exported | Readings table: site, timestamp, value, source | O1, M02 |
| 2 | Interval data, where available | Vendor cloud or app export (CSV), mapped to the IDL schema | Weekly upload | Telemetry table (schema-validated) | O1, O4–O6 |
| 3 | Grid presence | Owner's yes/no per day for outages, or the inverter's grid-input reading where exported | Daily | Grid events | **O2 split, RQ2** |
| 4 | Generator hours and fuel bought | Owner logs hours and receipts (photo) | Each refill | Generator log | O2, O3 |
| 5 | Tariff band and price | Bill or DisCo notice | On change | Site configuration | O2 |
| 6 | **Installer findings on every visit** | The two-line form (I01): what was wrong, how found, when it started, what was done | Each visit | Findings table: site, date, finding, onset estimate | **M01, RQ1** |
| 7 | Decisions taken | One line when the owner acts on a statement or answer | When it happens | Decision log | RQ4 |
| 8 | Consent | One-page note: what is collected, who sees it, aggregate-only use, how to withdraw | Once | Paper or PDF, outside the repo | Governance (Q06) |

**Before the first reading:**
- write the device-to-schema mapping for each site's inverter (G03);
- fix the ROI and carbon counterfactual (I02), so month-one statements are right.

**Stop rule:** if fewer than 2 of 3 sites give ≥ 28 days of item 1 in the month, the manual route has failed. Revisit the "own hardware: not now" verdict.
