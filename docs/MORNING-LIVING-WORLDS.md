# Morning Living Worlds — approved series (Founder Aug 23, 2026)

**Status:** Founder-approved concept series · phased production rollout  
**Config:** `config/morning_living_worlds.json`  
**Mixes with:** existing morning pool in `config/morning_flyer_styles.json` (Magritte, Folk, Da Vinci, Einstein, Thursday cards, artistic hero)  
**Agent rule:** `.cursor/rules/morning-living-worlds.mdc`

---

## What this is

A **rotating series of living morning worlds** — same shop every day, different imaginative doorway. Each morning post still delivers:

- **GOOD MORNING** (or day-specific greeting) + date + Sacred Ground
- **Who is reading today** + today’s events/classes
- **Same caption + first-comment links** as current morning automation (booking URLs, shop pride A/B/C by slot)
- **Six visual anchors** in every design: crystal · jewelry · incense · candle · reader · coffee

**Movement:** Each concept produces a **5–8s seamless MP4 loop** (slow, 3–5 moving elements) plus a **static cover** for email/thumbnail.

**Production stack (Founder Aug 23):** Layered **Remotion** compositions — not flat PIL/ffmpeg pixel animation. Decompose scene art into transparent PNG layers + clean background plate **before** animating. Text stays live React/HTML. See `docs/LIVING-WORLDS-LAYER-PREP.md` and `remotion/`.

---

## Six anchors (required in every design)

| Anchor | Rule |
|--------|------|
| Crystal | At least one clearly visible crystal or specimen |
| Jewelry | At least one finished piece (necklace, ring, earrings) |
| Candle | Burning or about to be lit |
| Incense | Visible curl of smoke |
| Reader | Featured reader setting or card |
| Coffee | Fresh cup, pour, or steam |

---

## Information hierarchy (on-image)

1. Morning greeting  
2. Day and date  
3. Featured reader(s)  
4. Main event / reason to visit  
5. Times (main slot)  
6. Secondary activities (if room)  
7. Call to action  
8. Footer: `shopsacredground.com` + `847-749-3922` + circular logo  

**Founder Aug 23:** Fine detail schedule should not live in tiny illegible labels inside the art. The **world creates the invitation**; a **clean readable panel** (or caption) carries the full schedule. Multi-event days still need **equal visual weight** per practitioner when 2+ events appear on the panel.

**Never on graphics:** dollar prices (`$`, ticket amounts). **FREE** for free community events is OK.

---

## Social deliverables (every concept)

| Asset | Size | Use |
|-------|------|-----|
| Animated vertical | 1080×1920 | Reels, Stories |
| Animated feed | 1080×1350 | IG + FB feed (primary) |
| Static cover | 1080×1350 | Thumbnail, email hero, backup post |

Email: **same static cover** with play invitation linking to the social MP4 (unless FluentCRM supports inline video reliably).

---

## Movement rules

**Use:** candle flicker · coffee steam · incense smoke · slow crystal rotation · light reflections · gentle jewelry sway · one card reveal · doors/drawers · slow pour · single hand action · subtle camera drift  

**Avoid:** rapid flash · everything moving · fast zoom · bouncing text · smoke over text · unreadable micro labels · sound-dependent motion  

**Ideal 7s loop:** 0–1 quiet · 1–3 main action · 3–5 anchors respond · 5–6 reader/event · 6–7 steam/light/smoke loops back  

---

## Rotation rules (system)

| Rule | Value |
|------|-------|
| Same design | Not within **7** Chicago days |
| Same visual medium | Not on **consecutive** days |
| Two dark designs | Not back-to-back |
| Two compartment designs | Not back-to-back |
| Two overhead tabletop | Not back-to-back |
| Busy formats | Only when **2+ events** |
| Single-object formats | When **1 reader / 1 event** |
| Hero object | Change crystal, jewelry, candle color, coffee vessel, reader setting each return |
| Every 7 days include | paper · tactile handmade · architectural/compartment · storytelling · mechanism · quiet · high-energy |

**Weekday hints** (soft preference — see `config/morning_living_worlds.json`):

