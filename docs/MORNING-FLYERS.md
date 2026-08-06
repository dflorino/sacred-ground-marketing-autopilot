# Morning flyers (Thursday-style)

Date-keyed finished flyers power Today Autopilot. Config: `config/morning_flyers.json`.

## Sacred Ground daily flyer template (Thursday-style)

**Gold standard (Founder-approved):** `assets/sg-morning-flyer-2026-08-06-today-collage.png`

Use **versions of this layout system** — beautiful and easy to read — not an exact clone every day (gets stale), and not busy collage soup.

| Zone | Content |
|---|---|
| **Header** | `{WEEKDAY} AT` + **Sacred Ground** (gold script) + `Mind • Body • Spirit • Community` |
| **Left** | Clear stacked rounded **cards** — one event per card: icon + name + host + time + short keywords |
| **Right** | Evocative graphics supporting those events (clear zones, not overlapping clutter) |
| **Footer** | Sacred Ground circular logo + `shopsacredground.com` + `847-749-3922` + come-as-you-are energy |

- Dark elegant palette with gold accents (vary colors by day so the pack does not feel identical)
- Separated event blocks beat freeform piles of imagery
- **No prices** on the graphic
- No invented practitioner faces — symbols/silhouettes OK

## Layout mix (required)

| Share | Style | When |
|---|---|---|
| **~75%** | **Thursday-style clear card layout** | Default for new/future flyers; always prefer for multi-event days |
| **~25%** | Artistic single-event hero | Only when still highly readable; one primary event; short ALSO TODAY line OK |

`generate-morning-flyers` / `build_generation_prompt` defaults to Thursday-style cards. Deterministic mix: multi-event days → cards; ~1/4 of single-event days may roll artistic hero. Do not ship chaotic collage soup in either bucket.

## Hard rule — no prices

Never put `$`, dollar amounts, ticket costs, or “$55”-style fees on morning flyer graphics. Do not use TEC `cost` on the image. Captions may still link to booking.

## Hard rule — Facebook ≠ Instagram images (same full-day info)

For date-keyed morning flyers, **Facebook and Instagram use different visuals**, but **both carry the same full-day information** (all main events of the day on readable Thursday-style cards). Never ship an incomplete single-event alt (or a price-bearing plate) to one platform.

| Field | Platform |
|---|---|
| `url` (or `urls[0]`) | Facebook |
| `url_instagram` (or `urls[1]`) | Instagram |
| `local` / `local_instagram` | Local PNGs for each variant |

`generate-morning-flyers` builds **two layout variants** per day (palette / right-side graphic differ; same event cards). If only one public URL exists, Autopilot temporarily shares it (logged) until the second variant is uploaded.

Aug 6 gold standard may remain a single shared URL — do not overwrite or republish solely to split platforms.

## Daily system

1. **Prefer prebuild (next 7 days)** — more reliable than inventing AI art at 7:00 AM:

   ```bash
   python3 -m marketing generate-morning-flyers --days 7 --source live-strict
   ```

   Writes local PNGs under `assets/sg-morning-flyer-YYYY-MM-DD-*.png` (variant A + `-b` for IG), appends config entries (`prebranded: true`). Prompts default to Thursday-style cards (~75%).

2. **Polish to Thursday-style** when a day needs Founder-quality art — keep the card layout system for most days; update `url` / `url_instagram` / media ids after WordPress upload.

3. **Upload missing URLs** — if the CLI reports `needs_upload`, upload via WordPress MCP `upload_media`, then set URLs:

   ```bash
   python3 -m marketing generate-morning-flyers --set-url YYYY-MM-DD https://…/file-a.png --media-id N --platform facebook
   python3 -m marketing generate-morning-flyers --set-url YYYY-MM-DD https://…/file-b.png --media-id M --platform instagram
   ```

4. **7am Today automation** — before drafts/publish, ensure today exists:

   ```bash
   python3 -m marketing generate-morning-flyers --days 1 --source live-strict
   # upload if needed, then:
   python3 -m marketing run --source live-strict
   python3 -m marketing publish-today
   ```

`pipeline.generate_batch` also calls `ensure_flyers_for_range(days=1)` so a missing today flyer is rendered locally before image selection. Autopilot uses the flyer when the platform URL is set; without a public URL it falls through to specialty plates then store exterior.

## Content rules

| Rule | Detail |
|---|---|
| Events on graphic | 1–3 max (same covers on FB + IG variants) |
| Empty day | Warm “Sacred Ground today / visit us” flyer (Thursday-style visit card) |
| Footer | Logo + shopsacredground.com + 847-749-3922 |
| Faces | Tina circle only with real ref photos; otherwise symbols |
| Overlays | `prebranded: true` → skip brand overlays |
| Layout mix | ~75% Thursday cards / ~25% readable artistic hero |
| Platforms | Two different full-day variants; never prices on either |

## Rejected: atmospheric creative plates

The plain `sg-morning-creative-*` pack was removed from `assets/` and `config/image_rules.json`. Do not put those URLs back into Autopilot rotation. Date flyers + specialty library + store exterior remain the path.

## Local render vs AI polish

Default backend is a local PIL compositor (sustainable offline) that emits **variant A + variant B**. Agents may replace a day’s asset with a higher-fidelity pass that follows the **Thursday-style template** (~75% of the time) — still **no prices**, still **full-day info on both platforms** — then update `url` / `url_instagram` / media ids. Never overwrite a Founder-loved day’s flyer when redesigning other dates. Never overwrite the Aug 6 gold standard.
