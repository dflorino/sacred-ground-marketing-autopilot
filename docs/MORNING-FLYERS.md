# Morning flyers (readable equal schedule — vary the art)

Date-keyed finished flyers power the morning Autopilot post (9:00 AM CT → **today’s full day**, then **tomorrow**). Prefer today’s date-key flyer when today has events. Config: `config/morning_flyers.json`.

## Hard creative ban — generic mystic AI template (Founder Aug 14, 2026 ~1:35pm CT)

**Rejected live look:** Fri Aug 14 navy equal-card collage with pristine AI singing bowls, shamanic drum, glowing healing hands, “Akashic Records” prop book — Canva/Midjourney wellness starter pack. Founder: *do not look like “Sacred Ground’s using the AI.” Completely individual, out of the box.*

**BAN:** floating singing bowls · glowing healing hands · pristine tarot fan · crystals on black velvet · Flower of Life wallpaper · Akashic prop books · ethereal purple fog · same factory layout every day (three dark cards + right mystic collage + gold script) when it reads as a template.

**REQUIRE:** mixed-pool art (four approved languages + existing shop-made approaches below). Designed-in Chicagoland **#1 / Premier / Voted** pride on every morning plate. No prices. Equal space when multi-event. Never reuse URLs.

## Visual style mixed pool (Founder Aug 14 ~2:14pm + ~2:29–2:31pm CT)

Config: `config/morning_flyer_styles.json` · picker: `choose_visual_style(day)` (`selection_mode: random_mixed`).

**Do not** run “new styles only for two weeks” then dump old Thursday plates afterward — interleave the full mix.

### What’s in the mix

| Id | Kind |
|---|---|
| Magritte floating door | Approved art |
| Folk outsider night | Approved art |
| Da Vinci storefront sketch | Approved art |
| Einstein chalkboard map | Approved art (large high-contrast schedule type) |
| Thursday equal-card shop-made | Existing morning approach (keep) |
| Artistic single-event hero shop-made | Existing approach (single-event only) |
| Unused date-keyed flyers in `morning_flyers.json` | Queued plates (URL must still be unused) |

**OUT / series_limit 0:** Bauhaus · Victorian · generic mystic AI navy wellness template.

### How random pick works

1. Build the mixed pool (above), drop artistic-hero on multi-event days.
2. Drop any style that would break series limits against recent queue/`visual_style` history.
3. Day-seeded shuffle → pick first eligible (stable per Chicago date; not ordinal lockstep).

### Series limits (hard)

| Cap | Value |
|---|---|
| Max consecutive days | **1** (same style id/family) |
| Rolling window | **7** Chicago days |
| Max per style in window | **2** |
| Banned mystic / Bauhaus / Victorian | **0** |

### Queue + never-reuse

| Rule | Detail |
|---|---|
| Keep approaches | Unused queued plates + legacy shop-made styles stay eligible |
| Never-reuse URLs | Absolute via `image_usage` — keeping a *style* ≠ re-posting a used URL |
| Pride on queued | If a queued flyer lacks baked-in pride → bake into a **NEW** local/url before use |

### Pride guarantee (every morning plate)

Every single morning image must show Chicagoland **#1 / Premier / Voted #1** baked into the picture (not caption-only). NEW gens use `designed_in_generation_brief` + style pride map. Queued plates missing pride use `bake_designed_in_pride_new_asset` → new URL.

| Style | On-image pride default |
|---|---|
| Magritte | B `#1 Crystal Shop` |
| Folk | C `Voted #1` |
| Da Vinci | A `Premier` |
| Einstein | B `#1` |
| Thursday shop-made | B `#1` |
| Artistic hero | A `Premier` |

Approved samples: `data/composites/flyer-concepts-v1/approved/`. Do **not** replace live posts unless Founder asks.

## Living Worlds series (Founder approved Aug 23, 2026)

**20 rotating imaginative morning worlds** — crystal, jewelry, incense, candle, reader, coffee in every design. **5–8s MP4 loops** + static cover for email. Mixes with legacy pool (phased). Full spec: **`docs/MORNING-LIVING-WORLDS.md`** · config: `config/morning_living_worlds.json`. Autopilot picks only when `status: active` and assets exist.

## Surprise campaign (Founder Sep 5, 2026)

