"""Rotating playful shop-pride social proof (captions, badges, first comment).

Honesty (Founder Aug 11 2026): these are warm local-pride lines — “i vote it
the best! lol” energy — NOT formal third-party award citations. Do not invent
Chicago Reader / Best Of winners unless Founder confirms a real source.
See config/social_proof.json → honesty_note + enabled flag.

On-image badges (Aug 11 ~2:52pm CT): OFF by default until Founder greenlights
a style. Preview rebuild uses only seal + footer_band (v1 sticker / v2 tiny
marks both rejected). Captions + first_comment stay enabled.
"""
from __future__ import annotations

import hashlib
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .paths import CONFIG_DIR, _load_json

SOCIAL_PROOF_PATH = os.path.join(CONFIG_DIR, "social_proof.json")

# Placement modes — rotate so not every post is identical.
MODE_CAPTION = "caption"
MODE_FIRST_COMMENT = "first_comment"
MODE_BOTH = "both"
MODE_SKIP = "skip"

# Two strong styles only (Founder Aug 11 ~2:52pm CT rebuild).
BADGE_STYLES = ("seal", "footer_band")


@lru_cache(maxsize=1)
def social_proof_config() -> Dict[str, Any]:
    if not os.path.isfile(SOCIAL_PROOF_PATH):
        return {"enabled": False, "claims": [], "badge_styles": list(BADGE_STYLES)}
    return _load_json(SOCIAL_PROOF_PATH)


def clear_social_proof_cache() -> None:
    social_proof_config.cache_clear()


def enabled() -> bool:
    return bool(social_proof_config().get("enabled"))


def _pick(opts: Sequence[str], seed: str, fallback: str = "") -> str:
    cleaned = [str(o).rstrip() for o in opts if o and str(o).strip()]
    if not cleaned:
        return fallback
    idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(cleaned)
    return cleaned[idx]


def _pick_index(n: int, seed: str) -> int:
    if n <= 0:
        return 0
    return int(hashlib.md5(seed.encode()).hexdigest(), 16) % n


def claims() -> List[str]:
    return [str(c).strip() for c in (social_proof_config().get("claims") or []) if str(c).strip()]


def badge_claims() -> List[str]:
    raw = social_proof_config().get("badge_claims") or claims()
    return [str(c).strip() for c in raw if str(c).strip()]


def badge_styles() -> List[str]:
    styles = [
        str(s).strip().lower()
        for s in (social_proof_config().get("badge_styles") or BADGE_STYLES)
        if str(s).strip()
    ]
    return [s for s in styles if s in BADGE_STYLES] or list(BADGE_STYLES)


def pick_claim(seed: str) -> str:
    """Rotating caption / first-comment claim line."""
    return _pick(claims(), f"sp-claim|{seed}", "Chicagoland’s favorite crystal & holistic center.")


def pick_badge_claim(seed: str) -> str:
    """Shorter multi-line claim for on-image badges."""
    return _pick(badge_claims(), f"sp-badge-claim|{seed}", "Chicago’s #1\ncrystal shop")


def pick_badge_style(seed: str) -> str:
    styles = badge_styles()
    return styles[_pick_index(len(styles), f"sp-badge-style|{seed}")]


def pick_placement_mode(seed: str, *, campaign: str = "") -> str:
    """Where the claim appears this post: caption / first_comment / both."""
    if not enabled():
        return MODE_SKIP
    camps = set(social_proof_config().get("caption_campaigns") or [])
    if camps and campaign and campaign not in camps:
        return MODE_SKIP
    modes = [
        str(m).strip().lower()
        for m in (social_proof_config().get("placement_modes") or [])
        if str(m).strip()
    ]
    modes = [m for m in modes if m in (MODE_CAPTION, MODE_FIRST_COMMENT, MODE_BOTH)]
    if not modes:
        modes = [MODE_CAPTION, MODE_FIRST_COMMENT, MODE_BOTH]
    return modes[_pick_index(len(modes), f"sp-place|{seed}|{campaign}")]


def should_badge_morning(seed: str) -> bool:
    # Default OFF — Founder rejected v1/v2 on-image marks (Aug 11 ~2:52pm CT).
    if not enabled() or not social_proof_config().get("badge_on_morning_flyers", False):
        return False
    # ~4/5 mornings get a badge so layout still breathes.
    return _pick_index(5, f"sp-mf-badge|{seed}") != 0


def should_badge_night(*, mode: str = "", creative_id: str = "", seed: str = "") -> bool:
    """Night plates: prefer shop/generic; skip pure celestial when configured."""
    # Default OFF — Founder rejected v1/v2 on-image marks (Aug 11 ~2:52pm CT).
    if not enabled() or not social_proof_config().get("badge_on_night", False):
        return False
    if social_proof_config().get("badge_skip_celestial", True):
        m = (mode or "").lower()
        cid = (creative_id or "").lower()
        if m == "celestial" or "celestial" in cid:
            return False
    # Subtle: ~3/5 nights
    return _pick_index(5, f"sp-night-badge|{seed}") in (0, 1, 2)


