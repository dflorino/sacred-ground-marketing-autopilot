"""Rotating playful shop-pride social proof (captions, badges, first comment).

Honesty (Founder Aug 11 2026): these are warm local-pride lines — “i vote it
the best! lol” energy — NOT formal third-party award citations. Do not invent
Chicago Reader / Best Of winners unless Founder confirms a real source.
See config/social_proof.json → honesty_note + enabled flag.
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

BADGE_STYLES = ("banner", "circle", "pill", "ribbon", "corner")


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
    return _pick(badge_claims(), f"sp-badge-claim|{seed}", "Chicago’s #1\ntalked-about\ncrystal shop")


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
    if not enabled() or not social_proof_config().get("badge_on_morning_flyers", True):
        return False
    # ~4/5 mornings get a badge so layout still breathes.
    return _pick_index(5, f"sp-mf-badge|{seed}") != 0


def should_badge_night(*, mode: str = "", creative_id: str = "", seed: str = "") -> bool:
    """Night plates: prefer shop/generic; skip pure celestial when configured."""
    if not enabled() or not social_proof_config().get("badge_on_night", True):
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
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
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


def draw_badge(
    img,
    *,
    style: str,
    text: str,
    photo_bottom: Optional[int] = None,
):
    """Draw a tasteful social-proof badge; returns (new_image, style_drawn).

    photo_bottom = Y above cream footer (default: full height). Keeps badges
    in the photo area, not on the contact footer.
    """
    from PIL import Image, ImageDraw

    style = (style or "pill").lower()
    if style not in BADGE_STYLES:
        style = "pill"
    lines = _wrap_lines(text)
    cols = _colors()
    gold, ink, cream, eggplant = cols["gold"], cols["ink"], cols["cream"], cols["eggplant"]

    base = img.convert("RGBA")
    w, h = base.size
    pb = photo_bottom if photo_bottom is not None else h
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font = _badge_font(max(16, int(w * 0.028)))
    font_sm = _badge_font(max(14, int(w * 0.022)))

    def _text_block(cx: int, cy: int, fill, use_sm: bool = False) -> None:
        fnt = font_sm if use_sm else font
        heights = []
        widths = []
        for ln in lines:
            bbox = draw.textbbox((0, 0), ln, font=fnt)
            widths.append(bbox[2] - bbox[0])
            heights.append(bbox[3] - bbox[1])
        total_h = sum(heights) + 4 * (len(lines) - 1)
        y = cy - total_h // 2
        for ln, tw, th in zip(lines, widths, heights):
            draw.text((cx - tw // 2, y), ln, font=fnt, fill=fill)
            y += th + 4

    pad = int(w * 0.02)
    if style == "banner":
        bh = max(48, int(h * 0.07))
        y0 = max(pad, int(pb * 0.08))
        draw.rounded_rectangle(
            (int(w * 0.08), y0, int(w * 0.92), y0 + bh),
            radius=18,
            fill=(*eggplant, 210),
            outline=(*gold, 255),
            width=2,
        )
        _text_block(w // 2, y0 + bh // 2, (*cream, 255), use_sm=True)

    elif style == "circle":
        r = int(min(w, pb) * 0.13)
        cx, cy = w - r - pad, r + pad + int(pb * 0.02)
        draw.ellipse(
            (cx - r, cy - r, cx + r, cy + r),
            fill=(*cream, 230),
            outline=(*gold, 255),
            width=3,
        )
        inner = r - 8
        draw.ellipse(
            (cx - inner, cy - inner, cx + inner, cy + inner),
            outline=(*eggplant, 180),
            width=1,
        )
        _text_block(cx, cy, (*ink, 255), use_sm=True)

    elif style == "ribbon":
        rw, rh = int(w * 0.42), max(44, int(h * 0.055))
        x0, y0 = pad, int(pb * 0.12)
        pts = [
            (x0, y0),
            (x0 + rw, y0),
            (x0 + rw - 18, y0 + rh // 2),
            (x0 + rw, y0 + rh),
            (x0, y0 + rh),
        ]
        draw.polygon(pts, fill=(*gold, 230), outline=(*ink, 200))
        _text_block(x0 + rw // 2 - 6, y0 + rh // 2, (*ink, 255), use_sm=True)

    elif style == "corner":
        cw, ch = int(w * 0.36), max(56, int(h * 0.08))
        x0, y0 = w - cw - pad, pad + int(pb * 0.04)
        draw.rounded_rectangle(
            (x0, y0, x0 + cw, y0 + ch),
            radius=14,
            fill=(*cream, 220),
            outline=(*gold, 255),
            width=2,
        )
        _text_block(x0 + cw // 2, y0 + ch // 2, (*ink, 255), use_sm=True)

    else:  # pill
        pw, ph = int(w * 0.55), max(40, int(h * 0.05))
        x0 = (w - pw) // 2
        y0 = pb - ph - pad - int(pb * 0.02)
        y0 = min(y0, pb - ph - pad)
        y0 = max(pad, y0)
        draw.rounded_rectangle(
            (x0, y0, x0 + pw, y0 + ph),
            radius=ph // 2,
            fill=(*gold, 225),
            outline=(*ink, 160),
            width=1,
        )
        one = " · ".join(lines) if len(lines) > 1 else lines[0]
        if len(one) > 42:
            one = one[:40] + "…"
        bbox = draw.textbbox((0, 0), one, font=font_sm)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            (x0 + (pw - tw) // 2, y0 + (ph - th) // 2 - 1),
            one,
            font=font_sm,
            fill=(*ink, 255),
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
) -> Optional[Dict[str, Any]]:
    """Load image, draw rotating badge, save. Returns meta or None if skipped."""
    if not enabled() or not path or not os.path.isfile(path):
        return None
    from PIL import Image

    style = force_style or pick_badge_style(seed)
    text = pick_badge_claim(seed)
    with Image.open(path) as im:
        img = im.convert("RGB")
        img, drawn = draw_badge(
            img, style=style, text=text, photo_bottom=photo_bottom
        )
        dest = out_path or path
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        img.save(dest, "PNG", optimize=True)
    return {"style": drawn, "text": text, "path": dest}


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
