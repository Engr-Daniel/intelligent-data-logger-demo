"""Exploratory rolling checks using the unchanged frozen trend policy; no API calls."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import platform
import shutil
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
local = ROOT / '.venv/Lib/site-packages'
if local.exists():
    sys.path.insert(0, str(local))
import numpy as np
import pandas as pd
from src.research.simulation import EPISODES, generate, corrupt
from src.research.policy import restrict, diagnose

BASE = ROOT / 'reports/research/20260923T190318100907Z_evaluation'
PERIODS = (1, 7, 14, 30)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def scheduled_days(period, phase, start=14, end=60):
    if period < 1 or not 0 <= phase < period:
        raise ValueError('Invalid period/phase')
    return list(range(start + phase, end + 1, period))


def alert_days(labels, period, phase, persistence):
    if persistence < 1:
        raise ValueError('Persistence must be positive')
    consecutive = 0
    alerts = []
    days = scheduled_days(period, phase)
    for day in days:
        consecutive = consecutive + 1 if labels[day] == 'pv_decline' else 0
        if consecutive >= persistence:
            alerts.append(day)
    return alerts, sum(labels[d] == 'unknown' for d in days), len(days)


def outcome(alerts, reference_day, end=60):
    post = [d for d in alerts if reference_day is not None and d >= reference_day]
    delay = post[0] - reference_day if post else None
    return dict(any_alert=int(bool(alerts)), first_alert=alerts[0] if alerts else None,
                pre_reference_alert=int(any(d < reference_day for d in alerts)) if reference_day else None,
                detected=int(bool(post)) if reference_day else None,
                first_post_reference_alert=post[0] if post else None, delay_days=delay,
                waiting_days=(delay if delay is not None else end + 1 - reference_day) if reference_day else None)


def reference_day(decline, days=60):
    loss = decline * np.linspace(0, 1, days * 96)
    daily = loss.reshape(days, 96).mean(axis=1)
    crossing = np.flatnonzero(daily >= .05)
    return int(crossing[0] + 1) if len(crossing) else None


def interval(values):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(20261006)
    draws = rng.integers(0, len(values), size=(2000, len(values)))
    lo, hi = np.quantile(values[draws].mean(axis=1), [.025, .975])
    return float(values.mean()), float(lo), float(hi)


def summarize(frame, output):
    summaries, paired = [], []
    groupcols = ['stress', 'condition', 'persistence', 'period']
    def record(keys, population, metric, values):
        values = values.dropna()
        if len(values):
            mean, lo, hi = interval(values)
            summaries.append(dict(zip(groupcols, keys), population=population, metric=metric,
                                  installations=len(values), mean=mean, lo=lo, hi=hi))
    for keys, group in frame.groupby(groupcols):
        decline = group[group.episode == 'trend_decline']
        crossing = decline[decline.reference_day.notna()]
        for metric in ['detected', 'pre_reference_alert', 'any_alert', 'waiting_days']:
            record(keys, 'crossing_declines', metric, crossing.groupby('seed')[metric].mean())
        below = decline[decline.reference_day.isna()]
        record(keys, 'below_threshold_declines', 'any_alert', below.groupby('seed').any_alert.mean())
        controls = group[group.episode != 'trend_decline']
        union = controls.groupby(['seed', 'phase']).any_alert.max().groupby('seed').mean()
        record(keys, 'any_control', 'any_alert', union)
        for episode, control in controls.groupby('episode'):
            for metric in ['any_alert', 'alert_check_rate', 'abstention_rate']:
                record(keys, episode, metric, control.groupby('seed')[metric].mean())
        detected = crossing[crossing.detected == 1]
        summaries.append(dict(zip(groupcols, keys), population='detected_crossing_site_phases',
                              metric='conditional_delay_days', installations=detected.seed.nunique(),
                              mean=detected.delay_days.mean(), lo=None, hi=None,
                              median=detected.delay_days.median(), detected_site_phases=len(detected),
                              eligible_site_phases=len(crossing)))
    for keys, group in frame[(frame.episode == 'trend_decline') & frame.reference_day.notna()].groupby(groupcols[:3]):
        site = group.groupby(['seed', 'period']).waiting_days.mean().unstack()
        for period in PERIODS[1:]:
            mean, lo, hi = interval(site[period] - site[1])
            paired.append(dict(zip(groupcols[:3], keys), period=period, installations=len(site),
                               mean_extra_wait_days=mean, lo=lo, hi=hi))
    summary = pd.DataFrame(summaries)
    summary.to_csv(output / 'summary.csv', index=False)
    pd.DataFrame(paired).to_csv(output / 'paired_schedule_effects.csv', index=False)
    rows = ['# Exploratory detection-delay results', '',
            'Synthetic automated checks; no installer comparator or field validation. Protocol specified after seeing',
            'unverified co-author claims. Existing policy and thresholds unchanged. No paid API calls.', '',
            'Intervals resample installations (2,000 draws). Periodic phases are averaged within installation.',
            'Delay is relative to the first daily mean latent loss >=5%, not physical onset.', '',
            '| Stress | Access | Rule | Period | Detection % | Mean delay among detected (days) | Any control alert % | Waiting score (days) |',
            '|---|---|---:|---:|---:|---:|---:|---:|']
    for keys, g in summary.groupby(groupcols, sort=False):
        stress, condition, persistence, period = keys
        def val(pop, metric):
            s = g[(g.population == pop) & (g.metric == metric)]
            return float(s.iloc[0]['mean']) if len(s) else float('nan')
        rows.append(f'| {stress} | {condition} | {persistence} | {period} | {100*val("crossing_declines", "detected"):.1f} | {val("detected_crossing_site_phases", "conditional_delay_days"):.2f} | {100*val("any_control", "any_alert"):.1f} | {val("crossing_declines", "waiting_days"):.2f} |')
    rows += ['', '## Interpretation and reproducibility', '',
             '- Detection coverage uses only reference-crossing declines. Below-threshold declines and pre-reference alerts are separate in summary.csv.',
             '- Conditional delay excludes misses; never infer a paired benefit by subtracting conditional means across schedules.',
             '- Waiting score assigns 61 minus reference day to misses; paired_schedule_effects.csv compares the same installations.',
             '- Any-control alert is a union across stable, changing-weather and static-low-efficiency controls.',
             '- Rule 3 requires three consecutive scheduled positives; unknown or normal resets it. It is exploratory, not tuned.',
             '- Recent-only conditions can abstain because the unchanged trend policy requires 14 valid days.',
             '- phase_outcomes.csv retains every installation, phase and rule. daily_predictions.csv and receipts.jsonl.gz preserve decisions.',
             '- manifest.json records source snapshots, input equivalence and all output hashes.',
             '- This analysis shares the original simulator and assumptions and does not reproduce or certify an unavailable co-author analysis.', '']
    (output / 'REPORT.md').write_text('\n'.join(rows), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    started = datetime.now(timezone.utc)
    output = args.output or ROOT / 'reports/research' / (started.strftime('%Y%m%dT%H%M%S%fZ') + '_detection_delay')
    output.mkdir(parents=True, exist_ok=False)
    config = ROOT / 'config/research_protocol.json'
    protocol = json.loads(config.read_text())
    sources = [Path(__file__), config, ROOT / 'docs/DETECTION_DELAY_PROTOCOL.md',
               ROOT / 'src/research/simulation.py', ROOT / 'src/research/policy.py',
               ROOT / 'tests/test_detection_delay.py']
    hashes = {}
    for source in sources:
        relative = source.relative_to(ROOT)
        target = output / 'source' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        hashes[relative.as_posix()] = sha(source)
    manifest = dict(status='running', started_utc=started.isoformat(), exploratory=True,
                    synthetic=True, python=platform.python_version(),
                    packages={p: version(p) for p in ['numpy', 'pandas']}, source_sha256=hashes,
                    baseline=str(BASE.relative_to(ROOT)),
                    baseline_sha256={n: sha(BASE / n) for n in ['predictions.csv', 'dataset_hashes.csv']},
                    seeds=protocol['evaluation_seeds'], periods=PERIODS, persistence=[1, 3],
                    bootstrap_replicates=2000, bootstrap_seed=20261006)
    def save():
        (output / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    save()
    print(f'Run directory: {output}', flush=True)
    baseline = pd.read_csv(BASE / 'predictions.csv').set_index(['case_id', 'stress', 'condition'])
    fingerprints = pd.read_csv(BASE / 'dataset_hashes.csv').set_index(['case_id', 'stress'])
    daily_rows, phase_rows, references, checks, input_hashes, equivalence = [], [], [], [], [], []
    try:
        with gzip.open(output / 'receipts.jsonl.gz', 'wt', encoding='utf-8') as receipts:
            for seed in protocol['evaluation_seeds']:
                for episode_index, (episode, task, _) in enumerate(EPISODES):
                    if task != 'pv_trend':
                        continue
                    case_id = f'site-{seed}-case-{episode_index:02d}'
                    df, static, oracle, physical = generate(seed, episode, protocol['days'], protocol['interval_minutes'])
                    checks.append(dict(case_id=case_id, **physical))
                    if not physical['passed']:
                        raise RuntimeError(f'Physical check failed: {case_id}')
                    ref = reference_day(oracle['decline_fraction']) if episode == 'trend_decline' else None
                    references.append(dict(case_id=case_id, seed=seed, episode=episode, reference_day=ref,
                                           final_injected_loss=oracle['decline_fraction'] if episode == 'trend_decline' else 0))
                    for stress_index, (stress, settings) in enumerate(protocol['stress_levels'].items()):
                        noise_seed = seed * 10000 + episode_index * 10 + stress_index
                        observed = corrupt(df, noise_seed, settings['relative_noise_sd'], settings['missing_fraction'])
                        digest = hashlib.sha256(pd.util.hash_pandas_object(observed, index=True).values.tobytes()).hexdigest()
                        expected = fingerprints.loc[(case_id, stress), 'data_hash']
                        input_hashes.append(dict(case_id=case_id, stress=stress, noise_seed=noise_seed,
                                                 data_hash=digest, baseline_data_hash=expected, matches=digest == expected))
                        if digest != expected:
                            raise RuntimeError(f'Input mismatch: {case_id}/{stress}')
                        for condition in protocol['conditions']:
                            labels = {}
                            for day in range(14, 61):
                                query = observed.timestamp.iloc[day * 96 - 1]
                                view = restrict(observed, condition, query)
                                if view.timestamp.max() > query:
                                    raise RuntimeError('Future-data leakage')
                                receipt = diagnose(view, static, task, protocol['thresholds'])
                                labels[day] = receipt['label']
                                row = dict(case_id=case_id, seed=seed, episode=episode, stress=stress,
                                           condition=condition, day=day, query_time=str(query), predicted=receipt['label'])
                                daily_rows.append(row)
                                receipts.write(json.dumps(dict(**row, evidence=receipt), allow_nan=False) + '\n')
                            old = baseline.loc[(case_id, stress, condition), 'predicted']
                            equivalence.append(dict(case_id=case_id, stress=stress, condition=condition,
                                                    archived_label=old, rolling_label=labels[60], matches=old == labels[60]))
                            if old != labels[60]:
                                raise RuntimeError(f'Day-60 mismatch: {case_id}/{stress}/{condition}')
                            for persistence in (1, 3):
                                for period in PERIODS:
                                    for phase in range(period):
                                        alerts, unknowns, count = alert_days(labels, period, phase, persistence)
                                        phase_rows.append(dict(case_id=case_id, seed=seed, episode=episode,
                                            stress=stress, condition=condition, persistence=persistence,
                                            period=period, phase=phase, reference_day=ref,
                                            alert_days=';'.join(map(str, alerts)), checks=count,
                                            alert_check_rate=len(alerts)/count, abstention_rate=unknowns/count,
                                            **outcome(alerts, ref)))
                print(f'Completed installation {seed}; {len(daily_rows)} daily decisions', flush=True)
        for name, rows in [('daily_predictions', daily_rows), ('phase_outcomes', phase_rows),
                           ('references', references), ('physical_checks', checks),
                           ('dataset_hashes', input_hashes), ('day60_equivalence', equivalence)]:
            pd.DataFrame(rows).to_csv(output / f'{name}.csv', index=False)
        summarize(pd.DataFrame(phase_rows), output)
        if len(equivalence) != 1152 or len(daily_rows) != 54144:
            raise RuntimeError('Unexpected evaluation size')
        manifest.update(status='complete', finished_utc=datetime.now(timezone.utc).isoformat(),
                        daily_predictions=len(daily_rows), phase_outcomes=len(phase_rows),
                        physical_trajectories=len(checks), verified_inputs=len(input_hashes),
                        verified_day60_labels=len(equivalence))
        manifest['artifact_sha256'] = {p.name: sha(p) for p in output.iterdir() if p.is_file() and p.name != 'manifest.json'}
        save()
        print(f'Complete: {output / "REPORT.md"}', flush=True)
    except Exception as exc:
        manifest.update(status='failed', error=f'{type(exc).__name__}: {exc}', completed_decisions=len(daily_rows))
        save()
        raise


if __name__ == '__main__':
    main()
