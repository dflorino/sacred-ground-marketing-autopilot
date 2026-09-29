#!/usr/bin/env python3
"""Sep 29 morning — Archangel Day type on the rose-window sky."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SRC = Path("/tmp/sg-archangel-28860.jpg")
OUT = ROOT / "assets" / "sg-morning-flyer-2026-09-29-archangel-day.jpg"
LOGO = ROOT / "config/brand/sacred-ground-logo-circle-transparent.png"
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
SIZE = 1080
FOOTER_H = 118


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def center(draw, y, text, fnt, fill, width, x0=0):
    box = draw.textbbox((0, 0), text, font=fnt)
    tw = box[2] - box[0]
    draw.text((x0 + (width - tw) / 2, y), text, font=fnt, fill=fill)


def rounded(draw, box, fill, r):
    draw.rounded_rectangle(box, radius=r, fill=fill)


def compose() -> Path:
    photo_h = SIZE - FOOTER_H
    photo = Image.open(SRC).convert("RGB").resize((SIZE, photo_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (SIZE, SIZE), (245, 236, 214))
    canvas.paste(photo, (0, 0))
    overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    cream = (255, 246, 226, 168)
    rounded(od, (48, 22, SIZE - 48, 158), cream, 26)
    band_h = 136
    band_top = photo_h - band_h - 8
    rounded(od, (22, band_top, SIZE - 22, photo_h - 6), cream, 18)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(canvas)
    ink = (8, 8, 8)
    gold = (120, 70, 16)

    center(draw, 32, "TODAY", font("Impact.ttf", 64), ink, SIZE)
    center(draw, 100, "ARCHANGEL DAY", font("Arial Black.ttf", 34), gold, SIZE)
    center(draw, 138, "#1  CHICAGOLAND", font("Georgia Bold.ttf", 22), gold, SIZE)

    events = [
        ("AMBER", "Massage  ·  12–5"),
        ("TINA", "Tarot  Runes  Reiki  ·  12–5"),
        ("KATE", "Sound Bath  ·  FREE  ·  7–8"),
    ]
    col_w = (SIZE - 36) / 3
    nf = font("Arial Black.ttf", 36)
    detf = font("Arial Bold.ttf", 20)
    for i, (name, detail) in enumerate(events):
        x0 = 18 + i * col_w
        center(draw, band_top + 16, name, nf, ink, col_w, x0=x0)
        center(draw, band_top + 68, detail, detf, (28, 28, 28), col_w, x0=x0)

    fy = SIZE - FOOTER_H + 38
    center(
        draw,
        fy,
        "shopsacredground.com   ·   847-749-3922",
        font("Georgia Bold.ttf", 30),
        (40, 32, 22),
        SIZE,
    )
    logo = Image.open(LOGO).convert("RGBA")
    lw = int(SIZE * 0.11)
    logo = logo.resize((lw, lw), Image.Resampling.LANCZOS)
    a = logo.split()[3].point(lambda p: int(p * 0.86))
    logo.putalpha(a)
    canvas.paste(logo, (16, SIZE - FOOTER_H + (FOOTER_H - lw) // 2), logo)
    canvas.convert("RGB").save(OUT, quality=93, optimize=True)
    print(OUT)
    return OUT


if __name__ == "__main__":
    compose()
