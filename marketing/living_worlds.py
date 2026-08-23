"""Morning Living Worlds — prompts, static covers, movement briefs."""
from __future__ import annotations

import os
from datetime import date
from typing import Any, Dict, List, Optional, Sequence

from .ingest import parse_tec_datetime
from .models import Event
from .morning_flyers import (
    ASSETS_DIR,
    LOGO_PATH,
    PHONE,
    WEBSITE,
    build_flyer_copy,
    pick_events_for_flyer,
)
from .paths import CONFIG_DIR, ROOT, _load_json, write_json

LIVING_WORLDS_PATH = os.path.join(CONFIG_DIR, "morning_living_worlds.json")
LIVING_WORLDS_DATA = os.path.join(ROOT, "data", "living_worlds")

FEED_W = 1080
FEED_H = 1350
ART_H = 980
FOOTER_H = 130
INFO_H = FEED_H - ART_H - FOOTER_H  # 240


def load_living_worlds_config() -> Dict[str, Any]:
    if os.path.isfile(LIVING_WORLDS_PATH):
        return _load_json(LIVING_WORLDS_PATH)
    return {}


def living_world_style_meta(style_id: str) -> Dict[str, Any]:
    cfg = load_living_worlds_config()
    meta = (cfg.get("styles") or {}).get(style_id)
    return dict(meta) if isinstance(meta, dict) else {}


def _host_from_title(title: str) -> str:
    t = title or ""
    for sep in (" with ", " With ", " w/ ", " | ", ": "):
        if sep in t:
            return t.split(sep)[-1].strip()[:48]
    return ""


def _reader_line(events: Sequence[Event]) -> str:
    picked = pick_events_for_flyer(events)
    if not picked:
        return "Readers & practitioners today"
    hosts: List[str] = []
    for ev in picked:
        host = _host_from_title(ev.title)
        if host and host not in hosts:
            hosts.append(host)
        elif ev.title and ev.title not in hosts:
            hosts.append(_short(ev.title))
    return " · ".join(hosts[:3])


def _short(s: str, n: int = 42) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def _event_lines(events: Sequence[Event]) -> List[str]:
    lines: List[str] = []
    for ev in pick_events_for_flyer(events):
        st = parse_tec_datetime(ev.start_date)
        en = parse_tec_datetime(ev.end_date)
        t0 = st.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")
        t1 = en.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")
        title = _short(ev.title, 36)
        lines.append(f"{title}")
        lines.append(f"{t0} – {t1}")
    return lines


def build_living_world_prompt(
    day: date,
    style_id: str,
    events: Sequence[Event],
    *,
    for_ai_scene_only: bool = False,
) -> str:
    """Full prompt for mlimg scene OR scene-only when PIL adds text."""
    meta = living_world_style_meta(style_id)
    label = meta.get("label") or style_id
    brief = str(meta.get("prompt_brief") or "").strip()
    movement = str(meta.get("movement_summary") or "").strip()
    copy = build_flyer_copy(day, events)
    weekday = day.strftime("%A").upper()
    reader = _reader_line(events)

    anchors = (
        "SIX ANCHORS (all visible in scene): clear quartz or amethyst crystal point, "
        "finished silver pendant necklace on chain, burning beeswax candle with flame, "
        "incense stick with curling smoke, tarot/reader card at end of track, "
        "fresh coffee in ceramic mug with steam."
    )
    scene = (
        f"MORNING LIVING WORLD — '{label}'. {brief} "
        f"{anchors} "
        "Handcrafted shop-made tactile energy: warm copper, wood, jewel tones, "
        "eggplant purple Sacred Ground accents. Colorful bright engaging — NOT generic "
        "mystic AI purple fog, NOT floating singing bowls, NOT Canva template. "
        "Photorealistic miniature / tabletop craft photography, shallow depth of field, "
        "morning window light with golden highlights."
    )
    if for_ai_scene_only:
        return (
            f"{scene} "
            "NO readable text, NO letters, NO numbers, NO watermark — pure illustration "
            "only. Leave clean cream negative space along the bottom 25% for typography overlay. "
            "Square composition centered on the machine mechanism."
        )

    from . import social_proof as sp

    pride = sp.designed_in_generation_brief(
        f"living|{day.isoformat()}|{style_id}",
        day=day,
        surface="morning",
        campaign="today",
        force_option="B",
    )
    events_bit = ""
    ev_lines = _event_lines(events)
    if ev_lines:
        events_bit = " Events: " + " | ".join(ev_lines[:4]) + "."

    return (
        f"{scene} "
        f"Readable info panel area for: GOOD MORNING, {weekday} · {day.strftime('%B').upper()} {day.day}, "
        f"Sacred Ground, Today's reader: {reader}.{events_bit} "
        f"Footer: {WEBSITE} and {PHONE}. Circular Sacred Ground sun-face logo. "
        f"{pride} NO dollar prices on image."
        + (f" Movement reference (for video loop): {movement}." if movement else "")
    )


