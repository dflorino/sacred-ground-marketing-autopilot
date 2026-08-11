# Cursor Automations — expected live schedule (America/Chicago)

Code schedule shipped in `87f5375`. Cursor Cloud Automations **cannot be listed or edited from agent chat** (Automations skill is creation-only; no inventory API). Founder must apply the clicks below in **Cursor → Automations** (or Agents Window → Automations).

| Expected name | Cron / time | Commands | Status |
|---|---|---|---|
| **SG Morning Today 9am Social** | Daily **9:00 AM** America/Chicago (`0 9 * * *` in that TZ — confirm TZ is Chicago, not UTC) | `generate-morning-flyers --start-offset 0 --days 2 --source live-strict` → `run --source live-strict` → `publish-today` | **Edit existing** morning job; disable any leftover 7am/10am duplicate |
| **SG Afternoon Spotlight 5pm Social** | Daily **5:00 PM** America/Chicago (`0 17 * * *`) | `run --source live-strict` → `publish-afternoon-spotlight` | **Create if missing** |
| **SG Week-Ahead 7pm Social** | Daily **7:00 PM** America/Chicago (`0 19 * * *`) | `run --source live-strict` → `publish-week-ahead` | **Leave intact** — only verify Next run shows 7:00 PM CT |
| **SG Tuesday Meditation 4pm Social** | **Tue 4:00 PM** America/Chicago (`0 16 * * 2`) | `run --source live-strict` → `publish-tuesday-meditation` | **Leave intact** — only verify Tuesday 4:00 PM CT |
| SG Daily Reels 10:30am | Daily 10:30 AM (scaffold) | none (not wired) | **Inactive** — do not activate |

Secret on all live image jobs: **`ZERNIO_API_KEY`**. Repo: `dflorino/sacred-ground-marketing-autopilot` · branch `main`.

## Founder clicks — morning (rename + 9am)

1. Open **Cursor → Automations**.
2. Find the morning job (likely **SG Morning Tomorrow 9am Social** / old 7am name).
3. **Rename** → **SG Morning Today 9am Social**.
4. **Schedule** → **9:00 AM** · timezone **America/Chicago** (confirm Next run is 9:00 AM CT — not 7:00, not 10:00, not UTC).
5. **Instructions / prompt** → paste the morning Agent instructions block below (today+tomorrow + flyer ensure + `publish-today` only).
6. Confirm commands are `publish-today` (not week-ahead / afternoon). Campaign key stays `today`.
7. Disable any second Active automation still on 7:00 AM or 10:00 AM.
8. Save · Status **Active**.

**Timing note (Aug 9, 2026):** Code + Zernio scheduledFor for Sunday morning were **~9:06 AM CT** (cloud agent lag after a 9:00 trigger). If Facebook looked like 10am, verify the Automation schedule is still 9:00 America/Chicago — agents cannot list/edit Automations from chat.

## Founder clicks — afternoon spotlight (create if missing)

1. Automations → **New automation**.
2. Name: **SG Afternoon Spotlight 5pm Social**.
3. Trigger: schedule · **Every day · 5:00 PM** · **America/Chicago**.
4. Repo/branch: `dflorino/sacred-ground-marketing-autopilot` / `main`.
5. Secret: `ZERNIO_API_KEY`.
6. Instructions → paste the afternoon Agent instructions block below.
7. Save · Status **Active**.
8. Do **not** change week-ahead 7pm or Tuesday 4pm while creating this.

## Founder clicks — verify only (do not retune)

1. **SG Week-Ahead 7pm Social** — Next run **7:00 PM** America/Chicago; commands end with `publish-week-ahead`.
2. **SG Tuesday Meditation 4pm Social** — **Tuesday · 4:00 PM** America/Chicago; commands end with `publish-tuesday-meditation`.

---

# Automation draft — SG Morning Today 9am Social (LIVE)

Daily morning posts for Sacred Ground Marketing Autopilot.

**Status: auto_publish ON.** Every morning at **9:00 AM America/Chicago**: generate FB+IG promoting **today’s full TEC slate**, then **tomorrow**, and publish via Zernio.

Campaign key stays `today` / CLI `publish-today` for compatibility. Content: `include_publish_day: true` + `target_offset_days: 1` (not evening-only). On-image word: `TODAY` when the flyer is publish-day dated; `TOMORROW` when tomorrow-only; skip overlays on prebranded flyers. Caption opener is today-first when today has events — never lead with “tonight” at 9am when daytime sessions exist. Keep `schedule_local_time` at `09:00` unless Founder explicitly wants 10am.

