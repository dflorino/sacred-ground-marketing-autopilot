"""CLI for Marketing Autopilot HTTP API."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from marketing import API_VERSION, SERVICE_NAME, __version__
from marketing import control, store
from marketing.paths import ensure_dirs

from .http_server import serve


def main(argv: Optional[List[str]] = None) -> int:
    ensure_dirs()
    parser = argparse.ArgumentParser(prog="python3 -m api.cli")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_serve = sub.add_parser("serve")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8792)

    sub.add_parser("version")
    sub.add_parser("summary")

    args = parser.parse_args(argv)

    if args.cmd == "version":
        print(
            json.dumps(
                {
                    "service": SERVICE_NAME,
                    "service_version": __version__,
                    "api_version": API_VERSION,
                }
            )
        )
        return 0

    if args.cmd == "summary":
        drafts = store.list_drafts()
        by = {}
        for d in drafts:
            by[d.get("status", "?")] = by.get(d.get("status", "?"), 0) + 1
        print(
            json.dumps(
                {
                    "phase": control.phase(),
                    "paused": control.is_paused(),
                    "total_drafts": len(drafts),
                    "by_status": by,
                },
                indent=2,
            )
        )
        return 0

    if args.cmd == "serve":
        serve(host=args.host, port=args.port)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
