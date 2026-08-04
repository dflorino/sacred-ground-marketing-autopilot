# AI-Deneene Reels — locked stack

TikTok / YouTube Shorts spoken by an AI avatar of Deneene (look + voice), with Sacred Ground store backgrounds.

## Chosen stack: HeyGen

**Locked** (Founder: “pick for me”). Default was HeyGen; that is now the v1 stack.

| Layer | Tool | Notes |
|---|---|---|
| **Avatar + lip-sync** | **HeyGen** | Photo refs → talking-head reel |
| **Voice** | **HeyGen / Fish clone** | Working per Founder (2026-08) |
| **Backgrounds** | Store photos | Exterior ready; interiors → `assets/heygen/backgrounds/` |

Config mirror: `config/reels.json`  
Scripts batch 01: `data/reels/scripts-batch-01.md` + `config/reel_scripts.json`  
Dry-run CLI: `python3 scripts/heygen_dry_run.py`

## Status (America/Chicago)

| Item | State |
|---|---|
| Stack choice | Locked — HeyGen |
| Voice clone | **Working** (Fish / HeyGen) |
| Avatar + custom background workflow | Started |
| Exterior plate | `assets/heygen/sg-store-background.jpg` |
| Interior / case plates | **Founder shooting** → drop in `assets/heygen/backgrounds/` |
| First short scripts | Batch 01 committed (welcome, Tuesday meditation, shop vibe, …) |
| API generate | Needs `HEYGEN_API_KEY` + avatar/voice IDs in env (not in repo) |
| FB/IG 7am / 7pm autopilot | **Unchanged** — reels path is isolated |

## Content sources

1. **Starter batch** — short 15–30s scripts in `data/reels/scripts-batch-01.md` (start here).
2. **Later cadence** — yesterday’s Observatory daily: WP option `eeo_daily_YYYY-MM-DD` → field `beneath_surface`, trimmed to a short reel (hook → one insight → soft invite).

Caption / links:

- Shop: `https://shopsacredground.com/`
- Observatory: `https://shopsacredground.com/sacred-ground-observatory/`

Daily 7am/7pm still graphics stay on the Zernio path — this track is **video only**.

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

## Publish policy (Phase 1)

**Approve-before-post:** generate draft reel → Founder reviews → then post to TikTok/YouTube.  
No silent auto-publish in the first phase. Do **not** wire TikTok/YT into Zernio morning/evening jobs.

## How to make the first short this week

### A. Manual (ready now — preferred for reel #1)

1. Founder drops interior photos in `assets/heygen/backgrounds/` (see README there).
2. Open HeyGen → AI-Deneene avatar → Fish/clone voice → paste script **welcome** from batch 01.
3. Custom background: exterior plate or best new interior.
4. Export **9:16** → Founder approves → upload TikTok + YouTube Shorts.

### B. API (when secrets exist)

```bash
# .env (gitignored) — never commit real values
# HEYGEN_API_KEY=...
# HEYGEN_AVATAR_ID=...
# HEYGEN_VOICE_ID=...

python3 scripts/heygen_dry_run.py           # checklist
python3 scripts/heygen_dry_run.py --probe   # list avatars/voices
python3 scripts/heygen_dry_run.py --script welcome --generate
```

See `.env.example` for variable names.

## What the Founder still needs

1. **Interior / case backgrounds** — upright, empty of people if possible (today’s shoot).
2. **Optional API wiring** — `HEYGEN_API_KEY`, `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID` in local `.env` (or Cloud secrets) if we should generate from CLI.
3. **Approve** the first draft before any public post.
4. **Cadence** (optional) — e.g. 3×/week from batch scripts, later + Observatory.

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
- [ ] Interior plates dropped in `assets/heygen/backgrounds/`
- [ ] One approved test reel posted (or ready to post) on TikTok + YouTube Shorts
- [ ] Cadence confirmed (approve-before-post already locked for Phase 1)
