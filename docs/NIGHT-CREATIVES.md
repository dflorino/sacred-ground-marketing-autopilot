# Night / week-ahead creatives (Sacred Ground identity)

Campaign: `week_ahead` (~7:00 PM America/Chicago). Pool: `config/image_atmosphere.json`.

## Hard rule (Founder — Aug 6, 2026)

Every night plate must include a **clear Sacred Ground visual anchor inside the photograph** — storefront with name, circular logo / folk-art sun as sky or moon mark, bat-signal searchlights, or glowing “Sacred Ground” in the landscape.

Autopilot overlay logo + cream footer (see `.cursor/rules/social-image-branding.mdc`) still apply for non-prebranded posts, but **do not replace** in-photo SG identity.

Cursor rule: `.cursor/rules/night-image-sacred-ground.mdc`.

## Do not

- Do not republish an already-live tonight post just to swap the creative.
- Do not leave pure aurora / Milky Way / star-trail / lake / meadow / temple plates in the active pool.

## Regen / upload pattern

1. Generate `assets/sg-night-creative-*.png` with SG baked in.
2. Upload via WordPress MCP `upload_media`.
3. Set `url` on the pool entry; `sg_identity: "pass"`; remove from `creative_pool_needs_sg_identity`.
4. Atmosphere code skips any plate with `sg_identity` fail or `active: false`.

## Audit (Aug 6, 2026)

See `notes` + `creative_pool` / `creative_pool_needs_sg_identity` in `config/image_atmosphere.json` for the live PASS/FAIL table and regen priority.
