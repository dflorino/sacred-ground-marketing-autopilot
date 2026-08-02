"""Compose branded social graphics (photo + logo + footer text band).

Applies to ALL campaigns: today, week, week_ahead, spotlight.
No event/campaign text is painted over the photo.
"""
from __future__ import annotations

import io
import os
import urllib.request
from datetime import date
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .classify import format_when
from .models import Event
from .paths import COMPOSITES_DIR, FONTS_DIR, ROOT, creative, ensure_dirs, settings

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Pillow is required for social composites. pip install Pillow") from exc


PHOTO_SIZE = 1080
# Tall cream band under the photo — event copy lives here (not over the image).
FOOTER_H = 340
INK = (22, 18, 14, 255)
CREAM = (245, 236, 220, 255)
GOLD = (232, 196, 110, 255)
RULE = (200, 170, 110, 180)

CAMPAIGN_WORDS = {
    "today": "TODAY",
    "week": "THIS WEEK",
    "week_ahead": "NEXT 7 DAYS",
    "spotlight": "SPOTLIGHT",
    "visit": "TODAY",
}


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = os.path.join(FONTS_DIR, name)
    if not os.path.exists(path):
        return ImageFont.load_default()
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def _load_image(url_or_path: str) -> Image.Image:
    if url_or_path.startswith("https://") or url_or_path.startswith("http://"):
        req = urllib.request.Request(
            url_or_path,
            headers={"User-Agent": "SacredGroundMarketingAutopilot/1.0"},
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = resp.read()
        return Image.open(io.BytesIO(data)).convert("RGBA")
    return Image.open(url_or_path).convert("RGBA")


def mean_luma(img: Image.Image) -> float:
    """Average perceived luma 0–255 for contrast decisions."""
    small = img.convert("RGB").resize((64, 64), Image.Resampling.BILINEAR)
    total = 0.0
    count = 0
    for r, g, b in small.get_flattened_data():
        total += 0.2126 * r + 0.7152 * g + 0.0722 * b
        count += 1
    return (total / count) if count else 128.0


def text_color_for(img: Image.Image) -> Tuple[Tuple[int, int, int, int], str]:
    cfg = (creative().get("contrast") or {})
    threshold = float(cfg.get("light_threshold") or 140)
    luma = mean_luma(img)
    if luma >= threshold:
        return INK, "black"
    return GOLD, "gold"


def _short_title(title: str, max_len: int = 42) -> str:
    t = (title or "").strip()
    for junk in ("*", "— Sacred Ground", " - Sacred Ground"):
        t = t.replace(junk, "")
    t = " ".join(t.split())
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].rstrip() + "…"


def _time_bit(ev: Event) -> str:
    when = format_when(ev)
    if "·" in when:
        return when.split("·", 1)[1].strip()
    return when


def footer_copy(
    campaign: str,
    events: Sequence[Event],
    day: date,
) -> Dict[str, Any]:
    """Short lines for the footer band — never drawn over the photo."""
    loc = creative().get("location") or "Arlington Heights"
    day_name = day.strftime("%A")
    word = CAMPAIGN_WORDS.get(campaign, "SACRED GROUND")

    if campaign in ("today", "visit") or (campaign == "today" and not events):
        if not events:
            return {
                "campaign_word": word,
                "lines": [
                    "Visit Sacred Ground",
                    "Crystals · Books · Curious Finds",
                    f"{day_name} · {loc}",
                ],
            }
        if len(events) == 1:
            ev = events[0]
            return {
                "campaign_word": word,
                "lines": [
                    _short_title(ev.title, 48),
                    f"{_time_bit(ev)} · {loc}",
                ],
            }
        lines = [f"{_short_title(ev.title, 34)} · {_time_bit(ev)}" for ev in list(events)[:3]]
        lines.append(f"{day_name} · {loc}")
        return {"campaign_word": word, "lines": lines}

    if campaign == "week":
        if not events:
            return {
                "campaign_word": word,
                "lines": [f"At Sacred Ground · {loc}", "See what’s on this week"],
            }
        lines = [f"{_short_title(ev.title, 36)} · {_time_bit(ev)}" for ev in list(events)[:3]]
        if len(events) > 3:
            lines.append(f"+{len(events) - 3} more · {loc}")
        else:
            lines.append(loc)
        return {"campaign_word": word, "lines": lines}

    if campaign == "week_ahead":
        if not events:
            return {
                "campaign_word": word,
                "lines": [f"At Sacred Ground · {loc}", "Come browse anytime"],
            }
        lines = [f"{_short_title(ev.title, 36)} · {_time_bit(ev)}" for ev in list(events)[:3]]
        if len(events) > 3:
            lines.append(f"+{len(events) - 3} more · {loc}")
        else:
            lines.append(loc)
        return {"campaign_word": word, "lines": lines}

    if campaign == "spotlight":
        if not events:
            return {
                "campaign_word": word,
                "lines": ["Special at Sacred Ground", loc],
            }
        ev = events[0]
        return {
            "campaign_word": word,
            "lines": [
                _short_title(ev.title, 48),
                f"{_time_bit(ev)} · {loc}",
            ],
        }

    # Fallback
    if events:
        ev = events[0]
        return {
            "campaign_word": word,
            "lines": [_short_title(ev.title, 48), f"{_time_bit(ev)} · {loc}"],
        }
    return {"campaign_word": word, "lines": [f"Sacred Ground · {loc}"]}


