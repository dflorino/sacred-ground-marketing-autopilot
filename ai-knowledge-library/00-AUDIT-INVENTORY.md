# Sacred Ground AI Knowledge Library — Audit Inventory

Verified against the live website on October 11, 2026. Read-only. No pages, plugins, or bookings were changed.

This is the proposal. Knowledge Cards are not written yet.

## Three layers, plus the voice

| Layer | What it holds | What it never holds |
|---|---|---|
| 0 — Voice Bible | How the guide speaks. Personality, crystal voice, grief voice, humor, honest AI identity. | Invented memories of Deneene. A claim that the visitor is talking to her. |
| 1 — Sacred Ground knowledge | What the place is, how to explore it, modalities, practitioners, Library, Observatory, store. | Today’s events. Open appointment times. Current prices. Stock. |
| 2 — Navigation | Exact public paths, desktop and mobile, with a direct link whenever one exists. | Staff tools. Private practitioner pages. |
| 3 — Live information | A map of which question asks which live system. The guide fetches; it does not memorize. | A copied event list that will be wrong next week. |

Contextual recommendations sit on top of Layers 1 and 3. A visitor who says “I’m stressed and I’ve never tried Reiki” gets a plain explanation, the practitioners who actually offer it, and their booking links. The guide does not invent a match.

## How a visitor actually moves

**Desktop menu:** Calendar → Shop → Observatory → Holistic Center → Monthly → Library → Contact → Languages.

**Mobile menu:** Calendar → Observatory → Shop → Contact → Library → Monthly → Languages.

Mobile Library only shows Guides. Articles, Books, Movies, Music, and Podcasts are on the desktop Library menu and on the Library page itself.

**Footer:** Contact, Accessibility, Working Calendar, Consent Form.

Working Calendar is the staff scheduler. The public guide does not send visitors there.

## What was found

### Homepage — https://shopsacredground.com/

Page 24589. Sections, in order:

1. Hero, “Fall Into Something Magical,” with Event Calendar and Call Now. A walk-through video sits beside the headline.
2. A Holistic Fair banner. On October 11 it still says October 10, 12 to 6, call to book. That line is stale. It stays out of static cards.
3. Upcoming event cards from `[sg_upcoming_events]` (plugin sacred-ground-event-cards-automation). These are live Events Calendar cards, with a hover detail on desktop and a tap detail on a phone.
4. About Sacred Ground. Crystal shop, treasure hunt, and Holistic Center. Curiosity is enough.
5. Photo carousel of the store.
6. Energy and holistic healing, signed “With love and curiosity, Deneene, Founder, Sacred Ground.”
7. Library highlights. This whole block is hidden on screens under 768px.
8. Holistic Center Happenings, including private parties, clearings, and group classes. Call 847-749-3922.
9. Social links and Google reviews.
10. Map and contact: 160 W Campbell St, Arlington Heights, IL 60005. Phone and hours match the Contact page.

Hero “Book Now” and “Book Session” currently go to `/events/`, the public calendar, not a practitioner booker. Appointment questions should be sent to the Holistic Center and the person’s `/book/...` page.

### Two calendars, and they are not the same

| Place | Who it is for | URL |
|---|---|---|
| Events Calendar | Anyone looking at classes, gatherings, and what is coming up | https://shopsacredground.com/events/list/ |
| Your Calendar | A customer who already booked, after they sign in with the same email | https://shopsacredground.com/your-calendar/ |
| A practitioner’s book page | Someone choosing a service, length, date, and time | https://shopsacredground.com/book/{service}/ |
| Working Calendar | Staff only | Not for the public guide |

Browsing an event is reading the Events Calendar card. Registering is completing the booking link on that event, or calling the store. The guide never says a seat is held until a real booking system says so.

Your Calendar tells a signed-in customer: reschedule or cancel as early as possible. Cancellations with less than 24 hours’ notice are not eligible for a refund. Questions: 847-749-3922.

About 300 published events exist. Dates, prices, and open seats stay live. Stable series the guide may describe as patterns, then confirm on the calendar:

- Free Community Meditation, Tuesdays, 7:00–8:00 PM Central.
- Free Community Educational Night, third Wednesday, 7:00–8:30 PM Central.
- Reiki Share, third Sunday, 3:00–5:00 PM Central.

The homepage also says free Angel readings and free community meditations happen each week, with a different guide. Who is leading a given week is live, not a static card.

### Holistic Center and booking

- Holistic Center: https://shopsacredground.com/holistic-center/
- Practitioners and modalities: https://shopsacredground.com/practitioners-modalities-2/
- Book parent: https://shopsacredground.com/book/

