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

1. **Captions** — short line woven before hashtags on morning / afternoon / week_ahead / specialty (placement mode rotates). **ON.**
2. **First comment** — Zernio `platformSpecificData.firstComment` on Facebook + Instagram when the placement mode is `first_comment` or `both` (live on publish). **ON.**
3. **On-image badges** — **OFF by default** until Founder greenlights a style
   (Aug 11 ~2:52pm CT: “no rebuild these look bad” — v1 sticker spam + v2 tiny/unreadable both rejected).

### On-image rebuild (preview only)

Two strong styles only (`badge_styles`: `seal` · `footer_band`):

| Style | Look |
|---|---|
| `seal` | Substantial gold/cream circular wax seal (~14–18% image width), readable 2–3 line claim, empty margin only (not over title/cards/logo) |
| `footer_band` | Dedicated cream band **extending the canvas** below photo/flyer content — brand-footer energy, not a floating pill over art |

Gates (both `false` until approved):

- `badge_on_morning_flyers`
- `badge_on_night`

When re-enabled: morning flyers bake via `render_local_flyer`; night locals via `apply_night_badge_if_eligible` (skips pure celestial by default). Remote pool URLs are not rewritten at publish.

## Config

- Claims: `claims` (caption / first comment) + short `badge_claims` (2–3 lines for seal; footer_band joins with `·`)
- Styles: `badge_styles` (`seal`, `footer_band`)
- Placement mix: `placement_modes` (`caption` / `first_comment` / `both`)
- Status note: `on_image_status`

## Sample lines

- Chicago’s #1 talked-about crystal shop.
- Chicagoland’s favorite crystal & holistic center.
- Come stop by the crystal shop Chicago keeps talking about.
- #1 vibe in Chicagoland for crystals & healing.
