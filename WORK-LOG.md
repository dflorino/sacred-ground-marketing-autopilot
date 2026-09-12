## 2026-09-11 — Morning missed Threads/TikTok; automation prompt fixed

Today’s Magritte morning (`1789135931977…magritte-v1`) shipped FB+IG only. Root cause: `AUTOMATION-DRAFT.md` morning Agent hard rule still said **“Only Facebook + Instagram”** — Cloud Agents followed that and skipped TikTok/Threads even though `settings.json` already listed all four.

Catch-up:
- Threads https://www.threads.com/@shopsacredground/post/DdJoYP7AmYc (`6aa410a6…`)
- TikTok published `6aa410c4…` (@shopsacredground)

Fixes: rewrite morning/afternoon/week_ahead/tuesday automation prompts to require FB+IG+TT+Threads; `publish_campaign_drafts` fails closed with `missing_platform_drafts` if any expected platform draft is absent; reel brand coverage docs include Threads. **Founder must re-paste** updated Agent instructions into each live Cursor Automation (agents cannot edit Automations).


## 2026-09-09 — Episode backfill: Threads (TikTok already complete)

Audit of S1E1–S1E9 vs Facebook:
- **TikTok:** already had every FB episode (E1–E7 published; E8–E9 scheduled). No TikTok gap.
- **Threads:** missing all nine. Backfilled via Zernio.

| Episode | Threads Zernio ID | Status |
|---|---|---|
| S1E1 | `6aa20588d4559fbdb3cdf2e9` | live https://www.threads.com/@shopsacredground/post/DdFo_uyjVpz |
| S1E2 | `6aa205d0b23e861d8ed1d359` | staggered ~8:23pm CT |
| S1E3 | `6aa205d1b23e861d8ed1d3be` | staggered ~8:26pm CT |
| S1E4 | `6aa205d1340a738c7321cb8d` | staggered ~8:29pm CT |
| S1E5 | `6aa205d2c024ff23fa4394f3` | staggered ~8:32pm CT |
| S1E6 | `6aa205d3340a738c7321cbdd` | staggered ~8:35pm CT |
| S1E7 | `6aa205d3340a738c7321cbfe` | staggered ~8:38pm CT |
| S1E8 | `6aa205d4c024ff23fa4395a6` | Thu Sep 10 9:00am CT (matches FB) |
| S1E9 | `6aa205d4340a738c7321ccaa` | Wed Sep 16 6:00pm CT (matches pack) |

Brand coverage rule now includes Threads. Flyer Autopilot already posts FB+IG+TT+Threads.


## 2026-09-07 — Remake batch trashed (fake sun / logo covering site)

Founder rejected Sep 8–30 remakes: invented sun at top, real logo pasted bottom
covering website, duplicate Chicagoland #1, prompt-meta on image (e.g. Sep 16).
Trashed remakes; kept celestial mornings for 10/22/26. **No regen until Founder asks.**
Lessons locked in `morning_flyers.json` → `last_founder_trash.lessons`.

## 2026-09-07 — Sep 8–30 morning remakes generated (review only)

Founder approved remake plan. Generated new morning plates for Sep 8–30
(celestial mornings for 10/22/26). Real sun logo pasted. Entries marked
`awaiting_founder_review` + `do_not_publish` until Founder signs off.
Gallery: `assets/_sep_rest_review/MORNINGS-REMAKE.html`

## 2026-09-07 — Today’s morning DID publish; keeper restored

Founder asked if trash meant today didn’t go out. It did — FB/IG ~9:04–9:05am CT
with plate media **27430**. Restored `2026-09-07` as keeper (`do_not_remake`).
Sep 8–30 remain trashed.

## 2026-09-07 — Founder trashed rest-of-September morning flyers

Founder stop: patching made plates worse (wrong sun logo, missing Chicagoland #1 /
Voted pride). **No more remakes / credit spend** until Founder asks.

- Marked `2026-09-07`–`2026-09-30` in `config/morning_flyers.json` as `founder_trashed`
  (`do_not_publish`, `do_not_remake`, URLs cleared)
- Locals moved to `assets/_trashed_sep_mornings_2026-09-07/` (recoverable)

## 2026-09-06 — Celestial event titles restored on images

Founder clarified: celestial plates must **keep** event titles on the photo
(`CELESTIAL NIGHT — …` / `CELESTIAL MORNING — …`). Only generic week-ahead
pool bans WEEK-AHEAD PLATE meta.

