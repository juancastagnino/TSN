"""Small compatibility reader for TYCHOS celestial settings schemas."""

from __future__ import annotations

import json
from pathlib import Path


def settings_entries(path: Path) -> list[dict]:
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(document, list):
        return document
    if not isinstance(document, dict):
        raise ValueError("Unsupported celestial settings document")
    if document.get("schemaVersion") == 2:
        entries = document.get("settings")
        if not isinstance(entries, list):
            raise ValueError("Versioned celestial settings have no settings array")
        return entries
    if document.get("schemaVersion") == 3:
        owners = [document.get("referenceFrame"), *document.get("bodies", [])]
        entries = []
        for owner in owners:
            if not isinstance(owner, dict) or not isinstance(owner.get("motion"), dict):
                raise ValueError("Unified celestial model has an invalid motion owner")
            entries.extend(owner["motion"].values())
        return entries
    raise ValueError("Unsupported celestial settings document")


def settings_map(path: Path) -> dict[str, dict]:
    return {item["name"]: item for item in settings_entries(path)}

