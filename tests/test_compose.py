from __future__ import annotations

import os
import tempfile
import unittest
from datetime import date

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


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
