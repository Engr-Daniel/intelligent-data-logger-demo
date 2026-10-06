"""Generate publication vectors from frozen archives; never rerun experiments."""
from pathlib import Path
import csv,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.venv/Lib/site-packages'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
import numpy as np
OUT=ROOT/'paper/overleaf/figs';OUT.mkdir(parents=True,exist_ok=True)
EVAL=ROOT/'reports/research/20260923T190318100907Z_evaluation'
LIVE=ROOT/'reports/research/20260928T072939445717Z_live_development'
POST=ROOT/'reports/research/20260928_live_format_sensitivity'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#243746','text.color':'#243746','savefig.facecolor':'white'})
colors=['#176454','#255795','#A45916','#715090'];labels=['Full cross-component','Full inverter-only','Recent cross-component','Recent inverter-only'];keys=['full_cross','full_inverter','recent_cross','recent_inverter']
rows=list(csv.DictReader((EVAL/'metrics.csv').open()));lookup={(r['stress'],r['condition']):r for r in rows}
def save(fig,name):
 fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight',pad_inches=.05)
 fig.savefig(OUT/(name+'.png'),dpi=300,bbox_inches='tight',pad_inches=.05)
 plt.close(fig)
def canvas(h):
 fig,ax=plt.subplots(figsize=(7.1,h));ax.set_xlim(0,10);ax.set_ylim(0,h*1.45);ax.axis('off');return fig,ax
def box(ax,x,y,w,h,title,sub='',color='#176454',size=10):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.06,rounding_size=0.07',facecolor='#F6F8F9',edgecolor=color,linewidth=1))
 ax.text(x+w/2,y+h*(.67 if sub else .5),title,ha='center',va='center',fontsize=size,weight='bold',color=color)
 if sub:ax.text(x+w/2,y+h*.29,sub,ha='center',va='center',fontsize=size-1,linespacing=1.35)
def arrow(ax,a,b,color='#526574',style='-'):
 ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=11,linewidth=1,color=color,linestyle=style))
# One architecture figure incorporates workflow; separate score branches avoid implying an external evaluator.
fig,ax=canvas(4.8)
ax.text(.1,6.65,'DIAGNOSTIC AND REPORTING PATH',fontsize=10,weight='bold',color=colors[0]);ax.text(6.2,6.65,'EVALUATION-ONLY PATH',fontsize=10,weight='bold',color=colors[3])
items=[('Observed telemetry','Task + legitimate installation metadata'),('Prepare and restrict','Quality checks; permitted history/channels'),('Deterministic diagnosis','Fixed policy; explicit unknown outcome'),('Evidence receipt','Decision, measurements, window, thresholds'),('Conversational report','Tool selection then receipt-grounded output')]
ys=[5.4,4.2,3,1.8,.6]
for (t,sub),y in zip(items,ys):box(ax,.15,y,5.3,.88,t,sub,size=10)
for a,b in zip(ys,ys[1:]):arrow(ax,(2.8,a),(2.8,b+.9))
ax.plot([5.8,5.8],[.25,6.4],ls='--',color='#9AA6AE',lw=1)
box(ax,6.25,5.4,3.5,.88,'Reference labels','Injected causes; scoring only',colors[3])
box(ax,6.25,2.8,3.5,1.05,'Diagnostic scoring','Correctness, coverage,\nfalse positives, abstention',colors[3])
box(ax,6.25,.5,3.5,1.1,'Reporting checks','Format, label fidelity,\ncitation-name validity',colors[3])
arrow(ax,(8,5.4),(8,3.9),colors[3]);arrow(ax,(5.5,3.43),(6.17,3.43));arrow(ax,(5.5,1.02),(6.17,1.02))
ax.text(8,4.55,'Reference labels excluded\nfrom diagnostic inputs',ha='center',fontsize=8.5,color='#963C32',bbox={'facecolor':'white','edgecolor':'none','pad':3})
save(fig,'01_evidence_boundary')
# Benchmark compact matrix.
fig,ax=canvas(3.4)
box(ax,.15,3.7,9.6,.85,'8 development installations | 24 evaluation installations','Disjoint seeds; 12 matched episodes per evaluation installation')
ax.text(.2,3.14,'History',weight='bold');ax.text(3.7,3.14,'Cross-component',ha='center',weight='bold');ax.text(7.8,3.14,'Inverter-only',ha='center',weight='bold')
for y,head,left,right in [(2.05,'60 days',0,1),(.98,'24 hours',2,3)]:
 ax.text(.2,y+.35,head,va='center');box(ax,1.9,y,3.65,.72,labels[left],color=colors[left],size=10);box(ax,5.95,y,3.65,.72,labels[right],color=colors[right],size=10)
