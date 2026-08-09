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


def _meditation_cfg() -> Dict:
    return settings().get("tuesday_community_meditation") or {}


def is_community_meditation(event: Event) -> bool:
    """True for Free Community Meditation / Meditation Free Community Event titles."""
    low = (event.title or "").lower()
    needles = _meditation_cfg().get("title_match_any") or [
        "community meditation",
        "meditation free community",
    ]
    return any(str(n).lower() in low for n in needles)


def _meditation_stub_for_day(day: date) -> Event:
    """Build the standing Tuesday-night meditation when TEC omitted it."""
    cfg = _meditation_cfg()
    stub = cfg.get("stub") or {}
    start_t = str(stub.get("start_time") or "19:00")
    end_t = str(stub.get("end_time") or "20:00")
    # Normalize HH:MM → HH:MM:00
    if len(start_t) == 5:
        start_t = f"{start_t}:00"
    if len(end_t) == 5:
        end_t = f"{end_t}:00"
    day_s = day.isoformat()
    return enrich(
        Event(
            id=int(stub.get("id") or 0),
            title=str(stub.get("title") or "Free Community Meditation"),
            start_date=f"{day_s} {start_t}",
            end_date=f"{day_s} {end_t}",
            url=normalize_event_url(str(stub.get("url") or "")),
            description=str(stub.get("excerpt") or ""),
            excerpt=str(stub.get("excerpt") or ""),
            cost=str(stub.get("cost") or "Free"),
            venue_name="Sacred Ground",
            timezone="America/Chicago",
        )
    )


def _has_meditation_on_day(events: List[Event], day: date) -> bool:
    for ev in events:
        if not is_community_meditation(ev):
            continue
        start = parse_tec_datetime(ev.start_date)
        if start and start.date() == day:
            return True
    return False


def ensure_tuesday_community_meditation(
    events: List[Event],
    day: date,
) -> List[Event]:
    """
    Founder rule: every Tuesday lineup must include community meditation.

    If `day` is Tuesday and no matching TEC event is present, inject the
    configured standing stub (7–8pm CT Free Community Meditation).
    """
    cfg = _meditation_cfg()
    if cfg.get("enabled", True) is False:
        return events
    # weekday(): Monday=0 … Tuesday=1
    if day.weekday() != 1:
        return events
    if _has_meditation_on_day(events, day):
        return events
    out = list(events) + [_meditation_stub_for_day(day)]
    out.sort(key=lambda e: e.start_date)
    return out


def ensure_meditation_in_horizon(
    events: List[Event],
    window_start: date,
    days: int,
) -> List[Event]:
    """Inject Tuesday meditation for each Tuesday inside [window_start, +days)."""
    cfg = _meditation_cfg()
    if cfg.get("enabled", True) is False:
        return events
    out = list(events)
    end = window_start + timedelta(days=max(1, days) - 1)
    d = window_start
    while d <= end:
        if d.weekday() == 1 and not _has_meditation_on_day(out, d):
            out.append(_meditation_stub_for_day(d))
        d += timedelta(days=1)
    out.sort(key=lambda e: e.start_date)
    return out


def cap_events(events: List[Event], limit: int) -> List[Event]:
    """
    Caption size cap. Community meditation is never dropped to make room —
    trim other (usually earlier) events first when over limit.
    """
    if limit <= 0 or len(events) <= limit:
        return list(events)
    meds = [e for e in events if is_community_meditation(e)]
    others = [e for e in events if not is_community_meditation(e)]
    # Keep meditation even if it alone exceeds limit (pathological config).
    room = max(0, limit - len(meds))
    out = others[:room] + meds
    out.sort(key=lambda e: e.start_date)
    return out


def events_on_day(events: List[Event], day: date) -> List[Event]:
    out: List[Event] = []
    for ev in events:
        start = parse_tec_datetime(ev.start_date)
        if start and start.date() == day:
            out.append(ev)
    out = ensure_tuesday_community_meditation(out, day)
    out.sort(key=lambda e: e.start_date)
    return out


def events_in_week(events: List[Event], week_start: date) -> List[Event]:
    week_end = week_start + timedelta(days=6)
    out: List[Event] = []
    for ev in events:
        start = parse_tec_datetime(ev.start_date)
        if start and week_start <= start.date() <= week_end:
            out.append(ev)
    out = ensure_meditation_in_horizon(out, week_start, days=7)
    out.sort(key=lambda e: e.start_date)
    return out


def event_calendar_days(events: List[Event]) -> List[date]:
    """Unique event calendar days in start order."""
    seen: List[date] = []
    for ev in events:
        start = parse_tec_datetime(ev.start_date)
        if not start:
            continue
        d = start.date()
        if d not in seen:
            seen.append(d)
    return seen


