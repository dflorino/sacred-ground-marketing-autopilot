"""Rotating shop-pride social proof (captions, badges, first comment).

Honesty (Founder Aug 11 + Aug 13 2026): warm local-pride lines aligned with
email Options A/B/C — NOT formal third-party award citations. “Voted #1” is
Founder/community vibe (“i vote it the best! lol”), not a publication trophy.
Do not invent Chicago Reader / Best Of winners unless Founder confirms a source.
See config/social_proof.json → honesty_note + canonical_options + enabled flag.

On-image (Founder Aug 11 ~3:05pm CT cutover + Aug 12 FINAL):
- Captions + first_comment stay ON.
- NEVER overlay / stamp badges onto already-made morning flyers, celestial
  plates, or night creatives in the pool.
- Every NEW image generation/remake MUST bake designed-in shop pride into the
  generation prompt (designed_in_required) — banner / seal / band, not a sticker.
- badge_on_morning_flyers / badge_on_night stay false (no live overlay path).

Slot rotation (Founder Aug 13 ~9:13am CT — NO weekday→option map):
- Normal day (3 posts): today → A, afternoon_spotlight → B, week_ahead → C
- 4th special campaigns (tuesday_meditation, visit, spotlight, …) → always B
America/Chicago. See config/social_proof.json → slot_rotation.
"""
from __future__ import annotations

import hashlib
import os
import re
from datetime import date, datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .paths import CONFIG_DIR, _load_json

SOCIAL_PROOF_PATH = os.path.join(CONFIG_DIR, "social_proof.json")

# Placement modes — rotate so not every post is identical.
MODE_CAPTION = "caption"
MODE_FIRST_COMMENT = "first_comment"
MODE_BOTH = "both"
MODE_SKIP = "skip"

# Style names kept for designed-in generation briefs (not live overlays).
BADGE_STYLES = ("seal", "footer_band", "top_banner", "ribbon", "medallion")

# Canonical email Options A/B/C (Founder Aug 13 2026).
OPTION_IDS = ("A", "B", "C")
# Fixed daily slot order (America/Chicago) — documented in slot_rotation.
_DEFAULT_DAILY_SLOTS = {
    "today": "A",
    "afternoon_spotlight": "B",
    "week_ahead": "C",
}
_DEFAULT_ALWAYS_B = ("tuesday_meditation", "visit", "spotlight")
_DEFAULT_SURFACE_TO_CAMPAIGN = {
    "morning": "today",
    "today": "today",
    "afternoon": "afternoon_spotlight",
    "afternoon_spotlight": "afternoon_spotlight",
    "night": "week_ahead",
    "week_ahead": "week_ahead",
    "celestial": "today",
    "celestial_morning": "today",
    "celestial_night": "week_ahead",
    "tuesday_meditation": "tuesday_meditation",
}
_DEFAULT_CAPTION = (
    "Sacred Ground — Chicagoland’s #1 Crystal Shop & Holistic Center."
)
_DEFAULT_BADGE = "Chicagoland’s #1\nCrystal Shop"


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


def badge_claims_for_style(style: str) -> List[str]:
    """Tight per-format claims (2-line seal, 1-line banner, short ribbon, etc.)."""
    by_style = social_proof_config().get("badge_claims_by_style") or {}
    raw = by_style.get(str(style or "").lower()) or badge_claims()
    return [str(c).strip() for c in raw if str(c).strip()] or badge_claims()


def badge_styles() -> List[str]:
    styles = [
        str(s).strip().lower()
        for s in (social_proof_config().get("badge_styles") or BADGE_STYLES)
        if str(s).strip()
    ]
    return [s for s in styles if s in BADGE_STYLES] or list(BADGE_STYLES)


def canonical_options() -> Dict[str, Dict[str, Any]]:
    """Options A/B/C from email monthly org (Founder Aug 13 2026)."""
    raw = social_proof_config().get("canonical_options") or {}
    out: Dict[str, Dict[str, Any]] = {}
    for key in OPTION_IDS:
        block = raw.get(key) or raw.get(key.lower())
        if isinstance(block, dict) and block:
            out[key] = block
    return out


def slot_rotation() -> Dict[str, Any]:
    """America/Chicago campaign-slot → Option A/B/C map (no weekday map)."""
    raw = social_proof_config().get("slot_rotation") or {}
    return raw if isinstance(raw, dict) else {}


def daily_slot_options() -> Dict[str, str]:
    """Normal 3 daily posts → option letters (today/afternoon/week_ahead)."""
    raw = slot_rotation().get("daily_slots") or {}
    out: Dict[str, str] = {}
    source = raw if isinstance(raw, dict) and raw else _DEFAULT_DAILY_SLOTS
    for camp, letter in source.items():
        key = str(camp or "").strip().lower()
        opt = str(letter or "").strip().upper()
        if key and opt in OPTION_IDS:
            out[key] = opt
    return out or dict(_DEFAULT_DAILY_SLOTS)


