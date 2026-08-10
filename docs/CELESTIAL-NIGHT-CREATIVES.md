# Celestial creatives — dual cadence (2026)

Source of truth: `config/celestial_events.json`  
Briefs: `assets/celestial-2026/briefs.json`  
Module: `marketing/celestial.py`

## Cadence (America/Chicago)

For **each** celestial event:

| Slot | When | Campaign | Image | Caption lead |
|---|---|---|---|---|
| Night-before | event_date − 1 @ **7:00 PM** | `week_ahead` | `night.urls` plate | `caption_tomorrow` (“Tomorrow’s …”) |
| Morning-of | event_date @ **9:00 AM** | `today` | `morning.urls` plate | `caption_today` (“Today’s …”) |

Shop TEC listings stay in the caption when present. Celestial still posts if the shop calendar is empty that horizon.

## Priority

**Night (`nighttime_plan`):** celestial → full_moon → holiday → creative pool  

**Morning (`select_today_image`):** celestial morning → date-keyed morning flyer → specialty rules  

## Example — Total Solar Eclipse in Leo (Aug 12)

- **Aug 11 night** → tomorrow’s total solar eclipse in Leo + night plate  
- **Aug 12 morning** → today’s total solar eclipse in Leo + morning plate  

## Hard rules

Same SG-in-photo night identity as `docs/NIGHT-CREATIVES.md`. Distinct mediums/palettes — not ten milky-way clones. No prices on creatives.
