"""Celestial dual cadence — night-before + morning-of."""
from __future__ import annotations

import unittest
from datetime import date

from marketing.atmosphere import atmosphere_config, nighttime_plan
from marketing.captions import caption_today, caption_week_ahead
from marketing.celestial import (
    celestial_config,
    celestial_morning_for,
    celestial_night_for,
    morning_plan,
    night_plan,
    schedule_rows,
)
from marketing.images import select_today_image


class CelestialCadenceTests(unittest.TestCase):
    def setUp(self) -> None:
        celestial_config.cache_clear()
        atmosphere_config.cache_clear()

    def test_schedule_has_ten_events(self) -> None:
        rows = schedule_rows()
        self.assertEqual(len(rows), 10)
        self.assertEqual(rows[0]["night_before"], "2026-08-11")
        self.assertEqual(rows[0]["morning_of"], "2026-08-12")

    def test_night_before_eclipse_and_perseids(self) -> None:
        n = night_plan(date(2026, 8, 11), platform="facebook")
        self.assertIsNotNone(n)
        assert n is not None
        self.assertEqual(n["id"], "solar_eclipse_leo_2026")
        self.assertIn("solar-eclipse", n["image_url"])
        self.assertIn("tomorrow", n["caption_opener"].lower())

        p = nighttime_plan(date(2026, 8, 11), platform="facebook")
        self.assertEqual(p["mode"], "celestial")
        self.assertEqual(p["celestial"], "solar_eclipse_leo_2026")

        # Next night is Perseids (not eclipse day plate)
        n2 = night_plan(date(2026, 8, 12), platform="facebook")
        self.assertIsNotNone(n2)
        assert n2 is not None
        self.assertEqual(n2["id"], "perseids_peak_2026")

    def test_morning_of_wins_image(self) -> None:
        m = morning_plan(date(2026, 8, 12), platform="facebook")
        self.assertIsNotNone(m)
        assert m is not None
        self.assertEqual(m["id"], "solar_eclipse_leo_2026")
        url, rule, _ = select_today_image([], date(2026, 8, 12), platform="facebook")
        self.assertEqual(rule, "celestial_morning")
        self.assertEqual(url, m["image_url"])

    def test_captions_tomorrow_and_today(self) -> None:
        night_cap = caption_week_ahead([], "facebook", date(2026, 8, 11))
        self.assertIn("solar eclipse", night_cap["hook"].lower())
        self.assertIn("leo", night_cap["hook"].lower())

        morning_cap = caption_today(
            [],
            "facebook",
            date(2026, 8, 13),
            today_events=[],
            publish_day=date(2026, 8, 12),
        )
        self.assertIn("solar eclipse", morning_cap["hook"].lower())

        perseids_night = caption_week_ahead([], "instagram", date(2026, 8, 12))
        self.assertIn("perseids", perseids_night["hook"].lower())

    def test_samhain_beats_generic_on_night_before(self) -> None:
        hit = celestial_night_for(date(2026, 10, 30))
        self.assertIsNotNone(hit)
        assert hit is not None
        self.assertEqual(hit[0], "samhain_2026")
        plan = nighttime_plan(date(2026, 10, 30))
        self.assertEqual(plan["mode"], "celestial")

    def test_helpers_match_event_dates(self) -> None:
        # Aug 12 is Perseids night-before AND eclipse morning-of (adjacent events).
        self.assertEqual(celestial_night_for(date(2026, 8, 12))[0], "perseids_peak_2026")
        self.assertEqual(celestial_morning_for(date(2026, 8, 12))[0], "solar_eclipse_leo_2026")
        self.assertIsNone(celestial_morning_for(date(2026, 8, 11)))
        # Non-celestial ordinary night
        self.assertIsNone(celestial_night_for(date(2026, 8, 20)))


if __name__ == "__main__":
    unittest.main()
