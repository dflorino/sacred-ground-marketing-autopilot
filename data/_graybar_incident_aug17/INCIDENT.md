# Gray-bar night creative — Mon Aug 17, 2026 (America/Chicago)

## Tonight’s live posts

- Campaign: `week_ahead` (~7:00 PM CT)
- Platforms: Facebook + Instagram via Social Media Connector / Zernio
- Drafts: `sgma-2026-08-17-week_ahead-fb-9b7e986b`, `sgma-2026-08-17-week_ahead-ig-8e3dca94`
- Image URL: `https://shopsacredground.com/wp-content/uploads/sg-night-creative-neon-fog-alley-1.png` (WP media **26010**)
- Rule: `week_ahead_creative_neon_fog_alley`
- Founder: will delete FB+IG themselves. **Do not auto-repost.**

## Root cause

Baked into the pool PNG (not Autopilot caption / not a late-summer remake-v4 paste).

- Mid-image desaturated gray veil through the neon/storefront join
- Objective signature: max mid chroma-drop **~16.7** (clean plates ~4–5)
- Same family as local `assets/sg-night-creative-neon-fog-alley.png` and `_night_doctor_backup/` copy
- `prebranded: false` on drafts; shop-pride overlays gated off — glitch is in the source plate

## Clean replacement (awaiting Founder approval)

| Field | Value |
|---|---|
| Local | `assets/sg-night-creative-neon-fog-storefront-clean-v5.png` |
| URL | `https://shopsacredground.com/wp-content/uploads/sg-night-creative-neon-fog-storefront-clean-v5.png` |
| Media ID | **26727** |
| Mid chroma-drop | ~4.7 |
| Pool status | `active: false` + `founder_approval_required: true` until Founder says go |

Review gallery: `data/_graybar_incident_aug17/REVIEW.html`

## Quarantine

- `neon_fog_alley` → `active: false` / `quarantine: true` in `config/image_atmosphere.json`
- Prior `…/neon-fog-alley.png` already lifetime-blocked via `image_usage`
- Broken `-1` URL stays in `image_usage` (never reuse)

## Audit Tue Aug 18 – Mon Aug 24

Morning flyers queued in `config/morning_flyers.json` (Einstein / collage / Magritte·Folk·Da Vinci·Matisse remake-v4): **no neon-fog-style mid chroma veil**.

Late-summer remake-v4 night pool: **do not share the ~16+ chroma-drop signature**.

`neon_puddles` / `-1`: mild (~11) — watchlist only; not quarantined tonight.

## Not done until Founder approves

- Activate `neon_fog_storefront_clean_v5` in creative_pool
- Repost week_ahead for Aug 17
- S1E1 untouched / never republish
