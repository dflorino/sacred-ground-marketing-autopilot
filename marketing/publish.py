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
    # Hard gate: never ship the banned navy mystic PIL morning factory
    # (Founder Aug 25 2026 — pride-baked compositor reached Zernio/FB/IG).
    campaign = str(draft.get("campaign") or "")
    rule = str(img.get("rule") or img.get("source") or "")
    if campaign in ("today", "morning") or rule in ("morning_flyer", "morning"):
        from . import morning_flyers as mf
        from .ingest import today_local

        url = str(img.get("url") or "").strip()
        if url and mf.image_url_looks_like_banned_compositor_upload(url):
            return False, "banned_mystic_navy_pil_image"
        day_key = str(draft.get("fingerprint") or "").split("|")
        publish_day = day_key[1] if len(day_key) > 1 else today_local().isoformat()
        flyer_day_s = ""
        for note in draft.get("notes") or []:
            if str(note).startswith("flyer_day:"):
                flyer_day_s = str(note).split(":", 1)[1].strip()
                break
        try:
            from datetime import date

            flyer_day = date.fromisoformat(flyer_day_s or publish_day)
        except ValueError:
            flyer_day = today_local()
        platform = str(draft.get("platform") or "facebook")
        if url and not mf.morning_image_url_is_authorized(
            flyer_day, url, platform=platform
        ):
            return False, "stale_morning_flyer_image"
        # Also refuse when draft notes / recommendation still point at PIL preview.
        blob = " ".join(
            [
                str(img.get("recommendation") or ""),
                str(img.get("rule") or ""),
                " ".join(str(n) for n in (draft.get("notes") or [])),
            ]
        ).lower()
        if "pil_compositor" in blob or "banned_pil" in blob:
            return False, "banned_mystic_navy_pil_image"
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
    platform_entry: Dict[str, Any] = {
        "platform": platform,
        "accountId": account_id,
    }
    # Zernio firstComment (FB + IG feed) — auto-posts after publish.
    # Founder Aug 14 2026: every FB/IG publish gets ONE pride first comment.
    # Prefer planned first_comment; fall back to claim whenever present so older
    # caption-only placement drafts still ship a comment.
    cap = draft.get("caption") or {}
    sp = cap.get("social_proof") or {}
    first_comment = (sp.get("first_comment") or "").strip()
    if not first_comment and sp.get("claim"):
        first_comment = str(sp.get("claim") or "").strip()
    if first_comment and platform in ("facebook", "instagram"):
        platform_entry["platformSpecificData"] = {"firstComment": first_comment}
    body: Dict[str, Any] = {
        "content": cap.get("text") or "",
        "platforms": [platform_entry],
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


def publish_campaign_drafts(*, campaign: str) -> Dict[str, Any]:
    """Publish/schedule one campaign's drafts for the shop-local calendar day."""
    if not zernio_api_key():
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
    from .paths import settings

    day_key = today_local().isoformat()
    horizon = 2
    if campaign == "week_ahead":
        wa = (settings().get("campaigns") or {}).get("week_ahead") or {}
        horizon = int(wa.get("horizon_days") or 2)

    skipped_stale: List[Dict[str, Any]] = []
    if campaign == "today":
        skipped_stale.extend(store.retire_stale_morning_drafts(day_key=day_key))
    elif campaign == "week_ahead":
        skipped_stale.extend(
            store.retire_stale_week_ahead_drafts(
                day=today_local(), horizon_days=horizon
            )
        )

    # Collect candidates; for week_ahead prefer newest non-stale draft per platform.
    candidates: List[Dict[str, Any]] = []
    for d in store.list_drafts():
        if d.get("campaign") != campaign:
            continue
        if d.get("status") in ("posted", "scheduled", "skipped", "rejected"):
            continue
        fp = d.get("fingerprint") or ""
        # Fingerprints look like: week_ahead|2026-08-03|facebook|…
        if f"|{day_key}|" not in f"|{fp}|":
            continue
        if campaign == "week_ahead" and store.is_stale_week_ahead_draft(d, horizon):
            store.update_draft(
                d["id"],
                status="skipped",
                approval_status="skipped",
                publish_blocked_reason="stale_week_ahead_horizon_or_exterior",
                notes=list(d.get("notes") or [])
                + ["stale_week_ahead_horizon_or_exterior"],
            )
            skipped_stale.append(
                {
                    "ok": False,
                    "draft_id": d["id"],
                    "error": "stale_week_ahead_horizon_or_exterior",
                }
            )
            continue
        candidates.append(d)

    if campaign == "week_ahead":
        # One draft per platform — newest created_at wins.
        best: Dict[str, Dict[str, Any]] = {}
        for d in candidates:
            plat = str(d.get("platform") or "")
            prev = best.get(plat)
            if not prev or str(d.get("created_at") or "") > str(prev.get("created_at") or ""):
                best[plat] = d
        candidates = list(best.values())

    publish_results: List[Dict[str, Any]] = [
        publish_draft(d["id"]) for d in candidates
    ]
    results = publish_results + skipped_stale
    ok = bool(candidates) and all(r.get("ok") for r in publish_results)
    return {
        "ok": ok,
        "campaign": campaign,
        "day": day_key,
        "published_or_scheduled": sum(1 for r in publish_results if r.get("ok")),
        "failed": sum(1 for r in results if not r.get("ok")),
        "results": results,
    }


def publish_today_drafts(*, campaign: str = "today") -> Dict[str, Any]:
    """Publish/schedule morning campaign drafts for today's publish day.

    Content = full publish-day slate + tomorrow (see morning_lineup_events).
    """
    return publish_campaign_drafts(campaign=campaign)


def publish_week_ahead_drafts() -> Dict[str, Any]:
    """Publish/schedule tonight's week-ahead planner drafts."""
    return publish_campaign_drafts(campaign="week_ahead")


def publish_tuesday_meditation_drafts() -> Dict[str, Any]:
    """Publish/schedule today's Tuesday meditation drafts (4pm CT)."""
    return publish_campaign_drafts(campaign="tuesday_meditation")


def publish_afternoon_spotlight_drafts() -> Dict[str, Any]:
    """Publish/schedule today's afternoon spotlight drafts (default 5pm CT)."""
    return publish_campaign_drafts(campaign="afternoon_spotlight")
