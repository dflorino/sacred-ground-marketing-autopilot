from __future__ import annotations

import hashlib
from datetime import date
from typing import Dict, List, Sequence

from .classify import format_when, short_blurb
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


def _event_line(ev: Event, with_link: bool) -> str:
    when = format_when(ev)
    line = f"• {ev.title} — {when}"
    if with_link and ev.url:
        line += f"\n  {ev.url}"
    return line


def caption_today(events: List[Event], platform: str, day: date) -> Dict:
    if not events:
        return caption_today_visit(platform, day)
    day_label = day.strftime("%A, %B %d").replace(" 0", " ")
    with_links = platform == "facebook" or True
    lines = [_event_line(e, with_links) for e in events]
    if len(events) == 1:
        ev = events[0]
        blurb = short_blurb(ev, 180)
        hook = f"Today at Sacred Ground — {ev.title}."
        body_bits = [hook, format_when(ev)]
        if blurb:
            body_bits.append(blurb)
        body_bits.append(ev.url)
        body = "\n\n".join(body_bits)
    else:
        hook = f"Today at Sacred Ground — {day_label}."
        body = hook + "\n\n" + "\n".join(lines)
        body += "\n\nDetails & tickets on each event page."
    body += "\n\n" + _signoff(f"today|{day.isoformat()}|{platform}", platform)
    tags = _hashtags(platform)
    text = body + "\n\n" + " ".join(tags)
    _assert_not_generic(text)
    return {"text": text, "hashtags": tags, "hook": hook}


def caption_today_visit(platform: str, day: date) -> Dict:
    """Empty calendar day — still post a warm visit/brand invite."""
    hook = "Visit Sacred Ground for cool and unusual things."
    body = (
        f"{hook}\n\n"
        "Chicagoland’s most famous crystal shop — crystals, books, gifts, "
        "and a floor full of curious finds in Arlington Heights.\n\n"
        "Come browse when you need a little sparkle in the day.\n"
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
    lines = [_event_line(e, True) for e in events]
    body = hook + "\n\n" + "\n".join(lines)
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


def caption_week_ahead(events: List[Event], platform: str, day: date) -> Dict:
    """Daily evening planner — next 7 days so people can book ahead."""
    if not events:
        raise ValueError("week_ahead caption requires events")
    from datetime import timedelta

    cfg = voice()
    end = day + timedelta(days=6)
    range_label = (
        f"{day.strftime('%a %b %d').replace(' 0', ' ')}"
        f"–{end.strftime('%a %b %d').replace(' 0', ' ')}"
    )
    hook = f"What’s ahead at Sacred Ground ({range_label})."
    lines = [_event_line(e, True) for e in events]
    body = hook + "\n\n" + "\n".join(lines)
    body += "\n\nPlan your week — call to book a session or grab your spot online."
    body += "\n847-749-3922"
    body += "\nhttps://shopsacredground.com/events/"
    body += "\n\n" + _signoff(f"week_ahead|{day.isoformat()}|{platform}", platform)
    tags = _hashtags(platform)
    text = body + "\n\n" + " ".join(tags)
    if platform == "instagram":
        max_chars = int(cfg.get("instagram_style", {}).get("max_chars") or 2100)
        if len(text) > max_chars:
            text = text[: max_chars - 1].rsplit(" ", 1)[0] + "…"
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
