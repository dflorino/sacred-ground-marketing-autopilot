# AI-Deneene Reels — locked stack

Daily short-form spoken by an AI avatar of Deneene (look + voice), with Sacred Ground store backgrounds.

**Founder target (locked):** daily **Instagram Reels** + **Facebook Reels** (America/Chicago).  
TikTok + YouTube Shorts stay optional / later.

**Posting cadence (story / comedy / Shorts going forward):** see **`REEL-POSTING-SCHEDULE.md`** (Founder 2026 guidelines — ML Social scheduled; not Autopilot cron).

## Chosen stack: HeyGen

**Locked** (Founder: “pick for me”). Default was HeyGen; that is now the v1 stack.

| Layer | Tool | Notes |
|---|---|---|
| **Avatar + lip-sync** | **HeyGen** | Photo refs → talking-head reel |
| **Voice** | **HeyGen / Fish clone** | Working per Founder (2026-08) |
| **Backgrounds** | Store photos | Exterior ready; interiors → `assets/heygen/backgrounds/` |
| **Format** | **9:16** · 1080p | Required for Reels / Shorts |

Config mirror: `config/reels.json`  
Campaign stub: `daily_reel` in `config/settings.json`  
Scripts batch 01: `data/reels/scripts-batch-01.md` + `config/reel_scripts.json`  
Scaffold module: `marketing/reels.py` · CLI: `python3 -m marketing reels-status`  
Dry-run CLI: `python3 scripts/heygen_dry_run.py`

## Honest status (America/Chicago)

| Item | State |
|---|---|
| Stack choice | Locked — HeyGen |
| Voice clone | **Working** (Fish / HeyGen) |
| Avatar + custom background workflow | Started |
| Exterior plate | `assets/heygen/sg-store-background.jpg` |
| Interior / case plates | **Founder shooting** → drop in `assets/heygen/backgrounds/` |
| First short scripts | Batch 01 committed (welcome, Tuesday meditation, shop vibe, …) |
| Target platforms | **Instagram Reels + Facebook Reels** (primary, daily) |
| Optional later | TikTok + YouTube Shorts |
| Suggested post time (scaffold only) | **10:30 AM** America/Chicago — inactive Autopilot stub; **live cadence** → `REEL-POSTING-SCHEDULE.md` |
| API generate | Needs `HEYGEN_API_KEY` + avatar/voice IDs in env (not in repo) |
| **FB/IG still-image autopilot** | **Live via Zernio** — Today 7am, Tuesday meditation 4pm, week-ahead 7pm |
| **Video / Reels auto-publish** | **Not ready** — scaffold only (`auto_publish: false`) |

### What works today

- **Image posts** to Facebook + Instagram via Zernio (`ZERNIO_API_KEY`, `config/accounts.json`).
- Campaigns: `today`, `week_ahead`, `tuesday_meditation` — `mediaItems` with `type: "image"`.
- HeyGen **manual** path: build a reel in the HeyGen UI, export **9:16**, Founder posts by hand.

### What is still needed for daily IG + FB Reels alone

1. **Generate** — HeyGen (UI or API) → 9:16 MP4 of AI-Deneene.
2. **Host** — Stable HTTPS URL for the video file (WP media, CDN, etc.).
3. **Publish video** — Confirm Zernio / ML Social `social_publish` accepts `type: "video"` (or Reels placement) for the same FB + IG account IDs; **or** wire Meta Reels APIs.
4. **Secrets** — Keep `ZERNIO_API_KEY` for social; add `HEYGEN_*` only if API generate is wanted (never commit).
5. **Gate** — First reel Founder-approved; then enable Cloud Agent automation. Keep `approve_before_post` until proven.

Do **not** claim full auto-publish for Reels until steps 1–4 are verified end-to-end.

## Content sources

1. **Starter batch** — short 15–30s scripts in `data/reels/scripts-batch-01.md` (start with **welcome**).
2. **Daily cadence** — rotate batch scripts; when available, yesterday’s Observatory daily: WP option `eeo_daily_YYYY-MM-DD` → field `beneath_surface`, trimmed to a short reel (hook → one insight → soft invite).

Caption / links:

- Shop: `https://shopsacredground.com/`
- Observatory: `https://shopsacredground.com/sacred-ground-observatory/`

Daily 7am / 4pm / 7pm still graphics stay on the Zernio **image** path — this track is **video only** and must not break those jobs.

