from __future__ import annotations

import os
import tempfile
import unittest
from datetime import date

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class WeekAheadVoiceTests(unittest.TestCase):
    def test_goodnight_caption_and_image_pool(self) -> None:
        from marketing import captions, images
        from marketing.models import Event

        pool = images.week_ahead_image_pool()
        self.assertEqual(len(pool), 3)
        self.assertTrue(all(u.startswith("https://shopsacredground.com/") for u in pool))
        url, rule = images.select_week_ahead_image(date(2026, 8, 2))
        self.assertIn(url, pool)
        self.assertEqual(rule, "week_ahead_pool")

        ev = Event(
            id=1,
            title="Tina’s Tarot",
            start_date="2026-08-03 12:00:00",
            end_date="2026-08-03 17:00:00",
            url="https://shopsacredground.com/tina/",
        )
        cap = captions.caption_week_ahead([ev], "facebook", date(2026, 8, 2))
        self.assertIn("good night", cap["text"].lower())
        self.assertIn("look forward", cap["text"].lower())
        self.assertIn("keep the lights on", cap["text"].lower())
        self.assertIn("Tomorrow is another day", cap["text"])
        self.assertIn("Tina’s Tarot", cap["text"])


class ComposeTests(unittest.TestCase):
    def test_contrast_and_footer(self) -> None:
        from marketing import compose

        dark = Image.new("RGB", (200, 200), (20, 20, 40))
        light = Image.new("RGB", (200, 200), (240, 235, 220))
        self.assertEqual(compose.text_color_for(dark)[1], "gold")
        self.assertEqual(compose.text_color_for(light)[1], "black")

        with tempfile.TemporaryDirectory() as td:
            bg = os.path.join(td, "bg.png")
            dark.save(bg)
            out = os.path.join(td, "out.png")
            meta = compose.compose_today_graphic(
                background_url=bg,
                events=[],
                day=date(2026, 8, 10),
                out_path=out,
            )
            self.assertTrue(os.path.exists(out))
            self.assertEqual(meta["contrast"], "gold")
            self.assertEqual(meta["footer"]["website"], "shopsacredground.com")
            self.assertEqual(meta["footer"]["phone"], "847-749-3922")
            self.assertEqual(meta["overlay"]["campaign_word"], "TODAY")
            with Image.open(out) as img:
                self.assertEqual(img.size[0], 1080)
                self.assertGreater(img.size[1], 1080)


if __name__ == "__main__":
    unittest.main()
