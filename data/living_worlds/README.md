# Living Worlds — layer repo (20 concepts)

**Founder approved:** Aug 23, 2026 · **Config:** `config/morning_living_worlds.json`

This folder tracks **layer prep** for all 20 Morning Living Worlds. Nothing publishes until Founder approves the look and assigns a calendar date.

## Quick links

| What | Where |
|------|--------|
| Concept config | `config/morning_living_worlds.json` |
| Layer index (machine-readable) | `data/living_worlds/layers/index.json` |
| Per-concept manifest | `data/living_worlds/layers/<style_id>/manifest.json` |
| Scene + layer PNGs | `assets/living_worlds/<slug>/` |
| Remotion sync target | `remotion/public/layers/<slug>/` |
| Prep docs | `docs/LIVING-WORLDS-LAYERS-REPO.md` |
| Agent rule | `.cursor/rules/living-worlds-layers.mdc` |

## CLI

```bash
# Init all 20 manifests + decomposition prompts
python3 -m marketing living-world-layers init --all

# Status table
python3 -m marketing living-world-layers status

# What's still missing scene-raw?
python3 -m marketing living-world-layers pending-scenes

# After layers exist — copy to Remotion public/
python3 -m marketing living-world-layers sync

# Validate scene + required transparent layers
python3 -m marketing living-world-layers validate
```

## Approval workflow (Founder)

1. **Scene raw** — hero plate per concept (`scene-raw.png`). Say yes/no on look.
2. **Layer decomposition** — transparent PNGs per manifest. Remotion animates these.
3. **Assign date** — only after look + motion pass QA; update manifest `approval.assigned_date`.

Pilot held: `living_crystal_morning_machine` — do not publish until Remotion panel matches standard.

## Slug map (style_id → folder)

| # | style_id | slug |
|---|----------|------|
| 1 | `living_crystal_morning_machine` | `living-crystal-morning-machine` |
| 2 | `living_matchbox_mysteries` | `living-matchbox-mysteries` |
| 3 | `living_popup_crystal_shop` | `living-popup-crystal-shop` |
| 4 | `living_nine_oclock_theater` | `living-nine-oclock-theater` |
| 5 | `living_cabinet_treasures` | `living-cabinet-treasures` |
| 6 | `living_inside_crystal_shop` | `living-inside-crystal-shop` |
| 7 | `living_shopkeeper_workbench` | `living-shopkeeper-workbench` |
| 8 | `living_crystal_board_game` | `living-crystal-board-game` |
| 9 | `living_crystal_weather` | `living-crystal-weather` |
| 10 | `living_crystal_clockwork` | `living-crystal-clockwork` |
| 11 | `living_curiosity_museum` | `living-curiosity-museum` |
| 12 | `living_shadow_puppet` | `living-shadow-puppet` |
| 13 | `living_ceramic_tile` | `living-ceramic-tile` |
| 14 | `living_embroidered_morning` | `living-embroidered-morning` |
| 15 | `living_community_quilt` | `living-community-quilt` |
| 16 | `living_impossible_blueprint` | `living-impossible-blueprint` |
| 17 | `living_surreal_scale_shop` | `living-surreal-scale-shop` |
| 18 | `living_crystal_comic` | `living-crystal-comic` |
| 19 | `living_paper_theater_windows` | `living-paper-theater-windows` |
| 20 | `living_found_object_message` | `living-found-object-message` |
