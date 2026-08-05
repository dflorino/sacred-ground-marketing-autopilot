# Sacred Ground HeyGen assets

## Backgrounds

| Path | Role |
|---|---|
| `sg-store-background.jpg` | Canonical **exterior** dusk storefront (from `assets/refs/exterior-1.png`) |
| `backgrounds/` | **New interior / case** plates — Founder drop zone (see `backgrounds/README.md`) |

Other alternates:

- `../refs/exterior-3.png` — dusk exterior, alternate framing
- `../../data/composites/store-interior.png` — warm checkout / logo-wall interior
- `../../data/composites/_interior-source.png` — crystal-aisle interior (busier)

**Shorts:** prefer portrait (9:16) plates, or crop landscape in HeyGen so the avatar doesn’t sit over the door/window/logo letters.

## Voice

Clone is live in HeyGen (Fish path) per Founder. Local samples stay gitignored under `assets/deneene-voice/`. Recording script: `assets/deneene-voice/heygen-clone-script.md`.

## Pipeline

- Plan: `REELS-PLAN.md` (primary: Instagram + Facebook Reels)
- Config: `config/reels.json` · campaign stub `daily_reel` in `config/settings.json`
- Scripts: `data/reels/scripts-batch-01.md`
- Status: `python3 -m marketing reels-status`
- Dry-run: `python3 scripts/heygen_dry_run.py`

Audio binaries (`*.m4a`, etc.) in this folder are gitignored.
