from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA = ROOT / "src" / "datacontext" / "schema.yaml"
DEFAULT_CONFIG = ROOT / "config" / "installation.yaml"


def load_schema(path: Path = DEFAULT_SCHEMA) -> dict:
    return yaml.safe_load(path.read_text())


def load_installation_config(path: Path = DEFAULT_CONFIG) -> dict:
    return yaml.safe_load(path.read_text())


def field_context(field: str, schema: dict | None = None) -> dict:
    schema = schema or load_schema()
    fields = schema.get("fields", {})
    if field not in fields:
        raise KeyError(f"Unknown telemetry field: {field}")
    return fields[field]
