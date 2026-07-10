from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

# Isolate draft/state dirs for tests
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class AutopilotTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix="sgma-test-")
        import marketing.paths as paths

        self.paths = paths
        paths.DATA_DIR = self._tmpdir
        paths.DRAFTS_DIR = os.path.join(self._tmpdir, "drafts")
        paths.STATE_DIR = os.path.join(self._tmpdir, "state")
        paths.AUDIT_DIR = os.path.join(self._tmpdir, "audit")
        paths.CONTROL_PATH = os.path.join(paths.STATE_DIR, "control.json")
        paths.POSTED_PATH = os.path.join(paths.STATE_DIR, "posted.json")
        paths.OVERRIDES_PATH = os.path.join(paths.STATE_DIR, "overrides.json")
        # keep fixtures from real project
        paths.FIXTURES_DIR = os.path.join(ROOT, "data", "fixtures")
        paths.settings.cache_clear()
        paths.voice.cache_clear()
        paths.ensure_dirs()

    def tearDown(self) -> None:
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_filter_drops_old_missing_link_excluded(self) -> None:
        from marketing.ingest import load_fixture_events
        from marketing import classify

        events = load_fixture_events()
        kept, skipped = classify.filter_valid(events, on=date(2026, 7, 9))
        reasons = {s["reason"] for s in skipped}
        self.assertIn("old_event", reasons)
        self.assertIn("missing_link", reasons)
        self.assertIn("excluded_title", reasons)
        ids = {e.id for e in kept}
        self.assertIn(901, ids)
        self.assertIn(902, ids)
        self.assertNotIn(905, ids)
        self.assertNotIn(906, ids)
        self.assertNotIn(907, ids)

    def test_generate_batch_creates_today_week_spotlight(self) -> None:
        from marketing import pipeline, store

        as_of = datetime(2026, 7, 9, 8, 0, tzinfo=ZoneInfo("America/Phoenix"))
        result = pipeline.generate_batch(source="fixture", as_of=as_of)
        self.assertTrue(result["ok"])
        self.assertGreaterEqual(result["drafts_created"], 4)
        campaigns = {d["campaign"] for d in result["drafts"]}
        self.assertIn("today", campaigns)
        self.assertIn("week", campaigns)
        self.assertIn("spotlight", campaigns)
        platforms = {d["platform"] for d in result["drafts"]}
        self.assertEqual(platforms, {"facebook", "instagram"})

        # no duplicates on second run
        result2 = pipeline.generate_batch(source="fixture", as_of=as_of)
        self.assertEqual(result2["drafts_created"], 0)

        # captions have links and brand voice
        drafts = store.list_drafts()
        today_fb = next(d for d in drafts if d["campaign"] == "today" and d["platform"] == "facebook")
        self.assertIn("Sacred Ground", today_fb["caption"]["text"])
        self.assertTrue(today_fb["links"])
        self.assertEqual(today_fb["approval_status"], "pending")
        self.assertEqual(today_fb["publish_blocked_reason"], "phase_1_drafts_only")

    def test_approve_does_not_publish_phase1(self) -> None:
        from marketing import pipeline, store, control

        as_of = datetime(2026, 7, 9, 8, 0, tzinfo=ZoneInfo("America/Phoenix"))
        pipeline.generate_batch(source="fixture", as_of=as_of)
        d = store.list_drafts()[0]
        out = pipeline.approve(d["id"])
        self.assertEqual(out["approval_status"], "approved")
        self.assertEqual(out["publish_blocked_reason"], "phase_1_drafts_only")
        self.assertEqual(control.phase(), 1)

    def test_live_strict_fails_without_creating_drafts(self) -> None:
        from marketing import pipeline, store
        from unittest.mock import patch

        with patch("marketing.pipeline.load_events", side_effect=RuntimeError("TEC fetch failed")):
            result = pipeline.generate_batch(source="live-strict")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "wordpress_refresh_failed")
        self.assertEqual(result["drafts_created"], 0)
        self.assertEqual(store.list_drafts(), [])

    def test_reviewed_draft_not_overwritten_or_recreated(self) -> None:
        from marketing import pipeline, store

        as_of = datetime(2026, 7, 9, 8, 0, tzinfo=ZoneInfo("America/Phoenix"))
        pipeline.generate_batch(source="fixture", as_of=as_of)
        d = next(x for x in store.list_drafts() if x["campaign"] == "today" and x["platform"] == "facebook")
        original_caption = d["caption"]["text"]
        pipeline.approve(d["id"])

        # Second run must not recreate fingerprint
        result2 = pipeline.generate_batch(source="fixture", as_of=as_of)
        self.assertEqual(result2["drafts_created"], 0)

        # Content overwrite refused
        with self.assertRaises(PermissionError):
            store.update_draft(d["id"], caption={"text": "CHANGED", "hashtags": []})

        reloaded = store.get_draft(d["id"])
        self.assertEqual(reloaded["caption"]["text"], original_caption)
        self.assertEqual(reloaded["approval_status"], "approved")

    def test_pause_switch(self) -> None:
        from marketing import control

        control.pause("test")
        self.assertTrue(control.is_paused())
        allowed, reason = control.publish_allowed()
        self.assertFalse(allowed)
        self.assertEqual(reason, "autopilot_paused")
        control.resume()
        self.assertFalse(control.is_paused())

    def test_starred_title_is_featured(self) -> None:
        from marketing.ingest import load_fixture_events
        from marketing import classify

        events = load_fixture_events()
        fair = next(e for e in events if e.id == 901)
        fair = classify.enrich(fair)
        self.assertEqual(fair.title, "Holistic Fair")
        self.assertTrue(fair.featured)
        self.assertTrue(fair.is_special)


if __name__ == "__main__":
    unittest.main()
