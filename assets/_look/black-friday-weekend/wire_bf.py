#!/usr/bin/env python3
"""Wire KEEP Black Friday plates into Autopilot configs."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WP = "https://shopsacredground.com/wp-content/uploads"
NOTE = (
    "Founder Nov 18 KEEP: Black Friday / Small Business Saturday. "
    "20% off while supplies last in cream. Unique URL. Do not reuse old KEEP."
)
STAMP = "2026-11-18T10:30:00-06:00"
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
    "2026-11-19": ("sg-morning-flyer-2026-11-19-bf.jpg", 35734),
    "2026-11-20": ("sg-morning-flyer-2026-11-20-bf.jpg", 35737),
    "2026-11-21": ("sg-morning-flyer-2026-11-21-bf.jpg", 35739),
    "2026-11-22": ("sg-morning-flyer-2026-11-22-bf.jpg", 35745),
    "2026-11-23": ("sg-morning-flyer-2026-11-23-bf.jpg", 35747),
    "2026-11-24": ("sg-morning-flyer-2026-11-24-bf.jpg", 35748),
    "2026-11-25": ("sg-morning-flyer-2026-11-25-bf.jpg", 35752),
    "2026-11-26": ("sg-morning-flyer-2026-11-26-bf.jpg", 35756),
    "2026-11-27": ("sg-morning-flyer-2026-11-27-bf.jpg", 35758),
    "2026-11-28": ("sg-morning-flyer-2026-11-28-bf.jpg", 35761),
}

AFTERNOONS = {
    "2026-11-18": ("sg-afternoon-spotlight-2026-11-18-bf-educational-night.jpg", 35732, "Educational Night", "Educational Night is at 7."),
    "2026-11-19": ("sg-afternoon-spotlight-2026-11-19-bf-tarotheads.jpg", 35736, "TarotHeads with Andre", "TarotHeads is at 7."),
    "2026-11-20": ("sg-afternoon-spotlight-2026-11-20-bf-andre.jpg", 35738, "Andre — cards already talking", "Tonight the cards are already talking at Sacred Ground."),
    "2026-11-21": ("sg-afternoon-spotlight-2026-11-21-bf-rose-robert.jpg", 35741, "Rose and Robert", "Rose and Robert are here this evening."),
    "2026-11-22": ("sg-afternoon-spotlight-2026-11-22-bf-sagittarius.jpg", 35743, "Sagittarius Season Begins", "The arrow already knows. It points to Sacred Ground."),
    "2026-11-23": ("sg-afternoon-spotlight-2026-11-23-bf-past-life.jpg", 35746, "Karen past life regression", "Past life regression is at 6."),
    "2026-11-24": ("sg-afternoon-spotlight-2026-11-24-bf-supermoon.jpg", 35750, "Full Moon / Supermoon", "Closer than it looks. Stand under it at Sacred Ground."),
    "2026-11-25": ("sg-afternoon-spotlight-2026-11-25-bf-lita.jpg", 35753, "Lita tarot and pendulum", "Lita is here until 5."),
    "2026-11-27": ("sg-afternoon-spotlight-2026-11-27-bf-tina-lisa.jpg", 35757, "Tina and Lisa Maria", "Tina and Lisa Maria are here this evening."),
    "2026-11-28": ("sg-afternoon-spotlight-2026-11-28-bf-deep-rest.jpg", 35760, "Deep Rest", "Deep Rest is at 7."),
}

NIGHTS = {
    "2026-11-18": 35733,
    "2026-11-19": 35735,
    "2026-11-20": 35740,
    "2026-11-21": 35742,
    "2026-11-22": 35744,
    "2026-11-23": 35749,
    "2026-11-24": 35751,
    "2026-11-25": 35754,
    "2026-11-26": 35755,
    "2026-11-27": 35759,
    "2026-11-28": 35762,
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
        row["note"] = NOTE + " Event info in cream. Sale photo is the 5pm whole thing."
    dump(path, data)


def wire_nights() -> None:
    path = ROOT / "config/image_atmosphere.json"
    data = json.loads(path.read_text())
    plates = data["nighttime"]["date_plates"]
    for ymd, media_id in NIGHTS.items():
        fname = f"sg-night-{ymd}-bf.jpg"
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
        " Founder Nov 18 KEEP: Black Friday / Small Business Saturday night flags "
        "Nov 18–28 with 20% off while supplies last in cream. Date plates win over pool."
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