29 active practitioner calendars and about 80 active services. A service page is the public booker: pick a time, enter details, pay if that service requires it. Confirmation is the booking system’s own email and text. The guide does not pretend it completed any of that.

Session length and price live on the book page. They are Layer 3.

**Public guide may name these practitioners, matched only to services that are actually published:**

Adie, Amber, Andre Peraza, Andrea, Cheryl, Eve, Gabriella, Janel, Jeniffer, Jill, Karen, Kashia, Kate Kent, Lin Boffeli, Lisa (astrology), Lisa Maria, Lisa Seyring, Lita Keller, Lori, Mary Keiser, Melissa, Mother Lotus, Renee, Richard Popp, Robert MacKay, Rose, Sherry Gurley, Tina Santana.

Deneene has a booking calendar on the site. The public guide does not offer it until she says that calendar is for visitors.

Private `*-11` pages (19 of them) stay out. So do draft pages, old V-22 duplicates, and plugin bug-report pages.

### Library — https://shopsacredground.com/library/

The Library page says articles are written by Deneene: things she is curious about, stories she thought others might enjoy, and topics that needed a little more explanation.

| Shelf | What it is | Count on Oct 11 | URL |
|---|---|---|---|
| Articles | Her essays | 48 published posts | https://shopsacredground.com/library-articles/ |
| Books | Hand-picked titles | 101 | https://shopsacredground.com/library-books/ |
| Movies | Hand-picked films | 99 | https://shopsacredground.com/library-movies/ |
| Podcasts | Hand-picked shows | 89 | https://shopsacredground.com/library-podcasts/ |
| Music | Sacred sounds: artists, albums, playlists | 242 artists, 49 playlists | https://shopsacredground.com/library-sacred-sounds/ |
| Guides | How to use the site and a few practices | 11 | https://shopsacredground.com/library/guides/ |

Book, movie, and podcast subjects:

- Spirituality & Wisdom (77)
- Science & Nature (61)
- UFO & Paranormal (60)
- Wellness & Healing (32)
- Consciousness & Psychology (31)
- Meditation & Mindfulness (27, plus 1 shared with Spirituality)

Visitors filter with `?sg_filter=book|movie|podcast` and browse by those subjects. Music has its own subject tree (meditation, sleep, sound healing, chant, frequencies, traditions, and many more). The guide gets one music navigation card, not a card for every branch.

Guides already on the site:

- A Guide to the Sacred Ground Website
- How to Use the Library
- How to Use the Observatory
- Guide to the Observatory Mineral Bank
- How to Find the Stone That Fits
- A Guide to Numerology
- A Guide to Astrology
- How to Find the Practitioner Who Fits
- A Guide to Tuesday Meditation
- How to Navigate the Holistic Fair
- Smudging: How to Clean and Clear Yourself and a Space

### Observatory — https://shopsacredground.com/sacred-ground-observatory/

Free and public. No membership and no login. The page is only the shortcode `[earth_ether_observatory]`. Welcome, Follow Your Curiosity, Field Notes, Help Shape Tomorrow, and Returning Tomorrow live inside the plugin, under the hero.

Daily pieces: today’s overview, moon, numerology, cosmic weather, a NASA feature, science and spirit, mineral focus, and Beneath the Surface.

Tools a visitor can use on the page: a personal astrology snapshot, a number lookup, a stone lookup (geology kept separate from traditional meaning), and a tarot card lookup. The Death card is not in the Observatory and is not in the guide.

Earth & Ether, the newsletter, is a different place: https://shopsacredground.com/earth-ether/ (Monthly in the menu). Past issues exist for June, July, August, and September 2026, plus a past-issues page.

### Store

Address, phone, email, and hours are published on Contact and on the homepage.

- 160 W Campbell Street, Arlington Heights, IL 60005
- 847-749-3922
- info@shopsacredground.com
- Sunday 11–5, Monday 11–6, Tuesday 11–8, Wednesday 11–6, Thursday 11–7, Friday 11–7, Saturday 10–8

Hours are published facts that can change. The guide treats them as “check Contact if you are about to drive over,” and refreshes the card when the page changes.

The shop is WooCommerce: https://shopsacredground.com/shop/ — 56 published products on October 11. People can buy online and walk in. The guide never invents what is on the shelf.

Categories that currently have products: Zodiac Bags, Wellness and Dis-Ease Bags, Sacred Waters and Sprays, Tumbles, Freeforms, Sage / Palo Santo / Incense, Jewelry, Tarot and Oracle Cards, Ritual Items, Mystery Boxes. Empty old categories are not taught as the shop.