- Restored titles via ML Image edit across all dual-cadence events (Leo → Sag)
- Wired `config/celestial_events.json` to new media IDs; locals under `assets/celestial-2026/`
- Real sun-face logo pasted bottom-left on locals; gallery refreshed

## 2026-09-06 — Celestial calendar dual cadence complete through Dec

Founder calendar (Sep 5 screenshot) verified. Sep–Oct already had night+morning plates. Generated + wired Nov 9 Scorpio, Nov 24 Gemini, Dec 9 Sagittarius (night media 27513/27514/27517 · morning 27512/27515/27516). Gallery: `assets/celestial-2026/CELESTIAL-DUAL-CADENCE.html`. Fall evening batch 10/15 parked in `assets/sg-night-fall-batch-2026-09/meta.json`.

## 2026-09-06 — S1E9 scheduled + Sep 25 morning locked

S1E9 media **27385**: all brand platforms **Wed Sep 16 6:00 PM CT** — FB `6a9d9b49655de817d79c0045` · IG `6a9d9b5a5fe11bec973cf59a` · TT `6a9d9b5b6dbd3c283b2fe44e` · YT `6a9d9b5d6dbd3c283b2fe4a2` (@sacredgroundchicagoland). Caption from S1E9-SOCIAL-GRAB.

Sep 25 morning flyer media **27497** Founder-approved (Robert / Kate / Sacred Creations benefit lines).


## 2026-09-05 — Surprise morning campaign + rest-of-September flyers

Founder brief: rest-of-Sept mornings + stop-scroll surprise creatives (law: if another metaphysical shop would use it, reject). Encoded `config/morning_surprise_campaign.json` + surprise styles in `morning_flyer_styles.json`; `choose_visual_style` honors `date_plan_YYYY_MM`. Sep 3 colorful Thursday = fall equal-card gold standard. Celestial: Sep–Oct already wired; added Nov 9 Scorpio / Nov 24 Gemini / Dec 9 Sagittarius stubs (`needs_generation`). OpenRouter Image key was $0 — repointed to wallet key.

Generated + registered **2026-09-05 → 2026-09-30** (26 plates, media ~27391–27421, all `locked_until_founder_review`). Flagship samples: Universe Morning Meeting (5), Where Landed peony (6), newspaper Mon, artifact Tue, tiny universe Wed, Hollywood Fri, etc.

## 2026-09-05 — Night snow banned outside winter

Last night (Sep 4) week_ahead used **aurora_winter_village** (snow village / mountain). Founder: no snow in September (Chicago / Central). Tagged `aurora_winter_village`, `crystal_mountain_v2`, `moonlit_lake_v2` as `snow` + `seasons_allowed: [winter]`; atmosphere `_eligible_creative_pool` now season-gates them. Winter storefront already season-locked.

## 2026-09-04 — S1E8 scheduled (media 27358)

Founder handoff Title **S1E8** / media **27358**. Cadence after S1E7: IG Wed Sep 9 6pm · FB Thu Sep 10 9am · YT Fri Sep 11 4pm · TT Sun Sep 13 9am America/Chicago. IDs IG `6a9af25aac10f6514c6a590d` · FB `6a9af0993a2fe811a3588393` · YT `6a9af09752fc2caa6f54a498` · TT `6a9af0953a2fe811a3588204`. Brand YouTube `@sacredgroundchicagoland`.

## 2026-09-01 — S1E7 accidental schedules cancelled

Reel agent queued S1E7 (media **27323**) on IG/FB/YT/TT too early. Deleted all four via Zernio API:

| Platform | Post ID | Was scheduled |
|----------|---------|---------------|
| Instagram | `6a9702751d0611286dd16991` | Wed Sep 3 6pm CT |
| Facebook | `6a970299f5a8f7cbe91f24be` | Thu Sep 4 9am CT |
| YouTube | `6a970299f5a8f7cbe91f24b9` | Fri Sep 5 4pm CT |
| TikTok | `6a97029a1d0611286dd1770c` | Sun Sep 7 9am CT |

**Rescheduled** same day per Founder — **Sun Sep 7, 2026** America/Chicago: FB `6a970555ac83b184a2418232` 5:00 PM · IG `6a970555a65cd666e3de9a84` 5:05 PM · YT `6a970555a65cd666e3de9a81` 5:00 PM · TT `6a97055679c2525fcb4341e1` 5:10 PM. Media **27323**.

## 2026-09-01 — Brand YouTube connected + S1E1–S1E5 backfill

