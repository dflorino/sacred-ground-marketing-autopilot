"""Day/night atmosphere plan for Sacred Ground social images.

Morning (today): specialty library only — no seasons.
Night (week_ahead): priority full_moon > holiday > creative_pool rotation
(night-sky creatives first; current-season storefront at most sparsely).
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

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


def _has_sg_identity(plate: Dict[str, Any]) -> bool:
    """Night creatives must carry Sacred Ground in the photo (not overlays alone)."""
    if plate.get("active") is False:
        return False
    identity = str(plate.get("sg_identity") or "pass").strip().lower()
    return identity in ("pass", "ok", "yes", "true", "1")


def _eligible_creative_pool(day: date) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Return (creatives, in-season storefronts) for the night pool."""
    night = atmosphere_config().get("nighttime") or {}
    season = season_for(day)
    creatives: List[Dict[str, Any]] = []
    storefronts: List[Dict[str, Any]] = []
    for p in night.get("creative_pool") or []:
        if not p.get("url"):
            continue
        if not _has_sg_identity(p):
            continue
        if p.get("kind") == "storefront":
            p_season = str(p.get("season") or "")
            if p_season and p_season != season:
                continue
            storefronts.append(p)
        else:
            creatives.append(p)

    # Ensure current-season plate is available even if omitted from creative_pool.
    s_meta = season_meta(day)
    season_url = str(s_meta.get("url") or "")
    if season_url and not any(str(p.get("url")) == season_url for p in storefronts):
        storefronts.append(
            {
                "id": f"season_{season}_storefront",
                "label": f"{season.title()} storefront",
                "url": season_url,
                "kind": "storefront",
                "season": season,
            }
        )
    return creatives, storefronts


def _is_storefront_usage(hit: Dict[str, Any]) -> bool:
    rule = str(hit.get("rule") or "")
    url = str(hit.get("url") or "")
    return "storefront" in rule or (
        "sg-night-" in url
        and "creative" not in url
        and any(s in url for s in ("spring", "summer", "fall", "winter"))
    )


def _recent_storefront_streak(day: date, lookback: int = 3) -> int:
    """How many consecutive prior nights used a storefront plate (0 if unknown)."""
    try:
        from .images import load_image_usage
    except Exception:
        return 0
    history = load_image_usage().get("history") or []
    by_date: Dict[str, List[Dict[str, Any]]] = {}
    for h in history:
        if h.get("campaign") == "week_ahead" and h.get("url"):
            by_date.setdefault(str(h.get("date")), []).append(h)
    streak = 0
    for i in range(1, lookback + 1):
        prev = (day - timedelta(days=i)).isoformat()
        hits = by_date.get(prev) or []
        if not hits:
            break
        # A night counts as storefront if either platform used a storefront plate.
        if any(_is_storefront_usage(h) for h in hits):
            streak += 1
        else:
            break
    return streak


def _rotate_pool(
    items: Sequence[Dict[str, Any]],
    day: date,
    platform: Optional[str] = None,
) -> Dict[str, Any]:
    if not items:
        return {}
    from .images import platform_salt

    idx = (day.toordinal() + platform_salt(platform)) % len(items)
    return items[idx]


