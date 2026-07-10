"""Optional read-only HTTP surface for Dashboard later."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Tuple
from urllib.parse import parse_qs, urlparse

from marketing import API_VERSION, SERVICE_NAME, __version__
from marketing import control, store
from marketing.paths import ensure_dirs


def _json(obj: Any) -> bytes:
    return json.dumps(obj, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"


def route(path: str, query: Dict[str, str]) -> Tuple[int, Any]:
    ensure_dirs()
    p = urlparse(path).path.rstrip("/") or "/"

    if p == "/health":
        return 200, {
            "status": "ok",
            "service": SERVICE_NAME,
            "service_version": __version__,
            "api_version": API_VERSION,
            "phase": control.phase(),
            "paused": control.is_paused(),
            "read_only": True,
        }

    base = f"/api/{API_VERSION}"
    if not p.startswith(base):
        return 404, {"error": "not_found", "path": p}

    sub = p[len(base) :] or "/"

    if sub == "/summary":
        drafts = store.list_drafts()
        by: Dict[str, int] = {}
        for d in drafts:
            by[d.get("status", "?")] = by.get(d.get("status", "?"), 0) + 1
        return 200, {
            "service": SERVICE_NAME,
            "api_version": API_VERSION,
            "phase": control.phase(),
            "paused": control.is_paused(),
            "total_drafts": len(drafts),
            "by_status": by,
            "posted_fingerprints": len(store.load_posted().get("fingerprints") or {}),
            "read_only": True,
        }

    if sub == "/drafts":
        status = query.get("status")
        return 200, {"drafts": store.list_drafts(status=status)}

    if sub.startswith("/drafts/"):
        did = sub[len("/drafts/") :]
        d = store.get_draft(did)
        if not d:
            return 404, {"error": "not_found", "id": did}
        return 200, d

    return 404, {"error": "not_found", "path": p}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # quieter
        pass

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        qs = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        code, body = route(parsed.path, qs)
        raw = _json(body)
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("X-Read-Only", "true")
        self.send_header("X-SG-Service", SERVICE_NAME)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self) -> None:
        self._reject_write()

    def do_PUT(self) -> None:
        self._reject_write()

    def do_PATCH(self) -> None:
        self._reject_write()

    def do_DELETE(self) -> None:
        self._reject_write()

    def _reject_write(self) -> None:
        raw = _json(
            {
                "error": "method_not_allowed",
                "message": "HTTP is read-only in Phase 1. Use CLI for approve/pause.",
            }
        )
        self.send_response(405)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def serve(host: str = "127.0.0.1", port: int = 8792) -> None:
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"{SERVICE_NAME} listening on http://{host}:{port}")
    httpd.serve_forever()
