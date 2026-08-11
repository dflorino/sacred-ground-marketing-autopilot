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

## Where it appears (rotates)

1. **Captions** — short line woven before hashtags on morning / afternoon / week_ahead / specialty (placement mode rotates).
2. **First comment** — Zernio `platformSpecificData.firstComment` on Facebook + Instagram when the placement mode is `first_comment` or `both` (live on publish).
3. **On-image badges** — rotating styles: `banner` · `circle` · `pill` · `ribbon` · `corner`
   - **Remake (Founder Aug 11 2026):** thin top cream/gold band, bottom strip above footer, or small soft seal in empty sky/margin — never giant white sticker disks over the Sacred Ground wordmark / event cards / logo / phone footer
   - Morning flyers: baked in `render_local_flyer` (photo area above cream footer)
   - Night creatives: `marketing.social_proof.apply_night_badge_if_eligible` when branding **local** shop/generic plates (skips pure celestial by default). Remote pool URLs are not rewritten at publish.

## Config

- Claims: `claims` (caption / first comment) + short `badge_claims` (1–2 lines; bands join with `·`)
- Styles: `badge_styles`
- Placement mix: `placement_modes` (`caption` / `first_comment` / `both`)

## Sample lines

- Chicago’s #1 talked-about crystal shop.
- Chicagoland’s favorite crystal & holistic center.
- Come stop by the crystal shop Chicago keeps talking about.
- #1 vibe in Chicagoland for crystals & healing.