def first_comment_supported(platform: str) -> bool:
    plats = {
        str(p).lower()
        for p in (social_proof_config().get("first_comment_platforms") or ["facebook", "instagram"])
    }
    return (platform or "").lower() in plats


def plan_for_post(
    *,
    campaign: str,
    platform: str,
    day_key: str,
) -> Dict[str, Any]:
    """Single rotation plan for a draft (caption line + optional first comment + badge)."""
    seed = f"{campaign}|{day_key}|{platform}"
    mode = pick_placement_mode(seed, campaign=campaign)
    claim = pick_claim(seed) if mode != MODE_SKIP else ""
    badge_style = pick_badge_style(seed)
    badge_text = pick_badge_claim(seed)
    in_caption = mode in (MODE_CAPTION, MODE_BOTH) and bool(claim)
    in_comment = (
        mode in (MODE_FIRST_COMMENT, MODE_BOTH)
        and bool(claim)
        and first_comment_supported(platform)
    )
    # If first_comment was chosen but platform unsupported, keep claim in caption.
    if mode == MODE_FIRST_COMMENT and not in_comment and claim:
        in_caption = True
    return {
        "enabled": enabled() and mode != MODE_SKIP,
        "mode": mode,
        "claim": claim,
        "in_caption": in_caption,
        "in_first_comment": in_comment,
        "first_comment": claim if in_comment else "",
        "badge_style": badge_style,
        "badge_text": badge_text,
    }


def weave_caption(
    text: str,
    *,
    campaign: str,
    platform: str,
    day_key: str,
    plan: Optional[Dict[str, Any]] = None,
) -> Tuple[str, Dict[str, Any]]:
    """Insert a short social-proof line into caption text when the plan says so.

    Returns (new_text, plan). Plan always included so publish can attach firstComment.
    """
    plan = plan or plan_for_post(campaign=campaign, platform=platform, day_key=day_key)
    if not plan.get("in_caption") or not plan.get("claim"):
        return text, plan

    claim = str(plan["claim"]).strip()
    if not claim or claim.lower() in text.lower():
        return text, plan

    # Prefer a quiet slot before hashtags / after signoff-ish body.
    # Keep a blank line before #tags so scannable caption tests still hold.
    tags_at = text.find("\n#")
    if tags_at > 0:
        before = text[:tags_at].rstrip()
        after = text[tags_at:].lstrip("\n")  # typically "#SacredGround …"
        return before + "\n\n" + claim + "\n\n" + after, plan

    return text.rstrip() + "\n\n" + claim, plan


def enrich_caption_dict(
    cap: Dict[str, Any],
    *,
    campaign: str,
    platform: str,
    day_key: str,
) -> Dict[str, Any]:
    """Mutate/return caption dict with social_proof metadata + woven text."""
    plan = plan_for_post(campaign=campaign, platform=platform, day_key=day_key)
    text = str(cap.get("text") or "")
    new_text, plan = weave_caption(
        text, campaign=campaign, platform=platform, day_key=day_key, plan=plan
    )
    out = dict(cap)
    out["text"] = new_text
    out["social_proof"] = {
        "mode": plan.get("mode"),
        "claim": plan.get("claim") or "",
        "in_caption": bool(plan.get("in_caption")),
        "in_first_comment": bool(plan.get("in_first_comment")),
        "first_comment": plan.get("first_comment") or "",
        "badge_style": plan.get("badge_style"),
    }
    return out


def _colors() -> Dict[str, Tuple[int, int, int]]:
    raw = social_proof_config().get("colors") or {}
    def _rgb(key: str, default: Tuple[int, int, int]) -> Tuple[int, int, int]:
        v = raw.get(key) or list(default)
        return (int(v[0]), int(v[1]), int(v[2]))
    return {
        "gold": _rgb("gold", (212, 175, 85)),
        "ink": _rgb("ink", (28, 22, 40)),
        "cream": _rgb("cream", (250, 245, 232)),
        "eggplant": _rgb("eggplant", (72, 42, 90)),
    }


