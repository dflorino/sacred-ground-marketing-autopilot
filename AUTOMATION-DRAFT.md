# Automation draft — SG Today 7am Social (LIVE)

Daily Today posts for Sacred Ground Marketing Autopilot.

**Status: auto_publish ON.** Every morning at 7:00 AM America/Chicago: generate Today FB+IG and publish via Zernio.

## Image rules (locked)

| Situation | Image used |
|-----------|------------|
| Specialty match (tarot, reiki, etc.) | Rule library URL (7-day no-repeat) |
| Multi-event / no specialty | Store exterior or rotation rules |
| **Empty calendar** | Store exterior + visit/brand caption |

Never post without a real media URL.

## Daily commands (Cloud Agent)

```bash
python3 -m marketing run --source live-strict
python3 -m marketing publish-today
```

Secret required: **`ZERNIO_API_KEY`** (Cursor Cloud Agent secrets).

## Agent instructions

```
You are running Sacred Ground Marketing Autopilot for the daily Today campaign.

Hard rules:
1. Timezone context is America/Chicago. Shop-local post time is 7:00 AM America/Chicago.
2. Checkout this repo and run from the project root.
3. Refresh live WordPress / The Events Calendar only:
   python3 -m marketing run --source live-strict
4. If the WordPress/TEC refresh fails: create NO new drafts, do not use stale cache, report wordpress_refresh_failed, and STOP. Do not publish.
5. Never overwrite or recreate a draft that is edited, approved, rejected, skipped, locked, or otherwise reviewed. Fingerprints that already exist must be left alone.
6. Today campaign has auto_publish=true. After a successful live-strict run, publish today's posts:
   python3 -m marketing publish-today
   This uses ZERNIO_API_KEY from Cloud Agent secrets. Do not skip publish unless step 4 failed or the key is missing.
7. Only Facebook + Instagram Today posts. Do not publish week / week_ahead / spotlight.
8. After the run, summarize: events (or empty-day visit), platforms, image URL/rule, publish results (posted/scheduled/errors). Include Zernio post links when available.
```

## Editor checklist — morning

1. Name: **SG Today 7am Social**
2. Schedule: **7:00 AM** · timezone **America/Chicago**
3. Repo: `dflorino/sacred-ground-marketing-autopilot` · branch `main`
4. Secret: `ZERNIO_API_KEY`
5. Only **one** Active automation at 7am (disable duplicates)
6. Status: **Active**

---

# Automation draft — SG Week-Ahead 7pm Social (LIVE)

Daily next-3-days evening planner posts (Facebook + Instagram).

**Status: auto_publish ON.** Every evening at **7:00 PM America/Chicago**.

Image: rotate the 3 founder exterior storefront photos. Schedule list lives in the caption only.

## Daily commands (Cloud Agent)

```bash
python3 -m marketing run --source live-strict
python3 -m marketing publish-week-ahead
```

Do **not** call `publish-today` in this automation (morning job owns that).

## Agent instructions

```
You are running Sacred Ground Marketing Autopilot for the daily week-ahead (evening planner) campaign.

Hard rules:
1. Timezone context is America/Chicago. Shop-local post time is 7:00 PM America/Chicago.
2. Checkout this repo and run from the project root.
3. Refresh live WordPress / The Events Calendar only:
   python3 -m marketing run --source live-strict
4. If the WordPress/TEC refresh fails: create NO new drafts, do not use stale cache, report wordpress_refresh_failed, and STOP. Do not publish.
5. Never overwrite or recreate a draft that is edited, approved, rejected, skipped, locked, or otherwise reviewed.
6. week_ahead has auto_publish=true. After a successful live-strict run, publish tonight's week-ahead posts only:
   python3 -m marketing publish-week-ahead
   Uses ZERNIO_API_KEY from Cloud Agent secrets. Do not call publish-today.
7. Caption lists the next 2 days only. Image from night atmosphere pool (creative night skies + seasonal/holiday storefronts) — never morning specialty art.
8. If there are no events in the next 2 days, report skip and do not invent events.
9. Summarize: event count, platforms, image URL, publish results.
```

## Editor checklist — evening

1. Name: **SG Week-Ahead 7pm Social**
2. Schedule: **7:00 PM** · confirm **Next run … 7:00 PM CDT** (not 2:00 PM / wrong UTC)
3. Repo: `dflorino/sacred-ground-marketing-autopilot` · `main`
4. Secret: `ZERNIO_API_KEY` (same as morning)
5. Status: **Active**
6. Keep separate from the 7am Today automation

---

# Automation draft — SG Tuesday Meditation 4pm Social (LIVE)

Dedicated Free Community Meditation posts every Tuesday (Facebook + Instagram).

**Status: auto_publish ON.** Every **Tuesday at 4:00 PM America/Chicago**.

**Holiday skips (Chicago local date only):** Christmas Eve, Christmas Day, New Year’s Eve, New Year’s Day. All other Tuesdays must publish — no fail.

Image: rotate meditation pool (Om, silhouette, metaphysical journey, sg-morning-meditation) with 7-day no-repeat.

## Weekly commands (Cloud Agent)

