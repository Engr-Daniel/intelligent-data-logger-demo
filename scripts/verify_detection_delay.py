"""Audit a timing archive independently of the analysis scorer; never modifies it."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.venv/Lib/site-packages'))
import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    folder = args.archive
    manifest = json.loads((folder / 'manifest.json').read_text())
    assert manifest['status'] == 'complete'
    for name, digest in manifest['artifact_sha256'].items():
        assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest, name
    for name, digest in manifest['source_sha256'].items():
        assert hashlib.sha256((folder / 'source' / name).read_bytes()).hexdigest() == digest, name
    for name, digest in manifest['baseline_sha256'].items():
        assert hashlib.sha256((ROOT / manifest['baseline'] / name).read_bytes()).hexdigest() == digest, name
    for name in ['src/research/simulation.py', 'src/research/policy.py', 'config/research_protocol.json']:
        assert (folder / 'source' / name).read_text(encoding='utf-8-sig') == (ROOT / manifest['baseline'] / 'source' / name).read_text(encoding='utf-8-sig'), name
    daily = pd.read_csv(folder / 'daily_predictions.csv')
    phases = pd.read_csv(folder / 'phase_outcomes.csv')
    refs = pd.read_csv(folder / 'references.csv')
    assert len(daily) == 54144 and len(phases) == 119808
    assert not daily.duplicated(['case_id', 'stress', 'condition', 'day']).any()
    assert pd.read_csv(folder / 'day60_equivalence.csv').matches.all()
    assert pd.read_csv(folder / 'dataset_hashes.csv').matches.all()
    assert pd.read_csv(folder / 'physical_checks.csv').passed.all()
    for r in refs[refs.episode == 'trend_decline'].itertuples():
        expected = next((day for day in range(1, 61)
                         if r.final_injected_loss * ((day-1)*96 + 47.5)/5759 >= .05), None)
        assert (expected is None and pd.isna(r.reference_day)) or expected == r.reference_day
    labels = {key: dict(zip(g.day, g.predicted)) for key, g in daily.groupby(['case_id', 'stress', 'condition'])}
    refmap = refs.set_index('case_id').reference_day.to_dict()
    for row in phases.itertuples():
        days = [d for d in range(14, 61) if (d - 14) % row.period == row.phase]
        decisions = labels[(row.case_id, row.stress, row.condition)]
        positives = [decisions[d] == 'pv_decline' for d in days]
        alerts = [days[i] for i in range(row.persistence-1, len(days))
                  if all(positives[i-row.persistence+1:i+1])]
        stored = [] if pd.isna(row.alert_days) else [int(float(d)) for d in str(row.alert_days).split(';')]
        assert alerts == stored
        assert row.checks == len(days)
        assert np.isclose(row.alert_check_rate, len(alerts)/len(days))
        assert np.isclose(row.abstention_rate, sum(decisions[d] == 'unknown' for d in days)/len(days))
        assert row.any_alert == bool(alerts)
        ref = refmap[row.case_id]
        if not pd.isna(ref):
            post = [d for d in alerts if d >= ref]
            assert row.detected == bool(post)
            assert row.pre_reference_alert == any(d < ref for d in alerts)
            assert row.waiting_days == (post[0]-ref if post else 61-ref)
            assert (pd.isna(row.delay_days) and not post) or (post and row.delay_days == post[0]-ref)
    receipt_count = 0
    with gzip.open(folder / 'receipts.jsonl.gz', 'rt', encoding='utf-8') as f:
        for line in f:
            row = json.loads(line)
            evidence = row['evidence']
            assert pd.Timestamp(evidence['data_window']['end']) <= pd.Timestamp(row['query_time'])
            assert evidence['label'] == labels[(row['case_id'], row['stress'], row['condition'])][row['day']]
            receipt_count += 1
    assert receipt_count == len(daily)
    # Independently recompute reported site averages and paired schedule effects.
    crossing = phases[(phases.episode == 'trend_decline') & phases.reference_day.notna()]
    summary = pd.read_csv(folder / 'summary.csv')
    for row in summary.itertuples():
        g = phases[(phases.stress == row.stress) & (phases.condition == row.condition) &
                   (phases.persistence == row.persistence) & (phases.period == row.period)]
        if row.population == 'crossing_declines':
            g = g[(g.episode == 'trend_decline') & g.reference_day.notna()]
            value = g.groupby('seed')[row.metric].mean().mean()
        elif row.population == 'any_control':
            g = g[g.episode != 'trend_decline']
            value = g.groupby(['seed', 'phase']).any_alert.max().groupby('seed').mean().mean()
        elif row.population == 'below_threshold_declines':
            g = g[(g.episode == 'trend_decline') & g.reference_day.isna()]
            value = g.groupby('seed').any_alert.mean().mean()
        elif row.population == 'detected_crossing_site_phases':
            value = g[(g.episode == 'trend_decline') & (g.detected == 1)].delay_days.mean()
        else:
            value = g[g.episode == row.population].groupby('seed')[row.metric].mean().mean()
        assert np.isclose(row.mean, value, equal_nan=True), (row.population, row.metric)
    for row in pd.read_csv(folder / 'paired_schedule_effects.csv').itertuples():
        g = crossing[(crossing.stress == row.stress) & (crossing.condition == row.condition) & (crossing.persistence == row.persistence)]
        means = g.groupby(['seed', 'period']).waiting_days.mean().unstack()
        assert np.isclose((means[row.period]-means[1]).mean(), row.mean_extra_wait_days)
    print(json.dumps(dict(status='passed', hashed_artifacts=len(manifest['artifact_sha256']),
          daily_decisions=len(daily), audited_phase_outcomes=len(phases), receipts=receipt_count,
          reference_crossing_installations=int(refs.reference_day.notna().sum())), indent=2))


if __name__ == '__main__':
    main()
