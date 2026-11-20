#!/usr/bin/env python3
"""Wire KEEP Black Friday plates into Autopilot configs."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WP = "https://shopsacredground.com/wp-content/uploads"
NOTE = (
    "Founder Nov 19: 20% off while supplies last lives on the Black Friday / "
    "Small Business Saturday talk, not the cream banner. Unique URL. Do not reuse old KEEP."
)
STAMP = "2026-11-19T21:55:00-06:00"
SALE_OPENER = "Black Friday sales: 20% off while supplies last."
SBS_OPENER = "Small Business Saturday: 20% off while supplies last."
SALE_BODY = (
    "Black Friday sales: 20% off while supplies last.\n"
    "Come as you are — Arlington Heights.\n"
    "https://shopsacredground.com/"
)
SBS_BODY = (
    "Small Business Saturday: 20% off while supplies last.\n"
    "Come as you are — Arlington Heights.\n"
    "https://shopsacredground.com/"
)

MORNINGS = {
    "2026-11-20": ("sg-morning-flyer-2026-11-20-bf-offer.jpg", 35798),
    "2026-11-21": ("sg-morning-flyer-2026-11-21-bf-offer.jpg", 35799),
    "2026-11-22": ("sg-morning-flyer-2026-11-22-bf-offer.jpg", 35801),
    "2026-11-23": ("sg-morning-flyer-2026-11-23-bf-offer.jpg", 35800),
    "2026-11-24": ("sg-morning-flyer-2026-11-24-bf-offer.jpg", 35802),
    "2026-11-25": ("sg-morning-flyer-2026-11-25-bf-offer.jpg", 35803),
    "2026-11-26": ("sg-morning-flyer-2026-11-26-bf-offer.jpg", 35804),
    "2026-11-27": ("sg-morning-flyer-2026-11-27-bf-offer.jpg", 35805),
    "2026-11-28": ("sg-morning-flyer-2026-11-28-bf-offer.jpg", 35806),
}

AFTERNOONS = {
    "2026-11-20": ("sg-afternoon-spotlight-2026-11-20-bf-offer-andre.jpg", 35807, "Andre — cards already talking", "Tonight the cards are already talking at Sacred Ground."),
    "2026-11-21": ("sg-afternoon-spotlight-2026-11-21-bf-offer-rose-robert.jpg", 35808, "Rose and Robert", "Rose and Robert are here this evening."),
    "2026-11-22": ("sg-afternoon-spotlight-2026-11-22-bf-offer-sagittarius.jpg", 35809, "Sagittarius Season Begins", "The arrow already knows. It points to Sacred Ground."),
    "2026-11-23": ("sg-afternoon-spotlight-2026-11-23-bf-offer-past-life.jpg", 35810, "Karen past life regression", "Past life regression is at 6."),
    "2026-11-24": ("sg-afternoon-spotlight-2026-11-24-bf-offer-supermoon.jpg", 35811, "Full Moon / Supermoon", "Closer than it looks. Stand under it at Sacred Ground."),
    "2026-11-25": ("sg-afternoon-spotlight-2026-11-25-bf-offer-lita.jpg", 35812, "Lita tarot and pendulum", "Lita is here until 5."),
    "2026-11-27": ("sg-afternoon-spotlight-2026-11-27-bf-offer-tina-lisa.jpg", 35813, "Tina and Lisa Maria", "Tina and Lisa Maria are here this evening."),
    "2026-11-28": ("sg-afternoon-spotlight-2026-11-28-bf-offer-deep-rest.jpg", 35814, "Deep Rest", "Deep Rest is at 7."),
}

NIGHTS = {
    "2026-11-20": 35817,
    "2026-11-21": 35816,
    "2026-11-22": 35815,
    "2026-11-23": 35818,
    "2026-11-24": 35819,
    "2026-11-25": 35820,
    "2026-11-26": 35821,
    "2026-11-27": 35823,
    "2026-11-28": 35822,
}


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def wire_mornings() -> None:
    path = ROOT / "config/morning_flyers.json"
    data = json.loads(path.read_text())
    flyers = data["flyers"]
    for ymd, (fname, media_id) in MORNINGS.items():
        row = flyers[ymd]
        prior = row.get("media_id")
        row["local"] = f"assets/{fname}"
        row["url"] = f"{WP}/{fname}"
        row["replaced_media_id"] = prior
        row["media_id"] = media_id
        row["prebranded"] = True
        row["pride_baked_in"] = True
        row["status"] = "founder_approved"
        row["founder_approved"] = True
        row["do_not_publish"] = False
        row["awaiting_founder_review"] = False
        row["locked_until_founder_review"] = False
        row["do_not_remake"] = True
        row["updated_at"] = STAMP
        row["note"] = NOTE
        row["caption_sale"] = SBS_OPENER if ymd >= "2026-11-28" else SALE_OPENER
    dump(path, data)


def wire_afternoons() -> None:
    path = ROOT / "config/afternoon_spotlight_plates.json"
    data = json.loads(path.read_text())
    plates = data["plates"]
    for ymd, (fname, media_id, label, opener) in AFTERNOONS.items():
        row = plates[ymd]
        prior = row.get("media_id")
        prior_url = row.get("url")
        row["label"] = label
        row["local"] = f"assets/{fname}"
        row["url"] = f"{WP}/{fname}"
        row["replaced_media_id"] = prior
        row["prior_url"] = prior_url
        row["media_id"] = media_id
        row["prebranded"] = True
        row["pride_baked_in"] = True
        row["do_not_publish"] = False
        row["founder_approved"] = True
        row["status"] = "founder_approved"
        row["do_not_remake"] = True
        row["founder_approved_at"] = STAMP
        row["updated_at"] = STAMP
        row["caption_opener"] = opener
        row["caption_body"] = SBS_BODY if ymd >= "2026-11-28" else SALE_BODY
        row["note"] = NOTE + " Event info in cream. 20% sits on the sale photo with Black Friday / Small Business Saturday."
    dump(path, data)


def wire_nights() -> None:
    path = ROOT / "config/image_atmosphere.json"
    data = json.loads(path.read_text())
    plates = data["nighttime"]["date_plates"]
    for ymd, media_id in NIGHTS.items():
        fname = f"sg-night-{ymd}-bf-offer.jpg"
        plates[ymd] = {
            "id": f"bf_night_{ymd}",
            "label": "Black Friday / Small Business Saturday night flag",
            "mode": "creative",
            "url": f"{WP}/{fname}",
            "local": f"assets/{fname}",
            "media_id": media_id,
            "prebranded": True,
            "pride_baked_in": True,
            "do_not_remake": True,
            "founder_approved": True,
            "founder_approved_at": STAMP,
            "caption_opener": SBS_OPENER if ymd >= "2026-11-28" else SALE_OPENER,
            "note": NOTE,
        }
    prior_note = str(data["nighttime"].get("date_plates_note") or "").rstrip()
    extra = (
        " Founder Nov 19: remaining night flags Nov 20–28 put 20% off while supplies last "
        "on the Black Friday / Small Business Saturday tag, not the cream. Date plates win over pool."
    )
    if extra.strip() not in prior_note:
        data["nighttime"]["date_plates_note"] = (prior_note + extra).strip()
    dump(path, data)


def main() -> None:
    wire_mornings()
    wire_afternoons()
    wire_nights()
    print("wired mornings", len(MORNINGS))
    print("wired afternoons", len(AFTERNOONS))
    print("wired nights", len(NIGHTS))


if __name__ == "__main__":
    main()
