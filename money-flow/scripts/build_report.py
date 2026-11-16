#!/usr/bin/env python3
"""Validate official monthly observations and prepare the Pages payload."""
import json
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "latest.json"
TARGET = ROOT / "site" / "data" / "latest.json"
REQUIRED = ("name", "value", "unit", "period", "source_url", "release_date")
def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    errors = []
    for i, row in enumerate(data.get("indicators", [])):
        missing = [key for key in REQUIRED if key not in row]
        if missing: errors.append(f"indicators[{i}] missing {missing}")
        if "value" in row and not isinstance(row["value"], (int, float)):
            errors.append(f"indicators[{i}].value must be numeric")
        if row.get("source_url") and not row["source_url"].startswith("https://"):
            errors.append(f"indicators[{i}].source_url must use HTTPS")
    if errors: raise SystemExit("Data validation failed:\n" + "\n".join(errors))
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {TARGET.relative_to(ROOT)}; {len(data.get('indicators', []))} validated indicators")
if __name__ == "__main__": main()