def always_option_b_campaigns() -> set:
    """Specialty / 4th posts that always use Option B."""
    raw = slot_rotation().get("always_option_b_campaigns")
    if isinstance(raw, list) and raw:
        return {str(c).strip().lower() for c in raw if str(c).strip()}
    return set(_DEFAULT_ALWAYS_B)


def surface_to_campaign() -> Dict[str, str]:
    raw = slot_rotation().get("surface_to_campaign") or {}
    source = raw if isinstance(raw, dict) and raw else _DEFAULT_SURFACE_TO_CAMPAIGN
    out: Dict[str, str] = {}
    for surf, camp in source.items():
        s = str(surf or "").strip().lower()
        c = str(camp or "").strip().lower()
        if s and c:
            out[s] = c
    return out or dict(_DEFAULT_SURFACE_TO_CAMPAIGN)


def normalize_campaign(
    campaign: str = "",
    *,
    surface: str = "",
) -> str:
    """Map campaign or designed-in surface → canonical campaign key."""
    camp = str(campaign or "").strip().lower()
    if camp:
        return camp
    surf = str(surface or "").strip().lower()
    if not surf:
        return ""
    return surface_to_campaign().get(surf, surf)


def _parse_day_key(day_key: Union[date, datetime, str, None]) -> Optional[date]:
    if day_key is None:
        return None
    if isinstance(day_key, datetime):
        return day_key.date()
    if isinstance(day_key, date):
        return day_key
    text = str(day_key).strip()
    if not text:
        return None
    # Prefer ISO date anywhere in the seed / day_key string.
    m = re.search(r"(20\d{2}-\d{2}-\d{2})", text)
    if m:
        try:
            return date.fromisoformat(m.group(1))
        except ValueError:
            pass
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def resolve_option_id(
    seed: str = "",
    *,
    day_key: Union[date, datetime, str, None] = None,
    campaign: str = "",
    surface: str = "",
) -> str:
    """Pick Option A/B/C by campaign slot within the America/Chicago day.

    Fixed daily map (config slot_rotation.daily_slots):
      today → A, afternoon_spotlight → B, week_ahead → C
    Special / 4th posts (always_option_b_campaigns) → always B.
    No tuesday/thursday/sunday weekday map.
    """
    opts = canonical_options()
    ids = [i for i in OPTION_IDS if i in opts] or list(OPTION_IDS)
    camp = normalize_campaign(campaign, surface=surface)
    if not camp:
        # Infer campaign from seed prefixes used by callers.
        low = str(seed or "").lower()
        for key in (
            "tuesday_meditation",
            "afternoon_spotlight",
            "week_ahead",
            "today",
            "visit",
            "spotlight",
        ):
            if key in low:
                camp = key
                break
        if not camp:
            for surf in ("morning", "afternoon", "night", "celestial"):
                if surf in low:
                    camp = normalize_campaign(surface=surf)
                    break
    if camp in always_option_b_campaigns():
        return "B" if "B" in ids else ids[0]
    slots = daily_slot_options()
    if camp in slots:
        letter = slots[camp]
        if letter in ids:
            return letter
    # Unknown campaign: fall back to Option B (safe specialty default).
    if "B" in ids:
        return "B"
    return ids[_pick_index(len(ids), f"sp-option|{seed}|{_parse_day_key(day_key) or ''}")]


def option_field(
    option_id: str,
    field: str,
    *,
    fallback: str = "",
) -> str:
    block = canonical_options().get(str(option_id or "").upper()) or {}
    val = block.get(field)
    if val is None:
        return fallback
    return str(val).strip()


def pick_claim(
    seed: str,
    *,
    day_key: Union[date, datetime, str, None] = None,
    campaign: str = "",
    surface: str = "",
) -> str:
    """Caption / first-comment claim — Options A/B/C by campaign slot."""
    opt = resolve_option_id(
        seed, day_key=day_key, campaign=campaign, surface=surface
    )
    caption = option_field(opt, "caption")
    if caption:
        return caption
    return _pick(claims(), f"sp-claim|{seed}", _DEFAULT_CAPTION)


