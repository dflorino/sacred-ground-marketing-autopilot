from __future__ import annotations

from typing import List, Optional

from .models import Event, ImagePlan
from .paths import settings


STORE_EXTERIOR_DEFAULT = (
    "https://shopsacredground.com/wp-content/uploads/Screenshot-2026-03-05-at-9.20.15-AM.png"
)
STORE_INTERIOR_DEFAULT = (
    "https://shopsacredground.com/wp-content/uploads/CD3C3C2E-620B-4933-BC24-11ED63552132-1.png"
)
# Back-compat alias — store fallback posts always use exterior.
STORE_IMAGE_DEFAULT = STORE_EXTERIOR_DEFAULT


def store_exterior_url() -> str:
    """Canonical Sacred Ground exterior — always-used shop photo for publish fallbacks."""
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
    """Canonical Sacred Ground interior — kept for in-store creative when needed."""
    cfg = settings()
    brand = cfg.get("brand_images") or {}
    if brand.get("interior_url"):
        return str(brand["interior_url"])
    return STORE_INTERIOR_DEFAULT


def store_image_url() -> str:
    """Publish fallback shop photo — always the exterior."""
    return store_exterior_url()


def plan_image(events: List[Event], campaign: str) -> ImagePlan:
    """
    Image policy for auto-publish:

    today:
      - exactly one event with a featured image → that event photo
      - otherwise (0 events, multi-event, or missing featured) → store exterior
    Never return generate_prompt without a URL — Zernio needs a media URL.
    """
    with_images = [e for e in events if e.image_url]

    if campaign == "today":
        if len(events) == 1 and events[0].image_url:
            e = events[0]
            return ImagePlan(
                source="event_featured",
                url=e.image_url,
                event_id=e.id,
                recommendation=(
                    f"Use featured image for “{e.title}” "
                    "(brand with logo + cream footer before publish when possible)."
                ),
            )
        url = store_image_url()
        if not events:
            return ImagePlan(
                source="store_photo",
                url=url,
                recommendation=(
                    "Empty calendar day — store exterior with visit/brand message "
                    "+ logo + cream footer."
                ),
            )
        if len(with_images) > 1:
            return ImagePlan(
                source="store_photo",
                url=url,
                recommendation=(
                    f"Multi-event day ({len(events)} events, {len(with_images)} photos) — "
                    "use store exterior so the post stays one clear brand image; "
                    "list all events in the caption."
                ),
            )
        return ImagePlan(
            source="store_photo",
            url=url,
            recommendation=(
                "No usable single featured image — store exterior fallback "
                "+ logo + cream footer."
            ),
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
        return ImagePlan(
            source="store_photo",
            url=store_image_url(),
            recommendation=(
                "Use Sacred Ground store exterior with readable next-7-days "
                "overlay + darker translucent logo."
            ),
        )

    if campaign == "visit":
        return ImagePlan(
            source="store_photo",
            url=store_image_url(),
            recommendation="Visit/brand day — store exterior + logo + cream footer.",
        )

    # spotlight
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
