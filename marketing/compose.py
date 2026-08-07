"""Compose branded Today social graphics (logo + overlay + footer)."""
from __future__ import annotations

import io
import math
import os
import urllib.request
from datetime import date
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .classify import format_when
from .models import Event
from .paths import COMPOSITES_DIR, FONTS_DIR, ROOT, creative, ensure_dirs, settings

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Pillow is required for social composites. pip install Pillow") from exc


PHOTO_SIZE = 1080
FOOTER_H = 160
GOLD = (232, 196, 110, 255)
GOLD_SOFT = (245, 220, 150, 255)
INK = (22, 18, 14, 255)
CREAM = (245, 236, 220, 255)


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
    for r, g, b in small.getdata():
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
    # format_when includes weekday; keep the time portion when possible
    if "·" in when:
        return when.split("·", 1)[1].strip()
    return when


def overlay_copy(events: Sequence[Event], day: date) -> Dict[str, Any]:
    """Short on-image lines — not the full caption."""
    loc = (creative().get("location") or "Arlington Heights")
    day_name = day.strftime("%A")
    if not events:
        return {
            "campaign_word": "TODAY",
            "lines": [
                "Visit Sacred Ground",
                "Crystals · Books · Curious Finds",
                f"{day_name} · {loc}",
            ],
        }
    if len(events) == 1:
        ev = events[0]
        return {
            "campaign_word": "TODAY",
            "lines": [
                _short_title(ev.title, 48),
                f"{_time_bit(ev)} · {loc}",
            ],
        }
    lines: List[str] = []
    for ev in list(events)[:4]:
        lines.append(f"{_short_title(ev.title, 34)} · {_time_bit(ev)}")
    lines.append(f"{day_name} · {loc}")
    return {"campaign_word": "TODAY", "lines": lines}


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
    # soft dark shadow only — never white stroke/halo
    draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 100))
    draw.text((x, y), text, font=font, fill=fill)
    return th


def _draw_arched_word(
    canvas: Image.Image,
    text: str,
    font: ImageFont.ImageFont,
    fill: Tuple[int, int, int, int],
    cy: int = 70,
    radius: int = 520,
) -> None:
    draw = ImageDraw.Draw(canvas)
    chars = list(text)
    widths = [_text_size(draw, font, c)[0] + 6 for c in chars]
    total = sum(widths) or 1
    span = min(1.15, total / max(radius, 1))
    angle = -span / 2
    W = canvas.width
    for c, w in zip(chars, widths):
        mid = angle + (w / radius) / 2
        ch_img = Image.new("RGBA", (w + 60, 180), (0, 0, 0, 0))
        cd = ImageDraw.Draw(ch_img)
        cd.text((22, 24), c, font=font, fill=(0, 0, 0, 90))
        cd.text((20, 22), c, font=font, fill=fill)
        rot = ch_img.rotate(-math.degrees(mid), resample=Image.Resampling.BICUBIC, expand=True)
        rx = int(W / 2 + radius * math.sin(mid) - rot.width / 2)
        ry = int(cy + radius * (1 - math.cos(mid)) - rot.height / 2 + 10)
        canvas.alpha_composite(rot, (max(0, rx), max(0, ry)))
        angle += w / radius


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


def compose_today_graphic(
    *,
    background_url: str,
    events: Sequence[Event],
    day: date,
    out_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build the final Today graphic:
    photo + TODAY + short event lines + translucent logo + cream footer
    with shopsacredground.com and phone.
    """
    ensure_dirs()
    os.makedirs(COMPOSITES_DIR, exist_ok=True)

    photo = _load_image(background_url)
    photo = photo.resize((PHOTO_SIZE, PHOTO_SIZE), Image.Resampling.LANCZOS)
    fill, contrast_name = text_color_for(photo)
    soft = GOLD_SOFT if contrast_name == "gold" else (40, 32, 24, 255)

    canvas = Image.new("RGBA", (PHOTO_SIZE, PHOTO_SIZE + FOOTER_H), CREAM)
    # Soft cream wash behind mid text (never a black box)
    wash = Image.new("RGBA", (PHOTO_SIZE, PHOTO_SIZE), (0, 0, 0, 0))
    for y0, y1, a in ((30, 210, 50), (280, 720, 65)):
        layer = Image.new("RGBA", (PHOTO_SIZE, PHOTO_SIZE), (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse((-100, y0, PHOTO_SIZE + 100, y1), fill=(250, 242, 225, a))
        wash = Image.alpha_composite(wash, layer)
    wash = wash.filter(ImageFilter.GaussianBlur(26))
    photo_area = Image.alpha_composite(photo, wash)
    canvas.paste(photo_area, (0, 0))

    copy = overlay_copy(events, day)
    f_today = _font("BubblegumSans-Regular.ttf", 112)
    f_line = _font("IndieFlower-Regular.ttf", 48)
    f_meta = _font("BubblegumSans-Regular.ttf", 40)
    f_script = _font("Courgette-Regular.ttf", 44)
    f_footer = _font("BubblegumSans-Regular.ttf", 36)
    f_phone = _font("IndieFlower-Regular.ttf", 34)

    _draw_arched_word(canvas, copy["campaign_word"], f_today, fill, cy=55, radius=540)

    draw = ImageDraw.Draw(canvas)
    y = 300 if len(copy["lines"]) <= 3 else 260
    for i, line in enumerate(copy["lines"]):
        font = f_script if i == len(copy["lines"]) - 1 and len(copy["lines"]) > 1 else (
            f_meta if "·" in line and i > 0 else f_line
        )
        # Keep long multi-event lines a bit smaller
        if len(line) > 40:
            font = _font("IndieFlower-Regular.ttf", 42)
        th = _draw_centered(draw, line, y, font, fill if i == 0 else soft, PHOTO_SIZE)
        y += th + 28

    _apply_logo(canvas, PHOTO_SIZE)

    # Footer band (always): website + phone under the photo
    website = ((creative().get("overlay_text") or {}).get("website_line") or "shopsacredground.com")
    phone = (
        ((settings().get("campaigns") or {}).get("week_ahead") or {}).get("cta_phone")
        or "847-749-3922"
    )
    draw.line([(70, PHOTO_SIZE + 10), (PHOTO_SIZE - 70, PHOTO_SIZE + 10)], fill=(200, 170, 110, 160), width=2)
    for text, font, yy in (
        (website, f_footer, PHOTO_SIZE + 42),
        (phone, f_phone, PHOTO_SIZE + 92),
    ):
        tw, _ = _text_size(draw, font, text)
        draw.text(((PHOTO_SIZE - tw) // 2, yy), text, font=font, fill=INK)

    if not out_path:
        out_path = os.path.join(COMPOSITES_DIR, f"today-{day.isoformat()}.png")
    rgb = canvas.convert("RGB")
    rgb.save(out_path, "PNG", optimize=True)

    return {
        "path": out_path,
        "filename": os.path.basename(out_path),
        "contrast": contrast_name,
        "luma": round(mean_luma(photo), 1),
        "width": rgb.width,
        "height": rgb.height,
        "overlay": copy,
        "footer": {"website": website, "phone": phone},
        "background_url": background_url,
    }
