"""Phase 2+ publish gate + Zernio HTTP schedule/publish."""
from __future__ import annotations

import io
import json
import os
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from . import control, store
from .paths import accounts

ZERNIO_API_BASE = os.environ.get("ZERNIO_API_BASE", "https://zernio.com/api/v1")

# Instagram feed still rejects ratios just outside 0.75–1.91 (Zernio 400).
IG_MIN_ASPECT = 0.75
IG_MAX_ASPECT = 1.91
_HTTP_UA = "SacredGroundMarketingAutopilot/1.0 (+shopsacredground.com)"


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


def ig_aspect_ok(width: int, height: int) -> bool:
    """True when width/height is inside Instagram feed's allowed range."""
    if width <= 0 or height <= 0:
        return False
    ratio = width / height
    # Tiny float slack — Zernio still rejects 1232×1646 (≈0.7485).
    return (IG_MIN_ASPECT - 1e-9) <= ratio <= (IG_MAX_ASPECT + 1e-9)


def crop_box_for_instagram_feed(width: int, height: int) -> Tuple[int, int, int, int]:
    """Center-crop box (left, top, right, bottom) into a valid IG feed ratio.

    Prefer 3:4 portrait when the source is too tall; 1.91:1 when too wide.
    """
    if width <= 0 or height <= 0:
        raise ValueError("invalid image dimensions")
    ratio = width / height
    if ratio < IG_MIN_ASPECT:
        # Too tall — crop height to width / 0.75 (= 4:3 height for given width).
        target_h = int(width / IG_MIN_ASPECT)
        target_h = max(1, min(target_h, height))
        top = (height - target_h) // 2
        return (0, top, width, top + target_h)
    if ratio > IG_MAX_ASPECT:
        target_w = int(height * IG_MAX_ASPECT)
        target_w = max(1, min(target_w, width))
        left = (width - target_w) // 2
        return (left, 0, left + target_w, height)
    return (0, 0, width, height)


def _download_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": _HTTP_UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def upload_zernio_media(
    *,
    filename: str,
    content_type: str,
    data: bytes,
) -> str:
    """Presign + PUT bytes to Zernio temp media; return publicUrl."""
    presign = _http_json(
        "POST",
        "media/presign",
        body={
            "filename": filename,
            "contentType": content_type,
            "size": len(data),
        },
    )
    upload_url = presign.get("uploadUrl")
    public_url = presign.get("publicUrl")
    if not upload_url or not public_url:
        raise RuntimeError("zernio_presign_missing_urls")
    put = urllib.request.Request(
        str(upload_url),
        data=data,
        method="PUT",
        headers={"Content-Type": content_type},
    )
    with urllib.request.urlopen(put, timeout=120):
        pass
    return str(public_url)


def ensure_instagram_feed_image_url(url: str, *, draft_id: str = "") -> str:
    """Return a Zernio-hosted URL cropped into IG feed bounds when needed.

    No-op (original url) when already valid, Pillow missing, or download fails.
    """
    if not url:
        return url
    try:
        from PIL import Image
    except ImportError:
        return url
    try:
        raw = _download_bytes(url)
        im = Image.open(io.BytesIO(raw))
        im.load()
        w, h = im.size
        if ig_aspect_ok(w, h):
            return url
        box = crop_box_for_instagram_feed(w, h)
        cropped = im.crop(box)
        if cropped.mode not in ("RGB", "RGBA"):
            cropped = cropped.convert("RGBA")
        buf = io.BytesIO()
        cropped.save(buf, format="PNG")
        payload = buf.getvalue()
        stem = (draft_id or "ig").replace("/", "-")[:48]
        return upload_zernio_media(
            filename=f"{stem}-ig-feed.png",
            content_type="image/png",
            data=payload,
        )
    except Exception:
        return url


def schedule_payload(draft: Dict[str, Any]) -> Dict[str, Any]:
    """Build Zernio / ML Social create-post body."""
    platform = draft["platform"]
    acct = accounts().get(platform) or {}
    account_id = acct.get("accountId")
    if not account_id:
        raise ValueError(f"No accountId configured for {platform}")
    media = []
    img = draft.get("image") or {}
    image_url = img.get("url")
    if image_url and platform == "instagram":
        image_url = ensure_instagram_feed_image_url(
            str(image_url), draft_id=str(draft.get("id") or "")
        )
    if image_url:
        media.append({"url": image_url, "type": "image"})
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

    # Collect candidates; for week_ahead prefer newest non-stale draft per platform.
    candidates: List[Dict[str, Any]] = []
    skipped_stale: List[Dict[str, Any]] = []
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

    Content promotes the next calendar day (see campaigns.today.target_offset_days).
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