```bash
python3 -m marketing run --source live-strict
python3 -m marketing publish-tuesday-meditation
```

Do **not** call `publish-today` or `publish-week-ahead` in this automation.

## Agent instructions

```
You are running Sacred Ground Marketing Autopilot for the Tuesday Free Community Meditation campaign.

Hard rules:
1. Timezone context is America/Chicago. Shop-local post time is 4:00 PM America/Chicago on Tuesdays only.
2. Checkout this repo and run from the project root.
3. Refresh live WordPress / The Events Calendar only:
   python3 -m marketing run --source live-strict
4. If the WordPress/TEC refresh fails: create NO new drafts, do not use stale cache, report wordpress_refresh_failed, and STOP. Do not publish.
5. Never overwrite or recreate a draft that is edited, approved, rejected, skipped, locked, or otherwise reviewed.
6. If the run reports draft_skips with reason holiday_skip for tuesday_meditation: that is expected on Christmas Eve, Christmas Day, New Year's Eve, or New Year's Day — report skip and STOP (do not invent a post).
7. If today is not Tuesday, report not_tuesday and STOP.
8. tuesday_meditation has auto_publish=true. After a successful live-strict run on a non-holiday Tuesday, publish today's meditation posts only:
   python3 -m marketing publish-tuesday-meditation
   Uses ZERNIO_API_KEY from Cloud Agent secrets. Do not call publish-today or publish-week-ahead.
9. Caption is the dedicated meditation post (daytime meditation block: Free Community Meditation / With [Practitioner] · [Style] from config/meditation_hosts.json ISO-week rotation / All are welcome / No sign-up needed / Doors close at 7:05pm from config/settings.json tuesday_community_meditation.doors_close_display). No door/light goodnight closer. No o'clock. Not the morning Today lineup. Do not regenerate or republish an already-published Tuesday (e.g. leave Aug 4 2026 as-is).
10. Image from the meditation pool only (Om / silhouette / metaphysical journey / sg-morning-meditation).
11. Summarize: platforms, image URL, scheduledFor (should be 4:00 PM America/Chicago unless already past), Zernio post IDs/links.
```

## Editor checklist — Tuesday 4pm

1. Name: **SG Tuesday Meditation 4pm Social**
2. Schedule: **Every Tuesday · 4:00 PM** · timezone **America/Chicago**
3. Repo: `dflorino/sacred-ground-marketing-autopilot` · branch `main`
4. Secret: `ZERNIO_API_KEY` (same as Today / week-ahead)
5. Status: **Active**
6. Keep separate from the 7am Today and 7pm week-ahead automations

---

# Automation draft — SG Daily Reels 10:30am (SCAFFOLD — NOT LIVE)

Daily AI-Deneene short-form video for **Instagram Reels + Facebook Reels**.

**Status: NOT Active.** Scaffold only. `daily_reel.auto_publish=false`. Do **not** turn this automation on until a 9:16 video has been posted successfully via Zernio/ML Social (or Meta Reels) end-to-end.

Suggested time: **10:30 AM America/Chicago** (late morning — clears 7am Today, 4pm Tuesday meditation, 7pm week-ahead image jobs).

TikTok / YouTube Shorts = optional later (same asset).

## What works today (do not confuse)

| Path | Status |
|---|---|
| FB+IG **image** posts (Today / week-ahead / Tuesday meditation) via Zernio | **Live** |
| HeyGen generate → hosted MP4 → Zernio/Meta **Reels** | **Not wired** |

## Secrets (when ready)

- `ZERNIO_API_KEY` — social publish (already used by image jobs)
- `HEYGEN_API_KEY`, `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID` — only if API generate (never commit)

## Commands (scaffold / dry only)

```bash
python3 -m marketing reels-status
python3 scripts/heygen_dry_run.py
```

There is **no** `publish-daily-reel` command yet — do not invent one in Cloud Agent until video publish is implemented and tested.

## Agent instructions (future — do not activate)

```
You are running Sacred Ground Marketing Autopilot for the daily_reel campaign (IG + FB Reels).

Hard rules:
1. Timezone America/Chicago. Suggested post time 10:30 AM.
2. Format must be 9:16 video — never post a still as a Reel from this job.
3. Do NOT call publish-today, publish-week-ahead, or publish-tuesday-meditation.
4. auto_publish is false until Founder enables it after a successful video publish proof.
5. If video URL or Reels publish API is missing: report blocked and STOP. Do not fall back to image posts.
6. Caption from welcome-batch rotation or Observatory beneath_surface (yesterday).
7. Summarize: script id, platforms (instagram_reels + facebook_reels), video URL, publish results or blockers.
```

## Editor checklist — only after video path works

1. Name: **SG Daily Reels 10:30am**
2. Schedule: **Daily · 10:30 AM** · timezone **America/Chicago**
3. Repo: `dflorino/sacred-ground-marketing-autopilot` · `main`
4. Secrets: `ZERNIO_API_KEY` (+ optional `HEYGEN_*`)
5. Status: **Inactive** until Founder approves first auto run
6. Keep separate from image automations (7am / 4pm / 7pm)
