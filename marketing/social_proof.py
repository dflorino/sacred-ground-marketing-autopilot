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


def _one_line(lines: Sequence[str], *, max_chars: int = 36) -> str:
    """Join badge lines for thin bands — never leave dangling '&' wraps."""
    one = " · ".join(str(ln).strip() for ln in lines if str(ln).strip())
    one = " ".join(one.split())
    if len(one) > max_chars:
        one = one[: max_chars - 1].rstrip(" ·-–—") + "…"
    return one or "Chicagoland favorite"


def _fit_lines(lines: Sequence[str], *, max_lines: int = 2) -> List[str]:
    cleaned = [str(ln).strip() for ln in lines if str(ln).strip()]
    if not cleaned:
        return ["Chicagoland favorite"]
    if len(cleaned) <= max_lines:
        return cleaned
    # Prefer keeping first lines; collapse remainder onto last slot.
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


def draw_badge(
    img,
    *,
    style: str,
    text: str,
    photo_bottom: Optional[int] = None,
):
    """Draw a designed-in social-proof mark; returns (new_image, style_drawn).

    Placement rules (Founder Aug 11 2026 remake):
    - Never cover Sacred Ground wordmark, event cards, circular logo, or phone footer
    - Prefer flush top thin cream/gold band, bottom strip above footer, or small seal
      in empty sky/margin
    - Soft cream wash OK — no giant opaque white sticker disks

    photo_bottom = Y above cream/contact footer (default: full height).
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
    # Keep marks inside the photo area with a tiny inset from the footer seam.
    safe_bottom = max(1, pb - max(4, int(w * 0.006)))
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font = _badge_font(max(15, int(w * 0.024)))
    font_sm = _badge_font(max(13, int(w * 0.019)))
    font_xs = _badge_font(max(12, int(w * 0.016)))
    pad = max(10, int(w * 0.018))

    if style == "banner":
        # Flush top-edge thin cream/gold band — sits above the wordmark.
        bh = max(26, int(w * 0.030))
        draw.rectangle((0, 0, w, bh), fill=(*cream, 238))
        draw.line((0, 0, w, 0), fill=(*gold, 220), width=1)
        draw.line((0, bh - 2, w, bh - 2), fill=(*gold, 255), width=2)
        one = _one_line(lines, max_chars=40)
        bbox = draw.textbbox((0, 0), one, font=font_sm)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            ((w - tw) // 2, (bh - th) // 2 - 1),
            one,
            font=font_sm,
            fill=(*eggplant, 255),
        )

    elif style == "pill":
        # Full-width thin strip just above the contact footer (not a floating chip).
        ph = max(26, int(w * 0.030))
        y0 = max(pad, safe_bottom - ph)
        draw.rectangle((0, y0, w, y0 + ph), fill=(*cream, 232))
        draw.line((0, y0, w, y0), fill=(*gold, 255), width=2)
        draw.line((0, y0 + ph - 1, w, y0 + ph - 1), fill=(*gold, 200), width=1)
        one = _one_line(lines, max_chars=40)
        bbox = draw.textbbox((0, 0), one, font=font_sm)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            ((w - tw) // 2, y0 + (ph - th) // 2 - 1),
            one,
            font=font_sm,
            fill=(*eggplant, 255),
        )

    elif style == "circle":
        # Small sky seal — soft cream wash + gold ring (not a giant opaque white disk).
        r = max(30, int(min(w, safe_bottom) * 0.055))
        cx = w - r - pad
        cy = r + max(6, int(w * 0.010))
        # Keep seal in the upper photo margin (empty sky), never mid-wordmark.
        cy = min(cy, max(r + 4, int(safe_bottom * 0.10)))
        draw.ellipse(
            (cx - r, cy - r, cx + r, cy + r),
            fill=(*cream, 150),
            outline=(*gold, 255),
            width=3,
        )
        inner = max(8, r - 6)
        draw.ellipse(
            (cx - inner, cy - inner, cx + inner, cy + inner),
            outline=(*gold, 170),
            width=1,
        )
        seal_lines = _fit_lines(lines, max_lines=2)
        _draw_centered_lines(
            draw, seal_lines, cx=cx, cy=cy, font=font_xs, fill=(*eggplant, 255), gap=2
        )

    elif style == "ribbon":
        # Slim top-left boutique ribbon hanging from the top edge (not over title).
        rw = int(w * 0.30)
        rh = max(26, int(w * 0.034))
        y0 = 0
        notch = max(10, int(rh * 0.42))
        pts = [
            (0, y0),
            (rw, y0),
            (rw - notch, y0 + rh // 2),
            (rw, y0 + rh),
            (0, y0 + rh),
        ]
        draw.polygon(pts, fill=(*gold, 220), outline=(*eggplant, 160))
        # Soft cream inset for shop-made (not Canva sticker) feel.
        inset = 3
        pts_in = [
            (inset, y0 + inset),
            (rw - notch - 2, y0 + inset),
            (rw - notch * 2 + 2, y0 + rh // 2),
            (rw - notch - 2, y0 + rh - inset),
            (inset, y0 + rh - inset),
        ]
        draw.polygon(pts_in, fill=(*cream, 90))
        one = _one_line(lines, max_chars=22)
        bbox = draw.textbbox((0, 0), one, font=font_xs)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = max(6, (rw - notch - tw) // 2)
        draw.text((tx, y0 + (rh - th) // 2 - 1), one, font=font_xs, fill=(*ink, 255))

    else:  # corner
        # Compact top-right corner chip in empty margin — soft wash, short type.
        cw = int(w * 0.22)
        ch = max(34, int(w * 0.048))
        x0 = w - cw - pad
        y0 = max(6, int(w * 0.01))
        draw.rounded_rectangle(
            (x0, y0, x0 + cw, y0 + ch),
            radius=10,
            fill=(*cream, 170),
            outline=(*gold, 245),
            width=2,
        )
        # Tiny gold tick on the outer corner so it feels designed-in.
        draw.line(
            (x0 + cw - 14, y0 + 3, x0 + cw - 3, y0 + 3),
            fill=(*eggplant, 160),
            width=1,
        )
        corner_lines = _fit_lines(lines, max_lines=2)
        _draw_centered_lines(
            draw,
            corner_lines,
            cx=x0 + cw // 2,
            cy=y0 + ch // 2,
            font=font_xs,
            fill=(*ink, 255),
            gap=1,
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
    """Load image, draw rotating badge, save. Returns meta or None if skipped."""
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
