from __future__ import annotations

from datetime import datetime, timedelta
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

    # Morning campaign: tomorrow (+ remaining same-day evening).
    # date_key / schedule stay on publish day so publish-today finds drafts.
    today_cfg = (cfg.get("campaigns") or {}).get("today") or {}
    as_of_dt = as_of
    if as_of_dt is None:
        as_of_dt = datetime.now(tzinfo())
    elif as_of_dt.tzinfo is None:
        as_of_dt = as_of_dt.replace(tzinfo=tzinfo())

    combined_morning, tomorrow_events, tonight_evening, event_day = (
        classify.morning_lineup_events(events, day, after=as_of_dt)
        if today_cfg.get("enabled", True)
        else ([], [], [], schedule.morning_target_day(day))
    )
    # Flyer day: prefer publish day when tonight evening is listed (covers Lions Gate
    # on Saturday morning); else tomorrow's flyer.
    flyer_day = day if tonight_evening else event_day

    flyer_ensure: Dict[str, Any] = {}
    try:
        from . import morning_flyers as mf

        # Ensure publish-day + tomorrow so either flyer plate is ready.
        flyer_ensure = mf.ensure_flyers_for_range(
            days=2, start=day, events=events, force=False
        )
        if flyer_ensure.get("needs_upload"):
            notes_base.append(
                "morning_flyer_needs_upload:"
                + ",".join(flyer_ensure.get("needs_upload") or [])
            )
    except Exception as exc:
        notes_base.append(f"morning_flyer_ensure_failed:{exc}")

    # --- Morning / "today" campaign ---
    if today_cfg.get("enabled", True):
        today_events = classify.cap_events(
            combined_morning,
            int(cfg.get("max_today_events_in_caption") or 6),
        )
        empty_ok = bool(today_cfg.get("empty_day_fallback", True))
        if today_events or empty_ok:
            sched = schedule.schedule_today(day)
            claimed_urls: List[str] = []
            for platform in platforms:
                img = images.plan_image(
                    today_events,
                    "today",
                    day=flyer_day,
                    platform=platform,
                    exclude_urls=claimed_urls,
                )
                prebranded = bool(getattr(img, "prebranded", False)) or images.skip_brand_overlays(
                    img
                )
                camp_word = schedule.morning_campaign_word(
                    flyer_day=flyer_day,
                    publish_day=day,
                    prebranded=prebranded,
                )
                visit_notes = notes_base + [
                    f"event_day:{event_day.isoformat()}",
                    f"flyer_day:{flyer_day.isoformat()}",
                    f"campaign_word:{camp_word or 'skip_prebranded'}",
                ]
                if prebranded:
                    visit_notes.append("skip_brand_overlays:prebranded_flyer")
                if tonight_evening:
                    visit_notes.append(
                        "includes_same_day_evening:"
                        + ",".join(str(e.id) for e in tonight_evening)
                    )
                if not today_events:
                    visit_notes.append("empty_day_visit")
                rule_note = (
                    f"image_rule:{img.rule}" if getattr(img, "rule", None) else None
                )
                day_notes = visit_notes + ([rule_note] if rule_note else [])
                cap = captions.caption_today(
                    tomorrow_events,
                    platform,
                    event_day,
                    tonight_events=tonight_evening,
                    flyer_day=flyer_day,
                    publish_day=day,
                )
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
                    if today_cfg.get("auto_publish") and not is_paused():
                        draft = _auto_ready_for_publish(draft["id"])
                    created.append(draft)
                    if img.url:
                        claimed_urls.append(str(img.url))
                        images.record_image_use(
                            day=flyer_day,
                            url=img.url,
                            rule=str(img.rule or img.source),
                            campaign="today",
                            platform=platform,
                        )
                else:
                    skipped_drafts.append(
                        {
                            "campaign": "today",
                            "platform": platform,
                            "reason": "duplicate_or_override",
                        }
                    )
        else:
            skipped_drafts.append(
                {"campaign": "today", "reason": "no_events_for_target_day"}
            )

    # --- Week (always refresh Monday key; generate any day for current week) ---
    week_start = classify.week_start_for(day)
    week_events = classify.cap_events(
        classify.events_in_week(events, week_start),
        int(cfg.get("max_week_events_in_caption") or 10),
    )
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

    # --- Afternoon spotlight (daily 5pm: one engaging event) ---
    af_cfg = (cfg.get("campaigns") or {}).get("afternoon_spotlight") or {}
    if af_cfg.get("enabled", True):
        spotlight_ev = classify.pick_afternoon_spotlight(
            events, day, after=as_of_dt
        )
        empty_af = bool(af_cfg.get("empty_day_fallback", True))
        if spotlight_ev or empty_af:
            sched_af = schedule.schedule_afternoon_spotlight(day)
            af_events = [spotlight_ev] if spotlight_ev else []
            claimed_af: List[str] = []
            for platform in platforms:
                img = images.plan_image(
                    af_events,
                    "afternoon_spotlight",
                    day=day,
                    platform=platform,
                    exclude_urls=claimed_af,
                )
                cap = captions.caption_afternoon_spotlight(
                    spotlight_ev, platform, day
                )
                af_notes = notes_base + ["afternoon_spotlight_5pm"]
                if spotlight_ev:
                    af_notes.append(f"spotlight_event:{spotlight_ev.id}")
                else:
                    af_notes.append("empty_afternoon_brand")
                if img.rule:
                    af_notes.append(f"image_rule:{img.rule}")
                draft = _make_draft(
                    campaign="afternoon_spotlight",
                    platform=platform,
                    date_key=day.isoformat(),
                    events=af_events,
                    caption=cap,
                    image=img,
                    sched=sched_af,
                    extra_fp="" if spotlight_ev else "brand_visit",
                    notes=af_notes,
                )
                if draft:
                    if af_cfg.get("auto_publish") and not is_paused():
                        draft = _auto_ready_for_publish(draft["id"])
                    created.append(draft)
                    if img.url:
                        claimed_af.append(str(img.url))
                        images.record_image_use(
                            day=day,
                            url=img.url,
                            rule=str(img.rule or img.source),
                            campaign="afternoon_spotlight",
                            platform=platform,
                        )
                else:
                    skipped_drafts.append(
                        {
                            "campaign": "afternoon_spotlight",
                            "platform": platform,
                            "reason": "duplicate_or_override",
                        }
                    )
        else:
            skipped_drafts.append(
                {"campaign": "afternoon_spotlight", "reason": "no_spotlight_event"}
            )

    # --- Week ahead (daily 7pm planner: next 2 days starting tomorrow) ---
    wa_cfg = (cfg.get("campaigns") or {}).get("week_ahead") or {}
    if wa_cfg.get("enabled", True):
        # Sat 7pm → Sun+Mon only. Never include the publish day's calendar
        # (morning through night / same-day evening). Morning campaign owns tonight.
        ahead_events, window_start, horizon = classify.week_ahead_lineup_events(
            events,
            day,
            after=as_of_dt,
            max_events=int(cfg.get("max_week_ahead_events_in_caption") or 8),
        )
        # Retire stale unposted week-ahead drafts for tonight that still carry
        # an old 3-day window or founder Screenshot exterior rotation.
        skipped_drafts.extend(
            store.retire_stale_week_ahead_drafts(
                day=day,
                horizon_days=horizon,
            )
        )
        if ahead_events:
            sched = schedule.schedule_week_ahead(day)
            wa_created = 0
            claimed_urls: List[str] = []
            for platform in platforms:
                img = images.plan_image(
                    ahead_events,
                    "week_ahead",
                    day=day,
                    platform=platform,
                    exclude_urls=claimed_urls,
                )
                cap = captions.caption_week_ahead(ahead_events, platform, day)
                wa_notes = notes_base + [
                    "daily_7pm_upcoming",
                    f"horizon_days={horizon}",
                    f"horizon_start={window_start.isoformat()}",
                ]
                if img.rule:
                    wa_notes.append(f"image_rule:{img.rule}")
                draft = _make_draft(
                    campaign="week_ahead",
                    platform=platform,
                    date_key=day.isoformat(),
                    events=ahead_events,
                    caption=cap,
                    image=img,
                    sched=sched,
                    notes=wa_notes,
                )
                if draft:
                    if wa_cfg.get("auto_publish") and not is_paused():
                        draft = _auto_ready_for_publish(draft["id"])
                    created.append(draft)
                    wa_created += 1
                    if img.url:
                        claimed_urls.append(str(img.url))
                        images.record_image_use(
                            day=day,
                            url=img.url,
                            rule=str(img.rule or img.source),
                            campaign="week_ahead",
                            platform=platform,
                        )
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
                {"campaign": "week_ahead", "reason": "no_events_in_horizon"}
            )

    # --- Tuesday Free Community Meditation (4pm CT dedicated post) ---
    tm_cfg = (cfg.get("campaigns") or {}).get("tuesday_meditation") or {}
    if tm_cfg.get("enabled", True):
        if day.weekday() != 1:
            skipped_drafts.append(
                {"campaign": "tuesday_meditation", "reason": "not_tuesday"}
            )
        elif schedule.is_tuesday_meditation_holiday(day):
            skipped_drafts.append(
                {
                    "campaign": "tuesday_meditation",
                    "reason": "holiday_skip",
                    "holiday": schedule.tuesday_meditation_holiday_name(day),
                    "date": day.isoformat(),
                }
            )
        else:
            day_with_med = classify.ensure_tuesday_community_meditation(
                classify.events_on_day(events, day),
                day,
            )
            med_events = [
                e for e in day_with_med if classify.is_community_meditation(e)
            ]
            if not med_events:
                skipped_drafts.append(
                    {
                        "campaign": "tuesday_meditation",
                        "reason": "meditation_missing",
                    }
                )
            else:
                img = images.plan_image(med_events, "tuesday_meditation", day=day)
                sched = schedule.schedule_tuesday_meditation(day)
                tm_platforms = list(tm_cfg.get("platforms") or platforms)
                tm_created = 0
                for platform in tm_platforms:
                    cap = captions.caption_tuesday_meditation(platform, day)
                    draft = _make_draft(
                        campaign="tuesday_meditation",
                        platform=platform,
                        date_key=day.isoformat(),
                        events=med_events,
                        caption=cap,
                        image=img,
                        sched=sched,
                        notes=notes_base
                        + [
                            "tuesday_4pm_meditation",
                            f"image_rule:{img.rule}",
                        ],
                    )
                    if draft:
                        if tm_cfg.get("auto_publish") and not is_paused():
                            draft = _auto_ready_for_publish(draft["id"])
                        created.append(draft)
                        tm_created += 1
                    else:
                        skipped_drafts.append(
                            {
                                "campaign": "tuesday_meditation",
                                "platform": platform,
                                "reason": "duplicate_or_override",
                            }
                        )
                if tm_created and img.url:
                    images.record_image_use(
                        day=day,
                        url=img.url,
                        rule=str(img.rule or img.source),
                        campaign="tuesday_meditation",
                    )

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
        "morning_event_day": event_day.isoformat() if today_cfg.get("enabled", True) else None,
        "morning_flyer_day": flyer_day.isoformat() if today_cfg.get("enabled", True) else None,
        "morning_campaign_word": schedule.morning_campaign_word(
            flyer_day=flyer_day,
            publish_day=day,
            prebranded=False,
        )
        if today_cfg.get("enabled", True)
        else None,
        "source": source_used,
        "events_considered": len(events_raw),
        "events_valid": len(events),
        "events_skipped": skipped,
        "drafts_created": len(created),
        "drafts": [{"id": d["id"], "campaign": d["campaign"], "platform": d["platform"], "fingerprint": d["fingerprint"]} for d in created],
        "draft_skips": skipped_drafts,
        "phase": phase(),
        "paused": is_paused(),
        "morning_flyers": {
            "needs_upload": list((flyer_ensure or {}).get("needs_upload") or []),
            "ensured": [
                {
                    "day": r.get("day"),
                    "action": r.get("action"),
                    "needs_upload": r.get("needs_upload"),
                }
                for r in ((flyer_ensure or {}).get("results") or [])
            ],
        },
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
