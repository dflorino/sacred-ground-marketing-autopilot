"""Day/night atmosphere plan for Sacred Ground social images.

Morning (today): specialty library only — no seasons.
Night (week_ahead): priority celestial > full_moon > holiday > creative_pool
rotation (night-sky creatives first; current-season storefront at most sparsely).
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


def celestial_for(day: date) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Return (celestial_id, meta) if publish night is a celestial night-before.

    Source of truth: ``config/celestial_events.json`` via ``marketing.celestial``.
    Optional mirror under ``nighttime.celestial_events`` is ignored when the
    dedicated config file has the event.
    """
    from . import celestial as cel_mod

    hit = cel_mod.celestial_night_for(day)
    if hit:
        return hit
    # Legacy / optional mirror in image_atmosphere.json
    events = ((atmosphere_config().get("nighttime") or {}).get("celestial_events") or {})
    for cid, meta in sorted(events.items(), key=lambda kv: str(kv[0])):
        if not isinstance(meta, dict) or meta.get("active") is False:
            continue
        post_raw = meta.get("post_date") or meta.get("post_night_before")
        if post_raw:
            try:
                if datetime.strptime(str(post_raw), "%Y-%m-%d").date() == day:
                    return str(cid), meta
            except ValueError:
                pass
        raw = meta.get("event_date")
        if raw:
            try:
                event_day = datetime.strptime(str(raw), "%Y-%m-%d").date()
            except ValueError:
                event_day = None
            if event_day is not None and day == event_day - timedelta(days=1):
                return str(cid), meta
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


def _is_daytime_sun_plate(plate: Dict[str, Any]) -> bool:
    """Founder 2026-08-09: sun-dominant / daytime-sun plates are not night creatives."""
    if plate.get("daytime_sun") is True:
        return True
    mood = str(plate.get("night_mood") or "").strip().lower()
    if mood in ("daytime_sun", "sun", "daytime"):
        return True
    family = str(plate.get("family") or "").strip().lower()
    return family in ("daytime_sun", "sun_sky")


def _is_night_pool_eligible(plate: Dict[str, Any]) -> bool:
    """Active + SG identity pass + not a retired daytime-sun plate."""
    return (
        bool(plate.get("url"))
        and _has_sg_identity(plate)
        and not _is_daytime_sun_plate(plate)
    )


def _night_never_reuse() -> bool:
    """Founder FINAL 2026-08-12: permanent URL never-reuse (default True)."""
    night = atmosphere_config().get("nighttime") or {}
    if "never_reuse" in night:
        return bool(night.get("never_reuse"))
    try:
        from .images import never_reuse_urls

        return never_reuse_urls()
    except Exception:
        return True


def _night_no_repeat_days() -> Optional[int]:
    """Legacy family soft-cooldown window; None / <=0 means lifetime URL block."""
    night = atmosphere_config().get("nighttime") or {}
    if _night_never_reuse():
        return None
    raw = night.get("no_repeat_days")
    if raw is None:
        return None
    try:
        days = int(raw)
    except (TypeError, ValueError):
        return None
    return days if days > 0 else None


def _recent_week_ahead_usage(
    day: date, within_days: Optional[int] = None
) -> Tuple[set[str], set[str]]:
    """Return (urls, families) used by week_ahead.

    within_days None → lifetime (all prior week_ahead history before today).
    Positive within_days → rolling window [day-(n-1), day).
    """
    try:
        from .images import load_image_usage
    except Exception:
        return set(), set()
    urls: set[str] = set()
    families: set[str] = set()
    history = load_image_usage().get("history") or []
    # Map URL → family from config so history rows (url-only) still block families.
    url_family: Dict[str, str] = {}
    night = atmosphere_config().get("nighttime") or {}
    for bucket in (
        night.get("creative_pool") or [],
        night.get("creative_pool_retired_daytime_sun") or [],
        night.get("creative_pool_needs_sg_identity") or [],
    ):
        for p in bucket:
            u = str(p.get("url") or "")
            fam = str(p.get("family") or "").strip().lower()
            if u and fam:
                url_family[u] = fam
    lifetime = within_days is None or int(within_days) <= 0
    cutoff = None if lifetime else day - timedelta(days=int(within_days) - 1)
    for h in history:
        if h.get("campaign") != "week_ahead" or not h.get("url"):
            continue
        try:
            d = date.fromisoformat(str(h.get("date")))
        except ValueError:
            continue
        if lifetime:
            if d >= day:
                continue
        elif not (cutoff <= d < day):
            continue
        url = str(h["url"])
        urls.add(url)
        fam = url_family.get(url) or str(h.get("family") or "").strip().lower()
        if fam:
            families.add(fam)
    return urls, families