def clamp_events_to_horizon(
    events: List[Event],
    window_start: date,
    days: int,
) -> List[Event]:
    """Hard cap: keep only events whose calendar day is in [start, start+days)."""
    horizon = max(1, int(days))
    end = window_start + timedelta(days=horizon - 1)
    out: List[Event] = []
    for ev in events:
        start = parse_tec_datetime(ev.start_date)
        if start and window_start <= start.date() <= end:
            out.append(ev)
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
    out = ensure_meditation_in_horizon(out, on, days=days)
    # Re-clamp after meditation inject so a stub can never widen the window.
    out = clamp_events_to_horizon(out, on, days)
    # Re-apply "after" so a stub that already ended tonight is not re-injected
    if after is not None:
        filtered: List[Event] = []
        for ev in out:
            start = parse_tec_datetime(ev.start_date)
            if not start:
                continue
            finish = parse_tec_datetime(ev.end_date) or start
            if finish.tzinfo is None and after.tzinfo is not None:
                finish = finish.replace(tzinfo=after.tzinfo)
            if finish <= after:
                continue
            filtered.append(ev)
        out = filtered
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


def _evening_hour_from(cfg_key: str, default: int = 17) -> int:
    cfg = (settings().get("campaigns") or {}).get(cfg_key) or {}
    return int(cfg.get("same_day_evening_start_hour") or default)


def is_free_community_event(event: Event) -> bool:
    """True for free community gatherings (Lions Gate, etc.) — not Tuesday doors-close.

    Matches when "free" appears with community/welcome language, or when cost is
    Free and the title carries a known free-gathering cue (Lions Gate, meditation,
    reiki share, etc.) even if "community" drops from the title.
    """
    title = (event.title or "").lower()
    cost = (event.cost or "").lower()
    excerpt = (event.excerpt or "").lower()
    blob = f"{title} {cost} {excerpt}"
    if "free" not in blob:
        return False
    if any(k in blob for k in ("community", "all welcome", "all are welcome")):
        return True
    # cost Free + signature free-gathering keywords (title may omit "community")
    if "free" in cost:
        cues = (
            "lions gate",
            "meditation",
            "reiki share",
            "educational night",
            "tarotheads",
            "tarot heads",
        )
        return any(k in title for k in cues)
    return False


def event_still_upcoming(event: Event, after: Optional[datetime] = None) -> bool:
    if after is None:
        return True
    start = parse_tec_datetime(event.start_date)
    finish = parse_tec_datetime(event.end_date) or start
    if not finish:
        return False
    if finish.tzinfo is None and after.tzinfo is not None:
        finish = finish.replace(tzinfo=after.tzinfo)
    return finish > after


def same_day_evening_events(
    events: List[Event],
    day: date,
    *,
    after: Optional[datetime] = None,
    evening_hour: Optional[int] = None,
) -> List[Event]:
    """Events on `day` that start at/after evening_hour and have not ended."""
    hour = evening_hour if evening_hour is not None else _evening_hour_from("today", 17)
    out: List[Event] = []
    for ev in events_on_day(events, day):
        start = parse_tec_datetime(ev.start_date)
        if not start or start.hour < hour:
            continue
        if not event_still_upcoming(ev, after):
            continue
        out.append(ev)
    out.sort(key=lambda e: e.start_date)
    return out


def merge_events_by_id(*groups: List[Event]) -> List[Event]:
    seen = set()
    out: List[Event] = []
    for group in groups:
        for ev in group:
            if ev.id in seen:
                continue
            seen.add(ev.id)
            out.append(ev)
    out.sort(key=lambda e: e.start_date)
    return out


def morning_lineup_events(
    events: List[Event],
    publish_day: date,
    *,
    after: Optional[datetime] = None,
) -> Tuple[List[Event], List[Event], List[Event], date]:
    """Return (combined, tomorrow, today_events, target_day).

    Founder product truth (Aug 9, 2026): morning = ALL remaining events on
    publish_day (full day — not evening-only) + ALL events on tomorrow.
    Legacy ``include_same_day_evening`` is evening-only and must stay off for
    the morning campaign; afternoon spotlight still uses that helper.
    """
    from .schedule import morning_target_day

    cfg = (settings().get("campaigns") or {}).get("today") or {}
    target = morning_target_day(publish_day)
    tomorrow = events_on_day(events, target)
    today_events: List[Event] = []
    if cfg.get("include_publish_day", True):
        for ev in events_on_day(events, publish_day):
            if event_still_upcoming(ev, after):
                today_events.append(ev)
        today_events.sort(key=lambda e: e.start_date)
    elif cfg.get("include_same_day_evening", False):
        # Legacy path — evening-only. Prefer include_publish_day instead.
        today_events = same_day_evening_events(
            events,
            publish_day,
            after=after,
            evening_hour=int(cfg.get("same_day_evening_start_hour") or 17),
        )
    combined = merge_events_by_id(today_events, tomorrow)
    return combined, tomorrow, today_events, target


