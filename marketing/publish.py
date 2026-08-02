"""Phase 2+ publish gate — never called in Phase 1."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from . import control, store
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
    if not (img.get("url") or "").startswith("https://"):
        return False, "missing_image_url"
    return True, "ok"


def _recommended_passed(sched: Optional[str], now: Optional[datetime] = None) -> bool:
    """True when recommended local post time is already at/past now."""
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
    """Build ML Social / Zernio social_publish args — does not call the API."""
    platform = draft["platform"]
    acct = accounts().get(platform) or {}
    account_id = acct.get("accountId")
    if not account_id:
        raise ValueError(f"No accountId configured for {platform}")
    media = []
    img = draft.get("image") or {}
    url = img.get("url") or ""
    if url.startswith("https://"):
        media.append({"url": url, "type": "image"})
    sched = (draft.get("schedule_recommendation") or {}).get("recommended_at")
    publish_now = _recommended_passed(sched)
    return {
        "content": (draft.get("caption") or {}).get("text") or "",
        "platforms": [{"accountId": account_id}],
        "mediaItems": media or None,
        "scheduledFor": sched,
        "timezone": draft.get("timezone") or accounts().get("timezone") or "America/Chicago",
        "publishNow": publish_now,
        "draft_id": draft["id"],
        "fingerprint": draft["fingerprint"],
    }


def mark_scheduled(draft_id: str, external: Optional[Dict] = None) -> Dict[str, Any]:
    d = store.update_draft(
        draft_id,
        status="scheduled",
        publish_blocked_reason=None,
        external=external or {},
    )
    return d
