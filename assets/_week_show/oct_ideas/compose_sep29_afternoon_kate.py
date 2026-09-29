#!/usr/bin/env python3
"""Sep 29 5pm — cosmic shop Fair-flag, Kate Sound Bath only."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "assets" / "sg-morning-flyer-2026-09-29-fair-flag.jpg"
OUT = ROOT / "assets" / "sg-afternoon-spotlight-2026-09-29-kate-sound-bath.jpg"
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
CREAM = (244, 236, 213)
INK = (12, 10, 8)
EGGPLANT = (62, 28, 74)
FLAG_CREAM = (245, 236, 214)
FLAG = "HOLISTIC FAIR   ·   OCT 10   ·   12–6"


def fnt(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def center(draw: ImageDraw.ImageDraw, y: float, text: str, font, fill, width: int) -> None:
    box = draw.textbbox((0, 0), text, font=font)
    tw = box[2] - box[0]
    draw.text(((width - tw) / 2, y), text, font=font, fill=fill)


def draw_pennant(canvas: Image.Image) -> None:
    draw = ImageDraw.Draw(canvas)
    font = fnt("Arial Black.ttf", 16)
    bbox = draw.textbbox((0, 0), FLAG, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 18, 7
    tail = 22
    body_w = tw + pad_x * 2
    h = th + pad_y * 2
    total_w = body_w + tail
    x0 = (canvas.width - total_w) // 2
    y0 = canvas.height - 62
    pts = [
        (x0, y0),
        (x0 + body_w, y0),
        (x0 + body_w + tail, y0 + h // 2),
        (x0 + body_w, y0 + h),
        (x0, y0 + h),
    ]
    draw.polygon(pts, fill=EGGPLANT)
    draw.line([(x0, y0), (x0, y0 + h)], fill=(196, 148, 52), width=4)
    draw.text((x0 + pad_x - bbox[0], y0 + pad_y - bbox[1]), FLAG, font=font, fill=FLAG_CREAM)


def compose() -> Path:
    canvas = Image.open(SRC).convert("RGB")
    draw = ImageDraw.Draw(canvas)
    w, h = canvas.size
    # Wipe date + three-name row. Keep pennant, website, logo.
    draw.rectangle((0, 912, w, 1016), fill=CREAM)
    center(draw, 922, "FREE MEDITATION SOUND BATH", fnt("Arial Black.ttf", 30), INK, w)
    center(draw, 962, "W/ KATE  ·  7–8 PM", fnt("Arial Black.ttf", 42), INK, w)
    draw_pennant(canvas)
    canvas.save(OUT, quality=93)
    return OUT


if __name__ == "__main__":
    print(compose())
