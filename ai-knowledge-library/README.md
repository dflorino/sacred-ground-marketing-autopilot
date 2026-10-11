# Sacred Ground knowledge library

Draft for review. Nothing here is installed on the website, and the guide is not turned on.

| Read this | Why |
|---|---|
| `01-DECISIONS.md` | What Deneene decided on October 11 |
| `voice/VOICE-BIBLE.md` | How the guide is allowed to sound |
| `INDEX.md` | Every card, by layer |
| `cards/REVIEW.md` | The spoken line and the link, for a fast read |
| `cards/*.json` | The import files |
| `questions/visitor-questions.json` | Questions mapped to cards |
| `live/DYNAMIC-DATA-MAP.md` | What must be looked up live |
| `reports/MISSING-INFORMATION.md` | What is still open |
| `00-AUDIT-INVENTORY.md` | How the site was mapped |

`build_library.py` rebuilds the JSON from the facts in that file. Edit the facts, then run it. Do not hand-edit the JSON and the script in two directions.

`pack_for_guide.py` picks the cards for one visitor question. The local Ask Deneene sandbox uses it. Nothing is installed on the website.

Layers: voice, knowledge, navigation, live. Membership is omitted on purpose. A card we do not display is refused on purpose, and spoken lines never name it.
