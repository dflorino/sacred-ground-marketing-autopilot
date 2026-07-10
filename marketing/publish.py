"""Phase 2+ publish gate — never called in Phase 1."""
from __future__ import annotations

from typing import Any, Dict, Optional

from . import control, store
from .paths import accounts


def can_schedule(draft: Dict[str, Any]) -> tuple[bool, str]:
    if control.is_paused():
        return False, "autopilot_paused"
    if control.phase() < 2:
        return False, "phase_1_drafts_only"
    if draft.get("approval_status") != "approved" and control.phase() < 3:
        return False, "awaiting_approval"
    if draft.get("status") in ("posted", "scheduled", "skipped", "rejected"):
        return False, f"status_{draft.get('status')}"
    return True, "ok"


def schedule_payload(draft: Dict[str, Any]) -> Dict[str, Any]:
    """Build ML Social social_publish args — does not call the API."""
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
    return {
        "content": (draft.get("caption") or {}).get("text") or "",
        "platforms": [{"accountId": account_id}],
        "mediaItems": media or None,
        "scheduledFor": sched,
        "timezone": draft.get("timezone") or accounts().get("timezone") or "America/Phoenix",
        "publishNow": False,
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
