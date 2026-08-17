# Reel / Short posting schedule (Founder guidelines)

Canonical cadence for Sacred Ground **Reels / Shorts** across Instagram, Facebook, TikTok, and YouTube Shorts.

**Timezone:** America/Chicago (Central) always.  
**Source:** Founder recommendations reflecting large 2026 platform studies (IG, FB, TikTok, YouTube Shorts).  
**How this is posted today:** ML Social **manual / scheduled** posts — **not** Zernio Autopilot cron. Do not invent or activate Autopilot reel automation from this doc alone. See `REELS-PLAN.md` + `AUTOMATION-DRAFT.md` for the separate (still inactive) HeyGen `daily_reel` scaffold.

## Hard rule — brand coverage (all SM platforms)

**Founder (Aug 16, 2026):** traction requires every episode on **all** social platforms — brand accounts only.

| Requirement | Rule |
|---|---|
| Platforms | Every episode **must** hit **Facebook + Instagram + TikTok + YouTube** |
| Accounts | **Sacred Ground brand only** (`shopsacredground` / Sacred Ground page) |
| YouTube | **Sacred Ground brand channel** — **never** personal `@deneeneflorino4711` |
| contentType | Use `reel` or `story` (not plain video alone) |
| FB Story media | **Zernio CDN** (`media.zernio.com`) — WP URLs fail Meta fetch (CF 403) |
| Live posts | Do **not** cancel successful live posts to “fix” coverage |

**Agent gate before publish:** confirm `social_accounts` shows brand YouTube connected. If only personal YouTube is present, **stop** and tell Founder to reconnect brand OAuth — do not ship the Short to personal as a brand substitute.

**Founder click path (connect brand YouTube in ML Social / Zernio):**

1. Open **ML Social → Accounts** (same workspace that shows FB / IG / TikTok Sacred Ground).
2. Click **Connect** / **Add account** → choose **YouTube**.
3. Complete Google OAuth while signed into the **Sacred Ground brand** Google/YouTube channel (not the personal `@deneeneflorino4711` channel).
4. Confirm the new account shows Sacred Ground branding / brand channel name — then tell the agent so S1E1 (media **26545**) can be republished as a brand Short.
5. Optional later: leave personal YouTube disconnected or clearly labeled so agents never pick it for brand episodes.

Until step 4 succeeds, **brand YouTube republish is blocked** — no agent workaround.

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

## S1E1 Store Quest — Sun Aug 16, 2026 (PUBLISHED — DO NOT REPOST)

Media **26545** (`S1E1-Store-Quest.mp4`). Verified ~7:43 PM CT via ML Social `social_posts` / `social_accounts`. Do **not** cancel live successes.

**Hard rule (Founder Aug 17, 2026 ~9:35 AM CT):** S1E1 is a **one-shot**. Do **not** republish, recycle, or put on any daily/weekly Autopilot or “Reel-building Friday” cron. Stories remaining visible the next morning (~24h tray) are **not** a new publish. If ML Social shows a **future scheduled** S1E1 duplicate, cancel that queue only — never cancel live successes or legitimate image Autopilot posts.

### Brand traction (Sacred Ground)