def pick_badge_claim(
    seed: str,
    *,
    style: Optional[str] = None,
    day_key: Union[date, datetime, str, None] = None,
    campaign: str = "",
    surface: str = "",
) -> str:
    """On-image / designed-in claim for Options A/B/C (style-aware)."""
    opt = resolve_option_id(
        seed, day_key=day_key, campaign=campaign, surface=surface
    )
    style_key = str(style or "").lower()
    if style_key == "top_banner":
        text = option_field(opt, "all_caps")
        if text:
            return text
    if style_key in ("footer_band",):
        text = option_field(opt, "on_image")
        if text:
            return text
    if style_key in ("ribbon", "medallion"):
        text = option_field(opt, "badge_short")
        if text:
            return text
    if style_key == "seal" or not style_key:
        text = option_field(opt, "badge_seal") or option_field(opt, "badge_short")
        if text:
            return text
    # Fall back to rotating style lists (still A/B/C vocabulary).
    if style:
        opts = badge_claims_for_style(style)
        fallback = {
            "seal": _DEFAULT_BADGE,
            "footer_band": option_field("B", "on_image", fallback=_DEFAULT_CAPTION.rstrip(".")),
            "top_banner": option_field("B", "all_caps", fallback="CHICAGOLAND'S #1 CRYSTAL SHOP & HOLISTIC CENTER"),
            "ribbon": "CHICAGO #1",
            "medallion": "Chicagoland’s #1",
        }.get(style_key, _DEFAULT_BADGE)
        return _pick(opts, f"sp-badge-claim|{style}|{seed}", fallback)
    return _pick(badge_claims(), f"sp-badge-claim|{seed}", _DEFAULT_BADGE)


def pick_badge_style(seed: str) -> str:
    styles = badge_styles()
    return styles[_pick_index(len(styles), f"sp-badge-style|{seed}")]


def always_first_comment() -> bool:
    """Founder Aug 14 2026: every FB/IG publish gets one Zernio firstComment."""
    cfg = social_proof_config()
    if "always_first_comment" in cfg:
        return bool(cfg.get("always_first_comment"))
    # Default ON — caption placement may still rotate; comment must not be skipped.
    return True


def pick_placement_mode(seed: str, *, campaign: str = "") -> str:
    """Where the claim appears this post: caption / first_comment / both.

    When always_first_comment is on, caption-only modes still get a first comment
    at plan time (treated as both for comment attachment).
    """
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


def never_overlay_existing() -> bool:
    """Hard policy: do not stamp badges onto finished inventory plates."""
    cfg = social_proof_config()
    # Default true — Founder Aug 11 ~3:05pm CT cutover.
    if "never_overlay_existing" in cfg:
        return bool(cfg.get("never_overlay_existing"))
    return bool(cfg.get("only_on_newly_generated", True))


def only_on_newly_generated() -> bool:
    return bool(social_proof_config().get("only_on_newly_generated", True))


def designed_in_required() -> bool:
    """Founder Aug 12 FINAL: every NEW gen/remake must include designed-in pride."""
    return bool(social_proof_config().get("designed_in_required", False))


def designed_in_on_new_generation() -> bool:
    """When True, NEW image generation prompts include a designed-in pride mark."""
    if designed_in_required():
        return True
    return bool(social_proof_config().get("designed_in_on_new_generation", False))


def badge_from_date() -> Optional[date]:
    """Optional America/Chicago cutover day for designed-in generation briefs."""
    raw = social_proof_config().get("badge_from_date")
    if not raw:
        return None
    try:
        return date.fromisoformat(str(raw)[:10])
    except ValueError:
        return None


def should_designed_in_for_day(day: Union[date, datetime, str, None] = None) -> bool:
    """True when a NEW-image generation must bake pride into the art brief.

    Never authorizes overlaying existing inventory. Overlay gates stay separate
    and remain false (`badge_on_morning_flyers` / `badge_on_night`).
    """
    if not enabled() or not designed_in_on_new_generation():
        return False
    cut = badge_from_date()
    if cut is None:
        return True
    if day is None:
        # Required + cutover set but no day → still require (agents must pass day).
        return bool(designed_in_required())
    if isinstance(day, datetime):
        d = day.date()
    elif isinstance(day, date):
        d = day
    else:
        try:
            d = date.fromisoformat(str(day)[:10])
        except ValueError:
            return bool(designed_in_required())
    return d >= cut


