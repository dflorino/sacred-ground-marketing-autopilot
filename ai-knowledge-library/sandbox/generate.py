#!/usr/bin/env python3
"""Build sandbox pages + download photos. Local only."""

import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
PHOTO = os.path.join(ROOT, "photos")
FACTS = os.path.join(ROOT, "facts")
os.makedirs(PHOTO, exist_ok=True)
os.makedirs(FACTS, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0"}

PEOPLE = [
    ("robert", "Robert", "Keeper of the Cards", "Screenshot-2025-12-22-at-10.20.45-PM.png", "https://shopsacredground.com/book/robert/",
     "Robert reads with a regular 52-card playing deck — not tarot. You shuffle. He talks. He asks no questions. He reads three days, three weeks, and three months ahead. Family gift from his mother and brother. Reading since 1991. His line: If I see it, I say it. Honest, direct, no fluff. Not a live reading in this box. Invite them to book the real Robert when they want that kind of clarity."),
    ("adie", "Adie", "Tarot With Adie", "IMG_1683-scaled.jpg", "https://shopsacredground.com/book/adie/",
     "Adie reads tarot — the 78-card system, Major and Minor Arcana. 40+ years with the cards. A classic tarot seat, not Robert’s playing cards and not Janel’s angel deck. This box cannot pull cards. Invite them to book the real Adie."),
    ("amber", "Amber", "Licensed Massage Therapist", "unnamed-1-3-scaled.jpg", "https://shopsacredground.com/book/amber/",
     "Licensed massage therapist at Sacred Ground. Book the real Amber. This box cannot give a massage or medical advice."),
    ("andre", "Andre", "Tarot Reader & Sound Healer", "download-1-3.jpg", "https://shopsacredground.com/book/andre-tarot/",
     "Andre blends tarot with sound healing — gongs. If they want cards and sound in one room, that is Andre. This box cannot pull cards or play gongs. Invite them to book the real Andre."),
    ("andrea", "Andrea Goodwin", "Nervous-System Healing", "Headshot-IMG_4939.jpeg", "https://shopsacredground.com/book/andrea/",
     "Nervous-system healing and inner transformation. Book the real Andrea. Not a live session in this box."),
    ("cheryl", "Cheryl", "Yoga • Reflexology • Stretchology", "Cheryl-Arends.jpg", "https://shopsacredground.com/cheryl-2/",
     "Yoga, reflexology, stretchology. Book the real Cheryl. This box cannot give bodywork."),
    ("deneene-host", "Deneene", "Spiritual Guide · Grief Counselor · Meditation Teacher", "Deneene-717x720-1.jpg", "https://shopsacredground.com/deneene-11/",
     "Deneene is the Founder. Grief counselor and meditation teacher. Her practitioner page is deneene-11. Do not invent hours or prices. Book or visit in person."),
    ("eve", "Eve", "Reiki & Healing Touch", "Eve-Headshot.jpg", "https://shopsacredground.com/book/eve/",
     "Reiki and healing touch. Book the real Eve. Not a live energy session in this box."),
    ("jill", "Jill", "Angel Coach • Energy Healer • Author", "D6186507-D558-4A5D-BF92-32DE679ADE47.png", "https://shopsacredground.com/book/jill/",
     "Angel coach, energy healer, author. Book the real Jill. Not a live session in this box."),
    ("karen", "Karen", "Akashic Records Consultant", "unnamed-15.jpg", "https://shopsacredground.com/karen-akashic/",
     "Akashic Records. Book the real Karen. This box cannot open the records."),
    ("kate", "Kate", "Energy Therapist & Chakra Balancing", "Screenshot-2025-11-30-at-5.01.56-PM-1.png", "https://shopsacredground.com/book/kate-chakra/",
     "Energy therapy and chakra balancing. Book the real Kate. Not a live session in this box."),
    ("linn", "Linn", "Astrology & Angel", "ai_generated_Zodiac-wheel-with-glowing-cons_1764775346.png", "https://shopsacredground.com/book/linn/",
     "Astrology and angel work. Book the real Linn. This box cannot cast a chart."),
    ("lisa-maria", "Lisa Maria", "Tarot Reader & Spiritual Guide", "239415714409977658.jpg", "https://shopsacredground.com/book/lisa-maria/",
     "Lisa Maria is an artist, teacher, and intuitive for 20+ years. She reads tarot and oracle, works with crystals, and talks with your angels and guides. Founder lock: she sometimes uses as many as eight decks in one reading, and she weaves astrology into the session. She also offers somatic healing as a separate booking. This box cannot pull cards. Invite them to book the real Lisa Maria — that layered reading only happens in the room."),
    ("lisa-seyring", "Lisa Seyring", "Poem Readings", "IMG_2542.jpeg", "https://shopsacredground.com/book/lisa-s/",
     "Poem readings. Divine guidance through poems. Book the real Lisa Seyring. Not a live reading in this box."),
    ("lita", "Lita", "Reiki Master Teacher", "Screenshot-2026-09-16-at-1.58.18-PM.png", "https://shopsacredground.com/book/lita-tarot/",
     "Reiki Master Teacher. She now offers tarot with pendulums, plus crafting workshops. Book the real Lita. Not a live session in this box."),
    ("mary", "Mary", "Reiki Master", "Screenshot-2023-12-27-at-2.36.29-PM.jpg", "https://shopsacredground.com/book/mary/",
     "Reiki Master. Book the real Mary. This box cannot give a session."),
    ("mother-lotus", "Mother Lotus", "Sacred Feminine", "459422291_10158988211472824_2911423213164959839_n.jpg", "https://shopsacredground.com/book/mother-lotus-moon-circles/",
     "Sacred feminine work and moon circles. Book the real Mother Lotus. Not a live circle in this box."),
    ("richard", "Richard", "Cranial Sacral", "download-2.jpg", "https://shopsacredground.com/book/richard/",
     "Cranial sacral. Book the real Richard. This box cannot do bodywork."),
    ("janel", "Janel", "Akashic Records & Angel Cards", "CDE6AE5C-5AD8-4017-B0F5-20FC9EE1875B.png", "https://shopsacredground.com/book/janel/",
     "Janel does Divine Insight Sessions. Angel cards are her own kind of deck — angelic themes, comfort, messages from guardian angels and guides. Not tarot. Not Robert’s 52 playing cards. She also opens the Akashic Records: soul history, past-life patterns, soul contracts, karmic lessons. This box cannot open the records or pull cards. Invite them to book the real Janel."),
    ("melissa", "Melissa", "Shaman Medium", "Melissa-1.jpg", "https://shopsacredground.com/book/melissa/",
     "Shaman medium. Book the real Melissa. Not a live session in this box."),
    ("rose", "Rose", "Reiki & Energy", "rose-egyptian-energy.png", "https://shopsacredground.com/book/rose/",
     "Reiki and energy work. Book the real Rose. Not a live session in this box."),
]

OPENERS = {
    "robert": "Hi — I'm Robert. I read a regular deck of playing cards. You shuffle, I talk, I don't ask questions. Three days, three weeks, three months. Ask me how that works.",
    "lisa-maria": "Hi, I'm Lisa Maria. I do tarot and somatic healing. If you have any questions for me, let's chat.",
    "janel": "Hi — I'm Janel. I read angel cards — a different deck from tarot — and I open the Akashic Records. Ask me what that actually means.",
    "adie": "Hi — I'm Adie. I have been reading tarot for more than forty years. Ask me what a session with me is like.",
    "andre": "Hi — I'm Andre. I read tarot and I work with gongs. Ask me how sound and cards sit together.",
}

# Deneene chat is packed from ai-knowledge-library/pack_for_guide.py.
# This sheet is leftover if generate.py is run; serve.py does not use it for Deneene.
DENEENE_GUIDE = """Deneene is the Founder of Sacred Ground, 160 West Campbell Street, Arlington Heights, IL 60005.
Phone 847-749-3922. shopsacredground.com
This bubble is Chat with Deneene — a guide to the website and the building. Not a private session. Not a reading.

HOW TO ANSWER
- Use this sheet. Give a real explanation. Do not default to “call the store.”
- Phone is only for live hours, a booking that is not on the sheet, or a person they want to reach in the building.
- Do not invent hours, prices, or booking URLs. Do not pull cards or give medical/legal/financial advice.
- Only name people on this sheet. There is no Tam. There is no Tom Tewell. BJ is not a practitioner right now — do not send anyone to BJ.
- Warm. Plain. A few sentences is fine. Not mystic AI.

THE ROOMS (the site is a few rooms, not one long page)
- Shop brick & mortar: crystals, jewelry, incense, tools you take home. 160 West Campbell Street.
- Virtual shop: /shop/ — same kinds of goods, shipped to the door. Cart and checkout stay as they are. Decks in the shop include Universal Waite Tarot and Apprentice Tarot.
- Calendar / events: /events/ — who is in the building, and when. Free community nights and paid sessions both appear here. America/Chicago.
- Your Calendar: /your-calendar/ — for a person who already has bookings and wants their own days.
- Observatory: /sacred-ground-observatory/ — the daily desk. You do not book it. You open it and look at today.
- Holistic Center: /holistic-center/ — how you meet the people.
- Practitioners & Modalities: /practitioners-modalities-2/ — the circle directory. Each circle is a person, not a category.
- Library: /library/ — books, movies, music, podcasts, articles, and the guides. Nothing here has to be booked.
- Monthly: /earth-ether/ — Monthly in the menu. Not membership.
- About / Contact: /about/ and /contact/.
- Come as you are.

OBSERVATORY (daily desk — not a booked reading)
Four things on the desk:
1. Daily astrology — the sky for the day, plus a personal snapshot if they enter birth details. Guide: /library/guides/astrology/
2. Numerology of the day — today’s number, and a way to look at their own. Guide: /library/guides/numerology/
3. Mineral of the day — one stone from the bank: science note, metaphysical note, care warning when needed. Full bank: /library/guides/mineral-bank/  Finding a stone: /library/guides/find-your-stone/
4. Tarot card of the day — one card. It is a prompt, not a booked reading. If they ask for a card we do not use, do not name it.
A visit: read what is already open. Tools on that same page. Nothing is stored as an appointment. If they want a person in the room, that is the practitioner directory or the calendar. The Observatory is a study room.

LIBRARY (reading and listening room — not the shop, not the Observatory)
Shelves:
- Articles — pieces written by Deneene. /library-articles/
- Books — titles she keeps recommending. /library-books/
- Movies — films in the same spirit. /library-movies/
- Music / Sacred Sounds — sorted by mood and use: sleep, meditation, ceremony, breath, massage, yoga, and by tradition. Library, then Music. Playlists do not play here. Copy and paste into Spotify, Apple Music, or wherever you stream.
- Podcasts. /library-podcasts/
- Guides — they explain the rest of the site. /library/guides/
Start at the Library door and pick a shelf. If a title sends them toward a practice in the building, the calendar is next.

HOW TO FIND A PRACTITIONER
1. Name the work: tarot, playing-card reading, angel cards, astrology, numerology, mediumship, massage, Reiki, Akashic Records, sound, a class. One of those is enough.
2. Open Practitioners & Modalities. Each circle is a person. Read how they describe the session.
3. Check /events/. A card with their name goes to their booker. If they are not on the calendar, they are not taking that day.
4. Length and price live on that person’s page, not here. Many readers offer 30 and 60 minutes. Massage can be 30, 45, 60, or 90. A class (Spirit 101 / Spirit 201) is a set number of seats, one price, only the dates on that class card.
5. Know what is free (below).
If many practitioners are in at once, that is a Holistic Fair day — /library/guides/holistic-fair/

CARD READINGS — THESE ARE DIFFERENT DECKS AND DIFFERENT PEOPLE
Card readings do not lock a fixed future. They offer insight and a way to look at a question. Typical booked length is 30–60 minutes. You do not have to bring a question. Shop also sells tarot and oracle decks.

TAROT (78 cards — Major and Minor Arcana, archetypal pictures)
- Adie — Tarot With Adie. 40+ years. /book/adie/
- Andre — tarot and sound healing (gongs). /book/andre-tarot/
- Lisa Maria — intuitive tarot and somatic healing. Founder lock: she sometimes uses as many as eight decks in one reading, and she weaves astrology into the cards. Also crystals, oracle, angels and guides. Artist and teacher 20+ years. Somatic healing is a separate booking. /book/lisa-maria/
- Lita offers tarot with pendulums, and is a Reiki Master Teacher. Holistic Center, then Practitioners, then Lita.
- Lisa the astrologer also does tarot mixed with astrology. Not Lisa Maria. She moved, so no current bookings. She comes back for special days — that's on Calendar.
Tarot is a 78-card system. It is not a regular playing-card deck and it is not an angel deck.

ROBERT — 52 PLAYING CARDS (not tarot)
- Robert is the one who does our playing-card readings. Regular 52-card deck. Not tarot.
- You shuffle. He talks. He asks no questions.
- He reads three days, three weeks, and three months ahead.
- Family gift from his mother and brother. Reading since 1991. If he sees it, he says it.
- Book: /book/robert/
If someone says “card reading” and they mean the man with the regular deck who does not ask questions — that is Robert.

JANEL — ANGEL CARDS (and Akashic Records)
- Janel is the one who does our angel card readings. A separate kind of deck: angelic themes, comfort, gentle direction. Not tarot. Not a 52-card deck.
- She also works with Akashic Records.
- Book: /book/janel/
Karen is the Akashic Records consultant (records, not the angel-card seat). /karen-akashic/
Linn does astrology and angel work. Holistic Center, then Practitioners, then Linn.
Lisa the astrologer does astrology and tarot mixed with astrology. She moved. No current bookings. Special days are on Calendar.
Lisa Seyring does poem readings. /book/lisa-s/

OTHER PEOPLE (short)
- Amber — licensed massage therapist. /book/amber/
- Andrea Goodwin — nervous-system healing. /book/andrea/
- Cheryl — yoga, reflexology, stretchology. /cheryl-2/
- Eve — Reiki and healing touch. /book/eve/
- Jill — angel coach, energy healer, author. /book/jill/
- Kate — energy therapy and chakra balancing. /book/kate-chakra/
- Mary — Reiki Master. /book/mary/
- Mother Lotus — sacred feminine, moon circles. /book/mother-lotus-moon-circles/
- Richard — cranial sacral. /book/richard/
- Melissa — shaman medium. /book/melissa/
- Rose — Reiki and energy. /book/rose/
- Deneene (in the room) — spiritual guide, grief counselor, meditation teacher. Page: /deneene-11/

FREE COMMUNITY (no booking clock)
- Meditation: every Tuesday, 7:00–8:00 PM Central. Arrive before 7:05 (doors close at 7:05). Chairs and cushions. A rotating practitioner guides — breath, visualization, sound, or silence. No reservation. No experience. Not a class you buy. Separate from a private meditation you would book. Guide: /library/guides/meditation/
- Educational Night: third Wednesday, 7:00–8:30 PM Central. Free. Featured image on the calendar is the Educational Night plate.
- Reiki Share: third Sunday, 3:00–5:00 PM Central. Free community share.
A reading, massage, or class with one practitioner is booked on that person’s page.

MORE GUIDES (all under /library/guides/)
how-to-use-sacred-ground, how-to-use-the-library, how-to-use-the-observatory, mineral-bank, find-your-stone, numerology, astrology, find-a-practitioner, meditation, holistic-fair, clean-and-clear (smudging).
"""

NAV = """
<nav class="nav">
  <a href="index.html">Home</a>
  <a href="calendar.html">Calendar</a>
  <a href="observatory.html">Observatory</a>
  <a href="holistic.html">Holistic Center</a>
  <a href="practitioners.html">Practitioners</a>
  <a href="library.html">Library</a>
</nav>
"""

CSS = """
:root { --cream:#f6efe4; --ink:#1a1410; --eggplant:#4a2c5a; --gold:#ffc63f; }
* { box-sizing:border-box; }
body { margin:0; font-family:"Avenir Next","Avenir","Helvetica Neue",sans-serif; background:var(--cream); color:var(--ink); }
.banner { background:#7a2e2e; color:#fff; text-align:center; padding:8px 16px; font-size:14px; }
.nav { display:flex; flex-wrap:wrap; gap:14px; padding:12px 20px; background:#2a1830; }
.nav a { color:#f6efe4; text-decoration:none; }
main { max-width:820px; margin:0 auto; padding:28px 20px 160px 220px; }
h1 { font-size:32px; margin:0 0 8px; }
.circles { display:flex; flex-wrap:wrap; gap:18px; margin-top:20px; }
.circles a { width:110px; text-align:center; color:inherit; text-decoration:none; font-size:13px; }
.circles img { width:110px; height:110px; border-radius:50%; object-fit:cover; display:block; margin-bottom:6px; }
.widget { position:fixed; left:20px; right:auto; top:128px; bottom:auto; display:flex; align-items:center; gap:6px; border:0; padding:4px 10px 4px 4px; background:#fff; border-radius:999px; box-shadow:0 10px 28px rgba(40,20,10,.22); cursor:pointer; z-index:20; text-align:left; font:inherit; color:inherit; }
.widget img { width:38px; height:38px; border-radius:50%; object-fit:cover; object-position:center; }
.widget strong { display:block; font-size:12px; line-height:1.15; }
.widget span { font-size:9px; color:#6a5648; }
.backdrop { display:none; position:fixed; inset:0; background:rgba(20,12,8,.45); align-items:flex-start; justify-content:flex-start; padding:128px 16px 16px; z-index:30; }
.backdrop.open { display:flex; }
.box { width:min(360px,calc(100vw - 32px)); height:min(46vh,380px); max-height:calc(100vh - 48px); min-height:0; background:#fff; border-radius:18px; overflow:hidden; display:flex; flex-direction:column; box-shadow:0 20px 50px rgba(0,0,0,.28); }
.box-top { position:relative; background:#efe6d8; display:flex; justify-content:center; padding:8px 12px 4px; flex-shrink:0; }
.box-top img { width:64px; height:64px; border-radius:50%; object-fit:contain; object-position:center; display:block; background:#efe6d8; }
.close { position:absolute; top:6px; right:6px; border:0; background:rgba(255,255,255,.92); width:28px; height:28px; border-radius:50%; font-size:18px; cursor:pointer; }
.who { padding:4px 12px 2px; flex-shrink:0; }
.who strong { display:block; font-size:16px; }
.who em { font-style:normal; color:#6a5648; font-size:12px; }
.log { flex:1 1 auto; min-height:0; overflow-x:hidden; overflow-y:auto; padding:6px 12px 8px; display:flex; flex-direction:column; gap:8px; }
.bubble { max-width:88%; padding:8px 10px; border-radius:12px; line-height:1.35; font-size:14px; }
.them { background:#efe6d8; align-self:flex-start; }
.me { background:var(--eggplant); color:#fff; align-self:flex-end; }
form { display:flex; gap:8px; padding:8px 12px 12px; border-top:1px solid #eadfce; flex-shrink:0; }
form input { flex:1; border:1px solid #d5c6b2; border-radius:12px; padding:8px 10px; font:inherit; font-size:14px; }
form button, .book { border:0; border-radius:12px; background:var(--eggplant); color:#fff; padding:8px 12px; font:inherit; font-size:14px; cursor:pointer; }
form button.mic { background:var(--gold); color:#111; width:40px; height:40px; padding:0; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
form button.mic.on { background:#f8c038; box-shadow:0 0 0 3px rgba(255,198,63,.45); }
form button.mic svg { display:block; }
.book { display:block; text-align:center; text-decoration:none; margin:0 12px 8px; background:var(--gold); color:#111; font-weight:600; }
.hear { margin-top:8px; }
.hear span { display:block; font-size:13px; color:#6a5648; margin-bottom:4px; }
.hear audio { width:100%; height:36px; }
.sg-links { display:flex; flex-wrap:wrap; gap:8px; margin-top:8px; }
.sg-links a { display:inline-block; background:var(--gold); color:#111; text-decoration:none; border-radius:12px; padding:6px 10px; font-weight:600; font-size:13px; }
"""


PAGE_SLUGS = {
    "robert": "robert-11",
    "adie": "adie-11",
    "amber": "amber-11",
    "andre": "andre-11",
    "andrea": "andrea-11",
    "cheryl": "cheryl-11",
    "deneene-host": "deneene-11",
    "eve": "eve-11",
    "jill": "jill-11",
    "karen": "karen-11",
    "kate": "kate-11",
    "linn": "linn-11",
    "lisa-maria": "lisa-maria-11",
    "lisa-seyring": "lisa-seyring-11",
    "lita": "lita-11",
    "mary": "mary-11",
    "mother-lotus": "mother-lotus-11",
    "richard": "richard-11",
    "janel": "janel-akashic-records-angel-card-reader",
    "melissa": "melissa",
    "rose": "rose-passarella",
}


def pull_page(slug):
    url = "https://shopsacredground.com/" + slug.strip("/") + "/"
    try:
        req = urllib.request.Request(url, headers=UA)
        html = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
    except Exception:
        return ""
    parts = []
    for m in re.finditer(r'<div class="intro-text">.*?<p>(.*?)</p>', html, re.S):
        parts.append(re.sub("<[^>]+>", "", m.group(1)))
    for m in re.finditer(r'<div class="topic-card">.*?<h3>(.*?)</h3>.*?<p>(.*?)</p>', html, re.S):
        parts.append(re.sub("<[^>]+>", "", m.group(1)) + " — " + re.sub("<[^>]+>", "", m.group(2)))
    text = "\n".join(p.strip() for p in parts if p.strip())
    return ("FROM THEIR LIVE PAGE\n" + text) if text else ""


def grab(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        return
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        open(dest, "wb").write(r.read())


def page(title, body, who, label, photo, book, opener):
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Sandbox — {title}</title>
<style>{CSS}</style></head>
<body>
<div class="banner">SANDBOX ONLY — not on the live website</div>
{NAV}
<main>
{body}
</main>
<button class="widget" id="open" type="button">
  <img src="photos/{photo}" alt=""/>
  <div><strong>Chat with {label}</strong><span>Ask a question</span></div>
</button>
<div class="backdrop" id="backdrop">
  <div class="box" role="dialog">
    <div class="box-top">
      <img src="photos/{photo}" alt="{label}"/>
      <button class="close" id="close" type="button">×</button>
    </div>
    <div class="who"><strong>Chat with {label}</strong><em>Knows a fact sheet. Not a live session.</em></div>
    <div class="log" id="log"></div>
    <a class="book" href="{book}" target="_blank" rel="noopener">Open their real page</a>
    <form id="form"><input id="q" type="text" placeholder="Ask a question…" autocomplete="off"/><button type="button" class="mic" id="mic" aria-label="Use microphone" title="Use microphone"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" d="M12 14a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v5a3 3 0 0 0 3 3zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2z"/></svg></button><button type="submit">Send</button></form>
  </div>
</div>
<script>
const WHO={who!r};
const OPENER={opener!r};
const log=document.getElementById("log"); const q=document.getElementById("q");
const history=[{{role:"assistant",content:OPENER}}];
let primed=false;
function attachVoice(audio,text){{
  fetch("/speak",{{method:"POST",headers:{{"Content-Type":"application/json"}},body:JSON.stringify({{who:WHO,text}})}})
    .then(r=>r.ok?r.blob():null)
    .then(b=>{{if(b) audio.src=URL.createObjectURL(b);}});
}}
function add(t,w,voice,links){{
  const d=document.createElement("div"); d.className="bubble "+w;
  const p=document.createElement("div"); p.textContent=t; d.appendChild(p);
  if(w==="them" && links && links.length){{
    const row=document.createElement("div"); row.className="sg-links";
    links.forEach(function(L){{
      if(!L||!L.url||String(L.url).indexOf("https://shopsacredground.com/")!==0) return;
      const a=document.createElement("a"); a.href=L.url; a.textContent=L.label||"Open this page";
      row.appendChild(a);
    }});
    if(row.childNodes.length) d.appendChild(row);
  }}
  if(w==="them"){{
    const wrap=document.createElement("div"); wrap.className="hear";
    const note=document.createElement("span"); note.textContent="Press Play to hear me";
    const audio=document.createElement("audio"); audio.preload="none"; audio.controls=true; audio.setAttribute("playsinline","");
    wrap.appendChild(note); wrap.appendChild(audio); d.appendChild(wrap);
    if(voice===false) audio.dataset.text=t; else attachVoice(audio,t);
  }}
  log.appendChild(d); log.scrollTop=log.scrollHeight;
}}
add(OPENER,"them",false);
document.getElementById("open").onclick=()=>{{
  document.getElementById("backdrop").classList.add("open"); q.focus();
  if(!primed){{ primed=true; const a=log.querySelector("audio"); if(a&&a.dataset.text) attachVoice(a,a.dataset.text); }}
}};
document.getElementById("close").onclick=()=>document.getElementById("backdrop").classList.remove("open");
document.getElementById("backdrop").addEventListener("click",e=>{{if(e.target.id==="backdrop") e.currentTarget.classList.remove("open");}});
(function(){{
  var btn=document.getElementById("mic");
  var form=document.getElementById("form");
  if(!btn||!form) return;
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  var rec=null, on=false;
  function off(){{ on=false; btn.classList.remove("on"); btn.setAttribute("aria-pressed","false"); try{{ if(rec) rec.stop(); }}catch(err){{}} }}
  function send(){{
    var t=(q.value||"").trim(); if(!t) return;
    try{{ if(form.requestSubmit) form.requestSubmit(); else form.dispatchEvent(new Event("submit",{{cancelable:true,bubbles:true}})); }}catch(err){{}}
  }}
  btn.addEventListener("click", function(ev){{
    ev.preventDefault();
    if(!SR){{ q.placeholder="Type your question — this browser can't hear you"; q.focus(); return; }}
    if(on){{ off(); return; }}
    try{{
      rec=new SR(); rec.lang="en-US"; rec.interimResults=true; rec.continuous=false;
      rec.onresult=function(e){{
        try{{
          var t=""; for(var i=0;i<e.results.length;i++) t+=e.results[i][0].transcript;
          q.value=t;
          if(e.results[e.results.length-1].isFinal){{ off(); send(); }}
        }}catch(err){{ off(); }}
      }};
      rec.onend=function(){{ on=false; btn.classList.remove("on"); }};
      rec.onerror=function(){{ off(); }};
      on=true; btn.classList.add("on"); btn.setAttribute("aria-pressed","true");
      rec.start();
    }}catch(err){{ off(); q.placeholder="Type your question — the mic didn't start"; q.focus(); }}
  }});
}})();
document.getElementById("form").onsubmit=async e=>{{
  e.preventDefault(); const text=q.value.trim(); if(!text) return; q.value=""; add(text,"me"); history.push({{role:"user",content:text}});
  const thinking=document.createElement("div"); thinking.className="bubble them"; thinking.textContent="…"; log.appendChild(thinking);
  try {{
    const res=await fetch("/chat",{{method:"POST",headers:{{"Content-Type":"application/json"}},body:JSON.stringify({{who:WHO,messages:history}})}});
    const data=await res.json(); thinking.remove(); const reply=data.reply||data.error||"The box did not answer.";
    add(reply,"them",true,data.links); history.push({{role:"assistant",content:reply}});
  }} catch(err) {{ thinking.remove(); add("The sandbox box is not running.","them"); }}
}};
</script>
</body></html>
"""


def main():
    for pid, name, title, file, book, facts in PEOPLE:
        url = "https://shopsacredground.com/wp-content/uploads/" + file
        dest = os.path.join(PHOTO, file)
        try:
            grab(url, dest)
            print("ok", pid, os.path.getsize(dest))
        except Exception as e:
            print("FAIL photo", pid, e)
        page_bits = pull_page(PAGE_SLUGS.get(pid, pid + "-11"))
        sheet = (
            f"Sacred Ground sandbox fact sheet — {name}\n"
            f"This box is NOT the live person. It only knows this sheet.\n"
            f"Title: {title}\nBook/page: {book}\n"
            f"Place: Sacred Ground, 160 West Campbell Street, Arlington Heights. 847-749-3922.\n"
            f"{facts}\n"
            f"{page_bits}\n"
            "VOICE: Warm, specific, a little magnetic. Answer how THEIR session actually works.\n"
            "Make a person want to come in and book the real human. Do not default to call the store.\n"
            "Do not invent hours or prices. Do not pull cards or give a session.\n"
        )
        open(os.path.join(FACTS, pid + ".txt"), "w").write(sheet)

    open(os.path.join(FACTS, "deneene.txt"), "w").write(DENEENE_GUIDE)
    deneene_photo = "deneene-official-face.jpg"
    try:
        grab("https://shopsacredground.com/wp-content/uploads/deneene-official-face.jpg", os.path.join(PHOTO, deneene_photo))
        print("ok deneene-official-face")
    except Exception as e:
        print("FAIL photo deneene-official-face", e)

    circles = "".join(
        f'<a href="{pid}.html"><img src="photos/{fn}" alt="{name}"/>{name}</a>'
        for pid, name, title, fn, book, facts in PEOPLE
        if pid != "deneene-host"
    )

    mains = [
        ("index.html", "Home", "<h1>Home</h1><p>Sandbox stand-in for the live homepage. Chat with Deneene is top left.</p>"),
        ("library.html", "Library", "<h1>Library</h1><p>Sandbox stand-in for the Library. Ask Deneene about meditations, playlists, and listening.</p>"),
        ("observatory.html", "Observatory", "<h1>Observatory</h1><p>Sandbox stand-in for the Observatory. Ask Deneene about the daily look, monthly, and Library.</p>"),
        ("holistic.html", "Holistic Center", "<h1>Holistic Center</h1><p>Sandbox stand-in for the Holistic Center. Ask Deneene how to find a practitioner.</p>"),
        ("practitioners.html", "Practitioners & Modalities", f"<h1>Our Practitioners</h1><p>Click a circle to open that person’s sandbox page. Deneene’s bubble stays here. Their bubble is only on their page.</p><div class=\"circles\">{circles}</div>"),
        ("calendar.html", "Calendar", "<h1>Calendar</h1><p>Sandbox stand-in for the Events Calendar. Ask Deneene what the calendar is. She will not invent dates.</p>"),
    ]
    for fn, title, body in mains:
        open(os.path.join(ROOT, fn), "w").write(page(
            title, body, "deneene", "Deneene", deneene_photo,
            "https://shopsacredground.com/",
            "Hi, I'm Deneene — the owner of Sacred Ground. Ask me anything about the shop, the Observatory, the Library, who to book, or how a reading works.",
        ))

    for pid, name, title, file, book, facts in PEOPLE:
        slug = "deneene-11.html" if pid == "deneene-host" else f"{pid}.html"
        who = "deneene-host" if pid == "deneene-host" else pid
        open(os.path.join(ROOT, slug), "w").write(page(
            name,
            f"<h1>{name}</h1><p>{title}</p><p>Sandbox stand-in for their page. Only their bubble is here — not Deneene’s site guide.</p>",
            who, name, file, book,
            OPENERS.get(pid, f"Hi, I'm {name}. If you have any questions for me, I'm glad you're here. Let's find a time."),
        ))
    print("pages written")


if __name__ == "__main__":
    main()
