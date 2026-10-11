#!/usr/bin/env python3
"""Pack knowledge cards for the Ask Deneene sandbox. Not live WordPress."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
CARDS_PATH = ROOT / "cards" / "all-cards.json"
QUESTIONS_PATH = ROOT / "questions" / "visitor-questions.json"
EVENTS_PATH = REPO / "data" / "cache" / "live_events.json"
CHICAGO = ZoneInfo("America/Chicago")

ALWAYS = (
    "SG-VOICE-IDENTITY",
    "SG-RULE-NO-DEATH",
    "SG-KNOW-ABOUT",
    "SG-KNOW-VISIT",
    "SG-PRAC-DENEENE",
)

EVENT_HINTS = (
    "today",
    "tomorrow",
    "tonight",
    "happening",
    "event",
    "calendar",
    "this week",
    "weekend",
    "meditation",
    "educational",
    "reiki share",
    "fair",
    "besom",
    "who is in",
    "who's in",
    "open today",
    "schedule",
)

STOP = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "am",
    "i",
    "im",
    "i'm",
    "me",
    "my",
    "you",
    "your",
    "we",
    "do",
    "does",
    "what",
    "who",
    "how",
    "where",
    "when",
    "can",
    "to",
    "for",
    "of",
    "and",
    "or",
    "in",
    "on",
    "at",
    "it",
    "this",
    "that",
    "with",
    "about",
}

_CARDS = None
_BY_ID = None
_QUESTIONS = None


def _load():
    global _CARDS, _BY_ID, _QUESTIONS
    if _CARDS is None:
        _CARDS = json.loads(CARDS_PATH.read_text())
        _BY_ID = {c["card_id"]: c for c in _CARDS}
        _QUESTIONS = json.loads(QUESTIONS_PATH.read_text())
    return _CARDS, _BY_ID, _QUESTIONS


def _tokens(text: str) -> set[str]:
    return {
        t
        for t in re.findall(r"[a-z0-9']+", (text or "").lower())
        if t not in STOP and len(t) > 1
    }


def _score(card: dict, question: str, q_tokens: set[str]) -> int:
    q = (question or "").lower()
    score = 0
    for kw in card.get("keywords") or []:
        k = str(kw).lower().strip()
        if not k:
            continue
        if k in q:
            score += 10 + min(len(k), 12)
    for vq in card.get("visitor_questions") or []:
        v = str(vq).lower()
        if v == q or v in q or q in v:
            score += 24
        overlap = len(q_tokens & _tokens(v))
        if overlap:
            score += overlap * 3
    title = str(card.get("title") or "").lower()
    if title and title in q:
        score += 16
    score += len(q_tokens & _tokens(title)) * 2
    score += len(q_tokens & _tokens(card.get("purpose") or ""))
    return score


def select_cards(question: str, extra_ids: list[str] | None = None, limit: int = 10):
    cards, by_id, questions = _load()
    q = (question or "").strip()
    q_tokens = _tokens(q)
    picked: list[str] = []

    def add(cid: str):
        if cid in by_id and cid not in picked:
            picked.append(cid)

    for cid in ALWAYS:
        add(cid)
    for cid in extra_ids or []:
        add(cid)

    for row in questions:
        rq = str(row.get("question") or "").lower()
        if not rq:
            continue
        if rq == q.lower() or rq in q.lower() or q.lower() in rq:
            add(row.get("card_id") or "")
        elif len(q_tokens & _tokens(rq)) >= 2:
            add(row.get("card_id") or "")

    ranked = sorted(
        ((_score(c, q, q_tokens), c["card_id"]) for c in cards),
        reverse=True,
    )
    for score, cid in ranked:
        if score < 6:
            break
        add(cid)
        if len(picked) >= len(ALWAYS) + limit:
            break

    related = []
    for cid in list(picked):
        for other in (by_id[cid].get("related_cards") or [])[:2]:
            related.append(other)
    for cid in related:
        if len(picked) >= len(ALWAYS) + limit + 4:
            break
        add(cid)
    return [by_id[cid] for cid in picked]


def _speak_clock(hm: str) -> str:
    try:
        hour, minute = hm.split(":")
        hour = int(hour)
    except ValueError:
        return hm
    suffix = "AM" if hour < 12 else "PM"
    hour12 = hour % 12 or 12
    if minute == "00":
        return f"{hour12} {suffix}"
    return f"{hour12}:{minute} {suffix}"


def live_events_slice(days: int = 7) -> str:
    fail = (
        "LIVE CALENDAR: lookup failed. Tell them that's on Calendar in the menu. "
        "Do not read a website address."
    )
    if not EVENTS_PATH.exists():
        return fail
    try:
        data = json.loads(EVENTS_PATH.read_text())
    except json.JSONDecodeError:
        return fail
    today = datetime.now(CHICAGO).date()
    end = today + timedelta(days=days)
    lines = []
    seen = set()
    for ev in data.get("events") or []:
        raw = str(ev.get("start_date") or "")[:19]
        try:
            start = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S").date()
        except ValueError:
            continue
        if start < today or start > end:
            continue
        end_raw = str(ev.get("end_date") or "")[11:16]
        start_hm = raw[11:16]
        title = " ".join(str(ev.get("title") or "Event").split())
        key = (start.isoformat(), start_hm, title)
        if key in seen:
            continue
        seen.add(key)
        when = start.strftime("%A, %B %-d")
        clock = _speak_clock(start_hm)
        if end_raw:
            clock += f" to {_speak_clock(end_raw)}"
        lines.append(f"- {when} · {clock} · {title}")
    if not lines:
        return (
            "LIVE CALENDAR (next 7 Chicago days): nothing in the cache. "
            "Say you cannot see the live list. That's on Calendar in the menu. "
            "Do not read a website address."
        )
    return (
        "LIVE CALENDAR from The Events Calendar cache. America/Chicago. "
        "No prices. Do not invent a seat count or a cost. "
        "Tell them they can find this on Calendar in the menu. "
        "Do not read a website address.\n"
        + "\n".join(lines)
    )


def format_card(card: dict) -> str:
    nav = card.get("navigation") or {}
    where = nav.get("desktop") or "the menu"
    return (
        f"### {card['card_id']} — {card.get('title')}\n"
        f"{card.get('answer')}\n"
        f"Say it like: {card.get('voice_response')}\n"
        f"On the nav: {where}"
    )


def pack_prompt(question: str, who: str = "deneene") -> str:
    extra = []
    if who == "deneene-host":
        extra.append("SG-VOICE-GRIEF")
    cards = select_cards(question, extra_ids=extra)
    body = "\n\n".join(format_card(c) for c in cards)
    want_events = True
    q = (question or "").lower()
    if q and not any(h in q for h in EVENT_HINTS):
        want_events = any(
            w in q for w in ("today", "tomorrow", "event", "calendar", "open")
        )
    live = live_events_slice() if (want_events or not q) else ""
    live_block = ("\n\n" + live) if live else ""
    return (
        "You are the Ask Deneene box on a Sacred Ground sandbox page. "
        "Not live WordPress. Not a private session or a reading.\n"
        "Speak in Deneene's house voice: warm, plain, curious, practical. "
        "Inspired by Deneene Florino, who founded this place. "
        "If they ask whether they are talking to Deneene in the room, use SG-VOICE-IDENTITY. "
        "Do not invent her memories, her sessions, or private stories.\n"
        "Answer ONLY from the cards below and the live calendar slice when it is present. "
        "Prefer the spoken line. "
        "Never read, type, or spell a website, a /book/ link, or shopsacredground.com. "
        "Tell them they can find it on our nav. "
        "Desktop nav: Calendar, Shop, Observatory, Holistic Center, Monthly, Library, Contact. "
        "A named person is Holistic Center, then Practitioners, then their name. "
        "Events are Calendar. The newsletter is Monthly.\n"
        "Do not default to “call the store” when a card already has the answer.\n"
        "If they ask for a tarot card Sacred Ground does not display, do not name it. "
        "Say it is not a card we use here, and offer another card or Observatory in the menu.\n"
        "Never mention Tam, Tom Tewell, or BJ. BJ is not a practitioner right now.\n"
        "Leave membership, Inner Circle, and Member Shop out. "
        "The menu item is Monthly. Call it Monthly, not the newsletter.\n"
        "Do not invent hours, prices, stock, or a time that is not on a booking page. "
        "Do not say you booked, charged, registered, or shipped anything.\n"
        "Address is always 160 W Campbell Street, Arlington Heights, IL 60005. "
        "Phone 847-749-3922. Working Calendar is staff only — never send a visitor there.\n"
        "If the cards do not cover it, say so and name the closest menu item, or the phone.\n\n"
        f"{body}{live_block}"
    )


def last_user_text(messages: list) -> str:
    for row in reversed(messages or []):
        if (row or {}).get("role") == "user":
            return str(row.get("content") or "")
    return ""


if __name__ == "__main__":
    sample = "What's happening today?"
    packed = pack_prompt(sample)
    print("cards", packed.count("### "))
    print("has besom", "Besom" in packed)
    print("chars", len(packed))
