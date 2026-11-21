#!/usr/bin/env python3
"""LOOK — sale photo is the 5pm whole thing; cream footer carries that day's info."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compose_look import FLAG_TALL, FLAG_WIDE, SALE_FLAG, hang_pennant

OUT = Path(__file__).resolve().parent
TRASH = Path("/Users/deneene/Library/Mobile Documents/.Trash")
LOGO = ROOT / "config/brand/sacred-ground-logo-circle-transparent.png"
AVENIR = "/System/Library/Fonts/Avenir Next.ttc"

W, H = 1080, 1350
FOOTER_H = 188
PHOTO_H = H - FOOTER_H
CREAM = (245, 236, 214)
INK = (18, 14, 12)

SIX = [
    "Sacred-Ground-Copper-and-Pine.jpg",
    "Sacred-Ground-Cosmic-Amethyst.jpg",
    "Sacred-Ground-Candlelit-Crystal-Shop.jpg",
    "Sacred-Ground-Frosted-Quartz.jpg",
    "Sacred-Ground-Cranberry-and-Rose-Quartz.jpg",
    "Sacred-Ground-Evergreen-and-Gold.jpg",
]


def bold(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(AVENIR, size, index=0)


def medium(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(AVENIR, size, index=5)


def crop_price_bar(im: Image.Image) -> Image.Image:
    rgb = im.convert("RGB")
    w, h = rgb.size
    cut = h
    for y in range(h - 1, h // 2, -1):
        r, g, b = rgb.getpixel((24, y))
        luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
        if luma > 40:
            cut = y + 1
            break
    return rgb.crop((0, 0, w, cut))


def fit_cover(im: Image.Image, w: int, h: int) -> Image.Image:
    scale = max(w / im.width, h / im.height)
    nw, nh = int(im.width * scale + 0.5), int(im.height * scale + 0.5)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = 0
    return im.crop((left, top, left + w, top + h))


def paste_logo(canvas: Image.Image) -> None:
    logo = Image.open(LOGO).convert("RGBA")
    lw = int(W * 0.12)
    logo = logo.resize((lw, lw), Image.Resampling.LANCZOS)
    logo.putalpha(logo.split()[3].point(lambda p: int(p * 0.85)))
    canvas.paste(logo, (18, PHOTO_H - lw - 16), logo)


def text_w(draw, text, fnt) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def center(draw, y, text, fnt) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    x = (W - (box[2] - box[0])) / 2
    draw.text((x, y - box[1]), text, font=fnt, fill=INK)
    return box[3] - box[1]


def footer(canvas: Image.Image, date_line: str, name: str, details: list[str]) -> None:
    draw = ImageDraw.Draw(canvas)
    y0 = PHOTO_H
    draw.rectangle((0, y0, W, H), fill=CREAM)
    name_size = 32
    name_font = bold(name_size)
    while text_w(draw, name, name_font) > 1000 and name_size > 24:
        name_size -= 2
        name_font = bold(name_size)
    detail_size = 20
    detail_font = bold(detail_size)
    date_font = medium(22)
    site_font = medium(18)
    block = (
        24
        + 6
        + name_size
        + 4
        + detail_size * len(details)
        + 3 * (len(details) - 1)
        + 6
        + 20
    )
    y = y0 + max(8, (FOOTER_H - block) // 2)
    y += center(draw, y, date_line, date_font) + 6
    y += center(draw, y, name, name_font) + 4
    for detail in details:
        y += center(draw, y, detail, detail_font) + 3
    y += 6
    center(draw, y, "shopsacredground.com  ·  847-749-3922", site_font)


def compose(
    src: Path,
    dest: Path,
    date_line: str,
    name: str,
    details: list[str],
    flag_lines: list[str] | None = None,
) -> Path:
    photo = fit_cover(crop_price_bar(Image.open(src)), W, PHOTO_H)
    canvas = Image.new("RGB", (W, H), CREAM)
    canvas.paste(photo, (0, 0))
    hang_pennant(
        canvas,
        flag_lines or SALE_FLAG,
        photo_h=PHOTO_H,
        top=PHOTO_H - 20,
        angle=-8.0,
        wide=FLAG_WIDE,
        tall=FLAG_TALL,
    )
    paste_logo(canvas)
    footer(canvas, date_line, name, details)
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, quality=93, optimize=True)
    return dest


def main() -> None:
    six_dir = OUT / "six"
    six_dir.mkdir(parents=True, exist_ok=True)
    locals_ = []
    for name in SIX:
        src = TRASH / name
        dest = six_dir / name
        if src.exists():
            shutil.copy2(src, dest)
        locals_.append(dest)

    today = compose(
        locals_[0],
        OUT / "05-afternoon-nov18-educational-night.jpg",
        "Wed Nov 18  ·  #1 Chicagoland",
        "Educational Night",
        ["Free  ·  7:00–8:30 PM", "Tina  ·  until 6:00 PM"],
    )
    thu = compose(
        locals_[1],
        OUT / "06-afternoon-nov19-tarotheads.jpg",
        "Thu Nov 19  ·  #1 Chicagoland",
        "TarotHeads with Andre",
        ["Free  ·  7:00–9:00 PM", "Frequency Reset  ·  until 6:30 PM"],
    )
    print(today.name, today.stat().st_size)
    print(thu.name, thu.stat().st_size)


if __name__ == "__main__":
    main()