ax.text(5,.4,'288 episodes × 4 access conditions × 3 stress levels = 3,456 predictions',ha='center',fontsize=10,weight='bold')
save(fig,'02_benchmark_design')
# Clean correctness and coverage share condition order, both with installation-bootstrap intervals.
fig,axes=plt.subplots(1,2,figsize=(7.1,3.15),sharey=True,gridspec_kw={'width_ratios':[1.3,1]})
for ax,metric,title in zip(axes,['diagnostic_accuracy','coverage'],['(a) Correct diagnostic label','(b) Non-unknown answer']):
 for i,key in enumerate(keys):
  r=lookup['clean',key];v=float(r[metric])*100;lo=float(r[metric+'_lo'])*100;hi=float(r[metric+'_hi'])*100
  ax.errorbar(v,3-i,xerr=[[max(0,v-lo)],[max(0,hi-v)]],fmt='o',color=colors[i],capsize=3,ms=6,lw=1.5)
  ax.annotate(f'{v:.1f}',(v,3-i),xytext=(0,10),textcoords='offset points',ha='center',fontsize=8.5)
 ax.set_xlim(0,105);ax.set_ylim(-.5,3.65);ax.set_xticks([0,25,50,75,100]);ax.set_xlabel('Percent');ax.set_title(title,fontsize=10,pad=16);ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
axes[0].set_yticks(range(4),list(reversed(labels)),fontsize=9)
fig.tight_layout(w_pad=1.1);save(fig,'03_correctness_coverage')
fig,ax=plt.subplots(figsize=(7.1,3.45))
for j,key in enumerate(keys):
 values=[lookup[stress,key] for stress in ['clean','moderate','severe']];v=np.array([float(r['diagnostic_accuracy'])*100 for r in values]);lo=np.array([float(r['diagnostic_accuracy_lo'])*100 for r in values]);hi=np.array([float(r['diagnostic_accuracy_hi'])*100 for r in values]);x=np.arange(3)+(j-1.5)*.025
 ax.errorbar(x,v,yerr=[np.maximum(0,v-lo),np.maximum(0,hi-v)],label=labels[j],color=colors[j],marker=['o','s','^','D'][j],ls=['-','--','-.',':'][j],capsize=3,lw=1.4,ms=5)
ax.set_xticks(range(3),['Clean','Moderate\n3% noise; 1% missing','Severe\n8% noise; 5% missing']);ax.set_ylim(0,105);ax.set_xlim(-.16,2.16);ax.set_ylabel('Correct diagnostic labels (%)');ax.grid(axis='y',alpha=.2);ax.legend(loc='lower center',bbox_to_anchor=(.5,1.02),ncol=2,frameon=False,fontsize=9);fig.tight_layout();save(fig,'04_corruption_robustness')
# Pilot graphic is quantitative too: derive every count from archives.
primary=json.loads((LIVE/'summary.json').read_text());post=json.loads((POST/'summary.json').read_text())
fig,axes=plt.subplots(1,2,figsize=(7.1,3.2),sharey=True)
metrics=['valid_json','label_fidelity','oracle_correct','citation_validity'];names=['JSON accepted','Label matches receipt','Label matches oracle','Valid citation names']
for ax,counts,title,c in [(axes[0],primary['counts'],'(a) Prespecified strict scoring',colors[1]),(axes[1],post['counts'],'(b) Post-hoc fence removal',colors[0])]:
 for i,m in enumerate(metrics):
  v=counts[m];ax.barh(3-i,v,color=c,height=.45);ax.text(v+.5,3-i,f'{v}/24',va='center',fontsize=9)
 ax.set_xlim(0,29);ax.set_xticks([0,12,24]);ax.set_xlabel('Conversations');ax.set_title(title,fontsize=10,pad=12);ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
