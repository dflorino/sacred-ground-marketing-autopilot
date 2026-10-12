#!/usr/bin/env python3
"""Local-only Hub sandbox. Not live WordPress. Keys are never printed."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import importlib.util
import json
import os
import re
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(ROOT, ".openrouter-local")
VOICE_KEY_PATH = os.path.join(ROOT, ".elevenlabs-local")
FACTS_DIR = os.path.join(ROOT, "facts")
VOICE_DIR = os.path.join(ROOT, "voice")
PORT = int(os.environ.get("SG_SANDBOX_PORT", "8766"))
DENEENE_VOICE = "vSbSsSjeNo7FMkmvwZJs"
LIBRARY = os.path.abspath(os.path.join(ROOT, "..", "pack_for_guide.py"))
_GUIDE = None


def load_guide():
    global _GUIDE
    if _GUIDE is None:
        spec = importlib.util.spec_from_file_location("pack_for_guide", LIBRARY)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _GUIDE = mod
    return _GUIDE

# Premade ElevenLabs voices for everyone except Deneene (her reel voice).
VOICES = {
    "deneene": DENEENE_VOICE,
    "deneene-host": DENEENE_VOICE,
    "robert": "JBFqnCBsd6RMkjVDRZzb",
    "adie": "pFZP5JQG7iQjIQuC4Bku",
    "amber": "EXAVITQu4vr4xnSDxMaL",
    "andre": "IKne3meq5aSn9XLyUdCD",
    "andrea": "cgSgspJ2msm6clMCkdW9",
    "cheryl": "XrExE9yKIg1WjnnlVkGX",
    "eve": "EXAVITQu4vr4xnSDxMaL",
    "jill": "jsCqWAovK2LkecY7zXl4",
    "karen": "pFZP5JQG7iQjIQuC4Bku",
    "kate": "Xb7hH8MSUJpSbSDYk0k2",
    "linn": "oWAxZDx7w5VEj9dCyTzz",
    "lisa-maria": "21m00Tcm4TlvDq8ikWAM",
    "lisa-seyring": "pFZP5JQG7iQjIQuC4Bku",
    "lita": "EXAVITQu4vr4xnSDxMaL",
    "mary": "ThT5KcBeYPX3keUQqHPh",
    "mother-lotus": "z9fAnlkpzviPz146aGWa",
    "richard": "onwK4e9ZLuTAKqWW03F9",
    "janel": "EXAVITQu4vr4xnSDxMaL",
    "melissa": "cgSgspJ2msm6clMCkdW9",
    "rose": "pFZP5JQG7iQjIQuC4Bku",
}


def load_facts(who):
    safe = "".join(c for c in (who or "deneene") if c.isalnum() or c in "-_")
    path = os.path.join(FACTS_DIR, safe + ".txt")
    if os.path.exists(path):
        return open(path).read()
    return "Sacred Ground sandbox. Do not invent hours or prices. Phone 847-749-3922."


def system_prompt(who, messages=None):
    if who in ("deneene", "deneene-host"):
        guide = load_guide()
        question = guide.last_user_text(messages or [])
        return guide.pack_prompt(question, who=who)
    if who == "lisa-maria":
        user_turns = sum(1 for m in (messages or []) if (m or {}).get("role") == "user")
        if user_turns < 2:
            booking = (
                "They just started chatting. Answer the question they asked. "
                "Do not mention booking, finding a time, or the Book a time button yet.\n"
            )
        else:
            booking = (
                "You have talked a little. You may now say they can book a time with you. "
                "One short humble line. Point them to the Book a time button. Do not sound salesy.\n"
            )
        return (
            "You are Lisa Maria's talking box on her Sacred Ground page only.\n"
            "Speak as Lisa Maria. Humble. Warm. Inviting. Not a performance.\n"
            "The first hello is already on the screen. Never repeat it. "
            "Never start again with Hi I'm Lisa Maria, I do tarot, let's find a time, or let's chat.\n"
            "Answer the question they just asked.\n"
            + booking
            + "Never say you are not here for small talk. Never sound curt or dismissive.\n"
            "This is NOT the live reading. Do not pull cards. Do not invent a spread, a future, hours, or a price.\n"
            "Do not read a website. Do not give email, PayPal, Venmo, Cash App, or a price.\n"
            "Not Lisa the astrologer. Not Lisa Seyring. Phone 847-749-3922 only if no time is open.\n"
            "We are not doctors. Say that only if they ask whether a session treats a symptom or a diagnosis.\n\n"
            + load_facts(who)
        )
    return (
        "You are a sandbox talking-box on a Sacred Ground page.\n"
        "You are NOT the live person and you are not doing a real session.\n"
        "Use ONLY the fact sheet below. Answer from it. Give a real explanation of THEIR style.\n"
        "Be warm and specific so a visitor wants to book the real person in the building.\n"
        "Never invent a practitioner. There is no Tam and no Tom Tewell. BJ is not on the team right now.\n"
        "Do not invent hours, prices, or spreads.\n"
        "Do not default to “call the store” when the sheet already has the answer.\n"
        "Phone 847-749-3922 only when they need a live person, a time not on the sheet, or a booking confirmation.\n\n"
        + load_facts(who)
    )


def drop_repeated_hello(who, reply, messages):
    if (who or "") != "lisa-maria":
        return reply
    if not any((m or {}).get("role") == "user" for m in (messages or [])):
        return reply
    text = (reply or "").strip()
    low = text.lower()
    if not low.startswith("hi, i'm lisa maria") and not low.startswith("hi i'm lisa maria"):
        return text
    parts = text.replace("? ", "?|").replace(". ", ".|").replace("! ", "!|").split("|")
    kept = []
    skipping = True
    for part in parts:
        bit = part.strip()
        if not bit:
            continue
        check = bit.lower()
        if skipping and (
            "i'm lisa maria" in check
            or "i do tarot" in check
            or "let's find a time" in check
            or "let's chat" in check
        ):
            continue
        skipping = False
        kept.append(bit)
    return " ".join(kept).strip() or text


def load_key():
    if os.path.exists(KEY_PATH):
        return open(KEY_PATH).read().strip()
    return os.environ.get("OPENROUTER_API_KEY", "").strip()


def load_voice_key():
    if os.path.exists(VOICE_KEY_PATH):
        return open(VOICE_KEY_PATH).read().strip()
    return os.environ.get("ELEVENLABS_API_KEY", "").strip()


def chat(messages, who="deneene"):
    key = load_key()
    if not key:
        return "The sandbox has no key. Jr needs to start this again."
    body = {
        "model": "openai/gpt-4.1-mini",
        "messages": [{"role": "system", "content": system_prompt(who, messages)}]
        + messages[-12:],
        "max_tokens": 700,
        "temperature": 0.4,
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "HTTP-Referer": "http://127.0.0.1:8766",
            "X-Title": "SG Hub sandbox",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        data = json.loads(r.read())
    reply = data["choices"][0]["message"]["content"].strip()
    return drop_repeated_hello(who, reply, messages)


def speak(who, text):
    key = load_voice_key()
    if not key:
        return None
    spoken = re.sub(r"\b160\s+W\.?\s+Campbell\b", "160 West Campbell", text or "", flags=re.I)
    spoken = " ".join(spoken.split())[:700]
    if not spoken:
        return None
    os.makedirs(VOICE_DIR, exist_ok=True)
    voice = VOICES.get(who or "deneene", DENEENE_VOICE)
    if (who or "") == "lisa-maria":
        settings = {
            "stability": 0.52,
            "similarity_boost": 0.78,
            "style": 0.12,
            "speed": 0.88,
        }
    else:
        settings = {"stability": 0.42, "similarity_boost": 0.78}
    digest = hashlib.sha1(
        (voice + "\n" + json.dumps(settings, sort_keys=True) + "\n" + spoken).encode()
    ).hexdigest()
    path = os.path.join(VOICE_DIR, digest + ".mp3")
    if os.path.exists(path) and os.path.getsize(path) > 200:
        return open(path, "rb").read()
    body = {
        "text": spoken,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": settings,
    }
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/text-to-speech/" + voice,
        data=json.dumps(body).encode(),
        headers={
            "xi-api-key": key,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            audio = r.read()
    except urllib.error.HTTPError as err:
        if (who or "") == "lisa-maria" and "speed" in settings:
            settings.pop("speed", None)
            body["voice_settings"] = settings
            req = urllib.request.Request(
                "https://api.elevenlabs.io/v1/text-to-speech/" + voice,
                data=json.dumps(body).encode(),
                headers={
                    "xi-api-key": key,
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=45) as r:
                    audio = r.read()
            except urllib.error.HTTPError:
                print("lisa-maria voice error", err.code, flush=True)
                return None
        else:
            return None
    if audio:
        open(path, "wb").write(audio)
    return audio


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, fmt, *args):
        path = str(args[0] if args else "")
        if "/chat" in path or "/speak" in path:
            print("box")
        else:
            super().log_message(fmt, *args)

    def _json(self, out, code=200):
        raw = json.dumps(out).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length) or b"{}")
        if self.path == "/chat":
            messages = payload.get("messages") or []
            who = payload.get("who") or "deneene"
            try:
                reply = chat(messages, who)
                payload = {"reply": reply}
                if who in ("deneene", "deneene-host"):
                    asked = ""
                    for row in reversed(messages or []):
                        if (row or {}).get("role") == "user":
                            asked = str((row or {}).get("content") or "")
                            break
                    payload["links"] = load_guide().pressable_links(asked)
                self._json(payload)
            except Exception:
                self._json({"error": "The box could not answer just now."})
            return
        if self.path == "/speak":
            who = payload.get("who") or "deneene"
            text = payload.get("text") or ""
            audio = speak(who, text)
            if not audio:
                self.send_error(503)
                return
            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.send_header("Content-Length", str(len(audio)))
            self.end_headers()
            self.wfile.write(audio)
            return
        self.send_error(404)


if __name__ == "__main__":
    print(f"Robert Hub sandbox  http://127.0.0.1:{PORT}/")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
