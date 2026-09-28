"""Generate the manuscript's architecture figure from explicit evaluation boundaries."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.venv/Lib/site-packages'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
out=ROOT/'paper/figures';out.mkdir(exist_ok=True)
fig,ax=plt.subplots(figsize=(11,5));ax.set_xlim(0,11);ax.set_ylim(0,5);ax.axis('off')
boxes=[(0.2,3.2,2.3,1.1,'Synthetic plant\n+ physical checks'),(3,3.2,2.3,1.1,'Observed telemetry\n+ noise / missingness'),(6,3.2,2.3,1.1,'Restricted view\nHistory × channels'),(6,1.3,2.3,1.1,'Deterministic policy\nLabel + evidence receipt'),(8.8,1.3,2,1.1,'Claude pilot\nTool + explanation'),(0.2,.3,2.3,1.1,'Evaluation-only oracle\nInjected mechanism'),(3,.3,2.3,1.1,'Scoring + archives\nPaired comparisons')]
for x,y,w,h,label in boxes:
 color='#fff2d7' if 'oracle' in label else '#edf6f4'
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.06',facecolor=color,edgecolor='#285d57',linewidth=1.4));ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=10)
for a,b in [((2.55,3.75),(2.94,3.75)),((5.35,3.75),(5.94,3.75)),((7.15,3.14),(7.15,2.46)),((8.35,1.85),(8.74,1.85)),((2.55,.85),(2.94,.85)),((5.94,1.5),(5.35,1.0))]:ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':'#285d57','lw':1.6})
ax.text(3.9,2.35,'Oracle never enters\ndiagnostic or model inputs',ha='center',fontsize=11,color='#815600')
ax.text(5.5,4.75,'Information access is varied; the diagnostic policy is shared',ha='center',fontsize=13,fontweight='bold')
fig.tight_layout();fig.savefig(out/'architecture.png',dpi=220,bbox_inches='tight');fig.savefig(out/'architecture.svg',bbox_inches='tight');plt.close(fig)

svg=out/"architecture.svg"
svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines())+"\n")
