from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from datetime import date, datetime, timedelta
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
        from marketing import meditation as meditation_mod
        from marketing import morning_flyers as mf
        from marketing import images as images_mod

        meditation_mod.clear_meditation_hosts_cache()
        paths.ensure_dirs()

        # Isolate morning flyer config/assets so ensure-if-missing never
        # writes into the real repo config during tests.
        self._mf = mf
        flyers_src = os.path.join(ROOT, "config", "morning_flyers.json")
        self._mf_path = os.path.join(self._tmpdir, "morning_flyers.json")
        if os.path.isfile(flyers_src):
            shutil.copy2(flyers_src, self._mf_path)
        else:
            with open(self._mf_path, "w", encoding="utf-8") as fh:
                fh.write('{"prebranded_default": true, "flyers": {}}\n')
        mf.FLYERS_PATH = self._mf_path
        mf.ASSETS_DIR = os.path.join(self._tmpdir, "assets")
        os.makedirs(mf.ASSETS_DIR, exist_ok=True)
        images_mod.morning_flyers.cache_clear()

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
        self.assertTrue(plan_m.url)

        # Specialty tests use Sept dates (no date-keyed morning flyers).
        # Sound bath should use sound_healing pool (gong / bowls), not meditation
        sound = [
            Event(
                id=26,
                title="Gong Sound Bath",
                start_date="2026-09-07 19:00:00",
                end_date="2026-09-07 20:30:00",
                url="https://shopsacredground.com/events/gong/",
            ),
        ]
        plan_sound = images.plan_image(sound, "today", day=date(2026, 9, 7))
        self.assertEqual(plan_sound.rule, "sound_healing")
        sound_url = (plan_sound.url or "").lower()
        self.assertTrue(
            "gong" in sound_url or "sound-bowls" in sound_url,
            sound_url,
        )

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
        self.assertTrue(plan_tr.url)

        # Reiki + chakra → chakra (not reiki)
        reiki_chakra = [
            Event(
                id=23,
                title="Reiki Healing",
                start_date="2026-09-02 12:00:00",
                end_date="2026-09-02 14:00:00",
                url="https://shopsacredground.com/book/reiki/",
            ),
            Event(
                id=24,
                title="Chakra Balancing",
                start_date="2026-09-02 15:00:00",
                end_date="2026-09-02 17:00:00",
                url="https://shopsacredground.com/book/chakra/",
            ),
        ]
        plan_rc = images.plan_image(reiki_chakra, "today", day=date(2026, 9, 2))
        self.assertEqual(plan_rc.rule, "chakra_healing")
        chakra_url = (plan_rc.url or "").lower()
        self.assertTrue(
            "chakra" in chakra_url,
            chakra_url,
        )

        # Tarot + sound bath / sonic fusion → sound_healing (not tarot)
        tarot_sound = [
            Event(
                id=31,
                title="Tarot with Tina",
                start_date="2026-09-07 12:00:00",
                end_date="2026-09-07 17:00:00",
                url="https://shopsacredground.com/book/tarot/",
            ),
            Event(
                id=32,
                title="Sonic Fusion Sound Bath",
                start_date="2026-09-07 19:00:00",
                end_date="2026-09-07 20:30:00",
                url="https://shopsacredground.com/events/sonic-fusion/",
            ),
        ]
        plan_ts = images.plan_image(tarot_sound, "today", day=date(2026, 9, 7))
        self.assertEqual(plan_ts.rule, "sound_healing")
        ts_url = (plan_ts.url or "").lower()
        self.assertTrue(
            "gong" in ts_url or "sound-bowls" in ts_url,
            ts_url,
        )

        # Tarot + reiki → reiki (reiki beats tarot when only those two)
        tarot_reiki = [
            Event(
                id=33,
                title="Intuitive Tarot",
                start_date="2026-09-08 12:00:00",
                end_date="2026-09-08 17:00:00",
                url="https://shopsacredground.com/book/tarot/",
            ),
            Event(
                id=34,
                title="Reiki Healing",
                start_date="2026-09-08 14:00:00",
                end_date="2026-09-08 16:00:00",
                url="https://shopsacredground.com/book/reiki/",
            ),
        ]
        plan_treiki = images.plan_image(tarot_reiki, "today", day=date(2026, 9, 8))
        self.assertEqual(plan_treiki.rule, "reiki")

        # Reiki + crystal class → crystal_healing (not reiki)
        reiki_crystal = [
            Event(
                id=35,
                title="Reiki Session",
                start_date="2026-09-09 12:00:00",
                end_date="2026-09-09 14:00:00",
                url="https://shopsacredground.com/book/reiki/",
            ),
            Event(
                id=36,
                title="Working with Crystals Workshop",
                start_date="2026-09-09 15:00:00",
                end_date="2026-09-09 17:00:00",
                url="https://shopsacredground.com/event/crystal-workshop/",
            ),
        ]
        plan_rcr = images.plan_image(reiki_crystal, "today", day=date(2026, 9, 9))
        self.assertEqual(plan_rcr.rule, "crystal_healing")
        self.assertTrue(plan_rcr.url)

        # Tarot & Runes linked event → runes specialty plate (not a mixed-day pair case)
        runes_day = [
            Event(
                id=25,
                title="Tina’s Tarot & Runes",
                start_date="2026-09-03 12:00:00",
                end_date="2026-09-03 17:00:00",
                url="https://shopsacredground.com/tina/",
            ),
        ]
        plan_runes = images.plan_image(runes_day, "today", day=date(2026, 9, 3))
        self.assertEqual(plan_runes.rule, "tarot_runes")
        self.assertIn("7347a0c3", plan_runes.url or "")

        # Multi-event with no specialty → rotation pool
        generic_multi = [
            Event(
                id=4,
                title="Crystal Browse Hour",
                start_date="2026-09-02 12:00:00",
                end_date="2026-09-02 14:00:00",
                url="https://shopsacredground.com/event/a/",
            ),
            Event(
                id=5,
                title="Tea & Chat",
                start_date="2026-09-02 15:00:00",
                end_date="2026-09-02 16:00:00",
                url="https://shopsacredground.com/event/b/",
            ),
        ]
        plan_r = images.plan_image(generic_multi, "today", day=date(2026, 9, 2))
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
                    start_date="2026-09-03 12:00:00",
                    end_date="2026-09-03 14:00:00",
                    url="https://shopsacredground.com/event/shaman/",
                )
            ],
            "today",
            day=date(2026, 9, 3),
        )
        self.assertEqual(shaman.rule, "shaman_medium")

        # Robert not two days in a row
        robert_url = (
            "https://shopsacredground.com/wp-content/uploads/"
            "ai_generated_Classic-playing-cards-fanned-o_1764775825.png"
        )
        images.record_image_use(
            day=date(2026, 9, 3), url=robert_url, rule="robert", campaign="today"
        )
        robert_ev = [
            Event(
                id=7,
                title="Readings with Robert",
                start_date="2026-09-04 12:00:00",
                end_date="2026-09-04 17:00:00",
                url="https://shopsacredground.com/event/robert/",
                image_url="https://example.com/robert.jpg",
            )
        ]
        robert_day2 = images.plan_image(robert_ev, "today", day=date(2026, 9, 4))
        self.assertNotEqual(robert_day2.url, robert_url)

        # 7-day no-repeat on rotation
        images.record_image_use(
            day=date(2026, 9, 2),
            url=plan_r.url or "",
            rule="multi_event_rotation",
            campaign="today",
        )
        plan_r2 = images.plan_image(generic_multi, "today", day=date(2026, 9, 3))
        self.assertEqual(plan_r2.rule, "multi_event_rotation")
        self.assertNotEqual(plan_r2.url, plan_r.url)

        # Date-keyed finished flyer beats specialty on Aug 5.
        plan_flyer_day = images.plan_image(reiki_chakra, "today", day=date(2026, 8, 5))
        self.assertEqual(plan_flyer_day.rule, "morning_flyer")
        self.assertTrue(plan_flyer_day.prebranded)
        self.assertTrue(images.skip_brand_overlays(plan_flyer_day))

        # Date-keyed finished flyer wins even with no events that day.
        plan_flyer = images.plan_image([], "today", day=date(2026, 8, 10))
        self.assertEqual(plan_flyer.rule, "morning_flyer")
        self.assertTrue(plan_flyer.prebranded)
        self.assertIn("sg-morning-flyer-", plan_flyer.url or "")
        self.assertTrue(images.skip_brand_overlays(plan_flyer))

        # Empty non-Tuesday with no date flyer → store exterior (creative pack removed).
        plan_empty = images.plan_image([], "today", day=date(2026, 9, 2))
        self.assertEqual(plan_empty.rule, "store_exterior")
        self.assertTrue(plan_empty.url)
        self.assertNotIn("sg-morning-creative-", plan_empty.url or "")
        self.assertFalse(plan_empty.prebranded)

        visit = captions.caption_today_visit("facebook", date(2026, 8, 4))
        self.assertIn("cool and unusual", visit["text"].lower())
        self.assertIn("chicagoland", visit["text"].lower())

        # Morning promotes tomorrow — pick a Wed whose Thursday has no fixture events
        # (and is not Tuesday, so no meditation stub).
        as_of = datetime(2026, 9, 2, 9, 0, tzinfo=ZoneInfo("America/Chicago"))
        result = pipeline.generate_batch(source="fixture", as_of=as_of)
        self.assertTrue(result["ok"])
        today = [d for d in result["drafts"] if d["campaign"] == "today"]
        self.assertEqual(len(today), 2)
        draft = store.get_draft(today[0]["id"])
        self.assertIn("empty_day_visit", draft.get("notes") or [])
        self.assertIn("event_day:2026-09-03", draft.get("notes") or [])
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

        # Today keeps full date·time on each event (single-day post)
        self.assertIn("• Amber | Customized Therapeutic Massage Sessions\n", today)
        self.assertIn("  Tuesday, August 4 · 12:00 PM–5:00 PM\n", today)
        self.assertIn("  https://shopsacredground.com/book/amber/\n", today)
        self.assertIn(
            "https://shopsacredground.com/book/amber/\n\n• Divine Insight Sessions with Janel",
            today,
        )
        self.assertRegex(today, r"\n\n#SacredGround")
        self.assertNotIn("ticket", today.lower())

        # Week / week-ahead: day header + time-only lines (no repeated weekday on every row)
        for text in (week_ahead, week):
            self.assertIn("Tuesday, August 4\n\n• Amber | Customized Therapeutic Massage Sessions\n", text)
            self.assertIn("  12:00 PM–5:00 PM\n", text)
            self.assertIn("  https://shopsacredground.com/book/amber/\n", text)
            self.assertNotIn("Tuesday, August 4 · 12:00 PM–5:00 PM", text)
            self.assertIn(
                "https://shopsacredground.com/book/amber/\n\n• Divine Insight Sessions with Janel",
                text,
            )
            self.assertRegex(text, r"\n\n#SacredGround")
            self.assertNotIn("ticket", text.lower())

    def test_caption_week_ahead_day_sections_scannable(self) -> None:
        """Two-day night caption: clear day breaks, standalone goodnight, blank before tags."""
        from marketing import captions
        from marketing.models import Event
        from marketing.paths import voice

        wed_a = Event(
            id=1,
            title="Tina's Tarot & Rune Sessions",
            start_date="2026-08-05 12:00:00",
            end_date="2026-08-05 18:00:00",
            url="https://shopsacredground.com/tina/",
        )
        wed_b = Event(
            id=2,
            title="Soul Alignment w/ Karen",
            start_date="2026-08-05 19:00:00",
            end_date="2026-08-05 22:00:00",
            url="https://shopsacredground.com/karen/",
        )
        thu = Event(
            id=3,
            title="Tarot with Adie",
            start_date="2026-08-06 12:00:00",
            end_date="2026-08-06 17:00:00",
            url="https://shopsacredground.com/book/adie/",
        )
        day = date(2026, 8, 4)
        text = captions.caption_week_ahead([wed_a, wed_b, thu], "facebook", day)["text"]

        # Day section headers with blank line before first event of that day
        self.assertIn(
            "Wednesday, August 5\n\n• Tina's Tarot & Rune Sessions\n  12:00 PM–6:00 PM\n"
            "  https://shopsacredground.com/tina/",
            text,
        )
        self.assertIn(
            "https://shopsacredground.com/karen/\n\nThursday, August 6\n\n• Tarot with Adie\n"
            "  12:00 PM–5:00 PM\n  https://shopsacredground.com/book/adie/",
            text,
        )
        # Blank line between events on the same day
        self.assertIn(
            "https://shopsacredground.com/tina/\n\n• Soul Alignment w/ Karen",
            text,
        )
        # Goodnight closer stands alone (blank line before it and before hashtags)
        closers = list(voice().get("week_ahead_closers") or [])
        matched = [c for c in closers if f"\n\n{c}\n\n#" in text]
        self.assertTrue(matched, "expected a rotating goodnight closer before hashtags")
        self.assertRegex(text, r"\n\n#SacredGround")
        # Door/light must not appear inside an event block
        self.assertNotIn("Tina's Tarot & Rune Sessions\nThe door is always open", text)
        self.assertNotIn("Doors close at 7:05pm\nThe door is always open", text)

    def test_caption_community_meditation_special_block(self) -> None:
        """Daytime meditation block only; door/light is a week-ahead goodnight closer."""
        import hashlib

        from marketing import captions
        from marketing.meditation import meditation_event_block
        from marketing.models import Event
        from marketing.paths import voice

        janel = Event(
            id=2,
            title="Divine Insight Sessions with Janel: Akashic Records or Angel Card Readings",
            start_date="2026-08-04 13:00:00",
            end_date="2026-08-04 17:00:00",
            url="https://shopsacredground.com/book/janel/",
        )
        meditation = Event(
            id=99,
            title="Free Community Meditation",
            start_date="2026-08-04 19:00:00",
            end_date="2026-08-04 20:00:00",
            url="https://shopsacredground.com/event/free-community-meditation-2/",
        )
        day = date(2026, 8, 4)
        daytime_block = meditation_event_block(day=day, event=meditation)
        self.assertIn("With ", daytime_block)
        self.assertIn("All are welcome", daytime_block)
        goodnight = "The door is always open...we will leave the light on"

        today = captions.caption_today([janel, meditation], "facebook", day)["text"]
        week_ahead = captions.caption_week_ahead(
            [janel, meditation], "facebook", day
        )["text"]
        week = captions.caption_week([janel, meditation], "facebook", day)["text"]
        solo = captions.caption_today([meditation], "instagram", day)["text"]

        for text in (today, week_ahead, week, solo):
            self.assertIn(daytime_block, text)
            self.assertIn("Doors close at 7:05pm", text)
            self.assertNotIn("8:05", text)
            self.assertNotIn("o'clock", text.lower())
            self.assertNotIn(
                "https://shopsacredground.com/event/free-community-meditation-2/",
                text,
            )
            # No generic Tuesday date/time line for meditation
            self.assertNotIn("Tuesday, August 4 · 7:00 PM", text)
            self.assertNotIn("7:00 PM–8:00 PM", text)
            # Goodnight must not be glued onto the daytime meditation block
            self.assertNotIn(daytime_block + "\n" + goodnight, text)

        # Daytime / non-night captions never use the evening goodnight closer
        for text in (today, solo, week):
            self.assertNotIn(goodnight, text)

        # Week-ahead rotates standalone goodnight closers; door/light is one of them
        closers = list(voice().get("week_ahead_closers") or [])
        self.assertIn(goodnight, closers)
        self.assertTrue(
            any(c in week_ahead for c in closers),
            "week_ahead should include a rotating goodnight closer",
        )
        # Prove the Founder goodnight line is selectable as a closer
        hit = None
        for i in range(500):
            seed = f"goodnight-probe|{i}"
            if int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(closers) == closers.index(
                goodnight
            ):
                hit = seed
                break
        self.assertIsNotNone(hit)
        self.assertEqual(captions._week_ahead_closer(hit), goodnight)

        # Blank line between Janel block and meditation block
        self.assertIn(
            "https://shopsacredground.com/book/janel/\n\n• Free Community Meditation\n"
            "With ",
            today,
        )
        self.assertIn("All are welcome", today)
        # Janel still gets normal when + URL
        self.assertIn("  Tuesday, August 4 · 1:00 PM–5:00 PM\n", today)
        self.assertIn("  https://shopsacredground.com/book/janel/\n", today)

        # Case-insensitive title match (stub / TEC variants)
        stub = Event(
            id=0,
            title="Tuesday Community Meditation at Sacred Ground",
            start_date="2026-08-04 19:00:00",
            end_date="2026-08-04 20:00:00",
            url="https://shopsacredground.com/event/meditation/",
        )
        stub_text = captions.caption_week([stub], "facebook", day)["text"]
        self.assertIn(daytime_block, stub_text)
        self.assertNotIn(goodnight, stub_text)
        self.assertNotIn("https://shopsacredground.com/event/meditation/", stub_text)

    def test_free_community_note_on_morning_multi_and_week_ahead(self) -> None:
        """Lions Gate / free community: explicit note on multi + week_ahead; soft CTA."""
        from marketing import captions
        from marketing.classify import is_free_community_event
        from marketing.models import Event

        melissa = Event(
            id=1,
            title="Shaman Medium Melissa",
            start_date="2026-08-08 11:00:00",
            end_date="2026-08-08 14:00:00",
            url="https://shopsacredground.com/book/melissa/",
            cost="$99",
        )
        lions = Event(
            id=25926,
            title="Lions Gate Meditation with Eve Free Community Event",
            start_date="2026-08-08 20:00:00",
            end_date="2026-08-08 21:00:00",
            url="https://shopsacredground.com/event/lions-gate-meditation-with-eve/",
            cost="Free",
        )
        # Title without "community" still qualifies via Free cost + lions gate cue
        lions_short = Event(
            id=25927,
            title="Lions Gate Meditation with Eve",
            start_date="2026-08-08 20:00:00",
            end_date="2026-08-08 21:00:00",
            url="https://shopsacredground.com/event/lions-gate-meditation-with-eve/",
            cost="Free",
        )
        self.assertTrue(is_free_community_event(lions))
        self.assertTrue(is_free_community_event(lions_short))

        note = "Free community gathering — all are welcome."
        day = date(2026, 8, 8)
        fri = date(2026, 8, 7)

        morning_multi = captions.caption_today([melissa, lions], "facebook", day)["text"]
        self.assertIn(note, morning_multi)
        self.assertIn("Lions Gate Meditation with Eve Free Community Event", morning_multi)

        # Friday morning: tomorrow=Sat lineup (multi) — note must appear
        fri_morning = captions.caption_today([melissa, lions], "facebook", day)["text"]
        self.assertIn(note, fri_morning)

        week_ahead = captions.caption_week_ahead(
            [melissa, lions], "facebook", fri
        )["text"]
        self.assertIn(note, week_ahead)
        self.assertIn(
            "Book a session when you’re ready — free community gatherings are open to all.",
            week_ahead,
        )
        self.assertNotIn("Call to book a session or grab your spot online.", week_ahead)

        # Paid-only week_ahead keeps the book CTA
        paid_only = captions.caption_week_ahead([melissa], "instagram", fri)["text"]
        self.assertIn("Call to book a session or grab your spot online.", paid_only)
        self.assertNotIn(note, paid_only)

        afternoon = captions.caption_afternoon_spotlight(lions, "facebook", fri)["text"]
        self.assertIn(note, afternoon)

        # Sat morning tonight merge still carries the note (and no duplicate spam)
        sat_morning = captions.caption_today(
            [melissa],
            "facebook",
            day,
            tonight_events=[lions],
        )["text"]
        self.assertEqual(sat_morning.count(note), 1)

        # Same-day flyer + tonight merge: lead with tonight, not “tomorrow”
        sunday = Event(
            id=25384,
            title="Divine Insight Sessions with Janel: Akashic Records or Angel Card Readings",
            start_date="2026-08-09 12:00:00",
            end_date="2026-08-09 17:00:00",
            url="https://shopsacredground.com/book/janel/",
        )
        mixed = captions.caption_today(
            [sunday],
            "facebook",
            date(2026, 8, 9),
            tonight_events=[lions],
            flyer_day=date(2026, 8, 8),
            publish_day=date(2026, 8, 8),
        )
        hook_l = mixed["hook"].lower()
        self.assertTrue(
            "tonight" in hook_l,
            f"mixed same-day flyer should lead with tonight, got: {mixed['hook']}",
        )
        self.assertNotIn("peek at tomorrow", hook_l)
        # Tonight events listed before tomorrow section
        self.assertLess(
            mixed["text"].find("Lions Gate"),
            mixed["text"].find("Divine Insight"),
        )

        tomorrow_only = captions.caption_today(
            [sunday], "facebook", date(2026, 8, 9)
        )
        self.assertIn("tomorrow", tomorrow_only["hook"].lower())
        self.assertNotIn("tonight", tomorrow_only["hook"].lower())

        tonight_only = captions.caption_today(
            [],
            "facebook",
            date(2026, 8, 9),
            tonight_events=[lions],
            flyer_day=date(2026, 8, 8),
            publish_day=date(2026, 8, 8),
        )
        self.assertIn("tonight", tonight_only["hook"].lower())
        self.assertNotIn("tomorrow", tonight_only["hook"].lower())

        from marketing import schedule

        self.assertEqual(
            schedule.morning_campaign_word(
                flyer_day=date(2026, 8, 8),
                publish_day=date(2026, 8, 8),
                prebranded=True,
            ),
            "",
        )
        self.assertEqual(
            schedule.morning_campaign_word(
                flyer_day=date(2026, 8, 8),
                publish_day=date(2026, 8, 8),
                prebranded=False,
            ),
            "TODAY",
        )
        self.assertEqual(
            schedule.morning_campaign_word(
                flyer_day=date(2026, 8, 9),
                publish_day=date(2026, 8, 8),
                prebranded=False,
            ),
            "TOMORROW",
        )

        # Tuesday Free Community Meditation still uses meditation block (doors close)
        tue_med = Event(
            id=99,
            title="Free Community Meditation",
            start_date="2026-08-04 19:00:00",
            end_date="2026-08-04 20:00:00",
            url="https://shopsacredground.com/event/free-community-meditation-2/",
            cost="Free",
        )
        self.assertTrue(is_free_community_event(tue_med))
        med_today = captions.caption_today([tue_med], "facebook", date(2026, 8, 4))["text"]
        self.assertIn("Doors close at 7:05pm", med_today)
        self.assertIn("All are welcome", med_today)

    def test_tuesday_meditation_schedule_and_holiday_skips(self) -> None:
        from marketing import schedule

        tue = date(2026, 8, 4)  # Tuesday, not a holiday
        self.assertTrue(schedule.should_run_tuesday_meditation(tue))
        self.assertFalse(schedule.is_tuesday_meditation_holiday(tue))
        plan = schedule.schedule_tuesday_meditation(tue)
        self.assertTrue(plan.recommended_at.startswith("2026-08-04T16:00:00"))

        wed = date(2026, 8, 5)
        self.assertFalse(schedule.should_run_tuesday_meditation(wed))

        # Holiday Tuesdays must skip (Chicago local month/day)
        xmas_eve_tue = date(2024, 12, 24)
        xmas_day_tue = date(2029, 12, 25)
        nye_tue = date(2024, 12, 31)
        nyd_tue = date(2030, 1, 1)
        for d, name in (
            (xmas_eve_tue, "christmas_eve"),
            (xmas_day_tue, "christmas_day"),
            (nye_tue, "new_years_eve"),
            (nyd_tue, "new_years_day"),
        ):
            self.assertEqual(d.weekday(), 1, msg=f"{d} should be Tuesday")
            self.assertTrue(schedule.is_tuesday_meditation_holiday(d))
            self.assertEqual(schedule.tuesday_meditation_holiday_name(d), name)
            self.assertFalse(schedule.should_run_tuesday_meditation(d))

    def test_tuesday_meditation_caption_daytime_block_no_goodnight(self) -> None:
        from marketing import captions
        from marketing.meditation import host_for_day, meditation_event_block

        day = date(2026, 8, 4)
        daytime_block = meditation_event_block(day=day)
        host = host_for_day(day)
        self.assertIsNotNone(host)
        goodnight = "The door is always open...we will leave the light on"

        for platform in ("facebook", "instagram"):
            text = captions.caption_tuesday_meditation(platform, day)["text"]
            self.assertIn(daytime_block, text)
            self.assertIn("Doors close at 7:05pm", text)
            self.assertNotIn("8:05", text)
            self.assertIn(f"With {host.practitioner} · {host.style}", text)
            self.assertIn("#SacredGround", text)
            self.assertNotIn(goodnight, text)
            self.assertNotIn("o'clock", text.lower())
            self.assertNotIn("leave the light", text.lower())
            self.assertNotIn("7:00 PM", text)
            self.assertNotIn(
                "https://shopsacredground.com/event/free-community-meditation",
                text,
            )
            # Opener mentions practitioner or style when host is known
            self.assertTrue(
                host.practitioner in text or host.style in text,
                "standalone opener/block should surface host info",
            )

    def test_tuesday_meditation_pipeline_publishes_tuesdays_skips_holidays(self) -> None:
        from marketing import images, pipeline, store
        from marketing.paths import settings

        images.IMAGE_USAGE_PATH = os.path.join(self._tmpdir, "state", "image_usage.json")
        pool = list(
            (settings().get("campaigns") or {})
            .get("tuesday_meditation", {})
            .get("image_urls")
            or []
        )
        self.assertGreaterEqual(len(pool), 3)

        # Ordinary Tuesday → FB + IG drafts at 4pm
        as_of = datetime(2026, 8, 4, 10, 0, tzinfo=ZoneInfo("America/Chicago"))
        result = pipeline.generate_batch(source="fixture", as_of=as_of)
        self.assertTrue(result["ok"])
        tm = [d for d in result["drafts"] if d["campaign"] == "tuesday_meditation"]
        self.assertEqual(len(tm), 2)
        platforms = {d["platform"] for d in tm}
        self.assertEqual(platforms, {"facebook", "instagram"})

        drafts = store.list_drafts()
        tm_fb = next(
            d
            for d in drafts
            if d["campaign"] == "tuesday_meditation" and d["platform"] == "facebook"
        )
        sched = tm_fb["schedule_recommendation"]["recommended_at"]
        self.assertTrue(sched.startswith("2026-08-04T16:00:00"))
        cap = tm_fb["caption"]["text"]
        self.assertIn("• Free Community Meditation\nWith ", cap)
        self.assertIn("All are welcome", cap)
        self.assertNotIn("The door is always open", cap)
        self.assertNotIn("o'clock", cap.lower())
        self.assertIn(tm_fb["image"]["url"], pool)
        self.assertEqual(tm_fb["image"]["rule"], "tuesday_meditation_pool")

        # Holiday Tuesday → skip, no drafts
        as_of_xmas = datetime(2024, 12, 24, 10, 0, tzinfo=ZoneInfo("America/Chicago"))
        result_x = pipeline.generate_batch(source="fixture", as_of=as_of_xmas)
        self.assertTrue(result_x["ok"])
        tm_x = [
            d for d in result_x["drafts"] if d["campaign"] == "tuesday_meditation"
        ]
        self.assertEqual(tm_x, [])
        skip_reasons = {
            s.get("reason")
            for s in result_x.get("draft_skips") or []
            if s.get("campaign") == "tuesday_meditation"
        }
        self.assertIn("holiday_skip", skip_reasons)

        # Non-Tuesday → not_tuesday skip
        as_of_wed = datetime(2026, 8, 5, 10, 0, tzinfo=ZoneInfo("America/Chicago"))
        result_w = pipeline.generate_batch(source="fixture", as_of=as_of_wed)
        skip_w = {
            s.get("reason")
            for s in result_w.get("draft_skips") or []
            if s.get("campaign") == "tuesday_meditation"
        }
        self.assertIn("not_tuesday", skip_w)

    def test_meditation_host_iso_week_rotation_and_shared_block(self) -> None:
        """Roster rotates by ISO week; Today + tuesday_meditation share one block helper."""
        from marketing import captions
        from marketing.meditation import (
            MeditationHost,
            host_for_day,
            iso_week_rotation_index,
            load_host_roster,
            meditation_event_block,
            parse_host_from_event,
        )
        from marketing.models import Event

        roster = load_host_roster()
        self.assertGreaterEqual(len(roster), 4)

        tue_a = date(2026, 8, 11)  # next Tuesday after Aug 4
        tue_b = date(2026, 8, 18)
        self.assertEqual(tue_a.weekday(), 1)
        self.assertEqual(tue_b.weekday(), 1)
        self.assertNotEqual(
            iso_week_rotation_index(tue_a, len(roster)),
            iso_week_rotation_index(tue_b, len(roster)),
        )
        host_a = host_for_day(tue_a)
        host_b = host_for_day(tue_b)
        self.assertIsNotNone(host_a)
        self.assertIsNotNone(host_b)
        self.assertNotEqual(host_a, host_b)

        block_a = meditation_event_block(day=tue_a)
        block_b = meditation_event_block(day=tue_b)
        self.assertIn(f"With {host_a.practitioner} · {host_a.style}", block_a)
        self.assertIn(f"With {host_b.practitioner} · {host_b.style}", block_b)
        self.assertNotEqual(block_a, block_b)

        # Shared helper: Today meditation block == tuesday_meditation block for same day
        med = Event(
            id=99,
            title="Free Community Meditation",
            start_date=f"{tue_a.isoformat()} 19:00:00",
            end_date=f"{tue_a.isoformat()} 20:00:00",
            url="https://shopsacredground.com/event/free-community-meditation-2/",
        )
        today_text = captions.caption_today([med], "facebook", tue_a)["text"]
        solo_text = captions.caption_tuesday_meditation("facebook", tue_a)["text"]
        self.assertIn(block_a, today_text)
        self.assertIn(block_a, solo_text)

        # TEC-embedded host wins over roster
        tec = Event(
            id=1,
            title="Free Community Meditation",
            start_date=f"{tue_a.isoformat()} 19:00:00",
            end_date=f"{tue_a.isoformat()} 20:00:00",
            url="https://shopsacredground.com/event/free-community-meditation/",
            description="With Pat Sample · Crystal bowl stillness. All are welcome.",
        )
        parsed = parse_host_from_event(tec)
        self.assertEqual(
            parsed,
            MeditationHost(practitioner="Pat Sample", style="Crystal bowl stillness"),
        )
        self.assertIn(
            "With Pat Sample · Crystal bowl stillness",
            meditation_event_block(day=tue_a, event=tec),
        )

        # Empty roster → block without With line (still usable)
        bare = meditation_event_block(day=tue_a, roster=[])
        self.assertEqual(
            bare,
            "• Free Community Meditation\n"
            "All are welcome\n"
            "No sign-up needed\n"
            "Doors close at 7:05pm",
        )

    def test_week_ahead_horizon_is_two_days(self) -> None:
        from marketing import classify
        from marketing.models import Event
        from marketing.paths import settings

        wa = (settings().get("campaigns") or {}).get("week_ahead") or {}
        self.assertEqual(int(wa.get("horizon_days") or 0), 2)
        self.assertEqual(int(wa.get("horizon_start_offset_days") or 0), 1)
        self.assertIn("2", str(wa.get("label") or ""))

        events = [
            Event(
                id=i,
                title=f"Event {d.isoformat()}",
                start_date=f"{d.isoformat()} 12:00:00",
                end_date=f"{d.isoformat()} 17:00:00",
                url=f"https://shopsacredground.com/e/{i}/",
            )
            for i, d in enumerate(
                [
                    date(2026, 8, 6),
                    date(2026, 8, 7),
                    date(2026, 8, 8),
                    date(2026, 8, 9),
                ],
                start=1,
            )
        ]
        window_start = date(2026, 8, 6)
        ahead = classify.events_next_days(events, window_start, days=2)
        days = classify.event_calendar_days(ahead)
        self.assertEqual(days, [date(2026, 8, 6), date(2026, 8, 7)])
        # Clamp never widens even if extra days sneak in
        wide = events + [
            Event(
                id=99,
                title="Too far",
                start_date="2026-08-08 12:00:00",
                end_date="2026-08-08 13:00:00",
                url="https://shopsacredground.com/e/99/",
            )
        ]
        clamped = classify.clamp_events_to_horizon(wide, window_start, 2)
        self.assertEqual(
            classify.event_calendar_days(clamped),
            [date(2026, 8, 6), date(2026, 8, 7)],
        )

    def test_night_creatives_rotate_not_storefront_only(self) -> None:
        from marketing.atmosphere import atmosphere_config, nighttime_plan

        atmosphere_config.cache_clear()
        creatives = 0
        storefronts = 0
        ids = []
        for i in range(20):
            d = date(2026, 8, 1) + timedelta(days=i)
            plan = nighttime_plan(d)
            if plan.get("mode") in ("full_moon", "holiday"):
                continue
            cid = str(plan.get("creative_id") or "")
            url = str(plan.get("image_url") or "")
            ids.append(cid)
            self.assertNotIn("Screenshot-2026-03-05", url)
            if "storefront" in cid:
                storefronts += 1
            else:
                creatives += 1
                self.assertTrue(
                    "creative" in url
                    or "ai_generated" in url
                    or cid.endswith(("_night_watch", "_night_journey", "_night_om", "_night_silhouette"))
                    or bool(cid),
                    f"expected creative plate, got {cid} {url}",
                )
        self.assertGreaterEqual(creatives, 15)
        self.assertLessEqual(storefronts, 5)
        # Not stuck on one plate
        self.assertGreaterEqual(len(set(ids)), 8)

    def test_fb_ig_distinct_images_today_and_week_ahead(self) -> None:
        """Today + week_ahead: FB ≠ IG when the pool has 2+ options; meditation stays shared."""
        from marketing import images, pipeline, store
        from marketing.atmosphere import atmosphere_config, nighttime_plan
        from marketing.models import Event

        images.IMAGE_USAGE_PATH = os.path.join(self._tmpdir, "state", "image_usage.json")
        images.image_rules.cache_clear()
        images.morning_flyers.cache_clear()
        atmosphere_config.cache_clear()

        day = date(2026, 9, 2)  # Wednesday — no date flyer; multi-event rotation pool
        generic_multi = [
            Event(
                id=401,
                title="Crystal Browse Hour",
                start_date="2026-09-02 12:00:00",
                end_date="2026-09-02 14:00:00",
                url="https://shopsacredground.com/event/a/",
            ),
            Event(
                id=402,
                title="Tea & Chat",
                start_date="2026-09-02 15:00:00",
                end_date="2026-09-02 16:00:00",
                url="https://shopsacredground.com/event/b/",
            ),
        ]
        fb = images.plan_image(
            generic_multi, "today", day=day, platform="facebook"
        )
        ig = images.plan_image(
            generic_multi,
            "today",
            day=day,
            platform="instagram",
            exclude_urls=[fb.url or ""],
        )
        self.assertEqual(fb.rule, "multi_event_rotation")
        self.assertEqual(ig.rule, "multi_event_rotation")
        self.assertTrue(fb.url)
        self.assertTrue(ig.url)
        self.assertNotEqual(fb.url, ig.url)

        # Date-keyed morning flyers with dual variants: FB ≠ IG, both full-day.
        # Aug 6 gold standard may still be single-URL (temporary share OK).
        flyer_day = date(2026, 8, 6)
        f_fb = images.plan_image([], "today", day=flyer_day, platform="facebook")
        f_ig = images.plan_image(
            [],
            "today",
            day=flyer_day,
            platform="instagram",
            exclude_urls=[f_fb.url or ""],
        )
        self.assertEqual(f_fb.rule, "morning_flyer")
        self.assertEqual(f_ig.rule, "morning_flyer")
        self.assertTrue(f_fb.prebranded and f_ig.prebranded)
        # Primary only — never the eve-quantum priced alt.
        self.assertNotIn("eve-quantum", f_fb.url or "")
        self.assertIn("sg-morning-flyer-2026-08-06-today-collage", f_fb.url or "")
        # Dual-variant day (when configured): FB and IG must differ.
        from marketing import morning_flyers as mf

        dual = {
            "label": "Dual test",
            "covers": ["Tai Chi Gung with Sherry Gurley", "Tarot with Adie"],
            "url": "https://shopsacredground.com/wp-content/uploads/sg-morning-flyer-dual-a.png",
            "url_instagram": "https://shopsacredground.com/wp-content/uploads/sg-morning-flyer-dual-b.png",
            "prebranded": True,
        }
        fb_u, shared_fb = mf.select_flyer_url_for_platform(dual, "facebook")
        ig_u, shared_ig = mf.select_flyer_url_for_platform(dual, "instagram")
        self.assertFalse(shared_fb or shared_ig)
        self.assertNotEqual(fb_u, ig_u)
        self.assertEqual(fb_u, dual["url"])
        self.assertEqual(ig_u, dual["url_instagram"])
        self.assertNotIn("$", " ".join(dual["covers"]))

        # Specialty with multi-URL pool (massage) → different cards from same rule
        massage_day = [
            Event(
                id=403,
                title="Therapeutic Massage",
                start_date="2026-08-03 13:00:00",
                end_date="2026-08-03 15:00:00",
                url="https://shopsacredground.com/book/massage/",
            ),
            Event(
                id=404,
                title="Tarot with Tina",
                start_date="2026-08-03 12:00:00",
                end_date="2026-08-03 17:00:00",
                url="https://shopsacredground.com/book/tina/",
            ),
        ]
        m_day = date(2026, 8, 3)
        m_fb = images.plan_image(
            massage_day, "today", day=m_day, platform="facebook"
        )
        m_ig = images.plan_image(
            massage_day,
            "today",
            day=m_day,
            platform="instagram",
            exclude_urls=[m_fb.url or ""],
        )
        self.assertEqual(m_fb.rule, "massage")
        self.assertNotEqual(m_fb.url, m_ig.url)

        # Sound specialty pool → second platform takes another plate (no date flyer)
        sound = [
            Event(
                id=405,
                title="Gong Sound Bath",
                start_date="2026-09-07 19:00:00",
                end_date="2026-09-07 20:30:00",
                url="https://shopsacredground.com/events/gong/",
            ),
            Event(
                id=406,
                title="Tarot with Tina",
                start_date="2026-09-07 12:00:00",
                end_date="2026-09-07 17:00:00",
                url="https://shopsacredground.com/book/tarot/",
            ),
        ]
        s_day = date(2026, 9, 7)
        s_fb = images.plan_image(sound, "today", day=s_day, platform="facebook")
        s_ig = images.plan_image(
            sound,
            "today",
            day=s_day,
            platform="instagram",
            exclude_urls=[s_fb.url or ""],
        )
        self.assertEqual(s_fb.rule, "sound_healing")
        self.assertNotEqual(s_fb.url, s_ig.url)

        # Night week_ahead: FB ≠ IG on a normal creative night
        night = date(2026, 8, 5)
        n_fb = nighttime_plan(night, platform="facebook")
        n_ig = nighttime_plan(
            night,
            platform="instagram",
            exclude_urls=[str(n_fb.get("image_url") or "")],
        )
        self.assertTrue(n_fb.get("image_url"))
        self.assertTrue(n_ig.get("image_url"))
        self.assertNotEqual(n_fb.get("image_url"), n_ig.get("image_url"))
        # Same day without exclude is stable
        n_fb2 = nighttime_plan(night, platform="facebook")
        self.assertEqual(n_fb.get("image_url"), n_fb2.get("image_url"))

        wa_fb = images.plan_image([], "week_ahead", day=night, platform="facebook")
        wa_ig = images.plan_image(
            [],
            "week_ahead",
            day=night,
            platform="instagram",
            exclude_urls=[wa_fb.url or ""],
        )
        self.assertNotEqual(wa_fb.url, wa_ig.url)

        # Pipeline wiring: Today drafts get distinct images; meditation stays shared
        as_of = datetime(2026, 8, 4, 10, 0, tzinfo=ZoneInfo("America/Chicago"))
        result = pipeline.generate_batch(source="fixture", as_of=as_of)
        self.assertTrue(result["ok"])
        drafts = store.list_drafts()
        today_fb = next(
            d
            for d in drafts
            if d["campaign"] == "today" and d["platform"] == "facebook"
        )
        today_ig = next(
            d
            for d in drafts
            if d["campaign"] == "today" and d["platform"] == "instagram"
        )
        # Tuesday morning uses tuesday_daily (single URL) — IG may fall through
        self.assertTrue(today_fb["image"]["url"])
        self.assertTrue(today_ig["image"]["url"])

        tm_fb = next(
            d
            for d in drafts
            if d["campaign"] == "tuesday_meditation" and d["platform"] == "facebook"
        )
        tm_ig = next(
            d
            for d in drafts
            if d["campaign"] == "tuesday_meditation" and d["platform"] == "instagram"
        )
        self.assertEqual(tm_fb["image"]["url"], tm_ig["image"]["url"])

        # Usage ledger keeps both platform rows for today
        usage = images.load_image_usage()
        today_rows = [
            h
            for h in usage.get("history") or []
            if h.get("campaign") == "today" and h.get("date") == "2026-08-04"
        ]
        plats = {str(h.get("platform") or "") for h in today_rows}
        self.assertIn("facebook", plats)
        self.assertIn("instagram", plats)

    def test_week_ahead_closers_pool_and_day_rotation(self) -> None:
        from marketing import captions
        from marketing.paths import voice

        closers = list(voice().get("week_ahead_closers") or [])
        self.assertGreaterEqual(len(closers), 30)
        self.assertEqual(len(closers), len(set(closers)), "closers must be unique")
        door = "The door is always open...we will leave the light on"
        self.assertIn(door, closers)
        self.assertEqual(closers.count(door), 1)

        # Day-ordinal rotation: consecutive nights differ; same night is stable
        a = captions._week_ahead_closer("x", day=date(2026, 8, 5))
        b = captions._week_ahead_closer("y", day=date(2026, 8, 6))
        c = captions._week_ahead_closer("z", day=date(2026, 8, 5))
        self.assertEqual(a, c)
        self.assertNotEqual(a, b)
        # Across 30 nights we cover the full pool (or at least many distinct)
        picked = {
            captions._week_ahead_closer("n", day=date(2026, 8, 1) + timedelta(days=i))
            for i in range(30)
        }
        self.assertEqual(len(picked), 30)

    def test_stale_week_ahead_draft_detected(self) -> None:
        from marketing import store

        stale_exterior = {
            "campaign": "week_ahead",
            "events": [
                {"start_date": "2026-08-06 12:00:00"},
                {"start_date": "2026-08-07 12:00:00"},
            ],
            "image": {
                "rule": "week_ahead_exterior",
                "url": "https://shopsacredground.com/wp-content/uploads/Screenshot-2026-03-05-at-9.20.15-AM.png",
            },
        }
        # Current shape: tonight evening + next 2 days (3 calendar days) + night creative
        fresh_with_tonight = {
            "campaign": "week_ahead",
            "events": [
                {"start_date": "2026-08-06 19:00:00"},
                {"start_date": "2026-08-07 12:00:00"},
                {"start_date": "2026-08-08 12:00:00"},
            ],
            "image": {
                "rule": "week_ahead_creative_milky_way",
                "url": "https://shopsacredground.com/wp-content/uploads/sg-night-creative-milky-way.png",
            },
        }
        fresh_two_day = {
            "campaign": "week_ahead",
            "events": [
                {"start_date": "2026-08-07 12:00:00"},
                {"start_date": "2026-08-08 12:00:00"},
            ],
            "image": {
                "rule": "week_ahead_creative_milky_way",
                "url": "https://shopsacredground.com/wp-content/uploads/sg-night-creative-milky-way.png",
            },
        }
        # More than horizon+1 (tonight + 2 forward) is the old oversized window
        stale_too_many_days = {
            "campaign": "week_ahead",
            "events": [
                {"start_date": "2026-08-06 12:00:00"},
                {"start_date": "2026-08-07 12:00:00"},
                {"start_date": "2026-08-08 12:00:00"},
                {"start_date": "2026-08-09 12:00:00"},
            ],
            "image": {
                "rule": "week_ahead_creative_milky_way",
                "url": "https://shopsacredground.com/wp-content/uploads/sg-night-creative-milky-way.png",
            },
        }
        self.assertTrue(store.is_stale_week_ahead_draft(stale_exterior, 2))
        self.assertTrue(store.is_stale_week_ahead_draft(stale_too_many_days, 2))
        self.assertFalse(store.is_stale_week_ahead_draft(fresh_with_tonight, 2))
        self.assertFalse(store.is_stale_week_ahead_draft(fresh_two_day, 2))

    def test_morning_flyer_no_price_rule(self) -> None:
        from marketing import morning_flyers as mf
        from marketing.models import Event

        self.assertTrue(mf.text_has_price("$99"))
        self.assertTrue(mf.text_has_price("Sessions from $55"))
        self.assertTrue(mf.text_has_price("ticket: $20"))
        self.assertFalse(mf.text_has_price("Free Community Meditation"))
        self.assertFalse(mf.text_has_price("Reflexology Reset with Cheryl"))

        priced = Event(
            id=1,
            title="The Reflexology Reset",
            start_date="2026-08-07 11:00:00",
            end_date="2026-08-07 15:00:00",
            url="https://shopsacredground.com/cheryl-2/",
            cost="$99",
        )
        copy = mf.build_flyer_copy(date(2026, 8, 7), [priced])
        blob = " ".join(
            [copy["label"], *copy["covers"], *copy["lines"], copy["primary"], priced.cost]
        )
        # Graphic copy must be price-free even when Event.cost is set.
        self.assertFalse(mf.text_has_price(copy["label"]))
        for part in copy["covers"] + copy["lines"] + [copy["primary"]]:
            self.assertFalse(mf.text_has_price(part), part)
        prompt = mf.build_generation_prompt(date(2026, 8, 7), copy)
        self.assertIn("do NOT include any prices", prompt)
        self.assertIn("Thursday-style", prompt)
        self.assertIn("VARIANT A / Facebook", prompt)
        prompt_b = mf.build_generation_prompt(
            date(2026, 8, 7), copy, variant=mf.VARIANT_B
        )
        self.assertIn("VARIANT B / Instagram", prompt_b)
        self.assertIn("MORE visual pop", prompt_b)
        self.assertIn("flat single-color", prompt_b)
        self.assertIn("do NOT include any prices", prompt_b)
        # Multi-event → thursday_cards; single-event days may roll artistic.
        self.assertEqual(
            mf.choose_layout_style(date(2026, 8, 7), [priced]),
            mf.LAYOUT_THURSDAY,
        )
        artistic_day = date(2026, 8, 12)  # ordinal % 4 == 0
        self.assertEqual(
            mf.choose_layout_style(artistic_day, [priced]),
            mf.LAYOUT_ARTISTIC,
        )
        art_prompt = mf.build_generation_prompt(
            artistic_day, copy, layout=mf.LAYOUT_ARTISTIC
        )
        self.assertIn("artistic single-event hero", art_prompt)
        self.assertIn("do NOT include any prices", art_prompt)
        # cost itself is priced — we only assert flyer fields
        self.assertTrue(mf.text_has_price(priced.cost))
        self.assertNotIn(priced.cost, copy["label"])
        self.assertNotIn("$", " ".join(copy["covers"] + copy["lines"]))

        with self.assertRaises(ValueError):
            mf.assert_price_free("Book for $55 today")

    def test_morning_flyer_ensure_empty_day_and_prebranded(self) -> None:
        from marketing import images, morning_flyers as mf

        images.IMAGE_USAGE_PATH = os.path.join(self._tmpdir, "state", "image_usage.json")
        images.image_rules.cache_clear()
        images.morning_flyers.cache_clear()

        empty_day = date(2026, 9, 15)
        info = mf.ensure_flyer_for_day(empty_day, [], force=True)
        self.assertEqual(info["action"], "created")
        self.assertTrue(info["needs_upload"])
        entry = info["entry"]
        self.assertTrue(entry.get("prebranded"))
        self.assertTrue(entry.get("empty_day"))
        self.assertIn("visit", (entry.get("label") or "").lower())
        self.assertTrue(os.path.isfile(info["local"]))

        # Date-keyed selection only when public URL is set.
        plan_no_url = images.plan_image([], "today", day=empty_day)
        self.assertNotEqual(plan_no_url.rule, "morning_flyer")

        mf.set_flyer_url(
            empty_day,
            "https://shopsacredground.com/wp-content/uploads/sg-morning-flyer-test-visit-a.png",
            media_id=99999,
            platform="facebook",
        )
        mf.set_flyer_url(
            empty_day,
            "https://shopsacredground.com/wp-content/uploads/sg-morning-flyer-test-visit-b.png",
            media_id=99998,
            platform="instagram",
        )
        images.morning_flyers.cache_clear()
        plan = images.plan_image([], "today", day=empty_day, platform="facebook")
        self.assertEqual(plan.rule, "morning_flyer")
        self.assertTrue(plan.prebranded)
        self.assertTrue(images.skip_brand_overlays(plan))
        plan_ig = images.plan_image([], "today", day=empty_day, platform="instagram")
        self.assertNotEqual(plan.url, plan_ig.url)

        # Existing day is not regenerated without --force
        again = mf.ensure_flyer_for_day(empty_day, [], force=False)
        self.assertEqual(again["action"], "exists")
        self.assertFalse(again["needs_upload"])

    def test_config_morning_flyers_price_free(self) -> None:
        """Repo morning_flyers.json labels/covers must never carry $ prices."""
        from marketing import morning_flyers as mf

        # Read the real committed config (not the tmp copy).
        real = os.path.join(ROOT, "config", "morning_flyers.json")
        with open(real, encoding="utf-8") as fh:
            import json

            data = json.load(fh)
        self.assertIn("NEVER include", data.get("notes") or "")
        self.assertIn("DIFFERENT full-day flyer", data.get("notes") or "")
        for day_key, entry in (data.get("flyers") or {}).items():
            bits = [str(entry.get("label") or "")]
            bits.extend(str(c) for c in (entry.get("covers") or []))
            for b in bits:
                self.assertFalse(
                    mf.text_has_price(b),
                    f"{day_key} has price-like text: {b!r}",
                )
            # Dual public variants (when both set) must differ and stay price-free URLs.
            fb, ig = mf.resolve_flyer_urls(entry)
            if entry.get("url_instagram") or (
                isinstance(entry.get("urls"), list) and len(entry.get("urls") or []) >= 2
            ):
                self.assertTrue(fb and ig)
                if day_key != "2026-08-06":
                    self.assertNotEqual(
                        fb,
                        ig,
                        f"{day_key} FB/IG morning flyer URLs must differ when dual variants exist",
                    )
                self.assertNotIn("$", fb)
                self.assertNotIn("$", ig)

    def test_morning_flyer_dual_variants_same_covers(self) -> None:
        """generate-morning-flyers produces A/B locals with identical covers; FB≠IG URLs."""
        from marketing import images, morning_flyers as mf
        from marketing.models import Event

        images.IMAGE_USAGE_PATH = os.path.join(self._tmpdir, "state", "image_usage.json")
        images.morning_flyers.cache_clear()

        day = date(2026, 9, 20)
        events = [
            Event(
                id=501,
                title="Tai Chi Gung with Sherry Gurley",
                start_date="2026-09-20 12:00:00",
                end_date="2026-09-20 13:00:00",
                url="https://shopsacredground.com/event/tai/",
            ),
            Event(
                id=502,
                title="Tarot with Adie",
                start_date="2026-09-20 12:00:00",
                end_date="2026-09-20 17:00:00",
                url="https://shopsacredground.com/event/adie/",
                cost="$55",
            ),
        ]
        info = mf.ensure_flyer_for_day(day, events, force=True)
        self.assertEqual(info["action"], "created")
        entry = info["entry"]
        self.assertTrue(entry.get("local"))
        self.assertTrue(entry.get("local_instagram"))
        self.assertNotEqual(entry.get("local"), entry.get("local_instagram"))
        self.assertEqual(
            list(entry.get("covers") or []),
            [e.title for e in mf.pick_events_for_flyer(events)],
        )
        for part in entry.get("covers") or []:
            self.assertFalse(mf.text_has_price(part))
            self.assertNotIn("$", part)
        self.assertTrue(os.path.isfile(info["local"]))
        self.assertTrue(os.path.isfile(info["local_instagram"]))

        mf.set_flyer_url(
            day,
            "https://shopsacredground.com/wp-content/uploads/sg-morning-flyer-dual-a.png",
            media_id=90001,
            platform="facebook",
        )
        mf.set_flyer_url(
            day,
            "https://shopsacredground.com/wp-content/uploads/sg-morning-flyer-dual-b.png",
            media_id=90002,
            platform="instagram",
        )
        images.morning_flyers.cache_clear()
        plan_fb = images.plan_image(events, "today", day=day, platform="facebook")
        plan_ig = images.plan_image(
            events,
            "today",
            day=day,
            platform="instagram",
            exclude_urls=[plan_fb.url or ""],
        )
        self.assertEqual(plan_fb.rule, "morning_flyer")
        self.assertEqual(plan_ig.rule, "morning_flyer")
        self.assertNotEqual(plan_fb.url, plan_ig.url)
        self.assertNotIn("$", plan_fb.url or "")
        self.assertNotIn("$", plan_ig.url or "")


if __name__ == "__main__":
    unittest.main()
