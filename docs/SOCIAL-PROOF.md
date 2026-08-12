# Social proof (playful shop pride)

**Enabled** via `config/social_proof.json` → `"enabled": true` (Founder Aug 11, 2026).

## Tone (hard)

These lines are **general / playful shop pride** — “i vote it the best! lol” energy — **not** formal third-party award citations.

| OK | Soften / avoid |
|---|---|
| Chicago’s #1 talked-about crystal shop | “Officially voted Best Of 20XX by [publication]” |
| Chicagoland’s favorite crystal & holistic center | Fake trophy / verified-award seal |
| Come stop by the crystal shop Chicago keeps talking about | Invented Chicago Reader / Best Of winners |

Repo search found **no** confirmed Chicago Reader / Best Of award source. Keep claims warm and local; do not invent a citation. Toggle `"enabled": false` to silence everywhere.

## Where it appears

1. **Captions** — short line woven before hashtags (placement mode rotates). **ON.**
2. **First comment** — Zernio `platformSpecificData.firstComment` on Facebook + Instagram. **ON.**
3. **On-image** — **not via overlays on existing art.**

## On-image cutover (Founder Aug 11 ~3:05pm CT) — hard

> “NO REMAKE NEW IMAGES THAT WILL START AFTER THE ONES MADE WITHOUT THE BADGES END”

Meaning:

| Do | Do not |
|---|---|
| Keep posting current no-badge morning / night / celestial inventory | Stamp badges onto already-made flyers or pool plates |
| Keep rotating caption + first-comment claims | Remake Aug 6 / v3 / v4 overlay preview spam on finished art |
| When generating **NEW** art, bake pride into the generation prompt (**required**) | Post-hoc sticker / seal / footer_band overlay on old creatives |

Config flags:

- `badge_on_morning_flyers`: **false** — no live morning overlay
- `badge_on_night`: **false** — no live night overlay
- `only_on_newly_generated` / `never_overlay_existing`: **true**
- `designed_in_on_new_generation`: **true**
- **`designed_in_required`: true** (Founder Aug 12 ~5:54pm CT) — every NEW morning / night / afternoon / celestial gen or remake must include designed-in pride
- `badge_from_date`: optional `YYYY-MM-DD` (America/Chicago); `null` = brief applies whenever a **new** image is generated

Code:

- `social_proof.designed_in_generation_brief(seed, day=…, surface="morning"|"night"|"afternoon"|"celestial")` → prompt fragment for **new** gens only
- Wired into `morning_flyers.build_generation_prompt` for AI flyer generations
- Night / celestial / afternoon **regen** prompts **must** call the same helper — do **not** stamp old inventory
- `should_badge_morning` / `should_badge_night` / `apply_badge_to_path` refuse overlays while `never_overlay_existing` is true

Cursor rule: `.cursor/rules/social-proof-on-image.mdc`.

## Sample caption lines

- Chicago’s #1 talked-about crystal shop.
- Chicagoland’s favorite crystal & holistic center.
- Come stop by the crystal shop Chicago keeps talking about.
- #1 vibe in Chicagoland for crystals & healing.
