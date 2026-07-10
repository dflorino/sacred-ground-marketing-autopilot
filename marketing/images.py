from __future__ import annotations

from typing import List, Optional

from .models import Event, ImagePlan


def plan_image(events: List[Event], campaign: str) -> ImagePlan:
    """Prefer real event images; otherwise a creative generation prompt."""
    with_images = [e for e in events if e.image_url]
    if campaign == "today":
        if len(with_images) == 1:
            e = with_images[0]
            return ImagePlan(
                source="event_featured",
                url=e.image_url,
                event_id=e.id,
                recommendation=f"Use featured image for “{e.title}”.",
            )
        if len(with_images) > 1:
            return ImagePlan(
                source="collage",
                url=with_images[0].image_url,
                event_id=with_images[0].id,
                recommendation=(
                    "Build a simple collage from today's event images "
                    f"({len(with_images)} available). Lead with “{with_images[0].title}”."
                ),
            )
        titles = ", ".join(e.title for e in events[:3])
        return ImagePlan(
            source="generate_prompt",
            prompt=_prompt_today(events),
            recommendation=f"No event image found. Generate from prompt for: {titles}.",
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
            source="generate_prompt",
            prompt=_prompt_week(events),
            recommendation="No event images this week — generate a roundup visual.",
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
        source="generate_prompt",
        prompt=_prompt_spotlight(e),
        recommendation=f"No featured image for “{e.title}” — generate promotional art.",
    )


def _prompt_today(events: List[Event]) -> str:
    names = "; ".join(f"{e.title} ({e.start_date})" for e in events[:4])
    return (
        "Sacred Ground crystal shop interior, Tucson desert light through the windows, "
        "warm wood and soft lamplight, crystals on shelves, inviting and grounded — not glossy stock. "
        f"Mood for today's gatherings: {names}. No text overlay."
    )


def _prompt_week(events: List[Event]) -> str:
    names = ", ".join(e.title for e in events[:6])
    return (
        "Editorial still life for Sacred Ground weekly events: crystals, oracle cards, "
        "a cup of tea, soft afternoon light, Tucson warmth. Calm and specific, not generic spa. "
        f"Suggests: {names}. No text overlay."
    )


def _prompt_spotlight(event: Event) -> str:
    return (
        f"Promotional atmosphere for Sacred Ground event “{event.title}”. "
        "Intimate Tucson metaphysical shop energy — crystals, soft glow, real texture. "
        "Cinematic but warm. No text overlay, no fake logos."
    )
