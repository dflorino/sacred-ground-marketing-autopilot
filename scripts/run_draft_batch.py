#!/usr/bin/env python3
"""One-shot: generate Phase 1 draft batch and print a review summary."""
from __future__ import annotations

import json
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from marketing import pipeline, store  # noqa: E402
from marketing.paths import ensure_dirs  # noqa: E402


def main() -> int:
    ensure_dirs()
    source = sys.argv[1] if len(sys.argv) > 1 else "auto"
    result = pipeline.generate_batch(source=source)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n--- Review queue ---")
    for d in store.list_drafts(status="draft"):
        print(
            f"{d['id']}\t{d['campaign']}/{d['platform']}\t"
            f"events={len(d['events'])}\timage={d['image']['source']}\t"
            f"sched={d['schedule_recommendation']['recommended_at']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
