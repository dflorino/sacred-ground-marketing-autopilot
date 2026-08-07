from __future__ import annotations

import hashlib
from datetime import date
from typing import Dict, List, Sequence

from .classify import format_when, is_community_meditation, short_blurb
from .meditation import (
    format_tuesday_meditation_opener,
    host_for_day,
    meditation_event_block,
)
from .models import Event
from .paths import voice


def _hashtags(platform: str, extra: Sequence[str] | None = None) -> List[str]:
    v = voice()
    tags = list(v["hashtags"]["core"])
    tags.extend(v["hashtags"].get("events") or [])
    if platform == "instagram":
        tags.extend(v["hashtags"].get("instagram_extra") or [])
    if extra:
        tags.extend(extra)
    # dedupe preserve order
    seen = set()
    out = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out[:12]


def _signoff(seed: str, platform: str = "") -> str:
    v = voice()
    platform = (platform or "").lower()
    if platform == "facebook":
        opts = v.get("facebook_signoff_options") or v.get("signoff_options")
    elif platform == "instagram":
        opts = v.get("instagram_signoff_options") or v.get("signoff_options")
    else:
        opts = v.get("signoff_options")
    opts = list(opts or ["Come as you are."])

    banned = list((v.get("forbidden_signoffs_by_platform") or {}).get(platform) or [])
    # Facebook must never use retail "on the floor" closings.
    if platform == "facebook":
        banned.extend(["See you on the floor.", "on the floor"])
    banned_l = {b.lower() for b in banned if b}
    opts = [o for o in opts if not any(b in o.lower() for b in banned_l)]
    if not opts:
        opts = ["Come as you are."]

    idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(opts)
    return opts[idx]


def _assert_not_generic(text: str) -> None:
    low = text.lower()
    for phrase in voice().get("forbidden_phrases") or []:
        if phrase.lower() in low:
            raise ValueError(f"Generic phrase blocked: {phrase}")


def _event_block(ev: Event, with_link: bool, *, under_day: bool = False) -> str:
    """One scannable event: title, when, optional URL — each on its own line.

    When under_day=True (week / week-ahead day sections), omit the weekday/date
    from the when line — the day header already carries it.
    """
    if is_community_meditation(ev):
        return meditation_event_block(event=ev)
    when = format_when(ev)
    if under_day and " · " in when:
        when_line = when.split(" · ", 1)[1]
    elif under_day:
        when_line = ""  # all-day; day header is enough
    else:
        when_line = when
    lines = [f"• {ev.title}"]
    if when_line:
        lines.append(f"  {when_line}")
    if with_link and ev.url:
        lines.append(f"  {ev.url}")
    return "\n".join(lines)


def _join_event_blocks(events: Sequence[Event], with_link: bool = True) -> str:
    """Blank line between events so expanded FB/IG posts are easy to scan."""
    return "\n\n".join(_event_block(e, with_link) for e in events)


def _join_event_blocks_by_day(events: Sequence[Event], with_link: bool = True) -> str:
    """Group multi-day lists under clear day headers; blank line between events."""
    from collections import OrderedDict

    from .ingest import parse_tec_datetime

    groups: "OrderedDict[tuple[str, str], list[Event]]" = OrderedDict()
    for ev in events:
        start = parse_tec_datetime(ev.start_date)
        if start:
            key = start.date().isoformat()
            label = start.strftime("%A, %B %d").replace(" 0", " ")
        else:
            key = (ev.start_date or "")[:10] or "unknown"
            label = key
        groups.setdefault((key, label), []).append(ev)

    sections: List[str] = []
    for (_key, label), day_events in groups.items():
        blocks = "\n\n".join(
            _event_block(e, with_link, under_day=True) for e in day_events
        )
        sections.append(f"{label}\n\n{blocks}")
    return "\n\n".join(sections)


