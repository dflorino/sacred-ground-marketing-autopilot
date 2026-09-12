#!/usr/bin/env python3
"""Build one review contact sheet per day (morning / afternoon / night)."""
from __future__ import annotations

import json
import os
import sys
from datetime import date

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW = os.path.join(ROOT, "assets", "_next7_review")

CELL = 620
PAD = 26
HEAD = 96
LABEL = 104
BG = (26, 22, 34)
CREAM = (247, 241, 228)
GOLD = (226, 178, 92)
MUTED = (168, 158, 178)
RED = (232, 108, 108)

SLOTS = [
    ("morning", "MORNING  ·  9:00 AM"),
    ("afternoon", "AFTERNOON  ·  5:00 PM"),
    ("night", "NIGHT  ·  7:00 PM"),
]


def font(size, bold=False):
    names = (
        ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"]
        if bold
        else ["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc"]
    )
    for n in names:
        if os.path.exists(n):
            try:
                return ImageFont.truetype(n, size)
            except Exception:
                pass
    return ImageFont.load_default()


def fit(path, box):
    im = Image.open(path).convert("RGB")
    im.thumbnail((box, box), Image.LANCZOS)
    canvas = Image.new("RGB", (box, box), (14, 12, 18))
    canvas.paste(im, ((box - im.width) // 2, (box - im.height) // 2))
    return canvas


def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    man = json.load(open(os.path.join(REVIEW, "manifest.json")))
    by_day = {}
    for m in man:
        by_day.setdefault(m["date"], {})[m["slot"]] = m

    made = []
    for day_key in sorted(by_day):
        row = by_day[day_key]
        w = PAD + (CELL + PAD) * 3
        h = HEAD + CELL + LABEL + PAD
        sheet = Image.new("RGB", (w, h), BG)
        d = ImageDraw.Draw(sheet)

        dt = date.fromisoformat(day_key)
        d.text((PAD, 24), dt.strftime("%A, %B %-d, %Y").upper(), font=font(40, True), fill=CREAM)
        d.text(
            (w - PAD - 300, 34),
            "YES / NO on each plate",
            font=font(24),
            fill=MUTED,
        )

        for i, (slot, title) in enumerate(SLOTS):
            x = PAD + (CELL + PAD) * i
            info = row.get(slot) or {}
            path = info.get("file")
            if path and os.path.exists(path):
                sheet.paste(fit(path, CELL), (x, HEAD))
            else:
                d.rectangle([x, HEAD, x + CELL, HEAD + CELL], fill=(48, 26, 30))
                d.text(
                    (x + 30, HEAD + CELL // 2 - 30),
                    "NO IMAGE PLANNED",
                    font=font(34, True),
                    fill=RED,
                )
                d.text(
                    (x + 30, HEAD + CELL // 2 + 16),
                    (info.get("rule") or "").replace("_", " "),
                    font=font(24),
                    fill=MUTED,
                )

            y = HEAD + CELL + 14
            d.text((x, y), title, font=font(27, True), fill=GOLD)
            rule = (info.get("rule") or "—").replace("_", " ")
            d.text((x, y + 34), f"rule: {rule}", font=font(21), fill=CREAM)
            evs = info.get("events") or []
            sub = "; ".join(evs) if evs else "no event — general shop plate"
            for j, line in enumerate(wrap(d, sub, font(19), CELL)[:2]):
                d.text((x, y + 62 + j * 22), line, font=font(19), fill=MUTED)

        out = os.path.join(REVIEW, f"sheet-{day_key}.jpg")
        sheet.save(out, "JPEG", quality=88)
        made.append(out)
        print(out)

    return made


if __name__ == "__main__":
    main()