def _eligible_creative_pool(day: date) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Return (creatives, in-season storefronts) for the night pool."""
    night = atmosphere_config().get("nighttime") or {}
    season = season_for(day)
    creatives: List[Dict[str, Any]] = []
    storefronts: List[Dict[str, Any]] = []
    for p in night.get("creative_pool") or []:
        if not _is_night_pool_eligible(p):
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


def _filter_cooldown(
    plates: Sequence[Dict[str, Any]],
    *,
    excluded: set[str],
    recent_urls: set[str],
    recent_families: set[str],
    hard_block_urls: set[str],
) -> List[Dict[str, Any]]:
    """Prefer plates not used recently; never ship hard-blocked / excluded URLs."""
    out: List[Dict[str, Any]] = []
    for p in plates:
        url = str(p.get("url") or "")
        if not url or url in excluded or url in hard_block_urls:
            continue
        fam = str(p.get("family") or "").strip().lower()
        if url in recent_urls:
            continue
        if fam and fam in recent_families:
            continue
        out.append(p)
    return out


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

    exclude_urls: lifetime never-reuse set from image_usage (cross-campaign) plus
    any same-slot claims. Never silently fall back to a used URL (Founder
    2026-08-12 FINAL). Returns {} when no unused plate remains.
    """
    excluded = {str(u) for u in (exclude_urls or []) if u}
    creatives, storefronts = _eligible_creative_pool(day)
    no_repeat = _night_no_repeat_days()
    recent_urls, recent_families = _recent_week_ahead_usage(day, no_repeat)
    # Hard block: every URL already used (lifetime via exclude_urls) + prior
    # week_ahead history when never_reuse is on.
    prior_urls, _ = _recent_week_ahead_usage(day, within_days=no_repeat)
    hard_block = set(prior_urls) | set(excluded)

    creatives_fresh = _filter_cooldown(
        creatives,
        excluded=excluded,
        recent_urls=recent_urls,
        recent_families=recent_families,
        hard_block_urls=hard_block,
    )
    storefronts_fresh = _filter_cooldown(
        storefronts,
        excluded=excluded,
        recent_urls=recent_urls,
        recent_families=recent_families,
        hard_block_urls=hard_block,
    )
    # Soft fallback: ignore family soft-cooldown only — still hard-block used URLs.
    creatives_avail = creatives_fresh or [
        p
        for p in creatives
        if str(p.get("url") or "") not in hard_block
    ]
    storefronts_avail = storefronts_fresh or [
        p
        for p in storefronts
        if str(p.get("url") or "") not in hard_block
    ]

    if not creatives_avail and storefronts_avail:
        return _rotate_pool(storefronts_avail, day, platform)
    if not creatives_avail and not storefronts_avail:
        # Nothing unique left — fail closed (never silently reuse).
        return {}

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

    # Priority 1: celestial night-before (config/celestial_events.json)
    from . import celestial as cel_mod

    cel_plan = cel_mod.night_plan(day, platform=platform, exclude_urls=list(excluded))
    if cel_plan:
        return {
            "campaign": "week_ahead",
            "mode": "celestial",
            "season": season,
            "holiday": None,
            "celestial": cel_plan["id"],
            "full_moon": False,
            "image_url": cel_plan["image_url"],
            "season_look": cel_plan.get("look") or cel_plan.get("label"),
            "cart": "",
            "caption_opener": cel_plan.get("caption_opener") or "",
            "prompt_hint": (
                f"Sacred Ground nighttime CELESTIAL={cel_plan['id']}. Base: {base} "
                f"Look: {cel_plan.get('look')}. Events stay in caption."
            ),
        }
    # Legacy atmosphere mirror (urls on celestial_events block)
    cel = celestial_for(day)
    if cel:
        cid, c_meta = cel
        night_block = c_meta.get("night") if isinstance(c_meta.get("night"), dict) else {}
        urls = [str(u) for u in (night_block.get("urls") or c_meta.get("urls") or []) if u]
        primary = str(night_block.get("url") or c_meta.get("url") or "")
        if primary and primary not in urls:
            urls.insert(0, primary)
        available = [u for u in urls if u not in excluded]
        if available:
            url = available[
                (day.toordinal() + platform_salt(platform)) % len(available)
            ]
            label = str(c_meta.get("label") or cid)
            return {
                "campaign": "week_ahead",
                "mode": "celestial",
                "season": season,
                "holiday": None,
                "celestial": cid,
                "full_moon": False,
                "image_url": url,
                "season_look": str(
                    night_block.get("look") or c_meta.get("look") or label
                ),
                "cart": "",
                "caption_opener": str(c_meta.get("caption_tomorrow") or ""),
                "prompt_hint": (
                    f"Sacred Ground nighttime CELESTIAL={cid}. Base: {base} "
                    f"Look: {night_block.get('look') or label}. Events stay in caption."
                ),
            }

    # Priority 2: full moon only (single plate — if other platform took it, diversify)
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

    # Priority 3: holiday (may rotate multiple holiday plates)
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

    # Priority 4: creative night skies (storefront only sparse / streak-safe)
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
