# Ask Deneene sandbox

This is the talking box another agent can copy. It is **not** the live website.

Repo: `dflorino/sacred-ground-marketing-autopilot`
Folder: `ai-knowledge-library/sandbox/`

The old local folder `assets/_week_show/oct_ideas/_hub-robert-sandbox/` stays gitignored (keys and photos). Do not commit those.

## Founder-approved look (Oct 12, 2026)

- Chat box: `315px` wide, `min(53vh, 465px)` tall (25% smaller than the 420×620 live start)
- Mic is a gold circle picture. Never the word Speak
- **Open their page** and the mic use website gold `#ffc63f` (same as Call Now)
- Send stays eggplant
- Press Play only. Never autoplay voice. Never auto-listen
- Address spoken as **160 West Campbell Street** (never W)

## Who appears where

- Deneene: header-nav pages only (Home, Calendar, Your Calendar, Shop, Observatory, Holistic Center, Practitioners & Modalities directory, Monthly, Library, Contact). Never Working Calendar, Staff Daily, consent forms, or individual `*-11` practitioner pages. Directory stays. Each practitioner page gets their own box later. The box floats and can be dragged.
- Lisa Maria: `lisa-maria-11` only. Her face. Her recorded take. Not Deneene’s voice
- BJ is not a practitioner right now. No Tam. No Tom Tewell
- Never name the banned tarot card

## Run it

```bash
cd ai-knowledge-library/sandbox
# keys stay local — never git
# .openrouter-local  = OpenRouter key
# .elevenlabs-local  = ElevenLabs key
SG_SANDBOX_PORT=8769 python3 serve.py
```

Open `http://127.0.0.1:8769/`

If 8766 is a stale `python -m http.server`, use another port.

## Brain

- Cards: `ai-knowledge-library/build_library.py` then rebuild JSON
- Pack: `ai-knowledge-library/pack_for_guide.py`
- Live-shaped PHP copy: `ai-knowledge-library/live-helper/ask-deneene.php` and `ask-lisa-maria.php`
- Always sandbox first. Never full-replace live Helper with an unproven file

## Do not

- Commit `.openrouter-local` or `.elevenlabs-local`
- Install an agent
- Put Deneene on practitioner pages
- Put Lisa Maria anywhere except her page
- Remake Oct 11 morning plates