def designed_in_generation_brief(
    seed: str = "",
    *,
    day: Union[date, datetime, str, None] = None,
    surface: str = "morning",
    campaign: str = "",
    force_option: str = "",
) -> str:
    """Prompt fragment for NEW art only — boutique pride designed into the plate.

    REQUIRED for every new morning flyer / night creative / afternoon event art /
    celestial remake when designed_in_required is true. Returns "" only when
    designed-in is off / before badge_from_date. Never use this to justify
    overlaying finished flyers or pool creatives.

    Phrasing uses email Options A/B/C by campaign slot (Founder Aug 13 2026),
    e.g. morning/today → Premier (A), afternoon → #1 (B), night → Voted #1 (C).
    `force_option` (A/B/C) overrides slot pick — used by morning visual-style
    rotation so Magritte/Folk/Da Vinci/Einstein each carry distinct pride text
    while still reading as #1 / Premier / Voted Chicagoland.
    """
    # When required + enabled, always emit a brief for NEW gens (even if day
    # parsing failed) so agents cannot ship pride-free art by accident.
    if not should_designed_in_for_day(day):
        if not (enabled() and designed_in_required()):
            return ""
    styles = [
        str(s).strip().lower()
        for s in (social_proof_config().get("designed_in_prompt_styles") or ["seal", "top_banner"])
        if str(s).strip()
    ]
    styles = [s for s in styles if s in BADGE_STYLES] or ["seal", "top_banner"]
    style = styles[_pick_index(len(styles), f"sp-designed-in|{surface}|{seed}")]
    day_key = day if day is not None else seed
    camp = normalize_campaign(campaign, surface=surface)
    forced = str(force_option or "").strip().upper()
    if forced in ("A", "B", "C"):
        opt = forced
    else:
        opt = resolve_option_id(
            seed or str(day or "new"),
            day_key=day_key,
            campaign=camp,
            surface=surface,
        )
    # Prefer full on-image phrase for the generation brief (readable sentence case).
    claim = (
        option_field(opt, "on_image")
        or pick_badge_claim(
            seed or str(day or "new"),
            style=style,
            day_key=day_key,
            campaign=camp,
            surface=surface,
        ).replace("\n", " / ")
    )
    surface_key = str(surface or "morning").lower().strip()
    surface_bit = {
        "morning": "morning flyer",
        "night": "night / week-ahead creative",
        "week_ahead": "night / week-ahead creative",
        "afternoon": "afternoon event art",
        "afternoon_spotlight": "afternoon event art",
        "celestial": "celestial plate",
        "celestial_morning": "celestial plate",
        "celestial_night": "celestial plate",
    }.get(surface_key, f"{surface_key} creative")
    required_bit = (
        " REQUIRED on every NEW generation/remake."
        if designed_in_required()
        else ""
    )
    return (
        f" DESIGNED-IN SHOP PRIDE (new {surface_bit} only — not a post-hoc "
        f"sticker on old art).{required_bit} Elegantly bake a boutique '{style}' "
        f"pride mark into the composition with claim '{claim}' (rotating email "
        "Options A/B/C: Chicagoland’s Premier Crystal Store & Holistic "
        "Destination / Chicagoland’s #1 Crystal Shop & Holistic Center / "
        "Voted #1 Chicagoland’s Crystal Store & Holistic Destination). Deep "
        "eggplant or navy + gold for seals; cream band with dark ink for "
        "footer/banner. ALL CAPS OK on banners. Keep clear of event cards, "
        "Sacred Ground script wordmark, and the circular sun logo. Warm shop "
        "pride — not a fake award citation."
    )


def should_badge_morning(seed: str) -> bool:
    """Live overlay on morning flyers — permanently gated OFF for inventory.

    Founder cutover: never stamp existing plates. Designed-in pride for NEW
    generations uses designed_in_generation_brief() instead.
    """
    if never_overlay_existing():
        return False
    if not enabled() or not social_proof_config().get("badge_on_morning_flyers", False):
        return False
    return _pick_index(5, f"sp-mf-badge|{seed}") != 0


def should_badge_night(*, mode: str = "", creative_id: str = "", seed: str = "") -> bool:
    """Live overlay on night plates — gated OFF; never touch celestial/pool inventory."""
    if never_overlay_existing():
        return False
    if not enabled() or not social_proof_config().get("badge_on_night", False):
        return False
    if social_proof_config().get("badge_skip_celestial", True):
        m = (mode or "").lower()
        cid = (creative_id or "").lower()
        if m == "celestial" or "celestial" in cid:
            return False
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
    option_id = resolve_option_id(seed, day_key=day_key, campaign=campaign)
    claim = (
        pick_claim(seed, day_key=day_key, campaign=campaign)
        if mode != MODE_SKIP
        else ""
    )
    badge_style = pick_badge_style(seed)
    badge_text = pick_badge_claim(
        seed, style=badge_style, day_key=day_key, campaign=campaign
    )
    in_caption = mode in (MODE_CAPTION, MODE_BOTH) and bool(claim)
    in_comment = (
        mode in (MODE_FIRST_COMMENT, MODE_BOTH)
        and bool(claim)
        and first_comment_supported(platform)
    )
    # Founder Aug 14: never skip the first comment on supported platforms.
    if (
        always_first_comment()
        and bool(claim)
        and first_comment_supported(platform)
        and mode != MODE_SKIP
    ):
        in_comment = True
    # If first_comment was chosen but platform unsupported, keep claim in caption.
    if mode == MODE_FIRST_COMMENT and not in_comment and claim:
        in_caption = True
    # Record effective mode so drafts / dry-runs show comment will ship.
    effective_mode = mode
    if in_comment and in_caption and mode == MODE_CAPTION:
        effective_mode = MODE_BOTH
    elif in_comment and not in_caption:
        effective_mode = MODE_FIRST_COMMENT
    return {
        "enabled": enabled() and mode != MODE_SKIP,
        "mode": effective_mode,
        "option": option_id,
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
        "option": plan.get("option") or "",
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
        "gold_bright": _rgb("gold_bright", (232, 198, 110)),
        "ink": _rgb("ink", (28, 22, 40)),
        "cream": _rgb("cream", (250, 245, 232)),
        "eggplant": _rgb("eggplant", (42, 24, 58)),
        "navy": _rgb("navy", (22, 32, 58)),
    }


