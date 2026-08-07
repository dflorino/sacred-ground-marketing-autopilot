# Morning flyers (Thursday-style equal cards)

Date-keyed finished flyers power the morning Autopilot post (9:00 AM CT → **tomorrow’s** events). Config: `config/morning_flyers.json`.

## Sacred Ground daily flyer template (Thursday-style)

**Gold standard (Founder-approved):** `assets/sg-morning-flyer-2026-08-06-today-collage.png`

Use **versions of this layout system** — beautiful and easy to read — not an exact clone every day (gets stale), and not busy collage soup.

| Zone | Content |
|---|---|
| **Header** | `{WEEKDAY} AT` + **Sacred Ground** (gold script) + `Mind • Body • Spirit • Community` |
| **Left** | Clear stacked rounded **equal cards** — one event per card, same height: icon + name + host + time + short keywords |
| **Right** | Evocative graphics supporting those events (clear zones, not overlapping clutter) |
| **Footer** | Sacred Ground circular logo + `shopsacredground.com` + `847-749-3922` + come-as-you-are energy |

## Equal space (hard — Founder Aug 7, 2026)

Multi-event days must give **every practitioner the same visual weight**.

| OK | Not OK |
|---|---|
| Aug 6 gold standard — 3 equal stacked cards | Aug 7 FB reflexology hero + tiny Robert “Also today” corner |
| Aug 7 IG / Aug 8 Lions Gate — equal cards | One giant photo + secondary badge |

Artistic single-event hero is allowed **only** when the day has exactly one event. Never demote a second practitioner into a corner callout.

## Layout mix (required)

| Share | Style | When |
|---|---|---|
| **~75%** | **Thursday-style equal card layout** | Default; **always** for multi-event days |
| **~25%** | Artistic single-event hero | Only when still highly readable **and** exactly one event |

`generate-morning-flyers` / `build_generation_prompt` force Thursday equal cards when 2+ events.

## Hard rule — no prices

Never put `$`, dollar amounts, ticket costs, or “$55”-style fees on morning flyer graphics. Do not use TEC `cost` on the image. Captions may still link to booking.

## Hard rule — Facebook ≠ Instagram images (same full-day info)

For date-keyed morning flyers, **Facebook and Instagram use different visuals**, but **both carry the same full-day information** on **equal** Thursday-style cards.

| Field | Platform |
|---|---|
| `url` (or `urls[0]`) | Facebook — variant A |
| `url_instagram` (or `urls[1]`) | Instagram — variant B |
| `local` / `local_instagram` | Local PNGs for each variant |

Aug 6 gold standard may remain a single shared URL — do not overwrite or republish solely to split platforms.

### Platform energy (Founder — Aug 7, 2026)

| Platform | Energy |
|---|---|
| **Facebook** (`url` / variant A) | Cleaner equal-card layout OK — gold-standard readability |
| **Instagram** (`url_instagram` / variant B) | Same equal cards + richer multi-tone mystical pop (not flat washes) |

Do not republish live posts just to swap a plate — updating archive assets for future reuse is fine.

## Daily system

1. **Prefer prebuild (next 7 days)**:

   ```bash
   python3 -m marketing generate-morning-flyers --days 7 --source live-strict
   ```

2. **Morning job @ 9am** — ensure tomorrow (and today if same-day evening is included):

   ```bash
   python3 -m marketing generate-morning-flyers --start-offset 1 --days 1 --source live-strict
   python3 -m marketing run --source live-strict
   python3 -m marketing publish-today
   ```

`pipeline.generate_batch` ensures flyers for publish-day + tomorrow before image selection.

## Content rules

| Rule | Detail |
|---|---|
| Events on graphic | 1–3 max; **equal card size** when 2+ |
| Empty day | Warm visit flyer (no “TODAY” squeeze badge) |
| Footer | Logo + shopsacredground.com + 847-749-3922 |
| Faces | Tina circle only with real ref photos; otherwise symbols |
| Overlays | `prebranded: true` → skip brand overlays |
| Layout mix | ~75% equal Thursday cards / ~25% single-event artistic hero only |
