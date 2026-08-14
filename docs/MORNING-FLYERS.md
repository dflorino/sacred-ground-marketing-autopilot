# Morning flyers (readable equal schedule — vary the art)

Date-keyed finished flyers power the morning Autopilot post (9:00 AM CT → **today’s full day**, then **tomorrow**). Prefer today’s date-key flyer when today has events. Config: `config/morning_flyers.json`.

## Hard creative ban — generic mystic AI template (Founder Aug 14, 2026 ~1:35pm CT)

**Rejected live look:** Fri Aug 14 navy equal-card collage with pristine AI singing bowls, shamanic drum, glowing healing hands, “Akashic Records” prop book — Canva/Midjourney wellness starter pack. Founder: *do not look like “Sacred Ground’s using the AI.” Completely individual, out of the box.*

**BAN:** floating singing bowls · glowing healing hands · pristine tarot fan · crystals on black velvet · Flower of Life wallpaper · Akashic prop books · ethereal purple fog · same factory layout every day (three dark cards + right mystic collage + gold script) when it reads as a template.

**REQUIRE:** shop-made / individual art — real storefront or interior when available, practitioner vibes, handcrafted collage, bold poster / typography, unexpected color, photography-first, or one strong original illustration. Designed-in Chicagoland pride. No prices. Equal space when multi-event. Never reuse URLs.

Future visual R&D concepts (preview only, not live posts): `data/composites/flyer-concepts-v1/`.

## Sacred Ground daily flyer system

Readability reference (not a daily clone): `assets/sg-morning-flyer-2026-08-06-today-collage.png`.

| Zone | Content |
|---|---|
| **Header** | Day / shop identity (mix fonts; gold script optional — not mandatory every day) |
| **Schedule** | 1–3 **equal-weight** event blocks — title + host + time + short keywords |
| **Art** | Shop-individual — never generic mystic dump |
| **Footer** | Circular logo + `shopsacredground.com` + `847-749-3922` + come-as-you-are |
| **Shop pride** | Caption/first-comment **ON**. No overlay badges on existing flyers. Every **NEW** gen/remake must bake designed-in pride via `designed_in_generation_brief` |

## Equal space (hard — Founder Aug 7, 2026)

Multi-event days must give **every practitioner the same visual weight**.

| OK | Not OK |
|---|---|
| Equal stacked / equal bands for every host | Aug 7 FB reflexology hero + tiny Robert “Also today” corner |
| Varied art languages day to day | Same mystic-card factory every morning |

Artistic single-event hero is allowed **only** when the day has exactly one event.

## Layout mix (required)

Vary the *look* day to day so the feed does not read as one template factory. Multi-event days always keep equal visual weight. `build_generation_prompt` must ban mystic AI starter-pack imagery and require shop-individual energy + designed-in pride.

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
| Layout mix | Equal weight multi-event; vary visual language; ban mystic AI template |