| Day | Energy |
|-----|--------|
| Mon | Start / awakening |
| Tue | Discovery / surprises |
| Wed | Handmade / behind scenes |
| Thu | Feature presentation |
| Fri | Celebration / weekend energy |
| Sat | Busy living shop |
| Sun | Warm / reflective |

Four-week sample calendar is in `config/morning_living_worlds.json` → `sample_calendar`.

---

## The 20 concepts

| # | ID | Name | Best days |
|---|-----|------|-----------|
| 1 | `living_crystal_morning_machine` | Crystal Morning Machine | Mon, month start |
| 2 | `living_matchbox_mysteries` | Matchbox Mysteries | Tue, multi-announcement |
| 3 | `living_popup_crystal_shop` | Pop-Up Crystal Shop | Wed, workshops |
| 4 | `living_nine_oclock_theater` | Nine O’Clock Crystal Theater | Thu, special readers |
| 5 | `living_cabinet_treasures` | Cabinet of Today’s Treasures | Fri, varied schedule |
| 6 | `living_inside_crystal_shop` | Inside the Crystal Shop | Sat, busy day |
| 7 | `living_shopkeeper_workbench` | Shopkeeper’s Mystical Workbench | Sun, BTS |
| 8 | `living_crystal_board_game` | Crystal Board Game | Multi-event, hunts |
| 9 | `living_crystal_weather` | Crystal Weather Forecast | Seasonal / playful |
| 10 | `living_crystal_clockwork` | Crystal Clockwork Morning | Month start, major news |
| 11 | `living_curiosity_museum` | Morning Curiosity Museum | Classes, demos |
| 12 | `living_shadow_puppet` | Shadow-Puppet Crystal Morning | Quiet / reflective |
| 13 | `living_ceramic_tile` | Ceramic Tile Morning | Seasonal, community |
| 14 | `living_embroidered_morning` | Embroidered Crystal Morning | Craft, cozy |
| 15 | `living_community_quilt` | Community Crystal Quilt | Community events |
| 16 | `living_impossible_blueprint` | Impossible Crystal Blueprint | Classes, complex schedule |
| 17 | `living_surreal_scale_shop` | Surreal Scale Crystal Shop | Surprise slot Tue/Fri |
| 18 | `living_crystal_comic` | Crystal Comic Morning | Mon, humor |
| 19 | `living_paper_theater_windows` | Paper Theater Windows | Multi-reveal days |
| 20 | `living_found_object_message` | Found-Object Morning Message | Simple / bold message |

Full build + movement notes per concept: `config/morning_living_worlds.json`.

---

## Mixing with existing morning art

**Founder Aug 23:** Living Worlds **mix into** the current morning pool — not replace Magritte / Folk / Da Vinci / Einstein / Thursday / hero overnight.

**Phased integration** (`config/morning_living_worlds.json` → `integration`):

1. **Phase 1 (now):** Concepts approved; config + docs; no autopilot pick until first plate exists.  
2. **Phase 2:** First 4 concepts produced (still + loop) → `status: active` on those ids → enter `living_worlds_pool`.  
3. **Phase 3:** `pool_mix_ratio` — e.g. **50%** living worlds / **50%** legacy mixed pool per eligible generation day (day-seeded).  
4. **Phase 4:** Full 20 in rotation with medium/energy rules in `choose_visual_style`.

Legacy **date-keyed queued flyers** in `morning_flyers.json` still win when unused URL exists for that date.

---

## Production checklist (per concept)

- [ ] Static cover 1080×1350 with six anchors + hierarchy + pride baked in  
- [ ] MP4 loop 5–8s, 1080×1350 feed + 1080×1920 vertical  
- [ ] WP Media Library upload + local PNG source  
- [ ] Never reuse URL (`image_usage` lifetime)  
- [ ] Caption + first-comment links unchanged from morning automation  
- [ ] Email handoff: static cover → `EMAIL-FROM-SOCIAL.md` within 1–2 days  

---

## Approval

**Founder approved** the Living Worlds series concept and rotation plan — **Aug 23, 2026** (America/Chicago). Production may begin concept-by-concept; autopilot picks only after `status: active` + assets exist.
