from __future__ import annotations

import unittest
from datetime import date

from marketing import slot_readiness


class SlotReadinessTests(unittest.TestCase):
    def test_libra_sep22_fails_closed(self) -> None:
        block = slot_readiness.afternoon_block(date(2026, 9, 22))
        self.assertIsNotNone(block)
        self.assertEqual(block["reason"], "required_plate_missing")
        self.assertIn("Libra", str(block.get("theme") or "") + str(block.get("detail") or ""))

    def test_peace_sep21_has_plate(self) -> None:
        self.assertIsNone(slot_readiness.afternoon_block(date(2026, 9, 21)))

    def test_optional_sep10_does_not_block(self) -> None:
        self.assertIsNone(slot_readiness.afternoon_block(date(2026, 9, 10)))

    def test_thursday_clip_owns_slot(self) -> None:
        block = slot_readiness.afternoon_block(date(2026, 9, 24))
        self.assertIsNotNone(block)
        self.assertEqual(block["reason"], "cinematic_short_owns_slot")

    def test_ordinary_day_still_posts(self) -> None:
        self.assertIsNone(slot_readiness.afternoon_block(date(2026, 9, 23)))

    def test_scorpio_season_fails_closed(self) -> None:
        block = slot_readiness.afternoon_block(date(2026, 10, 23))
        self.assertIsNotNone(block)
        self.assertEqual(block["reason"], "required_plate_missing")

    def test_check_range_reports_libra(self) -> None:
        report = slot_readiness.check_range(days=1, start=date(2026, 9, 22))
        self.assertFalse(report["ok"])
        self.assertEqual(report["missing"], 1)

    def test_cli_exits_1_when_missing(self) -> None:
        from marketing.__main__ import main

        self.assertEqual(
            main(["check-slot-readiness", "--start", "2026-09-22", "--days", "1"]),
            1,
        )
        self.assertEqual(
            main(["check-slot-readiness", "--start", "2026-09-23", "--days", "1"]),
            0,
        )