# Back-compat alias used by older tests / callers
def overlay_copy(events: Sequence[Event], day: date) -> Dict[str, Any]:
    return footer_copy("today", events, day)


def _text_size(draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont, text: str) -> Tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _draw_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.ImageFont,
    fill: Tuple[int, int, int, int],
    width: int,
) -> int:
    tw, th = _text_size(draw, font, text)
    x = (width - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return th


def _apply_logo(canvas: Image.Image, photo_h: int) -> None:
    cfg = (creative().get("logo") or {})
    rel = cfg.get("path") or "config/brand/sacred-ground-logo-circle-transparent.png"
    logo_path = rel if os.path.isabs(rel) else os.path.join(ROOT, rel)
    if not os.path.exists(logo_path):
        return
    logo = Image.open(logo_path).convert("RGBA")
    max_pct = float(cfg.get("max_width_percent") or 12) / 100.0
    logo_w = int(canvas.width * max_pct)
    logo = logo.resize(
        (logo_w, int(logo.height * (logo_w / logo.width))),
        Image.Resampling.LANCZOS,
    )
    opacity = float(cfg.get("opacity") or 0.88)
    r, g, b, a = logo.split()
    a = a.point(lambda p: int(p * opacity))
    logo = Image.merge("RGBA", (r, g, b, a))
    margin = int(canvas.width * 0.035)
    ly = photo_h - logo.height - margin
    canvas.alpha_composite(logo, (margin, max(0, ly)))


def compose_campaign_graphic(
    *,
    campaign: str,
    background_url: str,
    events: Sequence[Event],
    day: date,
    out_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a branded graphic for any campaign:
    clean photo + translucent logo + cream footer with campaign/event copy,
    shopsacredground.com, and phone. No text painted over the photo.
    """
    ensure_dirs()
    os.makedirs(COMPOSITES_DIR, exist_ok=True)
    campaign = (campaign or "today").strip().lower()

    photo = _load_image(background_url)
    photo = photo.resize((PHOTO_SIZE, PHOTO_SIZE), Image.Resampling.LANCZOS)
    _, contrast_name = text_color_for(photo)

    canvas = Image.new("RGBA", (PHOTO_SIZE, PHOTO_SIZE + FOOTER_H), CREAM)
    canvas.paste(photo, (0, 0))
    _apply_logo(canvas, PHOTO_SIZE)

    copy = footer_copy(campaign, events, day)
    # Slightly smaller campaign word for longer labels
    word = copy["campaign_word"]
    f_today = _font("BubblegumSans-Regular.ttf", 52 if len(word) > 8 else 64)
    f_title = _font("Courgette-Regular.ttf", 40)
    f_meta = _font("IndieFlower-Regular.ttf", 32)
    f_footer = _font("BubblegumSans-Regular.ttf", 34)
    f_phone = _font("IndieFlower-Regular.ttf", 32)

    draw = ImageDraw.Draw(canvas)
    website = ((creative().get("overlay_text") or {}).get("website_line") or "shopsacredground.com")
    phone = (
        ((settings().get("campaigns") or {}).get("week_ahead") or {}).get("cta_phone")
        or ((settings().get("campaigns") or {}).get("today") or {}).get("cta_phone")
        or "847-749-3922"
    )

    draw.line(
        [(70, PHOTO_SIZE + 14), (PHOTO_SIZE - 70, PHOTO_SIZE + 14)],
        fill=RULE,
        width=2,
    )

    y = PHOTO_SIZE + 36
    y += _draw_centered(draw, word, y, f_today, INK, PHOTO_SIZE) + 10
    for i, line in enumerate(copy["lines"]):
        font = f_title if i == 0 else f_meta
        if len(line) > 44:
            font = _font("IndieFlower-Regular.ttf", 28)
        y += _draw_centered(draw, line, y, font, INK, PHOTO_SIZE) + 8

    y = max(y + 6, PHOTO_SIZE + FOOTER_H - 96)
    draw.line(
        [(180, y - 8), (PHOTO_SIZE - 180, y - 8)],
        fill=RULE,
        width=1,
    )
    y += _draw_centered(draw, website, y, f_footer, INK, PHOTO_SIZE) + 6
    _draw_centered(draw, phone, y, f_phone, INK, PHOTO_SIZE)

    if not out_path:
        out_path = os.path.join(
            COMPOSITES_DIR, f"{campaign}-{day.isoformat()}.png"
        )
    rgb = canvas.convert("RGB")
    rgb.save(out_path, "PNG", optimize=True)

    return {
        "path": out_path,
        "filename": os.path.basename(out_path),
        "campaign": campaign,
        "contrast": contrast_name,
        "luma": round(mean_luma(photo), 1),
        "width": rgb.width,
        "height": rgb.height,
        "overlay": copy,
        "overlay_on_photo": False,
        "footer": {"website": website, "phone": phone, "event_lines": copy["lines"]},
        "background_url": background_url,
    }


def compose_today_graphic(
    *,
    background_url: str,
    events: Sequence[Event],
    day: date,
    out_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Back-compat wrapper — Today uses the shared campaign compositor."""
    return compose_campaign_graphic(
        campaign="today",
        background_url=background_url,
        events=events,
        day=day,
        out_path=out_path,
    )
