"""Build editable Overleaf main.tex from the reviewed manuscript."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'paper/overleaf'
front=json.loads((ROOT/'paper/front_matter.json').read_text())
keys=['king2004','holmgren2018','jordan2018','yao2023','schick2023','geifman2017','sunspec2018','sengupta2024','utama2023','sairam2020','gsc2026','oghifo2026']
def tex(s):
 slots=[]
 def stash(v):slots.append(v);return f'ZZTOKEN{len(slots)-1}ZZ'
 s=re.sub(r'https?://[^\s]+',lambda m:stash(r'\url{'+m[0].rstrip('.;,')+'}')+m[0][len(m[0].rstrip('.;,')):],s)
 s=re.sub(r'2026[0-9TZ]+_[a-z_]+',lambda m:stash(r'\nolinkurl{'+m[0]+'}'),s)
 s=re.sub(r'\[(\d+(?:,\d+)*)\]',lambda m:stash(r'\cite{'+','.join(keys[int(n)-1] for n in m[1].split(','))+'}'),s)
 s=re.sub(r'Table ([1-9])',lambda m:stash(r'Table~\ref{tab:'+m[1]+'}'),s)
 s=re.sub(r'Figure ([1-7])',lambda m:stash(r'Figure~\ref{fig:'+['care','boundary','flow','design','clean','stress','pilot'][int(m[1])-1]+'}'),s)
 for a,b in [('&',r'\&'),('%',r'\%'),('_',r'\_'),('#',r'\#'),('$',r'\$'),('–','--'),('—','---'),('×',r'\(\times\)'),('°C',r'\(^{\circ}\mathrm{C}\)'),('²',r'\(^{2}\)'),('≥',r'\(\geq\)'),('→',r'\(\rightarrow\)')]:s=s.replace(a,b)
 for i,v in enumerate(slots):s=s.replace(f'ZZTOKEN{i}ZZ',v)
 return s
figures={
 'care':('00_care_loop','The proposed care loop. Synthetic observations substitute for physical measurement; storage and diagnosis are implemented. Conversational reporting is implemented but its output contract failed in the pilot. Field acquisition, physical action and outcome verification remain proposed. Feedback from verified intervention outcomes is proposed, not a tested closed loop.'),
 'timing':('06_detection_delay','Exploratory timing under the unchanged policy. (a) Clean observations and one positive check, with detection scored on 20 reference-crossing declines. (b) Daily full-history cross-component access, comparing one positive with three consecutive positives; false-trend-alert probability uses 24 installations and the union across three non-decline controls. Error bars are 95% installation-bootstrap intervals; periodic schedule phases are averaged within installation.'),
 'boundary':('01_evidence_boundary','Diagnostic and conversational paths with evaluation-only references. Reference labels are unavailable to diagnosis. Reporting checks use the raw model output and tool receipt; oracle agreement is scored separately. The diagram denotes logical separation, not evaluation by an independent research group.'),
 'design':('02_benchmark_design','Matched information-access design. Cross-component access includes inverter channels plus irradiance, ambient temperature, load, battery and grid measurements. The four views share a policy and each corrupted realization; they are not optimized competing systems.'),
 'clean':('03_correctness_coverage','Clean-data correctness and coverage under the shared policy. Correctness uses 240 identifiable cases per condition; coverage uses all 288 cases. Points show installation means and bars show 95% installation-cluster bootstrap intervals. Zero-width intervals indicate identical scores within this generator.'),
 'stress':('04_corruption_robustness','Correct diagnostic labels across observation-quality levels. Error bars are 95% installation-cluster bootstrap intervals from the frozen archive. Slight horizontal offsets improve legibility. Lines connect experimental conditions rather than measurements through time.'),
 'pilot':('05_reporting_failures','Conversational reporting checks for the same 24 conversations. Intended tool selection was 24/24. All strict outputs failed JSON parsing, so downstream checks received no credit. Post-hoc removal of one Markdown fence is a separate sensitivity analysis, not a replacement primary result.')}
figures['flow']=('07_conversation_flow','')
for cap,asset in re.findall(r'!\[(.*?)\]\(overleaf/figs/(.*?)\.png\)',(ROOT/'paper/FULL_PAPER.md').read_text(encoding='utf-8')):
 for key,(name,_) in list(figures.items()):
  if name==asset and key in ['care','boundary','flow','design']:figures[key]=(name,re.sub(r'^Figure \d+\. ','',cap))

def figure(k):
 name,caption=figures[k]
 return '\n'+r'\begin{figure}[!htbp]'+'\n'+r'\centering'+'\n'+r'\includegraphics[width=\linewidth]{figs/'+name+'.pdf}\n'+r'\caption['+tex(caption.split('.')[0])+']{'+tex(caption)+'}\n'+r'\label{fig:'+k+'}\n'+r'\end{figure}'+'\n'
s=(ROOT/'paper/FULL_PAPER.md').read_text(encoding='utf-8');title=s.splitlines()[0][2:];abstract=s.split('## Abstract\n\n')[1].split('\n\nKeywords:')[0];keywords=s.split('Keywords: ')[1].split('\n')[0];body=s.split('## 1. Introduction',1)[1].split('## References')[0];body='## 1. Introduction'+body
preamble=r'''% Main editable Overleaf source. Compile with pdfLaTeX + BibTeX (XeLaTeX also supported).
% Provisional author layout: no full-paper template or page limit was supplied.
\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{newtxtext,newtxmath}
\usepackage[margin=23mm,headheight=14pt]{geometry}
\usepackage{microtype,graphicx,booktabs,tabularx,array,ragged2e}
\usepackage{caption,placeins,enumitem}
\usepackage[numbers,sort&compress]{natbib}
\usepackage{xcolor}
\definecolor{ink}{HTML}{203747}
\definecolor{accent}{HTML}{176454}
\usepackage[colorlinks=true,linkcolor=ink,citecolor=ink,urlcolor=accent,breaklinks=true]{hyperref}
\usepackage{xurl}
\usepackage{fancyhdr}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small Oyewale and Meyer-Petgrave}
\fancyhead[R]{\small Evidence-grounded solar diagnostics}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.3pt}
\captionsetup{font=small,labelfont=bf,justification=justified,singlelinecheck=false}
\setlength{\parskip}{3pt}\setlength{\parindent}{1em}
\linespread{1.08}
\clubpenalty=10000\widowpenalty=10000\displaywidowpenalty=10000
\setlength{\emergencystretch}{2em}
\setcounter{topnumber}{3}\setcounter{bottomnumber}{2}\setcounter{totalnumber}{5}
\renewcommand{\topfraction}{0.9}\renewcommand{\bottomfraction}{0.8}\renewcommand{\textfraction}{0.08}\renewcommand{\floatpagefraction}{0.75}
\newcolumntype{Y}{>{\RaggedRight\arraybackslash}X}
\title{\bfseries TITLE}
\author{Oyewale, D.O.\textsuperscript{1}\quad and\quad Meyer-Petgrave, F.\textsuperscript{1}\\[5pt]
\small \textsuperscript{1}Petgrave.io Technologies Ltd, Nigeria\\
\small Correspondence: \href{mailto:daniel.oyewale@petgrave.io}{daniel.oyewale@petgrave.io}}
\date{}
\begin{document}
\maketitle\thispagestyle{plain}
\begin{center}
{\small\bfseries CONFERENCE\par}
\vspace{3pt}
{\small SUBTHEME\par}
\end{center}
\begin{abstract}
ABSTRACT
\end{abstract}
\noindent\textbf{Keywords:} KEYWORDS
\clearpage
\renewcommand{\contentsname}{Table of contents}
\tableofcontents
\clearpage
\addcontentsline{toc}{section}{List of figures}
\listoffigures
\medskip
\addcontentsline{toc}{section}{List of tables}
\listoftables
\clearpage
\section*{List of abbreviations}
\addcontentsline{toc}{section}{List of abbreviations}
\begin{tabularx}{\linewidth}{@{}lY@{}}
ABBREVIATIONS
\end{tabularx}
\clearpage
'''.replace('CONFERENCE',tex(front['conference'])).replace('SUBTHEME',tex(front['subtheme'])).replace('ABBREVIATIONS','\n'.join(tex(k)+' & '+tex(v)+r' \\' for k,v in front['abbreviations'].items())).replace('TITLE',tex(title)).replace('ABSTRACT',tex(abstract)).replace('KEYWORDS',tex(keywords))
lines=body.splitlines();out=[];i=0;table=0;caption=''
while i<len(lines):
 line=lines[i].strip()
 if not line:i+=1;continue
 if line.startswith('## '):
  name=re.sub(r'^\d+\. ','',line[3:]);out.append(r'\FloatBarrier'+'\n'+r'\section{'+tex(name)+'}')
 elif line.startswith('### '):out.append((r'\FloatBarrier'+'\n' if any(line.startswith(x) for x in ['### 3.2','### 3.6','### 4.2','### 4.3','### 4.4']) else '')+r'\subsection{'+tex(re.sub(r'^\d+\.\d+ ','',line[4:]))+'}')
 elif re.match(r'Table \d+\.',line):caption=re.sub(r'^Table \d+\. ','',line)
 elif line.startswith('|'):
  table+=1;rs=[]
  while i<len(lines) and lines[i].strip().startswith('|'):
   cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
   if not all(re.fullmatch('[: -]+',c) for c in cells):rs.append(cells)
   i+=1
  cols=len(rs[0]);spec='Y'*cols
  if table==3:spec=r'>{\hsize=1.2\hsize}Y>{\hsize=1.3\hsize}Y'+r'>{\hsize=.833333\hsize}Y'*3
  out.append(r'\begin{table}[!htbp]\centering\small'+'\n'+r'\caption['+tex(caption.split('.')[0])+']{'+tex(caption)+'}'+r'\label{tab:'+str(table)+'}\n'+r'\renewcommand{\arraystretch}{1.18}\setlength{\tabcolsep}{4pt}'+'\n'+r'\begin{tabularx}{\linewidth}{@{}'+spec+'@{}}\n'+r'\toprule')
  for j,cells in enumerate(rs):
   out.append(' & '.join((r'\textbf{'+tex(c)+'}') if j==0 else tex(c) for c in cells)+r' \\')
   if j==0:out.append(r'\midrule')
  out.append(r'\bottomrule\end{tabularx}\end{table}')
  continue
 elif line.startswith('!['):
  out.append(figure(next(k for k,(name,_) in figures.items() if name in line)))
 else:out.append(tex(line)+'\n')
 i+=1
end=r'''
\FloatBarrier
\bibliographystyle{unsrtnat}
\bibliography{references}
\end{document}
'''
(OUT/'main.tex').write_text(preamble+'\n\n'.join(out)+end,encoding='utf-8')
print('Built main.tex with seven figures, four tables and twelve cited references.')