| Surface | Status | When (CT) | Post / URL |
|---|---|---|---|
| **FB Watch** (video) | ✅ brand | 6:45 PM | `6a820b7a323f485ce2f6cd5e` → [watch](https://www.facebook.com/watch/?v=1326169786395522) |
| **FB Reel** | ✅ brand | ~7:05 PM | `6a825050d4b2f7ccc74b778f` → [reel](https://www.facebook.com/reel/2118708588998551) |
| **FB Story** (Zernio CDN) | ✅ brand | ~7:35 PM | `6a825747be9ba353a3d363aa` → stories on Sacred Ground page |
| **IG Reel** | ✅ brand | ~6:57 PM | `6a824e52f73862dcd77323da` → [reel](https://www.instagram.com/reel/DcHsgELka4k/) |
| **IG Story** | ✅ brand | ~7:05 PM | `6a82504ee9b3fe4cc1f571d0` |
| **TikTok** | ✅ brand `@shopsacredground` | 7:30 PM | `6a820b7c323f485ce2f6cde8` → [video](https://www.tiktok.com/@shopsacredground/video/7674791869305441550) |

### Gap — brand YouTube

| Surface | Status | Detail |
|---|---|---|
| **YouTube Short** | ⚠️ **personal only** | `6a820b7c323f485ce2f6cdc1` → [watch](https://www.youtube.com/watch?v=OqDCjr3BPY0) on `@deneeneflorino4711` |
| **Sacred Ground YouTube** | ❌ **not connected** | No brand YT account in ML Social `social_accounts` — cannot republish until Founder OAuth |

Old wrong-media ids (deleted earlier): `6a8204a952e7ad0aab0854d9` · `6a8204ab23fabe1c288bd828` · `6a8204ac23fabe1c288bd85a` · `6a8204ac52e7ad0aab085527`

WP-only FB Story attempts failed (CF 403) and stay failed — CDN Story above is the keeper.

## S1E2 Lemuria — CANCELLED (not scheduled)

Founder remaking S1E2. Any Mon Aug 17 drafts cancelled. Media ID **26537** remains inventory only — **do not schedule**.

## Operational lesson — FB Story media hosting (Sun Aug 16, 2026)

**Do not publish Facebook Stories from shopsacredground.com WordPress media URLs.**

Tonight’s failure: ML Social / Zernio FB Story with a WP-hosted MP4 failed because Cloudflare returns **403** to Meta’s `meta-externalagent` crawler. Meta never fetches the file.

| Path | Result tonight |
|---|---|
| FB Story ← `shopsacredground.com/wp-content/uploads/…` | **Fail** (CF 403 to Meta crawler) |
| FB Story ← **Zernio CDN** (`media.zernio.com`) | **Works** — upload same video there, publish with that URL + `contentType: "story"` |
| Reels / IG Story ← WP URL | May still work; **FB Story specifically needed Zernio CDN** |

### Agent checklist (shorts / Stories)

1. **Brand coverage first:** confirm FB + IG + TikTok + **brand** YouTube are connected. If brand YouTube is missing, stop and ask Founder to OAuth-connect it (see Hard rule above) — do not use personal YT for brand traction.
2. **FB Story:** upload video to Zernio CDN first; use `media.zernio.com` URL — never rely on WP alone.
3. Schedule IG/FB shorts with explicit `contentType: "reel"` or `contentType: "story"` (not plain video alone).
4. Do not rewrite or cancel live/scheduled successful posts unless Founder asks.
5. After brand YouTube is connected: republish S1E1 (media **26545**) as a Short on the brand channel only.
6. **Name in closed captions:** never rely on platform auto-ASR for the Founder’s name (see hard rule below).

## Hard rule — closed captions / name spelling (Founder Aug 16, 2026)

**Correct spelling always:** **Deneene** (D-E-N-E-E-N-E). Never **Denise**. Never incomplete **Deneen**.

Auto closed captions (volume-off viewers) routinely mishear the name. Platform auto-ASR is **not** good enough for Sacred Ground video posts.

| Requirement | Rule |
|---|---|
| Before publish | Burn in correct captions **or** upload / review custom captions (SRT or in-app editor) with **Deneene** spelled correctly |
| Never | Ship relying on unreviewed auto-generated captions for any spoken “Deneene” |
| Post-publish | YouTube Studio can Duplicate & Edit / upload SRT; Meta Page videos may allow caption edit in Business Suite; **IG Reels auto-captions generally lock after publish**; TikTok may allow Edit post → captions on eligible videos only |
| Agent APIs | ML Social MCP (`social_publish` / `social_posts`) has **no** subtitle/caption-track edit — agents cannot fix ASR remotely |

### Founder fix paths (S1E1 Store Quest — live Sun Aug 16, 2026)

Do **not** delete live posts unless a platform forces re-upload.

| Platform | Live URL | Remote agent fix? | Founder action |
|---|---|---|---|
| **YouTube** (personal `@deneeneflorino4711`) | [OqDCjr3BPY0](https://www.youtube.com/watch?v=OqDCjr3BPY0) | **No** (no YT OAuth / caption API in this workspace) | Auto track currently opens with **“I'm Deni.”** — fix to **“I'm Deneene.”** YouTube Studio → Subtitles → English (auto-generated) → **Duplicate and edit** → correct every wrong name → Publish. Or upload a corrected `.srt`. |
| **Facebook Watch** | [watch/?v=1326169786395522](https://www.facebook.com/watch/?v=1326169786395522) | **No** | Meta Business Suite → Content → that video → Edit → Captions / Closed captions → edit auto-generated or upload `.srt` with **Deneene**. (Official help also: Page post → Edit Post → Closed captions.) |
| **Facebook Reel** | [reel/2118708588998551](https://www.facebook.com/reel/2118708588998551) | **No** | Try same Business Suite / Edit path first. If captions are not editable on the Reel surface, options are limited — prefer leaving engagement and fixing via Watch copy if that track is what CC uses, or re-upload only if Founder decides. |
| **Instagram Reel** | [DcHsgELka4k](https://www.instagram.com/reel/DcHsgELka4k/) | **No** | Auto video captions generally **cannot** be edited after publish. Written post caption under the Reel can still be edited (does not fix on-video CC). Fix requires delete + re-upload with corrected Captions sticker / burn-in — **only if Founder accepts losing engagement**. |
| **TikTok** `@shopsacredground` | [video/7674791869305441550](https://www.tiktok.com/@shopsacredground/video/7674791869305441550) | **No** | App → video → **⋯** → **Edit post** → if Captions appear, correct every Denise → **Deneene**. If Edit captions is missing, re-upload with Captions enabled and reviewed before post. |

## Related docs

- `config/accounts.json` — brand FB / IG / TikTok IDs + YouTube brand-missing gate
- `config/reels_media.json` — Founder Media Library IDs (S1E1 / S1E2) + brand coverage + FB Story hosting
- `REELS-PLAN.md` — HeyGen AI-Deneene stack, scaffold status, isolation from image jobs
- `AUTOMATION-DRAFT.md` — inactive “SG Daily Reels 10:30am” Cloud Agent draft (do not activate from this schedule alone)
- `config/reels.json` — scaffold publish config (`auto_publish: false`)
- `data/reels/scripts-batch-01.md` — starter spoken scripts
