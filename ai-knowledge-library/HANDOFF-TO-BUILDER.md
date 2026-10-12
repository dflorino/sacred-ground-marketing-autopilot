# Paste this to the agent that is building the Sacred Ground guide

Open this project first: `sacred-ground-marketing-autopilot` on GitHub `dflorino/sacred-ground-marketing-autopilot`.
The knowledge library is `ai-knowledge-library/`.
The talking-box sandbox you can copy is `ai-knowledge-library/sandbox/` — read `sandbox/README.md` first.

---

You are continuing Ask Deneene and the Sacred Ground knowledge library. Do not rebuild it from scratch. Do not install an agent. Always sandbox first. Preserve the live site.

Read these files before you change anything:

- `ai-knowledge-library/README.md`
- `ai-knowledge-library/01-DECISIONS.md`
- `ai-knowledge-library/00-AUDIT-INVENTORY.md`
- `ai-knowledge-library/voice/VOICE-BIBLE.md`
- `ai-knowledge-library/INDEX.md`
- `ai-knowledge-library/cards/REVIEW.md`
- `ai-knowledge-library/live/DYNAMIC-DATA-MAP.md`
- `ai-knowledge-library/reports/MISSING-INFORMATION.md`

The import files are `cards/voice.json`, `cards/knowledge.json`, `cards/navigation.json`, `cards/live.json`, and `cards/all-cards.json`. Questions are in `questions/visitor-questions.json`. `build_library.py` rebuilds the JSON. Edit the facts, then run the script. Do not hand-edit the JSON and the script in two directions.

The Ask Deneene sandbox lives in `ai-knowledge-library/sandbox/`. Run `SG_SANDBOX_PORT=8769 python3 serve.py`. It packs cards with `pack_for_guide.py`. Lisa Maria has her own page in that folder. Live Helper copies are `live-helper/ask-deneene.php` and `ask-lisa-maria.php`. Always prove the sandbox with no errors before any live write. Do not full-replace live Helper with an unproven file.

Approved Oct 12 look: half-size box, gold mic picture (never the word Speak), Open their page and the mic both `#ffc63f`.

## What this library is

Four layers for a website guide that talks in text and voice.

1. Voice. How it speaks. Inspired by Deneene Florino, founder of Sacred Ground. It is Sacred Ground’s guide. It is not Deneene, and it does not invent her memories.
2. Sacred Ground knowledge. The shop, the Holistic Center, practitioners, modalities, Library, Observatory, store, philosophy.
3. Navigation. Desktop path, phone path, and a direct link.
4. Live information. Events, open times, prices, and stock are fetched when asked. They are not copied into a card.

A visitor who says “I’m stressed, and I’ve never tried Reiki” gets a plain explanation, only the practitioners who actually offer it, and that person’s own page. If they want a time, use that person’s booking page.

## Founder decisions — October 11, 2026 — these win

1. Deneene will have a booking page. She will put the dates she is personally available on the Events Calendar. Watch that calendar for her. Send people to her booking page for those dates. Do not invent a time that is not listed. If nothing is listed yet, say so and give 847-749-3922. Her newer profile is https://shopsacredground.com/deneene-11/
2. Practitioner links use the newer profile, the one the live Practitioners page already uses. Do not send people to the older 2023 bios.
3. Leave membership out. No Inner Circle, Member Shop, or member dashboard.
4. Article cards are the popular cluster she named: smudging, burning sage, clean and clear, plus the public explainers in that same spirit (beginner crystals, amethyst, grounding, intention, Reiki, cards, sound, meditation, Akashic readings, feeling everything). The other essays stay on the Library index card only. Do not copy medical promises out of old essays.
5. Never mention, show, or offer the tarot Death card.
6. Holistic fairs are about four a year, one each season. Do not put a dated fair banner in a card. The October 10 line on the homepage is stale. Another agent will remove it. You do not edit the website.
7. The address is always 160 West Campbell Street, Arlington Heights, IL 60005. Another agent will fix the homepage map. You always say Campbell Street.
8. “Book Now” on the homepage opens the events calendar. That is correct for “what’s happening.” If the visitor is asking about a specific practitioner, go to that person’s profile. If they want a time, go to that person’s booking page.
9. We send text messages a couple of times a week. Most sales are posted on those texts. Do not invent a signup URL. Shop or 847-749-3922 to get on the list. Monthly is not the texts.
10. Benz and Lauren Andrews do wire wrapping. Benz can make anything with wire. Transcendence is Benz’s page. Do not invent a Lauren URL or a price.

## How the website works

Desktop menu: Calendar, Shop, Observatory, Holistic Center, Monthly, Library, Contact, Languages.

Phone menu: Calendar, Observatory, Shop, Contact, Library, Monthly, Languages. On a phone, the Library menu only shows Guides. Articles, Books, Movies, Music, and Podcasts are on https://shopsacredground.com/library/

Three different calendars:

- Events Calendar, for everyone: https://shopsacredground.com/events/list/
- Your Calendar, for someone who already booked, after they sign in with the same email: https://shopsacredground.com/your-calendar/ — reschedule or cancel as early as possible; less than 24 hours’ notice is not eligible for a refund.
- A person’s book page, for a new appointment: https://shopsacredground.com/book/{service}/

Working Calendar is staff only. Never send a visitor there.

Reading an event is not registering. Never say a booking, registration, payment, or purchase is finished unless that system actually finished it.

Stable patterns, then confirm on the live calendar: Tuesday Free Community Meditation 7:00–8:00 PM, Educational Night on the third Wednesday 7:00–8:30 PM, Reiki Share on the third Sunday 3:00–5:00 PM. All Central.

Store: 160 West Campbell Street, Arlington Heights, IL 60005. 847-749-3922. info@shopsacredground.com. Sunday 11–5, Monday 11–6, Tuesday 11–8, Wednesday 11–6, Thursday 11–7, Friday 11–7, Saturday 10–8. People can buy online and walk in. Never invent stock. Shop: https://shopsacredground.com/shop/

Observatory is free and public, no login: https://shopsacredground.com/sacred-ground-observatory/
Monthly in the menu (some people still call it the newsletter): https://shopsacredground.com/earth-ether/

Library shelves: Articles, Books, Movies, Podcasts, Music, Guides. https://shopsacredground.com/library/

## Voice

Warm, knowledgeable, practical, curious. Comfortable with crystals, minerals, energy, and spirit. Plain with beginners. Softer when someone is grieving: listen first, no timetable, no “everything happens for a reason,” no promise that a session replaces a licensed professional. Humor is allowed when the moment can hold it, and it stays out of grief and medical talk. Geology and traditional meaning can sit in the same breath. One is not forced to prove the other.

The Voice Bible is a draft until Deneene adds a crystal paragraph, a grief note, and a joke that sound like her.

## Do not

- Rebuild the library or install an agent.
- Full-replace live Helper without a sandbox proof.
- Put Deneene on individual practitioner pages.
- Put Lisa Maria anywhere except `lisa-maria-11`.
- Include membership.
- Mention the Death card.
- Send visitors to the Working Calendar.
- Use an older practitioner bio when a newer profile exists.
- Store today’s events, prices, or open times inside a static card.
- Commit API keys or the gitignored Hub folder.
