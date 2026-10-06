"""Produce a compact, source-linked interpretation and vector figure from a frozen timing run."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.venv/Lib/site-packages'))
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    folder = args.archive.resolve()
    manifest = json.loads((folder/'manifest.json').read_text())
    assert manifest['status'] == 'complete'
    output = folder.with_name(folder.name + '_interpretation')
    output.mkdir(exist_ok=False)
    summary = pd.read_csv(folder/'summary.csv')
    phases = pd.read_csv(folder/'phase_outcomes.csv')
    pairs = pd.read_csv(folder/'paired_schedule_effects.csv')
    refs = pd.read_csv(folder/'references.csv')
    def value(stress, condition, rule, period, population, metric):
        return summary[(summary.stress==stress)&(summary.condition==condition)&
            (summary.persistence==rule)&(summary.period==period)&
            (summary.population==population)&(summary.metric==metric)].iloc[0]
    def estimate(ax, positions, rows, color, label=None, scale=1):
        means=np.array([r['mean'] for r in rows])*scale
        lo=np.array([r['lo'] for r in rows])*scale
        hi=np.array([r['hi'] for r in rows])*scale
        ax.errorbar(positions, means, yerr=[np.maximum(0,means-lo), np.maximum(0,hi-means)],
                    color=color, marker='o', capsize=3, linewidth=1.6, label=label)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                         'axes.spines.right':False,'pdf.fonttype':42,'savefig.facecolor':'white'})
    fig, axes=plt.subplots(2,2,figsize=(10.8,7.8),layout='constrained')
    periods=[1,7,14,30]
    for condition, color, label in [('full_cross','#146b58','Cross-component'),('full_inverter','#173e80','Inverter-only')]:
        for ax, metric, scale in [(axes[0,0],'detected',100),(axes[0,1],'waiting_days',1)]:
            rows=[value('clean',condition,1,p,'crossing_declines',metric) for p in periods]
            estimate(ax,range(4),rows,color,label,scale)
    axes[0,0].set(title='A  Detection by day 60: clean observations',ylabel='Crossing installations detected (%)',ylim=(-3,103))
    axes[0,1].set(title='B  Waiting score, including missed detections',ylabel='Days without a qualifying detection')
    for ax in axes[0]:
        ax.set_xticks(range(4),['Daily','7 days','14 days','30 days'])
        ax.set_xlabel('Automated check interval')
    axes[0,0].legend(loc='lower left',frameon=False)
    stresses=['clean','moderate','severe']
    for rule,color,label in [(1,'#146b58','One positive check'),(3,'#ad681b','Three consecutive checks')]:
        for ax,pop,metric in [(axes[1,0],'any_control','any_alert'),(axes[1,1],'crossing_declines','detected')]:
            estimate(ax,range(3),[value(s,'full_cross',rule,1,pop,metric) for s in stresses],color,label,100)
    axes[1,0].set(title='C  Daily cross-component: false trend alerts',ylabel='Installations with any control alert (%)',ylim=(-3,103))
    axes[1,1].set(title='D  Daily cross-component: detection coverage',ylabel='Crossing installations detected (%)',ylim=(-3,103))
    for ax in axes[1]:
        ax.set_xticks(range(3),['Clean','Moderate','Severe'])
        ax.set_xlabel('Observation corruption')
    axes[1,0].legend(frameon=False)
    for ax in axes.flat:
        ax.grid(axis='y',alpha=.18)
    fig.savefig(output/'detection_delay.pdf',bbox_inches='tight')
    fig.savefig(output/'detection_delay.png',dpi=300,bbox_inches='tight')
    plt.close(fig)
    crossing=int(refs.reference_day.notna().sum())
    lines=['# Exploratory timing experiment: interpretation','',
           f'Linked [frozen run](../{folder.name}/REPORT.md). This is synthetic, exploratory evidence, not a field or installer comparison. No Claude calls were made.','',
           f'All 24 evaluation installations were reused; {crossing} decline trajectories crossed the 5% daily-mean loss reference and {24-crossing} did not. Four trend episodes, three stress levels, four access conditions and 47 daily checkpoints produced 54,144 decisions.', '',
           '## Clean observations: full-history cross-component access', '',
           '| Check interval | Detected, phase-average | Mean delay among detected | Waiting score including misses | Extra waiting versus daily (95% cluster interval) |',
           '|---|---:|---:|---:|---:|']
    for p in periods:
        d=value('clean','full_cross',1,p,'crossing_declines','detected')
        delay=value('clean','full_cross',1,p,'detected_crossing_site_phases','conditional_delay_days')
        wait=value('clean','full_cross',1,p,'crossing_declines','waiting_days')
        paired=pairs[(pairs.stress=='clean')&(pairs.condition=='full_cross')&(pairs.persistence==1)&(pairs.period==p)]
        diff='Reference' if p==1 else f'{paired.iloc[0].mean_extra_wait_days:.2f} [{paired.iloc[0].lo:.2f}, {paired.iloc[0].hi:.2f}]'
        lines.append(f'| {p} day(s) | {d["mean"]*crossing:.2f}/{crossing} ({d["mean"]*100:.1f}%) | {delay["mean"]:.2f} days | {wait["mean"]:.2f} days | {diff} |')
    lines += ['', 'Periodic fractional counts are averages over schedule phases. Conditional delays exclude misses and use different detected subsets; use the paired waiting-score comparison for schedule contrasts. The waiting score assigns 61 minus reference day to misses, so it does not estimate eventual delay.','',
              '## Daily checks: coverage and false alarms','',
              '| Stress | Access | Required consecutive positives | Detected after reference | Any pre-reference alert | Any control alert |',
              '|---|---|---:|---:|---:|---:|']
    for stress in stresses:
        for condition in ['full_cross','full_inverter']:
            for rule in [1,3]:
                d=value(stress,condition,rule,1,'crossing_declines','detected')['mean']
                pre=value(stress,condition,rule,1,'crossing_declines','pre_reference_alert')['mean']
                fp=value(stress,condition,rule,1,'any_control','any_alert')['mean']
                lines.append(f'| {stress} | {condition} | {rule} | {d*100:.1f}% | {pre*100:.1f}% | {fp*100:.1f}% |')
    lines += ['', 'False alerts here mean a pv_decline diagnosis in at least one stable, changing-weather or static-low-efficiency control. Their denominator is 24 installations. Pre-reference alerts concern the reference-crossing decline group; they are not proof that no loss existed.', '',
              '![Timing results](detection_delay.png)','',
              'Figure: installation-bootstrap 95% intervals; phases averaged within installation. Upper panels use one positive check. Lower panels compare one versus three consecutive daily positives with full-history cross-component access.', '',
              '## Limits and manuscript use', '',
              '- Use these independently generated values, not unverified draft numbers. Similar numerical values would not establish identical definitions or provenance.',
              '- The reference is injected daily-mean loss, whereas the policy compares early and late observed medians. Neither is physical field fault onset.',
              '- Three monthly positives are impossible in this observation window; their zero detection is a horizon limitation, not a useful competitor result.',
              '- Recent-only access cannot supply the existing trend tool with its required 14 days; report its abstentions, not a general failure of all recent-data methods.',
              '- Repeated checks create more opportunities for false alarms. Any-control alert probability and per-check rates answer different questions.',
              '- The same authored simulator, installations and policy are reused. The analysis was specified after seeing proposed results and is exploratory.',
              '- For the one-positive rule, daily checks include every periodic check by construction. Earlier or equal detection is structurally expected; the experiment quantifies delay, misses and false-alert exposure, not a new diagnostic superiority.',
              '- No field accuracy, prevented incidents, technician performance, or optimal check interval is established.',
              '- This report does not update the accepted abstract or full-paper numerical claims.', '']
    (output/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    provenance={'source_archive':folder.name,'source_manifest_sha256':hashlib.sha256((folder/'manifest.json').read_bytes()).hexdigest(),
                'builder_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (output/'provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    print(output)


if __name__=='__main__':
    main()