Founder connected **@sacredgroundchicagoland** via ML Social dashboard → orange **Zernio settings**. Removed erroneous S1E1 never-republish lock (was agent-added Aug 17, not Founder). Published brand Shorts:

| Ep | YouTube URL |
|----|-------------|
| S1E1 Store Quest | https://www.youtube.com/watch?v=aALb_jxjKRY |
| S1E2 Help Team | https://www.youtube.com/watch?v=iZ2QX0Xucrk |
| S1E3-B First Crystal | https://www.youtube.com/watch?v=miYOFkv62t0 |
| S1E4 First Chamber | https://www.youtube.com/watch?v=bBtFOH8leA8 |
| S1E5 Egypt Touchdown | https://www.youtube.com/watch?v=XgEDxoinZT0 |

S1E6 still scheduled Wed Sep 2 ~6pm CT (FB/IG/TT/YT). Personal `@deneeneflorino4711` retired.

## 2026-08-29 — S1E6 scheduled Wed Sep 2 6pm CT (media 27101)

Founder: set S1E6 / 27101 for Wednesday Sep 2. ML Social FB 6:00 · IG 6:05 · TikTok 6:10 · YouTube 6:00 America/Chicago. IDs FB `6a930302…` · IG `6a930310…` · TT `6a930313…` · YT `6a930315…`. Caption locked (royal tomb / crystal two / next destination).

## 2026-09-12 — Autopilot: never push tarot Death on social

- Founder: Death card posted again Sep 11 afternoon (media 23493 / 5D89500F…). She deleted posts.
- Autopilot fix on `sacred-ground-marketing-autopilot`: removed Death from `image_rules` tarot pool; `banned_social_*` + `is_banned_social_image_url`; cursor rule `never-push-tarot-death.mdc` (also copied to `~/.cursor/rules/`).
- WP Death media left in place for Observatory/print deck — social ban only.

## 2026-09-12 — Night pool: 7 dead image URLs uploaded + repointed

Founder review of the next 7 days (`tools/preview_next7.py`) surfaced night plates whose
`creative_pool` URLs 404'd — the `-1.png` uploads never happened. Two hit this week
(Sat Sep 12 blue hour, Fri Sep 18 fairy lights).

- Uploaded the 7 local PNGs to WP: blue-hour **28117**, fairy-lights **28119**,
  cozy-upstairs **28120**, oak-sidewalk **28121**, frost-sparkle **28122**,
  crescent-venus **28123**, neon-fog-alley **28124**.
- WP stored them without the `-1` suffix, so `config/image_atmosphere.json` was
  repointed to the real URLs (7 replacements).
- Verified: all 45 `nighttime.creative_pool` URLs now return 200 (0 dead).
- Known open items from the same review, not yet fixed: Wed Sep 16 afternoon is
  `reuse_blocked` (no plate), and every September date-keyed morning flyer is
  blocked so mornings fall back to specialty art.

## 2026-09-12 — Mornings: released the held v5 flyers; 40s poster joins the roster

Founder: “all these you showed me are boring, none of the morning ones are different
unusual or part of our huge design pool.” Root cause was **not** trashed art — every
September flyer carried `do_not_publish: true` / `status: awaiting_founder_review`
(the remake-v5c/v5d batch), so `plan_image` fell through to old specialty stock URLs.
The design pool was intact the whole time (23 morning styles, 20 Living Worlds).

- Showed her the seven held plates. She rejected **Sep 14** only.
- Released Sep 13 / 15 / 16 / 17 / 18 → `founder_approved: true`, `do_not_publish: false`.
  Sep 12 left alone (already posted this morning).
- Sep 14 marked `founder_rejected`, then remade: generated three pool options
  (Hollywood poster / cosmic subway / Magritte door) via `mlimg_generate`.
  OpenRouter checked first per rule — image key uncapped, unlimited remaining.
  Founder picked **A**, media **28134**, style `surprise_hollywood_poster`.
- Verified all six upcoming mornings now plan `rule=morning_flyer` with live URLs.
- Founder: “lets add the 40s poster to the roster with einstein davinci.”
  `surprise_hollywood_poster` promoted `surprise_campaign` → `approved_art`,
  inserted into `rotation_order` after Einstein, prompt_brief / pride_placement /
  readability_fix filled out to roster standard. Style id keeps its `surprise_`
  prefix so existing history stays valid. Reachable in rotation (2 hits / 120 days,
  same band as Einstein and Folk).
- Still open: afternoon plates for Sep 13 / 15 / 16 / 17 (two too tall for Instagram,
  one storefront she rejected, one with no plate at all).
