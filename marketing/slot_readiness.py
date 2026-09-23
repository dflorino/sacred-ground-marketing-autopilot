"""Fail-closed check: a planned social theme must have a plate before 5pm posts.

Libra Season (Sep 22 2026) lived in the master calendar as `needs_creative`.
Afternoon Autopilot still published a regular event still. Morning does not
do that — no flyer row, no 9am plate. This module is the afternoon twin.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from .ingest import today_local
from .paths import CONFIG_DIR, read_json

MASTER_PATH = f"{CONFIG_DIR}/master_social_calendar.json"
BLOCKING = {"needs_creative", "required", "missing", "locked"}
OPTIONAL = {
    "optional_skip",
    "optional",
    "skip",
    "caption_only",
    "rest",
    "default_pool",
}


def load_master() -> Dict[str, Any]:
    data = read_json(MASTER_PATH, {})
    return data if isinstance(data, dict) else {}


def _plate_ready(day: date) -> bool:
    from . import images

    pinned = images._afternoon_plate_for_day(day)
    if not pinned or pinned.get("do_not_publish"):
        return False
    return bool(str(pinned.get("url") or "").strip())


def _plan_afternoon(day: date) -> Optional[Dict[str, Any]]:
    days = ((load_master().get("near_term_slot_plan") or {}).get("days")) or {}
    row = days.get(day.isoformat())
    if not isinstance(row, dict):
        return None
    aft = row.get("afternoon")
    return aft if isinstance(aft, dict) else None


def _morning_companion(day: date) -> Optional[str]:
    from . import morning_flyers as mf

    entry = mf.flyer_entry_for_day(day)
    if not isinstance(entry, dict):
        return None
    key = str(entry.get("afternoon_companion") or "").strip()
    return key or None


def _master_zodiac_on(day: date) -> List[Dict[str, Any]]:
    hits: List[Dict[str, Any]] = []
    for ev in load_master().get("entries") or []:
        if not isinstance(ev, dict):
            continue
        if str(ev.get("date") or "") != day.isoformat():
            continue
        series = ev.get("series") or []
        if "zodiac_season" in series:
            hits.append(ev)
    return hits


def _missing(
    day: date, theme: str, status: str, detail: str
) -> Dict[str, Any]:
    return {
        "ok": False,
        "reason": "required_plate_missing",
        "day": day.isoformat(),
        "theme": theme,
        "status": status,
        "detail": detail,
    }


def afternoon_block(day: date) -> Optional[Dict[str, Any]]:
    """If set, 5pm must not invent a still — make the planned plate first."""
    from . import images

    if images.skip_afternoon_publish(day):
        return {
            "ok": False,
            "reason": "cinematic_short_owns_slot",
            "day": day.isoformat(),
            "theme": "cinematic short owns 5pm",
        }
    aft = _plan_afternoon(day)
    if aft:
        status = str(aft.get("status") or "").strip()
        theme = str(aft.get("theme") or "afternoon theme").strip()
        if status in OPTIONAL:
            return None
        if status in BLOCKING and not _plate_ready(day):
            return _missing(
                day,
                theme,
                status,
                (
                    f"{day.isoformat()} afternoon is {theme!r} ({status}) "
                    "and has no afternoon_spotlight_plates.json URL. "
                    "Do not publish a generic event still."
                ),
            )
    companion = _morning_companion(day)
    if companion and not _plate_ready(day):
        return _missing(
            day,
            companion,
            "afternoon_companion",
            (
                f"{day.isoformat()} morning flyer names afternoon_companion "
                f"{companion!r} and no afternoon plate exists. "
                "Do not publish a generic event still."
            ),
        )
    # Season opens on the master dates list (Scorpio, etc.) fail closed
    # unless this day's near-term afternoon is explicitly optional.
    if aft and str(aft.get("status") or "").strip() in OPTIONAL:
        return None
    for ev in _master_zodiac_on(day):
        if _plate_ready(day):
            return None
        title = str(ev.get("title") or "zodiac season")
        return _missing(
            day,
            title,
            "zodiac_season",
            (
                f"{day.isoformat()} master calendar has {title!r} "
                "(zodiac_season) and no afternoon plate. "
                "Do not publish a generic event still."
            ),
        )
    return None


def check_range(days: int = 7, start: Optional[date] = None) -> Dict[str, Any]:
    """Next N Chicago days — ready vs missing planned plates."""
    start = start or today_local()
    rows: List[Dict[str, Any]] = []
    missing = 0
    cinematic = 0
    for i in range(max(1, int(days))):
        day = start + timedelta(days=i)
        block = afternoon_block(day)
        aft = _plan_afternoon(day) or {}
        reason = (block or {}).get("reason")
        row = {
            "day": day.isoformat(),
            "weekday": day.strftime("%a"),
            "afternoon_theme": (aft.get("theme") or _morning_companion(day)),
            "afternoon_status": (aft.get("status") or None),
            "plate_ready": _plate_ready(day),
            "block": block,
        }
        if reason == "required_plate_missing":
            missing += 1
        if reason == "cinematic_short_owns_slot":
            cinematic += 1
        rows.append(row)
    return {
        "ok": missing == 0,
        "missing": missing,
        "cinematic_skips": cinematic,
        "days": rows,
        "how": (
            "Wire a URL into config/afternoon_spotlight_plates.json "
            "plates[YYYY-MM-DD] (or skip_publish_dates if a short owns 5pm). "
            "Until then, publish-afternoon-spotlight fails closed."
        ),
    }
