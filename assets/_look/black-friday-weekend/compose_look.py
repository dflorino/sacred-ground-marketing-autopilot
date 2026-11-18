#!/usr/bin/env python3
"""LOOK only — Black Friday / Small Business Saturday flag + 5pm whole plate.

Do not upload. Do not wire. Founder has not KEEP'd these.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LOGO = ROOT / "config/brand/sacred-ground-logo-circle-transparent.png"
AVENIR = "/System/Library/Fonts/Avenir Next.ttc"

W, H = 1080, 1350
FOOTER_H = 188
PHOTO_H = H - FOOTER_H
CREAM = (245, 236, 214)
INK = (18, 14, 12)
WHITE = (255, 255, 255)
GOLD = (238, 191, 42)
EGGPLANT = (74, 28, 92)
EGGPLANT_EDGE = (48, 16, 62)
SHADOW = (12, 8, 6)


def bold(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(AVENIR, size, index=0)


def medium(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(AVENIR, size, index=5)


def fit_cover(im: Image.Image, w: int, h: int) -> Image.Image:
    im = im.convert("RGB")
    scale = max(w / im.width, h / im.height)
    nw, nh = int(im.width * scale + 0.5), int(im.height * scale + 0.5)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = max(0, (nh - h) // 6)
    if top + h > nh:
        top = nh - h
    return im.crop((left, top, left + w, top + h))


def cream_start(im: Image.Image) -> int:
    rgb = im.convert("RGB")
    w, h = rgb.size
    for y in range(h - 1, h // 2, -1):
        r, g, b = rgb.getpixel((18, y))
        if abs(r - 245) > 18 or abs(g - 236) > 18 or abs(b - 214) > 18:
            return y + 1
    return h - FOOTER_H


def paste_logo(canvas: Image.Image, photo_h: int) -> None:
    logo = Image.open(LOGO).convert("RGBA")
    lw = int(W * 0.12)
    logo = logo.resize((lw, lw), Image.Resampling.LANCZOS)
    logo.putalpha(logo.split()[3].point(lambda p: int(p * 0.85)))
    canvas.paste(logo, (18, photo_h - lw - 16), logo)


def footer(canvas: Image.Image, lines: list[tuple[ImageFont.FreeTypeFont, str]]) -> None:
    draw = ImageDraw.Draw(canvas)
    y0 = PHOTO_H
    draw.rectangle((0, y0, W, H), fill=CREAM)
    heights = []
    for fnt, text in lines:
        box = draw.textbbox((0, 0), text, font=fnt)
        heights.append(box[3] - box[1])
    gap = 8
    block = sum(heights) + gap * (len(lines) - 1)
    y = y0 + (FOOTER_H - block) // 2
    for (fnt, text), hh in zip(lines, heights):
        box = draw.textbbox((0, 0), text, font=fnt)
        x = (W - (box[2] - box[0])) / 2
        draw.text((x, y - box[1]), text, font=fnt, fill=INK)
        y += hh + gap


def make_pennant(lines: list[str], *, wide: int = 268, tall: int = 156) -> Image.Image:
    """Handmade hanging swallowtail — eggplant cloth, gold type, no Canva pill."""
    pad = 36
    layer = Image.new("RGBA", (wide + pad * 2, tall + pad * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x0, y0 = pad, pad
    x1, y1 = pad + wide, pad + tall
    bite = 28
    pts = [
        (x0, y0),
        (x1, y0),
        (x1, y1 - bite),
        (x0 + wide // 2, y1),
        (x0, y1 - bite),
    ]
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    shift = [(p[0] + 4, p[1] + 6) for p in pts]
    sd.polygon(shift, fill=(12, 8, 6, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    layer = Image.alpha_composite(layer, shadow)
    draw = ImageDraw.Draw(layer)
    draw.polygon(pts, fill=EGGPLANT + (255,))
    inset = [
        (x0 + 7, y0 + 7),
        (x1 - 7, y0 + 7),
        (x1 - 7, y1 - bite - 2),
        (x0 + wide // 2, y1 - 10),
        (x0 + 7, y1 - bite - 2),
    ]
    draw.polygon(inset, outline=GOLD + (255,))
    # stitch
    for i in range(10):
        t = i / 9
        sx = int(x0 + 14 + (wide - 28) * t)
        draw.line((sx, y0 + 14, sx + 6, y0 + 14), fill=GOLD + (180,), width=2)
    if len(lines) == 3:
        sizes = [24, 36, 18]
    elif lines[0].startswith("SMALL"):
        sizes = [22, 22]
    elif lines[0] == "BLACK FRIDAY" and lines[-1] == "SALES":
        sizes = [26, 40]
    else:
        sizes = [26, 32]
    fonts = [bold(s) for s in sizes[: len(lines)]]
    boxes = [draw.textbbox((0, 0), line, font=fnt) for line, fnt in zip(lines, fonts)]
    text_h = sum(b[3] - b[1] for b in boxes) + 6 * (len(lines) - 1)
    ty = y0 + 22 + max(0, (tall - bite - 18 - text_h) // 2)
    for line, fnt, box in zip(lines, fonts, boxes):
        tw = box[2] - box[0]
        tx = x0 + (wide - tw) / 2
        draw.text((tx, ty - box[1]), line, font=fnt, fill=GOLD)
        ty += (box[3] - box[1]) + 6
    # grommet
    gx, gy = x1 - 18, y0 + 10
    draw.ellipse((gx - 7, gy - 7, gx + 7, gy + 7), fill=GOLD + (255,))
    draw.ellipse((gx - 3, gy - 3, gx + 3, gy + 3), fill=EGGPLANT_EDGE + (255,))
    return layer


def hang_pennant(
    canvas: Image.Image,
    lines: list[str],
    *,
    photo_h: int,
    angle: float = -11.0,
    top: int = 22,
    wide: int = 268,
    tall: int = 156,
) -> None:
    flag = make_pennant(lines, wide=wide, tall=tall)
    flag = flag.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    x = W - flag.width - 10
    y = max(4, top)
    if y + flag.height > photo_h - 8:
        y = photo_h - flag.height - 8
    canvas.paste(flag, (x, y), flag)


SALE = "20% off while supplies last"


def cream_sale_line(im: Image.Image, photo_h: int, date_line: str) -> None:
    """Redraw the date row plus the offer. Stay above the host names (~51px)."""
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, photo_h, W, photo_h + 48), fill=CREAM)
    date_fnt = medium(18)
    sale_fnt = bold(20)
    y = photo_h + 6
    box = draw.textbbox((0, 0), date_line, font=date_fnt)
    x = (W - (box[2] - box[0])) / 2
    draw.text((x, y - box[1]), date_line, font=date_fnt, fill=INK)
    y += (box[3] - box[1]) + 3
    box = draw.textbbox((0, 0), SALE, font=sale_fnt)
    x = (W - (box[2] - box[0])) / 2
    draw.text((x, y - box[1]), SALE, font=sale_fnt, fill=INK)


def morning_flag() -> Path:
    src = ROOT / "assets/sg-morning-flyer-2026-11-19-star-clean.jpg"
    im = Image.open(src).convert("RGB")
    photo_h = cream_start(im)
    hang_pennant(im, ["BLACK FRIDAY", "SALES"], photo_h=photo_h, top=86)
    cream_sale_line(im, photo_h, "Thu Nov 19  ·  #1 Chicagoland")
    dest = OUT / "01-morning-flag.jpg"
    im.save(dest, quality=93, optimize=True)
    return dest


def saturday_morning_flag() -> Path:
    src = ROOT / "assets/sg-morning-flyer-2026-11-19-star-clean.jpg"
    im = Image.open(src).convert("RGB")
    photo_h = cream_start(im)
    hang_pennant(im, ["SMALL BUSINESS", "SATURDAY"], photo_h=photo_h, top=86)
    cream_sale_line(im, photo_h, "Sat Nov 28  ·  #1 Chicagoland")
    dest = OUT / "04-saturday-morning-flag.jpg"
    im.save(dest, quality=93, optimize=True)
    return dest


def afternoon_whole() -> Path:
    src = ROOT / "assets/sg-night-creative-fall-store-fairy-lights-noglyph.png"
    photo = fit_cover(Image.open(src), W, PHOTO_H)
    canvas = Image.new("RGB", (W, H), CREAM)
    canvas.paste(photo, (0, 0))
    draw = ImageDraw.Draw(canvas)
    # Dark sky is the readable band — type lives there, no black panel.
    h1 = bold(72)
    h2 = bold(72)
    sub = medium(32)
    y = 48
    for line, fnt in (("BLACK FRIDAY", h1), ("SALES", h2)):
        box = draw.textbbox((0, 0), line, font=fnt)
        x = (W - (box[2] - box[0])) / 2
        draw.text((x, y - box[1]), line, font=fnt, fill=WHITE)
        y += (box[3] - box[1]) + 4
    y += 10
    sub_line = "Small Business Saturday too"
    box = draw.textbbox((0, 0), sub_line, font=sub)
    x = (W - (box[2] - box[0])) / 2
    draw.text((x, y - box[1]), sub_line, font=sub, fill=GOLD)
    paste_logo(canvas, PHOTO_H)
    footer(
        canvas,
        [
            (medium(24), "All weekend  ·  #1 Chicagoland"),
            (bold(36), "Black Friday sales"),
            (medium(20), "shopsacredground.com  ·  847-749-3922"),
        ],
    )
    dest = OUT / "02-afternoon-whole.jpg"
    canvas.save(dest, quality=93, optimize=True)
    return dest


def night_flag() -> Path:
    src = ROOT / "assets/sg-night-creative-fall-store-harvest-moonlight-noglyph.png"
    if not src.exists():
        src = ROOT / "assets/sg-night-creative-fall-store-fairy-lights-noglyph.png"
    photo = fit_cover(Image.open(src), W, PHOTO_H)
    canvas = Image.new("RGB", (W, H), CREAM)
    canvas.paste(photo, (0, 0))
    draw = ImageDraw.Draw(canvas)
    gn = bold(48)
    line = "Goodnight."
    box = draw.textbbox((0, 0), line, font=gn)
    x = (W - (box[2] - box[0])) / 2
    # Sky is the dark band.
    draw.text((x, 42 - box[1]), line, font=gn, fill=WHITE)
    hang_pennant(
        canvas,
        ["BLACK FRIDAY", "SALES", "Small Business Saturday"],
        photo_h=PHOTO_H,
        top=18,
        angle=-10.0,
        wide=300,
        tall=188,
    )
    paste_logo(canvas, PHOTO_H)
    footer(
        canvas,
        [
            (medium(24), "Thu + Fri  ·  #1 Chicagoland"),
            (bold(28), "20% off while supplies last"),
            (medium(20), "shopsacredground.com  ·  847-749-3922"),
        ],
    )
    dest = OUT / "03-night-flag.jpg"
    canvas.save(dest, quality=93, optimize=True)
    return dest


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path in (
        morning_flag(),
        afternoon_whole(),
        night_flag(),
        saturday_morning_flag(),
    ):
        print(path.name, path.stat().st_size)


if __name__ == "__main__":
    main()
