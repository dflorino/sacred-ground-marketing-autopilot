# AI-Deneene Reels — next step

TikTok / YouTube Shorts from Observatory **Beneath the Surface**, spoken by an AI avatar of Deneene (look + voice).

## Source (script)

1. Pull yesterday’s Observatory daily: WP option `eeo_daily_YYYY-MM-DD` → field `beneath_surface`.
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

## Recommended stack (pick one)

| Option | Likeness | Voice | Notes |
|---|---|---|---|
| **A. HeyGen** | Avatar from her photo refs | Built-in voice clone or upload | Fastest all-in-one; good for talking-head reels |
| **B. ElevenLabs + Hedra** | Hedra image-to-video from a chosen look still *produced by Hedra/avatar tool using her refs* | ElevenLabs voice clone | Best voice control; two tools to wire |
| **C. HeyGen look + ElevenLabs voice** | HeyGen avatar | ElevenLabs if HeyGen clone isn’t enough | Hybrid if voice quality needs a boost |

Default recommendation if she says “pick for me”: **HeyGen** for v1 (one account, photo→avatar→talking video), then upgrade voice to ElevenLabs only if needed.

## What Deneene still needs to provide

1. **Voice samples** — 1–3 minutes of clear speech (phone voice memo is fine): warm, natural, no heavy background music. Enough for a clone.
2. **Tool choice** — HeyGen / ElevenLabs+Hedra / hybrid — **or “pick for me”**.
3. **Cadence** — e.g. 1 reel/day from yesterday’s Beneath the Surface, or 3×/week.
4. **Approve-before-post** — keep Phase-1 style: generate draft reel → Founder reviews → then post to TikTok/YouTube (no silent auto-publish).

No new paid accounts or uploads will be opened until she chooses (or says pick for me) and supplies voice samples.

## Look rotation (after avatar tool is chosen)

Kit: `config/deneene_looks.json`

- Indoor: hair down/back, clear glasses / none, hats
- **Outdoor: sunglasses are first-class** (`outdoor_sunglasses_*`, default `outdoor_sunglasses_hair_down`)
- Apply as avatar “look” or wardrobe variants in the chosen tool — still grounded in `assets/deneene-refs/`, never Cursor stills

## Done when

- [ ] Voice samples in repo (e.g. `assets/deneene-voice/`) or linked private folder
- [ ] Avatar tool account chosen
- [ ] One approved test reel from yesterday’s Beneath the Surface
- [ ] Cadence + approve-before-post confirmed
