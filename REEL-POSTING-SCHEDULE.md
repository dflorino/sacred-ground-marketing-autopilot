# Reel / Short posting schedule (Founder guidelines)

Canonical cadence for Sacred Ground **Reels / Shorts** across Instagram, Facebook, TikTok, and YouTube Shorts.

**Timezone:** America/Chicago (Central) always.  
**Source:** Founder recommendations reflecting large 2026 platform studies (IG, FB, TikTok, YouTube Shorts).  
**How this is posted today:** ML Social **manual / scheduled** posts — **not** Zernio Autopilot cron. Do not invent or activate Autopilot reel automation from this doc alone. See `REELS-PLAN.md` + `AUTOMATION-DRAFT.md` for the separate (still inactive) HeyGen `daily_reel` scaffold.

## Team Sacred Ground recommended week

| Day | Local time (CT) | Content |
|---|---|---|
| **Tuesday** | **6:00 PM** | Character comedy or clue |
| **Wednesday** | **6:00 PM** | Main story episode |
| **Thursday** | **9:00 AM** | World reveal or decoder |
| **Friday** | **4:00 PM** YouTube Short; **~6:00–7:00 PM** other platforms | Friday short / week closer |

### Platform defaults

| Platform | Default time (CT) | Notes |
|---|---|---|
| Instagram | **6:00 PM** | Weekday default with TikTok / YouTube |
| TikTok | **6:00 PM** | Weekday default |
| YouTube Shorts | **6:00 PM** (Fri Short **4:00 PM**) | Simple weekday default; Friday Short earlier |
| Facebook | **~9:00 AM** | Exception — generally better morning than evening |

### Most important weekly Reel

**Wednesday 6:00 PM Central** — main story episode. Protect this slot when prioritizing the week.

## Simple weekday default

Across **Instagram, TikTok, and YouTube:** prefer **6:00 PM Central**.  
**Facebook** exception: prefer around **9:00 AM Central**.

## Scope / do not confuse with image Autopilot

Still-image Autopilot (Zernio) stays separate:

| Job | Time (CT) | Path |
|---|---|---|
| Morning today/tomorrow | 9:00 AM | Image Autopilot |
| Tuesday meditation | 4:00 PM Tue | Image Autopilot |
| Afternoon spotlight | 5:00 PM | Image Autopilot |
| Week-ahead night | 7:00 PM | Image Autopilot |

This reel/short cadence is for **video** story / comedy / decoder posts. It does **not** replace those image jobs and does **not** enable `campaigns.daily_reel` (scaffold schedule `10:30` in `config/reels.json` remains inactive until video publish is proven).

## WordPress Media Library IDs (Founder-confirmed)

Canonical file: **`config/reels_media.json`**. Agents must use these IDs / URLs for ML Social video posts:

| Episode | Library name | Media ID | URL |
|---|---|---|---|
| Season 1 Episode 1 — Store Quest | **S1E1** | **26545** | `https://shopsacredground.com/wp-content/uploads/S1E1-Store-Quest.mp4` |
| Season 1 Episode 2 — Lemuria | **S1E2** | **26537** | `https://shopsacredground.com/wp-content/uploads/S1E2-Lemuria.mp4` |

**Do not use** media ID **26546** or `…/s01e01-store-quest.mp4` for S1E1.  
**S1E2** — Founder remaking; **not scheduled**. Do not queue until Founder asks.

## S1E1 Store Quest — Sun Aug 16, 2026 (TONIGHT — KEEP)

Media **26545** (`S1E1-Store-Quest.mp4`). Wrong-media originals were deleted earlier; these corrected posts stay scheduled:

| Platform | Scheduled (CT) | Post id | Media |
|---|---|---|---|
| Facebook | 6:45 PM | `6a820b7a323f485ce2f6cd5e` | 26545 |
| Instagram | 7:00 PM | `6a820b7b323f485ce2f6cd96` | 26545 |
| YouTube Shorts | 7:00 PM | `6a820b7c323f485ce2f6cdc1` | 26545 |
| TikTok | 7:30 PM | `6a820b7c323f485ce2f6cde8` | 26545 |

Old wrong-media ids (deleted): `6a8204a952e7ad0aab0854d9` · `6a8204ab23fabe1c288bd828` · `6a8204ac23fabe1c288bd85a` · `6a8204ac52e7ad0aab085527`

## S1E2 Lemuria — CANCELLED (not scheduled)

Founder remaking S1E2. Any Mon Aug 17 drafts cancelled. Media ID **26537** remains inventory only — **do not schedule**.

## Related docs

- `config/reels_media.json` — Founder Media Library IDs (S1E1 / S1E2)
- `REELS-PLAN.md` — HeyGen AI-Deneene stack, scaffold status, isolation from image jobs
- `AUTOMATION-DRAFT.md` — inactive “SG Daily Reels 10:30am” Cloud Agent draft (do not activate from this schedule alone)
- `config/reels.json` — scaffold publish config (`auto_publish: false`)
- `data/reels/scripts-batch-01.md` — starter spoken scripts
