# Exploratory detection-delay analysis v1

Specified 6 October 2026 after seeing unverified timing claims in a co-author draft,
before running this implementation. This is exploratory, not preregistered or an
independent validation. No settings will be tuned to reproduce those claims.

Use all 24 frozen evaluation seeds, four pv_trend episodes, four access conditions
and three stress levels. Regenerate original observations and noise seeds; require
fingerprints and all 1,152 day-60 labels to match the frozen benchmark. Keep policy,
thresholds and original archives unchanged. Check physical consistency as before.
Run at the last sample of days 14 through 60, excluding future readings. No API use.

Reference: first local calendar day with mean latent injected loss >=5%, averaging
all 96 samples. This is an operational reference, not fault onset and not identical
to the policy's early/late median statistic. Latent values are for scoring only.

Schedules: periods 1,7,14,30 days; all phases 0..period-1; check days
14+phase+k*period <=60. Do not force an extra final check. Phases are alternative
schedules, not independent installations. Average phases within installation.

Rules: primary one positive check; exploratory sensitivity three consecutive
scheduled positive checks. Unknown/normal resets the counter. An alert occurs at
the third check, not retrospectively at the first. Periodic rules never use hidden
intermediate daily decisions. After reaching persistence, subsequent positive
checks remain alerting until a non-positive resets the run.

For crossing declines, separately report any alert, pre-reference alerts and
on/after-reference detection. Primary delay is first on/after-reference alert minus
reference day. Continue monitoring after early alerts. Give conditional delay and
its denominator; do not interpret early flags as detection of an absent decline.
For declines never crossing 5%, report their alert rate separately.

For each non-decline control report alerting-check and abstention rates, and the
fraction of installations with any alert. Also report any-control union per site
and phase. These are false trend alerts; low static efficiency is not a decline.

Finite-horizon waiting score: delay if detected on/after reference, otherwise
61-reference_day. This is time without a qualifying detection through day 60,
not predicted eventual delay. Compare schedules using paired differences versus
daily across the same crossing installations, averaging phases within site first.
Retain phase-level outcomes. Do not subtract conditional means on different subsets
and call that a paired advantage.

Bootstrap 2,000 whole-installation resamples, seed 20261006, for detection coverage,
union control-alert probability, waiting score and paired waiting-score differences.
Retain phases within each site. Conditional delay means/medians are descriptive.

Before evaluation snapshot this protocol, analysis code, frozen configuration,
simulator/policy and environment versions. Archive receipts, references, hashes,
status and errors. Test scheduling, persistence, pre-threshold handling, censoring
and future exclusion. Preserve all results, including failures. Do not update paper
numerical claims until the run is audited. This evaluates automated checks, not
installer visits, prevention of incidents or field diagnostic performance.