def _spotlight_rank(event: Event) -> tuple:
    """Higher is better for afternoon single-event spotlight."""
    start = parse_tec_datetime(event.start_date)
    hour = start.hour if start else 0
    free = is_free_community_event(event) or "free" in (event.cost or "").lower()
    community = is_free_community_event(event) or is_community_meditation(event)
    special = bool(event.is_special or event.is_one_time)
    featured = bool(event.featured)
    lions = "lions gate" in (event.title or "").lower()
    return (lions, special, community, free, featured, hour)


def pick_afternoon_spotlight(
    events: List[Event],
    day: date,
    *,
    after: Optional[datetime] = None,
) -> Optional[Event]:
    """
    Prefer tonight's best remaining evening event; else tomorrow's standout.
    On Tuesdays, skip the standing Free Community Meditation (4pm campaign owns it).
    """
    cfg = (settings().get("campaigns") or {}).get("afternoon_spotlight") or {}
    hour = int(cfg.get("same_day_evening_start_hour") or 17)
    skip_tue_med = bool(cfg.get("skip_tuesday_meditation_duplicate", True))

    def _ok(ev: Event) -> bool:
        if skip_tue_med and day.weekday() == 1 and is_community_meditation(ev):
            return False
        return True

    tonight: List[Event] = []
    if cfg.get("prefer_same_day_evening", True):
        tonight = [
            e
            for e in same_day_evening_events(
                events, day, after=after, evening_hour=hour
            )
            if _ok(e)
        ]
    if tonight:
        return sorted(tonight, key=_spotlight_rank, reverse=True)[0]

    from .schedule import morning_target_day

    target = morning_target_day(day)
    tomorrow = [e for e in events_on_day(events, target) if _ok(e)]
    if not tomorrow:
        return None
    return sorted(tomorrow, key=_spotlight_rank, reverse=True)[0]


def with_same_day_evening(
    ahead_events: List[Event],
    all_events: List[Event],
    day: date,
    *,
    after: Optional[datetime] = None,
    campaign_key: str = "today",
) -> List[Event]:
    """Prepend remaining same-day evening events into a forward horizon list.

    Morning ``today`` uses ``morning_lineup_events`` (full publish-day) instead.
    week_ahead keeps ``include_same_day_evening: false`` — next-2-days starting
    tomorrow only. This helper remains for tests / legacy callers.
    """
    cfg = (settings().get("campaigns") or {}).get(campaign_key) or {}
    if not cfg.get("include_same_day_evening", False):
        return ahead_events
    tonight = same_day_evening_events(
        all_events,
        day,
        after=after,
        evening_hour=int(cfg.get("same_day_evening_start_hour") or 17),
    )
    return merge_events_by_id(tonight, ahead_events)


def week_ahead_lineup_events(
    events: List[Event],
    publish_day: date,
    *,
    after: Optional[datetime] = None,
    max_events: Optional[int] = None,
) -> Tuple[List[Event], date, int]:
    """Next N calendar days starting tomorrow — never the publish day.

    Returns (events, window_start, horizon_days).
    Sat 7pm → Sun+Mon; Sun 7pm → Mon+Tue. Same-day evening is not merged.
    """
    cfg = (settings().get("campaigns") or {}).get("week_ahead") or {}
    horizon = int(cfg.get("horizon_days") or 2)
    start_offset = int(cfg.get("horizon_start_offset_days") or 1)
    window_start = publish_day + timedelta(days=start_offset)
    if max_events is None:
        max_events = int(settings().get("max_week_ahead_events_in_caption") or 8)
    ahead = cap_events(
        events_next_days(events, window_start, days=horizon, after=after),
        int(max_events),
    )
    ahead = clamp_events_to_horizon(ahead, window_start, horizon)
    # Hard rule: publish-day events never appear on week_ahead (even if an old
    # include_same_day_evening flag is left on in settings).
    ahead = [e for e in ahead if _event_day(e) != publish_day]
    ahead = cap_events(ahead, int(max_events))
    return ahead, window_start, horizon


def _event_day(event: Event) -> Optional[date]:
    start = parse_tec_datetime(event.start_date)
    return start.date() if start else None
