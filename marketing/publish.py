"""Phase 2+ publish gate + Zernio / ML Social schedule/publish."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

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


def zernio_api_key() -> Optional[str]:
    return zernio.api_key()


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


def schedule_payload(draft: Dict[str, Any]) -> Dict[str, Any]:
    """Build Zernio / ML Social create-post body."""
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
    tz = draft.get("timezone") or accounts().get("timezone") or "America/Chicago"
    publish_now = _should_publish_now(sched, tz)
    body: Dict[str, Any] = {
        "content": (draft.get("caption") or {}).get("text") or "",
        "platforms": [{"platform": platform, "accountId": account_id}],
        "timezone": tz,
        "publishNow": publish_now,
        "draft_id": draft["id"],
        "fingerprint": draft["fingerprint"],
    }
    if media:
        body["mediaItems"] = media
    if sched and not publish_now:
        body["scheduledFor"] = _to_zernio_local(sched, tz)
    return body


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


def publish_draft(draft_id: str) -> Dict[str, Any]:
    draft = store.get_draft(draft_id)
    if not draft:
        return {"ok": False, "error": "draft_not_found", "draft_id": draft_id}
    ok, reason = can_schedule(draft)
    if not ok:
        store.update_draft(draft_id, publish_blocked_reason=reason)
        return {"ok": False, "error": reason, "draft_id": draft_id}
    if not zernio.configured():
        store.update_draft(draft_id, publish_blocked_reason="missing_zernio_api_key")
        return {"ok": False, "error": "missing_zernio_api_key", "draft_id": draft_id}

    # Cross-checkout guard: skip if Zernio already has a Today post today.
    if draft.get("campaign") == "today":
        platform = draft.get("platform") or ""
        acct = (accounts().get(platform) or {}).get("accountId")
        day_key = None
        sched = (draft.get("schedule_recommendation") or {}).get("recommended_at")
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
            posted = mark_posted(draft_id, external=external)
            store.update_draft(
                draft_id,
                notes=list(posted.get("notes") or [])
                + ["skipped_publish: already_live_on_zernio_today"],
            )
            return {
                "ok": True,
                "draft_id": draft_id,
                "status": "already_posted",
                "skipped": True,
                "reason": "already_live_on_zernio_today",
                "zernio_post_id": existing.get("_id") or existing.get("id"),
            }

    payload = schedule_payload(draft)
    try:
        result = zernio.publish_draft_payload(payload)
    except zernio.ZernioError as exc:
        store.update_draft(
            draft_id,
            publish_blocked_reason=str(exc),
            notes=list(draft.get("notes") or []) + [f"zernio_error:{exc}"],
        )
        return {
            "ok": False,
            "error": "zernio_publish_failed",
            "message": str(exc),
            "status": exc.status,
            "body": exc.body,
            "draft_id": draft_id,
            "payload": {k: v for k, v in payload.items() if k != "content"},
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "draft_id": draft_id,
            "payload": {k: v for k, v in payload.items() if k != "content"},
        }

    post = (result.get("post") or result) if isinstance(result, dict) else {}
    status = (post.get("status") or "").lower()
    external = {
        "zernio": result,
        "payload": {
            k: payload[k]
            for k in ("publishNow", "scheduledFor", "timezone")
            if k in payload
        },
    }
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


def publish_campaign_drafts(*, campaign: str) -> Dict[str, Any]:
    """Publish/schedule one campaign's drafts for the shop-local calendar day."""
    if not zernio.configured():
        return {
            "ok": False,
            "error": "missing_zernio_api_key",
            "hint": (
                "Add ZERNIO_API_KEY to Cursor Cloud Agent secrets "
                "(Dashboard → Cloud Agents → Secrets), then re-run."
            ),
            "campaign": campaign,
            "results": [],
        }
    from .ingest import today_local

    day_key = today_local().isoformat()
    results: List[Dict[str, Any]] = []
    for d in store.list_drafts():
        if d.get("campaign") != campaign:
            continue
        if d.get("status") in ("posted", "scheduled", "skipped", "rejected"):
            continue
        if d.get("approval_status") != "approved" and campaign == "today":
            # Today Phase 2 auto-publish path requires approved drafts.
            continue
        fp = d.get("fingerprint") or ""
        # Fingerprints look like: today|2026-08-03|facebook|…
        if f"|{day_key}|" not in f"|{fp}|":
            continue
        results.append(publish_draft(d["id"]))
    ok = bool(results) and all(r.get("ok") for r in results)
    return {
        "ok": ok,
        "campaign": campaign,
        "day": day_key,
        "published_or_scheduled": sum(1 for r in results if r.get("ok")),
        "failed": sum(1 for r in results if not r.get("ok")),
        "results": results,
    }


def publish_today_drafts(*, campaign: str = "today") -> Dict[str, Any]:
    """Publish/schedule today's Today-campaign drafts (shop-local calendar day)."""
    return publish_campaign_drafts(campaign=campaign)


def publish_today_approved() -> Dict[str, Any]:
    """Alias used by pipeline auto-publish."""
    result = publish_today_drafts()
    return {
        "ok": result.get("ok"),
        "published": result.get("results") or [],
        "count": len(result.get("results") or []),
        "zernio_configured": zernio.configured(),
        "day": result.get("day"),
        "campaign": result.get("campaign"),
    }


def publish_week_ahead_drafts() -> Dict[str, Any]:
    """Publish/schedule tonight's week-ahead planner drafts."""
    return publish_campaign_drafts(campaign="week_ahead")