axes[0].set_yticks(range(4),list(reversed(names)),fontsize=9);fig.tight_layout();save(fig,'05_reporting_failures')
# Care-loop overview with readable type at final manuscript width.
fig,ax=plt.subplots(figsize=(7.1,3.4));ax.set_xlim(0,10);ax.set_ylim(-.1,4.6);ax.axis('off')
steps=[('1  Measure','Simulated input;\nphysical acquisition\nproposed',True),('2  Record','Stored, aligned history',False),('3  Diagnose','Deterministic tool\nand evidence receipt',False),('4  Explain','Reporting tested;\noutput contract failed',False),('5  Act','Proposed field\nintervention',True),('6  Verify','Field intervention\noutcome (proposed)',True)]
for i,(title,detail,proposed) in enumerate(steps):
 x=.15+(i%3)*3.35;y=2.8 if i<3 else .75
 ax.add_patch(FancyBboxPatch((x,y),2.8,1.15,boxstyle='round,pad=.03',fc='white' if proposed else '#edf5f2',ec='#176454',ls='--' if proposed else '-',lw=1.2))
 ax.text(x+1.4,y+.85,title,ha='center',va='center',fontsize=10,weight='bold')
 ax.text(x+1.4,y+.36,detail,ha='center',va='center',fontsize=9)
 if i%3<2:arrow(ax,(x+2.85,y+.57),(x+3.25,y+.57))
ax.plot([8.25,8.25,1.55],[2.73,2.35,2.35],color='#526574',lw=1)
arrow(ax,(1.55,2.35),(1.55,1.95))
ax.text(5,.13,'Proposed feedback: verified outcomes become part of the next record',ha='center',fontsize=9,color='#8a5a00')
ax.text(5,4.35,'Software evidence path evaluated; physical care loop remains proposed',ha='center',fontsize=9.5)
save(fig,'00_care_loop')
# Manuscript-sized timing panels; the full four-panel master remains in the archive.
TIMING=ROOT/'reports/research/20261006T022136185304Z_detection_delay_interpretation'
TIMINGRUN=ROOT/'reports/research/20261006T022136185304Z_detection_delay'
timingrows=list(csv.DictReader((TIMINGRUN/'summary.csv').open()))
def timingvalue(stress,condition,rule,period,population,metric):
 return next(r for r in timingrows if r['stress']==stress and r['condition']==condition and int(r['persistence'])==rule and int(r['period'])==period and r['population']==population and r['metric']==metric)
def timingplot(ax,x,rs,color,label,marker):
 means=np.array([float(r['mean'])*100 for r in rs]);lo=np.array([float(r['lo'])*100 for r in rs]);hi=np.array([float(r['hi'])*100 for r in rs])
 ax.errorbar(x,means,yerr=[np.maximum(0,means-lo),np.maximum(0,hi-means)],color=color,label=label,marker=marker,capsize=3,lw=1.3,ms=4)
fig,axes=plt.subplots(1,2,figsize=(7.1,3.5))
for condition,color,label,marker in [('full_cross',colors[0],'Cross-component','o'),('full_inverter',colors[1],'Inverter-only','s')]:
 timingplot(axes[0],np.arange(4),[timingvalue('clean',condition,1,p,'crossing_declines','detected') for p in [1,7,14,30]],color,label,marker)
for rule,color,label,marker in [(1,colors[0],'One positive','o'),(3,colors[2],'Three consecutive','s')]:
 timingplot(axes[1],np.arange(3),[timingvalue(stress,'full_cross',rule,1,'any_control','any_alert') for stress in ['clean','moderate','severe']],color,label,marker)
axes[0].set_xticks(range(4),['Daily','7 d','14 d','30 d']);axes[0].set_xlabel('Check interval');axes[0].set_ylabel('Detection (% of crossing sites)');axes[0].set_title('(a) Clean: detection by day 60',fontsize=10)
axes[1].set_xticks(range(3),['Clean','Moderate','Severe']);axes[1].set_xlabel('Observation corruption');axes[1].set_ylabel('Any control alert (% of sites)');axes[1].set_title('(b) Daily: false trend alerts',fontsize=10)
for ax in axes:
 ax.set_ylim(-3,105);ax.tick_params(labelsize=9);ax.grid(axis='y',alpha=.2);ax.legend(frameon=False,fontsize=8,loc='upper center',bbox_to_anchor=(.5,-.22))
fig.tight_layout();save(fig,'06_detection_delay')
import runpy
runpy.run_path(str(ROOT/'scripts/build_architecture_figures.py'))
import shutil
for ext in ['pdf','png','svg']:
 shutil.copyfile(ROOT/'docs/architecture/figs'/('07_conversation_flow.'+ext),OUT/('07_conversation_flow.'+ext))
manifest={'description':'New presentation figures; archived experiments unchanged. PDF vector masters and 300 dpi PNG previews.','inputs':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [EVAL/'metrics.csv',LIVE/'summary.json',POST/'summary.json',TIMINGRUN/'summary.csv',TIMINGRUN/'manifest.json']},'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('*')) if p.suffix in ['.pdf','.png','.svg']}}
(OUT/'provenance.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('Generated seven manuscript figures and one supplementary timing figure and previews from verified source tables.')
