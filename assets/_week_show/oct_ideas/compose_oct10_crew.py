#!/usr/bin/env python3
"""Oct 10 Galactic Adventurers boxes — names on the colored lips (PIL)."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "assets/_week_show/oct_nights/oct10-crew-boxes-v13.jpg"
OUT = ROOT / "assets/sg-morning-flyer-2026-10-10.jpg"
DESK = Path.home() / "Desktop" / "sg-civilization-nights" / "sg-morning-flyer-2026-10-10.jpg"
LOGO = ROOT / "config/brand/sacred-ground-logo-circle-transparent.png"
SIZE, FOOTER_H = 1080, 168
CREAM, INK, GOLD = (245, 236, 214), (12, 10, 8), (120, 70, 16)
# Names sit on the box lip under the window (22pt). Kobi lower on gold.
BOX_NAMES = [
    ("DENEENE", 215, 758, (245, 236, 214)),
    ("LUCA", 540, 748, (245, 236, 214)),
    ("KOBI", 870, 722, (20, 16, 12)),
]


def fnt(name: str, size: int):
    for base in (Path("/System/Library/Fonts/Supplemental"), Path("/System/Library/Fonts")):
        p = base / name
        if p.is_file():
            return ImageFont.truetype(str(p), size)
    return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)


def fit_cover(im, w, h):
    im = im.convert("RGB")
    iw, ih = im.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = max(0, (nh - h) // 6)
    return im.crop((left, top, left + w, top + h))


def center(draw, y, text, font, fill, width, x0=0):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((x0 + (width - tw) / 2, y - bbox[1]), text, font=font, fill=fill)


def main() -> None:
    photo_h = SIZE - FOOTER_H
    photo = fit_cover(Image.open(ART), SIZE, photo_h)
    d = ImageDraw.Draw(photo)
    namef = fnt("Arial Black.ttf", 22)
    for text, cx, cy, fill in BOX_NAMES:
        bbox = d.textbbox((0, 0), text, font=namef)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), text, font=namef, fill=fill)

    canvas = Image.new("RGB", (SIZE, SIZE), CREAM)
    canvas.paste(photo, (0, 0))
    draw = ImageDraw.Draw(canvas)
    top = photo_h + 6
    center(draw, top, "SATURDAY  OCT 10", fnt("Impact.ttf", 26), INK, SIZE)
    center(draw, top + 26, "CHICAGOLAND’S PREMIER", fnt("Georgia Bold.ttf", 15), GOLD, SIZE)
    events = [("MELISSA", "Shaman Medium  ·  11–2"), ("ADIE", "Tarot  ·  11–3"), ("ROSE", "Reiki  ·  12–5")]
    col_w = (SIZE - 40) / 3
    for i, (name, detail) in enumerate(events):
        x0 = 20 + i * col_w
        center(draw, top + 46, name, fnt("Arial Black.ttf", 28), INK, col_w, x0=x0)
        center(draw, top + 80, detail, fnt("Georgia Bold.ttf", 16), INK, col_w, x0=x0)
    center(draw, SIZE - 28, "shopsacredground.com   ·   847-749-3922", fnt("Georgia Bold.ttf", 18), (40, 32, 22), SIZE)
    logo = Image.open(LOGO).convert("RGBA").resize((52, 52), Image.Resampling.LANCZOS)
    a = logo.split()[3].point(lambda p: int(p * 0.88))
    logo.putalpha(a)
    canvas.paste(logo, (10, SIZE - 58), logo)
    canvas.save(OUT, quality=92, optimize=True)
    DESK.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(DESK, quality=92)
    print(OUT)


if __name__ == "__main__":
    main()