def _font(size: int, *, bold: bool = True, serif: bool = True):
    from PIL import ImageFont

    if serif and bold:
        candidates = [
            "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
            "/Library/Fonts/Merriweather_Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ]
    elif serif:
        candidates = [
            "/System/Library/Fonts/Supplemental/Georgia.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
            "/Library/Fonts/Merriweather_Regular.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
    elif bold:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Black.ttf",
            "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Georgia.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def _badge_font(size: int):
    """Default bold serif for badges."""
    return _font(size, bold=True, serif=True)


def _wrap_lines(text: str) -> List[str]:
    lines: List[str] = []
    for raw in str(text).replace("\\n", "\n").split("\n"):
        bit = raw.strip()
        if bit:
            lines.append(bit)
    return lines or ["Chicagoland favorite"]


def _one_line(lines: Sequence[str], *, max_chars: int = 52) -> str:
    """Join badge lines for single-line formats."""
    one = " · ".join(str(ln).strip() for ln in lines if str(ln).strip())
    one = " ".join(one.split())
    if len(one) > max_chars:
        one = one[: max_chars - 1].rstrip(" ·-–—") + "…"
    return one or "Chicagoland favorite"


def _fit_lines(lines: Sequence[str], *, max_lines: int = 2) -> List[str]:
    cleaned = [str(ln).strip() for ln in lines if str(ln).strip()]
    if not cleaned:
        return ["Chicago’s #1", "Crystal Shop"]
    if len(cleaned) <= max_lines:
        return cleaned
    head = list(cleaned[: max_lines - 1])
    tail = " ".join(cleaned[max_lines - 1 :])
    head.append(tail)
    return head


def _draw_centered_lines(
    draw, lines: Sequence[str], *, cx: int, cy: int, font, fill, gap: int = 3
) -> None:
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


def _draw_seal(base, *, lines: Sequence[str], cols: Dict, w: int, h: int, pb: int, pad: int):
    """Boutique wax seal: deep eggplant disc + gold ring + gold text."""
    from PIL import Image, ImageDraw, ImageFilter

    gold = cols["gold"]
    gold_bright = cols["gold_bright"]
    eggplant = cols["eggplant"]
    navy = cols["navy"]

    # 16–20% of image width — substantial, not a chip sticker.
    diam = max(130, int(w * 0.175))
    diam = min(diam, int(w * 0.195))
    rx = ry = diam // 2

    # True empty margin: snug top-right corner of photo area — clear of
    # header script / event cards (left) / sun logo (bottom-left).
    cx = w - rx - max(8, int(pad * 0.55))
    cy = ry + max(8, int(pad * 0.55))
    cy = min(cy, pb - ry - 4)
    cy = max(cy, ry + 6)

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    # Soft drop shadow
    sh = max(5, int(w * 0.009))
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse(
        (cx - rx + sh, cy - ry + sh, cx + rx + sh, cy + ry + sh),
        fill=(8, 4, 16, 130),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=max(3, sh // 2)))
    overlay = Image.alpha_composite(overlay, shadow)
    draw = ImageDraw.Draw(overlay)

    # Outer gold glow (thin — does not wash out the disc)
    glow = max(2, int(w * 0.0035))
    draw.ellipse(
        (cx - rx - glow, cy - ry - glow, cx + rx + glow, cy + ry + glow),
        fill=(*gold, 70),
    )
    # Fully opaque deep eggplant disc (never translucent charcoal)
    rim = max(7, int(w * 0.009))
    draw.ellipse(
        (cx - rx, cy - ry, cx + rx, cy + ry),
        fill=(*eggplant, 255),
        outline=(*gold, 255),
        width=rim,
    )
    # Subtle navy depth ring (opaque, not a wash over art)
    inner = max(10, rx - rim - 3)
    draw.ellipse(
        (cx - inner, cy - inner, cx + inner, cy + inner),
        fill=(*navy, 255),
    )
    # Soft eggplant center so text field stays rich, not flat black
    core = max(8, int(inner * 0.92))
    draw.ellipse(
        (cx - core, cy - core, cx + core, cy + core),
        fill=(*eggplant, 255),
    )
    # Inner gold decorative ring
    ring_r = max(14, rx - max(16, int(rx * 0.20)))
    draw.ellipse(
        (cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r),
        outline=(*gold_bright, 240),
        width=max(2, int(w * 0.004)),
    )

    seal_lines = _fit_lines(lines, max_lines=2)
    text_box_w = int(ring_r * 1.68)
    text_box_h = int(ring_r * 1.40)
    font, gap = _seal_font_for(
        draw,
        seal_lines,
        max_w=text_box_w,
        max_h=text_box_h,
        start=max(22, int(diam * 0.165)),
    )
    # Bright gold text on opaque dark disc — high contrast
    _draw_centered_lines(
        draw, seal_lines, cx=cx, cy=cy, font=font, fill=(*gold_bright, 255), gap=gap
    )

    return Image.alpha_composite(base, overlay)


def _draw_footer_band(base, *, lines: Sequence[str], cols: Dict, w: int, h: int, pad: int):
    """Extend canvas with a proper cream brand band — poster footer, not a sticker."""
    from PIL import Image, ImageDraw

    gold = cols["gold"]
    gold_bright = cols["gold_bright"]
    ink = cols["ink"]
    cream = cols["cream"]

    band_h = max(72, int(w * 0.078))
    new_h = h + band_h
    out = Image.new("RGBA", (w, new_h), (*cream, 255))
    out.paste(base, (0, 0))
    draw = ImageDraw.Draw(out)
    y0 = h

    # Cream field
    draw.rectangle((0, y0, w, new_h), fill=(*cream, 255))
    # Gold double rules (ticket / boutique poster energy)
    draw.line((pad, y0 + 8, w - pad, y0 + 8), fill=(*gold, 255), width=2)
    draw.line((pad, y0 + 12, w - pad, y0 + 12), fill=(*gold, 140), width=1)
    draw.line((pad, new_h - 10, w - pad, new_h - 10), fill=(*gold, 200), width=2)
    draw.line((pad, new_h - 6, w - pad, new_h - 6), fill=(*gold_bright, 120), width=1)

    # Small gold diamond accents
    mid_y = y0 + band_h // 2
    for ax in (pad + 10, w - pad - 10):
        d = 5
        draw.polygon(
            [(ax, mid_y - d), (ax + d, mid_y), (ax, mid_y + d), (ax - d, mid_y)],
            fill=(*gold, 220),
        )

    one = _one_line(lines, max_chars=48)
    # Elegant serif primary
    font = _font(max(22, int(w * 0.030)), bold=True, serif=True)
    bbox = draw.textbbox((0, 0), one, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    if tw > w - 2 * pad - 40:
        font = _font(max(16, int(w * 0.024)), bold=True, serif=True)
        bbox = draw.textbbox((0, 0), one, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # Dark ink on cream — high contrast (never lavender strip / purple ink wash)
    draw.text(
        ((w - tw) // 2, y0 + (band_h - th) // 2 - 1),
        one,
        font=font,
        fill=(*ink, 255),
    )
    return out


def _draw_top_banner(base, *, lines: Sequence[str], cols: Dict, w: int, h: int, pad: int):
    """Full-width cream hairline bar at the very top — premium ticket stub."""
    from PIL import Image, ImageDraw

    gold = cols["gold"]
    gold_bright = cols["gold_bright"]
    cream = cols["cream"]

    band_h = max(28, int(h * 0.03))
    band_h = min(band_h, int(h * 0.038))
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    draw.rectangle((0, 0, w, band_h), fill=(*cream, 248))
    draw.line((0, band_h - 1, w, band_h - 1), fill=(*gold, 255), width=2)
    draw.line((0, 0, w, 0), fill=(*gold, 180), width=1)

    one = _one_line(lines, max_chars=46).upper()
    font = _font(max(14, int(band_h * 0.50)), bold=True, serif=False)
    bbox = draw.textbbox((0, 0), one, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    if tw > w - 2 * pad:
        font = _font(max(12, int(band_h * 0.42)), bold=True, serif=False)
        bbox = draw.textbbox((0, 0), one, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # Gold endcaps + gold text on cream (ticket stub)
    draw.line((pad // 2, band_h // 2, pad, band_h // 2), fill=(*gold_bright, 255), width=2)
    draw.line(
        (w - pad, band_h // 2, w - pad // 2, band_h // 2),
        fill=(*gold_bright, 255),
        width=2,
    )
    # Deep gold / ink-darkened gold for readability on cream
    fill = (120, 88, 28, 255)  # dark antique gold — high contrast on cream
    draw.text(((w - tw) // 2, (band_h - th) // 2 - 1), one, font=font, fill=fill)
    return Image.alpha_composite(base, overlay)


def _draw_ribbon(base, *, lines: Sequence[str], cols: Dict, w: int, h: int, pb: int, pad: int):
    """Folded gold corner ribbon — short elegant claim, corner only (not a sash)."""
    from PIL import Image, ImageDraw, ImageFilter

    gold = cols["gold"]
    gold_bright = cols["gold_bright"]
    eggplant = cols["eggplant"]
    ink = cols["ink"]

    one = _one_line(lines, max_chars=12).upper()
    # Corner arm large enough that full claim sits on the diagonal
    arm = max(140, int(w * 0.28))
    band = max(30, int(w * 0.040))

    # Strip length ~ diagonal of the corner triangle
    strip_w = max(int(arm * 1.25), int(arm * 1.414) - band)
    strip_h = band
    ribbon = Image.new("RGBA", (strip_w, strip_h + 8), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ribbon)
    rd.rectangle((0, 4, strip_w, strip_h + 4), fill=(*gold, 255))
    rd.rectangle((0, 4, strip_w, 7), fill=(*gold_bright, 255))
    rd.rectangle((0, strip_h + 1, strip_w, strip_h + 4), fill=(*eggplant, 80))
    # Soft end fades (fold suggestion)
    for i in range(10):
        a = int(90 * (1 - i / 10))
        rd.line((i, 4, i, strip_h + 4), fill=(20, 12, 30, a))
        rd.line((strip_w - 1 - i, 4, strip_w - 1 - i, strip_h + 4), fill=(20, 12, 30, a))

    font = _font(max(14, int(strip_h * 0.52)), bold=True, serif=False)
    bbox = rd.textbbox((0, 0), one, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    while tw > strip_w - 16 and font.size > 11:  # type: ignore[attr-defined]
        font = _font(font.size - 1, bold=True, serif=False)  # type: ignore[attr-defined]
        bbox = rd.textbbox((0, 0), one, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    rd.text(
        ((strip_w - tw) // 2, 4 + (strip_h - th) // 2 - 1),
        one,
        font=font,
        fill=(*ink, 255),
    )

    angled = ribbon.rotate(45, expand=True, resample=Image.BICUBIC)
    aw, ah = angled.size
    # Center strip on the corner diagonal midpoint so full text is visible
    mid_x = w - arm / 2.0
    mid_y = arm / 2.0
    ox = int(mid_x - aw / 2)
    oy = int(mid_y - ah / 2)

    # Corner mask — slightly larger than the tip triangle so the claim fits
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    inset = max(6, band // 3)
    md.polygon(
        [
            (w - arm - inset, 0),
            (w, 0),
            (w, arm + inset),
        ],
        fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(radius=1))

    alpha = angled.split()[-1]
    dark = Image.new("RGBA", (aw, ah), (12, 6, 20, 0))
    dark.putalpha(alpha.point(lambda a: int(a * 0.40)))

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh_layer.paste(dark, (ox + 2, oy + 3), dark)
    sh_layer = sh_layer.filter(ImageFilter.GaussianBlur(radius=2))
    rib_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rib_layer.paste(angled, (ox, oy), angled)

    for layer in (sh_layer, rib_layer):
        r, g, b, a = layer.split()
        a = Image.composite(a, Image.new("L", (w, h), 0), mask)
        overlay = Image.alpha_composite(overlay, Image.merge("RGBA", (r, g, b, a)))

    return Image.alpha_composite(base, overlay)


def _draw_medallion(base, *, lines: Sequence[str], cols: Dict, w: int, h: int, pb: int, pad: int):
    """Small oval gold medallion near bottom — clear of circular sun logo."""
    from PIL import Image, ImageDraw, ImageFilter

    gold = cols["gold"]
    gold_bright = cols["gold_bright"]
    eggplant = cols["eggplant"]
    cream = cols["cream"]
    ink = cols["ink"]

    # Small — ~9–11% width so it never fights the logo (~10–13% BL)
    ow = max(92, int(w * 0.105))
    oh = max(58, int(ow * 0.64))
    rx, ry = ow // 2, oh // 2

    # Bottom-right of photo area — near logo zone but NOT covering BL sun logo
    logo_clear = max(pad, int(w * 0.20))
    cx = w - rx - pad - max(4, int(w * 0.01))
    cy = pb - ry - max(pad, int(w * 0.016))
    cx = max(cx, logo_clear + rx)
    cy = min(cy, pb - ry - 4)
    cy = max(cy, int(h * 0.55))

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sh = max(3, int(w * 0.005))
    sd.ellipse(
        (cx - rx + sh, cy - ry + sh, cx + rx + sh, cy + ry + sh),
        fill=(12, 8, 20, 110),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=max(2, sh // 2)))
    overlay = Image.alpha_composite(overlay, shadow)
    draw = ImageDraw.Draw(overlay)

    # Thick gold bezel (reads as a real medallion, not a white sticker)
    draw.ellipse(
        (cx - rx, cy - ry, cx + rx, cy + ry),
        fill=(*gold, 255),
        outline=(*gold_bright, 255),
        width=max(2, int(w * 0.003)),
    )
    # Warm antique-gold mid ring
    mid_x = max(3, int(rx * 0.10))
    mid_y = max(2, int(ry * 0.12))
    draw.ellipse(
        (cx - rx + mid_x, cy - ry + mid_y, cx + rx - mid_x, cy + ry - mid_y),
        fill=(196, 158, 72, 255),
    )
    # Cream cartouche for dark ink (high contrast)
    inset_x = max(6, int(rx * 0.22))
    inset_y = max(5, int(ry * 0.24))
    draw.ellipse(
        (cx - rx + inset_x, cy - ry + inset_y, cx + rx - inset_x, cy + ry - inset_y),
        fill=(*cream, 255),
        outline=(*eggplant, 70),
        width=1,
    )
    draw.ellipse(
        (
            cx - rx + inset_x + 2,
            cy - ry + inset_y + 2,
            cx + rx - inset_x - 2,
            cy + ry - inset_y - 2,
        ),
        outline=(*gold, 180),
        width=1,
    )

    med_lines = _fit_lines(lines, max_lines=2)
    if len(med_lines) == 1 and len(med_lines[0]) > 12:
        med_lines = [med_lines[0][:14]]
    font, gap = _seal_font_for(
        draw,
        med_lines,
        max_w=int((rx - inset_x) * 1.65),
        max_h=int((ry - inset_y) * 1.45),
        start=max(13, int(ow * 0.17)),
    )
    _draw_centered_lines(
        draw, med_lines, cx=cx, cy=cy, font=font, fill=(*ink, 255), gap=gap
    )
    return Image.alpha_composite(base, overlay)


def draw_badge(
    img,
    *,
    style: str,
    text: str,
    photo_bottom: Optional[int] = None,
):
    """Draw a designed-in social-proof mark; returns (new_image, style_drawn).

    Styles (Founder Aug 11 ~3pm CT v4 remake — preview only until approved):
    - seal: deep eggplant disc + gold ring + gold text (~16–20% width)
    - footer_band: cream brand band extending the canvas (poster footer)
    - top_banner: full-width cream hairline bar at top (~3% height)
    - ribbon: diagonal gold corner sash, short claim
    - medallion: small oval gold mark near bottom, clear of sun logo

    photo_bottom = Y above cream/contact footer (default: full height).
    """
    style = (style or "seal").lower()
    if style not in BADGE_STYLES:
        style = "seal"
    lines = _wrap_lines(text)
    cols = _colors()

    base = img.convert("RGBA")
    w, h = base.size
    pb = photo_bottom if photo_bottom is not None else h
    pad = max(12, int(w * 0.02))

    if style == "footer_band":
        out = _draw_footer_band(base, lines=lines, cols=cols, w=w, h=h, pad=pad)
    elif style == "top_banner":
        out = _draw_top_banner(base, lines=lines, cols=cols, w=w, h=h, pad=pad)
    elif style == "ribbon":
        out = _draw_ribbon(base, lines=lines, cols=cols, w=w, h=h, pb=pb, pad=pad)
    elif style == "medallion":
        out = _draw_medallion(base, lines=lines, cols=cols, w=w, h=h, pb=pb, pad=pad)
    else:
        out = _draw_seal(base, lines=lines, cols=cols, w=w, h=h, pb=pb, pad=pad)

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
    """Legacy overlay helper — refused while never_overlay_existing is true.

    Do not use on finished inventory. Designed-in pride for NEW art goes through
    designed_in_generation_brief() in generation prompts.
    """
    if never_overlay_existing():
        return None
    if not enabled() or not path or not os.path.isfile(path):
        return None
    from PIL import Image

    style = force_style or pick_badge_style(seed)
    text = (
        force_text
        if force_text is not None
        else pick_badge_claim(seed, style=style)
    )
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
