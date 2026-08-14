# Flyer concepts v1

**Status (Founder Aug 14 ~2:14–2:31pm CT):** four approved art styles **plus** existing
Thursday equal-card / artistic hero approaches in one **random mixed pool**. Unused
date-keyed queue plates stay eligible. Series limits: max **1 consecutive** day per
style, max **2** in any rolling **7** Chicago days. Banned mystic AI navy template =
series_limit 0. **Every** morning plate must bake Chicagoland #1 / Premier / Voted
pride into the image. Do **not** run “new styles only for two weeks.” Preview samples
are **not** a replacement for any live morning post unless Founder asks.

## Mixed morning pool

Day-seeded random among series-eligible ids:

1. Magritte floating door — LOVED
2. Folk outsider night — YES
3. Da Vinci storefront sketch — LIKE
4. Einstein chalkboard map — LIKE (production must fix typography/contrast)
5. Thursday equal-card shop-made — existing approach (keep)
6. Artistic single-event hero shop-made — existing (single-event only)

Config: `config/morning_flyer_styles.json`  
Code: `marketing.morning_flyers.choose_visual_style` / `build_generation_prompt`

## Pride (required on EVERY morning plate)

Designed-in Chicagoland pride baked into the image — prefer visible **#1 Chicagoland** /
Premier / Voted #1. NEW gens: `designed_in_generation_brief`. Queued plates missing
pride: bake into a **NEW** url (`bake_designed_in_pride_new_asset`). Caption slot for
morning remains Option A; on-image follows style map.

## Approved production samples

`approved/` — production-ready plates (Fri schedule dummy OK). Einstein sample
uses the readability fix (larger type, calmer slate behind schedule).

## Archived OUT

`archived/` — Bauhaus Swiss goldleaf + Victorian botanical ledger. Keep for
reference; **never** pick for morning generation.

## Policy

- Do **not** upload / republish social unless Founder asks
- Large PNGs may stay local / gitignored; this README + CATALOG are the record
- No prices on plates
- Ban generic mystic AI navy wellness template forever (series_limit 0)
- Keep unused queued morning flyers + legacy approaches in the random mix
- Never-reuse URLs absolute
