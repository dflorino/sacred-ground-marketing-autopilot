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
        self.assertIn(907, ids)  # Free Community Meditation must not be title-excluded
        self.assertNotIn(905, ids)
        self.assertNotIn(906, ids)
        self.assertNotIn(908, ids)  # Internal Closed Training — intentional exclude

    def test_tuesday_today_always_includes_community_meditation(self) -> None:
        """Founder rule: Tuesday Today lineup always lists community meditation."""
        from marketing import classify
        from marketing.models import Event

        tuesday = date(2026, 8, 4)  # Tuesday
        amber = Event(
            id=24175,
            title="Amber | Customized Therapeutic Massage Sessions",
            start_date="2026-08-04 12:00:00",
            end_date="2026-08-04 17:00:00",
            url="https://shopsacredground.com/book/amber/",
            cost="$2 – $166",
        )
        meditation = Event(
            id=21516,
            title="Free Community Meditation",
            start_date="2026-08-04 19:00:00",
            end_date="2026-08-04 20:00:00",
            url="https://shopsacredground.com/event/free-community-meditation-2/",
            cost="Free",
        )
        kept, skipped = classify.filter_valid([amber, meditation], on=tuesday)
        self.assertFalse(any(s["reason"] == "excluded_title" for s in skipped))
        today = classify.events_on_day(kept, tuesday)
        self.assertTrue(any(classify.is_community_meditation(e) for e in today))
        self.assertEqual({e.id for e in today}, {24175, 21516})

        # TEC omit → stub inject
        kept2, _ = classify.filter_valid([amber], on=tuesday)
        today2 = classify.events_on_day(kept2, tuesday)
        self.assertTrue(any(classify.is_community_meditation(e) for e in today2))
        self.assertTrue(any(e.id == 0 for e in today2))  # configured stub id

        # Caption cap must not drop evening meditation
        crowded = [
            Event(
                id=i,
                title=f"Session {i}",
                start_date=f"2026-08-04 {10 + i}:00:00",
                end_date=f"2026-08-04 {11 + i}:00:00",
                url=f"https://shopsacredground.com/event/{i}/",
            )
            for i in range(1, 8)
        ] + [meditation]
        kept3, _ = classify.filter_valid(crowded, on=tuesday)
        capped = classify.cap_events(classify.events_on_day(kept3, tuesday), limit=6)
        self.assertLessEqual(len(capped), 6)
        self.assertTrue(any(classify.is_community_meditation(e) for e in capped))

        # Week-ahead horizon that includes a Tuesday gets meditation too
        ahead = classify.ensure_meditation_in_horizon([], date(2026, 8, 4), days=1)
        self.assertEqual(len(ahead), 1)
        self.assertTrue(classify.is_community_meditation(ahead[0]))
        self.assertEqual(ahead[0].start_date, "2026-08-04 19:00:00")

    def test_generate_batch_creates_today_week_spotlight(self) -> None:
        from marketing import pipeline, store

        as_of = datetime(2026, 7, 9, 8, 0, tzinfo=ZoneInfo("America/Chicago"))
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

        as_of = datetime(2026, 7, 9, 8, 0, tzinfo=ZoneInfo("America/Chicago"))
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

        as_of = datetime(2026, 7, 9, 8, 0, tzinfo=ZoneInfo("America/Chicago"))
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

    def test_today_image_policy_and_empty_day_visit(self) -> None:
        from marketing import captions, control, images, pipeline, publish, store
        from marketing.models import Event

        # Isolate image usage ledger in temp state dir
        images.IMAGE_USAGE_PATH = os.path.join(self._tmpdir, "state", "image_usage.json")
        images.image_rules.cache_clear()

        store_url = images.store_image_url()
        self.assertTrue(store_url.startswith("https://"))

        one = Event(
            id=1,
            title="Tina",
            start_date="2026-08-03 12:00:00",
            end_date="2026-08-03 17:00:00",
            url="https://shopsacredground.com/book/tina/",
            image_url="https://example.com/tina.jpg",
        )
        # Monday with single non-specialty event → featured photo
        plan = images.plan_image([one], "today", day=date(2026, 8, 3))
        self.assertEqual(plan.source, "event_featured")
        self.assertEqual(plan.url, "https://example.com/tina.jpg")

        # Tarot + massage multi-event → specialty (tarot/massage) before rotation
        multi = [
            Event(
                id=2,
                title="Tarot with Tina",
                start_date="2026-08-03 12:00:00",
                end_date="2026-08-03 17:00:00",
                url="https://shopsacredground.com/book/tina/",
            ),
            Event(
                id=3,
                title="Therapeutic Massage",
                start_date="2026-08-03 13:00:00",
                end_date="2026-08-03 15:00:00",
                url="https://shopsacredground.com/book/massage/",
            ),
        ]
        plan_m = images.plan_image(multi, "today", day=date(2026, 8, 3))
        self.assertEqual(plan_m.rule, "massage")  # rarer specialty beats common tarot
        self.assertIn("Inner-Knowing-Portal", plan_m.url or "")

        # Sound bath should use gong plate, not generic meditation
        sound = [
            Event(
                id=26,
                title="Gong Sound Bath",
                start_date="2026-08-07 19:00:00",
                end_date="2026-08-07 20:30:00",
                url="https://shopsacredground.com/events/gong/",
            ),
        ]
        plan_sound = images.plan_image(sound, "today", day=date(2026, 8, 7))
        self.assertEqual(plan_sound.rule, "sound_healing")
        self.assertIn("gong", (plan_sound.url or "").lower())

        # Tarot + reflexology → reflexology (not tarot)
        tarot_ref = [
            Event(
                id=21,
                title="Intuitive Tarot",
                start_date="2026-08-04 12:00:00",
                end_date="2026-08-04 17:00:00",
                url="https://shopsacredground.com/book/tarot/",
            ),
            Event(
                id=22,
                title="Reflexology Session",
                start_date="2026-08-04 13:00:00",
                end_date="2026-08-04 15:00:00",
                url="https://shopsacredground.com/book/reflexology/",
            ),
        ]
        plan_tr = images.plan_image(tarot_ref, "today", day=date(2026, 8, 4))
        self.assertEqual(plan_tr.rule, "reflexology")
        self.assertIn("Restorative-Touch", plan_tr.url or "")

        # Reiki + chakra → chakra (not reiki)
        reiki_chakra = [
            Event(
                id=23,
                title="Reiki Healing",
                start_date="2026-08-05 12:00:00",
                end_date="2026-08-05 14:00:00",
                url="https://shopsacredground.com/book/reiki/",
            ),
            Event(
                id=24,
                title="Chakra Balancing",
                start_date="2026-08-05 15:00:00",
                end_date="2026-08-05 17:00:00",
                url="https://shopsacredground.com/book/chakra/",
            ),
        ]
        plan_rc = images.plan_image(reiki_chakra, "today", day=date(2026, 8, 5))
        self.assertEqual(plan_rc.rule, "chakra_healing")
        self.assertIn("sg-morning-chakra", plan_rc.url or "")

        # Tarot + sound bath / sonic fusion → sound_healing (not tarot)
        tarot_sound = [
            Event(
                id=31,
                title="Tarot with Tina",
                start_date="2026-08-07 12:00:00",
                end_date="2026-08-07 17:00:00",
                url="https://shopsacredground.com/book/tarot/",
            ),
            Event(
                id=32,
                title="Sonic Fusion Sound Bath",
                start_date="2026-08-07 19:00:00",
                end_date="2026-08-07 20:30:00",
                url="https://shopsacredground.com/events/sonic-fusion/",
            ),
        ]
        plan_ts = images.plan_image(tarot_sound, "today", day=date(2026, 8, 7))
        self.assertEqual(plan_ts.rule, "sound_healing")
        self.assertIn("gong", (plan_ts.url or "").lower())

        # Tarot + reiki → reiki (reiki beats tarot when only those two)
        tarot_reiki = [
            Event(
                id=33,
                title="Intuitive Tarot",
                start_date="2026-08-08 12:00:00",
                end_date="2026-08-08 17:00:00",
                url="https://shopsacredground.com/book/tarot/",
            ),
            Event(
                id=34,
                title="Reiki Healing",
                start_date="2026-08-08 14:00:00",
                end_date="2026-08-08 16:00:00",
                url="https://shopsacredground.com/book/reiki/",
            ),
        ]
        plan_treiki = images.plan_image(tarot_reiki, "today", day=date(2026, 8, 8))
        self.assertEqual(plan_treiki.rule, "reiki")

        # Reiki + crystal class → crystal_healing (not reiki)
        reiki_crystal = [
            Event(
                id=35,
                title="Reiki Session",
                start_date="2026-08-09 12:00:00",
                end_date="2026-08-09 14:00:00",
                url="https://shopsacredground.com/book/reiki/",
            ),
            Event(
                id=36,
                title="Working with Crystals Workshop",
                start_date="2026-08-09 15:00:00",
                end_date="2026-08-09 17:00:00",
                url="https://shopsacredground.com/event/crystal-workshop/",
            ),
        ]
        plan_rcr = images.plan_image(reiki_crystal, "today", day=date(2026, 8, 9))
        self.assertEqual(plan_rcr.rule, "crystal_healing")
        self.assertTrue(plan_rcr.url)

        # Tarot & Runes linked event → runes specialty plate (not a mixed-day pair case)
        runes_day = [
            Event(
                id=25,
                title="Tina’s Tarot & Runes",
                start_date="2026-08-06 12:00:00",
                end_date="2026-08-06 17:00:00",
                url="https://shopsacredground.com/tina/",
            ),
        ]
        plan_runes = images.plan_image(runes_day, "today", day=date(2026, 8, 6))
        self.assertEqual(plan_runes.rule, "tarot_runes")
        self.assertIn("7347a0c3", plan_runes.url or "")

        # Multi-event with no specialty → rotation pool
        generic_multi = [
            Event(
                id=4,
                title="Crystal Browse Hour",
                start_date="2026-08-05 12:00:00",
                end_date="2026-08-05 14:00:00",
                url="https://shopsacredground.com/event/a/",
            ),
            Event(
                id=5,
                title="Tea & Chat",
                start_date="2026-08-05 15:00:00",
                end_date="2026-08-05 16:00:00",
                url="https://shopsacredground.com/event/b/",
            ),
        ]
        # Wednesday Aug 5 2026
        plan_r = images.plan_image(generic_multi, "today", day=date(2026, 8, 5))
        self.assertEqual(plan_r.rule, "multi_event_rotation")
        self.assertTrue(plan_r.url)

        # Tuesday override
        tue = images.plan_image([one], "today", day=date(2026, 8, 4))  # Tuesday
        self.assertEqual(tue.rule, "tuesday_daily")

        # Shaman / medium always
        shaman = images.plan_image(
            [
                Event(
                    id=6,
                    title="Andean Shaman Session",
                    start_date="2026-08-06 12:00:00",
                    end_date="2026-08-06 14:00:00",
                    url="https://shopsacredground.com/event/shaman/",
                )
            ],
            "today",
            day=date(2026, 8, 6),
        )
        self.assertEqual(shaman.rule, "shaman_medium")

        # Robert not two days in a row
        robert_url = (
            "https://shopsacredground.com/wp-content/uploads/"
            "ai_generated_Classic-playing-cards-fanned-o_1764775825.png"
        )
        images.record_image_use(
            day=date(2026, 8, 6), url=robert_url, rule="robert", campaign="today"
        )
        robert_ev = [
            Event(
                id=7,
                title="Readings with Robert",
                start_date="2026-08-07 12:00:00",
                end_date="2026-08-07 17:00:00",
                url="https://shopsacredground.com/event/robert/",
                image_url="https://example.com/robert.jpg",
            )
        ]
        robert_day2 = images.plan_image(robert_ev, "today", day=date(2026, 8, 7))
        self.assertNotEqual(robert_day2.url, robert_url)

        # 7-day no-repeat on rotation
        images.record_image_use(
            day=date(2026, 8, 5),
            url=plan_r.url or "",
            rule="multi_event_rotation",
            campaign="today",
        )
        plan_r2 = images.plan_image(generic_multi, "today", day=date(2026, 8, 6))
        self.assertEqual(plan_r2.rule, "multi_event_rotation")
        self.assertNotEqual(plan_r2.url, plan_r.url)

        plan_empty = images.plan_image([], "today", day=date(2026, 8, 10))
        self.assertEqual(plan_empty.rule, "store_exterior")
        self.assertEqual(plan_empty.url, store_url)

        visit = captions.caption_today_visit("facebook", date(2026, 8, 4))
        self.assertIn("cool and unusual", visit["text"].lower())
        self.assertIn("chicagoland", visit["text"].lower())

        as_of = datetime(2026, 8, 10, 7, 0, tzinfo=ZoneInfo("America/Chicago"))
        result = pipeline.generate_batch(source="fixture", as_of=as_of)
        self.assertTrue(result["ok"])
        today = [d for d in result["drafts"] if d["campaign"] == "today"]
        self.assertEqual(len(today), 2)
        draft = store.get_draft(today[0]["id"])
        self.assertIn("empty_day_visit", draft.get("notes") or [])
        self.assertTrue(draft["image"]["url"])

        control.set_phase(2)
        control.resume()
        result2 = pipeline.generate_batch(source="fixture", as_of=as_of)
        self.assertEqual(result2["drafts_created"], 0)
        for d in store.list_drafts():
            if d["campaign"] == "today":
                store.update_draft(
                    d["id"],
                    status="approved",
                    approval_status="approved",
                    publish_blocked_reason=None,
                )
                ok, why = publish.can_schedule(store.get_draft(d["id"]))
                self.assertTrue(ok, why)
                payload = publish.schedule_payload(store.get_draft(d["id"]))
                self.assertTrue(payload["mediaItems"])

    def test_caption_event_blocks_are_spaced_and_scannable(self) -> None:
        """Multi-event Today + Week-Ahead captions: blank line between events, URL alone."""
        from marketing import captions
        from marketing.models import Event

        a = Event(
            id=1,
            title="Amber | Customized Therapeutic Massage Sessions",
            start_date="2026-08-04 12:00:00",
            end_date="2026-08-04 17:00:00",
            url="https://shopsacredground.com/book/amber/",
        )
        b = Event(
            id=2,
            title="Divine Insight Sessions with Janel: Akashic Records or Angel Card Readings",
            start_date="2026-08-04 13:00:00",
            end_date="2026-08-04 17:00:00",
            url="https://shopsacredground.com/book/janel/",
        )
        day = date(2026, 8, 4)

        today = captions.caption_today([a, b], "facebook", day)["text"]
        week_ahead = captions.caption_week_ahead([a, b], "facebook", day)["text"]
        week = captions.caption_week([a, b], "facebook", day)["text"]

        self.assertIn("Details & signup on each event page.", today)
        self.assertNotIn("ticket", today.lower())

        for text in (today, week_ahead, week):
            # Title line, then indented when, then indented URL (not packed on one line)
            self.assertIn("• Amber | Customized Therapeutic Massage Sessions\n", text)
            self.assertIn("  Tuesday, August 4 · 12:00 PM–5:00 PM\n", text)
            self.assertIn("  https://shopsacredground.com/book/amber/\n", text)
            # Blank line between event blocks (URL of first, then bullet of second)
            self.assertIn(
                "https://shopsacredground.com/book/amber/\n\n• Divine Insight Sessions with Janel",
                text,
            )
            # Hashtags still separated by a blank line
            self.assertRegex(text, r"\n\n#SacredGround")
            self.assertNotIn("ticket", text.lower())


if __name__ == "__main__":
    unittest.main()
