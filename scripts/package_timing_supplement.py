"""Package the reviewed timing extension as an overlay on the public repository."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
run='20261006T022136185304Z_detection_delay'
files=[ROOT/p for p in ['paper/TIMING_SUPPLEMENT.md','paper/overleaf/figs/06_detection_delay.png','paper/overleaf/figs/06_detection_delay.pdf','scripts/build_timing_supplement_word.py','docs/DETECTION_DELAY_PROTOCOL.md','docs/DETECTION_DELAY_GUIDE.md',
 'scripts/analyze_detection_delay.py','scripts/verify_detection_delay.py','scripts/summarize_detection_delay.py',
 'scripts/package_timing_supplement.py','tests/test_detection_delay.py','config/research_protocol.json',
 'src/research/policy.py','src/research/simulation.py']]
for name in [run,run+'_interpretation']:
 files.extend(p for p in (ROOT/'reports/research'/name).rglob('*') if p.is_file())
readme='''# Exploratory timing reproducibility supplement

This is an overlay for https://github.com/Engr-Daniel/intelligent-data-logger-demo
(original benchmark release b45331e). Extract into a checkout of that repository,
install its Python dependencies, then follow docs/DETECTION_DELAY_GUIDE.md.
The original frozen benchmark in that repository is required for comparison.

Verify the supplied archive:
python scripts/verify_detection_delay.py reports/research/20261006T022136185304Z_detection_delay

To rerun, use python scripts/analyze_detection_delay.py. It creates a fresh archive
and does not replace the supplied one. No API credentials or paid calls are needed.

The analysis is exploratory, specified after exposure to proposed timing claims.
It uses synthetic installations and unchanged policy thresholds, not field data.
Read the protocol for reference dates, missing detections, phases and persistence.
Raw evidence and an independently checked interpretation are both included.

FILES_SHA256.json gives SHA-256 digests of every supplied source/evidence file.
'''
manifest={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
out=ROOT/'paper/submission/NASEF2026_Timing_Reproducibility.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.relative_to(ROOT).as_posix())
 z.writestr('README_TIMING_SUPPLEMENT.md',readme)
 z.writestr('FILES_SHA256.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for name,digest in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
print(json.dumps({'file':str(out),'source_evidence_files':len(files),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))