**Hard law:** if another metaphysical store would logically use this image, **reject**. First visual should stop the scroll (Vogue / museum / Wes Anderson miniature / absurd editorial) — Sacred Ground + schedule are the reveal.

Config: **`config/morning_surprise_campaign.json`** · styles in `morning_flyer_styles.json` · `choose_visual_style` prefers `date_plan_YYYY_MM` when set.

Flagship recurring: **Where Did Sacred Ground Land Today?** (recognizable eggplant-awning storefront in impossible places; people act normal). Weekly architecture preference: newspaper Mon · artifact Tue · tiny universe Wed (max 2/month) · unpredictable rest. Tarot-card oversized plates max **2/month**. Sep 3 colorful Thursday equal-cards = fall color gold standard for multi-event readable days.

## Sacred Ground daily flyer system

Readability reference: `assets/sg-morning-flyer-2026-08-06-today-collage.png`. Art language is a day-seeded random mix from the full pool above (series-limited).

| Zone | Content |
|---|---|
| **Header** | Day / shop identity (mix fonts; gold script optional — not mandatory every day) |
| **Schedule** | 1–3 **equal-weight** event blocks — title + host + time + short keywords |
| **Art** | Mixed pool (Magritte / Folk / Da Vinci / Einstein / Thursday shop-made / artistic hero) — never mystic dump, never Bauhaus/Victorian |
| **Footer** | Circular logo + `shopsacredground.com` + `847-749-3922` + come-as-you-are |
| **Shop pride** | Caption/first-comment **ON**. No overlay badges on used URLs. Every morning plate must bake designed-in pride (`designed_in_generation_brief` / `bake_designed_in_pride_new_asset`). Prefer visible **#1 Chicagoland** energy on morning art. |

## Equal space (hard — Founder Aug 7, 2026)

Multi-event days must give **every practitioner the same visual weight**.

| OK | Not OK |
|---|---|
| Equal stacked / equal bands for every host | Aug 7 FB reflexology hero + tiny Robert “Also today” corner |
| Varied art languages day to day | Same mystic-card factory every morning |

Artistic single-event hero is allowed **only** when the day has exactly one event.

## Layout mix (required)

True **random mix** of Magritte / Folk / Da Vinci / Einstein / Thursday shop-made / artistic hero (series limits: 1 consecutive / max 2 per rolling 7) so the feed does not read as one template factory or a two-week new-styles block. Keep unused queued date flyers. Multi-event days always keep equal visual weight. `build_generation_prompt` must include the day’s `visual_style`, ban mystic AI + Bauhaus/Victorian, and require designed-in #1 / Chicagoland pride on **every** plate.

## Hard rule — no prices

Never put `$`, dollar amounts, ticket costs, or “$55”-style fees on morning flyer graphics. Do not use TEC `cost` on the image. Captions may still link to booking.

## Hard rule — single-image mode (Founder Aug 10, 2026)

One excellent primary plate posts to **both Facebook and Instagram**.

| Field | Role |
|---|---|
| `url` / `local` | Primary plate — used on FB **and** IG |
| `url_instagram` / `local_instagram` | Legacy / optional — ignored unless `allow_ig_variant: true` |

Do not generate a separate weaker Instagram variant. Pipeline reuses the same media URL on both platforms (all campaigns).

### Color energy (hard — Founder Aug 10 + Aug 14, 2026)

The shared plate must look **colorful, bright, interesting, engaging** — unexpected bold color welcome (coral, teal, sunflower, eggplant), not only navy+gold. Reject drab / muddy sludge, empty near-black voids, **and** the generic mystic AI starter pack (Aug 14 reject). Gate: `flyer_passes_visual_energy`.

**Do not republish** already-live morning posts just to swap art unless the Founder explicitly asks (Aug 14: leave rejected live flyer alone; explore concepts offline in `data/composites/flyer-concepts-v1/` first).

## Daily system

1. **Prefer prebuild (next 7 days)**:

   ```bash
   python3 -m marketing generate-morning-flyers --days 7 --source live-strict
   ```

2. **Morning job @ 9am** — ensure today + tomorrow flyers:

   ```bash
   python3 -m marketing generate-morning-flyers --start-offset 0 --days 2 --source live-strict
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
| Layout mix | Equal weight multi-event; rotate Magritte/Folk/Da Vinci/Einstein; ban mystic AI + Bauhaus/Victorian |
