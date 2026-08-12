from __future__ import annotations

import os
from datetime import date, timedelta
from functools import lru_cache
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .models import Event, ImagePlan
from .paths import CONFIG_DIR, STATE_DIR, ensure_dirs, read_json, settings, write_json

STORE_EXTERIOR_DEFAULT = (
    "https://shopsacredground.com/wp-content/uploads/Screenshot-2026-03-05-at-9.20.15-AM.png"
)
STORE_INTERIOR_DEFAULT = (
    "https://shopsacredground.com/wp-content/uploads/CD3C3C2E-620B-4933-BC24-11ED63552132-1.png"
)
STORE_IMAGE_DEFAULT = STORE_EXTERIOR_DEFAULT

IMAGE_USAGE_PATH = os.path.join(STATE_DIR, "image_usage.json")
WEEKDAY_INDEX = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

# Founder FINAL 2026-08-12 ~5:54pm CT — never silently reuse a posted URL.
REUSE_BLOCKED_MSG = (
    "NEVER-REUSE: every candidate media URL was already posted or used in a "
    "published draft. Regenerate a new plate, pick an unused alternate, or skip "
    "— do not ship a repeat. Same-slot FB+IG single-image mode (one URL to both "
    "platforms in one publish) is OK; cross-campaign / cross-day reuse is not."
)


def store_exterior_url() -> str:
    """Canonical Sacred Ground exterior — empty-day / last-resort fallback."""
    cfg = settings()
    brand = cfg.get("brand_images") or {}
    if brand.get("exterior_url"):
        return str(brand["exterior_url"])
    today = (cfg.get("campaigns") or {}).get("today") or {}
    if today.get("default_image_url"):
        return str(today["default_image_url"])
    wa = (cfg.get("campaigns") or {}).get("week_ahead") or {}
    if wa.get("store_image_url"):
        return str(wa["store_image_url"])
    return STORE_EXTERIOR_DEFAULT


def store_interior_url() -> str:
    cfg = settings()
    brand = cfg.get("brand_images") or {}
    if brand.get("interior_url"):
        return str(brand["interior_url"])
    return STORE_INTERIOR_DEFAULT


def store_image_url() -> str:
    return store_exterior_url()


@lru_cache(maxsize=1)
def image_rules() -> Dict[str, Any]:
    path = os.path.join(CONFIG_DIR, "image_rules.json")
    with open(path, encoding="utf-8") as fh:
        import json

        return json.load(fh)


@lru_cache(maxsize=1)
def morning_flyers() -> Dict[str, Any]:
    from . import morning_flyers as mf

    data = mf.load_flyers_config()
    if not isinstance(data, dict):
        return {"flyers": {}, "prebranded_default": True}
    data.setdefault("flyers", {})
    data.setdefault("prebranded_default", True)
    return data


def skip_brand_overlays(image: Any) -> bool:
    """
    True when the plate is a finished flyer (logo + footer + event text baked in).
    Accepts ImagePlan, dict, or any object with a prebranded attribute/key.
    """
    if image is None:
        return False
    if isinstance(image, dict):
        if image.get("prebranded") is True:
            return True
        rule = str(image.get("rule") or "")
        url = str(image.get("url") or "")
        return rule == "morning_flyer" or "sg-morning-flyer-" in url
    if getattr(image, "prebranded", False):
        return True
    rule = str(getattr(image, "rule", "") or "")
    url = str(getattr(image, "url", "") or "")
    return rule == "morning_flyer" or "sg-morning-flyer-" in url


def _flyer_for_day(day: date) -> Optional[Dict[str, Any]]:
    flyers = morning_flyers().get("flyers") or {}
    entry = flyers.get(day.isoformat())
    return entry if isinstance(entry, dict) else None


def load_image_usage() -> Dict[str, Any]:
    ensure_dirs()
    data = read_json(IMAGE_USAGE_PATH, {"history": []})
    if not isinstance(data, dict):
        return {"history": []}
    data.setdefault("history", [])
    return data


def save_image_usage(data: Dict[str, Any]) -> None:
    ensure_dirs()
    write_json(IMAGE_USAGE_PATH, data)


