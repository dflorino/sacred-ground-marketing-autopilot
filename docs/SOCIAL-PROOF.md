# Social proof (shop pride — email Options A/B/C)

**Enabled** via `config/social_proof.json` → `"enabled": true` (Founder Aug 11, 2026).

**Vocabulary** aligned with email monthly org (Founder Aug 13 ~9:06am CT).

**Slot rotation** (Founder Aug 13 ~9:13am CT) — **no** weekday→option map.

## Canonical Options (primary rotating set)

| Option | ALL CAPS (on-image banners OK) | Caption / designed-in (title case) |
|---|---|---|
| **A** | CHICAGOLAND'S PREMIER CRYSTAL STORE & HOLISTIC DESTINATION | Sacred Ground — Chicagoland’s Premier Crystal Store & Holistic Destination. |
| **B** | CHICAGOLAND'S #1 CRYSTAL SHOP & HOLISTIC CENTER | Sacred Ground — Chicagoland’s #1 Crystal Shop & Holistic Center. |
| **C** | VOTED #1 CHICAGOLAND'S CRYSTAL STORE & HOLISTIC DESTINATION | Sacred Ground — Voted #1 Chicagoland’s Crystal Store & Holistic Destination. |

Config: `canonical_options` + `claims` / `badge_claims` / `badge_claims_by_style`.

## Slot rotation (America/Chicago) — no day mapping

`day_assignment` is **null / retired**. Options are assigned by **campaign slot
within each calendar day**, not by Tuesday/Thursday/Sunday.

Config: `config/social_proof.json` → `slot_rotation`.

### Normal day (3 posts)

| Slot | Campaign | Time (CT) | Option | Claim |
|---|---|---|---|---|
| Morning | `today` | 9:00 AM | **A** | Chicagoland’s Premier Crystal Store & Holistic Destination |
| Afternoon | `afternoon_spotlight` | 5:00 PM | **B** | Chicagoland’s #1 Crystal Shop & Holistic Center |
| Night | `week_ahead` | 7:00 PM | **C** | Voted #1 Chicagoland’s Crystal Store & Holistic Destination |

Each of the three daily posts gets a **different** Option (A / B / C).

### Tuesday (4 posts) — special always B

| Slot | Campaign | Time (CT) | Option |
|---|---|---|---|
| Morning | `today` | 9:00 AM | **A** |
| Special | `tuesday_meditation` | 4:00 PM | **B** (always) |
| Afternoon | `afternoon_spotlight` | 5:00 PM | **B** |
| Night | `week_ahead` | 7:00 PM | **C** |

Any other specialty / 4th post (`visit`, `spotlight`, … listed in
`always_option_b_campaigns`) also uses **Option B** exactly.

Code: `social_proof.resolve_option_id(..., campaign=…)` /
`designed_in_generation_brief(..., surface=…, campaign=…)`.

## Tone (hard)

These lines are **warm shop pride** — Founder / community “i vote it the best”
energy — **not** formal third-party award citations.

| OK | Soften / avoid |
|---|---|
| Options A/B/C above (Premier / #1 / Voted #1) | “Officially voted Best Of 20XX by [publication]” |
| Sacred Ground — Chicagoland’s #1 Crystal Shop & Holistic Center | Fake trophy / verified-award seal |
| ALL CAPS banners matching email blocks | Invented Chicago Reader / Best Of winners |

Repo search found **no** confirmed Chicago Reader / Best Of award source. Keep
claims warm and local; do not invent a citation. Toggle `"enabled": false` to
silence everywhere.

## Where it appears

1. **Captions** — short line woven before hashtags (placement mode still rotates caption-in vs comment-only). **ON.**
2. **First comment** — Zernio `platformSpecificData.firstComment` on Facebook + Instagram. **ALWAYS ON** for every FB/IG publish (`always_first_comment: true`, Founder Aug 14 2026). Caption-only placement no longer skips the comment.
3. **On-image** — **not via overlays on existing art.**

Publish path: `marketing/publish.schedule_payload` attaches `firstComment` from
`caption.social_proof.first_comment` (or falls back to `claim`) for facebook +
instagram. When `firstComment` is in the create payload, Zernio auto-posts it
after publish (verified live on IG Aug 14 morning).

## On-image cutover (Founder Aug 11 ~3:05pm CT) — hard

> “NO REMAKE NEW IMAGES THAT WILL START AFTER THE ONES MADE WITHOUT THE BADGES END”

Meaning:

| Do | Do not |
|---|---|
| Keep posting current no-badge morning / night / celestial inventory | Stamp badges onto already-made flyers or pool plates |
| Keep rotating caption + first-comment claims (A/B/C by slot) | Remake Aug 6 / v3 / v4 overlay preview spam on finished art |
| When generating **NEW** art, bake pride into the generation prompt (**required**) | Post-hoc sticker / seal / footer_band overlay on old creatives |

Config flags:

- `badge_on_morning_flyers`: **false** — no live morning overlay
- `badge_on_night`: **false** — no live night overlay
- `only_on_newly_generated` / `never_overlay_existing`: **true**
- `designed_in_on_new_generation`: **true**
- **`designed_in_required`: true** (Founder Aug 12 ~5:54pm CT) — every NEW morning / night / afternoon / celestial gen or remake must include designed-in pride
- `badge_from_date`: optional `YYYY-MM-DD` (America/Chicago); `null` = brief applies whenever a **new** image is generated

Code:

- `social_proof.resolve_option_id(seed, day_key=…, campaign=…)` → `"A"` / `"B"` / `"C"` by slot
- `social_proof.designed_in_generation_brief(seed, day=…, surface="morning"|"night"|"afternoon"|"celestial", campaign=…)` → prompt fragment for **new** gens only (uses Option A/B/C phrases for that slot)
- Wired into `morning_flyers.build_generation_prompt` for AI flyer generations (`campaign="today"` → A)
- Night / celestial / afternoon **regen** prompts **must** call the same helper — do **not** stamp old inventory
- `should_badge_morning` / `should_badge_night` / `apply_badge_to_path` refuse overlays while `never_overlay_existing` is true

Cursor rule: `.cursor/rules/social-proof-on-image.mdc`.

## Sample caption lines

- Sacred Ground — Chicagoland’s Premier Crystal Store & Holistic Destination.
- Sacred Ground — Chicagoland’s #1 Crystal Shop & Holistic Center.
- Sacred Ground — Voted #1 Chicagoland’s Crystal Store & Holistic Destination.
