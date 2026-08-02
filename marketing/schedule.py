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


def schedule_today(day: date) -> SchedulePlan:
    hhmm = settings()["campaigns"]["today"]["schedule_local_time"]
    when = _at_local(day, hhmm)
    return SchedulePlan(
        recommended_at=when.isoformat(),
        rationale="Daily 7:00 AM Central — today's TEC events for same-day planning.",
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


def schedule_week_ahead(day: date) -> SchedulePlan:
    """Daily 7pm Central — next-7-days planner post."""
    cfg = settings()["campaigns"]["week_ahead"]
    when = _at_local(day, cfg.get("schedule_local_time") or "19:00")
    return SchedulePlan(
        recommended_at=when.isoformat(),
        rationale="Daily evening planner so people can book the next 7 days.",
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