def build_movement_storyboard(
    day: date,
    style_id: str,
    events: Sequence[Event],
) -> str:
    """7-second seamless loop storyboard for MP4 production."""
    meta = living_world_style_meta(style_id)
    label = meta.get("label") or style_id
    movement = str(meta.get("movement_summary") or "").strip()
    reader = _reader_line(events)
    weekday = day.strftime("%A")

    return f"""# Movement storyboard — {label}
**Date:** {day.isoformat()} ({weekday}) · **Reader:** {reader}
**Loop:** 7.0s seamless · **Deliverables:** 1080×1350 feed + 1080×1920 vertical

## Timeline

| Time | Action | Audio |
|------|--------|-------|
| 0.0–1.0s | Hold still — machine at rest, candle unlit, OPEN sign back | silent |
| 1.0–2.0s | Crystal sphere rolls down copper track (single smooth roll) | silent |
| 2.0–2.8s | Coffee beans release; kettle tilts; slow pour into mug; steam rises | silent |
| 2.8–3.5s | Small gear turns; candle flame ignites; incense smoke begins | silent |
| 3.5–4.5s | Silver pendant on chain swings once; light catch on crystal | silent |
| 4.5–5.5s | Reader tarot card flips face-up at track end | silent |
| 5.5–6.5s | Wooden OPEN sign flips to face camera | silent |
| 6.5–7.0s | Coffee steam drifts across frame — matches 0.0s steam position for loop | silent |

## Moving elements (5 max)
1. Crystal roll
2. Coffee pour + steam
3. Candle ignite + incense smoke
4. Pendant swing
5. Card flip + OPEN sign

## Static overlay (burned on all frames)
- Bottom info band + footer from static cover PNG
- Do NOT animate typography

## Production notes
- Seedance / TopView from static cover as first frame OR image-to-video on hero plate
- 480p proof before 1080p
- Same cast/objects as static cover — continuity for email thumbnail

## Sequence reference
{movement}
"""


