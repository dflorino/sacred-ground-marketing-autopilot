"""Phase 2+ publish gate + Zernio HTTP schedule/publish."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from . import control, store
from .paths import accounts

ZERNIO_API_BASE = os.environ.get("ZERNIO_API_BASE", "https://zernio.com/api/v1")


def can_schedule(draft: Dict[str, Any]) -> tuple[bool, str]:
    if control.is_paused():
        return False, "autopilot_paused"
    if control.phase() < 2:
        return False, "phase_1_drafts_only"
    from .paths import settings

    camp = (settings().get("campaigns") or {}).get(draft.get("campaign") or "") or {}
    auto = bool(camp.get("auto_publish"))
    if (
        draft.get("approval_status") != "approved"
        and control.phase() < 3
        and not auto
    ):
        return False, "awaiting_approval"
    if draft.get("status") in ("posted", "scheduled", "skipped", "rejected"):
        return False, f"status_{draft.get('status')}"
    img = draft.get("image") or {}
    if not img.get("url"):
        return False, "missing_image_url"
    return True, "ok"


def zernio_api_key() -> Optional[str]:
    key = (os.environ.get("ZERNIO_API_KEY") or "").strip()
    return key or None


def schedule_payload(draft: Dict[str, Any]) -> Dict[str, Any]:
    """Build Zernio / ML Social create-post body."""
    platform = draft["platform"]
    acct = accounts().get(platform) or {}
    account_id = acct.get("accountId")
    if not account_id:
        raise ValueError(f"No accountId configured for {platform}")
    media = []
    img = draft.get("image") or {}
    if img.get("url"):
        media.append({"url": img["url"], "type": "image"})
    sched = (draft.get("schedule_recommendation") or {}).get("recommended_at")
    tz = draft.get("timezone") or accounts().get("timezone") or "America/Chicago"
    publish_now = _should_publish_now(sched, tz)
    body: Dict[str, Any] = {
        "content": (draft.get("caption") or {}).get("text") or "",
        "platforms": [{"platform": platform, "accountId": account_id}],
        "timezone": tz,
        "publishNow": publish_now,
    }
    if media:
        body["mediaItems"] = media
    if sched and not publish_now:
        body["scheduledFor"] = _to_zernio_local(sched, tz)
    return {
        **body,
        "draft_id": draft["id"],
        "fingerprint": draft["fingerprint"],
    }


def _should_publish_now(recommended_at: Optional[str], tz_name: str) -> bool:
    if not recommended_at:
        return True
    try:
        when = datetime.fromisoformat(recommended_at)
        if when.tzinfo is None:
            when = when.replace(tzinfo=ZoneInfo(tz_name))
        now = datetime.now(ZoneInfo(tz_name))
        return when <= now
    except Exception:
        return False


def _to_zernio_local(iso_ts: str, tz_name: str) -> str:
    """Zernio examples use local wall time without offset, plus timezone field."""
    when = datetime.fromisoformat(iso_ts)
    if when.tzinfo is None:
        when = when.replace(tzinfo=ZoneInfo(tz_name))
    local = when.astimezone(ZoneInfo(tz_name))
    return local.strftime("%Y-%m-%dT%H:%M:%S")


def mark_scheduled(draft_id: str, external: Optional[Dict] = None) -> Dict[str, Any]:
    return store.update_draft(
        draft_id,
        status="scheduled",
        publish_blocked_reason=None,
        external=external or {},
    )


def mark_posted(draft_id: str, external: Optional[Dict] = None) -> Dict[str, Any]:
    d = store.update_draft(
        draft_id,
        status="posted",
        publish_blocked_reason=None,
        external=external or {},
    )
    fp = d.get("fingerprint")
    if fp:
        store.mark_posted(fp, draft_id, meta={"external": external or {}})
    return d


def _http_json(
    method: str,
    path: str,
    *,
    body: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    key = zernio_api_key()
    if not key:
        raise RuntimeError("missing_zernio_api_key")
    url = f"{ZERNIO_API_BASE.rstrip('/')}/{path.lstrip('/')}"
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"zernio_http_{exc.code}: {detail[:500]}") from exc


def create_zernio_post(payload: Dict[str, Any]) -> Dict[str, Any]:
    """POST /posts — strips local-only keys."""
    body = {
        k: v
        for k, v in payload.items()
        if k not in ("draft_id", "fingerprint") and v is not None
    }
    return _http_json("POST", "posts", body=body)


def publish_draft(draft_id: str) -> Dict[str, Any]:
    draft = store.get_draft(draft_id)
    if not draft:
        return {"ok": False, "error": "draft_not_found", "draft_id": draft_id}
    ok, reason = can_schedule(draft)
    if not ok:
        return {"ok": False, "error": reason, "draft_id": draft_id}
    if not zernio_api_key():
        return {"ok": False, "error": "missing_zernio_api_key", "draft_id": draft_id}
    payload = schedule_payload(draft)
    try:
        result = create_zernio_post(payload)
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "draft_id": draft_id,
            "payload": {k: v for k, v in payload.items() if k != "content"},
        }
    post = (result.get("post") or result) if isinstance(result, dict) else {}
    status = (post.get("status") or "").lower()
    external = {"zernio": result}
    if status == "published" or payload.get("publishNow"):
        mark_posted(draft_id, external=external)
        final = "posted"
    else:
        mark_scheduled(draft_id, external=external)
        final = "scheduled"
    return {
        "ok": True,
        "draft_id": draft_id,
        "status": final,
        "zernio_status": status or None,
        "external": external,
    }


def publish_today_drafts(*, campaign: str = "today") -> Dict[str, Any]:
    """Publish/schedule approved Today drafts that are still draft/approved."""
    if not zernio_api_key():
        return {
            "ok": False,
            "error": "missing_zernio_api_key",
            "hint": (
                "Add ZERNIO_API_KEY to Cursor Cloud Agent secrets "
                "(Dashboard → Cloud Agents → Secrets), then re-run."
            ),
            "results": [],
        }
    results: List[Dict[str, Any]] = []
    for d in store.list_drafts():
        if d.get("campaign") != campaign:
            continue
        if d.get("status") in ("posted", "scheduled", "skipped", "rejected"):
            continue
        results.append(publish_draft(d["id"]))
    ok = bool(results) and all(r.get("ok") for r in results)
    return {
        "ok": ok,
        "published_or_scheduled": sum(1 for r in results if r.get("ok")),
        "failed": sum(1 for r in results if not r.get("ok")),
        "results": results,
    }
