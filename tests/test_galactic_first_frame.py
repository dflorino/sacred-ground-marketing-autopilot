"""S1E17 Martian first-frame engine — lock the bar and fail closed on new rolls."""
from __future__ import annotations

import unittest

from marketing.galactic_first_frame import (
    engine,
    mute_first_frame_gate,
    opener_kind,
    will_block_new_roll,
)


class GalacticFirstFrameTests(unittest.TestCase):
    def test_engine_bar_is_s1e17(self) -> None:
        bar = engine()
        self.assertEqual(bar.get("bar_episode"), "s1e17")
        self.assertEqual(bar.get("bar_media_id"), 34919)
        self.assertEqual(bar.get("bar_plate_id"), 34909)
        ig = bar.get("instagram") or {}
        self.assertEqual(ig.get("views"), 2202)
        self.assertEqual(ig.get("skip_rate"), 28.0)
        self.assertEqual(bar.get("contrast_episode"), "s1e16")
        self.assertEqual(bar.get("contrast_skip_rate"), 52.5)

    def test_s1e17_opener_is_discovery(self) -> None:
        self.assertEqual(
            opener_kind("We've found them. Actual Martians."),
            "discovery",
        )

    def test_s1e16_opener_is_location(self) -> None:
        self.assertEqual(opener_kind("We've landed on Mars."), "location")

    def test_new_roll_blocks_landscape_arrival(self) -> None:
        blocks = will_block_new_roll(
            "We've landed on Mars.",
            punch_visible=False,
            keep_locked=False,
        )
        self.assertIn("opener_is_location_not_discovery", blocks)
        self.assertIn("first_frame_punch_missing", blocks)

    def test_keep_locked_never_blocks(self) -> None:
        blocks = will_block_new_roll(
            "Just think! We've collected crystals from all across the solar system!",
            punch_visible=False,
            keep_locked=True,
        )
        self.assertEqual(blocks, [])

    def test_martian_punch_passes(self) -> None:
        gate = mute_first_frame_gate(
            punch_one_liner="Martians already on the cliff looking down at the climb",
            opener="We've found them. Actual Martians.",
        )
        self.assertTrue(gate["ok"])
        self.assertEqual(gate["will_block"], [])
        self.assertEqual(gate["opener_kind"], "discovery")

    def test_s1e18_is_scheduled_tonight(self) -> None:
        from marketing.galactic_first_frame import load_reels_media

        ep = (load_reels_media().get("episodes") or {}).get("s1e18") or {}
        self.assertEqual(ep.get("media_id"), 34949)
        self.assertEqual(ep.get("plate_id"), 34924)
        self.assertEqual(ep.get("schedule_status"), "scheduled_same_minute_2026-11-11_6pm")
        self.assertEqual((ep.get("scheduled_for") or {}).get("instagram"), "2026-11-11T18:00:00-06:00")
        self.assertTrue(ep.get("do_not_repost"))


if __name__ == "__main__":
    unittest.main()
