# Night / week-ahead creatives (Sacred Ground identity)

Campaign: `week_ahead` (~7:00 PM America/Chicago). Pool: `config/image_atmosphere.json`.

## Hard rule (Founder — Aug 6, 2026)

Every night plate must include a **clear Sacred Ground visual anchor inside the photograph** — storefront with name, circular logo / folk-art sun as a small sky or moon mark, bat-signal searchlights, or glowing “Sacred Ground” in the landscape.

**When a shop appears:** use real Sacred Ground storefront resemblance (eggplant awning, tan stone architecture). Invented fantasy facades are banned. Creative surroundings (sky, mountains, water) are fine without a shop.

Autopilot overlay logo + cream footer (see `.cursor/rules/social-image-branding.mdc`) still apply for non-prebranded posts, but **do not replace** in-photo SG identity. Bake the circular sun logo bottom-left when overlays do not run.

## Hard rule (Founder — Aug 9, 2026) — night mood + rotation

- Plates must read as **night**, not daytime sun.
- Sun-dominating / sun-in-sky plates are retired under
  `nighttime.creative_pool_retired_daytime_sun` (`daytime_sun: true`).
  Code skips them even if someone leaves a copy in `creative_pool`.
- Rotation enforces lifetime `never_reuse` via `data/state/image_usage.json` —
  any URL already posted is permanently blocked; fail closed rather than silently
  reuse (Founder Aug 12 FINAL). Same-slot FB+IG single-image mode may share one URL.

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

## Shop pride (Founder Aug 11 + Aug 12 FINAL)

- **Do not** overlay Chicago #1 / favorite badges onto existing night or celestial pool plates.
- Keep posting the current no-badge inventory until it naturally rotates out.
- When generating a **NEW** night / celestial creative, **must** append
  `social_proof.designed_in_generation_brief(seed, day=…, surface="night"|"celestial")`
  to the generation prompt (`designed_in_required: true`) so pride is designed into
  the plate (not a sticker after the fact).
- Live gates `badge_on_night` stay **false**.

## Audit

See `notes` + `creative_pool` / `creative_pool_retired_daytime_sun` /
`creative_pool_needs_sg_identity` in `config/image_atmosphere.json` for the live
PASS / retired-sun / FAIL tables.
