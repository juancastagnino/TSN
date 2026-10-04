from pathlib import Path


old = "phase2_recheck"
new = "binary tychos overhaul test phase 2. 2000-2026 3h"
for path in Path("edits/reports").iterdir():
    if path.suffix not in {".md", ".json"}:
        continue
    text = path.read_text(encoding="utf-8")
    if old in text:
        path.write_text(text.replace(old, new), encoding="utf-8")