## Image rules (locked)

| Situation | Image used |
|-----------|------------|
| **Date flyer in `morning_flyers.json`** | Thursday-style **equal-card** prebranded flyer (preferred) |
| Specialty match (tarot, reiki, etc.) | Rule library URL (7-day no-repeat) — only if no date flyer URL |
| Multi-event / no specialty | Rotation rules — only if no date flyer |
| **Empty calendar** | Warm visit flyer (generate-if-missing) + visit caption — not storefront-only |

**Equal cards:** multi-event flyers must give every practitioner the same card size (Aug 6 gold standard). Never hero + tiny corner secondary.

**Never put prices on morning flyers** — no `$`, dollar amounts, or ticket costs on the graphic.

Never post without a real media URL.

## Daily commands (Cloud Agent)

```bash
# Prefer weekly prebuild. Morning job ensures today + tomorrow flyers.
python3 -m marketing generate-morning-flyers --days 7 --source live-strict
# Or today+tomorrow only:
# python3 -m marketing generate-morning-flyers --start-offset 0 --days 2 --source live-strict
python3 -m marketing run --source live-strict
python3 -m marketing publish-today
```

Secret required: **`ZERNIO_API_KEY`** (Cursor Cloud Agent secrets).

See also: `docs/MORNING-FLYERS.md`, `.cursor/rules/morning-flyers.mdc`.

## Agent instructions

```
You are running Sacred Ground Marketing Autopilot for the daily morning (today + tomorrow) campaign.

Hard rules:
1. Timezone context is America/Chicago. Shop-local post time is 9:00 AM America/Chicago.
2. Checkout this repo and run from the project root.
3. Content promotes TODAY’s full day (all remaining events — not evening-only), then TOMORROW. Caption opener is today-first when today has events; tomorrow-only wording only if today is empty. Never open with “tonight” at 9am when daytime sessions exist.
4. Ensure Thursday-style equal-card morning flyer(s) before drafts (never prices/$ on graphics; never hero+tiny secondary):
   python3 -m marketing generate-morning-flyers --start-offset 0 --days 2 --source live-strict
   Prefer a weekly --days 7 prebuild so 9am is not inventing art cold. Prefer today’s date flyer when today has events.
5. Refresh live WordPress / The Events Calendar only:
   python3 -m marketing run --source live-strict
6. If the WordPress/TEC refresh fails: create NO new drafts, do not use stale cache, report wordpress_refresh_failed, and STOP. Do not publish.
7. Never overwrite or recreate a draft that is edited, approved, rejected, skipped, locked, or otherwise reviewed.
8. After a successful live-strict run, publish morning posts:
   python3 -m marketing publish-today
9. Only Facebook + Instagram morning posts. Do not publish afternoon_spotlight / week_ahead / tuesday_meditation / spotlight.
10. Summarize: today’s events + tomorrow’s events, platforms, image URL/rule, publish results.
```

## Editor checklist — morning

1. Name: **SG Morning Today 9am Social**
2. Schedule: **9:00 AM** · timezone **America/Chicago** (not UTC, not 10:00)
3. Repo: `dflorino/sacred-ground-marketing-autopilot` · branch `main`
4. Secret: `ZERNIO_API_KEY`
5. Only **one** Active morning automation (disable 7am/10am duplicates)
6. Status: **Active**

---

# Automation draft — SG Afternoon Spotlight 5pm Social (LIVE)

Daily single-event afternoon spotlight (Facebook + Instagram).

**Status: auto_publish ON.** Every afternoon at **5:00 PM America/Chicago**.

**Why 5pm:** Meta Insights showed strong early traction on a ~5pm Lions Gate–style promo; leaves a clear gap before 7pm `week_ahead` without stacking too close. Flip `campaigns.afternoon_spotlight.schedule_local_time` to `16:00` for 4pm.

**Content:** one engaging spotlight — prefer tonight’s best remaining evening event; else tomorrow’s standout; else warm brand/visit. Not a full calendar dump (morning + week_ahead already cover the calendar).

## Daily commands (Cloud Agent)

```bash
python3 -m marketing run --source live-strict
python3 -m marketing publish-afternoon-spotlight
```

Do **not** call `publish-today` or `publish-week-ahead` in this automation.

## Agent instructions

