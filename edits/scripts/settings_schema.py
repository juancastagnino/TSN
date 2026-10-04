"""Small compatibility reader for TYCHOS celestial settings schemas."""

from __future__ import annotations

import json
from pathlib import Path


def settings_entries(path: Path) -> list[dict]:
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(document, list):
        return document
    if not isinstance(document, dict) or document.get("schemaVersion") != 2:
        raise ValueError("Unsupported celestial settings document")
    entries = document.get("settings")
    if not isinstance(entries, list):
        raise ValueError("Versioned celestial settings have no settings array")
    return entries


def settings_map(path: Path) -> dict[str, dict]:
    return {item["name"]: item for item in settings_entries(path)}