def _pick_night_creative(
    day: date,
    platform: Optional[str] = None,
    exclude_urls: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """
    Rotate creative night plates by default.

    In-season storefronts may appear at most every 5th creative-mode night,
    and never after a recent storefront streak — so creatives cannot get stuck
    behind founder exterior / season storefront photos.

    exclude_urls: URLs already claimed by the other platform tonight.
    """
    excluded = {str(u) for u in (exclude_urls or []) if u}
    creatives, storefronts = _eligible_creative_pool(day)
    creatives_avail = [p for p in creatives if str(p.get("url") or "") not in excluded]
    storefronts_avail = [
        p for p in storefronts if str(p.get("url") or "") not in excluded
    ]

    if not creatives_avail and storefronts_avail:
        return _rotate_pool(storefronts_avail, day, platform)
    if not creatives_avail and not storefronts_avail:
        # Nothing unique left — fall back to full pools (may duplicate).
        if not creatives and storefronts:
            return _rotate_pool(storefronts, day, platform)
        if not creatives:
            return {}
        creatives_avail = list(creatives)
        storefronts_avail = list(storefronts)

    # Storefront slot: every 5th night only, and only if no recent streak.
    allow_storefront = (
        bool(storefronts_avail)
        and (day.toordinal() % 5 == 0)
        and _recent_storefront_streak(day, lookback=3) == 0
    )
    if allow_storefront:
        return _rotate_pool(storefronts_avail, day, platform)

    # Stable day + platform rotation across creatives (not storefronts).
    return _rotate_pool(creatives_avail, day, platform)


def nighttime_plan(
    day: date,
    platform: Optional[str] = None,
    exclude_urls: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    night = atmosphere_config().get("nighttime") or {}
    base = night.get("base_style") or "Sacred Ground exterior storefront"
    season = season_for(day)
    s_meta = season_meta(day)
    excluded = {str(u) for u in (exclude_urls or []) if u}
    from .images import platform_salt

    # Priority 1: full moon only (single plate — if other platform took it, diversify)
    full_cfg = night.get("full_moon") or {}
    if full_cfg.get("enabled", True) and is_full_moon(day):
        url = str(full_cfg.get("url") or "")
        if url and url not in excluded:
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
        # Fall through to holiday/creative so FB ≠ IG when possible.

    # Priority 2: holiday (may rotate multiple holiday plates)
    hit = holiday_for(day)
    if hit:
        hid, h_meta = hit
        urls = [str(u) for u in (h_meta.get("urls") or []) if u]
        primary = str(h_meta.get("url") or "")
        if primary and primary not in urls:
            urls.insert(0, primary)
        available = [u for u in urls if u not in excluded]
        if available:
            url = available[
                (day.toordinal() + platform_salt(platform)) % len(available)
            ]
            return {
                "campaign": "week_ahead",
                "mode": "holiday",
                "season": season,
                "holiday": hid,
                "full_moon": False,
                "image_url": url,
                "season_look": str(h_meta.get("look") or hid),
                "cart": str(h_meta.get("cart") or ""),
                "prompt_hint": (
                    f"Sacred Ground nighttime HOLIDAY={hid}. Base: {base} "
                    f"Outdoors: {h_meta.get('look')}. Cart: {h_meta.get('cart')}. "
                    "Events stay in caption."
                ),
            }
        # Single holiday plate already used by the other platform — diversify via creatives.

    # Priority 3: creative night skies (storefront only sparse / streak-safe)
    pick = _pick_night_creative(day, platform=platform, exclude_urls=list(excluded))
    if pick:
        kind = str(pick.get("kind") or "creative")
        label = str(pick.get("label") or pick.get("id") or "creative")
        return {
            "campaign": "week_ahead",
            "mode": "creative",
            "season": season,
            "holiday": None,
            "full_moon": False,
            "creative_id": str(pick.get("id") or ""),
            "image_url": str(pick.get("url") or ""),
            "season_look": label,
            "cart": str(s_meta.get("cart") or "") if kind == "storefront" else "",
            "atmosphere": str(s_meta.get("lighting") or ""),
            "prompt_hint": (
                f"Sacred Ground nighttime creative plate ({label}). "
                f"Base note: {base} Events stay in caption."
            ),
        }

    # Fallback: season storefront if creative pool empty
    season_url = str(s_meta.get("url") or "")
    if season_url and season_url in excluded:
        season_url = ""
    return {
        "campaign": "week_ahead",
        "mode": "season",
        "season": season,
        "holiday": None,
        "full_moon": False,
        "image_url": season_url,
        "season_look": str(s_meta.get("look") or season),
        "cart": str(s_meta.get("cart") or ""),
        "atmosphere": str(s_meta.get("lighting") or ""),
        "prompt_hint": (
            f"Sacred Ground nighttime storefront. Base: {base} "
            f"Season={season}: {s_meta.get('look')}. Lighting: {s_meta.get('lighting')}. "
            f"Cart: {s_meta.get('cart')}. Events stay in caption."
        ),
    }


def night_image_url(
    day: date,
    platform: Optional[str] = None,
    exclude_urls: Optional[Sequence[str]] = None,
) -> Optional[str]:
    plan = nighttime_plan(day, platform=platform, exclude_urls=exclude_urls)
    url = plan.get("image_url")
    return str(url) if url else None
