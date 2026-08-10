# Night / week-ahead creatives (Sacred Ground identity)

Campaign: `week_ahead` (~7:00 PM America/Chicago). Pool: `config/image_atmosphere.json`.

## Hard rule (Founder — Aug 6, 2026)

Every night plate must include a **clear Sacred Ground visual anchor inside the photograph** — storefront with name, circular logo / folk-art sun as a small sky or moon mark, bat-signal searchlights, or glowing “Sacred Ground” in the landscape.

Autopilot overlay logo + cream footer (see `.cursor/rules/social-image-branding.mdc`) still apply for non-prebranded posts, but **do not replace** in-photo SG identity.

## Hard rule (Founder — Aug 9, 2026) — night mood + rotation

- Plates must read as **night**, not daytime sun.
- Sun-dominating / sun-in-sky plates are retired under
  `nighttime.creative_pool_retired_daytime_sun` (`daytime_sun: true`).
  Code skips them even if someone leaves a copy in `creative_pool`.
- Rotation enforces `nighttime.no_repeat_days` (default **7**) via
  `data/state/image_usage.json`, and **never** reuses the same URL from the prior night.
- FB and IG still take different URLs the same night when the pool allows.

Cursor rule: `.cursor/rules/night-image-sacred-ground.mdc`.

## Do not

- Do not republish an already-live tonight post just to swap the creative.
- Do not leave pure aurora / Milky Way / star-trail / lake / meadow / temple plates in the active pool.
- Do not return sun-in-sky plates (`logo_sun_sky`, `sun_in_moon`, `logo_sun_horizon`) to the active pool.

## Regen / upload pattern

1. Generate `assets/sg-night-creative-*.png` with SG baked in (night mood).
2. Upload via WordPress MCP `upload_media`.
3. Set `url` on the pool entry; `sg_identity: "pass"`; remove from `creative_pool_needs_sg_identity`.
4. Atmosphere code skips any plate with `sg_identity` fail, `active: false`, or `daytime_sun: true`.

## Audit

See `notes` + `creative_pool` / `creative_pool_retired_daytime_sun` /
`creative_pool_needs_sg_identity` in `config/image_atmosphere.json` for the live
PASS / retired-sun / FAIL tables.