```
You are running Sacred Ground Marketing Autopilot for the daily afternoon_spotlight campaign.

Hard rules:
1. Timezone America/Chicago. Post time 5:00 PM America/Chicago.
2. Checkout this repo and run from the project root.
3. python3 -m marketing run --source live-strict
4. If TEC refresh fails: create NO drafts, STOP.
5. Publish only afternoon_spotlight:
   python3 -m marketing publish-afternoon-spotlight
6. Do not publish today / week_ahead / tuesday_meditation.
7. Caption is a single-event spotlight (or brand visit). Summarize event + Zernio links.
```

## Editor checklist — afternoon

1. Name: **SG Afternoon Spotlight 5pm Social**
2. Schedule: **5:00 PM** · timezone **America/Chicago**
3. Repo: `dflorino/sacred-ground-marketing-autopilot` · `main`
4. Secret: `ZERNIO_API_KEY`
5. Status: **Active**
6. Keep separate from morning 9am, Tuesday 4pm meditation, and 7pm week-ahead

---

# Automation draft — SG Week-Ahead 7pm Social (LIVE)

Daily next-2-days evening planner posts (Facebook + Instagram).

**Status: auto_publish ON.** Every evening at **7:00 PM America/Chicago**.

Image: rotate the creative night-sky pack (plus sparse in-season storefront / holiday / full-moon overrides). Schedule list lives in the caption — next **2** days starting tomorrow only (Sat 7pm → Sun+Mon). Do **not** include the publish day’s events; morning/afternoon own tonight.

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
7. Caption lists the next 2 days starting tomorrow only (Sat → Sun+Mon). Never include the publish day’s events. Image from night atmosphere pool (creative night skies + seasonal/holiday storefronts) — never morning specialty art.
8. If there are no events in the next 2 days, report skip and do not invent events.
9. Summarize: event count, platforms, image URL, publish results.
```

## Editor checklist — evening

1. Name: **SG Week-Ahead 7pm Social**
2. Schedule: **7:00 PM** · confirm **Next run … 7:00 PM CDT** (not 2:00 PM / wrong UTC)
3. Repo: `dflorino/sacred-ground-marketing-autopilot` · `main`
4. Secret: `ZERNIO_API_KEY` (same as morning)
5. Status: **Active**
6. Keep separate from the 9am morning and 5pm afternoon automations

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
9. Caption is the dedicated meditation post (anonymous block only — Founder 2026-08-09: never name who leads): Free Community Meditation / Tuesday night 7:00–8:00 PM (`session_display`) / All are welcome / No sign-up needed / Doors close at 7:05pm (`doors_close_display`). `meditation_hosts.json` is ops-only, not for captions. No door/light goodnight closer. No o'clock. Not the morning Today lineup. Do not regenerate or republish an already-published Tuesday (e.g. leave Aug 4 2026 as-is).
10. Image from the meditation pool only (Om / silhouette / metaphysical journey / sg-morning-meditation).
11. Summarize: platforms, image URL, scheduledFor (should be 4:00 PM America/Chicago unless already past), Zernio post IDs/links.
```

## Editor checklist — Tuesday 4pm

1. Name: **SG Tuesday Meditation 4pm Social**
2. Schedule: **Every Tuesday · 4:00 PM** · timezone **America/Chicago**
3. Repo: `dflorino/sacred-ground-marketing-autopilot` · branch `main`
4. Secret: `ZERNIO_API_KEY` (same as Today / week-ahead)
5. Status: **Active**
6. Keep separate from the 9am morning, 5pm afternoon, and 7pm week-ahead automations

---

# Automation draft — SG Daily Reels 10:30am (SCAFFOLD — NOT LIVE)

Daily AI-Deneene short-form video for **Instagram Reels + Facebook Reels**.

**Status: NOT Active.** Scaffold only. `daily_reel.auto_publish=false`. Do **not** turn this automation on until a 9:16 video has been posted successfully via Zernio/ML Social (or Meta Reels) end-to-end.

Suggested time: **10:30 AM America/Chicago** (late morning — clears 9am morning, 4pm Tuesday meditation, 5pm afternoon, 7pm week-ahead image jobs).

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
6. Keep separate from image automations (9am / 4pm Tue / 5pm / 7pm)

---

## Social proof (playful shop pride — Aug 11 2026)

Rotating local-pride lines (not formal award citations) live in `config/social_proof.json`
(`enabled: true`). See **docs/SOCIAL-PROOF.md**.

- Captions + Zernio **firstComment** (FB/IG) rotate via `marketing/social_proof.py` (**ON**)
- On-image badges **OFF** (`badge_on_morning_flyers` / `badge_on_night` = false) until Founder greenlights; preview rebuild styles: `seal` · `footer_band`
- Do **not** republish already-live posts just to add a claim line
