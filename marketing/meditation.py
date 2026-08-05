"""Shared Free Community Meditation caption helpers (Today + tuesday_meditation)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from typing import Any, Dict, List, Optional, Sequence

from .ingest import parse_tec_datetime
from .models import Event
from .paths import CONFIG_DIR, _load_json, settings

MEDITATION_HOSTS_PATH = os.path.join(CONFIG_DIR, "meditation_hosts.json")

# Fallback only if config/settings.json omits doors_close_display.
_DEFAULT_DOORS_CLOSE_DISPLAY = "7:05pm"


def doors_close_display() -> str:
    """Single source of truth for caption 'Doors close at …' (Founder-editable in settings)."""
    cfg = settings().get("tuesday_community_meditation") or {}
    raw = str(cfg.get("doors_close_display") or "").strip()
    return raw or _DEFAULT_DOORS_CLOSE_DISPLAY


def doors_close_line() -> str:
    """Caption line — no o'clock; e.g. 'Doors close at 7:05pm'."""
    return f"Doors close at {doors_close_display()}"


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
    """Prefer host/style embedded in TEC title/description when present."""
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
    m = re.search(
        r"[Ww]ith\s+([A-Z][\w'’.\-]+(?:\s+[A-Z][\w'’.\-]+){0,3})"
        r"\s*[·\-–—]\s*([^\n.!?]{2,60})",
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
    """Resolve this Tuesday's practitioner/style — TEC parse first, else weekly roster."""
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


def meditation_event_block(
    day: Optional[date] = None,
    event: Optional[Event] = None,
    *,
    roster: Optional[Sequence[MeditationHost]] = None,
) -> str:
    """Daytime Free Community Meditation block — no time line, booking URL, or goodnight."""
    resolved_day = day or day_from_event(event)
    host = host_for_day(resolved_day, event, roster=roster)
    lines = ["• Free Community Meditation"]
    if host:
        lines.append(f"With {host.practitioner} · {host.style}")
    lines.extend(
        [
            "All are welcome",
            "No sign-up needed",
            doors_close_line(),
        ]
    )
    return "\n".join(lines)


def format_tuesday_meditation_opener(
    template: str,
    host: Optional[MeditationHost],
) -> str:
    """Fill opener placeholders or append With Practitioner · Style when present."""
    tmpl = (template or "").strip() or (
        "Tonight at Sacred Ground — Free Community Meditation."
    )
    if host and ("{practitioner}" in tmpl or "{style}" in tmpl):
        return tmpl.format(practitioner=host.practitioner, style=host.style)
    cleaned = (
        tmpl.replace(" with {practitioner}", "")
        .replace(" — {style}", "")
        .replace(" ({style})", "")
        .replace("{practitioner}", "")
        .replace("{style}", "")
    )
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" -—·")
    if not host:
        return cleaned or "Tonight at Sacred Ground — Free Community Meditation."
    low = cleaned.lower()
    if host.practitioner.lower() in low:
        return cleaned
    base = cleaned.rstrip(".")
    return f"{base} — with {host.practitioner} · {host.style}."
