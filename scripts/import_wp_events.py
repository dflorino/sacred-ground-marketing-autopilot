#!/usr/bin/env python3
"""Refresh data/cache/live_events.json from a TEC-shaped JSON file or stdin.

Usage:
  python3 scripts/import_wp_events.py path/to/export.json
  python3 scripts/import_wp_events.py < export.json

Then:
  python3 -m marketing run --source cache
"""
from __future__ import annotations

import json
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from marketing.ingest import normalize_tec_event, save_cache_events  # noqa: E402


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] != "-":
        with open(sys.argv[1], encoding="utf-8") as fh:
            payload = json.load(fh)
    else:
        payload = json.load(sys.stdin)
    raw = payload.get("events") if isinstance(payload, dict) else payload
    events = [normalize_tec_event(e) for e in raw if e.get("id")]
    path = save_cache_events(
        events,
        {
            "source": payload.get("source", "import") if isinstance(payload, dict) else "import",
            "site": "https://shopsacredground.com",
        },
    )
    print(json.dumps({"ok": True, "path": path, "events": len(events)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
