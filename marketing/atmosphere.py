"""Day/night atmosphere plan for Sacred Ground social images.

Morning (today): specialty library only — no seasons.
Night (week_ahead): eggplant-purple storefront; priority full_moon > holiday > season.
"""
from __future__ import annotations

import json
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .paths import ROOT


@lru_cache(maxsize=1)
def atmosphere_config() -> Dict[str, Any]:
    path = Path(ROOT) / "config" / "image_atmosphere.json"
    return json.loads(path.read_text(encoding="utf-8"))


def season_for(day: date) -> str:
    cfg = atmosphere_config().get("nighttime") or {}
    seasons = cfg.get("seasons") or {}
    for name, meta in seasons.items():
        months = meta.get("months") or []
        if day.month in months:
            return str(name)
    return "summer"


def season_meta(day: date) -> Dict[str, Any]:
    name = season_for(day)
    return ((atmosphere_config().get("nighttime") or {}).get("seasons") or {}).get(name) or {}


def season_look(day: date) -> str:
    return str(season_meta(day).get("look") or season_for(day))


def is_full_moon(day: date) -> bool:
    """
    Approximate full-moon check for America/Chicago calendar days.
    Synodic month anchored to 2026-08-28 full moon.
    """
    anchor = date(2026, 8, 28)
    synodic = 29.530588853
    delta = (day - anchor).days
    nearest = min(delta % synodic, synodic - (delta % synodic))
    return nearest <= 0.6


def _parse_md(token: str, year: int) -> date:
    month_s, day_s = token.split("-")
    return date(year, int(month_s), int(day_s))


def _in_md_window(day: date, start_md: str, end_md: str) -> bool:
    """Month-day windows; supports wrap across year (e.g. 12-24 .. 01-02)."""
    start = _parse_md(start_md, day.year)
    end = _parse_md(end_md, day.year)
    if start <= end:
        return start <= day <= end
    # wraps year boundary
    return day >= start or day <= end


def holiday_for(day: date) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Return (holiday_id, meta) if day falls in a configured holiday window."""
    holidays = ((atmosphere_config().get("nighttime") or {}).get("holidays") or {})
    # Prefer more specific / shorter windows when overlap (Hanukkah date_ranges first).
    ordered = sorted(
        holidays.items(),
        key=lambda kv: (
            0 if kv[1].get("date_ranges") else 1,
            str(kv[0]),
        ),
    )
    for hid, meta in ordered:
        for rng in meta.get("date_ranges") or []:
            try:
                start = datetime.strptime(str(rng["start"]), "%Y-%m-%d").date()
                end = datetime.strptime(str(rng["end"]), "%Y-%m-%d").date()
            except (KeyError, ValueError):
                continue
            if start <= day <= end:
                return str(hid), meta
        for win in meta.get("windows") or []:
            if _in_md_window(day, str(win["start"]), str(win["end"])):
                return str(hid), meta
    return None


def daytime_plan(day: date, specialty: Optional[str] = None) -> Dict[str, Any]:
    specialty_key = specialty or "multi_or_empty"
    return {
        "campaign": "today",
        "seasons": False,
        "specialty": specialty_key,
        "source": "config/image_rules.json",
        "prompt_hint": (
            "Sacred Ground morning Today image: use specialty library rules only "
            f"(specialty={specialty_key}). No seasonal or holiday overlays."
        ),
    }


def nighttime_plan(day: date) -> Dict[str, Any]:
    night = atmosphere_config().get("nighttime") or {}
    base = night.get("base_style") or "Sacred Ground exterior storefront"
    season = season_for(day)
    s_meta = season_meta(day)

    # Priority 1: full moon only
    full_cfg = night.get("full_moon") or {}
    if full_cfg.get("enabled", True) and is_full_moon(day):
        url = str(full_cfg.get("url") or "")
        return {
            "campaign": "week_ahead",
            "mode": "full_moon",
            "season": season,
            "holiday": None,
            "full_moon": True,
            "image_url": url,
            "season_look": "full moon night — dedicated full-moon storefront only",
            "cart": "as shown on full-moon plate",
            "prompt_hint": (
                f"Sacred Ground nighttime storefront FULL MOON only. Base: {base} "
                "Use the dedicated full-moon image. Do not paint events onto the image."
            ),
        }

    # Priority 2: holiday
    hit = holiday_for(day)
    if hit:
        hid, h_meta = hit
        return {
            "campaign": "week_ahead",
            "mode": "holiday",
            "season": season,
            "holiday": hid,
            "full_moon": False,
            "image_url": str(h_meta.get("url") or ""),
            "season_look": str(h_meta.get("look") or hid),
            "cart": str(h_meta.get("cart") or ""),
            "prompt_hint": (
                f"Sacred Ground nighttime storefront HOLIDAY={hid}. Base: {base} "
                f"Outdoors: {h_meta.get('look')}. Cart: {h_meta.get('cart')}. "
                "Do not invent a different building. Events stay in caption."
            ),
        }

    # Priority 3: season
    return {
        "campaign": "week_ahead",
        "mode": "season",
        "season": season,
        "holiday": None,
        "full_moon": False,
        "image_url": str(s_meta.get("url") or ""),
        "season_look": str(s_meta.get("look") or season),
        "cart": str(s_meta.get("cart") or ""),
        "atmosphere": str(s_meta.get("lighting") or ""),
        "prompt_hint": (
            f"Sacred Ground nighttime storefront. Base: {base} "
            f"Season={season}: {s_meta.get('look')}. Lighting: {s_meta.get('lighting')}. "
            f"Cart: {s_meta.get('cart')}. Events stay in caption."
        ),
    }


def night_image_url(day: date) -> Optional[str]:
    plan = nighttime_plan(day)
    url = plan.get("image_url")
    return str(url) if url else None
