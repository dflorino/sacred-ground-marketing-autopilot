"""Shared Free Community Meditation caption helpers (Today + tuesday_meditation)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import date, datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional, Sequence

from .ingest import parse_tec_datetime
from .models import Event
from .paths import CONFIG_DIR, _load_json, settings

MEDITATION_HOSTS_PATH = os.path.join(CONFIG_DIR, "meditation_hosts.json")

# Fallback only if config/settings.json omits doors_close_display.
_DEFAULT_DOORS_CLOSE_DISPLAY = "7:05pm"
_DEFAULT_SESSION_DISPLAY = "Tuesday night 7:00–8:00 PM"

# Facilitator first names / known hosts — never appear in public meditation captions.
_FACILITATOR_NAME_RE = re.compile(
    r"\b("
    r"Amber|Eve|Andre(?:\s+Peraza)?|Rose|Cheryl|Mother\s+Lotus|"
    r"Randa(?:\s+Clark)?|Richard(?:\s+Popp)?|Janel|Lisa(?:\s+Maria)?|"
    r"Tina|Adie|Sherry(?:\s+Gurley)?|Renee|Melissa|Pat(?:\s+Sample)?"
    r")\b",
    re.IGNORECASE,
)


def doors_close_display() -> str:
    """Single source of truth for caption 'Doors close at …' (Founder-editable in settings)."""
    cfg = settings().get("tuesday_community_meditation") or {}
    raw = str(cfg.get("doors_close_display") or "").strip()
    return raw or _DEFAULT_DOORS_CLOSE_DISPLAY


def doors_close_line() -> str:
    """Caption line — no o'clock; e.g. 'Doors close at 7:05pm'."""
    return f"Doors close at {doors_close_display()}"


def _format_clock(hhmm: str) -> str:
    t = datetime.strptime(hhmm, "%H:%M").time()
    hour = t.hour % 12 or 12
    ampm = "AM" if t.hour < 12 else "PM"
    return f"{hour}:{t.minute:02d} {ampm}"


def session_display() -> str:
    """Public session when line — never names a facilitator (Founder 2026-08-09)."""
    cfg = settings().get("tuesday_community_meditation") or {}
    raw = str(cfg.get("session_display") or "").strip()
    if raw:
        return raw
    stub = cfg.get("stub") or {}
    start_s = str(stub.get("start_time") or "19:00").strip()
    end_s = str(stub.get("end_time") or "20:00").strip()
    try:
        return f"Tuesday night {_format_clock(start_s)}–{_format_clock(end_s)}"
    except ValueError:
        return _DEFAULT_SESSION_DISPLAY


@dataclass(frozen=True)
class MeditationHost:
    practitioner: str
    style: str


@lru_cache(maxsize=1)
def meditation_hosts_config() -> Dict[str, Any]:
    return _load_json(MEDITATION_HOSTS_PATH)


def clear_meditation_hosts_cache() -> None:
    meditation_hosts_config.cache_clear()


def load_host_roster() -> List[MeditationHost]:
    """Internal ops roster only — never used in public captions (Founder 2026-08-09)."""
    cfg = meditation_hosts_config()
    out: List[MeditationHost] = []
    for raw in cfg.get("hosts") or []:
        if not isinstance(raw, dict):
            continue
        practitioner = str(raw.get("practitioner") or "").strip()
        style = str(raw.get("style") or "").strip()
        if practitioner and style:
            out.append(MeditationHost(practitioner=practitioner, style=style))
    return out


def iso_week_rotation_index(day: date, size: int) -> int:
    """Stable weekly index from ISO year/week (Chicago local date)."""
    if size <= 0:
        return 0
    iso = day.isocalendar()
    return (iso.year * 53 + iso.week) % size


