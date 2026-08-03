from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

from .ingest import parse_tec_datetime, today_local
from .models import Event
from .paths import settings


def _excluded(title: str) -> bool:
    low = title.lower()
    for needle in settings().get("exclude_title_substrings") or []:
        if needle.lower() in low:
            return True
    return False


def _matches_special(event: Event) -> bool:
    """True for Holistic Fair–class promotions — not every starred practitioner slot."""
    cfg = settings()
    cat_set = {c.lower() for c in event.categories}
    for name in cfg.get("special_category_names") or []:
        if name.lower() in cat_set:
            return True
    low_title = event.title.lower()
    for kw in cfg.get("special_title_keywords") or []:
        if kw.lower() in low_title:
            return True
    # Asterisk / featured flag alone is NOT enough when spotlight_only_special is on
    if cfg.get("spotlight_only_special", True):
        return False
    if event.featured:
        return True
    return False


def _looks_one_time(event: Event) -> bool:
    """One-time spotlight candidates: special events, not recurring floor sessions."""
    series_hints = (
        "with tina",
        "tina's",
        "weekly",
        "ongoing",
        "drop-in",
        "every ",
        "sessions",
        "with adie",
        "tarot with",
        "massage",
        "amber |",
        "keeper of the cards",
        "lisa maria intuitive",
    )
    low = event.title.lower()
    if any(h in low for h in series_hints) and not _matches_special(event):
        return False
    return _matches_special(event)


def enrich(event: Event) -> Event:
    event.is_special = _matches_special(event)
    event.is_one_time = _looks_one_time(event)
    return event


def is_upcoming_or_today(event: Event, on: Optional[date] = None) -> bool:
    on = on or today_local()
    start = parse_tec_datetime(event.start_date)
    if not start:
        return False
    return start.date() >= on


def normalize_event_url(url: str) -> str:
    """Turn relative booking paths into absolute Sacred Ground URLs."""
    if not url:
        return ""
    u = url.strip()
    if u.startswith("http://") or u.startswith("https://"):
        return u
    site = (settings().get("site_url") or "https://shopsacredground.com").rstrip("/")
    if u.startswith("/"):
        return site + u
    return f"{site}/{u}"


def has_required_link(event: Event) -> bool:
    if not settings().get("require_event_url", True):
        return True
    event.url = normalize_event_url(event.url or "")
    return bool(event.url.startswith("http"))


def filter_valid(events: List[Event], on: Optional[date] = None) -> Tuple[List[Event], List[Dict]]:
    """Drop old events, excluded titles, missing links. Return (kept, skipped_reasons)."""
    on = on or today_local()
    kept: List[Event] = []
    skipped: List[Dict] = []
    for raw in events:
        ev = enrich(raw)
        if _excluded(ev.title):
            skipped.append({"id": ev.id, "title": ev.title, "reason": "excluded_title"})
            continue
        if not is_upcoming_or_today(ev, on):
            skipped.append({"id": ev.id, "title": ev.title, "reason": "old_event"})
            continue
        if not has_required_link(ev):
            skipped.append({"id": ev.id, "title": ev.title, "reason": "missing_link"})
            continue
        kept.append(ev)
    return kept, skipped


def events_on_day(events: List[Event], day: date) -> List[Event]:
    out: List[Event] = []
    for ev in events:
        start = parse_tec_datetime(ev.start_date)
        if start and start.date() == day:
            out.append(ev)
    out.sort(key=lambda e: e.start_date)
    return out


def events_in_week(events: List[Event], week_start: date) -> List[Event]:
    week_end = week_start + timedelta(days=6)
    out: List[Event] = []
    for ev in events:
        start = parse_tec_datetime(ev.start_date)
        if start and week_start <= start.date() <= week_end:
            out.append(ev)
    out.sort(key=lambda e: e.start_date)
    return out


def events_next_days(
    events: List[Event],
    on: date,
    days: int = 7,
    *,
    after: Optional[datetime] = None,
) -> List[Event]:
    """Rolling window: on through on+(days-1). Optionally drop already-ended events."""
    end = on + timedelta(days=max(1, days) - 1)
    out: List[Event] = []
    for ev in events:
        start = parse_tec_datetime(ev.start_date)
        if not start or not (on <= start.date() <= end):
            continue
        if after is not None:
            finish = parse_tec_datetime(ev.end_date) or start
            if finish.tzinfo is None and after.tzinfo is not None:
                finish = finish.replace(tzinfo=after.tzinfo)
            if finish <= after:
                continue
        out.append(ev)
    out.sort(key=lambda e: e.start_date)
    return out


def week_start_for(day: date) -> date:
    # Monday-start week in local TZ
    return day - timedelta(days=day.weekday())


def spotlight_candidates(events: List[Event], on: Optional[date] = None) -> List[Event]:
    """Special Event Spotlight only — Holistic Fair / special categories / keywords."""
    on = on or today_local()
    horizon = on + timedelta(days=21)
    out: List[Event] = []
    for ev in events:
        if not (ev.is_special or ev.is_one_time):
            continue
        start = parse_tec_datetime(ev.start_date)
        if not start:
            continue
        if on <= start.date() <= horizon:
            out.append(ev)
    out.sort(key=lambda e: e.start_date)
    return out


def format_when(event: Event) -> str:
    start = parse_tec_datetime(event.start_date)
    if not start:
        return event.start_date
    if event.all_day:
        return start.strftime("%A, %B %-d") if False else start.strftime("%A, %B %d").replace(" 0", " ")
    end = parse_tec_datetime(event.end_date)
    day = start.strftime("%A, %B %d").replace(" 0", " ")
    t0 = start.strftime("%-I:%M %p") if False else start.strftime("%I:%M %p").lstrip("0")
    if end and end.date() == start.date():
        t1 = end.strftime("%I:%M %p").lstrip("0")
        return f"{day} · {t0}–{t1}"
    return f"{day} · {t0}"


def short_blurb(event: Event, max_len: int = 160) -> str:
    text = event.excerpt or event.description
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_len:
        return text
    cut = text[: max_len - 1].rsplit(" ", 1)[0]
    return cut + "…"
