"""Day/night atmosphere plan for Sacred Ground social images.

Morning (today): specialty library only — no seasons.
Night (week_ahead): uploaded storefront vein + seasonal outdoors (+ sky mood).
"""
from __future__ import annotations

import json
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from .paths import ROOT


@lru_cache(maxsize=1)
def atmosphere_config() -> Dict[str, Any]:
    path = Path(ROOT) / "config" / "image_atmosphere.json"
    return json.loads(path.read_text(encoding="utf-8"))


def season_for(day: date) -> str:
    """Season applies to nighttime storefront outdoors only."""
    cfg = atmosphere_config().get("nighttime") or {}
    seasons = cfg.get("seasons") or {}
    for name, meta in seasons.items():
        months = meta.get("months") or []
        if day.month in months:
            return str(name)
    return "summer"


def season_look(day: date) -> str:
    name = season_for(day)
    meta = ((atmosphere_config().get("nighttime") or {}).get("seasons") or {}).get(name) or {}
    return str(meta.get("look") or name)


def is_full_moon(day: date) -> bool:
    """
    Approximate full-moon check for America/Chicago calendar days.
    Uses the known synodic cycle anchored to a recent full moon.
    Good enough for social art; can swap to a precise ephemeris later.
    """
    anchor = date(2026, 8, 28)
    synodic = 29.530588853
    delta = (day - anchor).days
    nearest = min(delta % synodic, synodic - (delta % synodic))
    return nearest <= 0.6


def night_mood(day: date) -> str:
    night = atmosphere_config().get("nighttime") or {}
    sky = night.get("sky_moods") or {}
    full_cfg = sky.get("full_moon") or {}
    if full_cfg.get("enabled", True) and full_cfg.get("overrides_rotation", True):
        if is_full_moon(day):
            return "full_moon"
    rotation: List[str] = list(sky.get("default_rotation") or ["sunset"])
    if not rotation:
        return "sunset"
    return rotation[day.toordinal() % len(rotation)]


def daytime_plan(day: date, specialty: Optional[str] = None) -> Dict[str, Any]:
    """Morning posts: specialty library only — seasons intentionally off."""
    specialty_key = specialty or "multi_or_empty"
    return {
        "campaign": "today",
        "seasons": False,
        "specialty": specialty_key,
        "source": "config/image_rules.json",
        "prompt_hint": (
            "Sacred Ground morning Today image: use specialty library rules only "
            f"(specialty={specialty_key}). No seasonal overlays."
        ),
    }


def nighttime_plan(day: date) -> Dict[str, Any]:
    season = season_for(day)
    look = season_look(day)
    mood = night_mood(day)
    sky = ((atmosphere_config().get("nighttime") or {}).get("sky_moods") or {})
    moods = sky.get("moods") or {}
    mood_look = moods.get(mood) or mood
    base = (atmosphere_config().get("nighttime") or {}).get("base_style") or (
        "Sacred Ground exterior storefront vein"
    )
    return {
        "campaign": "week_ahead",
        "season": season,
        "season_look": look,
        "mood": mood,
        "atmosphere": mood_look,
        "full_moon": mood == "full_moon",
        "events_in_image": False,
        "prompt_hint": (
            f"Sacred Ground nighttime storefront. Base style: {base} "
            f"Season={season}: {look}. Sky mood={mood} ({mood_look}). "
            "Do not invent a different building. Do not paint the event schedule onto the image."
        ),
    }