def parse_host_from_event(event: Optional[Event]) -> Optional[MeditationHost]:
    """Parse host/style from TEC text for ops use only — never for public captions."""
    if event is None:
        return None
    blob = "\n".join(
        part
        for part in (event.title or "", event.excerpt or "", event.description or "")
        if part
    )
    if not blob.strip():
        return None

    # With Name · Style  /  With Name - Style  /  With Name — Style
    # Horizontal whitespace only so title+description join cannot span lines.
    m = re.search(
        r"[Ww]ith[^\S\n]+([A-Z][\w'’.\-]+(?:[^\S\n]+[A-Z][\w'’.\-]+){0,3})"
        r"[^\S\n]*[·\-–—][^\S\n]*([^\n.!?]{2,60})",
        blob,
    )
    if m:
        return MeditationHost(
            practitioner=m.group(1).strip(),
            style=m.group(2).strip().rstrip(" ."),
        )

    # Led by Name
    m = re.search(
        r"[Ll]ed by\s+([A-Z][\w'’.\-]+(?:\s+[A-Z][\w'’.\-]+){0,3})",
        blob,
    )
    if m:
        return MeditationHost(
            practitioner=m.group(1).strip(),
            style="Community meditation",
        )

    return None


def host_for_day(
    day: Optional[date],
    event: Optional[Event] = None,
    *,
    roster: Optional[Sequence[MeditationHost]] = None,
) -> Optional[MeditationHost]:
    """Resolve this Tuesday's practitioner/style for ops — not for public captions."""
    parsed = parse_host_from_event(event)
    if parsed is not None:
        return parsed
    if day is None:
        return None
    hosts = list(roster) if roster is not None else load_host_roster()
    if not hosts:
        return None
    return hosts[iso_week_rotation_index(day, len(hosts))]


def day_from_event(event: Optional[Event]) -> Optional[date]:
    if event is None:
        return None
    start = parse_tec_datetime(event.start_date)
    return start.date() if start else None


def strip_facilitator_names(text: str) -> str:
    """Remove known facilitator names from meditation-related public copy."""
    if not text:
        return text
    cleaned = _FACILITATOR_NAME_RE.sub("", text)
    cleaned = re.sub(
        r"\s*[|·\-–—]\s*(?=\s|$)",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"\b(?:with|led by|hosted by|facilitated by)\s*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\s+([,.;:])", r"\1", cleaned)
    return cleaned.strip(" -—·|,")


def public_meditation_title(event: Optional[Event] = None) -> str:
    """Always the anonymous community title — never facilitator-named TEC titles."""
    title = str((event.title if event else "") or "").strip()
    if title:
        stripped = strip_facilitator_names(title)
        low = stripped.lower()
        if "community meditation" in low or (
            "meditation" in low and "community" in low
        ):
            return "Free Community Meditation"
        if stripped and not _FACILITATOR_NAME_RE.search(stripped):
            # Keep specialty meditation titles only when no facilitator remains.
            if "meditation" in low and "lions gate" not in low:
                return stripped
    return "Free Community Meditation"


def meditation_event_block(
    day: Optional[date] = None,
    event: Optional[Event] = None,
    *,
    roster: Optional[Sequence[MeditationHost]] = None,
) -> str:
    """Anonymous Free Community Meditation block — never names who leads (Founder).

    day/roster are accepted for call-site compatibility but ignored for public copy.
    """
    _ = (day, roster)
    return "\n".join(
        [
            f"• {public_meditation_title(event)}",
            session_display(),
            "All are welcome",
            "No sign-up needed",
            doors_close_line(),
        ]
    )


def format_tuesday_meditation_opener(
    template: str,
    host: Optional[MeditationHost] = None,
) -> str:
    """Fill opener without naming facilitators (host arg ignored for public copy)."""
    del host
    tmpl = (template or "").strip() or (
        "Tonight at Sacred Ground — Free Community Meditation."
    )
    cleaned = (
        tmpl.replace(" with {practitioner}", "")
        .replace(" — {style}", "")
        .replace(" ({style})", "")
        .replace("{practitioner}", "")
        .replace("{style}", "")
    )
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" -—·")
    cleaned = strip_facilitator_names(cleaned)
    return cleaned or "Tonight at Sacred Ground — Free Community Meditation."