def _tomorrow_hook(seed: str, *, day_label: str = "", title: str = "", kind: str = "multi") -> str:
    """Warm next-day opener (morning campaign promotes tomorrow, not today)."""
    v = voice()
    if kind == "meditation":
        opts = list(v.get("tomorrow_meditation_openers") or [])
        fallback = "Tomorrow at Sacred Ground — Free Community Meditation."
        raw = _pick_rotating(opts, seed, fallback)
        return raw
    if kind == "single":
        opts = list(v.get("tomorrow_single_openers") or [])
        fallback = "Tomorrow at Sacred Ground — {title}."
        raw = _pick_rotating(opts, seed, fallback)
        return raw.replace("{title}", title or "Sacred Ground")
    opts = list(v.get("tomorrow_openers") or [])
    fallback = "See what you can do tomorrow at Sacred Ground — {day_label}."
    raw = _pick_rotating(opts, seed, fallback)
    return raw.replace("{day_label}", day_label or "tomorrow")


def _free_community_note(ev: Event) -> str:
    from .classify import is_free_community_event

    if is_free_community_event(ev) or "free" in (ev.cost or "").lower():
        if "community" in (ev.title or "").lower() or is_free_community_event(ev):
            return "Free community gathering — all are welcome."
    return ""


def caption_today(
    events: List[Event],
    platform: str,
    day: date,
    *,
    tonight_events: List[Event] | None = None,
) -> Dict:
    """Morning caption — `day` is tomorrow's calendar day; optional tonight evening add-on."""
    tonight = list(tonight_events or [])
    tomorrow = list(events or [])
    # If caller passed a combined list, split by calendar day when tonight not set.
    if not tonight and tomorrow:
        from .ingest import parse_tec_datetime

        split_t, split_m = [], []
        for ev in tomorrow:
            start = parse_tec_datetime(ev.start_date)
            if start and start.date() != day:
                split_t.append(ev)
            else:
                split_m.append(ev)
        if split_t:
            tonight, tomorrow = split_t, split_m

    if not tomorrow and not tonight:
        return caption_today_visit(platform, day)

    day_label = day.strftime("%A, %B %d").replace(" 0", " ")
    with_links = True
    seed = f"today|{day.isoformat()}|{platform}"

    if tomorrow and not tonight and len(tomorrow) == 1:
        ev = tomorrow[0]
        if is_community_meditation(ev):
            hook = _tomorrow_hook(f"{seed}|med", kind="meditation")
            body = hook + "\n\n" + meditation_event_block(day=day, event=ev)
        else:
            blurb = short_blurb(ev, 180)
            hook = _tomorrow_hook(f"{seed}|single", title=ev.title, kind="single")
            body_bits = [hook, format_when(ev)]
            note = _free_community_note(ev)
            if note:
                body_bits.append(note)
            if blurb:
                body_bits.append(blurb)
            body_bits.append(ev.url)
            body = "\n\n".join(body_bits)
    elif tomorrow:
        hook = _tomorrow_hook(f"{seed}|multi", day_label=day_label, kind="multi")
        body = hook + "\n\n" + _join_event_blocks(tomorrow, with_links)
        body += "\n\nDetails & signup on each event page."
    else:
        hook = "Tonight at Sacred Ground — something beautiful still ahead."
        body = hook

    if tonight:
        body += "\n\nTonight at Sacred Ground\n\n" + _join_event_blocks(tonight, with_links)
        for ev in tonight:
            note = _free_community_note(ev)
            if note and note not in body:
                body += f"\n\n{note}"

    body += "\n\n" + _signoff(seed, platform)
    tags = _hashtags(platform)
    text = body + "\n\n" + " ".join(tags)
    _assert_not_generic(text)
    return {"text": text, "hashtags": tags, "hook": hook}


def caption_today_visit(platform: str, day: date) -> Dict:
    """Empty next-day calendar — still post a warm visit/brand invite."""
    day_label = day.strftime("%A, %B %d").replace(" 0", " ")
    hook = "Tomorrow’s a beautiful day to visit Sacred Ground."
    body = (
        f"{hook}\n\n"
        f"Nothing fixed on the calendar for {day_label} — come browse anyway.\n\n"
        "Chicagoland’s most famous crystal shop — crystals, books, gifts, "
        "and a floor full of curious finds in Arlington Heights.\n\n"
        "Come for cool and unusual things whenever you need a little sparkle.\n"
        "847-749-3922\n"
        "https://shopsacredground.com/\n\n"
        + _signoff(f"today-visit|{day.isoformat()}|{platform}", platform)
    )
    tags = _hashtags(platform)
    text = body + "\n\n" + " ".join(tags)
    _assert_not_generic(text)
    return {"text": text, "hashtags": tags, "hook": hook}


