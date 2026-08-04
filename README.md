# Sacred Ground Marketing Autopilot v1

Event-driven social marketing drafts from WordPress / The Events Calendar.

When events exist in WordPress, Autopilot creates reviewable drafts for:

- **Today at Sacred Ground** — daily Facebook + Instagram (7:00 AM CT)
- **Tuesday Free Community Meditation** — every Tuesday 4:00 PM CT (FB + IG); skips only Christmas Eve/Day and New Year’s Eve/Day
- **This Week at Sacred Ground** — weekly roundup (FB + IG)
- **Week Ahead** — daily evening planner (7:00 PM CT)
- **Special Event Spotlight** — Holistic Fair / special one-time events (stronger caption + reminder schedule)

**Phase 1 (default): drafts only.** Nothing publishes live until you approve a test batch.

## Quick start

```bash
cd ~/Projects/sacred-ground-marketing-autopilot

# Generate draft batch (TEC REST → live cache → fixtures)
python3 -m marketing run --source auto

# Or from the WordPress cache already in this repo
python3 -m marketing run --source cache

# Human review queue
python3 -m marketing review

# Approve one draft (still does not publish in Phase 1)
python3 -m marketing approve DRAFT_ID

# Pause / resume autopilot
python3 -m marketing pause
python3 -m marketing resume

# Manual override: skip a fingerprint so it won't regenerate
python3 -m marketing skip --fingerprint FINGERPRINT --reason "manual post already live"

# Phase 2+ publish helpers (need ZERNIO_API_KEY)
python3 -m marketing publish-today
python3 -m marketing publish-tuesday-meditation
python3 -m marketing publish-week-ahead
```

Live Cloud Agent schedules are documented in `AUTOMATION-DRAFT.md` (Today 7am · Tuesday meditation 4pm · Week-ahead 7pm).

HTTP (optional local review surface):

```bash
python3 -m api.cli serve --port 8792
# GET /health  GET /api/v1/summary  GET /api/v1/drafts
```

## Phases

| Phase | Behavior |
|---|---|
| **1 — Drafts** (default) | Create + store drafts inside Sacred Ground Marketing. No ML Social publish. |
| **2 — Schedule after approval** | Approved drafts become a Marketing Package; the **Workflow Engine** records Founder approval and hands the package to ML Social (Social Distribution Adapter). Autopilot must not bypass the Engine. |
| **3 — Autopilot** | Trusted event types may auto-approve *inside SG policy*; the Engine still releases the package to the adapter. |

```bash
python3 -m marketing set-phase 1
```

## Guarantees

- No duplicate posts (fingerprint + posted ledger)
- No old events (America/Chicago calendar day)
- No missing links (events without URL are excluded)
- No generic captions (Sacred Ground voice + forbidden-phrase guard)
- Event featured image when available; otherwise a creative image prompt
- Draft status stored; posted history tracked
- Manual override + pause switch
- Spotlights only for Holistic Fair–class specials (not every starred reading)

## Source of truth

- **Events:** The Events Calendar REST  
  `https://shopsacredground.com/wp-json/tribe/events/v1/events`
- **Fallback cache:** `data/cache/live_events.json` (refreshed from WordPress when REST is unreachable)
- **Event inclusion:** TEC `publish` only. Free + evening events are included. `exclude_title_substrings` is for rare staff-only titles — never community meditation. Tuesday Free Community Meditation is guaranteed (TEC event or configured stub).
- **Distribution (Phase 2+):** Workflow Engine releases an approved Marketing Package to ML Social (`social_publish`) — last mile only. Account IDs in `config/accounts.json`. See Sacred Ground **Distribution Rule** (`Sacred-Ground-Social-Distribution-Adapter-v1.0.md`).
- **This repo** owns draft state and fingerprints under Marketing; Founder approval and adapter handoff are Workflow Engine responsibilities

## First live batch (2026-07-09)

Generated from WordPress (43 upcoming events → 40 valid):

| Campaign | Platforms | Notes |
|---|---|---|
| Today | FB + IG | Tai Chi Gung, Tarot With Adie, Quantum Alignment Series |
| This Week | FB + IG | Roundup through Jul 12 incl. Summer Holistic Fair |
| Spotlight | FB + IG | Summer Holistic Fair + day-before reminder |
| Skipped | — | Only intentional title excludes (e.g. internal closed); free community meditation is always kept |

All drafts: `approval_status=pending`, `publish_blocked_reason=phase_1_drafts_only`.

## Layout

```
config/          voice, accounts, defaults, reels.json + reel_scripts.json
marketing/       ingest → classify → captions → images → schedule → store
api/             optional read API for Dashboard later
data/drafts/     draft JSON files
data/cache/      live WordPress event export
data/state/      pause, phase, posted ledger, overrides
data/fixtures/   offline sample events for tests
data/reels/      TikTok / YouTube Shorts scripts (HeyGen path)
assets/heygen/   store backgrounds for AI-Deneene reels
scripts/         one-shot runners + WP import + heygen_dry_run.py
```

**Reels (TikTok / YouTube Shorts):** separate from FB/IG Zernio publish. See `REELS-PLAN.md`. Dry-run: `python3 scripts/heygen_dry_run.py`.

See `API-CONTRACT.md` for the draft artifact shape.