def render_static_cover(
    day: date,
    style_id: str,
    events: Sequence[Event],
    art_path: str,
    out_path: str,
) -> str:
    """Composite 1080×1350 feed cover: AI art + readable info band + footer."""
    from PIL import Image, ImageDraw

    copy = build_flyer_copy(day, events)
    reader = _reader_line(events)
    weekday = day.strftime("%A").upper()

    art = Image.open(art_path).convert("RGB")
    art = art.resize((FEED_W, ART_H), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (FEED_W, FEED_H), (250, 245, 232))
    canvas.paste(art, (0, 0))

    draw = ImageDraw.Draw(canvas)
    cream = (250, 245, 232)
    ink = (28, 22, 40)
    eggplant = (58, 28, 72)
    gold = (180, 140, 50)

    # Info band
    y_info = ART_H
    draw.rectangle((0, y_info, FEED_W, y_info + INFO_H), fill=cream)
    draw.line((40, y_info + 4, FEED_W - 40, y_info + 4), fill=gold, width=2)

    serif_b = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
    serif = "/System/Library/Fonts/Supplemental/Georgia.ttf"
    sans = "/System/Library/Fonts/Helvetica.ttc"
    script = "/System/Library/Fonts/Supplemental/SnellRoundhand.ttc"

    def font(path: str, size: int):
        from PIL import ImageFont

        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            from PIL import ImageFont

            return ImageFont.load_default()

    y = y_info + 18
    draw.text((48, y), "GOOD MORNING", font=font(serif_b, 44), fill=eggplant)
    y += 52
    draw.text(
        (48, y),
        f"{weekday} · {day.strftime('%B').upper()} {day.day} · Sacred Ground",
        font=font(sans, 24),
        fill=ink,
    )
    y += 36
    draw.text((48, y), f"Today's reader · {reader}", font=font(serif_b, 28), fill=ink)
    y += 40

    for ev in pick_events_for_flyer(events):
        st = parse_tec_datetime(ev.start_date)
        en = parse_tec_datetime(ev.end_date)
        t0 = st.strftime("%I:%M %p").lstrip("0")
        t1 = en.strftime("%I:%M %p").lstrip("0")
        title = _short(ev.title, 40)
        draw.text((48, y), title, font=font(serif, 26), fill=ink)
        y += 32
        draw.text((48, y), f"{t0} – {t1} · Arlington Heights", font=font(sans, 22), fill=(80, 70, 90))
        y += 34

    if copy.get("empty_day"):
        draw.text(
            (48, y),
            "Crystals · readings · quiet wonder — come browse",
            font=font(serif, 24),
            fill=ink,
        )

    # Pride + CTA
    pride_y = y_info + INFO_H - 44
    draw.text(
        (48, pride_y),
        "Chicagoland's #1 Crystal Shop & Holistic Center",
        font=font(sans, 20),
        fill=eggplant,
    )
    draw.text(
        (FEED_W - 280, pride_y),
        "Book · Visit · Explore",
        font=font(script if os.path.isfile(script) else serif, 28),
        fill=gold,
    )

    # Footer band
    y_foot = FEED_H - FOOTER_H
    draw.rectangle((0, y_foot, FEED_W, FEED_H), fill=cream)
    draw.line((40, y_foot + 6, FEED_W - 40, y_foot + 6), fill=gold, width=2)

    if os.path.isfile(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        lw = int(FEED_W * 0.11)
        lh = int(logo.height * (lw / logo.width))
        logo = logo.resize((lw, lh), Image.Resampling.LANCZOS)
        canvas.paste(logo, (36, y_foot + 18), logo)

    draw.text(
        (170, y_foot + 28),
        WEBSITE,
        font=font(sans, 26),
        fill=ink,
    )
    draw.text(
        (170, y_foot + 62),
        PHONE,
        font=font(sans, 24),
        fill=ink,
    )
    draw.text(
        (520, y_foot + 42),
        "Come as you are",
        font=font(script if os.path.isfile(script) else serif, 30),
        fill=eggplant,
    )

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    canvas.save(out_path, "PNG", optimize=True)
    return out_path


def default_paths(day: date, style_id: str) -> Dict[str, str]:
    slug = style_id.replace("living_", "").replace("_", "-")
    base = os.path.join(ASSETS_DIR, f"sg-living-{day.isoformat()}-{slug}")
    bundle = os.path.join(LIVING_WORLDS_DATA, f"{day.isoformat()}-{slug}")
    return {
        "scene_raw": f"{base}-scene-raw.png",
        "static_cover": f"{base}-cover-1350.png",
        "preview_loop": f"{base}-loop-1350.mp4",
        "preview_loop_vertical": f"{base}-loop-1920.mp4",
        "prompt": os.path.join(bundle, "prompt.txt"),
        "storyboard": os.path.join(bundle, "storyboard.md"),
        "meta": os.path.join(bundle, "meta.json"),
    }


def save_bundle(
    day: date,
    style_id: str,
    events: Sequence[Event],
    *,
    scene_prompt: str,
    paths: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    paths = paths or default_paths(day, style_id)
    os.makedirs(os.path.dirname(paths["prompt"]), exist_ok=True)
    with open(paths["prompt"], "w", encoding="utf-8") as fh:
        fh.write(scene_prompt)
    with open(paths["storyboard"], "w", encoding="utf-8") as fh:
        fh.write(build_movement_storyboard(day, style_id, events))
    write_json(
        paths["meta"],
        {
            "day": day.isoformat(),
            "style_id": style_id,
            "label": living_world_style_meta(style_id).get("label"),
            "reader": _reader_line(events),
            "events": [e.title for e in pick_events_for_flyer(events)],
        },
    )
    return paths


def _smoothstep(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def _draw_smoke_wisp(
    layer: "Image.Image",
    cx: int,
    cy: int,
    *,
    alpha: int,
    w: int,
    h: int,
    drift: int = 0,
) -> None:
    from PIL import ImageDraw

    draw = ImageDraw.Draw(layer, "RGBA")
    draw.ellipse(
        (cx - w // 2 + drift, cy - h, cx + w // 2 + drift, cy),
        fill=(235, 240, 255, alpha),
    )
    draw.ellipse(
        (cx - w // 3 + drift + 8, cy - h - 16, cx + w // 3 + drift + 8, cy - 4),
        fill=(255, 255, 255, max(0, alpha - 20)),
    )
    draw.ellipse(
        (cx - w // 4 + drift - 6, cy - h - 28, cx + w // 4 + drift - 6, cy - 12),
        fill=(245, 248, 255, max(0, alpha - 40)),
    )


def _paste_rotated(
    base: "Image.Image",
    patch: "Image.Image",
    center: tuple[int, int],
    angle_deg: float,
) -> None:
    from PIL import Image

    rotated = patch.rotate(angle_deg, resample=Image.Resampling.BICUBIC, expand=True)
    x = center[0] - rotated.width // 2
    y = center[1] - rotated.height // 2
    base.paste(rotated, (x, y), rotated)


def _scale_scene_pt(x: float, y: float, *, out_w: int, out_h: int) -> tuple[int, int]:
    """Map 1024×1024 scene coordinates → art band size."""
    return (int(x * out_w / 1024), int(y * out_h / 1024))


def _interp_track(points: Sequence[tuple[int, int]], u: float) -> tuple[int, int]:
    if not points:
        return (0, 0)
    if u <= 0:
        return points[0]
    if u >= 1:
        return points[-1]
    seg = (len(points) - 1) * u
    i = int(seg)
    frac = seg - i
    x0, y0 = points[i]
    x1, y1 = points[i + 1]
    return (int(x0 + (x1 - x0) * frac), int(y0 + (y1 - y0) * frac))


def _erase_disk(img: "Image.Image", cx: int, cy: int, r: int) -> None:
    """Hide a circular object by pasting a soft blurred local patch."""
    from PIL import Image, ImageDraw, ImageFilter

    pad = r + 10
    x0 = max(0, cx - pad)
    y0 = max(0, cy - pad)
    x1 = min(img.width, cx + pad)
    y1 = min(img.height, cy + pad)
    patch = img.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(7))
    mask = Image.new("L", (x1 - x0, y1 - y0), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((pad - r, pad - r, pad + r, pad + r), fill=255)
    img.paste(patch, (x0, y0), mask)



def _paste_pendant_swing(
    art: "Image.Image",
    pendant_sprite: "Image.Image",
    *,
    pivot_canvas: tuple[int, int],
    sprite_origin: tuple[int, int],
    angle_deg: float,
    erase_box: tuple[int, int, int, int],
    inpaint_src: "Image.Image",
) -> None:
    from PIL import Image, ImageFilter

    x0, y0, x1, y1 = erase_box
    patch = inpaint_src.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(6))
    art.paste(patch, (x0, y0))

    layer = Image.new("RGBA", art.size, (0, 0, 0, 0))
    ox, oy = sprite_origin
    layer.paste(pendant_sprite, (ox, oy), pendant_sprite)
    layer = layer.rotate(
        angle_deg,
        resample=Image.Resampling.BICUBIC,
        center=pivot_canvas,
        expand=False,
    )
    art.alpha_composite(layer)


def _animate_candle_flame(
    art: "Image.Image",
    candle_xy: tuple[int, int],
    t: float,
    *,
    frame_i: int,
) -> None:
    """Replace static candle flame with a visibly flickering drawn flame + warm halo."""
    import math

    from PIL import Image, ImageDraw, ImageEnhance

    gx, gy = candle_xy
    # Wipe the baked-in flame so our animation reads clearly
    _erase_disk(art, gx, gy - 22, 26)

    wobble_x = math.sin(t * 17.3 + frame_i * 0.4) * 7
    wobble_y = math.sin(t * 23.1 + 1.2) * 4
    flame_h = 42 + int(16 * math.sin(t * 21.7)) + int(10 * math.sin(t * 33.4))
    flame_w = 18 + int(7 * math.sin(t * 19.1))

    layer = Image.new("RGBA", art.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(layer, "RGBA")

    tip_y = gy - flame_h + wobble_y
    base_y = gy + 8
    cx = gx + wobble_x

    # Outer warm halo (pulses)
    pulse = 0.5 + 0.5 * math.sin(t * 14.0)
    fd.ellipse(
        (cx - 58, tip_y - 30, cx + 58, base_y + 38),
        fill=(255, 120, 20, int(95 * pulse)),
    )
    fd.ellipse(
        (cx - 36, tip_y - 10, cx + 36, base_y + 22),
        fill=(255, 160, 40, int(120 * pulse)),
    )

    # Flame body — teardrop changes shape each frame
    fd.ellipse(
        (cx - flame_w, tip_y, cx + flame_w, base_y),
        fill=(255, 165, 35, 245),
    )
    fd.ellipse(
        (cx - flame_w + 4, tip_y + 6, cx + flame_w - 4, base_y - 2),
        fill=(255, 210, 60, 230),
    )
    # Bright core
    core_h = max(12, flame_h // 2)
    fd.ellipse(
        (cx - 8, base_y - core_h, cx + 8, base_y - 4),
        fill=(255, 255, 210, 215),
    )
    # Wick spark
    fd.line((cx, base_y - 2, cx + int(wobble_x * 0.3), tip_y + 10), fill=(80, 40, 10, 200), width=2)

    art.alpha_composite(layer)

    # Local brightness pop on candle + nearby brass (not whole image)
    pad = 70
    x0 = max(0, int(cx - pad))
    y0 = max(0, int(tip_y - pad))
    x1 = min(art.width, int(cx + pad))
    y1 = min(art.height, int(base_y + pad))
    region = art.crop((x0, y0, x1, y1))
    boost = 1.08 + 0.14 * math.sin(t * 18.5)
    region = ImageEnhance.Brightness(region).enhance(boost)
    region = ImageEnhance.Color(region).enhance(1.0 + 0.08 * pulse)
    art.paste(region, (x0, y0))


def render_preview_loop(
    cover_path: str,
    out_path: str,
    *,
    duration_s: float = 7.0,
    fps: int = 24,
    intensity: str = "strong",
) -> str:
    """
    Storyboard-faithful preview loop for Living Worlds (local ffmpeg via imageio).

    Animates the art band only; info panel + footer stay static. For Founder
    review before TopView/Seedance final. Use intensity='strong' for visible motion.
    """
    import math

    import imageio.v3 as iio
    import numpy as np
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

    cover = Image.open(cover_path).convert("RGBA")
    w, h = cover.size
    art_h = min(ART_H, h - FOOTER_H - INFO_H)
    static_bottom = cover.crop((0, art_h, w, h)).convert("RGBA")

    # Use scene_raw (1024) scaled to art band — coordinates match the machine photo
    scene_path = cover_path.replace("-cover-1350.png", "-scene-raw.png")
    if os.path.isfile(scene_path):
        art_base = (
            Image.open(scene_path)
            .convert("RGBA")
            .resize((w, art_h), Image.Resampling.LANCZOS)
        )
    else:
        art_base = cover.crop((0, 0, w, art_h)).convert("RGBA")

    aw, ah = art_base.size

    # Wooden ramp waypoints (measured on 1024 scene → scaled to art band)
    track = [
        _scale_scene_pt(178, 232, out_w=aw, out_h=ah),  # big sphere at top
        _scale_scene_pt(205, 305, out_w=aw, out_h=ah),
        _scale_scene_pt(238, 385, out_w=aw, out_h=ah),
        _scale_scene_pt(268, 465, out_w=aw, out_h=ah),
        _scale_scene_pt(290, 545, out_w=aw, out_h=ah),
        _scale_scene_pt(305, 640, out_w=aw, out_h=ah),  # near tarot card
    ]
    marble_start = track[0]
    marble_r = int(46 * aw / 1024)

    mug_xy = _scale_scene_pt(895, 655, out_w=aw, out_h=ah)
    candle_xy = _scale_scene_pt(538, 508, out_w=aw, out_h=ah)
    incense_xy = _scale_scene_pt(808, 478, out_w=aw, out_h=ah)
    card_xy = _scale_scene_pt(292, 698, out_w=aw, out_h=ah)

    # Pendant — heart + chain on right brass rail
    pend_x0, pend_y0 = _scale_scene_pt(698, 288, out_w=aw, out_h=ah)
    pend_x1, pend_y1 = _scale_scene_pt(878, 535, out_w=aw, out_h=ah)
    pend_box = (pend_x0, pend_y0, pend_x1, pend_y1)
    pendant_pivot_canvas = _scale_scene_pt(782, 292, out_w=aw, out_h=ah)
    pendant_sprite = art_base.crop(pend_box)
    sprite_origin = (pend_x0, pend_y0)

    # Marble sprite from the actual glass sphere at ramp top
    mx0, my0 = marble_start
    marble = art_base.crop(
        (mx0 - marble_r, my0 - marble_r, mx0 + marble_r, my0 + marble_r)
    )

    card = art_base.crop(
        (
            card_xy[0] - 55,
            card_xy[1] - 75,
            card_xy[0] + 55,
            card_xy[1] + 75,
        )
    )

    inpaint_src = art_base.copy()

    n_frames = max(2, int(round(duration_s * fps)))
    frames: List[np.ndarray] = []

    for i in range(n_frames):
        t = (i / n_frames) * duration_s
        art = art_base.copy()

        # ── CRYSTAL ROLL 1.0–2.4s — erase static sphere, roll along ramp ──
        roll_u = 0.0
        if t < 1.0:
            roll_u = 0.0
        elif t < 2.4:
            roll_u = _smoothstep((t - 1.0) / 1.4)
        else:
            roll_u = 1.0

        mx, my = _interp_track(track, roll_u)
        spin = roll_u * 540.0

        if roll_u > 0.02:
            _erase_disk(art, marble_start[0], marble_start[1], marble_r + 4)

        if roll_u > 0.0:
            # Trail sparkles on the ramp
            trail = Image.new("RGBA", art.size, (0, 0, 0, 0))
            tdraw = ImageDraw.Draw(trail, "RGBA")
            for k in range(8):
                u = max(0.0, roll_u - k * 0.04)
                tx, ty = _interp_track(track, u)
                tdraw.ellipse((tx - 12, ty - 8, tx + 12, ty + 8), fill=(255, 230, 150, 110 - k * 12))
            art = Image.alpha_composite(art, trail)
            _paste_rotated(art, marble, (mx, my), spin)

        # ── PENDANT SWING 3.2–6.8s — obvious 22° pendulum ──
        if t >= 3.2:
            swing_deg = math.sin((t - 3.2) * 3.6) * 22.0
            _paste_pendant_swing(
                art,
                pendant_sprite,
                pivot_canvas=pendant_pivot_canvas,
                sprite_origin=sprite_origin,
                angle_deg=swing_deg,
                erase_box=pend_box,
                inpaint_src=inpaint_src,
            )
        if t >= 2.0:
            pour = _smoothstep(min(1.0, max(0.0, (t - 2.0) / 0.9)))
            pour_layer = Image.new("RGBA", art.size, (0, 0, 0, 0))
            pd = ImageDraw.Draw(pour_layer, "RGBA")
            # Pour stream
            stream_x = mug_xy[0] - 35
            stream_top = mug_xy[1] - 80 - int(pour * 20)
            pd.line(
                (stream_x, stream_top, stream_x + int(pour * 8), mug_xy[1] - 25),
                fill=(180, 140, 90, int(180 * pour)),
                width=5,
            )
            art = Image.alpha_composite(art, pour_layer)
            steam = Image.new("RGBA", art.size, (0, 0, 0, 0))
            phase = (t - 2.0) % 0.9
            for j, off in enumerate((-12, 0, 14, 28)):
                cy = mug_xy[1] - 40 - int(phase * 90) - j * 30
                alpha = int(160 - j * 28)
                if alpha > 20:
                    _draw_smoke_wisp(
                        steam,
                        mug_xy[0] + off,
                        cy,
                        alpha=alpha,
                        w=48 - j * 6,
                        h=40,
                    )
            art = Image.alpha_composite(art, steam)

        # ── CANDLE FLICKER — every frame (visible flame animation) ──
        _animate_candle_flame(art, candle_xy, t, frame_i=i)

        # ── 2.8s+ INCENSE (thick drifting smoke) ──
        if t >= 2.8:
            smoke = Image.new("RGBA", art.size, (0, 0, 0, 0))
            drift = int((t - 2.8) * 35)
            for j in range(6):
                cy = incense_xy[1] - 20 - j * 32 - int((t * 25) % 28)
                _draw_smoke_wisp(
                    smoke,
                    incense_xy[0],
                    cy,
                    alpha=120 - j * 15,
                    w=38,
                    h=32,
                    drift=drift + j * 14,
                )
            art = Image.alpha_composite(art, smoke)

        # ── 4.5–5.8s CARD FLIP ──
            flip_prog = _smoothstep(min(1.0, (t - 4.5) / 0.7))
            scale_x = max(0.15, abs(math.cos(flip_prog * math.pi)))
            cw, ch = card.size
            new_w = max(8, int(cw * scale_x))
            scaled = card.resize((new_w, ch), Image.Resampling.BICUBIC)
            bright = ImageEnhance.Brightness(scaled).enhance(1.0 + 0.35 * flip_prog)
            px = card_xy[0] - new_w // 2
            py = card_xy[1] - ch // 2
            art.paste(bright, (px, py), bright)

        # ── 5.5–6.5s OPEN sign (scale in + bounce) ──
        if t >= 5.5:
            open_prog = _smoothstep(min(1.0, (t - 5.5) / 0.7))
            bounce = 1.0 + 0.15 * math.sin(open_prog * math.pi) if open_prog < 1.0 else 1.0
            bw, bh = int(160 * open_prog * bounce), int(64 * open_prog * bounce)
            if bw > 8 and bh > 8:
                badge = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
                bdraw = ImageDraw.Draw(badge)
                bdraw.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=8, fill=(120, 72, 40, 245))
                try:
                    from PIL import ImageFont

                    bf = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", max(14, int(bh * 0.42)))
                except OSError:
                    bf = ImageFont.load_default()
                bdraw.text((int(bw * 0.18), int(bh * 0.22)), "OPEN", font=bf, fill=(255, 245, 220, 255))
                art.paste(badge, (400, 620), badge)

        # ── Subtle machine breathe (always) ──
        breathe = 1.0 + 0.02 * math.sin(t * 3.1)
        art = ImageEnhance.Brightness(art).enhance(breathe)

        frame = Image.new("RGBA", (w, h), (250, 245, 232, 255))
        frame.paste(art, (0, 0))
        frame.paste(static_bottom, (0, art_h), static_bottom)
        frames.append(np.array(frame.convert("RGB")))

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    # Pad to multiple of 16 to avoid ffmpeg resize warning
    pad_w = ((w + 15) // 16) * 16
    pad_h = ((h + 15) // 16) * 16
    if pad_w != w or pad_h != h:
        padded = []
        for fr in frames:
            canvas = np.full((pad_h, pad_w, 3), 250, dtype=np.uint8)
            canvas[:h, :w] = fr
            padded.append(canvas)
        frames = padded

    iio.imwrite(
        out_path,
        np.stack(frames),
        extension=".mp4",
        fps=fps,
        codec="libx264",
        pixelformat="yuv420p",
    )
    return out_path

