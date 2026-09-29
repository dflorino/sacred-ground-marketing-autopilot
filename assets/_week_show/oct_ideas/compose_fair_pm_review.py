#!/usr/bin/env python3
"""Ten Holistic Fair 5pm review plates — type on the photo, footer is site+phone."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "assets/_week_show/oct_ideas/fair_pm_raw"
OUT = ROOT / "assets/_week_show/oct_ideas/fair_pm_review"
LOGO = ROOT / "config/brand/sacred-ground-logo-circle-transparent.png"
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
SIZE = 1080
FOOTER_H = 88
CREAM = (245, 236, 214)
INK = (14, 10, 8)
EGGPLANT = (62, 28, 74)


def fnt(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def center(draw, y, text, font, fill, width, x0=0):
    box = draw.textbbox((0, 0), text, font=font)
    tw = box[2] - box[0]
    draw.text((x0 + (width - tw) / 2, y), text, font=font, fill=fill)


def fit_cover(im: Image.Image, w: int, h: int) -> Image.Image:
    im = im.convert("RGB")
    scale = max(w / im.width, h / im.height)
    nw, nh = int(im.width * scale + 0.5), int(im.height * scale + 0.5)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def paste_logo(canvas: Image.Image, photo_h: int) -> None:
    logo = Image.open(LOGO).convert("RGBA")
    lw = int(SIZE * 0.11)
    logo = logo.resize((lw, lw), Image.Resampling.LANCZOS)
    a = logo.split()[3].point(lambda p: int(p * 0.86))
    logo.putalpha(a)
    canvas.paste(logo, (14, photo_h - lw - 10), logo)


def footer(canvas: Image.Image) -> None:
    draw = ImageDraw.Draw(canvas)
    y0 = SIZE - FOOTER_H
    draw.rectangle((0, y0, SIZE, SIZE), fill=CREAM)
    center(
        draw,
        y0 + 26,
        "shopsacredground.com   ·   847-749-3922",
        fnt("Georgia Bold.ttf", 26),
        EGGPLANT,
        SIZE,
    )


def stroke_center(draw, y, text, font, fill, shadow, width):
    for dx, dy in ((2, 2), (-2, 1), (2, -1), (0, 2)):
        center(draw, y + dy, text, font, shadow, width)
    center(draw, y, text, font, fill, width)


def compose_one(src: Path, dest: Path, kind: str) -> Path:
    photo_h = SIZE - FOOTER_H
    canvas = Image.new("RGB", (SIZE, SIZE), CREAM)
    canvas.paste(fit_cover(Image.open(src), SIZE, photo_h), (0, 0))
    draw = ImageDraw.Draw(canvas)

    title = fnt("Impact.ttf", 72)
    script = fnt("SnellRoundhand.ttc", 42) if (FONT_DIR / "SnellRoundhand.ttc").is_file() else fnt("Georgia Italic.ttf", 40)
    detail = fnt("Arial Black.ttf", 32)
    small = fnt("Georgia Bold.ttf", 26)

    if kind == "ticket":
        # Write on the blank floating ticket.
        center(draw, 118, "HOLISTIC FAIR", fnt("Impact.ttf", 48), INK, SIZE)
        center(draw, 176, "Sat  Oct 10", fnt("Georgia Italic.ttf", 30), EGGPLANT, SIZE)
        center(draw, 214, "12–6 pm", fnt("Arial Black.ttf", 28), INK, SIZE)
    elif kind == "carousel":
        stroke_center(draw, 28, "HOLISTIC FAIR", title, INK, (255, 248, 230), SIZE)
        center(draw, 108, "Saturday  Oct 10  ·  12–6", detail, EGGPLANT, SIZE)
    elif kind == "folk":
        stroke_center(draw, 24, "HOLISTIC FAIR", title, INK, (255, 248, 230), SIZE)
        center(draw, 104, "Oct 10  ·  12–6", fnt("Georgia Bold.ttf", 34), EGGPLANT, SIZE)
    elif kind == "lanterns":
        stroke_center(draw, 36, "HOLISTIC FAIR", title, (255, 248, 230), (12, 8, 4), SIZE)
        center(draw, 116, "Saturday Oct 10  ·  12–6", detail, (255, 236, 180), SIZE)
    elif kind == "travel":
        stroke_center(draw, 28, "HOLISTIC FAIR", title, INK, (255, 248, 230), SIZE)
        center(draw, 108, "Arlington Heights  ·  Oct 10  ·  12–6", small, EGGPLANT, SIZE)
    elif kind == "harvest":
        center(draw, 18, "HOLISTIC FAIR", fnt("Impact.ttf", 64), INK, SIZE)
        center(draw, 88, "Sat Oct 10   ·   12–6", detail, EGGPLANT, SIZE)
    elif kind == "birdseye":
        # Soft cream wash at the bottom of the photo so type reads on leaves.
        wash = Image.new("RGBA", (SIZE, 150), (245, 236, 214, 210))
        canvas.paste(wash, (0, photo_h - 150), wash)
        draw = ImageDraw.Draw(canvas)
        center(draw, photo_h - 132, "HOLISTIC FAIR", fnt("Impact.ttf", 58), INK, SIZE)
        center(draw, photo_h - 68, "Saturday Oct 10  ·  12–6", detail, EGGPLANT, SIZE)
    elif kind == "night":
        stroke_center(draw, 40, "HOLISTIC FAIR", title, (255, 248, 230), (12, 8, 4), SIZE)
        center(draw, 120, "Sat Oct 10  ·  12–6", detail, (255, 220, 140), SIZE)
    elif kind == "magritte":
        stroke_center(draw, 36, "HOLISTIC FAIR", title, INK, (255, 248, 230), SIZE)
        center(draw, 116, "Oct 10  ·  12–6", fnt("Georgia Italic.ttf", 36), EGGPLANT, SIZE)
    elif kind == "kids":
        stroke_center(draw, 22, "HOLISTIC FAIR", title, INK, (255, 248, 230), SIZE)
        center(draw, 100, "Saturday Oct 10  ·  12–6", detail, EGGPLANT, SIZE)

    paste_logo(canvas, photo_h)
    footer(canvas)
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, quality=93)
    return dest


PLATES = [
    ("01-ticket.jpg", "01-ticket.jpg", "ticket"),
    ("02-carousel.jpg", "02-carousel.jpg", "carousel"),
    ("03-folk.jpg", "03-folk.jpg", "folk"),
    ("04-lanterns.jpg", "04-lanterns.jpg", "lanterns"),
    ("05-travel.jpg", "05-travel.jpg", "travel"),
    ("06-harvest.jpg", "06-harvest.jpg", "harvest"),
    ("07-birdseye.jpg", "07-birdseye.jpg", "birdseye"),
    ("08-night.jpg", "08-night.jpg", "night"),
    ("09-magritte.jpg", "09-magritte.jpg", "magritte"),
    ("10-kids.jpg", "10-kids.jpg", "kids"),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for src_name, dest_name, kind in PLATES:
        print(compose_one(RAW / src_name, OUT / dest_name, kind))


if __name__ == "__main__":
    main()
