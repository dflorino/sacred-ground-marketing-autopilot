from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from . import captions, classify, images, schedule, store
from .control import is_paused, phase, publish_allowed
from .ingest import load_events, today_local, tzinfo
from .models import DraftPackage, Event
from .paths import settings


def _now_iso() -> str:
    return datetime.now(tzinfo()).isoformat()


def _event_dicts(events: List[Event]) -> List[Dict[str, Any]]:
    return [e.to_dict() for e in events]


def _links(events: List[Event]) -> List[str]:
    return [e.url for e in events if e.url]


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


def generate_batch(source: str = "auto", as_of: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Create draft packages for today / week / spotlights.

    For Automations / production: use source="live-strict".
    If WordPress/TEC refresh fails, return ok=False and create zero drafts
    (never silently use stale cache).

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

    notes_base: List[str] = []
    if is_paused():
        notes_base.append("Autopilot paused — drafts only; no schedule/publish.")

    # --- Today ---
    today_events = classify.events_on_day(events, day)[
        : int(cfg.get("max_today_events_in_caption") or 6)
    ]
    if today_events and cfg["campaigns"]["today"].get("enabled", True):
        img = images.plan_image(today_events, "today")
        sched = schedule.schedule_today(day)
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
                notes=notes_base,
            )
            if draft:
                created.append(draft)
            else:
                skipped_drafts.append(
                    {
                        "campaign": "today",
                        "platform": platform,
                        "reason": "duplicate_or_override",
                    }
                )
    elif not today_events:
        skipped_drafts.append({"campaign": "today", "reason": "no_events_today"})

    # --- Week (always refresh Monday key; generate any day for current week) ---
    week_start = classify.week_start_for(day)
    week_events = classify.events_in_week(events, week_start)[
        : int(cfg.get("max_week_events_in_caption") or 10)
    ]
    if week_events and cfg["campaigns"]["week"].get("enabled", True):
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
    elif not week_events:
        skipped_drafts.append({"campaign": "week", "reason": "no_events_this_week"})

    # --- Spotlights + reminders ---
    if cfg["campaigns"]["spotlight"].get("enabled", True):
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

    return {
        "ok": True,
        "as_of": day.isoformat(),
        "source": source_used,
        "events_considered": len(events_raw),
        "events_valid": len(events),
        "events_skipped": skipped,
        "drafts_created": len(created),
        "drafts": [{"id": d["id"], "campaign": d["campaign"], "platform": d["platform"], "fingerprint": d["fingerprint"]} for d in created],
        "draft_skips": skipped_drafts,
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
