#!/usr/bin/env python3
"""Paint correct, readable type onto the Sep 13 / Sep 17 afternoon remakes."""
from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    paths = (
        (
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
            if bold
            else "/System/Library/Fonts/Supplemental/Arial.ttf"
        ),
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    )
    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def sep13() -> str:
    src = os.path.join(ROOT, "assets/_next7_review/src-sep13-afternoon.jpg")
    dest = os.path.join(ROOT, "assets/sg-afternoon-spotlight-2026-09-13-lisa-maria.jpg")
    im = Image.open(src).convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")
    # Cover the whole original headline column, including leftover AI type.
    d.rectangle([0, 0, 1024, 500], fill=(24, 14, 24, 236))

    cream = (247, 241, 228)
    gold = (232, 196, 96)
    d.text((512, 56), "SACRED GROUND PRESENTS", font=font(26, True), fill=cream, anchor="mt")
    d.text((512, 106), "LISA MARIA", font=font(72, True), fill=gold, anchor="mt")
    d.text((512, 200), "INTUITIVE TAROT", font=font(32, True), fill=cream, anchor="mt")
    d.text((512, 250), "MONDAY  ·  12 PM – 5 PM", font=font(26, True), fill=cream, anchor="mt")
    d.text((512, 294), "Arlington Heights", font=font(22, False), fill=(210, 198, 178), anchor="mt")
    d.text(
        (512, 360),
        "Chicagoland's #1 Crystal Shop & Holistic Center",
        font=font(20, True),
        fill=gold,
        anchor="mt",
    )

    im.convert("RGB").save(dest, "JPEG", quality=93)
    return dest


def sep17() -> str:
    src = os.path.join(ROOT, "assets/_next7_review/src-sep17-afternoon.jpg")
    dest = os.path.join(ROOT, "assets/sg-afternoon-spotlight-2026-09-17-tarotheads-andre.jpg")
    im = Image.open(src).convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")
    # Cover the whole title band down to the cream footer.
    d.rectangle([0, 600, 1024, 868], fill=(32, 20, 40, 255))

    cream = (247, 241, 228)
    gold = (232, 196, 96)
    d.text((512, 628), "TAROTHEADS WITH ANDRE", font=font(46, True), fill=cream, anchor="mt")
    d.text((512, 698), "FREE COMMUNITY EVENT", font=font(28, True), fill=gold, anchor="mt")
    d.text(
        (512, 748),
        "THURSDAY  ·  7 PM – 9 PM  ·  Arlington Heights",
        font=font(22, True),
        fill=cream,
        anchor="mt",
    )

    im.convert("RGB").save(dest, "JPEG", quality=93)
    return dest


if __name__ == "__main__":
    print(sep13())
    print(sep17())
