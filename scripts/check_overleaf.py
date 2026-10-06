"""Check the portable Overleaf source, figure provenance and compiled PDF."""
from pathlib import Path
import re,json,hashlib,sys,zipfile,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.venv/Lib/site-packages'))
import pymupdf as fitz
project=ROOT/'paper/overleaf';tex=(project/'main.tex').read_text(encoding='utf-8');bib=(project/'references.bib').read_text(encoding='utf-8-sig')
keys=set(re.findall(r'@\w+\{([^,]+),',bib));cited={k for group in re.findall(r'\\cite\{([^}]+)\}',tex) for k in group.split(',')}
assert cited==keys and len(keys)==12
labels=re.findall(r'\\label\{([^}]+)\}',tex);assert len(labels)==len(set(labels));assert set(re.findall(r'\\ref\{([^}]+)\}',tex))<=set(labels)
assert 'ZZTOKEN' not in tex
figs=re.findall(r'\\includegraphics\[[^]]*\]\{([^}]+)\}',tex);assert len(figs)==7
manifest=json.loads((project/'figs/provenance.json').read_text())
for name,digest in manifest['inputs'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
for name,digest in manifest['outputs'].items():assert hashlib.sha256((project/'figs'/name).read_bytes()).hexdigest()==digest,name
for name in figs:
 with fitz.open(project/name) as d:
  assert len(d)==1 and not d[0].get_images(),'Figure should be vector-only: '+name
  assert d[0].get_fonts(),name
log=(project/'main.log').read_text(encoding='utf-8',errors='replace')
for problem in ['Overfull \\hbox','Overfull \\vbox','There were undefined references','Citation `','Missing character:','! LaTeX Error']:
 assert problem not in log,problem
pdf=fitz.open(project/'main.pdf');alltext='\n'.join(p.get_text() for p in pdf)
assert '233' in alltext and '97.1' in alltext and '90.0' in alltext
assert '??' not in alltext
outside=[]
for i,page in enumerate(pdf):
 assert len(page.get_text().strip())>50,(i,'nearly blank page')
 for b in page.get_text('blocks'):
  if b[0]<-1 or b[1]<-1 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1:outside.append(i+1)
assert not outside,outside
out=ROOT/'paper/submission';out.mkdir(exist_ok=True)
shutil.copyfile(project/'main.pdf',out/'NASEF2026_Full_Paper_Overleaf.pdf')
assets=['main.tex','references.bib','README.md','figs/provenance.json']+[str(p.relative_to(project)).replace('\\','/') for p in sorted((project/'figs').glob('*')) if p.suffix in ['.pdf','.png','.svg']]
with zipfile.ZipFile(out/'NASEF2026_Overleaf.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name in assets:z.write(project/name,name)
result={'pages':len(pdf),'figures':len(figs),'tables':len(re.findall(r'\\begin\{table\}',tex)),'cited_references':len(keys),'vector_figures':True,'source_hashes_verified':True,'latex_layout_errors':0,'files_in_zip':len(assets),'pdf_sha256':hashlib.sha256((project/'main.pdf').read_bytes()).hexdigest()}
(out/'overleaf_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
preview=ROOT/'.venv/overleaf_review';preview.mkdir(exist_ok=True)
for i,page in enumerate(pdf):page.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(preview/f'page_{i+1:02}.png')
