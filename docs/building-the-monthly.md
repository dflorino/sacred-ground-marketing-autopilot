# Build & Publish "The Monthly" (Earth & Ether)

Sacred Ground's monthly newsletter: one self-contained HTML doc (inline <style>,
hosted image URLs) published to WordPress, written through the browser using
push-to-browser.md.

## Pages (stable IDs)
- /earth-ether/  = page 22780 — permanent current-issue URL (slug never changes; overwritten monthly). "The Monthly" nav points here.
- /newsletters/  = page 23746 — archive grid (newest first).
- /earth-ether-<month>-2026/  — dated archive page, created each month for the outgoing issue.
- Observatory: /sacred-ground-observatory/ (22806).

## Sections (in order)
Hero -> Masthead (Month Year / Vol I / No. N) -> Welcome -> Deneene's Corner ->
Galactic Adventures -> Practitioner of the Month (optional) -> New Practitioners
(alphabetical, photo each) -> Artisan of the Month -> New at Sacred Ground (workshops)
-> From the Library (5 picks) -> Practice This Month (ritual) -> Community Calendar
(real dates) -> Past Issues.

## Brand rules (hard)
- "crystal shop, rock shop, and holistic center" — never "metaphysical store".
- Never "gifts" for intuitive/psychic abilities (literal presents are fine).
- Founder signs "Deneene" (no surname). No emojis in body copy.
- Practitioners by first name; disambiguate duplicates (Mary R./Mary G.).
- No "pagan" as a label — use "earth-honoring traditions" / "Wheel of the Year".

## Build
- Start from last month's HTML; keep the <style> block verbatim. Change masthead + hero if themed.
- Placeholders while waiting: <div class="todo"> and <div class="imgslot">.
  A finished issue has ZERO of both (grep before publishing).
- Images: resize to display size, upload to /wp/v2/media, verify the URL loads before use.
- Calendar: real dates from The Events Calendar REST:
  /wp-json/tribe/events/v1/events?start_date=YYYY-MM-01%2000:00:00&end_date=YYYY-MM-28%2023:59:59&per_page=50&status=publish

## Publish ritual (in a WP-admin tab)
1. Make/upload the archive cover (themed art, or reuse the Earth & Ether banner).
2. Archive outgoing: GET /wp/v2/pages/22780?context=edit -> content.raw ->
   POST /wp/v2/pages to create earth-ether-<prevmonth>-2026 (publish). Only if slug is new + content matches the month.
3. Publish new issue into 22780 via the base64-chunk method (verify length, decode, POST;
   wrap content in <!-- wp:html --> ... <!-- /wp:html -->).
4. Rebuild archive (23746): regenerate <div class="na-grid">...</div> — new issue first with a
   "Current Issue" ribbon, then prior months (cover, Month/Year, Vol/No, 1-line desc, link).
5. Purge CDN (admin bar -> CDN Cache -> Purge Everything).
Then verify live: fetch /earth-ether/, /newsletters/, new archive page with ?cb= and check.

## Rebuild / recover
- Canonical source = the saved HTML file per issue. Re-publish = re-run step 3 from it.
- Corrupted live page (dup section / mangled tag) = a chunking error. Re-inject cleanly from source.
- Small fix = GET content.raw, string-replace, POST back; keep the source file in sync.
- Broken image = re-upload, confirm it loads, swap src (live + source).

## Stable assets
- E&E hero/cover: .../uploads/606b3ba0-6c38-429a-b90f-8a4fac85595c.png
- Deneene portrait: .../uploads/b2a9f4c7-8681-4b06-a98e-4cbc7b7b9115.png (crop: bg-size 220%, bg-pos 90% 20%)
- Library banner: .../uploads/737867a4-07dd-42d7-a610-7e6344dbd016.png
- Community photo: .../uploads/FCDAF320-DF3D-4DF4-BD70-9D829928F937.png