def record_image_use(
    *,
    day: date,
    url: str,
    rule: str,
    campaign: str = "today",
    platform: str = "",
) -> None:
    """Record a used URL. When platform is set, FB/IG can each keep a row for the same day."""
    data = load_image_usage()
    plat = str(platform or "")
    history = []
    for h in data.get("history") or []:
        same_day_camp = (
            h.get("date") == day.isoformat() and h.get("campaign") == campaign
        )
        if not same_day_camp:
            history.append(h)
            continue
        # Platform-scoped replace: empty platform clears all rows for that day/campaign
        # (legacy / shared-pool campaigns like tuesday_meditation).
        if not plat:
            continue
        if str(h.get("platform") or "") == plat:
            continue
        history.append(h)
    entry: Dict[str, Any] = {
        "date": day.isoformat(),
        "url": url,
        "rule": rule,
        "campaign": campaign,
    }
    if plat:
        entry["platform"] = plat
    history.append(entry)
    # Lifetime ledger (Founder 2026-08-12 FINAL): never truncate — permanent never-reuse.
    data["history"] = sorted(
        history,
        key=lambda h: (h.get("date") or "", h.get("platform") or "", h.get("url") or ""),
    )
    save_image_usage(data)


def never_reuse_urls() -> bool:
    """
    Founder FINAL 2026-08-12 ~5:54pm CT: permanent never-reuse of any media URL
    already posted / used in a published draft. Default True.

    Config: image_rules.never_reuse (bool). Legacy: no_repeat_days null/<=0 → lifetime;
    positive no_repeat_days only applies when never_reuse is explicitly false.
    """
    cfg = image_rules()
    if "never_reuse" in cfg:
        return bool(cfg.get("never_reuse"))
    raw = cfg.get("no_repeat_days")
    if raw is None:
        return True
    try:
        return int(raw) <= 0
    except (TypeError, ValueError):
        return True


def urls_ever_used() -> set[str]:
    """Every media URL ever recorded in image_usage history (all campaigns)."""
    used: set[str] = set()
    for h in load_image_usage().get("history") or []:
        if h.get("url"):
            used.add(str(h["url"]))
    return used


def urls_used_before_day(day: date, within_days: int) -> set[str]:
    """URLs used in the window [day-(within_days-1), day) — excludes today."""
    cutoff = day - timedelta(days=within_days - 1)
    used: set[str] = set()
    for h in load_image_usage().get("history") or []:
        try:
            d = date.fromisoformat(str(h.get("date")))
        except ValueError:
            continue
        if cutoff <= d < day and h.get("url"):
            used.add(str(h["url"]))
    return used


def urls_used_recently(day: date, within_days: int) -> set[str]:
    """
    URLs used in [day-(within_days-1), day] inclusive — all campaigns.

    Prefer urls_ever_used() / cooldown_blocked_urls() under never_reuse (default).
    Legacy windowed helper kept for tests and explicit within_days callers.
    """
    if within_days <= 0:
        return urls_ever_used()
    cutoff = day - timedelta(days=max(1, int(within_days)) - 1)
    used: set[str] = set()
    for h in load_image_usage().get("history") or []:
        try:
            d = date.fromisoformat(str(h.get("date")))
        except ValueError:
            continue
        if cutoff <= d <= day and h.get("url"):
            used.add(str(h["url"]))
    return used


def urls_used_on_day(day: date, *, exclude_campaign: str = "") -> set[str]:
    """URLs already claimed today by any campaign (optionally skip one campaign)."""
    used: set[str] = set()
    key = day.isoformat()
    skip = str(exclude_campaign or "")
    for h in load_image_usage().get("history") or []:
        if h.get("date") != key or not h.get("url"):
            continue
        if skip and str(h.get("campaign") or "") == skip:
            continue
        used.add(str(h["url"]))
    return used


def used_yesterday(url: str, day: date) -> bool:
    y = (day - timedelta(days=1)).isoformat()
    for h in load_image_usage().get("history") or []:
        if h.get("date") == y and h.get("url") == url:
            return True
    return False


def cooldown_blocked_urls(
    day: date,
    *,
    within_days: Optional[int] = None,
    exclude_campaign: str = "",
    extra_exclude: Optional[Sequence[str]] = None,
) -> set[str]:
    """
    URLs that must not be selected.

    Default (never_reuse): lifetime block of every URL in image_usage history.
    Optional within_days>0: legacy rolling window (only when never_reuse is false
    or caller passes an explicit positive window).

    exclude_campaign: drop this campaign's *same-day* rows so a slot can re-plan
    itself (idempotent). That is not cross-slot reuse — FB+IG single-image mode
    still records one shared URL for the pair.
    """
    if within_days is None:
        if never_reuse_urls():
            blocked = urls_ever_used()
        else:
            try:
                days = int(image_rules().get("no_repeat_days") or 7)
            except (TypeError, ValueError):
                days = 7
            blocked = urls_used_recently(day, days) if days > 0 else urls_ever_used()
    elif int(within_days) <= 0:
        blocked = urls_ever_used()
    else:
        blocked = urls_used_recently(day, int(within_days))
    # Allow a campaign to re-plan its own same-day slot without blocking itself.
    if exclude_campaign:
        own = {
            str(h["url"])
            for h in load_image_usage().get("history") or []
            if h.get("date") == day.isoformat()
            and str(h.get("campaign") or "") == exclude_campaign
            and h.get("url")
        }
        blocked -= own
    for u in extra_exclude or []:
        if u:
            blocked.add(str(u))
    return blocked


