"""Zernio / ML Social client — upload media + create posts."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


API_BASE = os.environ.get("ZERNIO_API_BASE", "https://zernio.com/api/v1").rstrip("/")


class ZernioError(RuntimeError):
    def __init__(self, message: str, *, status: Optional[int] = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body


def api_key() -> Optional[str]:
    for name in ("ZERNIO_API_KEY", "ML_SOCIAL_API_KEY", "MLS_API_KEY"):
        val = (os.environ.get(name) or "").strip()
        if val:
            return val
    # Optional local secrets file (gitignored)
    from .paths import ROOT

    for rel in (".env", "config/secrets.local.json"):
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        if rel.endswith(".json"):
            try:
                data = json.loads(open(path, encoding="utf-8").read())
            except Exception:
                continue
            for name in ("ZERNIO_API_KEY", "zernio_api_key", "api_key"):
                if data.get(name):
                    return str(data[name]).strip()
        else:
            for line in open(path, encoding="utf-8"):
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() in ("ZERNIO_API_KEY", "ML_SOCIAL_API_KEY") and v.strip():
                    return v.strip().strip('"').strip("'")
    return None


def configured() -> bool:
    return bool(api_key())


def _request(
    method: str,
    path: str,
    *,
    body: Optional[Dict[str, Any]] = None,
    raw_body: Optional[bytes] = None,
    content_type: Optional[str] = None,
    auth: bool = True,
) -> Dict[str, Any]:
    url = path if path.startswith("http") else f"{API_BASE}{path}"
    data = raw_body
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif content_type and raw_body is not None:
        headers["Content-Type"] = content_type
    if auth:
        key = api_key()
        if not key:
            raise ZernioError("missing_zernio_api_key")
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8") or "{}"
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(err_body) if err_body else {}
        except Exception:
            parsed = {"error": err_body}
        raise ZernioError(
            parsed.get("error") or parsed.get("message") or f"HTTP {exc.code}",
            status=exc.code,
            body=parsed,
        ) from exc


def upload_image(path: str, filename: Optional[str] = None) -> str:
    """Presign + PUT local image; return public https URL."""
    filename = filename or os.path.basename(path)
    content_type = "image/png" if filename.lower().endswith(".png") else "image/jpeg"
    presign = _request(
        "POST",
        "/media/presign",
        body={"filename": filename, "contentType": content_type},
    )
    upload_url = presign.get("uploadUrl") or presign.get("upload_url")
    public_url = presign.get("publicUrl") or presign.get("public_url")
    if not upload_url or not public_url:
        raise ZernioError("presign_missing_urls", body=presign)
    with open(path, "rb") as fh:
        raw = fh.read()
    _request(
        "PUT",
        upload_url,
        raw_body=raw,
        content_type=content_type,
        auth=False,
    )
    if not str(public_url).startswith("https://"):
        raise ZernioError("upload_did_not_return_https", body=presign)
    return str(public_url)


def create_post(payload: Dict[str, Any]) -> Dict[str, Any]:
    """POST /posts — schedule or publishNow."""
    # Strip internal helper fields
    body = {
        k: v
        for k, v in payload.items()
        if k not in ("draft_id", "fingerprint") and v is not None
    }
    return _request("POST", "/posts", body=body)


def publish_draft_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure media is a public https URL (upload local file if needed),
    then create the Zernio post.
    """
    media = list(payload.get("mediaItems") or [])
    fixed: List[Dict[str, Any]] = []
    for item in media:
        url = (item or {}).get("url") or ""
        if url.startswith("https://"):
            fixed.append({"type": item.get("type") or "image", "url": url})
        elif url.startswith("file://") or (url and os.path.exists(url)):
            local = url.replace("file://", "")
            public = upload_image(local)
            fixed.append({"type": "image", "url": public})
        else:
            raise ZernioError(f"invalid_media_url:{url}")
    payload = dict(payload)
    payload["mediaItems"] = fixed
    # Zernio platforms entries may include platform name; keep accountId as configured
    platforms = []
    for p in payload.get("platforms") or []:
        entry = {"accountId": p["accountId"]}
        if p.get("platform"):
            entry["platform"] = p["platform"]
        platforms.append(entry)
    payload["platforms"] = platforms
    return create_post(payload)
