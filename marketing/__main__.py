"""CLI: python3 -m marketing <command>"""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from . import __version__
from . import control, pipeline, store
from .paths import ensure_dirs


def _print(obj) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def main(argv: Optional[List[str]] = None) -> int:
    ensure_dirs()
    parser = argparse.ArgumentParser(
        prog="python3 -m marketing",
        description="Sacred Ground Marketing Autopilot v1",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Generate draft batch from WordPress events")
    p_run.add_argument(
        "--source",
        choices=["auto", "live", "live-strict", "cache", "fixture"],
        default="auto",
        help="Event source. Automations must use live-strict (fail hard, no stale cache).",
    )

    p_list = sub.add_parser("list", help="List drafts")
    p_list.add_argument("--status", default=None)

    p_show = sub.add_parser("show", help="Show one draft")
    p_show.add_argument("draft_id")

    p_approve = sub.add_parser("approve", help="Approve a draft (Phase 1: no publish)")
    p_approve.add_argument("draft_id")

    p_reject = sub.add_parser("reject", help="Reject a draft")
    p_reject.add_argument("draft_id")
    p_reject.add_argument("--reason", default="")

    sub.add_parser("pause", help="Pause autopilot (blocks schedule/publish)")
    sub.add_parser("resume", help="Resume autopilot")

    p_phase = sub.add_parser("set-phase", help="Set phase 1|2|3")
    p_phase.add_argument("phase", type=int)

    p_skip = sub.add_parser("skip", help="Manual override: skip a fingerprint")
    p_skip.add_argument("--fingerprint", required=True)
    p_skip.add_argument("--reason", default="manual_override")

    sub.add_parser("status", help="Show pause/phase/counts")
    sub.add_parser("review", help="Human-readable review queue for Phase 1")
    sub.add_parser("version", help="Print version")

    args = parser.parse_args(argv)

    if args.cmd == "version":
        _print({"service": "sacred-ground-marketing-autopilot", "version": __version__})
        return 0

    if args.cmd == "status":
        drafts = store.list_drafts()
        by = {}
        for d in drafts:
            by[d.get("status")] = by.get(d.get("status"), 0) + 1
        _print(
            {
                "control": control.load_control(),
                "draft_counts": by,
                "total_drafts": len(drafts),
                "posted_fingerprints": len(store.load_posted().get("fingerprints") or {}),
            }
        )
        return 0

    if args.cmd == "review":
        drafts = store.list_drafts(status="draft")
        print(f"Phase {control.phase()} · paused={control.is_paused()} · {len(drafts)} drafts pending\n")
        for d in drafts:
            titles = ", ".join(e.get("title", "?") for e in (d.get("events") or [])[:4])
            print(f"[{d['campaign']}/{d['platform']}] {d['id']}")
            print(f"  events: {titles}")
            print(f"  image:  {d['image'].get('source')} — {d['image'].get('recommendation')}")
            print(f"  sched:  {d['schedule_recommendation'].get('recommended_at')}")
            print(f"  block:  {d.get('publish_blocked_reason')}")
            hook = (d.get("caption") or {}).get("hook") or ""
            print(f"  hook:   {hook}")
            print()
        print("Approve: python3 -m marketing approve DRAFT_ID")
        print("Nothing publishes in Phase 1.")
        return 0

    if args.cmd == "run":
        result = pipeline.generate_batch(source=args.source)
        _print(result)
        return 0 if result.get("ok") else 1

    if args.cmd == "list":
        _print(store.list_drafts(status=args.status))
        return 0

    if args.cmd == "show":
        d = store.get_draft(args.draft_id)
        if not d:
            print(f"Unknown draft: {args.draft_id}", file=sys.stderr)
            return 1
        _print(d)
        return 0

    if args.cmd == "approve":
        _print(pipeline.approve(args.draft_id))
        return 0

    if args.cmd == "reject":
        _print(pipeline.reject(args.draft_id, reason=args.reason))
        return 0

    if args.cmd == "pause":
        _print(control.pause())
        return 0

    if args.cmd == "resume":
        _print(control.resume())
        return 0

    if args.cmd == "set-phase":
        _print(control.set_phase(args.phase))
        return 0

    if args.cmd == "skip":
        store.skip_fingerprint(args.fingerprint, args.reason)
        _print({"ok": True, "fingerprint": args.fingerprint, "reason": args.reason})
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