def _badge_font(size: int):
    from PIL import ImageFont

    candidates = [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Avenir Next.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def _wrap_lines(text: str) -> List[str]:
    lines: List[str] = []
    for raw in str(text).replace("\\n", "\n").split("\n"):
        bit = raw.strip()
        if bit:
            lines.append(bit)
    return lines or ["Chicagoland favorite"]


def _one_line(lines: Sequence[str], *, max_chars: int = 42) -> str:
    """Join badge lines for footer band — confident single claim."""
    one = " · ".join(str(ln).strip() for ln in lines if str(ln).strip())
    one = " ".join(one.split())
    if len(one) > max_chars:
        one = one[: max_chars - 1].rstrip(" ·-–—") + "…"
    return one or "Chicagoland favorite"


def _fit_lines(lines: Sequence[str], *, max_lines: int = 3) -> List[str]:
    cleaned = [str(ln).strip() for ln in lines if str(ln).strip()]
    if not cleaned:
        return ["Chicagoland favorite"]
    if len(cleaned) <= max_lines:
        return cleaned
    head = list(cleaned[: max_lines - 1])
    tail = " ".join(cleaned[max_lines - 1 :])
    head.append(tail)
    return head


def _draw_centered_lines(draw, lines: Sequence[str], *, cx: int, cy: int, font, fill, gap: int = 3) -> None:
    widths: List[int] = []
    heights: List[int] = []
    for ln in lines:
        bbox = draw.textbbox((0, 0), ln, font=font)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])
    total_h = sum(heights) + gap * (len(lines) - 1)
    y = cy - total_h // 2
    for ln, tw, th in zip(lines, widths, heights):
        draw.text((cx - tw // 2, y), ln, font=font, fill=fill)
        y += th + gap


def _seal_font_for(draw, lines: Sequence[str], *, max_w: int, max_h: int, start: int):
    """Pick the largest bold font that fits the seal’s text box."""
    size = start
    while size >= 11:
        font = _badge_font(size)
        widths = []
        heights = []
        for ln in lines:
            bbox = draw.textbbox((0, 0), ln, font=font)
            widths.append(bbox[2] - bbox[0])
            heights.append(bbox[3] - bbox[1])
        gap = max(2, size // 8)
        total_h = sum(heights) + gap * (len(lines) - 1)
        if max(widths or [0]) <= max_w and total_h <= max_h:
            return font, gap
        size -= 1
    return _badge_font(11), 2


def draw_badge(
    img,
    *,
    style: str,
    text: str,
    photo_bottom: Optional[int] = None,
):
    """Draw a designed-in social-proof mark; returns (new_image, style_drawn).

    Styles (Founder Aug 11 ~2:52pm CT rebuild — preview only until approved):
    - seal: substantial gold/cream wax-seal (~14–18% width), 2–3 line claim,
      empty margin only (not over title/cards/logo)
    - footer_band: dedicated cream band extending the canvas below content —
      brand-footer energy, not a floating pill over art

    photo_bottom = Y above cream/contact footer (default: full height).
    """
    from PIL import Image, ImageDraw

    style = (style or "seal").lower()
    if style not in BADGE_STYLES:
        style = "seal"
    lines = _wrap_lines(text)
    cols = _colors()
    gold, ink, cream, eggplant = cols["gold"], cols["ink"], cols["cream"], cols["eggplant"]

    base = img.convert("RGBA")
    w, h = base.size
    pb = photo_bottom if photo_bottom is not None else h
    safe_bottom = max(1, pb - max(4, int(w * 0.006)))
    pad = max(12, int(w * 0.02))

    if style == "footer_band":
        # Dedicated cream claim band extending the canvas — never floats over art.
        band_h = max(56, int(w * 0.062))
        new_h = h + band_h
        out = Image.new("RGBA", (w, new_h), (*cream, 255))
        out.paste(base, (0, 0))
        draw = ImageDraw.Draw(out)
        y0 = h
        # Gold top rule + soft double line for boutique footer energy
        draw.rectangle((0, y0, w, new_h), fill=(*cream, 255))
        draw.line((0, y0, w, y0), fill=(*gold, 255), width=3)
        draw.line((0, y0 + 4, w, y0 + 4), fill=(*gold, 140), width=1)
        draw.line((0, new_h - 2, w, new_h - 2), fill=(*gold, 180), width=2)
        one = _one_line(lines, max_chars=44)
        font = _badge_font(max(22, int(w * 0.032)))
        bbox = draw.textbbox((0, 0), one, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        # Shrink once if claim is wide
        if tw > w - 2 * pad:
            font = _badge_font(max(16, int(w * 0.026)))
            bbox = draw.textbbox((0, 0), one, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            ((w - tw) // 2, y0 + (band_h - th) // 2 - 1),
            one,
            font=font,
            fill=(*eggplant, 255),
        )
        if img.mode == "RGB":
            return out.convert("RGB"), style
        return out, style

    # --- seal ---
    # Substantial boutique wax seal — 14–18% of image width (not a tiny sticker).
    # Slight oval (wider than tall) reads more like a pressed wax seal than a chip.
    diam_x = max(120, int(w * 0.165))
    diam_x = min(diam_x, int(w * 0.18))
    diam_y = max(110, int(diam_x * 0.92))
    rx, ry = diam_x // 2, diam_y // 2
    # Prefer true empty margin: upper-right sky / margin, clear of title cards
    # (left) and circular logo (bottom-left). Avoid lower-right graphic zones
    # on Thursday-style flyers (tarot / horse art).
    cx = w - rx - pad
    header_clear = max(pad, int(w * 0.105))
    cy = header_clear + ry + max(4, int(w * 0.008))
    # Keep fully inside the photo area when a cream footer is present.
    cy = min(cy, safe_bottom - ry - 4)
    cy = max(cy, ry + pad)

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Soft drop shadow so it sits *in* the plate (not a flat cutout sticker)
    sh = max(3, int(w * 0.006))
    draw.ellipse(
        (cx - rx + sh, cy - ry + sh, cx + rx + sh, cy + ry + sh),
        fill=(20, 12, 28, 70),
    )
    # Outer gold wash (wax rim)
    glow = max(3, int(w * 0.005))
    draw.ellipse(
        (cx - rx - glow, cy - ry - glow, cx + rx + glow, cy + ry + glow),
        fill=(*gold, 95),
    )
    # Cream fill + thick gold rim
    rim = max(5, int(w * 0.007))
    draw.ellipse(
        (cx - rx, cy - ry, cx + rx, cy + ry),
        fill=(*cream, 242),
        outline=(*gold, 255),
        width=rim,
    )
    # Warm gold inner wash (wax depth — not flat white Canva)
    wash_rx = max(10, rx - rim - 2)
    wash_ry = max(10, ry - rim - 2)
    draw.ellipse(
        (cx - wash_rx, cy - wash_ry, cx + wash_rx, cy + wash_ry),
        fill=(245, 230, 190, 55),
    )
    # Inner decorative ring
    inner_rx = max(12, rx - max(12, int(rx * 0.16)))
    inner_ry = max(12, ry - max(12, int(ry * 0.16)))
    draw.ellipse(
        (cx - inner_rx, cy - inner_ry, cx + inner_rx, cy + inner_ry),
        outline=(*gold, 210),
        width=max(2, int(w * 0.003)),
    )
    # Tiny ticks at N/E/S/W — boutique seal energy
    tick = max(4, int(min(rx, ry) * 0.09))
    for angle_pts in (
        (cx, cy - ry + rim, cx, cy - ry + rim + tick),
        (cx, cy + ry - rim - tick, cx, cy + ry - rim),
        (cx - rx + rim, cy, cx - rx + rim + tick, cy),
        (cx + rx - rim - tick, cy, cx + rx - rim, cy),
    ):
        draw.line(angle_pts, fill=(*eggplant, 170), width=2)

    seal_lines = _fit_lines(lines, max_lines=3)
    text_box_w = int(inner_rx * 1.65)
    text_box_h = int(inner_ry * 1.55)
    font, gap = _seal_font_for(
        draw,
        seal_lines,
        max_w=text_box_w,
        max_h=text_box_h,
        start=max(18, int(diam_x * 0.15)),
    )
    _draw_centered_lines(
        draw, seal_lines, cx=cx, cy=cy, font=font, fill=(*eggplant, 255), gap=gap
    )

    out = Image.alpha_composite(base, overlay)
    if img.mode == "RGB":
        return out.convert("RGB"), style
    return out, style


def apply_badge_to_path(
    path: str,
    *,
    seed: str,
    out_path: Optional[str] = None,
    photo_bottom: Optional[int] = None,
    force_style: Optional[str] = None,
    force_text: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Load image, draw rotating badge, save. Returns meta or None if skipped.

    Note: live morning/night pipelines gate via should_badge_*; this helper still
    draws when enabled so Founder previews can force styles while badges are OFF.
    """
    if not enabled() or not path or not os.path.isfile(path):
        return None
    from PIL import Image

    style = force_style or pick_badge_style(seed)
    text = force_text if force_text is not None else pick_badge_claim(seed)
    with Image.open(path) as im:
        img = im.convert("RGB")
        img, drawn = draw_badge(
            img, style=style, text=text, photo_bottom=photo_bottom
        )
        dest = out_path or path
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        img.save(dest, "PNG", optimize=True)
        size = list(img.size)
    return {"style": drawn, "text": text, "path": dest, "size": size}


def apply_night_badge_if_eligible(
    path: str,
    *,
    day_key: str,
    mode: str = "",
    creative_id: str = "",
    out_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Badge shop/generic night locals; skip pure celestial plates by default.

    Call when saving/branding night creatives before WordPress upload. Remote
    pool URLs already live are not rewritten at publish time.
    """
    seed = f"night|{day_key}|{mode}|{creative_id}"
    if not should_badge_night(mode=mode, creative_id=creative_id, seed=seed):
        return None
    return apply_badge_to_path(path, seed=seed, out_path=out_path)
