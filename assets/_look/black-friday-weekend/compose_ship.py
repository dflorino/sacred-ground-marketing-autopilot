#!/usr/bin/env python3
"""KEEP ship — unique BF/SBS plates for morning, 5pm, and 7pm."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageDraw

from compose_look import (
    BF_FLAG,
    CREAM,
    FOOTER_H,
    H,
    NIGHT_BOTH,
    PHOTO_H,
    SALE,
    SBS_FLAG,
    W,
    bold,
    cream_start,
    fit_cover,
    hang_pennant,
    medium,
    paste_logo,
)
from compose_sale_footer import SIX, compose as compose_afternoon

ROOT = Path(__file__).resolve().parents[3]
LOOK = Path(__file__).resolve().parent
SIX_DIR = LOOK / "six"

OFFER_SUFFIX = "-bf-offer.jpg"

MORNINGS = [
    ("2026-11-19", "sg-morning-flyer-2026-11-19-star-clean.jpg", "Thu Nov 19"),
    ("2026-11-20", "sg-morning-flyer-2026-11-20-moon-clean.jpg", "Fri Nov 20"),
    ("2026-11-21", "sg-morning-flyer-2026-11-21-vending.jpg", "Sat Nov 21"),
    ("2026-11-22", "sg-morning-flyer-2026-11-22-bookclub.jpg", "Sun Nov 22"),
    ("2026-11-23", "sg-morning-flyer-2026-11-23-chicago.jpg", "Mon Nov 23"),
    ("2026-11-24", "sg-morning-flyer-2026-11-24-lostfound.jpg", "Tue Nov 24"),
    ("2026-11-25", "sg-morning-flyer-2026-11-25-tsa.jpg", "Wed Nov 25"),
    ("2026-11-26", "sg-morning-flyer-2026-11-26-thanksgiving-closed.jpg", "Thu Nov 26"),
    ("2026-11-27", "sg-morning-flyer-2026-11-27-renaissance.jpg", "Fri Nov 27"),
    ("2026-11-28", "sg-morning-flyer-2026-11-28-purchases.jpg", "Sat Nov 28"),
]

AFTERNOONS = [
    (
        "2026-11-18",
        0,
        "Wed Nov 18  ·  #1 Chicagoland",
        "Educational Night",
        ["Free  ·  7:00–8:30 PM", "Tina  ·  until 6:00 PM"],
        "educational-night",
        "Educational Night is at 7.",
    ),
    (
        "2026-11-19",
        1,
        "Thu Nov 19  ·  #1 Chicagoland",
        "TarotHeads with Andre",
        ["Free  ·  7:00–9:00 PM", "Frequency Reset  ·  until 6:30 PM"],
        "tarotheads",
        "TarotHeads is at 7.",
    ),
    (
        "2026-11-20",
        2,
        "Fri Nov 20  ·  #1 Chicagoland",
        "Andre",
        ["Tarot  ·  6–10"],
        "andre",
        "Tonight the cards are already talking at Sacred Ground.",
    ),
    (
        "2026-11-21",
        3,
        "Sat Nov 21  ·  #1 Chicagoland",
        "Rose and Robert",
        ["Rose  ·  4–7", "Robert  ·  3–7:30"],
        "rose-robert",
        "Rose and Robert are here this evening.",
    ),
    (
        "2026-11-22",
        4,
        "Sun Nov 22  ·  #1 Chicagoland",
        "Sagittarius Season",
        ["The arrow already knows"],
        "sagittarius",
        "The arrow already knows. It points to Sacred Ground.",
    ),
    (
        "2026-11-23",
        5,
        "Mon Nov 23  ·  #1 Chicagoland",
        "Karen",
        ["Past life regression  ·  6–10"],
        "past-life",
        "Past life regression is at 6.",
    ),
    (
        "2026-11-24",
        0,
        "Tue Nov 24  ·  #1 Chicagoland",
        "Gemini Supermoon",
        ["Tonight  ·  stand under it here"],
        "supermoon",
        "Closer than it looks. Stand under it at Sacred Ground.",
    ),
    (
        "2026-11-25",
        1,
        "Wed Nov 25  ·  #1 Chicagoland",
        "Lita",
        ["Tarot & pendulum  ·  until 5"],
        "lita",
        "Lita is here until 5.",
    ),
    (
        "2026-11-27",
        2,
        "Fri Nov 27  ·  #1 Chicagoland",
        "Tina and Lisa Maria",
        ["Tina  ·  until 7", "Lisa Maria  ·  until 6"],
        "tina-lisa",
        "Tina and Lisa Maria are here this evening.",
    ),
    (
        "2026-11-28",
        3,
        "Sat Nov 28  ·  #1 Chicagoland",
        "Deep Rest",
        ["7:00–9:00 PM", "Robert  ·  until 7:30"],
        "deep-rest",
        "Deep Rest is at 7.",
    ),
]

NIGHT_SRC = [
    "sg-night-creative-fall-store-harvest-moonlight-noglyph.png",
    "sg-night-creative-fall-store-fairy-lights-noglyph.png",
    "sg-night-creative-fall-store-blue-hour-noglyph.png",
    "sg-night-creative-fall-store-frost-sparkle-noglyph.png",
    "sg-night-creative-fall-store-oak-sidewalk-noglyph.png",
    "sg-night-creative-fall-store-cozy-upstairs-noglyph.png",
    "sg-night-creative-fall-store-crescent-venus-noglyph.png",
    "sg-night-creative-fall-store-rain-puddles-noglyph.png",
    "sg-night-creative-fall-store-bonfire-street-noglyph.png",
    "sg-night-creative-fall-store-star-trails-noglyph.png",
    "sg-night-creative-fall-store-pumpkin-porch.png",
]

NIGHT_DAYS = [
    date(2026, 11, 18),
    date(2026, 11, 19),
    date(2026, 11, 20),
    date(2026, 11, 21),
    date(2026, 11, 22),
    date(2026, 11, 23),
    date(2026, 11, 24),
    date(2026, 11, 25),
    date(2026, 11, 26),
    date(2026, 11, 27),
    date(2026, 11, 28),
]


def date_line(short: str) -> str:
    return f"{short}  ·  #1 Chicagoland"


def two_day_line(day: date) -> str:
    a = day + timedelta(days=1)
    b = day + timedelta(days=2)
    return f"{a.strftime('%a')} + {b.strftime('%a')}  ·  #1 Chicagoland"


def morning_flag_lines(ymd: str) -> list[str]:
    return SBS_FLAG if ymd == "2026-11-28" else BF_FLAG


def night_flag_lines(day: date) -> list[str]:
    if day == date(2026, 11, 28):
        return SBS_FLAG
    if day == date(2026, 11, 27):
        return BF_FLAG
    return NIGHT_BOTH


def stamp_morning(src: Path, dest: Path, ymd: str, short: str) -> Path:
    src_im = Image.open(src).convert("RGB")
    if ymd == "2026-11-26":
        photo = src_im.crop((0, 0, src_im.width, cream_start(src_im)))
        photo = fit_cover(photo, W, PHOTO_H)
        im = Image.new("RGB", (W, H), CREAM)
        im.paste(photo, (0, 0))
        hang_pennant(
            im, morning_flag_lines(ymd), photo_h=PHOTO_H, top=72, wide=300, tall=210
        )
        draw = ImageDraw.Draw(im)
        draw.rectangle((0, PHOTO_H, W, H), fill=CREAM)
        rows = [
            (medium(22), date_line(short)),
            (bold(32), "We're closed  ·  Happy Thanksgiving"),
            (medium(18), "shopsacredground.com  ·  847-749-3922"),
        ]
        heights = []
        for fnt, text in rows:
            b = draw.textbbox((0, 0), text, font=fnt)
            heights.append(b[3] - b[1])
        gap = 8
        block = sum(heights) + gap * (len(rows) - 1)
        y = PHOTO_H + (FOOTER_H - block) // 2
        for (fnt, text), hh in zip(rows, heights):
            b = draw.textbbox((0, 0), text, font=fnt)
            x = (W - (b[2] - b[0])) / 2
            draw.text((x, y - b[1]), text, font=fnt, fill=(18, 14, 12))
            y += hh + gap
    else:
        im = src_im
        photo_h = cream_start(im)
        hang_pennant(
            im, morning_flag_lines(ymd), photo_h=photo_h, top=72, wide=300, tall=210
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, quality=93, optimize=True)
    return dest


def compose_night(src: Path, dest: Path, day: date) -> Path:
    photo = fit_cover(Image.open(src), W, PHOTO_H)
    canvas = Image.new("RGB", (W, H), CREAM)
    canvas.paste(photo, (0, 0))
    draw = ImageDraw.Draw(canvas)
    gn = bold(48)
    line = "Goodnight."
    box = draw.textbbox((0, 0), line, font=gn)
    x = (W - (box[2] - box[0])) / 2
    draw.text((x, 42 - box[1]), line, font=gn, fill=(255, 255, 255))
    lines = night_flag_lines(day)
    kwargs = {"photo_h": PHOTO_H, "top": 12, "angle": -10.0, "wide": 300, "tall": 210}
    if len(lines) >= 4:
        kwargs.update(wide=320, tall=236)
    hang_pennant(canvas, lines, **kwargs)
    paste_logo(canvas, PHOTO_H)
    y0 = PHOTO_H
    draw.rectangle((0, y0, W, H), fill=CREAM)
    rows = [
        (medium(24), two_day_line(day)),
        (medium(20), "shopsacredground.com  ·  847-749-3922"),
    ]
    heights = []
    for fnt, text in rows:
        b = draw.textbbox((0, 0), text, font=fnt)
        heights.append(b[3] - b[1])
    gap = 8
    block = sum(heights) + gap * (len(rows) - 1)
    y = y0 + (FOOTER_H - block) // 2
    for (fnt, text), hh in zip(rows, heights):
        b = draw.textbbox((0, 0), text, font=fnt)
        x = (W - (b[2] - b[0])) / 2
        draw.text((x, y - b[1]), text, font=fnt, fill=(18, 14, 12))
        y += hh + gap
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, quality=93, optimize=True)
    return dest


def sale_caption_body(ymd: str) -> str:
    if ymd >= "2026-11-28":
        lead = "Small Business Saturday"
    else:
        lead = "Black Friday sales"
    return (
        f"{lead}: 20% off while supplies last.\n"
        "Come as you are — Arlington Heights.\n"
        "https://shopsacredground.com/"
    )


def main() -> None:
    manifest: list[dict] = []

    for ymd, fname, short in MORNINGS:
        dest = ROOT / f"assets/sg-morning-flyer-{ymd}{OFFER_SUFFIX}"
        stamp_morning(ROOT / "assets" / fname, dest, ymd, short)
        manifest.append(
            {
                "slot": "morning",
                "date": ymd,
                "local": str(dest.relative_to(ROOT)),
                "title": f"SG morning {ymd} Black Friday",
            }
        )
        print("am", dest.name, dest.stat().st_size)

    for ymd, idx, dline, name, details, slug, opener in AFTERNOONS:
        dest = ROOT / f"assets/sg-afternoon-spotlight-{ymd}-bf-offer-{slug}.jpg"
        compose_afternoon(SIX_DIR / SIX[idx], dest, dline, name, details)
        manifest.append(
            {
                "slot": "afternoon",
                "date": ymd,
                "local": str(dest.relative_to(ROOT)),
                "title": f"SG afternoon {ymd} Black Friday {slug}",
                "label": name,
                "caption_opener": opener,
                "caption_body": sale_caption_body(ymd),
            }
        )
        print("5pm", dest.name, dest.stat().st_size)

    for i, day in enumerate(NIGHT_DAYS):
        dest = ROOT / f"assets/sg-night-{day.isoformat()}{OFFER_SUFFIX}"
        compose_night(ROOT / "assets" / NIGHT_SRC[i], dest, day)
        if day.isoformat() >= "2026-11-28":
            opener = "Small Business Saturday: 20% off while supplies last."
        else:
            opener = "Black Friday sales: 20% off while supplies last."
        manifest.append(
            {
                "slot": "night",
                "date": day.isoformat(),
                "local": str(dest.relative_to(ROOT)),
                "title": f"SG night {day.isoformat()} Black Friday",
                "id": f"bf_night_{day.isoformat()}",
                "label": "Black Friday / Small Business Saturday night flag",
                "caption_opener": opener,
            }
        )
        print("7pm", dest.name, dest.stat().st_size)

    out = LOOK / "ship-manifest.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n")
    print("manifest", len(manifest), out)


if __name__ == "__main__":
    main()