def caption_week(events: List[Event], platform: str, week_start: date) -> Dict:
    if not events:
        raise ValueError("week caption requires events")
    from datetime import timedelta

    week_end = week_start + timedelta(days=6)
    range_label = f"{week_start.strftime('%b %d').replace(' 0',' ')}–{week_end.strftime('%b %d').replace(' 0',' ')}"
    hook = f"This week at Sacred Ground ({range_label})."
    body = hook + "\n\n" + _join_event_blocks_by_day(events, True)
    body += "\n\nCome for one — or make a day of it."
    body += "\n\n" + _signoff(f"week|{week_start.isoformat()}|{platform}", platform)
    tags = _hashtags(platform)
    text = body + "\n\n" + " ".join(tags)
    if platform == "instagram":
        max_chars = int(voice().get("instagram_style", {}).get("max_chars") or 2100)
        if len(text) > max_chars:
            text = text[: max_chars - 1].rsplit(" ", 1)[0] + "…"
    _assert_not_generic(text)
    return {"text": text, "hashtags": tags, "hook": hook}


def _pick_rotating(opts: List[str], seed: str, fallback: str) -> str:
    cleaned = [o.rstrip() for o in opts if o and str(o).strip()]
    if not cleaned:
        return fallback
    idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(cleaned)
    return cleaned[idx]


def _week_ahead_opener(seed: str) -> str:
    cfg = voice()
    opts = list(cfg.get("week_ahead_openers") or [])
    if not opts and cfg.get("week_ahead_opener"):
        opts = [str(cfg["week_ahead_opener"])]
    # Never append stale “this week” closings.
    opts = [o for o in opts if o and "this week" not in o.lower()]
    return _pick_rotating(
        opts,
        seed,
        "As the shop settles in for the night, we’re reminded that tomorrow’s another day—and there’s plenty to look forward to.",
    )


def _week_ahead_night_block(seed: str) -> str:
    cfg = voice()
    opts = list(cfg.get("week_ahead_night_blocks") or [])
    if not opts and cfg.get("week_ahead_night_block"):
        opts = [str(cfg["week_ahead_night_block"])]
    return _pick_rotating(
        opts,
        seed,
        "If you’re not done for the night yet…\n"
        "Peek at the Observatory — it changes every day.\n"
        "https://shopsacredground.com/sacred-ground-observatory/\n\n"
        "And don’t forget the Library: download a meditation or playlist, "
        "find something to watch or listen to, or explore sacred chanting and music.\n"
        "https://shopsacredground.com/library/",
    )


def _week_ahead_closer(seed: str, day: date | None = None) -> str:
    """Pick a goodnight closer. Day-ordinal rotation so nights never stick on one line."""
    cfg = voice()
    opts = [o.rstrip() for o in (cfg.get("week_ahead_closers") or []) if o and str(o).strip()]
    fallback = "The door is always open...we will leave the light on"
    if not opts:
        return fallback
    if day is not None:
        return opts[day.toordinal() % len(opts)]
    return _pick_rotating(opts, seed, fallback)


def caption_week_ahead(events: List[Event], platform: str, day: date) -> Dict:
    """Daily evening planner — upcoming days in caption; night creative photo."""
    if not events:
        raise ValueError("week_ahead caption requires events")

    cfg = voice()
    seed = f"week_ahead|{day.isoformat()}|{platform}"
    # Separate seeds so opener / night block / closer don't lock to the same index.
    hook = _week_ahead_opener(f"{seed}|opener")
    body = hook + "\n\n" + _join_event_blocks_by_day(events, True)
    night = _week_ahead_night_block(f"{seed}|night")
    if night:
        body += "\n\n" + night
    body += "\n\nCall to book a session or grab your spot online."
    body += "\n847-749-3922"
    body += "\nhttps://shopsacredground.com/events/"
    # Standalone goodnight — day-based so FB+IG match and consecutive nights differ.
    closer = _week_ahead_closer(f"{seed}|closer", day=day)
    body += "\n\n" + closer
    tags = _hashtags(platform)
    text = body + "\n\n" + " ".join(tags)
    if platform == "instagram":
        max_chars = int(cfg.get("instagram_style", {}).get("max_chars") or 2100)
        if len(text) > max_chars:
            text = text[: max_chars - 1].rsplit(" ", 1)[0] + "…"
    _assert_not_generic(text)
    return {"text": text, "hashtags": tags, "hook": hook}