Also public: cart, checkout, my account, accessibility, privacy, terms, refunds, languages, testimonials, contact.

The homepage map embed searches a different street name than 160 W Campbell. The guide uses Campbell Street, which is the address on Contact, the homepage text, and the business listing.

### Kept out of the public guide

Working Calendar. Private `*-11` practitioner pages. Fernando, My Dash, and staff chats. Plugin settings, keys, and payment credentials. Customer records. Deneene’s own booking calendar, until she says otherwise. The Death card. Drafts and one-off invitation pages.

## Proposed cards

About 140 cards in the first library. Not 273 pages, not 300 events, not 211 music branches.

### Voice — 12 cards, after she approves the Voice Bible

Honest identity. Welcome and philosophy. Beginner. Experienced crystal and mineral voice. Metaphysical explorer. Grief and hard days. Humor, and when to leave it alone. Booking voice (clear, short). Words she uses. Words the guide does not use. Adaptive tone. “I’m not sure where to start.”

### Knowledge — about 95 cards

- Home, first visit, philosophy, store and Holistic Center as one place: 6
- Contact, hours, accessibility, policies, languages, social: 6
- Shop and each live product family: 12
- Modalities, in welcoming language, no medical promises: about 20 (Reiki, massage, reflexology, sound, meditation, tarot, oracle, angel communication, mediumship, Akashic Records, astrology, numerology, runes, shamanic practice, cranial sacral, yoga, crystal sessions, pendulums, and the free community series)
- One card per public practitioner: 28, plus “help me choose”
- Library system, six subjects, music, and the 11 guides: 20
- Observatory sections and tools: 12
- Earth & Ether newsletter, separate from the Observatory: 2
- Cornerstone articles she wants quoted in her voice: a short list she names, not all 48 on day one

### Navigation — 15 cards

Find a practitioner. Book an appointment. See what is happening. Open an event. Register. Browse the Library. Find a topic. Explore the Observatory. Look up a stone. Store hours and how to visit. Contact. Shop online. Your bookings, sign-in, cancel and reschedule. Free events. “I’m not sure where to start.”

Each card has the desktop path, the mobile path, and the direct URL.

### Live map — 1 document, not a pile of event cards

| Question | Ask this, live |
|---|---|
| What’s happening tomorrow / this week / is it free | Events Calendar |
| Is there a time with this practitioner | That person’s Fluent book page |
| What does this session cost, and how long is it | That book page, at the moment of the question |
| What have I already booked | Your Calendar, after sign-in |
| Is this product available | WooCommerce |
| Moon, stone, number, tarot meaning on the Observatory | The Observatory page itself |
| Hours, if someone is about to drive over | Contact page |

If the live lookup fails, the guide says it cannot see current availability and gives the page.

## Card shape

JSON is the file the system imports. A matching Markdown file is the one to read.

```
card_id, layer, category, title, purpose,
visitor_questions[], answer, voice_response,
navigation: { desktop, mobile, direct_url },
related_cards[], keywords[],
source, last_verified, update_frequency,
live_source (null when the card is static)
```

`update_frequency` is `stable`, `review_quarterly`, or `live_only`.

## Voice Bible, before any card is written in her tone

Working title: The Deneene Voice Bible — the heart and soul of Sacred Ground’s guide.

Seed already on the site, in her signed homepage letter: curiosity is enough. You do not have to believe anything. Grief is named plainly. The shop and the Holistic Center are one walk. Science and symbol can sit in the same sentence without one being forced to prove the other. That last habit is also how the Observatory explains a stone.

The guide introduces itself as Sacred Ground’s guide. It can say its approach is inspired by Deneene. It does not say it is her, and it does not invent her memories.

Grief: listen first. No timetable. No “everything happens for a reason.” No promise that a session replaces care from a licensed professional. She is not presented as a licensed grief counselor unless she says that is accurate.

Humor stays out of grief, distress, and anything medical.

She reviews the Voice Bible before it governs answers.

## Conflicts to settle before the cards are written

1. Homepage fair banner still says October 10. Leave it out of the guide.
2. Homepage map searches a different street than 160 W Campbell. The guide will say Campbell.
3. Homepage Book Now opens the events list, not a practitioner booker. The guide will send appointment questions to the book pages.
4. Deneene’s booking calendar: public or private?
5. Which page is the real public profile when a person has an older page and a newer one?
6. Inner Circle, Member Shop, and Member Dashboard: may the guide mention them, or are they for members only?
7. Which of the 48 articles should become their own cards in the first library?
8. Death card stays banned everywhere in this guide. Confirm.
9. The guide never claims a booking, registration, payment, or purchase is done.
