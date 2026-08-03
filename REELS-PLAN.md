# AI-Deneene Reels — locked stack

TikTok / YouTube Shorts from Observatory **Beneath the Surface**, spoken by an AI avatar of Deneene (look + voice).

## Chosen stack: HeyGen

**Locked** (Founder: “pick for me”). Default was HeyGen; that is now the v1 stack.

| Layer | Tool | Notes |
|---|---|---|
| **Avatar + lip-sync** | **HeyGen** | Photo refs → talking-head reel |
| **Voice** | **HeyGen voice clone** from her samples (primary) | Use ElevenLabs only later if HeyGen clone is insufficient — keep v1 simple |

Config mirror: `config/reels.json`

## Content source (script)

1. Pull **yesterday’s** Observatory daily: WP option `eeo_daily_YYYY-MM-DD` → field `beneath_surface`.
2. Trim to a 30–60s reel script (hook → one insight → soft invite to Observatory / shop).
3. Caption + link: `https://shopsacredground.com/sacred-ground-observatory/`

Daily 7am/7pm still graphics are already shipped — this track is **video only**.

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
No silent auto-publish in the first phase.

## What the Founder still needs to provide

1. **Voice samples** — 1–3 minutes of clear speech (phone voice memo is fine): warm, natural, no heavy background music. Drop files in **`assets/deneene-voice/`** (see README there).
2. **HeyGen account / API access** — confirm when ready so we can wire avatar + voice clone.
3. **Cadence** (optional for v1) — e.g. 1 reel/day from yesterday’s Beneath the Surface, or 3×/week.

## Stack options (historical — not active)

| Option | Status |
|---|---|
| **A. HeyGen** | **Chosen** |
| B. ElevenLabs + Hedra | Deferred |
| C. HeyGen look + ElevenLabs voice | Fallback only if HeyGen voice clone isn’t enough |

## Done when

- [ ] Voice samples in `assets/deneene-voice/`
- [ ] HeyGen account/API access confirmed
- [ ] One approved test reel from yesterday’s Beneath the Surface
- [ ] Cadence confirmed (approve-before-post already locked for Phase 1)
