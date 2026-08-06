# Morning flyers (Cheryl-style)

Date-keyed finished flyers power Today Autopilot. Config: `config/morning_flyers.json`.

## Hard rule — no prices

Never put `$`, dollar amounts, ticket costs, or “$55”-style fees on morning flyer graphics. Do not use TEC `cost` on the image. Captions may still link to booking.

## Daily system

1. **Prefer prebuild (next 7 days)** — more reliable than inventing AI art at 7:00 AM:

   ```bash
   python3 -m marketing generate-morning-flyers --days 7 --source live-strict
   ```

   Writes local PNGs under `assets/sg-morning-flyer-YYYY-MM-DD-*.png`, appends config entries (`prebranded: true`).

2. **Upload missing URLs** — if the CLI reports `needs_upload`, upload via WordPress MCP `upload_media`, then set `url` + `media_id` in `morning_flyers.json` (or re-run with `--set-url` after upload).

3. **7am Today automation** — before drafts/publish, ensure today exists:

   ```bash
   python3 -m marketing generate-morning-flyers --days 1 --source live-strict
   # upload if needed, then:
   python3 -m marketing run --source live-strict
   python3 -m marketing publish-today
   ```

`pipeline.generate_batch` also calls `ensure_flyers_for_range(days=1)` so a missing today flyer is rendered locally before image selection. Autopilot uses the flyer when `url` is set; without a public URL it falls through to specialty/creative until upload completes.

## Content rules

| Rule | Detail |
|------|--------|
| Events on graphic | 1–3 max |
| Empty day | Warm “Sacred Ground today / visit us” flyer (not storefront-only) |
| Footer | Logo + shopsacredground.com + 847-749-3922 |
| Faces | Tina circle only with real ref photos; otherwise symbols |
| Overlays | `prebranded: true` → skip brand overlays |

## Local render vs AI polish

Default backend is a local PIL Cheryl-style compositor (sustainable offline). Agents may replace a day’s asset with a higher-fidelity mlimg / GenerateImage pass — still **no prices** — then update `url` / `media_id`.
