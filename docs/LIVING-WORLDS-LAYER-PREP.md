# Living Worlds — layer prep (required before Remotion render)

**Hard rule:** A finished JPG/PNG is one flat surface. Objects cannot move naturally unless they are **separate transparent PNG layers** on a **clean background plate** with moving objects removed.

**Production:** `remotion/` · **Deprecated:** `marketing/living_worlds.py` → `render_preview_loop` (flat PIL — do not use for social MP4).

## Timing standard

| Setting | Value |
|---------|-------|
| FPS | **30** |
| Loop frames | **210** (7 seconds) |
| Last frame | **209** — must visually connect to frame **0** |
| Animation | `useCurrentFrame()` only — no CSS keyframes, timers, rAF |

## Required layer files (18+)

Export at **1080×980** art-band scale from `scene-raw.png`. Place in  
`remotion/public/layers/<concept-id>/`

| # | File | Contents |
|---|------|----------|
| 1 | `background-plate.png` | Full scene — **no** moving objects baked in |
| 2 | `foreground-frame.png` | Optional decorative border |
| 3 | `coffee-cup.png` | Mug only |
| 4–6 | `coffee-steam-1/2/3.png` | Optional static wisp art; motion is procedural in `CoffeeSteam` |
| 7 | `candle-body.png` | Beeswax + wick, **no flame** |
| 8 | `candle-flame.png` | Flame only (transparent) |
| 9 | `candle-glow.png` | Amber halo (transparent) |
| 10 | `incense-holder.png` | Stick + holder |
| 11–12 | `incense-smoke-1/2.png` | Optional; motion is procedural in `IncenseSmoke` |
| 13 | `hero-crystal.png` | Rolling / hero crystal |
| 14 | `crystal-highlight.png` | Optional highlight sweep |
| 15 | `pendant.png` | Jewelry — pivot at top center of chain |
| 16 | `reader.png` | Optional stable reader figure |
| 17 | `reader-hand.png` | Optional moving forearm |
| 18 | `card-front.png` / `card-back.png` | Reader card faces |
| 19+ | `open-sign.png`, `lever.png`, `kettle.png`, `gear.png` | Mechanism parts |

**Duplicate rule:** If an object is visible in `background-plate.png`, do **not** animate a second copy on top. Remove it from the plate and repair the hole.

**Text:** Greeting, date, reader, events, phone — **live React** in `EventPanel`. Never bake into artwork.

## Validate before render

```bash
cd remotion
npm run validate:layers -- --slug living-crystal-morning-machine
```

Manifest source: `data/living_worlds/layers/<style_id>/manifest.json`  
Synced PNGs: `remotion/public/layers/<slug>/`

See **`docs/LIVING-WORLDS-LAYERS-REPO.md`** for the full GitHub layout.

## Implementation order

1. **Motion Laboratory** (`npm run start:lab`) — test all 8 motion components
2. **Crystal Morning Machine** — after layers exist + lab passes QA
3. Other templates reuse proven components

## Compositions

| ID | Purpose |
|----|---------|
| `MotionLaboratory` | All 8 components + diagnostics |
| `MotionLaboratoryReduced` | Reduced motion preview |
| `CrystalMorningMachine` | Full pilot template |
| `CrystalMorningMachineDiagnostics` | Anchors, safe areas, frame # |
| `LoopBoundaryPreview` | Scrub frames 190–209 → 0–19 in Studio |

## Render exports

```bash
npm run render:machine          # 1080×1350 MP4 feed
npm run render:machine:still    # frame 0 static cover
```

Story/Reel 1080×1920: separate composition with repositioned layers (not stretch) — TODO after feed passes QA.

## Daily content

Edit `remotion/src/data/crystal-morning-machine-2026-08-24.ts` or pass `defaultProps` — date, reader, hours, events never hardcoded in PNGs.

## Python bridge (planned)

`marketing/living_worlds.py` should invoke `npm run render:machine` with daily JSON — not PIL loops.
