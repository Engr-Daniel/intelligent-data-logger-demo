from __future__ import annotations

import json

from src.datacontext.context import load_installation_config, load_schema
from src.datacontext.validation import validate_telemetry
from src.storage.local_store import load_telemetry

def main() -> None:
    df = load_telemetry()
    cfg = load_installation_config()
    report = validate_telemetry(df, cfg, load_schema())
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