def caption_tuesday_meditation(platform: str, day: date) -> Dict:
    """Standalone Tuesday Free Community Meditation post (not the morning tomorrow lineup)."""
    seed = f"tuesday_meditation|{day.isoformat()}|{platform}"
    host = host_for_day(day)
    openers = list(voice().get("tuesday_meditation_openers") or [])
    raw_hook = _pick_rotating(
        openers,
        f"{seed}|opener",
        "Tonight at Sacred Ground — Free Community Meditation.",
    )
    hook = format_tuesday_meditation_opener(raw_hook, host)
    body = hook + "\n\n" + meditation_event_block(day=day)
    body += "\n\n" + _signoff(seed, platform)
    tags = _hashtags(platform)
    text = body + "\n\n" + " ".join(tags)
    _assert_not_generic(text)
    return {"text": text, "hashtags": tags, "hook": hook}


def caption_afternoon_spotlight(event: Event | None, platform: str, day: date) -> Dict:
    """Single-event afternoon spotlight (or warm brand invite when empty)."""
    seed = f"afternoon_spotlight|{day.isoformat()}|{platform}"
    if event is None:
        hook = "A little afternoon light from Sacred Ground."
        body = (
            f"{hook}\n\n"
            "Crystals, curious finds, and a soft place to land in Arlington Heights.\n"
            "Come browse when the day needs a spark.\n"
            "847-749-3922\n"
            "https://shopsacredground.com/\n\n"
            + _signoff(seed, platform)
        )
        tags = _hashtags(platform)
        text = body + "\n\n" + " ".join(tags)
        _assert_not_generic(text)
        return {"text": text, "hashtags": tags, "hook": hook}

    when = format_when(event)
    blurb = short_blurb(event, 200)
    note = _free_community_note(event)
    from .ingest import parse_tec_datetime

    start = parse_tec_datetime(event.start_date)
    same_day = bool(start and start.date() == day)
    if same_day:
        openers = list(voice().get("afternoon_spotlight_tonight_openers") or [])
        fallback = "Tonight at Sacred Ground — {title}."
    else:
        openers = list(voice().get("afternoon_spotlight_tomorrow_openers") or [])
        fallback = "Looking ahead — {title} at Sacred Ground."
    raw = _pick_rotating(openers, f"{seed}|opener", fallback)
    hook = raw.replace("{title}", event.title)

    parts = [hook, when]
    if note:
        parts.append(note)
    if blurb:
        parts.append(blurb)
    parts.append(event.url)
    parts.append("847-749-3922")
    parts.append(_signoff(seed, platform))
    body = "\n\n".join(parts)
    tags = _hashtags(platform)
    text = body + "\n\n" + " ".join(tags)
    _assert_not_generic(text)
    return {"text": text, "hashtags": tags, "hook": hook}


def caption_spotlight(event: Event, platform: str, reminder_day: int | None = None) -> Dict:
    when = format_when(event)
    blurb = short_blurb(event, 220)
    if reminder_day == 1:
        hook = f"Tomorrow at Sacred Ground: {event.title}."
    elif reminder_day == 3:
        hook = f"Three days out — {event.title}."
    elif reminder_day == 7:
        hook = f"One week until {event.title}."
    else:
        hook = f"Spotlight: {event.title}."

    parts = [hook, when]
    if blurb:
        parts.append(blurb)
    if event.categories:
        parts.append("Filed under: " + ", ".join(event.categories[:3]))
    parts.append(event.url)
    parts.append(_signoff(f"spotlight|{event.id}|{platform}|{reminder_day}", platform))
    body = "\n\n".join(parts)
    tags = _hashtags(platform, ["#SpecialEvent"] if event.is_special else None)
    text = body + "\n\n" + " ".join(tags)
    _assert_not_generic(text)
    return {"text": text, "hashtags": tags, "hook": hook}
