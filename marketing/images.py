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
) -> None:
    data = load_image_usage()
    history = [
        h
        for h in (data.get("history") or [])
        if not (h.get("date") == day.isoformat() and h.get("campaign") == campaign)
    ]
    history.append(
        {
            "date": day.isoformat(),
            "url": url,
            "rule": rule,
            "campaign": campaign,
        }
    )
    cutoff = (day - timedelta(days=30)).isoformat()
    history = [h for h in history if (h.get("date") or "") >= cutoff]
    data["history"] = sorted(history, key=lambda h: h.get("date") or "")
    save_image_usage(data)


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


def used_yesterday(url: str, day: date) -> bool:
    y = (day - timedelta(days=1)).isoformat()
    for h in load_image_usage().get("history") or []:
        if h.get("date") == y and h.get("url") == url:
            return True
    return False


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


def _pick_from_urls(
    urls: Sequence[str],
    *,
    day: date,
    blocked: set[str],
) -> Optional[str]:
    available = [u for u in urls if u not in blocked]
    if not available:
        # All recently used — pick least-recently among pool by falling back to rotation
        available = list(urls)
    if not available:
        return None
    idx = day.toordinal() % len(available)
    return available[idx]


def select_today_image(
    events: Sequence[Event],
    day: date,
) -> Tuple[str, str, str]:
    """Return (url, rule_id, recommendation). Does not record usage."""
    cfg = image_rules()
    rules = cfg.get("rules") or {}
    priority = list(cfg.get("priority") or [])
    no_repeat = int(cfg.get("no_repeat_days") or 7)
    blocked = urls_used_before_day(day, no_repeat)
    haystack = _event_haystack(events)

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

        url = _pick_from_urls(pool, day=day, blocked=blocked)
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
        return (
            str(e.image_url),
            "event_featured",
            f"Use featured image for “{e.title}”.",
        )

    return (
        store_exterior_url(),
        "store_exterior",
        "Store exterior fallback (empty day or no matching rule).",
    )


def plan_image(
    events: List[Event],
    campaign: str,
    day: Optional[date] = None,
) -> ImagePlan:
    """
    today: specialty rules + multi-event rotation + 7-day no-repeat,
    then single event featured, then store exterior.
    """
    with_images = [e for e in events if e.image_url]

    if campaign == "today":
        from .ingest import today_local

        on = day or today_local()
        url, rule_id, rec = select_today_image(events, on)
        source = {
            "event_featured": "event_featured",
            "store_exterior": "store_photo",
            "multi_event_rotation": "rotation",
        }.get(rule_id, "rule_library")
        return ImagePlan(
            source=source,
            url=url,
            event_id=events[0].id if len(events) == 1 else None,
            recommendation=rec,
            rule=rule_id,
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
        # Locked: rotate founder exterior storefront photos only.
        # Never interior, never AI specialty / night-sky creatives.
        from .ingest import today_local

        on = day or today_local()
        wa = (settings().get("campaigns") or {}).get("week_ahead") or {}
        brand = settings().get("brand_images") or {}
        urls = [str(u) for u in (wa.get("image_urls") or []) if u]
        if not urls:
            urls = [str(u) for u in (brand.get("exterior_urls") or []) if u]
        if not urls:
            urls = [store_exterior_url()]
        url = urls[on.toordinal() % len(urls)]
        return ImagePlan(
            source="brand_week_ahead",
            url=url,
            recommendation=(
                "Founder exterior storefront rotation — events stay in caption only."
            ),
            rule="week_ahead_founder_exterior",
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
        no_repeat = int(image_rules().get("no_repeat_days") or 7)
        blocked = urls_used_before_day(on, no_repeat)
        url = _pick_from_urls(pool, day=on, blocked=blocked) or pool[0]
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
