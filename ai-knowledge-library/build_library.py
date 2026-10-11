#!/usr/bin/env python3
"""Build the Sacred Ground knowledge-card library from verified Oct 11, 2026 facts."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERIFIED = "2026-10-11"
BASE = "https://shopsacredground.com"

cards = []


def add(**kwargs):
    card = {
        "layer": "knowledge",
        "status": "draft_for_founder_review",
        "last_verified": VERIFIED,
        "update_frequency": "stable",
        "live_source": None,
        "related_cards": [],
        "keywords": [],
    }
    card.update(kwargs)
    cards.append(card)
    return card["card_id"]


def nav(desktop, mobile, url):
    return {"desktop": desktop, "mobile": mobile, "direct_url": url}


def spoken_name(name):
    keep = {
        "Mother Lotus": "Mother Lotus",
        "Lisa Maria": "Lisa Maria",
        "Lisa Seyring": "Lisa Seyring",
        "Andre Peraza": "Andre",
        "Mary Keiser": "Mary",
        "Richard Popp": "Richard",
        "Robert MacKay": "Robert",
        "Kate Kent": "Kate",
        "Lita Keller": "Lita",
        "Tina Santana": "Tina",
        "Sherry Gurley": "Sherry",
    }
    return keep.get(name, name.split()[0])


def join_names(people):
    if not people:
        return ""
    if len(people) == 1:
        return people[0]
    if len(people) == 2:
        return f"{people[0]} and {people[1]}"
    return ", ".join(people[:-1]) + f", and {people[-1]}"


def speak_nav(path):
    return {
        "/": "the homepage",
        "/events/list/": "Calendar in the menu",
        "/your-calendar/": "Calendar, then Your Calendar",
        "/library/": "Library in the menu",
        "/sacred-ground-observatory/": "Observatory in the menu",
        "/shop/": "Shop in the menu",
        "/contact/": "Contact in the menu",
        "/earth-ether/": "Monthly in the menu",
        "/practitioners-modalities-2/": "Holistic Center, then Practitioners",
        "/about/": "Contact, then About",
    }.get(path, "Holistic Center, then Practitioners")


def modality_voice(answer, people):
    first = answer.split(".")[0].strip()
    if not first.endswith("."):
        first += "."
    if not people:
        return first + " If you're not sure which, that's Holistic Center, then Practitioners, or you can call 847-749-3922."
    if first.lower().startswith(people[0].lower()):
        return first + " You'll find them under Holistic Center, then Practitioners."
    return first + f" Here that's {join_names(people)}. You'll find them under Holistic Center, then Practitioners."


# --- Voice -----------------------------------------------------------------

add(
    card_id="SG-VOICE-IDENTITY",
    layer="voice",
    category="Voice",
    title="Honest identity",
    purpose="Keep the guide from pretending to be Deneene or from claiming it completed a booking.",
    visitor_questions=[
        "Am I talking to Deneene?",
        "Are you a real person?",
        "Can you book this for me?",
        "Did you just reserve that?",
        "Who am I talking to?",
    ],
    answer=(
        "I'm Sacred Ground's guide. The way I explain things is inspired by Deneene, who founded this place, "
        "and by the philosophy she built it on. I am not Deneene, and I don't invent her memories. "
        "I can walk you to the right place on the menu, the right practitioner, and the right way to book. "
        "I have not booked, charged, or registered anything unless a booking page or the shop checkout has actually finished it."
    ),
    voice_response=(
        "I'm Sacred Ground's guide, and the way I talk is inspired by Deneene. "
        "I can point you to the right person, and you'll find them on our nav. I can't hold the session for her, "
        "and I won't tell you something is booked until the booking page says it is."
    ),
    navigation=nav("Any page.", "Any page.", BASE + "/"),
    keywords=["are you deneene", "real person", "chatbot", "did you book it"],
    source="Founder decision, October 11, 2026. Voice Bible.",
)

add(
    card_id="SG-VOICE-GRIEF",
    layer="voice",
    category="Voice",
    title="When someone is grieving",
    purpose="Shift tone when a visitor is in grief, loss, or a hard emotional place.",
    visitor_questions=[
        "I just lost my mom",
        "I'm grieving",
        "I don't know how to do this",
        "Can a reading fix my grief?",
        "I feel so alone",
        "My pet died",
    ],
    answer=(
        "Grief is personal. There isn't a timetable, and there isn't a correct way to do it. "
        "You don't have to be positive, and you don't have to find a lesson in it. "
        "Sacred Ground can be a place to sit, breathe, and not explain yourself. "
        "Deneene's published profile lists her as a spiritual guide, grief counselor, and meditation teacher, "
        "and the site says she studied with Elisabeth Kübler-Ross. That is companionship and spiritual support, "
        "not a promise that a session replaces a doctor or a licensed clinician, and not a claim about a license beyond what she has published. "
        "If you want her, look on Calendar for the days she is in. She puts her own dates there. Do not invent a time. "
        "If nothing is listed yet, say so and offer 847-749-3922. "
        "If you are in immediate danger, call 911. "
        "If you are feeling suicidal or in a crisis, please call or text 988. "
        "A dedicated professional can help you now. Do not lecture."
    ),
    voice_response=(
        "I'm glad you said it out loud. Grief doesn't run on a schedule, and you don't owe anyone a silver lining. "
        "If you want time with Deneene, look on Calendar for the days she is in. "
        "If you are feeling suicidal or in a crisis, please call or text 988. A dedicated professional can help you now."
    ),
    navigation=nav(
        "Calendar in the menu, for Deneene's dates.",
        "Calendar in the phone menu.",
        BASE + "/events/list/",
    ),
    related_cards=["SG-PRAC-DENEENE", "SG-NAV-EVENTS"],
    keywords=["grief", "loss", "died", "mourning", "sad", "lonely", "Kübler-Ross", "988", "crisis"],
    source="Homepage letter. Practitioners page, Deneene. Founder voice brief, October 11, 2026.",
    update_frequency="stable",
)

add(
    card_id="SG-VOICE-MEDICAL",
    layer="voice",
    category="Voice",
    title="We are not doctors",
    purpose="Refuse medical advice. Sacred Ground is not a clinic.",
    visitor_questions=[
        "Can you tell me what's wrong with me?",
        "Is this medical advice?",
        "Should I stop my medication?",
        "Do you diagnose?",
        "Can a crystal replace my doctor?",
        "Is Reiki a medical treatment?",
    ],
    answer=(
        "Sacred Ground is a crystal shop and a Holistic Center. We are not doctors, and we do not give medical advice. "
        "We do not diagnose, prescribe, or tell anyone to stop or start a treatment. "
        "A session, a stone, a card, or a conversation here is not medicine and does not replace a doctor. "
        "If they need a clinician, say so. If they want time with someone here, that is Calendar. "
        "The shop phone is 847-749-3922. Do not invent a medical claim."
    ),
    voice_response=(
        "We are not doctors, and we do not give medical advice. "
        "If you want time with someone here, that's Calendar."
    ),
    navigation=nav("Calendar in the menu.", "Calendar in the phone menu.", BASE + "/events/list/"),
    related_cards=["SG-VOICE-GRIEF", "SG-NAV-EVENTS"],
    keywords=["doctor", "medical", "medical advice", "diagnose", "prescription", "medicine", "not a doctor"],
    source="Founder, October 11, 2026.",
)

add(
    card_id="SG-VOICE-CRYSTAL",
    layer="voice",
    category="Voice",
    title="How to talk about a stone",
    purpose="Separate mineral fact from traditional meaning, in Deneene's crystal voice.",
    visitor_questions=[
        "Tell me about amethyst",
        "Is moldavite real?",
        "What stone should I get?",
        "What's the difference between citrine and heat-treated amethyst?",
        "Do crystals actually work?",
    ],
    answer=(
        "Talk about the mineral first, then the tradition, and label the tradition as tradition. "
        "Amethyst is a violet variety of quartz. The color comes from iron and natural irradiation. "
        "The old Greek name means not drunken. People have long associated it with a clear head and with intuition. "
        "Neither sentence has to cancel the other. Do not promise a stone will treat anxiety, depression, or any illness. "
        "If someone wants the stone that fits, send them to the guide How to Find the Stone That Fits, and invite them to come hold them in the shop. "
        "Stock is live. Do not invent what is on the shelf."
    ),
    voice_response=(
        "Amethyst is quartz that came out purple, from iron and a little natural radiation. "
        "People have also loved it for a clear head and for intuition. Both of those can be true without one proving the other. "
        "If you want to find yours, come hold them. The shop is at 160 W Campbell Street in Arlington Heights."
    ),
    navigation=nav(
        "Library, then Guides, then How to Find the Stone That Fits. Or Shop.",
        "Library, then Guides. Shop is in the phone menu.",
        BASE + "/library/guides/find-your-stone/",
    ),
    related_cards=["SG-ART-AMETHYST", "SG-ART-BEGINNER-CRYSTALS", "SG-KNOW-SHOP"],
    keywords=["amethyst", "crystal", "mineral", "stone", "geology", "metaphysical"],
    source="Article: Why Amethyst is Called Swiss Army Knife of Crystals. Voice Bible. Observatory mineral method.",
)

# --- Place -----------------------------------------------------------------

add(
    card_id="SG-KNOW-HOME",
    category="Homepage",
    title="Homepage",
    purpose="Explain what a visitor sees first and where the buttons go.",
    visitor_questions=[
        "What's on the homepage?",
        "Where do I start?",
        "What is Sacred Ground?",
        "I'm not sure where to start",
        "What does Book Now do?",
    ],
    answer=(
        "The homepage is the front door. The line across the top is Fall Into Something Magical, with a short walk through the shop. "
        "Event Calendar opens the public events list. Call Now opens Contact. "
        "Under that are live upcoming-event cards. Then the story of the place: part crystal shop, part treasure hunt, part Holistic Center. "
        "Deneene's letter is there too. Curiosity is enough, and you do not have to believe anything. "
        "Book Now and Book Session on the homepage open the events calendar, not one person's book page. "
        "If you already know who you want, go to that person's profile. "
        "The Library block on the homepage is hidden on a phone. The Library itself is still in the menu."
    ),
    voice_response=(
        "Start at the homepage if you want the feel of the place. The event cards are what's coming up. "
        "Book Now there opens the calendar. If you want a particular person, I'll take you to their page instead."
    ),
    navigation=nav(
        "The logo, or the site root.",
        "The logo. The phone menu does not repeat every homepage section.",
        BASE + "/",
    ),
    related_cards=["SG-NAV-EVENTS", "SG-NAV-PRACTITIONER", "SG-KNOW-ABOUT"],
    keywords=["homepage", "start", "front page", "book now"],
    source="Homepage page 24589, read October 11, 2026. Founder decision 8.",
)

add(
    card_id="SG-KNOW-ABOUT",
    category="About",
    title="What Sacred Ground is",
    purpose="Tell the story of the shop and the Holistic Center as one place.",
    visitor_questions=[
        "What is Sacred Ground?",
        "Tell me about this place",
        "What's the difference between the shop and the holistic center?",
        "Do I need an appointment to come in?",
        "What should I expect the first time?",
        "Who founded Sacred Ground?",
        "Do I have to be spiritual to come in?",
    ],
    answer=(
        "Sacred Ground is a crystal shop and a Holistic Center in downtown Arlington Heights, and they are the same walk. "
        "Deneene founded it. She hand-selects the crystals, from everyday tumbles to collector specimens. "
        "Past the shop is the Holistic Center: Reiki, massage, reflexology, sound, meditation, tarot, astrology, mediumship, classes, and community gatherings. "
        "You can come in without an appointment to wander, ask questions, and shop. Sessions and many classes are booked. "
        "You do not have to follow a religion or already know the words. The homepage says it plainly: curiosity is enough."
    ),
    voice_response=(
        "It's a crystal shop and a holistic center on the same walk, in downtown Arlington Heights. Deneene founded it. "
        "You can wander in without an appointment. If you want a session with someone, we book that. You don't have to believe anything to come in."
    ),
    navigation=nav(
        "Contact menu, then About. The story is also on the homepage.",
        "Contact, then About.",
        BASE + "/about/",
    ),
    related_cards=["SG-KNOW-VISIT", "SG-KNOW-HOME", "SG-NAV-PRACTITIONER"],
    keywords=["about", "founder", "first visit", "what is sacred ground", "appointment to shop"],
    source="Homepage about section. About page 17335. Contact page.",
)

add(
    card_id="SG-KNOW-VISIT",
    category="Store",
    title="Visit the store",
    purpose="Give the address, phone, hours, and the fact that walk-ins are welcome.",
    visitor_questions=[
        "Where are you?",
        "What are your hours?",
        "Can I come in without an appointment?",
        "What's the phone number?",
        "Are you in Arlington Heights?",
        "What's the address?",
        "Can I just browse?",
    ],
    answer=(
        "Sacred Ground is at 160 W Campbell Street, Arlington Heights, Illinois 60005. "
        "Call 847-749-3922 or email info@shopsacredground.com. "
        "Published hours: Sunday 11 to 5, Monday 11 to 6, Tuesday 11 to 8, Wednesday 11 to 6, Thursday 11 to 7, Friday 11 to 7, Saturday 10 to 8. "
        "Hours can change. If you are about to drive over, the Contact page is the check. "
        "You can walk in and browse with no appointment. A session with a practitioner is booked on that person's page. "
        "The map should always be read as 160 W Campbell Street. An older map search used a different street. Campbell Street is the address."
    ),
    voice_response=(
        "We're at 160 W Campbell Street in Arlington Heights. The phone is 847-749-3922. "
        "You can walk in and look around. Hours are on the contact page if you're heading over, because those can change."
    ),
    navigation=nav(
        "Contact in the menu. Hours are also at the bottom of the homepage.",
        "Contact in the phone menu.",
        BASE + "/contact/",
    ),
    related_cards=["SG-KNOW-SHOP", "SG-NAV-HOURS", "SG-KNOW-ABOUT"],
    keywords=["address", "hours", "phone", "campbell", "arlington heights", "walk in", "directions"],
    source="Contact page 1007 and homepage contact block, October 11, 2026. Founder decision 7.",
    update_frequency="review_quarterly",
    live_source="Contact page if the visitor is about to visit.",
)

add(
    card_id="SG-KNOW-SHOP",
    category="Shop",
    title="The shop, in person and online",
    purpose="Explain what the retail shop sells and that inventory is live.",
    visitor_questions=[
        "Can I buy crystals online?",
        "What do you sell?",
        "Do you have jewelry?",
        "Do you sell sage?",
        "Can I shop in the store?",
        "Do you have books?",
        "What if something is out of stock?",
    ],
    answer=(
        "You can shop in the store and on the website. The online shop is ordinary checkout: cart, then secure checkout. "
        "On October 11 the published shelves with products were zodiac bags, wellness bags, sacred waters and sprays, tumbles, freeforms, "
        "sage, palo santo and incense, jewelry, tarot and oracle decks, ritual items, and mystery boxes. "
        "Crystals and minerals are the heart of the physical shop, including pieces that may not all be listed online. "
        "This guide does not know what is on the shelf today. The product page does. If it is not listed, call the shop."
    ),
    voice_response=(
        "Yes, you can buy online, and yes, you can come in. Crystals, jewelry, sage, decks, and gifts are the idea. "
        "I won't guess what's in stock. The shop page will show you, or call 847-749-3922."
    ),
    navigation=nav("Shop in the top menu.", "Shop in the phone menu.", BASE + "/shop/"),
    related_cards=["SG-KNOW-VISIT", "SG-ART-SMUDGING", "SG-NAV-SHOP"],
    keywords=["shop", "buy", "crystals", "jewelry", "sage", "online", "woocommerce", "gifts"],
    source="WooCommerce categories with products, October 11, 2026. Homepage shop story.",
    update_frequency="live_only",
    live_source="WooCommerce shop and product pages.",
)

add(
    card_id="SG-KNOW-FAIR",
    category="Events",
    title="Holistic fairs",
    purpose="Describe the seasonal fairs without quoting a stale date.",
    visitor_questions=[
        "When is the holistic fair?",
        "Do you have a psychic fair?",
        "How many fairs do you have?",
        "Can I have a table at the fair?",
        "What happens at the fair?",
    ],
    answer=(
        "Sacred Ground holds about four holistic fairs a year, one for each season. "
        "The date, the hours, and how to reserve a reading or a table change with each fair. "
        "Look at the events calendar for the next one, read How to Navigate the Holistic Fair, and call 847-749-3922. "
        "Do not quote an old homepage banner. The calendar is the date."
    ),
    voice_response=(
        "We do about four fairs a year, one a season. I don't want to give you an old date. "
        "The calendar has the next one, and the phone is 847-749-3922 if you want a table or a reading."
    ),
    navigation=nav(
        "Calendar, then look for the fair. Library, Guides, How to Navigate the Holistic Fair.",
        "Calendar in the phone menu. The fair guide is under Library, Guides.",
        BASE + "/library/guides/holistic-fair/",
    ),
    related_cards=["SG-NAV-EVENTS", "SG-LIVE-EVENTS"],
    keywords=["fair", "holistic fair", "psychic fair", "vendor", "season"],
    source="Founder, October 11, 2026. Guide page holistic-fair. Homepage banner excluded as stale.",
    update_frequency="live_only",
    live_source="Events Calendar for the next fair date.",
)

add(
    card_id="SG-KNOW-COMMUNITY",
    category="Events",
    title="Free community gatherings",
    purpose="Describe the standing free series, and send dates to the live calendar.",
    visitor_questions=[
        "Are there any free events?",
        "When is meditation?",
        "What is educational night?",
        "When is reiki share?",
        "Do you have free angel readings?",
        "What's happening this week?",
    ],
    answer=(
        "Some gatherings are free and repeat. Free Community Meditation is Tuesday nights, 7:00 to 8:00 PM Central. "
        "Free Community Educational Night is the third Wednesday, 7:00 to 8:30 PM Central. "
        "Reiki Share is the third Sunday, 3:00 to 5:00 PM Central. "
        "The homepage also says free angel readings and free community meditations happen through the week, with a different guide. "
        "Who is leading a given week, and whether a date is still on the calendar, comes from the events list. "
        "Free does not mean you have to book a private session. Showing up for a community event is not the same as reserving a private appointment."
    ),
    voice_response=(
        "Yes. Tuesday night meditation is free, 7 to 8. Educational Night is the third Wednesday, 7 to 8:30. "
        "Reiki Share is the third Sunday, 3 to 5. All of that is Central time. "
        "If you want this week's actual list, the calendar is the place to look."
    ),
    navigation=nav("Calendar in the top menu.", "Calendar in the phone menu.", BASE + "/events/list/"),
    related_cards=["SG-NAV-EVENTS", "SG-LIVE-EVENTS", "SG-MOD-MEDITATION"],
    keywords=["free", "meditation tuesday", "educational night", "reiki share", "angel readings"],
    source="Founder locks for meditation, educational night, and reiki share. Homepage community paragraph.",
    update_frequency="live_only",
    live_source="The Events Calendar.",
)

add(
    card_id="SG-RULE-NO-DEATH",
    category="Rules",
    title="A card we do not use",
    purpose="If a visitor asks for a card Sacred Ground does not display, redirect without naming it.",
    visitor_questions=[
        "What about that one tarot card you don't use?",
        "Can I see every card?",
        "Is every card in the Observatory tool?",
    ],
    answer=(
        "Some cards are not part of what Sacred Ground displays. "
        "Do not name a card that is not on the public Observatory tool. "
        "Say it is not a card we use here, and offer another card or the Observatory tarot tool."
    ),
    voice_response="That's not a card we use here. I can help you with another card, or the Observatory tarot tool.",
    navigation=nav("Observatory, then the tarot tool.", "Observatory in the phone menu.", BASE + "/sacred-ground-observatory/"),
    keywords=["death card", "tarot death", "major 13"],
    source="Founder, September 12, 2026, confirmed October 11, 2026. Spoken lines never name it.",
)

# --- Library and Observatory ------------------------------------------------

add(
    card_id="SG-KNOW-LIBRARY",
    category="Library",
    title="The Sacred Ground Library",
    purpose="Explain the shelves and how to move among them.",
    visitor_questions=[
        "What's the Library?",
        "Where are the articles?",
        "Do you have book recommendations?",
        "Where is the music?",
        "How do I get back to the Library?",
        "Who writes the articles?",
        "Do the playlists play here?",
        "Can I listen on Spotify?",
    ],
    answer=(
        "The Library is a hand-picked collection: articles, books, movies, podcasts, music, and short guides. "
        "The Library page says the articles are written by Deneene, about things she is curious about. "
        "Subjects for books, movies, and podcasts are Spirituality and Wisdom, Science and Nature, UFO and Paranormal, "
        "Wellness and Healing, Consciousness and Psychology, and Meditation and Mindfulness. "
        "Music is its own room, Sacred Sounds, with artists and playlists for meditation, sleep, chant, sound healing, and more. "
        "The playlists do not play on this website. Copy what you like and paste it into Spotify, Apple Music, or wherever you stream. "
        "Every shelf links back. The Library home is the way back to all six doors. "
        "On a phone, the menu under Library only shows Guides. Articles, books, movies, music, and podcasts are buttons on the Library page itself."
    ),
    voice_response=(
        "The Library is Deneene's collection of articles, books, movies, podcasts, music, and how-to guides. "
        "On a phone, open Library and you'll see all six. The little menu only shows Guides. "
        "The playlists don't play here. Copy what you like and paste it into Spotify, Apple Music, or wherever you stream."
    ),
    navigation=nav(
        "Library in the top menu, then Articles, Books, Movies, Music, Podcasts, or Guides.",
        "Library, then the buttons on the page. Guides is also in the submenu.",
        BASE + "/library/",
    ),
    related_cards=["SG-ART-SMUDGING", "SG-KNOW-OBSERVATORY", "SG-NAV-LIBRARY"],
    keywords=["library", "articles", "books", "podcasts", "movies", "sacred sounds", "playlist", "spotify", "apple music"],
    source="Library page 24588. Counts on October 11, 2026: 48 articles, 101 books, 99 movies, 89 podcasts, 242 artists, 49 playlists, 11 guides. Founder Oct 11: playlists do not play on the site.",
)

add(
    card_id="SG-KNOW-PLAYLISTS",
    category="Library",
    title="Music playlists",
    purpose="Say the playlists do not play on the website. People copy them to their own streamer.",
    visitor_questions=[
        "Do the playlists play on the website?",
        "How do I listen to the music?",
        "Can I put this on Spotify?",
        "Can I use Apple Music?",
        "Where do I play the Sacred Sounds playlists?",
        "The music won't play",
    ],
    answer=(
        "Sacred Sounds is under Library, then Music. Artists and playlists are there for meditation, sleep, chant, sound healing, and more. "
        "They do not play on this website. Copy the selection and paste it into Spotify, Apple Music, or wherever else you stream. "
        "Do not read a website address. Do not say the site will start the song."
    ),
    voice_response=(
        "Those playlists don't play here. Copy what you like and paste it into Spotify, Apple Music, or wherever else you stream. "
        "That's under Library, then Music."
    ),
    navigation=nav(
        "Library in the top menu, then Music.",
        "Library, then Music on the page. The phone submenu only shows Guides.",
        BASE + "/library/",
    ),
    related_cards=["SG-KNOW-LIBRARY", "SG-NAV-LIBRARY"],
    keywords=["playlist", "playlists", "spotify", "apple music", "stream", "sacred sounds", "music"],
    source="Founder, October 11, 2026. Library Sacred Sounds.",
)

add(
    card_id="SG-KNOW-OBSERVATORY",
    category="Observatory",
    title="The Sacred Ground Observatory",
    purpose="Explain the free daily Observatory and its tools.",
    visitor_questions=[
        "What's the Observatory?",
        "Where do I find information about the moon?",
        "Can I look up a stone?",
        "Is the Observatory free?",
        "What's the difference between the Observatory and Monthly?",
        "What's the difference between the Observatory and the newsletter?",
        "Can I look up my number?",
        "Where is the tarot tool?",
    ],
    answer=(
        "The Observatory is a free public daily page. No membership and no login. "
        "It holds today's moon, a numerology note, cosmic weather, a NASA feature, a science-and-spirit note, a mineral focus, and Beneath the Surface. "
        "Tools on the page: an astrology snapshot, a number lookup, a stone lookup, and a tarot lookup. "
        "A stone note keeps the geology separate from the traditional meaning. "
        "Monthly, in the menu, is a different place from the Observatory."
    ),
    voice_response=(
        "The Observatory is free, and you don't need an account. Moon, numbers, a stone lookup, a NASA note, and a tarot tool live there. "
        "Monthly is a different place. It's in the menu as Monthly."
    ),
    navigation=nav(
        "Observatory in the top menu.",
        "Observatory in the phone menu.",
        BASE + "/sacred-ground-observatory/",
    ),
    related_cards=["SG-RULE-NO-DEATH", "SG-KNOW-LIBRARY", "SG-NAV-OBSERVATORY"],
    keywords=["observatory", "moon", "nasa", "mineral bank", "numerology", "earth and ether"],
    source="Observatory plugin README. Page 22806 is only the shortcode. Tools in class-tools.php. Founder decision 5.",
)

# --- Modalities -------------------------------------------------------------

MODS = [
    ("SG-MOD-REIKI", "Reiki", "A quiet session. The word joins rei, universal, and ki, life energy. You stay clothed. The practitioner uses a light touch or hands just off the body. People come for rest, a heavy week, or simple curiosity. You do not have to believe a theory for it to be a peaceful hour. It is not medicine and it does not replace a doctor.",
     ["Eve", "Mary", "Rose", "Karen", "Renee", "Andrea"], ["reiki", "energy healing", "hands on"]),
    ("SG-MOD-MASSAGE", "Massage", "Amber offers customized therapeutic massage. It is bodywork, for tension and for an hour that belongs to your body. Come as you are. The booking page shows the length and the price that day.",
     ["Amber"], ["massage", "bodywork", "amber"]),
    ("SG-MOD-REFLEX", "Reflexology", "Cheryl works specific points on the feet that traditional reflexology maps to the rest of the body. Shoes off, a chair or a table, and a session aimed at rest. She also teaches yoga and stretchology. The practitioners page says to call her, and booking pages are published too.",
     ["Cheryl"], ["reflexology", "feet", "stretchology"]),
    ("SG-MOD-SOUND", "Sound healing", "Sound baths, bowls, gongs, and voice. You mostly listen and feel. Andre, Kate, and Karen are the names on the practitioners page. Tina also has a published Reiki and sound bath booking page. It is an experience, not a medical treatment.",
     ["Andre", "Kate", "Karen"], ["sound bath", "gong", "singing bowls", "vibration"]),
    ("SG-MOD-MEDITATION", "Meditation", "Sitting, breathing, and a little quiet. Tuesday nights at 7 are the free community hour, 7:00 to 8:00 Central. Deneene is listed as a meditation teacher. You can also come with no experience at all.",
     ["Deneene"], ["meditation", "tuesday", "mindfulness"]),
    ("SG-MOD-TAROT", "Tarot", "A tarot deck has 78 cards with old images for ordinary human situations. A reading is a conversation with those images, not a locked future. Adie, Andre, and Lisa Maria are on the practitioners page for tarot. Lita now offers tarot with pendulums. Lisa the astrologer also does tarot mixed with astrology. She moved, so she has no current bookings. She comes back now and then for special days — that's on Calendar when she does.",
     ["Adie", "Andre", "Lisa Maria", "Lita"], ["tarot", "cards", "reading", "pendulum"]),
    ("SG-MOD-ANGEL", "Angel readings", "Angel cards and angel communication are a gentler symbolic reading. People ask for comfort, a nudge, or a name for a feeling. Janel and Linn are listed for angel readings. Jill teaches angels and intuition. Melissa has a published Whispers of Angelic Guidance booking page.",
     ["Janel", "Linn", "Jill"], ["angel", "angels", "oracle", "archangel"]),
    ("SG-MOD-AKASHIC", "Akashic Records", "A traditional idea of a record of the soul, read in session as a way to look at patterns and questions. It is a spiritual practice, not a file cabinet science can audit. Janel and Karen both offer it. Janel's booking lets you choose Akashic or angel cards.",
     ["Janel", "Karen"], ["akashic", "akashic records", "soul"]),
    ("SG-MOD-ASTROLOGY", "Astrology", "A natal chart is a map of the sky when you were born. People use it for temperament, timing, and a language for their life. Linn is on the practitioners page. Lisa the astrologer also does astrology, and tarot mixed with astrology. She moved, so she has no current bookings. She comes back now and then for special days — that's on Calendar when she does. It is interpretive. It is not a medical chart.",
     ["Linn"], ["astrology", "birth chart", "horoscope", "zodiac", "lisa"]),
    ("SG-MOD-MEDIUM", "Mediumship", "A mediumship session is a spiritual practice of listening for messages people associate with someone who has died. Melissa is listed for mediumship. Karen offers mediumship development as a class and spirit portraits. Lori has a published intuitive mediumship booking page. Nothing here proves an afterlife, and nothing here replaces grief care.",
     ["Melissa"], ["medium", "mediumship", "loved one", "crossed over"]),
    ("SG-MOD-SHAMANIC", "Shamanic practice", "Melissa and Kate are listed for shamanic healing. Andre is listed for shamanic drumming. These are traditional earth-based practices. Come curious. Do not expect a medical procedure.",
     ["Melissa", "Kate", "Andre"], ["shaman", "shamanic", "drum", "journey"]),
    ("SG-MOD-CRANIAL", "Cranial sacral", "A very light hands-on session around the head, spine, and the body's own rhythm. Mary and Richard offer it. Mary pairs it with Reiki and intuitive guidance. It is gentle bodywork, not a promise to fix a condition.",
     ["Mary", "Richard"], ["cranial sacral", "craniosacral", "cst"]),
    ("SG-MOD-RUNES", "Runes and numerology", "Tina teaches runes, including the Elder Futhark, and also offers numerology, tarot, and Reiki on her booking pages. Numerology uses numbers from a name or a birth date as a reflective language. The Observatory has a separate number lookup you can try with no appointment.",
     ["Tina"], ["runes", "numerology", "futhark"]),
    ("SG-MOD-YOGA", "Yoga", "Cheryl offers yoga for healthy aging, plus reflexology and stretchology. You do not need to be flexible to start. Her yoga has its own booking page.",
     ["Cheryl"], ["yoga", "stretch"]),
    ("SG-MOD-CRYSTAL-HEAL", "Crystal sessions", "Janel offers crystal connections, crystal energy sessions, and a class on crystal grids. This is a guided way to work with stones, different from buying a stone in the shop. The shop is for taking one home. The session is time with her.",
     ["Janel"], ["crystal healing", "crystal grid", "janel crystals"]),
    ("SG-MOD-POEM", "Poem readings", "Lisa Seyring offers soul guidance through a poem made in the moment. It is on the practitioners page as poem readings. It is not tarot.",
     ["Lisa Seyring"], ["poem", "poetry", "channeled"]),
    ("SG-MOD-MOON", "Women's moon circles", "Mother Lotus holds women's moon circles. The practitioners page says to call for moon-circle information. A booking page for the circles is also published.",
     ["Mother Lotus"], ["moon circle", "women's circle", "new moon"]),
    ("SG-MOD-MASSAGE-NOTE", "Choosing between similar sessions", "Tarot, angel cards, and playing-card readings are all card conversations, with different decks. Reiki, cranial sacral, and massage are all hands-on or hands-near, and they do not feel the same. If you are unsure, call 847-749-3922 and say what you are carrying. The practitioners page says the shop will point you, with no pressure.",
     [], ["difference", "which one", "compare", "not sure"]),
]

for cid, title, answer, people, keys in MODS:
    names = ", ".join(people) if people else "the shop"
    add(
        card_id=cid,
        category="Modalities",
        title=title,
        purpose=f"Explain {title} in plain language and name who publishes it.",
        visitor_questions=[
            f"What is {title}?",
            f"What happens in a {title} session?",
            f"Who does {title}?",
            f"I've never tried {title}",
            f"Is {title} religious?",
            f"How do I book {title}?",
        ],
        answer=answer + f" People published for this: {names}. Holistic Center, then Practitioners, then their name. A time and a price stay on their booking page. Do not read a website address. The guide does not invent either.",
        voice_response=modality_voice(answer, people),
        navigation=nav(
            "Holistic Center, then Practitioners and Modalities. Choose the practice, then the person's name.",
            "Use the practitioners page directly. The phone menu's shortest path is the link.",
            BASE + "/practitioners-modalities-2/",
        ),
        related_cards=["SG-NAV-PRACTITIONER", "SG-NAV-BOOK"],
        keywords=keys,
        source="Practitioners and Modalities page 17216, October 11, 2026, plus published booking pages.",
        update_frequency="review_quarterly",
    )

# --- Practitioners ----------------------------------------------------------

PEOPLE = [
    ("SG-PRAC-CHERYL", "Cheryl", "/cheryl-11/", "Reflexology, yoga, and stretchology.", "The directory says call to book.", [("Reflexology", "/cheryl-2/"), ("Yoga", "/cheryl-yoga/")], True),
    ("SG-PRAC-DENEENE", "Deneene", "/deneene-11/", "Spiritual guide, grief counselor, and meditation teacher. The site says she studied with Elisabeth Kübler-Ross. She is also the founder.", "She is adding times herself. The 60-minute booking session is still a draft, so there is no public booking link yet.", [], True),
    ("SG-PRAC-ADIE", "Adie", "/adie-11/", "Tarot, with about forty years at it. The directory notes she speaks Greek.", "Here weekly, as the directory says. Open times are on her booking page.", [("Tarot", "/book/adie/")], True),
    ("SG-PRAC-AMBER", "Amber", "/amber-11/", "Customized therapeutic massage.", "The directory says four days a month. The booking page has the real openings.", [("Massage", "/book/amber/")], True),
    ("SG-PRAC-ANDREA", "Andrea", "/andrea-11/", "Nervous-system work with Brainspotting and IFS, plus Reiki. New on the directory.", "Book the published session. Open times are live.", [("Nervous-system healing", "/book/andrea/")], True),
    ("SG-PRAC-ANDRE", "Andre Peraza", "/andre-11/", "Tarot, teaching, sound bath, and shamanic drumming. The directory notes he speaks Spanish, and that he is in high demand, about one day a month.", "Open times are on the booking pages.", [("Tarot", "/book/andre-tarot/"), ("Sound bath", "/book/andre-sound-healing/")], True),
    ("SG-PRAC-EVE", "Eve", "/eve-11/", "Quantum healing, Reiki, and spiritual classes, including Spirit 101 and Spirit 201.", "Here weekly, as the directory says.", [("Reiki and energy", "/book/eve/"), ("Energy", "/book/eve-energy/"), ("Frequency", "/book/eve-frequency/"), ("Spirit 101", "/book/spirit-101/"), ("Spirit 201", "/book/spirit-201/")], True),
    ("SG-PRAC-JANEL", "Janel", "/janel-akashic-records-angel-card-reader/", "Akashic Records, angel cards, and crystal sessions.", "Here weekly, as the directory says.", [("Sessions", "/book/janel/")], True),
    ("SG-PRAC-JILL", "Jill", "/jill-11/", "Angel coach and energy healing, including workshops.", "Workshops and sessions.", [("Angels and intuition", "/book/jill/"), ("Energy body", "/book/jill-body/")], True),
    ("SG-PRAC-KAREN", "Karen", "/karen-11/", "Akashic Records, Reiki, aura imaging, soul portraits, and ancestral clearings. Also past-life sessions and classes on her booking pages.", "Several times a month, as the directory says.", [("Akashic", "/karen-akashic/")], True),
    ("SG-PRAC-KATE", "Kate Kent", "/kate-11/", "Chakra balancing, sound healing, and shamanic healing. Also paint nights and wheel-of-the-year gatherings on her booking pages.", "One day a month, as the directory says.", [("Chakra", "/book/kate-chakra/"), ("Wheel", "/book/kate-wheel/")], True),
    ("SG-PRAC-LINN", "Linn", "/linn-11/", "Astrology and angel readings. The public name on the directory is Linn. Older pages say Lin Boffeli.", "The directory says call to book. A booking page is also published.", [("Astrology or angel communication", "/book/linn/")], True),
    ("SG-PRAC-LITA", "Lita Keller", "/lita-11/", "Tarot with pendulums, and sacred crafting workshops. New on the directory.", "Open times are on her booking pages.", [("Tarot with pendulums", "/book/lita-tarot/"), ("Besom", "/book/lita-besom/"), ("Crafting", "/book/lita-crafting/")], True),
    ("SG-PRAC-LISA", "Lisa", "/lisa-astrology-v5-final/", "Astrology, and tarot mixed with astrology. This is Lisa the astrologer, not Lisa Maria and not Lisa Seyring.", "She moved. No current bookings. She comes back occasionally for special days.", [("Astrology and tarot", "/book/lisa/")], True),
    ("SG-PRAC-LISAMARIA", "Lisa Maria", "/lisa-maria-11/", "Intuitive tarot and teaching. Also somatic healing on her booking pages. The directory says she is in high demand.", "Book on her pages. Do not send her tarot clients to Lisa the astrologer.", [("Tarot", "/book/lisa-maria-tarot/"), ("Sessions", "/book/lisa-maria/"), ("Class", "/book/lisa-maria-class/")], True),
    ("SG-PRAC-LISAS", "Lisa Seyring", "/lisa-seyring-11/", "Poem readings. A poem made in the moment, not a tarot spread.", "New on the directory.", [("Poem reading", "/book/lisa-s/")], True),
    ("SG-PRAC-MARY", "Mary Keiser", "/mary-11/", "Reiki, cranial sacral, and intuitive guidance, in one integrated session.", "One day a month, as the directory says.", [("Integrated session", "/mary/")], True),
    ("SG-PRAC-MELISSA", "Melissa", "/melissa-v5/", "Shaman and medium. The directory notes she speaks Spanish and is in high demand. Classes and angelic guidance are on her other booking pages.", "Open times are on the booking pages.", [("Session", "/book/melissa/"), ("Class", "/book/melissa-class/")], True),
    ("SG-PRAC-LOTUS", "Mother Lotus", "/mother-lotus-11/", "Women's moon circles.", "Call for moon-circle information. A booking page is also published.", [("Moon circles", "/book/mother-lotus-moon-circles/")], True),
    ("SG-PRAC-RICHARD", "Richard Popp", "/richard-11/", "Cranial sacral and astral healing.", "The directory says call to book. A booking page is also published.", [("Sessions", "/book/richard/")], True),
    ("SG-PRAC-ROBERT", "Robert MacKay", "/robert-11/", "Card reading with a regular playing deck. His published line is: if I see it, I say it. Not tarot.", "In high demand, as the directory says.", [("Card reading", "/book/robert/")], True),
    ("SG-PRAC-ROSE", "Rose", "/rose-v5-working/", "Reiki using the energies of the ankh and archangels, in her published booking title. The directory notes she speaks Italian and is in high demand.", "Open times are on her booking pages.", [("Reiki", "/book/rose/"), ("Vision", "/book/rose-vision/")], True),
    ("SG-PRAC-RENEE", "Renee", "/renee-2/", "Reiki. Her published booking title says free community appointments, love donations.", "New on the directory.", [("Reiki", "/book/renee/")], True),
    ("SG-PRAC-TINA", "Tina Santana", "/tina-v-5/", "Runes educator on the directory. Her booking pages also include numerology, tarot, Reiki, sound, pendulums, and a women's stillness circle.", "Limited availability, as the directory says.", [("Runes class", "/book/tina-runes-class/"), ("Sound", "/book/tina-sound/"), ("Divine feminine", "/book/tina-divine-feminine/")], True),
    ("SG-PRAC-SHERRY", "Sherry Gurley", "/sherry/", "Tai Chi Gung. She has a published booking page. She is not on the practitioners portrait grid.", "Book the Tai Chi page or call the shop.", [("Tai Chi Gung", "/sherry/")], False),
    ("SG-PRAC-KASHIA", "Kashia", "/book/hawaiian-massage/", "Hawaiian massage, on a published booking page. Not on the practitioners portrait grid.", "The booking page has the openings.", [("Hawaiian massage", "/book/hawaiian-massage/")], False),
    ("SG-PRAC-LORI", "Lori", "/book/lori-medium/", "Intuitive mediumship, on a published booking page. Not on the practitioners portrait grid.", "The booking page has the openings.", [("Mediumship", "/book/lori-medium/")], False),
]

for cid, name, profile, blurb, avail, bookings, on_dir in PEOPLE:
    book_urls = [BASE + path for _, path in bookings]
    where = "on the practitioners page" if on_dir else "by a published booking page, and not yet on the portrait grid"
    if cid == "SG-PRAC-LISA":
        voice = (
            "Lisa is the astrologer — not Lisa Maria, and not Lisa Seyring. "
            "She does astrology, and tarot mixed with astrology. "
            "She moved, so she has no current bookings. "
            "She comes back now and then for special days. When she does, that's on Calendar."
        )
        answer = (
            f"{name} is {where}. {blurb} {avail} "
            "Do not invent a time or say she is here this week unless Calendar shows her. "
            "Do not send her clients to Lisa Maria. Do not read a website address. "
            "If they want a day she is in, say Calendar, or call 847-749-3922."
        )
    elif cid == "SG-PRAC-DENEENE":
        voice = (
            "Deneene is the founder. Her page lists her as a spiritual guide, grief counselor, and meditation teacher. "
            "If you want time with her, look on Calendar for the days she is in. "
            "I can't see a time that isn't published."
        )
        answer = (
            f"{name} is {where}. {blurb} {avail} "
            "Her dates go on Calendar. Send grief questions there, not to a sales pitch. "
            "Do not invent a time. If nothing is listed, say so and offer 847-749-3922. "
            "Do not read a website address. Do not claim a license beyond the words on her page. "
            "If they are feeling suicidal or in a crisis, please call or text 988. A dedicated professional can help them now."
        )
    else:
        voice = (
            f"{spoken_name(name)} is {where}. {blurb} "
            "For a time, Holistic Center, then Practitioners, then their name. Not the homepage Book Now button."
        )
        answer = (
            f"{name} is {where}. {blurb} {avail} "
            "A time is on their booking page. Do not read a website address out loud. "
            "Say Holistic Center, then Practitioners, then their name. "
            "Length and price stay on that page. If no time is open, say so and offer the phone, 847-749-3922. "
            "Homepage Book Now opens Calendar. This person gets their own page."
        )
    add(
        card_id=cid,
        category="Practitioners",
        title=name,
        purpose=f"Identify {name}, what they publish, and where to book them.",
        visitor_questions=[
            f"Who is {name.split()[0]}?",
            f"What does {name.split()[0]} do?",
            f"How do I book {name.split()[0]}?",
            f"Is {name.split()[0]} available?",
            f"Tell me about {name}",
        ],
        answer=answer,
        voice_response=voice,
        navigation=nav(
            "Holistic Center, then Practitioners, then their name.",
            "Holistic Center is under the desktop menu. On a phone, Practitioners is the path.",
            BASE + profile,
        ),
        related_cards=["SG-NAV-BOOK", "SG-NAV-PRACTITIONER"],
        keywords=[name.lower(), name.split()[0].lower()],
        source="Practitioners page 17216 and published booking pages, October 11, 2026.",
        update_frequency="review_quarterly",
        live_source="The booking URL for open times and price.",
        booking_urls=book_urls,
        on_directory=on_dir,
    )

# --- Articles ---------------------------------------------------------------

ARTS = [
    ("SG-ART-SMUDGING", "Smudging, sage, and clearing a space",
     "/cleansing-rituals-smudging/",
     "Smudging is the practice of burning an herb, often white sage or another traditional plant, and moving the smoke through a room or around yourself as a way of clearing. People use it when a space feels heavy, after an argument, or when they move. It is a ritual, not a disinfectant and not a medical treatment. The shop sells sage and related incense when it is in stock. The guide Smudging: How to Clean and Clear Yourself and a Space is the short how-to. Her longer essay is Cleansing Rituals, Smudging.",
     ["smudging", "sage", "burn sage", "palo santo", "clear and clean", "cleansing", "smudge"]),
    ("SG-ART-CLEAR-CRYSTAL", "How to clear a crystal and choose one for a room",
     "/how-to-clean-clear-and-pick-the-right-crystal-for-your-space/",
     "Clearing a crystal means the traditional rinse of use: sunlight for some stones, moonlight, smoke, sound, or simply time, depending on the mineral. Not every stone likes water or salt or direct sun. Amethyst can fade in a hard sun. The essay is about a home or an office, and about picking a stone for the room rather than grabbing the prettiest one. Read her piece before inventing a care method. The shop is where you can hold them.",
     ["clear crystal", "cleanse crystal", "charge", "which crystal for my house"]),
    ("SG-ART-BEGINNER-CRYSTALS", "A beginner's guide to crystals",
     "/a-beginners-guide-to-working-with-crystals/",
     "You can start with one stone you like in your hand. You do not need a grid, a glossary, or a belief system. Her beginner's essay walks through what a crystal is and simple ways people work with them. Treat older lines in that essay about healing disease or weight with care: the guide does not repeat medical promises. Come in, pick it up, ask.",
     ["beginner crystals", "how to use crystals", "new to crystals"]),
    ("SG-ART-AMETHYST", "Amethyst",
     "/why-amethyst-is-called-swiss-army-knife-of-crystals/",
     "Amethyst is a violet variety of quartz. Iron and natural irradiation make the purple. The Greek name means not drunken. It shows up from pale lilac to deep grape, depending on where it grew. People have traditionally reached for it when they want a clear head, quiet, or help with intuition, and it is often paired with the crown. That is tradition. It is also just a beautiful mineral. Her essay calls it the Swiss Army knife because people use it for so many ordinary intentions.",
     ["amethyst", "purple quartz", "crown chakra"]),
    ("SG-ART-GROUND", "Stones people use to feel steadier",
     "/the-top-5-crystals-to-ground-you-and-how-to-use-them/",
     "Grounding, in this shop's language, means feeling back in your body and on the floor after a scattered day. Her essay names stones people traditionally use for that and how they keep them nearby. It is a practice, not a prescription. If the day is more than a stone can hold, say so, and offer a person or the phone.",
     ["grounding", "root", "hematite", "black tourmaline", "anxious"]),
    ("SG-ART-INTENTION", "Setting an intention with a stone",
     "/how-to-program-crystals-and-set-intentions/",
     "Programming is shop language for sitting with a stone and getting clear about what you want it to remind you of. It is attention, not a remote control. Her essay is the longer version. A simple version: hold it, say the true thing, put it where you will see it.",
     ["program a crystal", "intention", "set intention"]),
    ("SG-ART-REIKI", "What is Reiki?",
     "/what-is-reiki-understanding-energy-healing/",
     "Reiki is a Japanese word for a gentle energy practice. Rei and ki: universal, and life energy. You stay clothed. Touch is light, or the hands stay just off the body. People come to rest. The essay on the site is the longer explanation. Who offers it is on the Reiki modality card. It does not replace medical care.",
     ["what is reiki", "energy healing"]),
    ("SG-ART-CARDS", "Tarot, angel cards, and intuitive readings",
     "/what-are-card-readings-understanding-tarot-angel-intuitive-guidance/",
     "A card reading uses a symbolic deck to look at a question. Tarot is 78 archetypal images. Angel or oracle cards tend to be gentler and more direct. An intuitive reading leans on the reader's impressions. None of them lock a future in place. Her essay says that. Adie, Andre, and Lisa Maria read tarot. Robert reads a regular playing deck. Janel and Linn read angel cards. Lisa Seyring works in poems, not cards.",
     ["tarot vs oracle", "card reading", "intuitive reading", "difference between tarot and angel"]),
    ("SG-ART-SOUND", "What is sound healing?",
     "/what-is-sound-healing-understanding-vibrational-healing/",
     "Sound healing here means bowls, gongs, forks, or voice, used so you can feel sound in the body. You usually lie down and listen. Her essay is the longer piece. Andre, Kate, and Karen are on the practitioners page for sound.",
     ["sound healing", "sound bath", "what is a gong bath"]),
    ("SG-ART-MEDITATION", "What is meditation?",
     "/what-is-meditation-understanding-mindfulness-practice/",
     "Meditation is practice at being here: breath, a phrase, or just sitting. You can be bad at it and still be doing it. Tuesday at 7 PM is the free community hour. Her essay is the longer welcome. The Observatory and the Library also have music for it.",
     ["what is meditation", "how to meditate", "beginner meditation"]),
    ("SG-ART-AKASHIC", "What is an Akashic reading?",
     "/akashic-record-reading-everything-you-need-to-know/",
     "The Akashic Records are a traditional picture of a soul's memory, opened in session as a way to ask about patterns. Her essay is the long version. Janel and Karen are who the practitioners page names. It is a spiritual session. It is not a background check and not therapy.",
     ["akashic", "akashic records reading"]),
    ("SG-ART-EMPATH", "If you feel everything",
     "/do-you-easily-cry-are-you-highly-sensitive-to-other-peoples-energy-maybe-you-are-an-empath/",
     "Some people walk into a room and feel it before anyone speaks. Her essay talks about that sensitivity. It is not a diagnosis. If the feeling is grief, slow down. If they want language and company, the essay is there, and so is the Holistic Center. Janel has a published class called Navigating Life as an Empath or Sensitive Soul.",
     ["empath", "highly sensitive", "i feel everything", "overwhelmed"]),
    ("SG-GUIDE-CLEAN", "Guide: clean and clear",
     "/library/guides/clean-and-clear/",
     "This short guide is Smudging: How to Clean and Clear Yourself and a Space. It sits with the longer smudging essay. Use both when someone asks how to burn sage or how to clear a room. Sell nothing they did not ask for. The shop has sage when the product page says so.",
     ["how to smudge", "clear a room", "clean and clear"]),
]

for cid, title, path, answer, keys in ARTS:
    add(
        card_id=cid,
        category="Articles",
        title=title,
        purpose="Answer a popular question in her voice and hand them her essay.",
        visitor_questions=[
            title + "?",
            "Where can I read about this?",
            "Do you have something on " + keys[0] + "?",
        ],
        answer=answer + " That essay is under Library, then Articles. Do not read a website address.",
        voice_response=answer.split(".")[0] + ". That's under Library, then Articles, if you want the longer version.",
        navigation=nav("Library, then Articles.", "Library in the menu, then Articles on the page.", BASE + path),
        related_cards=["SG-KNOW-LIBRARY", "SG-ART-SMUDGING"],
        keywords=keys,
        source=f"Published essay or guide {path}, October 11, 2026. Topic set chosen with the founder: smudging, sage, clear and clean, and the matching public explainers. No view-count plugin was present.",
        update_frequency="stable",
    )

# --- Navigation -------------------------------------------------------------

NAVS = [
    ("SG-NAV-PRACTITIONER", "Find a practitioner",
     "Open Holistic Center, then Practitioners and Modalities. Portraits are on that page. Each name goes to the newer profile.",
     "The phone menu does not list every person. Use the practitioners link directly.",
     "/practitioners-modalities-2/",
     ["who works there", "find a reader", "help me choose"]),
    ("SG-NAV-BOOK", "Book a specific person",
     "Open that person's profile from the practitioners page, then their booking link. Do not use homepage Book Now for a named person. Homepage Book Now opens the events calendar.",
     "Same. Use their direct profile and booking links.",
     "/practitioners-modalities-2/",
     ["book an appointment", "schedule", "reserve"]),
    ("SG-NAV-EVENTS", "See what is happening",
     "Calendar in the top menu opens the events list. You can switch months in The Events Calendar. Open a title for the description. Registering is the booking or ticket link on that event, or a call to the shop.",
     "Calendar in the phone menu. Your Calendar under it is for bookings you already made, after you sign in.",
     "/events/list/",
     ["calendar", "what's on", "this weekend", "tomorrow"]),
    ("SG-NAV-YOUR-CAL", "See bookings you already made",
     "Calendar, then Your Calendar. Sign in with the same email you booked with. Upcoming and past are the two tabs. Reschedule or cancel as early as you can. Less than 24 hours' notice is not eligible for a refund. Questions: 847-749-3922.",
     "Calendar, then Your Calendar. Same sign-in.",
     "/your-calendar/",
     ["my appointment", "cancel", "reschedule", "I already booked"]),
    ("SG-NAV-LIBRARY", "Browse the Library",
     "Library in the top menu, then Articles, Books, Movies, Music, Podcasts, or Guides.",
     "Library in the phone menu shows Guides in the submenu. The Library page has all six shelves.",
     "/library/",
     ["library", "read", "books"]),
    ("SG-NAV-OBSERVATORY", "Open the Observatory",
     "Observatory in the top menu.",
     "Observatory in the phone menu.",
     "/sacred-ground-observatory/",
     ["observatory", "moon", "daily"]),
    ("SG-NAV-SHOP", "Shop online",
     "Shop in the top menu. Add to cart, then checkout.",
     "Shop in the phone menu.",
     "/shop/",
     ["buy", "store online", "cart"]),
    ("SG-NAV-HOURS", "Hours, address, and the phone",
     "Contact in the menu. Address is 160 W Campbell Street, Arlington Heights, IL 60005.",
     "Contact in the phone menu.",
     "/contact/",
     ["hours", "address", "call", "directions"]),
    ("SG-NAV-FREE", "Find a free event",
     "Open the events list and look for Free in the title, or ask for meditation, educational night, or reiki share. Confirm the date on the calendar.",
     "Same calendar link.",
     "/events/list/",
     ["free events", "free class"]),
    ("SG-NAV-START", "Not sure where to start",
     "Ask what they are carrying, or what they are curious about. Shop if they want to wander. Practitioners if they want a person. Library if they want to read. Observatory if they want the moon, a stone, or a number. Calendar if they want to see the week. Phone if they want a human: 847-749-3922.",
     "Same destinations. Name the menu item. Do not read a website.",
     "/",
     ["where do I start", "help me", "overwhelmed", "just browsing"]),
    ("SG-NAV-MONTHLY", "Open Monthly",
     "Monthly in the top menu. That is the name on the nav. Some people still call it the newsletter. Do not call the menu item the newsletter.",
     "Monthly in the phone menu.",
     "/earth-ether/",
     ["monthly", "newsletter", "earth and ether", "earth & ether"]),
]

for cid, title, desktop, mobile, path, keys in NAVS:
    add(
        card_id=cid,
        layer="navigation",
        category="Navigation",
        title=title,
        purpose=f"Walk a visitor through: {title}.",
        visitor_questions=[title + "?", "How do I " + title.lower() + "?", "Where is that on my phone?"],
        answer=desktop + " On a phone: " + mobile + " Do not read a website address. Name the menu item.",
        voice_response=f"That's on our nav — {speak_nav(path)}.",
        navigation=nav(desktop, mobile, BASE + path),
        keywords=keys,
        source="Primary menu, mobile menu, and homepage buttons, October 11, 2026. Founder decision 8.",
    )

# --- Live map cards (instructions, not cached facts) ------------------------

add(
    card_id="SG-LIVE-EVENTS",
    layer="live",
    category="Live data",
    title="Upcoming events must be fetched",
    purpose="Stop the guide from memorizing the calendar.",
    visitor_questions=["What's happening tomorrow?", "What's on this weekend?", "Is meditation on this Tuesday?"],
    answer="Answer from The Events Calendar at the time of the question. If the lookup fails, say you cannot see the live calendar and point them to Calendar in the menu. Do not read a website address.",
    voice_response="Let me look at Calendar rather than guess. If I can't see it, that's Calendar in the menu.",
    navigation=nav("Calendar menu.", "Calendar in the phone menu.", BASE + "/events/list/"),
    keywords=["tomorrow", "this week", "schedule"],
    source="The Events Calendar, tribe_events.",
    update_frequency="live_only",
    live_source="WordPress Events Calendar.",
)

add(
    card_id="SG-LIVE-BOOKING",
    layer="live",
    category="Live data",
    title="Appointment times and prices must be fetched",
    purpose="Stop the guide from quoting a stale price or an open slot.",
    visitor_questions=["Is there a time on Friday?", "How much is a reading?", "How long is the session?"],
    answer="Open that practitioner's booking URL. Read the length and price there. If no time is published, say so and offer 847-749-3922. Never say you booked it.",
    voice_response="The booking page has the real times and the real price. I won't guess, and I won't tell you it's reserved until that page finishes it.",
    navigation=nav("The person's booking link.", "The person's booking link.", BASE + "/practitioners-modalities-2/"),
    keywords=["price", "availability", "cost", "how much"],
    source="Fluent Booking event pages.",
    update_frequency="live_only",
    live_source="Fluent Booking.",
)

add(
    card_id="SG-LIVE-STOCK",
    layer="live",
    category="Live data",
    title="Product stock must be fetched",
    purpose="Stop the guide from inventing inventory.",
    visitor_questions=["Do you have amethyst in the shop?", "Is this in stock?", "Can I buy this online?"],
    answer="Check the WooCommerce product. If it is not listed, say you cannot see it online and give the phone and the address. People can also walk in.",
    voice_response="I can only confirm what the shop page shows. If it isn't listed, call the store or come by 160 W Campbell Street.",
    navigation=nav("Shop menu.", "Shop in the phone menu.", BASE + "/shop/"),
    keywords=["in stock", "inventory", "do you have"],
    source="WooCommerce.",
    update_frequency="live_only",
    live_source="WooCommerce.",
)

# Write -----------------------------------------------------------------------

by_layer = {}
for c in cards:
    by_layer.setdefault(c["layer"], []).append(c)

(ROOT / "cards").mkdir(exist_ok=True)
(ROOT / "questions").mkdir(exist_ok=True)

for layer, group in by_layer.items():
    (ROOT / "cards" / f"{layer}.json").write_text(json.dumps(group, indent=2, ensure_ascii=False) + "\n")

(ROOT / "cards" / "all-cards.json").write_text(json.dumps(cards, indent=2, ensure_ascii=False) + "\n")

questions = []
for c in cards:
    for q in c["visitor_questions"]:
        questions.append({
            "question": q,
            "card_id": c["card_id"],
            "category": c["category"],
            "direct_url": c["navigation"]["direct_url"],
        })
(ROOT / "questions" / "visitor-questions.json").write_text(json.dumps(questions, indent=2, ensure_ascii=False) + "\n")

index = {
    "generated": VERIFIED,
    "card_count": len(cards),
    "question_count": len(questions),
    "by_category": {},
    "by_keyword": {},
    "by_url": {},
}
for c in cards:
    index["by_category"].setdefault(c["category"], []).append(c["card_id"])
    index["by_url"].setdefault(c["navigation"]["direct_url"], []).append(c["card_id"])
    for k in c["keywords"]:
        index["by_keyword"].setdefault(k.lower(), []).append(c["card_id"])
(ROOT / "INDEX.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")

lines = [
    "# Sacred Ground AI Knowledge Library",
    "",
    f"Verified {VERIFIED}. {len(cards)} cards. {len(questions)} visitor questions.",
    "Draft for Deneene to read. The guide is not switched on.",
    "",
    "Start with `voice/VOICE-BIBLE.md` and `01-DECISIONS.md`.",
    "",
]
order = ["voice", "knowledge", "navigation", "live"]
for layer in order:
    lines.append(f"## {layer.title()}")
    lines.append("")
    for c in by_layer.get(layer, []):
        url = c["navigation"]["direct_url"]
        lines.append(f"- **{c['card_id']}** — {c['title']} — {url}")
    lines.append("")
(ROOT / "INDEX.md").write_text("\n".join(lines))

# Human review, one block per card
review = ["# Cards for review", "", "Spoken line first, then the page.", ""]
for c in cards:
    review.append(f"## {c['title']}")
    review.append("")
    review.append(c["voice_response"])
    review.append("")
    review.append(c["navigation"]["desktop"])
    review.append("")
(ROOT / "cards" / "REVIEW.md").write_text("\n".join(review))

print(f"cards={len(cards)} questions={len(questions)}")