## Why Cursor image gen is NOT the avatar path

| Attempt | Result |
|---|---|
| GenerateImage **with** her photo refs | **400** — tool path cannot use refs |
| GenerateImage **without** refs | Generic faces — **rejected** (“hell no”) |

Likeness source of truth = **real photos** in `assets/deneene-refs/` (and `png/`).  
Rejected Cursor stills live in `assets/deneene-looks/_rejected/` — do not regenerate more fake faces here.

## Look rotation

Kit: `config/deneene_looks.json` (also referenced from `config/reels.json`)

- Indoor: hair down/back, clear glasses / none, hats
- **Outdoor: sunglasses are first-class** (`outdoor_sunglasses_*`, default `outdoor_sunglasses_hair_down`)
- Apply as HeyGen avatar “look” / wardrobe variants — still grounded in `assets/deneene-refs/`, never Cursor stills

## Publish policy

| Phase | Behavior |
|---|---|
| **Now (scaffold)** | Plan + config say IG Reels + FB Reels daily. Generate draft → Founder reviews → manual post. `auto_publish: false`. |
| **Next** | Wire video URL into Zernio/ML Social (or Meta) after a successful manual test post. |
| **Later (optional)** | Add TikTok / YouTube Shorts if wanted — same 9:16 asset. |

Image autopilot jobs are **isolated** — do not fold Reels into `publish-today` / `publish-week-ahead` / `publish-tuesday-meditation`.

## How to make the first short this week

### A. Manual (ready now — preferred for reel #1)

1. Founder drops interior photos in `assets/heygen/backgrounds/` (see README there).
2. Open HeyGen → AI-Deneene avatar → Fish/clone voice → paste script **welcome** from batch 01.
3. Custom background: exterior plate or best new interior.
4. Export **9:16** → Founder approves → upload **Instagram Reels** + **Facebook Reels**.
5. Optional later: same file to TikTok / YouTube Shorts.

### B. API (when secrets exist)

```bash
# .env (gitignored) — never commit real values
# HEYGEN_API_KEY=...
# HEYGEN_AVATAR_ID=...
# HEYGEN_VOICE_ID=...

python3 scripts/heygen_dry_run.py           # checklist
python3 -m marketing reels-status           # plan + blockers
python3 scripts/heygen_dry_run.py --probe   # list avatars/voices
python3 scripts/heygen_dry_run.py --script welcome --generate
```

See `.env.example` for variable names.

## Scaffold in this repo

- `config/reels.json` — primary platforms = IG + FB Reels; TikTok/YT optional later
- `config/settings.json` → `campaigns.daily_reel` — **enabled: false**, **auto_publish: false**, schedule **10:30**
- `marketing/reels.py` — caption/script pick + readiness report (no publish)
- `python3 -m marketing reels-status` — Founder-facing checklist JSON
- Tests: `tests/test_reels.py`

## What the Founder still needs

1. **Interior / case backgrounds** — upright, empty of people if possible.
2. **Optional API wiring** — `HEYGEN_API_KEY`, `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID` in local `.env` (or Cloud secrets) if we should generate from CLI.
3. **Approve** the first draft before any public IG/FB Reels post.
4. **Video publish proof** — one manual or API test that Zernio (or Meta) can place a 9:16 video as a Reel on both platforms.
5. **Then** turn on a Cloud Agent automation (see `AUTOMATION-DRAFT.md` scaffold section) — not before.

## Stack options (historical — not active)

| Option | Status |
|---|---|
| **A. HeyGen** | **Chosen** |
| B. ElevenLabs + Hedra | Deferred |
| C. HeyGen look + ElevenLabs voice | Fallback only if clone isn’t enough |

## Done when

- [x] Voice clone working (Founder)
- [x] Exterior background plate in repo
- [x] Interior shoot folder + brief
- [x] First batch of short scripts committed
- [x] Config + dry-run CLI wired (env pattern; no secrets in git)
- [x] Plan targets **Instagram Reels + Facebook Reels** daily (TikTok/YT optional)
- [x] `daily_reel` campaign stub + `reels-status` (no auto-publish)
- [ ] Interior plates dropped in `assets/heygen/backgrounds/`
- [ ] One approved test reel posted on **IG Reels + FB Reels**
- [ ] Video URL → Zernio/ML Social (or Meta) path verified
- [ ] Cadence automation Active (only after video path works)
