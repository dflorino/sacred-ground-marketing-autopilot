"""Founder Nov 18 KEEP — Black Friday / Small Business Saturday clock."""

from __future__ import annotations

import json
import os
import unittest
from datetime import date

from marketing.atmosphere import atmosphere_config, nighttime_plan
from marketing.captions import caption_today
from marketing.images import _afternoon_plate_for_day, afternoon_spotlight_plates
from marketing.models import Event
from marketing.morning_flyers import (
    flyer_entry_for_day,
    flyer_has_leftover_stacked_cream,
)


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BlackFridayWeekendTests(unittest.TestCase):
    def test_mornings_nov19_28_are_unique_bf_urls(self) -> None:
        urls = []
        for day in (
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
        ):
            entry = flyer_entry_for_day(day) or {}
            url = str(entry.get("url") or "")
            local = os.path.join(ROOT, str(entry.get("local") or ""))
            self.assertTrue(entry.get("founder_approved"), day)
            if day >= date(2026, 11, 22):
                self.assertIn("-bf-flag.jpg", url, day)
                self.assertIn("15 to 20% off", str(entry.get("caption_sale") or ""))
            elif day >= date(2026, 11, 20):
                self.assertIn("-bf-offer.jpg", url, day)
                self.assertIn("20% off while supplies last", str(entry.get("caption_sale") or ""))
            else:
                self.assertIn("-bf.jpg", url, day)
                self.assertIn("20% off while supplies last", str(entry.get("caption_sale") or ""))
            self.assertTrue(os.path.isfile(local), local)
            self.assertFalse(flyer_has_leftover_stacked_cream(local), local)
            urls.append(url)
        self.assertEqual(len(urls), len(set(urls)))
        sat = flyer_entry_for_day(date(2026, 11, 28)) or {}
        self.assertIn("Small Business Saturday", str(sat.get("caption_sale") or ""))
        self.assertIn("15 to 20% off", str(sat.get("caption_sale") or ""))

    def test_afternoons_rotate_sale_photos_and_skip_thanksgiving(self) -> None:
        skips = afternoon_spotlight_plates().get("skip_publish_dates") or []
        self.assertIn("2026-11-26", skips)
        self.assertIsNone(_afternoon_plate_for_day(date(2026, 11, 26)))
        urls = []
        for day in (
            date(2026, 11, 18),
            date(2026, 11, 19),
            date(2026, 11, 20),
            date(2026, 11, 21),
            date(2026, 11, 22),
            date(2026, 11, 23),
            date(2026, 11, 24),
            date(2026, 11, 25),
            date(2026, 11, 27),
            date(2026, 11, 28),
        ):
            plate = _afternoon_plate_for_day(day) or {}
            url = str(plate.get("url") or "")
            local = os.path.join(ROOT, str(plate.get("local") or ""))
            self.assertTrue(plate.get("founder_approved"), day)
            if day >= date(2026, 11, 21):
                self.assertIn("-bf-flag-", url, day)
                self.assertIn("15 to 20% off", str(plate.get("caption_body") or ""))
            elif day >= date(2026, 11, 20):
                self.assertIn("-bf-offer-", url, day)
                self.assertIn("20% off while supplies last", str(plate.get("caption_body") or ""))
            else:
                self.assertIn("-bf-", url, day)
                self.assertIn("20% off while supplies last", str(plate.get("caption_body") or ""))
            self.assertTrue(os.path.isfile(local), local)
            urls.append(url)
        self.assertEqual(len(urls), len(set(urls)))
        self.assertIn("educational-night", urls[0])

    def test_nights_nov18_28_are_date_plates(self) -> None:
        atmosphere_config.cache_clear()
        urls = []
        for day in (
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
        ):
            plan = nighttime_plan(day)
            url = str(plan.get("image_url") or "")
            self.assertTrue(plan.get("prebranded"), day)
            if day >= date(2026, 11, 21):
                self.assertIn(f"sg-night-{day.isoformat()}-bf-flag.jpg", url, day)
            elif day >= date(2026, 11, 20):
                self.assertIn(f"sg-night-{day.isoformat()}-bf-offer.jpg", url, day)
            else:
                self.assertIn(f"sg-night-{day.isoformat()}-bf.jpg", url, day)
            plate = ((atmosphere_config().get("nighttime") or {}).get("date_plates") or {}).get(
                day.isoformat()
            )
            opener = str((plate or {}).get("caption_opener") or "")
            if day >= date(2026, 11, 21):
                self.assertIn("15 to 20% off", opener)
            else:
                self.assertIn("20% off while supplies last", opener)
            urls.append(url)
        self.assertEqual(len(urls), len(set(urls)))

    def test_morning_caption_includes_sale_line(self) -> None:
        day = date(2026, 11, 19)
        ev = Event(
            id=1,
            title="Tarot with Adie",
            start_date="2026-11-19 12:00:00",
            end_date="2026-11-19 17:00:00",
            url="https://shopsacredground.com/book/adie/",
        )
        text = caption_today(
            [],
            "facebook",
            day,
            today_events=[ev],
            publish_day=day,
        )["text"]
        self.assertIn("20% off while supplies last", text)

    def test_afternoon_json_keeps_thanksgiving_skip(self) -> None:
        path = os.path.join(ROOT, "config/afternoon_spotlight_plates.json")
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertIn("2026-11-26", data.get("skip_publish_dates") or [])
        self.assertNotIn("2026-11-26", data.get("plates") or {})


if __name__ == "__main__":
    unittest.main()
