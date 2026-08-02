from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from . import captions, classify, compose, images, schedule, store
from . import publish as publish_mod
from .control import is_paused, phase, publish_allowed
from .ingest import load_events, today_local, tzinfo
from .models import DraftPackage, Event
from .paths import settings


def _now_iso() -> str:
    return datetime.now(tzinfo()).isoformat()


def _git_rev() -> Optional[str]:
    """Best-effort full commit SHA for GitHub raw composite URLs."""
    import subprocess

    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out and len(out) >= 7:
            return out
    except Exception:
        pass
    return None


def _git_branch() -> Optional[str]:
    """Best-effort current branch name for GitHub raw composite URLs."""
    import subprocess

    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out and out != "HEAD":
            return out
    except Exception:
        pass
    return None


def _event_dicts(events: List[Event]) -> List[Dict[str, Any]]:
    return [e.to_dict() for e in events]


def _links(events: List[Event]) -> List[str]:
    return [e.url for e in events if e.url]


def _campaign_auto_publish(campaign: str) -> bool:
    camp = (settings().get("campaigns") or {}).get(campaign) or {}
    return bool(camp.get("auto_publish"))


def _make_draft(
    *,
    campaign: str,
    platform: str,
    date_key: str,
    events: List[Event],
    caption: Dict[str, Any],
    image,
    sched,
    extra_fp: str = "",
    notes: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    fp = store.fingerprint(
        campaign,
        date_key,
        platform,
        [e.id for e in events],
        extra=extra_fp,
    )
    blocked = store.is_blocked(fp)
    if blocked:
        return None

    created = _now_iso()
    did = store.draft_id(fp, created)
    allowed, reason = publish_allowed()
    # Today auto-publish still needs Phase 2+ and not paused; campaign flag
    # unlocks approval, but phase_1 / pause still block.
    if allowed and _campaign_auto_publish(campaign):
        reason = None
    elif not allowed:
        pass
    pkg = DraftPackage(
        id=did,
        version="1.0",
        campaign=campaign,
        platform=platform,
        status="draft",
        approval_status="pending",
        fingerprint=fp,
        created_at=created,
        timezone=settings()["timezone"],
        schedule_recommendation=sched.to_dict(),
        caption=caption,
        image=image.to_dict(),
        events=_event_dicts(events),
        links=_links(events),
        phase=phase(),
        publish_blocked_reason=None if allowed else reason,
        notes=notes or [],
    )
    path = store.save_draft(pkg.to_dict())
    out = pkg.to_dict()
    out["_path"] = path
    return out


def _auto_ready_for_publish(draft_id: str) -> Dict[str, Any]:
    """Mark today drafts approved when campaign auto_publish is on (Phase 2+)."""
    allowed, reason = publish_allowed()
    if not allowed:
        return store.update_draft(
            draft_id,
            publish_blocked_reason=reason,
            notes=list(store.get_draft(draft_id).get("notes") or [])
            + [f"auto_publish pending: {reason}"],
        )
    return store.update_draft(
        draft_id,
        status="approved",
        approval_status="approved",
        reviewed_at=_now_iso(),
        publish_blocked_reason=None,
        notes=list(store.get_draft(draft_id).get("notes") or [])
        + ["auto_publish: approved for schedule/send"],
    )


def _attach_today_composite(
    drafts: List[Dict[str, Any]],
    events: List[Event],
    day,
    background_url: str,
) -> Dict[str, Any]:
    """Compose branded graphic once and attach to all Today drafts."""
    if os.environ.get("SGMA_SKIP_COMPOSE") == "1":
        return {
            "path": None,
            "public_url": background_url,
            "contrast": "skipped",
            "luma": None,
            "overlay": None,
            "url_via": "skipped",
            "filename": None,
        }
    result = compose.compose_today_graphic(
        background_url=background_url,
        events=events,
        day=day,
    )
    public_url = None
    # Prefer Zernio-hosted https URL when API key is present
    try:
        from . import zernio

        if zernio.configured():
            public_url = zernio.upload_image(result["path"], filename=result["filename"])
    except Exception as exc:  # keep local composite; publish step will retry/report
        result["upload_error"] = str(exc)

    # GitHub raw fallback for public repo (so media URL is https even without Zernio upload).
    # Prefer commit SHA: brand-new slashy branch names often 404 on raw.githubusercontent
    # until CDN catches up; SHA URLs are immediately fetchable after push.
    if not public_url:
        from urllib.parse import quote

        rev = (
            os.environ.get("GITHUB_SHA")
            or os.environ.get("COMPOSITE_SHA")
            or _git_rev()
        )
        branch = (
            os.environ.get("GITHUB_REF_NAME")
            or os.environ.get("COMPOSITE_BRANCH")
            or _git_branch()
            or "main"
        )
        ref = rev or quote(branch, safe="")
        public_url = (
            "https://raw.githubusercontent.com/dflorino/sacred-ground-marketing-autopilot/"
            f"{ref}/data/composites/{result['filename']}"
        )
        result["url_via"] = "github_raw_sha" if rev else "github_raw"
        result["git_ref"] = ref
    else:
        result["url_via"] = "zernio_media"

    result["public_url"] = public_url
    image_patch = {
        "source": "composed_today",
        "url": public_url,
        "local_path": result["path"],
        "event_id": events[0].id if len(events) == 1 else None,
        "prompt": None,
        "recommendation": (
            f"Composed Today graphic ({result['contrast']} text, luma {result['luma']}) "
            f"with translucent logo + website/phone footer."
        ),
        "rule": "composed",
        "contrast": result["contrast"],
        "luma": result["luma"],
        "overlay": result.get("overlay"),
    }
    for d in drafts:
        if d.get("campaign") != "today":
            continue
        updated = store.update_draft(
            d["id"],
            allow_content_update=True,
            image=image_patch,
            notes=list(d.get("notes") or [])
            + [f"composed:{result['filename']}", f"contrast:{result['contrast']}"],
        )
        d.update(updated)
    return result


def generate_batch(
    source: str = "auto",
    as_of: Optional[datetime] = None,
    campaigns: Optional[List[str]] = None,
    publish: bool = False,
) -> Dict[str, Any]:
    """
    Create draft packages for today / week / spotlights.

    For Automations / production: use source="live-strict".
    If WordPress/TEC refresh fails, return ok=False and create zero drafts
    (never silently use stale cache).

    campaigns: optional allow-list (e.g. ["today"]). When set, only those
    campaign types are created — used by the daily Today automation.

    Respects pause for *publishing* only — drafts still generate when paused
    so the queue stays warm; set notes accordingly.
    """
    day = today_local(as_of)
    try:
        events_raw, source_used = load_events(source)
    except Exception as exc:
        return {
            "ok": False,
            "error": "wordpress_refresh_failed",
            "message": str(exc),
            "as_of": day.isoformat(),
            "source_requested": source,
            "drafts_created": 0,
            "drafts": [],
            "draft_skips": [],
            "phase": phase(),
            "paused": is_paused(),
        }

    # Guard: live-strict must never report a non-live source
    if source in ("live", "live-strict") and source_used != "live":
        return {
            "ok": False,
            "error": "wordpress_refresh_failed",
            "message": f"Expected live WordPress events, got source={source_used}",
            "as_of": day.isoformat(),
            "source_requested": source,
            "drafts_created": 0,
            "drafts": [],
            "draft_skips": [],
            "phase": phase(),
            "paused": is_paused(),
        }

    events, skipped = classify.filter_valid(events_raw, on=day)

    created: List[Dict[str, Any]] = []
    skipped_drafts: List[Dict[str, Any]] = []
    platforms = list(settings().get("platforms") or ["facebook", "instagram"])
    cfg = settings()
    allowed = {c.strip().lower() for c in (campaigns or []) if c and str(c).strip()}
    def _want(name: str) -> bool:
        return (not allowed) or (name in allowed)

    notes_base: List[str] = []
    if is_paused():
        notes_base.append("Autopilot paused — drafts only; no schedule/publish.")

    composite_meta: Optional[Dict[str, Any]] = None
    publish_results: Optional[Dict[str, Any]] = None

    # --- Today (events day OR empty-day visit post) ---
    today_cfg = (cfg.get("campaigns") or {}).get("today") or {}
    if _want("today") and today_cfg.get("enabled", True):
        today_events = classify.events_on_day(events, day)[
            : int(cfg.get("max_today_events_in_caption") or 6)
        ]
        empty_ok = bool(today_cfg.get("empty_day_fallback", True))
        if today_events or empty_ok:
            img = images.plan_image(today_events, "today", day=day)
            sched = schedule.schedule_today(day)
            visit_notes = (
                notes_base + ["empty_day_visit"]
                if not today_events
                else notes_base
            )
            rule_note = f"image_rule:{img.rule}" if getattr(img, "rule", None) else None
            day_notes = visit_notes + ([rule_note] if rule_note else [])
            today_created = 0
            today_drafts: List[Dict[str, Any]] = []
            for platform in platforms:
                cap = captions.caption_today(today_events, platform, day)
                draft = _make_draft(
                    campaign="today",
                    platform=platform,
                    date_key=day.isoformat(),
                    events=today_events,
                    caption=cap,
                    image=img,
                    sched=sched,
                    extra_fp="empty_visit" if not today_events else "",
                    notes=day_notes,
                )
                if draft:
                    today_drafts.append(draft)
                    today_created += 1
                else:
                    skipped_drafts.append(
                        {
                            "campaign": "today",
                            "platform": platform,
                            "reason": "duplicate_or_override",
                        }
                    )
            if today_drafts and img.url:
                try:
                    composite_meta = _attach_today_composite(
                        today_drafts,
                        today_events,
                        day,
                        background_url=str(img.url),
                    )
                except Exception as exc:
                    composite_meta = {"error": f"compose_failed:{exc}"}
                    for draft in today_drafts:
                        store.update_draft(
                            draft["id"],
                            allow_content_update=True,
                            notes=list(draft.get("notes") or [])
                            + [f"compose_failed:{exc}"],
                        )
                images.record_image_use(
                    day=day,
                    url=str(img.url),
                    rule=str(img.rule or img.source),
                    campaign="today",
                )
            for draft in today_drafts:
                if today_cfg.get("auto_publish") and not is_paused():
                    draft = _auto_ready_for_publish(draft["id"])
                created.append(draft)
        else:
            skipped_drafts.append({"campaign": "today", "reason": "no_events_today"})

    # --- Week (always refresh Monday key; generate any day for current week) ---
    week_start = classify.week_start_for(day)
    week_events = classify.events_in_week(events, week_start)[
        : int(cfg.get("max_week_events_in_caption") or 10)
    ]
    if _want("week") and week_events and cfg["campaigns"]["week"].get("enabled", True):
        img = images.plan_image(week_events, "week")
        sched = schedule.schedule_week(week_start)
        for platform in platforms:
            cap = captions.caption_week(week_events, platform, week_start)
            draft = _make_draft(
                campaign="week",
                platform=platform,
                date_key=week_start.isoformat(),
                events=week_events,
                caption=cap,
                image=img,
                sched=sched,
                notes=notes_base,
            )
            if draft:
                created.append(draft)
            else:
                skipped_drafts.append(
                    {
                        "campaign": "week",
                        "platform": platform,
                        "reason": "duplicate_or_override",
                    }
                )
    elif _want("week") and not week_events:
        skipped_drafts.append({"campaign": "week", "reason": "no_events_this_week"})

    # --- Week ahead (daily 7pm planner: next 7 days) ---
    wa_cfg = (cfg.get("campaigns") or {}).get("week_ahead") or {}
    if _want("week_ahead") and wa_cfg.get("enabled", True):
        horizon = int(wa_cfg.get("horizon_days") or 7)
        ahead_events = classify.events_next_days(events, day, days=horizon)[
            : int(cfg.get("max_week_ahead_events_in_caption") or 14)
        ]
        if ahead_events:
            img = images.plan_image(ahead_events, "week_ahead")
            sched = schedule.schedule_week_ahead(day)
            for platform in platforms:
                cap = captions.caption_week_ahead(ahead_events, platform, day)
                draft = _make_draft(
                    campaign="week_ahead",
                    platform=platform,
                    date_key=day.isoformat(),
                    events=ahead_events,
                    caption=cap,
                    image=img,
                    sched=sched,
                    notes=notes_base + ["daily_7pm_next_7_days"],
                )
                if draft:
                    created.append(draft)
                else:
                    skipped_drafts.append(
                        {
                            "campaign": "week_ahead",
                            "platform": platform,
                            "reason": "duplicate_or_override",
                        }
                    )
        else:
            skipped_drafts.append(
                {"campaign": "week_ahead", "reason": "no_events_next_7_days"}
            )

    # --- Spotlights + reminders ---
    if _want("spotlight") and cfg["campaigns"]["spotlight"].get("enabled", True):
        for ev in classify.spotlight_candidates(events, on=day):
            img = images.plan_image([ev], "spotlight")
            # initial spotlight (extra=initial)
            sched0 = schedule.schedule_spotlight(ev, days_before=None)
            for platform in platforms:
                cap = captions.caption_spotlight(ev, platform, reminder_day=None)
                draft = _make_draft(
                    campaign="spotlight",
                    platform=platform,
                    date_key=ev.start_date[:10],
                    events=[ev],
                    caption=cap,
                    image=img,
                    sched=sched0,
                    extra_fp="initial",
                    notes=notes_base + ["special_event_spotlight"],
                )
                if draft:
                    created.append(draft)
                else:
                    skipped_drafts.append(
                        {
                            "campaign": "spotlight",
                            "platform": platform,
                            "event_id": ev.id,
                            "reason": "duplicate_or_override",
                        }
                    )

            for offset in schedule.reminder_offsets():
                from .ingest import parse_tec_datetime
                from datetime import timedelta

                start = parse_tec_datetime(ev.start_date)
                if not start:
                    continue
                # only create reminder drafts whose recommended day is today or future
                rem_day = start.date() - timedelta(days=offset)
                if rem_day < day:
                    continue
                sched_r = schedule.schedule_spotlight(ev, days_before=offset)
                for platform in platforms:
                    cap = captions.caption_spotlight(ev, platform, reminder_day=offset)
                    draft = _make_draft(
                        campaign="spotlight",
                        platform=platform,
                        date_key=ev.start_date[:10],
                        events=[ev],
                        caption=cap,
                        image=img,
                        sched=sched_r,
                        extra_fp=f"reminder-{offset}",
                        notes=notes_base + [f"reminder_{offset}d"],
                    )
                    if draft:
                        created.append(draft)

    # Today auto_publish → send to Zernio when requested / campaign flag + phase 2
    today_auto = bool(((cfg.get("campaigns") or {}).get("today") or {}).get("auto_publish"))
    should_publish = bool(publish) or (
        today_auto and phase() >= 2 and not is_paused() and _want("today")
    )
    if should_publish:
        publish_results = publish_mod.publish_today_approved()

    return {
        "ok": True,
        "as_of": day.isoformat(),
        "source": source_used,
        "events_considered": len(events_raw),
        "events_valid": len(events),
        "events_skipped": skipped,
        "drafts_created": len(created),
        "drafts": [
            {
                "id": d["id"],
                "campaign": d["campaign"],
                "platform": d["platform"],
                "fingerprint": d["fingerprint"],
                "image_url": (d.get("image") or {}).get("url"),
                "status": d.get("status"),
            }
            for d in created
        ],
        "draft_skips": skipped_drafts,
        "composite": {
            "path": (composite_meta or {}).get("path"),
            "public_url": (composite_meta or {}).get("public_url"),
            "contrast": (composite_meta or {}).get("contrast"),
            "luma": (composite_meta or {}).get("luma"),
            "overlay": (composite_meta or {}).get("overlay"),
            "url_via": (composite_meta or {}).get("url_via"),
        }
        if composite_meta
        else None,
        "publish": publish_results,
        "phase": phase(),
        "paused": is_paused(),
    }


def approve(draft_id: str) -> Dict[str, Any]:
    """Approve for review queue. Phase 1 never schedules or publishes."""
    d = store.update_draft(
        draft_id,
        status="approved",
        approval_status="approved",
        reviewed_at=_now_iso(),
    )
    # Hard gate: Phase 1 never publishes, even after approval
    allowed, reason = publish_allowed()
    if not allowed:
        d = store.update_draft(
            draft_id,
            publish_blocked_reason=reason,
            notes=list(d.get("notes") or []) + [f"Approved but not published: {reason}"],
        )
    elif phase() < 2:
        # Belt-and-suspenders if control state is inconsistent
        d = store.update_draft(
            draft_id,
            publish_blocked_reason="phase_1_drafts_only",
            notes=list(d.get("notes") or []) + ["Approved but not published: phase_1_drafts_only"],
        )
    return d


def reject(draft_id: str, reason: str = "") -> Dict[str, Any]:
    return store.update_draft(
        draft_id,
        status="rejected",
        approval_status="rejected",
        reviewed_at=_now_iso(),
        notes=list(store.get_draft(draft_id).get("notes") or []) + ([reason] if reason else []),
    )
