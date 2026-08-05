"""Tests for daily_reel scaffold — must not enable auto-publish or break image campaigns."""
from __future__ import annotations

import os
import tempfile
import unittest
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class ReelsScaffoldTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix="sgma-reels-")
        import marketing.paths as paths

        self.paths = paths
        paths.DATA_DIR = self._tmpdir
        paths.DRAFTS_DIR = os.path.join(self._tmpdir, "drafts")
        paths.STATE_DIR = os.path.join(self._tmpdir, "state")
        paths.AUDIT_DIR = os.path.join(self._tmpdir, "audit")
        paths.CONTROL_PATH = os.path.join(paths.STATE_DIR, "control.json")
        paths.POSTED_PATH = os.path.join(paths.STATE_DIR, "posted.json")
        paths.OVERRIDES_PATH = os.path.join(paths.STATE_DIR, "overrides.json")
        paths.settings.cache_clear()
        paths.ensure_dirs()

    def tearDown(self) -> None:
        import shutil

        shutil.rmtree(self._tmpdir, ignore_errors=True)
        self.paths.settings.cache_clear()

    def test_config_targets_ig_fb_reels(self) -> None:
        from marketing import reels
        from marketing.paths import settings

        camp = (settings().get("campaigns") or {}).get("daily_reel") or {}
        self.assertFalse(camp.get("enabled"))
        self.assertFalse(camp.get("auto_publish"))
        self.assertEqual(camp.get("schedule_local_time"), "10:30")
        self.assertEqual(
            set(camp.get("platforms") or []),
            {"instagram_reels", "facebook_reels"},
        )
        primary = set(reels.primary_platforms())
        self.assertEqual(primary, {"instagram_reels", "facebook_reels"})
        optional = set(reels.optional_platforms())
        self.assertIn("tiktok", optional)
        self.assertIn("youtube_shorts", optional)

    def test_schedule_late_morning_chicago(self) -> None:
        from marketing import schedule

        plan = schedule.schedule_daily_reel(date(2026, 8, 5))
        self.assertIn("2026-08-05T10:30:00", plan.recommended_at)

    def test_plan_uses_welcome_rotation_and_blocks_publish(self) -> None:
        from marketing import reels

        plan = reels.plan_daily_reel(date(2026, 8, 5))
        self.assertTrue(plan["ok"])
        self.assertEqual(plan["campaign"], "daily_reel")
        self.assertFalse(plan["auto_publish"])
        self.assertEqual(
            {d["platform"] for d in plan["draft_plans"]},
            {"instagram_reels", "facebook_reels"},
        )
        for d in plan["draft_plans"]:
            self.assertEqual(d["media_type"], "video")
            self.assertEqual(d["format"], "9:16")
            self.assertEqual(d["publish_blocked_reason"], "reels_video_path_not_ready")
            self.assertIn("caption", d)
            self.assertTrue(d["caption"]["text"])

    def test_beneath_surface_prefers_observatory(self) -> None:
        from marketing import reels

        plan = reels.plan_daily_reel(
            date(2026, 8, 5),
            beneath_surface="The moon asks for quiet courage today.",
        )
        self.assertEqual(plan["script_id"], "observatory_teaser")
        self.assertEqual(plan["content_source"], "observatory_beneath_surface")
        self.assertIn("quiet courage", plan["draft_plans"][0]["spoken"])

    def test_zernio_account_map(self) -> None:
        from marketing import reels

        self.assertEqual(reels.zernio_account_key("instagram_reels"), "instagram")
        self.assertEqual(reels.zernio_account_key("facebook_reels"), "facebook")

    def test_readiness_does_not_claim_auto_publish(self) -> None:
        from marketing import reels

        status = reels.readiness()
        self.assertTrue(status["works_today"]["image_posts_zernio"])
        self.assertFalse(status["target"]["auto_publish"])
        self.assertFalse(status["target"]["campaign_enabled"])
        self.assertTrue(any("Video publish" in b for b in status["blocked_for_auto_reels"]))
        self.assertIn("instagram_reels", status["target"]["platforms_primary"])

    def test_image_campaigns_untouched(self) -> None:
        from marketing.paths import settings

        camps = settings()["campaigns"]
        for name in ("today", "week_ahead", "tuesday_meditation"):
            self.assertTrue(camps[name].get("auto_publish"))
            self.assertEqual(
                set(camps[name]["platforms"]),
                {"facebook", "instagram"},
            )


if __name__ == "__main__":
    unittest.main()
