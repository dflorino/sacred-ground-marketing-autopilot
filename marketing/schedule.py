from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from .ingest import parse_tec_datetime, tzinfo
from .models import Event, SchedulePlan
from .paths import settings


def _at_local(day: date, hhmm: str) -> datetime:
    hour, minute = [int(x) for x in hhmm.split(":")]
    return datetime.combine(day, time(hour, minute), tzinfo=tzinfo())


def morning_target_day(day: Optional[date] = None) -> date:
    """Calendar day whose events the morning (`today`) campaign promotes.

    Defaults to the next Chicago calendar day (target_offset_days=1) so the
    9am post gives ~24 hours to plan/book. Publish day stays `day`.
    """
    from .ingest import today_local

    on = day or today_local()
    cfg = (settings().get("campaigns") or {}).get("today") or {}
    offset = int(cfg.get("target_offset_days") or 1)
    return on + timedelta(days=offset)


def morning_campaign_word() -> str:
    """On-image campaign word for non-prebranded morning posts (default TOMORROW)."""
    cfg = (settings().get("campaigns") or {}).get("today") or {}
    word = str(cfg.get("campaign_word") or "TOMORROW").strip()
    return word or "TOMORROW"


def schedule_today(day: date) -> SchedulePlan:
    """Schedule the morning post on `day` (publish day); content is for target day."""
    cfg = (settings().get("campaigns") or {}).get("today") or {}
    hhmm = cfg.get("schedule_local_time") or "09:00"
    when = _at_local(day, hhmm)
    target = morning_target_day(day)
    return SchedulePlan(
        recommended_at=when.isoformat(),
        rationale=(
            f"Daily {hhmm} Central — promote {target.isoformat()} events "
            "(next calendar day) so people have ~24 hours to plan/book."
        ),
    )


def schedule_week(week_start: date) -> SchedulePlan:
    cfg = settings()["campaigns"]["week"]
    # Prefer configured weekday (monday default)
    weekday_name = (cfg.get("weekday") or "monday").lower()
    names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    target = names.index(weekday_name) if weekday_name in names else 0
    day = week_start + timedelta(days=(target - week_start.weekday()) % 7)
    when = _at_local(day, cfg["schedule_local_time"])
    return SchedulePlan(
        recommended_at=when.isoformat(),
        rationale="Weekly roundup at the start of the week.",
    )


def schedule_afternoon_spotlight(day: date) -> SchedulePlan:
    """Daily afternoon single-event spotlight (default 5:00 PM Central)."""
    cfg = (settings().get("campaigns") or {}).get("afternoon_spotlight") or {}
    hhmm = cfg.get("schedule_local_time") or "17:00"
    when = _at_local(day, hhmm)
    return SchedulePlan(
        recommended_at=when.isoformat(),
        rationale=(
            f"Daily {hhmm} Central afternoon spotlight — one engaging event "
            "(prefer tonight's evening gathering; else tomorrow's standout). "
            "5pm chosen for Meta Insights traction headroom before 7pm week_ahead; "
            "set schedule_local_time to 16:00 for 4pm."
        ),
    )


def schedule_week_ahead(day: date) -> SchedulePlan:
    """Daily 7pm Central — short upcoming-days planner post."""
    cfg = settings()["campaigns"]["week_ahead"]
    when = _at_local(day, cfg.get("schedule_local_time") or "19:00")
    horizon = int(cfg.get("horizon_days") or 2)
    return SchedulePlan(
        recommended_at=when.isoformat(),
        rationale=f"Daily evening planner so people can book the next {horizon} days.",
    )


# Chicago-local month/day skips for the dedicated Tuesday meditation post.
# Only these four holidays; other closed days still get the post if Tuesday.
_TUESDAY_MEDITATION_HOLIDAYS = {
    (12, 24): "christmas_eve",
    (12, 25): "christmas_day",
    (12, 31): "new_years_eve",
    (1, 1): "new_years_day",
}


def tuesday_meditation_holiday_name(day: date) -> Optional[str]:
    """Return holiday skip key for Chicago local date, or None."""
    return _TUESDAY_MEDITATION_HOLIDAYS.get((day.month, day.day))


def is_tuesday_meditation_holiday(day: date) -> bool:
    """True when the dedicated Tuesday meditation post must not run."""
    return tuesday_meditation_holiday_name(day) is not None


def should_run_tuesday_meditation(day: date) -> bool:
    """Every Tuesday except the four configured holidays."""
    if day.weekday() != 1:  # Tuesday
        return False
    return not is_tuesday_meditation_holiday(day)


def schedule_tuesday_meditation(day: date) -> SchedulePlan:
    """Tuesday 4:00 PM Central — dedicated Free Community Meditation post."""
    cfg = settings()["campaigns"]["tuesday_meditation"]
    when = _at_local(day, cfg.get("schedule_local_time") or "16:00")
    return SchedulePlan(
        recommended_at=when.isoformat(),
        rationale="Every Tuesday 4:00 PM Central — Free Community Meditation reminder.",
    )


def schedule_daily_reel(day: date) -> SchedulePlan:
    """Late-morning Central — daily IG + FB Reels (scaffold; not auto-published)."""
    cfg = (settings().get("campaigns") or {}).get("daily_reel") or {}
    when = _at_local(day, cfg.get("schedule_local_time") or "10:30")
    return SchedulePlan(
        recommended_at=when.isoformat(),
        rationale=(
            "Daily late-morning Reels (Instagram + Facebook) — "
            "HeyGen 9:16 video; approve-before-post until video publish is verified."
        ),
    )


def schedule_spotlight(event: Event, days_before: Optional[int] = None) -> SchedulePlan:
    cfg = settings()["campaigns"]["spotlight"]
    start = parse_tec_datetime(event.start_date)
    if not start:
        start = datetime.now(tzinfo())
    if days_before is None:
        # Initial spotlight: 7 days before if possible, else next morning
        days_before = 7
        if start.date() - timedelta(days=7) < datetime.now(tzinfo()).date():
            days_before = max(0, (start.date() - datetime.now(tzinfo()).date()).days)
    post_day = start.date() - timedelta(days=days_before)
    when = _at_local(post_day, cfg["schedule_local_time"])
    label = {
        0: "Day-of spotlight",
        1: "Day-before reminder",
        3: "3-day reminder",
        7: "1-week teaser",
    }.get(days_before, f"{days_before}-day reminder")
    return SchedulePlan(
        recommended_at=when.isoformat(),
        rationale=f"{label} for “{event.title}”.",
    )


def reminder_offsets() -> list:
    return list(settings()["campaigns"]["spotlight"].get("reminder_days_before") or [7, 3, 1])
