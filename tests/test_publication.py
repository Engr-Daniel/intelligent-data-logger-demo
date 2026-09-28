"""Publication checks: evidence fidelity and a strictly bounded static artifact."""
import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('public_site',ROOT/'scripts/build_public_site.py')
site=importlib.util.module_from_spec(spec);spec.loader.exec_module(site)
def test_demo_evidence_is_identical_to_archive():
    assert len(site.validate_demo()['scenarios'])==6

def test_static_build_contains_only_reviewed_files(tmp_path):
    site.build(tmp_path)
    files={p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob('*') if p.is_file()}
    assert files=={'index.html','research.html','app.js','research.js','styles.css','data/experiment.json','data/research.json','data/outage.json','.nojekyll','publication.json'}
    manifest=json.loads((tmp_path/'publication.json').read_text())
    for name,digest in manifest['sha256'].items():assert site.sha(tmp_path/name)==digest
    assert 'href="/"' not in (tmp_path/'index.html').read_text(encoding='utf-8')

def test_primary_and_exploratory_live_scores_are_separate():
    source=ROOT/'reports/research/20260928T072939445717Z_live_development'
    primary=json.loads((source/'summary.json').read_text())
    secondary=json.loads((ROOT/'reports/research/20260928_live_format_sensitivity/summary.json').read_text())
    assert primary['completed']==24 and primary['counts']['valid_json']==0
    assert secondary['counts']['valid_json']==24
    assert secondary['source_sha256']['conversations.jsonl']==site.sha(source/'conversations.jsonl')

def test_outage_trace_matches_archive_hash_and_has_restoration():
    data=json.loads((site.ASSETS/'data/outage.json').read_text())
    manifest=json.loads((site.DEMO/'run_manifest.json').read_text())
    assert data['sha256']==next(v for k,v in manifest['sha256'].items() if k.replace('\\','/')=='data/processed/telemetry.csv')
    rows=data['rows'];assert len(rows)==37
    assert rows[0]['grid_available']==rows[-1]['grid_available']==1
    assert sum(r['grid_available']==0 for r in rows)==12
    assert all(r['unmet_load_w']==0 for r in rows if r['grid_available']==0)
