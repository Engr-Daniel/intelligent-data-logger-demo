# Offline experiment run — 21 September 2026

The configured synthetic experiment completed successfully.

- Telemetry: 34,560 rows, 120 days, five-minute cadence, seed 42.
- Synthetic time window: 1 August–28 November 2026 (Africa/Lagos).
- Physical validation: PASS.
- M6: all six scenarios PASS on every applicable dimension.
- Canonical query evidence paths: all eleven PASS.
- Regression suite: 80 passed in 173.92 seconds; see `tests.xml`.
- M5 retains its expected battery capability gap and partial dropout localization.
- Existing milestone reports were preserved byte-for-byte. Regenerated ground truth differs from the original only in line endings.

See `m6_dry_run.md` for scenario-level results, `physical_validation.json` for physical checks,
`offline_walkthrough.json` for the eleven questions and answers, and `run_manifest.json`
for versions and source/input hashes. The experiment itself took approximately 93 seconds,
excluding dependency installation and regression tests.

This run used Python 3.10.0, pandas 2.3.3 and NumPy 2.2.6. The README recommends
Python 3.11 or newer; that interpreter was not available in this workspace.
The Windows virtual-environment launcher failed, so dependencies were installed with
`python -m pip install --target .venv/Lib/site-packages -r requirements-dev.txt`.
The working interpreter loaded those local packages through `PYTHONPATH`.

Commands used from the repository root (PowerShell):

```powershell
$env:PYTHONPATH = 'C:\intelligent-data-logger-demo\.venv\Lib\site-packages'
$env:PYTHONNOUSERSITE = '1'
python scripts/run_experiment.py
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
python -m pytest -q --junitxml=reports/runs/20260921T055826825005Z/tests.xml
```

The runner creates a new timestamped folder on each invocation. Adjust the test-output
path when recording a subsequent run.

These results cover deterministic synthetic functionality. No live Claude API calls
were made; the tool-loop tests use mocked responses. This run does not measure live
LLM answer quality or real-world diagnostic accuracy.
