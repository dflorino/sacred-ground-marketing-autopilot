#!/usr/bin/env python3
"""Sun Sep 20 remake: fall festival sun, no shop, no white boxes, no under-image bars."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
BG = Path(__file__).resolve().parent / "2026-09-20-art-fallfest-28292.jpg"
LOGO = ROOT / "config/brand/sacred-ground-logo-circle-transparent.png"
OUT = ROOT / "assets/sg-morning-flyer-2026-09-20-birthday-reiki.jpg"
SIZE = 1080
FOOTER = 92
FONT_DIR = Path("/System/Library/Fonts/Supplemental")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def fit_cover(im: Image.Image, w: int, h: int) -> Image.Image:
    im = im.convert("RGB")
    iw, ih = im.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def text_size(text, fnt):
    bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def font_to_width(name: str, text: str, target_w: int, start: int = 56) -> ImageFont.FreeTypeFont:
    size = start
    chosen = font(name, size)
    while size < 160:
        trial = font(name, size)
        if text_size(text, trial)[0] >= target_w:
            return trial
        chosen = trial
        size += 2
    return chosen


def draw_span(draw, y, text, fnt, fill, *, width: int, pad: int = 22):
    """One smaller line from the left edge to the right edge."""
    chars = list(text)
    if not chars:
        return
    inner = width - pad * 2
    if len(chars) == 1:
        draw.text((pad, y), text, font=fnt, fill=fill)
        return
    total = 0
    widths = []
    for ch in chars:
        w, _ = text_size(ch, fnt)
        widths.append(w)
        total += w
    extra = max(0, inner - total)
    gap = extra / (len(chars) - 1)
    x = pad
    bbox = draw.textbbox((0, 0), "Ag", font=fnt)
    py = y - bbox[1]
    for ch, w in zip(chars, widths):
        draw.text((x, py), ch, font=fnt, fill=fill)
        x += w + gap


def center_text(draw, xy, text, fnt, fill, nudge=None):
    x, y = xy
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    px, py = x - tw / 2, y - bbox[1]
    if nudge:
        draw.text((px + nudge[0], py + nudge[1]), text, font=fnt, fill=nudge[2])
    draw.text((px, py), text, font=fnt, fill=fill)
    return bbox[3] - bbox[1]


def main() -> None:
    photo_h = SIZE - FOOTER
    photo = fit_cover(Image.open(BG), SIZE, photo_h).convert("RGBA")
    plate = Image.new("RGBA", (SIZE, SIZE), (255, 246, 228, 255))
    plate.paste(photo, (0, 0))

    overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    ink = (16, 8, 12, 255)
    white = (255, 252, 246, 255)

    # Same face as HAPPY BIRTHDAY; two sizes bigger than the 42pt light pass.
    f_happy = font("Arial Rounded Bold.ttf", 90)
    f_name = font("Arial Rounded Bold.ttf", 90)
    f_reiki = font("Arial Rounded Bold.ttf", 44)
    f_foot = font("Arial Bold.ttf", 26)

    cx = SIZE / 2
    center_text(draw, (cx, 88), "HAPPY BIRTHDAY", f_happy, white)
    center_text(draw, (cx, 800), "DENEENE", f_name, white)
    center_text(draw, (cx, 886), "Reiki Share Free 3 to 5 PM", f_reiki, white)
    center_text(draw, (cx, 938), "Robert 12 to 5 PM", f_reiki, white)

    logo = Image.open(LOGO).convert("RGBA")
    logo_w = 118
    logo = logo.resize((logo_w, logo_w), Image.Resampling.LANCZOS)
    alpha = logo.split()[-1].point(lambda a: int(a * 0.88))
    logo.putalpha(alpha)
    overlay.paste(logo, (16, photo_h - logo_w - 12), logo)

    draw.rectangle((0, photo_h, SIZE, SIZE), fill=(255, 246, 228, 255))
    center_text(
        draw,
        (cx, photo_h + 22),
        "Chicagoland's #1   ·   shopsacredground.com   ·   847-749-3922",
        f_foot,
        ink,
    )

    out = Image.alpha_composite(plate, overlay).convert("RGB")
    out = out.filter(ImageFilter.UnsharpMask(radius=1.1, percent=70, threshold=2))
    out.save(OUT, quality=94)
    print(OUT)


if __name__ == "__main__":
    main()
