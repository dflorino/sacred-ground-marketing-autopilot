# Cinematic shorts (Threads / Reels / Shorts / TikTok)

Founder KEEP look: **Fri Sep 18, 2026** — `sun-inside-v4` (no leaves).
These are **not** cartoon Galactic Explorers, **not** HeyGen talking-head, **not** TopView storyboard.

## What “that” is

1. An **idea-first still** (9:16). The picture *is* the idea.
2. A **second still** for where the camera ends.
3. **Image-to-video** that travels from first frame to last frame (8–10s).
4. Founder **watches the MP4 on this Mac** (`open` the file). Nothing posts until she says.

Bar plate: nested suns living inside a cosmic body, camera dives in. **No maple / no foliage** (Founder Sep 18).

## KEEP — v4 (run on social soon)

| | |
|---|---|
| **Look** | Cosmic body in a night lake. Nested solar system in the chest (spiral sun + smaller orbiting sun + tiny ember world). Camera walks in, then **into** the chest. Ends inside the spiral. **No leaves.** |
| **MP4 media** | **28363** |
| **MP4 URL** | `https://shopsacredground.com/wp-content/uploads/sg-cinematic-short-sun-inside-v4.mp4` |
| **Admin** | `https://shopsacredground.com/wp-admin/upload.php?item=28363` |
| **Start still** | media **28361** `sg-cinematic-v4-start-no-leaves.jpg` |
| **End still** | media **28360** `sg-cinematic-v4-end-no-leaves.jpg` |
| **Local play** | `assets/cinematic-shorts/sg-cinematic-short-sun-inside-v4.mp4` (gitignored) or `PLAY-V4.html` next to it |
| **Status** | In the media library. **Not scheduled.** Founder will run it on SM soon. |

Do **not** use v1 (frozen still) or v2 (weaker mannequin). v3 had leaves — retired.

## Ready — v6 (we are all connected)

| | |
|---|---|
| **Look** | Wet night street. A gold thread leaves a cup, finds a person, then the whole field — people, Earth, stardust — is one web. |
| **MP4 media** | **28367** |
| **MP4 URL** | `https://shopsacredground.com/wp-content/uploads/sg-cinematic-short-connected-v6-1.mp4` |
| **Start still** | media **28365** `sg-cinematic-v6-start-3d-thread.jpg` |
| **End still** | media **28366** `sg-cinematic-v6-end-one-field.jpg` |
| **Local play** | `assets/_week_show/sg-cinematic-short-connected-v6.mp4` + `PLAY-V6.html` |
| **Status** | In the library. **Not published.** Founder watches on this Mac first. |

Motion check Fri Sep 18: 10.04s, start / mid / end are three different pictures.

## Next series — night storefront (Founder Fri Sep 18)

After connected: **the real shop at night**, a new sky each short.

Same locked facade every time (eggplant awning, tan stone, white `SACRED GROUND` with a space — never a hyphen). Only the sky changes.

| Short | Sky | Still we already have? |
|---|---|---|
| **sky opens** (first) | Quiet stars tear open into galaxies | New stills `v7` start **28369** + end local |
| Orion | Orion’s belt / hunter | Yes — `fall_store_orion_rising` (still only) |
| Northern lights | Aurora over the shop | Yes — aurora / teal-copper stills |
| Fall night | Amber harvest night, not daytime sun | Yes — `sg-night-fall.png` |
| Rain | Rain + neon puddles | Yes — rain puddle stills |
| Lightning | Storm opens the sky | No — new |
| Deep night | Milky Way field, shop still the anchor | Partial |

These are **moving shorts**, not the 7pm week-ahead still. Do not steal a used `image_usage` URL. Do not invent a fantasy shop.

## How to make the next one

### 1. Still pair (9:16)

- Generate two stills: **start** (wide world) + **end** (where the camera arrives).
- One new visual thought. Not Magritte / Einstein rotation. Not generic mystic starter-pack (bowls, healing hands, Flower of Life, Akashic prop books).
- **No leaves / no plants** unless Founder asks.
- Jewel tones. No beige / muddy purple sludge.
- No baked-in campaign text (“week-ahead”, shop URL). Caption later.

### 2. Get stills onto the shop disk

Upload JPEGs to WP (or write under `wp-content/uploads/`). Cloudflare **403s** OpenRouter if you only pass a shopsacredground.com URL. Feed the video API a **data URI** from the file on disk.

### 3. Image-to-video

Wallet OpenRouter key (`ml_openrouter_key`). Never print the key. Image $12 cap is stills only — video uses the wallet.

```
POST https://openrouter.ai/api/v1/videos
model: kwaivgi/kling-v3.0-pro
duration: 10
resolution: 720p
aspect_ratio: 9:16
generate_audio: false
frame_images:
  - first_frame  (data:image/jpeg;base64,...)
  - last_frame   (data:image/jpeg;base64,...)
```

Motion prompt: name the **journey** (push in, enter the chest, suns rotate, second sun orbits). Say **obvious continuous motion**. Ban leaves if they must stay gone. Ban freeze-frame, extra people, on-image text.

Poll `GET /api/v1/videos/{id}` until `completed`. Download:

```
GET /api/v1/videos/{id}/content?index=0
Authorization: Bearer <wallet>
```

Save as `wp-content/uploads/sg-cinematic-short-<name>.mp4` and `wp media import` so it lands in the library.

Cost ballpark: Kling 3 pro ~$0.11/s → ~$1.10 for 10s.

### 4. Show Founder (this is the part we got wrong)

**Do not** use the Cursor / Glass browser as the only player. She cannot see those tabs.

On this Mac:

```bash
open /absolute/path/to/the.mp4
```

That opens **QuickTime** (or her default player). Also write a tiny `PLAY.html` beside the file (`<video src="that.mp4">`) and `open` that for Safari/Chrome.

Prove motion before you call it done: start / mid / end must be different pictures. If it is an 8-second still, throw it out.

### 5. Social later (not auto)

When she says send:

- Same MP4 across Facebook + Instagram + TikTok + YouTube Shorts + Threads (brand accounts).
- FB Story still needs **Zernio CDN** (`media.zernio.com`) — WP URLs 403 Meta. See `REEL-POSTING-SCHEDULE.md`.
- Thumbnail = a frame from **this** KEEP clip, not a new face.
- Never-reuse still applies to stills pulled from the short.

## Wrong tools

| Tool | Why not |
|---|---|
| TopView `storyboard/queue` | Cartoon talking-head adventure (Deneene / Luca / Kobi) |
| HeyGen | Talking Deneene |
| Morning flyer Magritte / Einstein invent | Flat daily template |
| Living Worlds / Remotion | Layer loops, different job |
| Cursor browser tab only | Founder does not see it |

## Credits

Before still gen: OpenRouter Image key. If `$12` cap at `$0` and wallet has funds, copy wallet onto the Image key (never print keys). Video bills the wallet.

## Config

IDs and status: `config/cinematic_shorts.json`
Agent rule: `.cursor/rules/cinematic-shorts.mdc`
