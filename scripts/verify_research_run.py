"""Verify archived offline evidence and paired-design integrity without API calls."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def verify(folder):
    manifest=json.loads((folder/"manifest.json").read_text())
    assert manifest["status"]=="complete", "Run did not complete"
    for name,digest in manifest["artifact_sha256"].items():
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest, f"Artifact changed: {name}"
    for name,digest in manifest["code_sha256"].items():
        relative=Path(*name.replace("\\", "/").split("/"))
        assert hashlib.sha256((folder/"source"/relative).read_bytes()).hexdigest()==digest, f"Source snapshot changed: {name}"
    with (folder/"predictions.csv").open() as f: rows=list(csv.DictReader(f))
    protocol=json.loads((folder/"protocol.json").read_text())
    keys={(r['case_id'],r['stress'],r['condition']) for r in rows}
    assert len(keys)==len(rows), "Duplicate predictions"
    cases={r['case_id'] for r in rows}
    assert len(rows)==len(cases)*len(protocol['conditions'])*len(protocol['stress_levels'])
    for r in rows:
        assert (r['correct']=='True')==(r['expected']==r['predicted']), "Scoring mismatch"
    evidence=[json.loads(line) for line in (folder/'receipts.jsonl').read_text().splitlines()]
    assert len(evidence)==len(rows)
    for row in evidence:
        assert row['predicted']==row['evidence']['label']
        assert not {'oracle_label','episode','seed'} & set(row['evidence']['columns_available'])
    physical=[json.loads(line) for line in (folder/'physical_checks.jsonl').read_text().splitlines()]
    assert len(physical)==len(cases) and all(x['passed'] for x in physical)
    print(f"Verified {len(cases)} episodes, {len(rows)} paired predictions, all hashes and physical checks.")


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('run',type=Path)
    verify(parser.parse_args().run)
