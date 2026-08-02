"""Phase 2+ publish gate + Zernio handoff."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from . import control, store, zernio
from .ingest import tzinfo
from .paths import accounts


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
    url = img.get("url") or ""
    local = img.get("local_path") or ""
    if not (url.startswith("https://") or (local and os.path.exists(local))):
        return False, "missing_image_url"
    return True, "ok"


def _recommended_passed(sched: Optional[str], now: Optional[datetime] = None) -> bool:
    if not sched:
        return False
    now = now or datetime.now(tzinfo())
    try:
        rec = datetime.fromisoformat(sched)
    except ValueError:
        return False
    if rec.tzinfo is None:
        rec = rec.replace(tzinfo=tzinfo())
    return now >= rec


def schedule_payload(draft: Dict[str, Any]) -> Dict[str, Any]:
    """Build Zernio create-post args."""
    platform = draft["platform"]
    acct = accounts().get(platform) or {}
    account_id = acct.get("accountId")
    if not account_id:
        raise ValueError(f"No accountId configured for {platform}")
    media = []
    img = draft.get("image") or {}
    url = img.get("url") or ""
    local = img.get("local_path") or ""
    if url.startswith("https://"):
        media.append({"url": url, "type": "image"})
    elif local and os.path.exists(local):
        media.append({"url": local, "type": "image"})
    sched = (draft.get("schedule_recommendation") or {}).get("recommended_at")
    publish_now = _recommended_passed(sched)
    return {
        "content": (draft.get("caption") or {}).get("text") or "",
        "platforms": [{"platform": platform, "accountId": account_id}],
        "mediaItems": media or None,
        "scheduledFor": None if publish_now else sched,
        "timezone": draft.get("timezone") or accounts().get("timezone") or "America/Chicago",
        "publishNow": publish_now,
        "draft_id": draft["id"],
        "fingerprint": draft["fingerprint"],
    }


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
    store.mark_posted(d["fingerprint"], draft_id, meta=external or {})
    return d


def publish_draft(draft_id: str) -> Dict[str, Any]:
    """Approve-gate + send one draft to Zernio."""
    d = store.get_draft(draft_id)
    if not d:
        return {"ok": False, "error": "unknown_draft", "draft_id": draft_id}
    ok, reason = can_schedule(d)
    if not ok:
        store.update_draft(draft_id, publish_blocked_reason=reason)
        return {"ok": False, "error": reason, "draft_id": draft_id}
    if not zernio.configured():
        store.update_draft(draft_id, publish_blocked_reason="missing_zernio_api_key")
        return {
            "ok": False,
            "error": "missing_zernio_api_key",
            "draft_id": draft_id,
            "message": "Set ZERNIO_API_KEY in the automation environment once.",
        }

    # Cross-checkout guard: skip if Zernio already has a Today post today.
    if d.get("campaign") == "today":
        platform = d.get("platform") or ""
        acct = (accounts().get(platform) or {}).get("accountId")
        day_key = None
        sched = (d.get("schedule_recommendation") or {}).get("recommended_at")
        if sched:
            try:
                day_key = datetime.fromisoformat(sched).astimezone(tzinfo()).date()
            except ValueError:
                day_key = None
        if day_key is None:
            day_key = datetime.now(tzinfo()).date()
        existing = zernio.existing_today_post(
            platform=platform,
            account_id=str(acct or ""),
            day=day_key,
        )
        if existing:
            external = {
                "zernio_existing": {
                    "id": existing.get("_id") or existing.get("id"),
                    "status": existing.get("status"),
                    "content": ((existing.get("content") or "")[:120]),
                }
            }
            draft = mark_posted(draft_id, external=external)
            store.update_draft(
                draft_id,
                notes=list(draft.get("notes") or [])
                + ["skipped_publish: already_live_on_zernio_today"],
            )
            return {
                "ok": True,
                "state": "already_posted",
                "draft_id": draft_id,
                "skipped": True,
                "reason": "already_live_on_zernio_today",
                "zernio_post_id": existing.get("_id") or existing.get("id"),
            }

    payload = schedule_payload(d)
    try:
        result = zernio.publish_draft_payload(payload)
    except zernio.ZernioError as exc:
        store.update_draft(
            draft_id,
            publish_blocked_reason=str(exc),
            notes=list(d.get("notes") or []) + [f"zernio_error:{exc}"],
        )
        return {
            "ok": False,
            "error": "zernio_publish_failed",
            "message": str(exc),
            "status": exc.status,
            "body": exc.body,
            "draft_id": draft_id,
        }

    external = {"zernio": result, "payload": {
        k: payload[k] for k in ("publishNow", "scheduledFor", "timezone") if k in payload
    }}
    if payload.get("publishNow"):
        draft = mark_posted(draft_id, external=external)
        state = "posted"
    else:
        draft = mark_scheduled(draft_id, external=external)
        state = "scheduled"
    return {"ok": True, "state": state, "draft": draft, "zernio": result}


def publish_today_approved() -> Dict[str, Any]:
    """Publish all approved Today drafts that are still sendable."""
    results: List[Dict[str, Any]] = []
    for d in store.list_drafts():
        if d.get("campaign") != "today":
            continue
        if d.get("approval_status") != "approved":
            continue
        if d.get("status") in ("posted", "scheduled", "rejected", "skipped"):
            continue
        results.append(publish_draft(d["id"]))
    ok = all(r.get("ok") for r in results) if results else False
    return {
        "ok": ok,
        "published": results,
        "count": len(results),
        "zernio_configured": zernio.configured(),
    }
