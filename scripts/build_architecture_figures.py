"""Original vector system diagrams; proposed field hardware is explicitly marked."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'.venv/Lib/site-packages'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch,Rectangle,Polygon,Ellipse,Circle
OUT=Path(__file__).resolve().parents[1]/'docs/architecture/figs'
OUT.mkdir(parents=True,exist_ok=True)
INK='#19394D';BLUE='#235C96';GREEN='#167766';GOLD='#A16816';PURPLE='#70578C';MUTED='#566674'
plt.rcParams.update({'font.family':'DejaVu Sans','pdf.fonttype':42,'svg.fonttype':'none','text.color':INK})

def canvas(h,title,sub):
 f,a=plt.subplots(figsize=(10,h));a.set_xlim(0,10);a.set_ylim(0,h);a.axis('off');f.subplots_adjust(0,0,1,1)
 a.text(.2,h-.25,title,fontsize=16,weight='bold',va='top')
 a.text(.2,h-.64,sub,fontsize=10.5,va='top',color=MUTED)
 return f,a

def text(a,x,y,t,size=11,**kw):a.text(x,y,t,fontsize=size,ha=kw.pop('ha','center'),va='center',**kw)
def panel(a,x,y,w,h,title,color=GREEN,dashed=False):
 a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.02,rounding_size=.08',fc='#F4F7F9',ec=color,lw=1.2,ls='--' if dashed else '-'))
 text(a,x+.14,y+h-.25,title,11,color=color,weight='bold',ha='left')
def box(a,x,y,w,h,title,detail='',color=BLUE,dashed=False):
 a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.025,rounding_size=.06',fc='white',ec=color,lw=1.25,ls='--' if dashed else '-'))
 text(a,x+w/2,y+h*(.72 if detail else .5),title,11.5,weight='bold',color=color)
 if detail:text(a,x+w/2,y+h*.32,detail,10,linespacing=1.3)
def arrow(a,pts,color=BLUE,dashed=False,both=False,lw=1.5):
 if both and len(pts)>2:a.add_patch(FancyArrowPatch(pts[1],pts[0],arrowstyle='-|>',color=color,lw=lw,mutation_scale=12,shrinkA=0,shrinkB=2))
 if len(pts)>2:a.plot(*zip(*pts[:-1]),color=color,lw=lw,ls='--' if dashed else '-',solid_capstyle='round')
 a.add_patch(FancyArrowPatch(pts[-2],pts[-1],arrowstyle='<->' if both and len(pts)==2 else '-|>',color=color,lw=lw,linestyle='--' if dashed else '-',mutation_scale=12,shrinkA=1,shrinkB=2))
def label(a,x,y,t,color=MUTED):text(a,x,y,t,9.5,color=color,bbox={'facecolor':'white','edgecolor':'none','pad':1.5})
def icon(a,x,y,kind,color=BLUE):
 if kind=='pv':
  a.add_patch(Polygon([(x-.42,y-.22),(x+.33,y-.22),(x+.43,y+.24),(x-.32,y+.24)],fc='#DBE8F4',ec=color,lw=1.5))
  for dx in [-.08,.17]:a.plot([x+dx-.09,x+dx],[y-.22,y+.24],color=color,lw=.8)
  a.plot([x-.37,x+.38],[y+.01,y+.01],color=color,lw=.8);a.plot([x,x],[y-.22,y-.36],color=color);a.plot([x-.27,x+.27],[y-.36,y-.36],color=color)
 elif kind=='battery':
  a.add_patch(Rectangle((x-.32,y-.25),.64,.5,fc='#DCF0E9',ec=color,lw=1.5));a.add_patch(Rectangle((x-.1,y+.25),.2,.07,fc=color))
  for dx in [-.18,0,.18]:a.add_patch(Rectangle((x+dx-.05,y-.14),.1,.28,fc=color))
 elif kind=='house':
  a.add_patch(Polygon([(x-.36,y-.25),(x-.36,y+.1),(x,y+.4),(x+.36,y+.1),(x+.36,y-.25)],fc='#E7EEF5',ec=color,lw=1.5));a.add_patch(Rectangle((x-.08,y-.25),.16,.25,fc='white',ec=color))
 elif kind=='grid':
  a.plot([x-.25,x,x+.25],[y-.35,y+.4,y-.35],color=color,lw=1.5)
  for dy,w in [(0,.4),(.22,.3),(-.2,.21)]:a.plot([x-w,x+w],[y+dy,y+dy],color=color,lw=1.3)
 elif kind=='weather':
  a.add_patch(Circle((x,y+.04),.18,fc='#FFF0CB',ec=GOLD,lw=1.3))
  import math
  for i in range(8):
   t=i*math.pi/4;a.plot([x+.24*math.cos(t),x+.34*math.cos(t)],[y+.04+.24*math.sin(t),y+.04+.34*math.sin(t)],color=GOLD)
 elif kind=='inverter':
  a.add_patch(FancyBboxPatch((x-.35,y-.35),.7,.7,boxstyle='round,pad=.02',fc='#E4EDF4',ec=color,lw=1.5));a.add_patch(Rectangle((x-.23,y+.05),.46,.17,fc='white',ec=color));text(a,x,y-.14,'~',22,color=color)
 elif kind=='store':
  a.add_patch(Rectangle((x-.34,y-.25),.68,.5,fc='#DCF0E9',ec=color,lw=1.3))
  for dy in [-.25,0,.25]:a.add_patch(Ellipse((x,y+dy),.68,.16,fc='#DCF0E9',ec=color,lw=1.3))

def save(f,name):
 for ext in ['pdf','png','svg']:f.savefig(OUT/f'{name}.{ext}',dpi=300,bbox_inches='tight',pad_inches=.04,facecolor='white')
 plt.close(f)

# Figure 1: distinguish electrical topology from read-only observations.
f,a=canvas(7.8,'Installation blueprint: power, observations and continuity','Reference hybrid topology; physical devices and acquisition gateway are proposed.')
panel(a,.2,3.5,9.6,3.25,'A  PHYSICAL INSTALLATION',BLUE,True)
for x,y,k,t in [(1.25,5.6,'pv','PV array'),(1.25,4.25,'battery','Battery / BMS'),(4.1,5.15,'inverter','Hybrid inverter'),(8.65,5.85,'grid','Utility grid'),(8.65,4.25,'house','Served loads')]:
 icon(a,x,y,k);text(a,x,y-.63,t,11,weight='bold')
arrow(a,[(1.8,5.55),(2.8,5.55),(2.8,5.36),(3.6,5.36)]);label(a,2.7,5.75,'DC generation')
arrow(a,[(1.8,4.25),(3,4.25),(3,4.93),(3.62,4.93)],both=True);label(a,2.57,4.04,'DC charge / discharge')
arrow(a,[(4.58,5.2),(6,5.2)],both=True);label(a,5.25,5.44,'AC')
a.plot([6,6],[4.25,5.85],color=BLUE,lw=2);label(a,6,6.1,'AC bus')
box(a,6.55,5.58,1.05,.53,'Meter',color=BLUE);arrow(a,[(6,5.85),(6.5,5.85)],both=True);arrow(a,[(7.65,5.85),(8.13,5.85)],both=True)
arrow(a,[(6,4.25),(8.12,4.25)]);label(a,7.08,4.48,'Load meter')
text(a,4.1,4.03,'Installation identity\nanchored to inverter',10,color=BLUE)
panel(a,.2,.75,9.6,2.42,'B  READ-ONLY DATA PATH',GREEN,True)
icon(a,.82,2.12,'weather');text(a,1.57,2.12,'Weather\nsensors',10,ha='left')
box(a,3.2,1.75,2.6,.87,'Logger / gateway','Time, units, quality flags',GREEN,True)
box(a,6.55,1.75,2.93,.87,'Persistent installation record','Measurements + device identity',GREEN)
arrow(a,[(2.62,2.12),(3.15,2.12)],GREEN,True);arrow(a,[(5.85,2.18),(6.5,2.18)],GREEN,True)
# A shared acquisition bus carries observations, never electrical power.
a.plot([1.25,8.65],[3.32,3.32],color=GREEN,ls='--',lw=1.4)
for x,y in [(1.25,3.53),(4.1,3.53),(8.65,3.53)]:a.plot([x,x],[y,3.32],color=GREEN,ls='--',lw=1.4)
arrow(a,[(4.5,3.32),(4.5,2.67)],GREEN,True)
label(a,7.15,3.3,'Inverter, battery, load and grid observations',GREEN)
text(a,4.5,1.21,'Proposed: authorized device adapters,\nlocal buffering and timestamp alignment',10,color=MUTED)
text(a,8.0,1.2,'Study: synthetic records\nsubstitute for field acquisition',10,color=GREEN)
text(a,.24,.32,'Solid blue: electrical power     Dashed green: telemetry     Dashed enclosure: proposed field scope',10,ha='left')
save(f,'00_care_loop')

# Figure 2: a layered blueprint with explicit user/report and evaluation boundaries.
f,a=canvas(8.2,'Intelligent Data Logger: evidence-grounded architecture','One installation record connects current status, historical investigation and inspectable evidence.')
panel(a,.2,5.9,9.6,1.22,'01  OWNER / INSTALLER EXPERIENCE',BLUE)
box(a,.45,6.08,3.25,.55,'Status first: PV | load | SOC',color=BLUE)
box(a,4.25,6.08,5.25,.55,'Ask: "Why was output low this week?"',color=BLUE)
arrow(a,[(6.88,6.03),(6.88,5.48)],BLUE);label(a,7.85,5.72,'Question / task')
panel(a,.2,3.18,9.6,2.25,'02  DIAGNOSTIC AND CONVERSATIONAL SERVICES',GREEN)
box(a,.45,3.5,2.65,1.3,'Restricted evidence view','Allowed channels / history\nAt or before query time\nNameplate metadata',GREEN)
box(a,3.65,3.5,2.65,1.3,'Deterministic tools','Daily output | alarms\nLongitudinal PV trend\nSupported label or unknown',GREEN)
box(a,6.85,3.5,2.65,1.3,'Conversational reporting','Approved tool selection\nReceipt-based explanation\nRaw response retained',BLUE)
arrow(a,[(3.15,4.16),(3.6,4.16)],GREEN);arrow(a,[(6.35,4.16),(6.8,4.16)],GREEN)
label(a,6.57,4.4,'Receipt',GREEN)
arrow(a,[(7.9,4.85),(7.9,4.97),(4.97,4.97),(4.97,4.85)],BLUE)
label(a,6.5,4.97,'Tool call',BLUE)
# Question routes to service, while the response returns along outer right side.
arrow(a,[(6.88,5.48),(8.18,5.48),(8.18,4.85)],BLUE)
arrow(a,[(9.55,4.65),(9.72,4.65),(9.72,5.74),(8.55,5.74),(8.55,6.03)],BLUE)
label(a,3.2,5.67,'Latest stored snapshot',GREEN)
arrow(a,[(.36,2.92),(.08,2.92),(.08,5.74),(1.5,5.74),(1.5,6.03)],GREEN)
panel(a,.2,1.58,5.95,1.42,'03  PERSISTENT OPERATIONAL MEMORY',GREEN)
icon(a,.83,2.12,'store',GREEN)
text(a,1.43,2.12,'Time series + legitimate installation metadata\nProposed extension: commissioning / service history',10,ha='left')
arrow(a,[(1.77,3.04),(1.77,3.45)],GREEN)
panel(a,6.45,1.58,3.35,1.42,'04  OFFLINE EVALUATION',PURPLE)
text(a,8.13,2.12,'Reference labels: scoring only\nDiagnosis, coverage, format, citations',9.8,color=PURPLE)
arrow(a,[(8.18,3.45),(8.18,3.05)],PURPLE)
arrow(a,[(5.9,3.45),(5.9,3.1),(6.3,3.1),(6.3,2.1),(6.4,2.1)],PURPLE)
panel(a,.2,.35,9.6,.94,'PROPOSED FIELD CONTINUITY',GOLD,True)
text(a,5,.66,'Authorized owner / installer access  |  Physical intervention  |  Verified outcome added to record',10,color=GOLD)
text(a,5,7.2,'Study boundary: synthetic diagnostic evaluation + separate Claude development pilot',10,color=GREEN)
arrow(a,[(3,1.33),(3,1.53)],GOLD,True)
save(f,'01_evidence_boundary')

# Figure 3: actual reproducibility flow, including the access matrix and branching validation.
f,a=canvas(7.7,'Worked evaluation: from generated episodes to auditable results','Diagnostic policy fixed after development; references remain outside the operational evidence path.')
box(a,.35,5.35,3.45,1.13,'1  Define and generate','8 development / 24 evaluation sites\n12 matched episodes; 60 days each',BLUE)
# validation diamond
cx,cy=5.65,5.9;a.add_patch(Polygon([(cx-1.12,cy),(cx,cy+.66),(cx+1.12,cy),(cx,cy-.66)],fc='#F0F6F3',ec=GREEN,lw=1.4));text(a,cx,cy,'Physical\nchecks pass?',11,weight='bold',color=GREEN)
arrow(a,[(3.85,5.9),(4.48,5.9)],BLUE)
box(a,7.55,5.48,2.02,.88,'Stop / investigate','Retain failure record',GOLD)
arrow(a,[(6.82,5.9),(7.5,5.9)],GOLD);label(a,7.17,6.13,'No',GOLD)
arrow(a,[(5.65,5.2),(5.65,4.9)],GREEN);label(a,6,5.08,'Yes',GREEN)
panel(a,.35,2.94,9.22,1.95,'2  CORRUPT OBSERVATIONS, THEN RESTRICT ACCESS',GREEN)
text(a,2.05,4.14,'Shared realization:\nclean / moderate / severe',10)
# compact access matrix
text(a,6.7,4.39,'Cross-component                 Inverter-only',10,weight='bold')
for y,history,c1,c2 in [(3.78,'60 days','Full cross','Full inverter'),(3.23,'24 hours','Recent cross','Recent inverter')]:
 text(a,4.25,y+.17,history,10)
 box(a,4.95,y,2.02,.37,c1,color=GREEN);box(a,7.2,y,2.02,.37,c2,color=BLUE)
arrow(a,[(2.8,2.89),(2.8,2.57)],GREEN)
box(a,.35,1.45,4.62,1.09,'3  Run fixed tools; retain receipts','288 episodes x 4 views x 3 quality levels\n= 3,456 paired predictions',GREEN)
box(a,5.58,1.45,3.99,1.09,'4  Score against references','Correctness + coverage + false positives\nInstallation-cluster uncertainty',PURPLE)
arrow(a,[(5.02,2),(5.53,2)],PURPLE)
panel(a,.35,.3,9.22,.88,'SEPARATE CONVERSATIONAL DEVELOPMENT PILOT',BLUE)
text(a,4.96,.6,'24 conversations: tool choice / raw response / strict checks / separate post-hoc sensitivity',10)
save(f,'02_benchmark_design')


# Figure 3: question-to-receipt flow and distinct conversational audit outcomes.
f,a=canvas(8.2,'From status to a supported diagnostic conversation','Logical information flow; output checks below describe evaluation, not a validated runtime safeguard.')
box(a,.35,5.95,3.6,1.02,'Open installation dashboard','Latest complete stored snapshot\nGeneration, load, battery SOC',BLUE)
box(a,5.65,5.95,3.95,1.02,'Ask a plain-language question','Identify task and allowed tool\nSelect the relevant time window',BLUE)
arrow(a,[(4,6.46),(5.6,6.46)],BLUE)
box(a,5.65,4.48,3.95,1.05,'Prepare permitted evidence','Filter time and measurement channels\nCompute deterministic diagnostics',GREEN)
arrow(a,[(7.63,5.9),(7.63,5.58)],BLUE)
cx,cy=3.04,4.99
a.add_patch(Polygon([(cx-1.5,cy),(cx,cy+.67),(cx+1.5,cy),(cx,cy-.67)],fc='#F0F6F3',ec=GREEN,lw=1.4))
text(a,cx,cy,'Does evidence\nresolve the task?',11,weight='bold',color=GREEN)
arrow(a,[(5.6,4.99),(4.6,4.99)],GREEN)
box(a,.35,2.83,3.9,1.02,'Return unknown','State missing or ambiguous evidence\nDo not invent a resolved cause',GOLD)
box(a,5.65,2.83,3.95,1.02,'Return supported diagnosis','Label + supporting measurements\nTime window + decision thresholds',GREEN)
arrow(a,[(3.04,4.27),(3.04,3.9)],GOLD);label(a,2.66,4.05,'No',GOLD)
arrow(a,[(4.4,4.9),(4.95,4.9),(4.95,4.1),(7.63,4.1),(7.63,3.9)],GREEN);label(a,5.5,4.1,'Yes',GREEN)
box(a,2.8,1.35,4.4,1.04,'Generate explanation from the receipt','Preserve the diagnosis or uncertainty\nCite measurement names; retain raw output',BLUE)
arrow(a,[(2.3,2.78),(2.3,2.57),(4,2.57),(4,2.44)],BLUE)
arrow(a,[(7.63,2.78),(7.63,2.57),(6,2.57),(6,2.44)],BLUE)
panel(a,.35,.1,9.25,.91,'AUDIT THE REPORT SEPARATELY FROM DIAGNOSTIC CORRECTNESS',PURPLE)
text(a,4.98,.4,'Pilot: strict JSON 0/24  |  After fence removal: receipt labels 24/24; citation names 15/24',10,color=PURPLE)
arrow(a,[(5,1.3),(5,1.06)],PURPLE)
save(f,'07_conversation_flow')

print('Generated four system/workflow diagrams as PDF, SVG and 300 dpi PNG.')
