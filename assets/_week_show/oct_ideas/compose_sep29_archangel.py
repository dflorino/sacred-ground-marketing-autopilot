#!/usr/bin/env python3
"""Sep 29 morning — gold ARCHANGEL DAY on the glass; names in the footer."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SRC = Path("/tmp/sg-archangel-28860.jpg")
OUT = ROOT / "assets" / "sg-morning-flyer-2026-09-29-archangel-day-v2.jpg"
LOGO = ROOT / "config/brand/sacred-ground-logo-circle-transparent.png"
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
SIZE = 1080
FOOTER_H = 200


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def center(draw, y, text, fnt, fill, width, x0=0):
    box = draw.textbbox((0, 0), text, font=fnt)
    tw = box[2] - box[0]
    draw.text((x0 + (width - tw) / 2, y), text, font=fnt, fill=fill)


def compose() -> Path:
    photo_h = SIZE - FOOTER_H
    photo = Image.open(SRC).convert("RGB").resize((SIZE, photo_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (SIZE, SIZE), (245, 236, 214))
    canvas.paste(photo, (0, 0))
    draw = ImageDraw.Draw(canvas)

    gold = (212, 168, 58)
    ink = (18, 14, 8)
    title = font("Impact.ttf", 72)
    # Gold on the glass — no cream banner. Soft dark shadow for read.
    for dx, dy in ((2, 2), (0, 2), (2, 0)):
        center(draw, 36 + dy, "ARCHANGEL DAY", title, (20, 12, 4), SIZE)
    center(draw, 36, "ARCHANGEL DAY", title, gold, SIZE)

    events = [
        ("AMBER", "Massage  ·  12–5"),
        ("TINA", "Tarot  Runes  Reiki  ·  12–5"),
        ("KATE", "Sound Bath  ·  FREE  ·  7–8"),
    ]
    col_w = SIZE / 3
    nf = font("Arial Black.ttf", 40)
    detf = font("Arial Bold.ttf", 22)
    for i, (name, detail) in enumerate(events):
        x0 = i * col_w
        center(draw, photo_h + 22, name, nf, ink, col_w, x0=x0)
        center(draw, photo_h + 74, detail, detf, (36, 28, 18), col_w, x0=x0)

    center(
        draw,
        photo_h + 132,
        "#1  CHICAGOLAND",
        font("Georgia Bold.ttf", 28),
        (120, 70, 16),
        SIZE,
    )

    logo = Image.open(LOGO).convert("RGBA")
    lw = int(SIZE * 0.11)
    logo = logo.resize((lw, lw), Image.Resampling.LANCZOS)
    a = logo.split()[3].point(lambda p: int(p * 0.86))
    logo.putalpha(a)
    canvas.paste(logo, (16, photo_h - lw - 12), logo)

    canvas.convert("RGB").save(OUT, quality=93, optimize=True)
    print(OUT)
    return OUT


if __name__ == "__main__":
    compose()