def reuse_blocked_plan(campaign: str) -> ImagePlan:
    """Clear failure plan when no unused media URL remains."""
    return ImagePlan(
        source="reuse_blocked",
        url=None,
        recommendation=f"{REUSE_BLOCKED_MSG} (campaign={campaign})",
        rule="reuse_blocked",
        prebranded=False,
    )


def _event_haystack(events: Sequence[Event]) -> str:
    bits: List[str] = []
    for e in events:
        bits.append(e.title or "")
        bits.extend(e.categories or [])
        bits.extend(e.tags or [])
    return " ".join(bits).lower()


def _nth_weekday_of_month(day: date, weekday_name: str, nth: int) -> bool:
    want = WEEKDAY_INDEX[weekday_name.lower()]
    if day.weekday() != want:
        return False
    return ((day.day - 1) // 7) + 1 == nth


def _rule_matches(
    rule: Dict[str, Any],
    *,
    events: Sequence[Event],
    day: date,
    haystack: str,
) -> bool:
    if rule.get("require_weekday"):
        if day.weekday() != WEEKDAY_INDEX[str(rule["require_weekday"]).lower()]:
            return False

    nth = rule.get("require_nth_weekday")
    if nth:
        if not _nth_weekday_of_month(day, str(nth["weekday"]), int(nth["nth"])):
            return False

    min_events = rule.get("min_events")
    if min_events is not None and len(events) < int(min_events):
        return False

    excludes = [x.lower() for x in (rule.get("exclude_if_match_any") or [])]
    if excludes and any(x in haystack for x in excludes):
        return False

    needles = [x.lower() for x in (rule.get("match_any") or [])]
    if needles:
        return any(n in haystack for n in needles)

    # No keyword needles: weekday-only or multi-event-only rules
    if rule.get("require_weekday") or min_events is not None or nth:
        return True
    return False


def platform_salt(platform: Optional[str]) -> int:
    """Deterministic offset so FB vs IG land on different pool indices."""
    if not platform:
        return 0
    key = str(platform).lower().strip()
    if key in ("facebook", "fb"):
        return 0
    if key in ("instagram", "ig"):
        return 1
    return sum(ord(c) for c in key) % 97


def _pick_from_urls(
    urls: Sequence[str],
    *,
    day: date,
    blocked: set[str],
    platform: Optional[str] = None,
    exclude: Optional[Sequence[str]] = None,
    prefer_unique: bool = False,
) -> Optional[str]:
    """
    Day-ordinal + platform-salt rotation over an eligible pool.

    When prefer_unique is True and every pool URL is excluded, return None so the
    caller can try another specialty / general pool instead of duplicating.
    """
    excluded = {str(u) for u in (exclude or []) if u}
    available = [u for u in urls if u not in blocked and u not in excluded]
    if not available:
        # All recently used — rotate among non-excluded pool members
        available = [u for u in urls if u not in excluded]
    if not available:
        if prefer_unique:
            return None
        available = list(urls)
    if not available:
        return None
    idx = (day.toordinal() + platform_salt(platform)) % len(available)
    return available[idx]


def select_today_image(
    events: Sequence[Event],
    day: date,
    platform: Optional[str] = None,
    exclude_urls: Optional[Sequence[str]] = None,
    *,
    campaign: str = "today",
    allow_morning_plates: bool = True,
) -> Tuple[str, str, str]:
    """Return (url, rule_id, recommendation). Does not record usage.

    Empty url + rule_id ``reuse_blocked`` when every candidate was already used
    (Founder never-reuse — never silently ship a repeat).
    """
    cfg = image_rules()
    rules = cfg.get("rules") or {}
    priority = list(cfg.get("priority") or [])
    excluded = [str(u) for u in (exclude_urls or []) if u]
    blocked = cooldown_blocked_urls(
        day,
        exclude_campaign=campaign,
        extra_exclude=excluded,
    )
    haystack = _event_haystack(events)
    # When the other platform already claimed a URL, skip single-URL specialties
    # that cannot diversify and fall through to the next eligible rule/pool.
    prefer_unique = bool(excluded)

    # Celestial morning-of plate beats generic morning flyers (Founder 2026-08-10).
    # Afternoon spotlight must never take these — different time-of-day slot.
    if allow_morning_plates:
        from . import celestial as cel_mod

        cel_m = cel_mod.morning_plan(day, platform=platform, exclude_urls=list(blocked))
        if cel_m and cel_m.get("image_url"):
            cel_url = str(cel_m["image_url"])
            if cel_url not in blocked:
                label = cel_m.get("label") or cel_m.get("id") or day.isoformat()
                return (
                    cel_url,
                    "celestial_morning",
                    (
                        f"Celestial morning plate for {day.isoformat()} ({label}) — "
                        "today’s celestial moment; shop events stay in caption."
                    ),
                )

        # Date-keyed finished flyers beat specialty / atmospheric plates.
        # Single-image mode (Founder Aug 10 2026): primary `url` for FB+IG.
        flyer = _flyer_for_day(day)
        if flyer:
            from . import morning_flyers as mf

            chosen, shared = mf.select_flyer_url_for_platform(flyer, platform)
            if chosen and str(chosen) not in blocked:
                label = flyer.get("label") or day.isoformat()
                if shared:
                    rec = (
                        f"Prebranded morning flyer for {day.isoformat()} ({label}) — "
                        "single-image mode (same plate on FB+IG). Skip overlays."
                    )
                else:
                    plat = (platform or "facebook").lower()
                    rec = (
                        f"Prebranded morning flyer for {day.isoformat()} ({label}) — "
                        f"{plat} variant (allow_ig_variant). Skip overlays."
                    )
                return (chosen, "morning_flyer", rec)

    for rule_id in priority:
        rule = rules.get(rule_id) or {}
        if not _rule_matches(rule, events=events, day=day, haystack=haystack):
            continue

        # Specialty rules may rotate a pool via "urls" (tarot deck, multi-event, etc.).
        pool = [str(u) for u in (rule.get("urls") or []) if u]
        primary = str(rule.get("url") or "")
        if primary and primary not in pool:
            pool.insert(0, primary)
        if not pool:
            continue

        if rule.get("not_consecutive_days"):
            # Skip any pool URL used yesterday (Robert, etc.).
            if any(used_yesterday(u, day) for u in pool):
                continue

        url = _pick_from_urls(
            pool,
            day=day,
            blocked=blocked,
            platform=platform,
            exclude=excluded,
            prefer_unique=prefer_unique,
        )
        if not url:
            continue

        label = rule.get("label") or rule_id
        if rule_id == "multi_event_rotation":
            rec = f"Multi-event day — rotation image ({label})."
        elif len(pool) > 1:
            rec = f"Matched image rule: {label} (rotating pool)."
        else:
            rec = f"Matched image rule: {label}."
        return (url, rule_id, rec)

    if len(events) == 1 and events[0].image_url:
        e = events[0]
        featured = str(e.image_url)
        if featured not in blocked and featured not in excluded:
            return (
                featured,
                "event_featured",
                f"Use featured image for “{e.title}”.",
            )

    # General morning creative pool — empty days / no specialty / no featured.
    # Top-level config key (sibling of "rules"), not inside the specialty map.
    creative = cfg.get("morning_creative") or {}
    cpool = [str(u) for u in (creative.get("urls") or []) if u]
    cprimary = str(creative.get("url") or "")
    if cprimary and cprimary not in cpool:
        cpool.insert(0, cprimary)
    if cpool:
        curl = _pick_from_urls(
            cpool,
            day=day,
            blocked=blocked,
            platform=platform,
            exclude=excluded,
            prefer_unique=prefer_unique,
        )
        if curl:
            return (
                curl,
                "morning_creative",
                "Morning creative rotation (empty day or no specialty match).",
            )

    exterior = store_exterior_url()
    if exterior and exterior not in blocked and exterior not in excluded:
        return (
            exterior,
            "store_exterior",
            "Store exterior fallback (empty day or no matching rule).",
        )

    # Never silently reuse a blocked URL (Founder 2026-08-12 FINAL).
    return ("", "reuse_blocked", REUSE_BLOCKED_MSG)


def plan_image(
    events: List[Event],
    campaign: str,
    day: Optional[date] = None,
    platform: Optional[str] = None,
    exclude_urls: Optional[Sequence[str]] = None,
) -> ImagePlan:
    """
    today: specialty rules + multi-event rotation + lifetime never-reuse,
    then single event featured, then store exterior.

    afternoon_spotlight: NEVER reuse morning plates (celestial / morning_flyer)
    and NEVER reuse any previously posted media URL — including TEC thumbnails /
    Eve flyers / event_featured (Founder 2026-08-12 FINAL). Prefer an unused
    event featured image, then specialty / exterior; fail clearly if none left.

    platform / exclude_urls: legacy diversification hooks. Pipeline plans once
    and uses the same media URL on Facebook and Instagram for one slot
    (Founder Aug 10 2026 single-image mode — that is one post pair, not reuse).
    """
    with_images = [e for e in events if e.image_url]
    excluded = [str(u) for u in (exclude_urls or []) if u]

    if campaign == "afternoon_spotlight":
        from .ingest import today_local

        on = day or today_local()
        blocked = cooldown_blocked_urls(
            on,
            exclude_campaign="afternoon_spotlight",
            extra_exclude=excluded,
        )
        # Hard refuse morning-owned plate families even if usage ledger lagged.
        morning_owned = {
            "celestial_morning",
            "morning_flyer",
            "morning_creative",
        }
        if events and events[0].image_url:
            featured = str(events[0].image_url)
            if featured not in blocked:
                return ImagePlan(
                    source="event_featured",
                    url=featured,
                    event_id=events[0].id,
                    recommendation=(
                        "Afternoon spotlight — unused event featured / TEC "
                        "thumbnail (never a previously posted URL; never the "
                        "morning plate)."
                    ),
                    rule="event_featured",
                    prebranded=False,
                )
        # Specialty / pool path — never celestial / morning flyer plates.
        url, rule_id, rec = select_today_image(
            events,
            on,
            platform=platform,
            exclude_urls=list(blocked),
            campaign="afternoon_spotlight",
            allow_morning_plates=False,
        )
        if rule_id == "reuse_blocked" or not url:
            return reuse_blocked_plan("afternoon_spotlight")
        if rule_id in morning_owned or url in blocked:
            exterior = store_exterior_url()
            if exterior and exterior not in blocked:
                url = exterior
                rule_id = "store_exterior"
                rec = (
                    "Afternoon spotlight — store exterior fallback "
                    "(blocked morning/celestial / used-URL reuse)."
                )
            else:
                return reuse_blocked_plan("afternoon_spotlight")
        source = {
            "event_featured": "event_featured",
            "store_exterior": "store_photo",
            "multi_event_rotation": "rotation",
            "morning_creative": "rotation",
            "reuse_blocked": "reuse_blocked",
        }.get(rule_id, "rule_library")
        return ImagePlan(
            source=source,
            url=url or None,
            event_id=events[0].id if len(events) == 1 else None,
            recommendation=rec,
            rule=rule_id,
            prebranded=False,
        )

    if campaign == "today":
        from .ingest import today_local

        on = day or today_local()
        url, rule_id, rec = select_today_image(
            events, on, platform=platform, exclude_urls=excluded
        )
        if rule_id == "reuse_blocked" or not url:
            return reuse_blocked_plan("today")
        source = {
            "event_featured": "event_featured",
            "store_exterior": "store_photo",
            "multi_event_rotation": "rotation",
            "morning_creative": "rotation",
            "morning_flyer": "morning_flyer",
            "celestial_morning": "celestial_morning",
            "reuse_blocked": "reuse_blocked",
        }.get(rule_id, "rule_library")
        prebranded = rule_id == "morning_flyer" or skip_brand_overlays(
            {"rule": rule_id, "url": url}
        )
        if rule_id == "celestial_morning":
            # Celestial plates bake circular logo bottom-left (Founder Aug 10 2026).
            # Overlays never ran for these URLs — treat as prebranded to avoid a gap.
            prebranded = True
        return ImagePlan(
            source=source,
            url=url,
            event_id=events[0].id if len(events) == 1 else None,
            recommendation=rec,
            rule=rule_id,
            prebranded=prebranded,
        )

    if campaign == "week":
        if with_images:
            return ImagePlan(
                source="collage",
                url=with_images[0].image_url,
                event_id=with_images[0].id,
                recommendation=(
                    f"Weekly collage from {len(with_images)} event image(s); "
                    "warm shop atmosphere, readable titles optional as overlay in design tool."
                ),
            )
        return ImagePlan(
            source="store_photo",
            url=store_image_url(),
            recommendation="No event images this week — store exterior roundup visual.",
        )

    if campaign == "week_ahead":
        # Priority: celestial > full_moon > holiday > creative_pool rotation.
        # Never fall back to the old founder Screenshot exterior trio when the
        # creative night pack is configured — that path caused storefront-only weeks.
        from .atmosphere import nighttime_plan, season_meta
        from .ingest import today_local

        on = day or today_local()
        cross_blocked = cooldown_blocked_urls(
            on,
            exclude_campaign="week_ahead",
            extra_exclude=excluded,
        )
        atm = nighttime_plan(
            on, platform=platform, exclude_urls=list(cross_blocked)
        )
        url = str(atm.get("image_url") or "")
        if url and url in cross_blocked:
            url = ""
        if not url:
            # Last resort: unused season night plate, then unused brand exterior.
            season_url = str(season_meta(on).get("url") or "")
            for candidate in (season_url, store_exterior_url()):
                if candidate and candidate not in cross_blocked:
                    url = candidate
                    break
        if not url:
            return reuse_blocked_plan("week_ahead")

        mode = atm.get("mode") or "creative"
        season = atm.get("season") or "summer"
        holiday = atm.get("holiday")
        creative_id = atm.get("creative_id") or ""
        celestial_id = atm.get("celestial") or ""
        kind = "storefront" if "storefront" in str(creative_id).lower() else "creative"
        if mode == "celestial":
            rule = f"week_ahead_celestial_{celestial_id or 'event'}"
            label = celestial_id or "celestial"
        elif mode == "full_moon":
            rule = "week_ahead_full_moon"
            label = "full_moon"
        elif mode == "holiday":
            rule = f"week_ahead_holiday_{holiday}"
            label = holiday
        elif mode == "creative":
            rule = (
                f"week_ahead_storefront_{creative_id}"
                if kind == "storefront"
                else f"week_ahead_creative_{creative_id or 'pool'}"
            )
            label = creative_id or "creative"
        else:
            rule = f"week_ahead_season_{season}"
            label = season
        return ImagePlan(
            source="brand_week_ahead",
            url=url,
            prompt=str(atm.get("prompt_hint") or ""),
            recommendation=(
                f"Night image ({mode}/{label}): {atm.get('season_look')}. "
                f"Cart: {atm.get('cart') or 'n/a'}. Events stay in caption only. "
                "No post-hoc shop-pride overlay on pool/celestial inventory "
                "(designed-in only when generating NEW night art)."
            ),
            rule=rule,
        )

    if campaign == "visit":
        return ImagePlan(
            source="store_photo",
            url=store_image_url(),
            recommendation="Visit/brand day — store exterior + logo + cream footer.",
        )

    if campaign == "tuesday_meditation":
        from .ingest import today_local

        on = day or today_local()
        camp = (settings().get("campaigns") or {}).get("tuesday_meditation") or {}
        pool = [str(u) for u in (camp.get("image_urls") or []) if u]
        if not pool:
            # Fallback to Today meditation specialty pool + metaphysical journey plate
            med = (image_rules().get("rules") or {}).get("meditation") or {}
            pool = [str(u) for u in (med.get("urls") or []) if u]
            primary = str(med.get("url") or "")
            if primary and primary not in pool:
                pool.insert(0, primary)
            journey = (
                "https://shopsacredground.com/wp-content/uploads/"
                "ai_generated_Metaphysical-spiritual-journey_1763939976.png"
            )
            if journey not in pool:
                pool.append(journey)
        if not pool:
            pool = [store_exterior_url()]
        blocked = cooldown_blocked_urls(
            on,
            exclude_campaign="tuesday_meditation",
            extra_exclude=excluded,
        )
        url = _pick_from_urls(pool, day=on, blocked=blocked)
        if not url:
            return reuse_blocked_plan("tuesday_meditation")
        return ImagePlan(
            source="meditation_pool",
            url=url,
            recommendation="Tuesday meditation post — rotating Om / silhouette / journey / morning meditation pool.",
            rule="tuesday_meditation_pool",
        )

    e = events[0]
    if e.image_url:
        return ImagePlan(
            source="event_featured",
            url=e.image_url,
            event_id=e.id,
            recommendation=f"Promotional crop of “{e.title}” featured image.",
        )
    return ImagePlan(
        source="store_photo",
        url=store_image_url(),
        recommendation=f"No featured image for “{e.title}” — store exterior fallback.",
    )
