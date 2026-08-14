"""Cheryl-style date-keyed morning flyers — generate, validate, register."""
from __future__ import annotations

import json
import math
import os
import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .ingest import parse_tec_datetime, today_local
from .models import Event
from .paths import CONFIG_DIR, ROOT, write_json

FLYERS_PATH = os.path.join(CONFIG_DIR, "morning_flyers.json")
ASSETS_DIR = os.path.join(ROOT, "assets")
LOGO_PATH = os.path.join(
    CONFIG_DIR, "brand", "sacred-ground-logo-circle-transparent.png"
)
TINA_CIRCLE_REFS = (
    os.path.join(ASSETS_DIR, "ref-tina-circle-from-meditation.png"),
    os.path.join(ASSETS_DIR, "ref-tina-circle-from-tarot.png"),
)

WEBSITE = "shopsacredground.com"
PHONE = "847-749-3922"
MAX_EVENTS_ON_FLYER = 3
CANVAS = 1080

# Dollar amounts / ticket-style prices — never on morning flyer graphics.
PRICE_RE = re.compile(
    r"""
    \$ \s* \d |                  # $55, $ 99
    \d+ \s* \$ |                 # 55$
    (?:^|[^\w]) (?:USD|CAD) \b | # currency codes as price
    \b (?:ticket|tickets|admission) \s* [:–-]?\s* \$?\d |
    \b \d{1,4} (?:\.\d{2})? \s* (?:dollars?|bucks) \b
    """,
    re.IGNORECASE | re.VERBOSE,
)

# ~75% Thursday-style clear cards; up to ~25% artistic single-event hero.
THURSDAY_CARDS_SHARE = 0.75
LAYOUT_THURSDAY = "thursday_cards"
LAYOUT_ARTISTIC = "artistic_hero"

NOTES = (
    "Sacred Ground daily flyer template (Thursday-style): gold standard "
    "assets/sg-morning-flyer-2026-08-06-today-collage.png. ~75% of new/future "
    "morning flyers MUST use Thursday-style clear stacked EQUAL event cards "
    "(left cards + right graphics + logo footer) — multi-event days give "
    "EVERY practitioner the SAME card size / visual weight (gold standard "
    "Aug 6). FORBIDDEN: one hero photo + tiny ALSO TODAY corner badge "
    "(Aug 7 FB reflexology/Robert rejected). Up to ~25% may be artistic "
    "single-event hero layouts ONLY when there is exactly one event. Header "
    "WEEKDAY AT Sacred Ground + Mind • Body • Spirit • Community; LEFT stacked rounded event "
    "cards; RIGHT evocative graphics in clear zones; FOOTER logo + "
    f"{WEBSITE} + {PHONE} + come-as-you-are. COLOR ENERGY (Founder Aug 10 "
    "2026): FB and IG plates MUST be colorful, bright, interesting, and "
    "engaging — jewel tones, strong contrast, rich accents (gold / emerald / "
    "amethyst / teal / amber). FORBIDDEN: drab, muddy, beige, grey, "
    "desaturated purple AI sludge, empty near-black voids, low-saturation "
    "washes, thin faint line-art on a dead field (Aug 10 IG Lisa Maria "
    "muddy-purple empty-card plate rejected). Dark elegant backgrounds OK "
    "ONLY when lit with bright jewel accents like the Aug 6 gold standard. "
    "Versions of the system, not exact clones. Date-keyed flyers are "
    "prebranded (skip overlays). SINGLE-IMAGE MODE (Founder Aug 10 2026): "
    "one excellent primary plate (`url` / `local`) posts to BOTH Facebook "
    "and Instagram. Do not generate or require a separate weaker "
    "`url_instagram` variant — Aug 10 Lisa Maria IG muddy-purple plate "
    "proved dual variants hurt quality. Legacy `url_instagram` is ignored "
    "unless entry sets allow_ig_variant:true. Primary plate must pass "
    "flyer_passes_visual_energy. NEVER include $, dollar amounts, ticket "
    "costs, or \"$55\"-style prices on flyer graphics. Empty days get a "
    "warm visit flyer. 1–3 events max. No invented practitioner faces."
)

# Founder Aug 10 2026 — share one excellent primary plate on FB+IG.
# Opt-in only: entry["allow_ig_variant"] = true to use url_instagram again.
ALLOW_IG_VARIANT_KEY = "allow_ig_variant"

# Visual-energy gate (Founder Aug 10, 2026) — reject drab/muddy plates.
# Gold standard ~cf 50 / accents ~0.22; Aug 10 bad IG ~cf 18 / accents ~0.001.
MIN_FLYER_COLORFULNESS = 28.0
MIN_FLYER_ACCENT_RATIO = 0.05
MAX_SINGLE_CARD_HEIGHT = 300

# Founder-approved gold standard — do not overwrite or force a second variant.
PROTECTED_DAYS = frozenset({"2026-08-06"})

VARIANT_A = "a"
VARIANT_B = "b"


def text_has_price(text: str) -> bool:
    """True if text looks like it contains a price / dollar amount."""
    if not text:
        return False
    return bool(PRICE_RE.search(str(text)))


def assert_price_free(*parts: str) -> None:
    bad = [p for p in parts if p and text_has_price(p)]
    if bad:
        raise ValueError(f"Morning flyer must not include prices: {bad!r}")


def flyer_visual_energy(path: str) -> Dict[str, float]:
    """Score colorfulness / accent density for a local flyer PNG.

    Rejects drab muddy low-saturation plates (Founder Aug 10, 2026).
    """
    import colorsys

    from PIL import Image

    if not path or not os.path.isfile(path):
        return {
            "colorfulness": 0.0,
            "sat_mean": 0.0,
            "accent_ratio": 0.0,
            "near_black": 1.0,
        }
    im = Image.open(path).convert("RGB").resize((120, 120))
    sats: List[float] = []
    lums: List[float] = []
    rg: List[float] = []
    yb: List[float] = []
    for r, g, b in im.getdata():
        _h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        sats.append(s)
        lums.append(l)
        rg.append(float(r - g))
        yb.append(0.5 * (r + g) - float(b))

    def _mstd(vals: List[float]) -> Tuple[float, float]:
        m = sum(vals) / len(vals)
        var = sum((x - m) ** 2 for x in vals) / len(vals)
        return m, var**0.5

    rg_m, rg_s = _mstd(rg)
    yb_m, yb_s = _mstd(yb)
    colorfulness = (rg_s**2 + yb_s**2) ** 0.5 + 0.3 * (rg_m**2 + yb_m**2) ** 0.5
    accent_ratio = sum(
        1 for s, l in zip(sats, lums) if s > 0.35 and 0.2 < l < 0.85
    ) / len(sats)
    near_black = sum(1 for l in lums if l < 0.12) / len(lums)
    return {
        "colorfulness": round(colorfulness, 2),
        "sat_mean": round(sum(sats) / len(sats), 3),
        "accent_ratio": round(accent_ratio, 3),
        "near_black": round(near_black, 3),
    }


def flyer_passes_visual_energy(path: str) -> bool:
    """True when a plate is colorful/bright enough for FB or IG."""
    m = flyer_visual_energy(path)
    return (
        m["colorfulness"] >= MIN_FLYER_COLORFULNESS
        and m["accent_ratio"] >= MIN_FLYER_ACCENT_RATIO
    )


def _abs_asset(path: str) -> str:
    if not path:
        return ""
    if os.path.isabs(path):
        return path
    return os.path.join(ROOT, path)


def entry_fails_visual_energy(entry: Optional[Dict[str, Any]]) -> List[str]:
    """Platforms whose local flyer PNGs fail the color-energy gate.

    Single-image mode: only the primary `local` plate is gated unless
    `allow_ig_variant` is explicitly enabled.
    """
    if not isinstance(entry, dict):
        return []
    failed: List[str] = []
    keys = [("facebook", "local")]
    if entry.get(ALLOW_IG_VARIANT_KEY):
        keys.append(("instagram", "local_instagram"))
    for platform, key in keys:
        local = str(entry.get(key) or "").strip()
        abs_path = _abs_asset(local)
        if abs_path and os.path.isfile(abs_path) and not flyer_passes_visual_energy(
            abs_path
        ):
            failed.append(platform)
    return failed


def load_flyers_config() -> Dict[str, Any]:
    if not os.path.isfile(FLYERS_PATH):
        return {"notes": NOTES, "prebranded_default": True, "flyers": {}}
    with open(FLYERS_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        return {"notes": NOTES, "prebranded_default": True, "flyers": {}}
    data.setdefault("flyers", {})
    data.setdefault("prebranded_default", True)
    data["notes"] = NOTES
    return data


def save_flyers_config(data: Dict[str, Any]) -> None:
    data = dict(data)
    data["notes"] = NOTES
    data.setdefault("prebranded_default", True)
    data.setdefault("flyers", {})
    # Validate all text fields are price-free before write.
    for day_key, entry in (data.get("flyers") or {}).items():
        if not isinstance(entry, dict):
            continue
        bits = [str(entry.get("label") or "")]
        bits.extend(str(c) for c in (entry.get("covers") or []))
        for line in entry.get("lines") or []:
            bits.append(str(line))
        assert_price_free(*bits)
    write_json(FLYERS_PATH, data)
    try:
        from . import images

        images.morning_flyers.cache_clear()
    except Exception:
        pass


def flyer_entry_for_day(day: date) -> Optional[Dict[str, Any]]:
    flyers = load_flyers_config().get("flyers") or {}
    entry = flyers.get(day.isoformat())
    return entry if isinstance(entry, dict) else None


def resolve_flyer_urls(entry: Dict[str, Any]) -> Tuple[str, str]:
    """
    Return (facebook_url, instagram_url) for a morning_flyers date entry.

    Single-image mode (default): both return primary `url` / `urls[0]`.
    Only when `allow_ig_variant` is true: IG may use `url_instagram` / `urls[1]`.
    """
    fb = str(entry.get("url") or "").strip()
    urls = [str(u).strip() for u in (entry.get("urls") or []) if str(u).strip()]
    if not fb and urls:
        fb = urls[0]
    if not entry.get(ALLOW_IG_VARIANT_KEY):
        return fb, fb
    ig = str(entry.get("url_instagram") or "").strip()
    if not ig and len(urls) >= 2:
        ig = urls[1]
    if not ig:
        ig = fb
    return fb, ig


def select_flyer_url_for_platform(
    entry: Dict[str, Any],
    platform: Optional[str] = None,
) -> Tuple[str, bool]:
    """
    Pick the flyer URL for a platform.

    Default (Founder Aug 10 2026): primary `url` for BOTH Facebook and Instagram.
    Returns (url, shared). `shared` is True in single-image mode (by design).
    Dual IG variants only when entry.allow_ig_variant is true.
    """
    fb, ig = resolve_flyer_urls(entry)
    if not fb and not ig:
        return "", False
    key = (platform or "").lower().strip()
    allow_ig = bool(entry.get(ALLOW_IG_VARIANT_KEY))
    if allow_ig and key in ("instagram", "ig"):
        chosen = ig or fb
    else:
        # Single-image mode: always prefer the stronger/primary Facebook plate.
        chosen = fb or ig
    shared = (not allow_ig) or (len({u for u in (fb, ig) if u}) < 2)
    return chosen, shared


def has_dual_flyer_variants(entry: Dict[str, Any]) -> bool:
    """True when allow_ig_variant and two distinct public flyer URLs are set."""
    if not entry.get(ALLOW_IG_VARIANT_KEY):
        return False
    fb, ig = resolve_flyer_urls(entry)
    return bool(fb and ig and fb != ig)


def _short_title(title: str) -> str:
    t = (title or "").strip()
    for sep in (" — ", " - ", ": ", " with ", " With ", " w/ ", " W/ "):
        if sep in t:
            t = t.split(sep)[0].strip()
            break
    return t[:72]


def _slug_bit(title: str) -> str:
    raw = re.sub(r"[^a-z0-9]+", "-", _short_title(title).lower()).strip("-")
    return (raw or "today")[:28]


def _format_time(dt: datetime) -> str:
    h = dt.strftime("%I").lstrip("0") or "0"
    m = dt.strftime("%M")
    ampm = dt.strftime("%p")
    if m == "00":
        return f"{h} {ampm}"
    return f"{h}:{m} {ampm}"


def _event_time_line(ev: Event) -> str:
    start = parse_tec_datetime(ev.start_date)
    end = parse_tec_datetime(ev.end_date) if ev.end_date else None
    if not start:
        return ""
    if ev.all_day:
        return "All day"
    if end and end.date() == start.date() and end > start:
        return f"{_format_time(start)} – {_format_time(end)}"
    return _format_time(start)


def pick_events_for_flyer(events: Sequence[Event], limit: int = MAX_EVENTS_ON_FLYER) -> List[Event]:
    """Prefer featured/special, then earlier start; hard-cap for graphic space."""
    scored: List[Tuple[int, str, int, Event]] = []
    for ev in events:
        score = 0
        if getattr(ev, "featured", False) or getattr(ev, "is_special", False):
            score += 10
        low = (ev.title or "").lower()
        if "meditation" in low:
            score += 4
        if any(k in low for k in ("sound bath", "shaman", "quantum", "reflexology", "chakra")):
            score += 3
        eid = int(getattr(ev, "id", 0) or 0)
        scored.append((-score, ev.start_date or "", eid, ev))
    scored.sort()
    return [e for _, __, ___, e in scored[: max(0, limit)]]


def choose_layout_style(
    day: date,
    events: Optional[Sequence[Event]] = None,
    *,
    force: Optional[str] = None,
) -> str:
    """
    Deterministic layout mix: ~75% thursday_cards, ~25% artistic_hero.

    Multi-event days (2+) always prefer Thursday-style cards for readability.
    Single-event / empty days may roll the artistic 25% bucket via day hash.
    """
    if force in (LAYOUT_THURSDAY, LAYOUT_ARTISTIC):
        return force
    picked = pick_events_for_flyer(events or [])
    if len(picked) >= 2:
        return LAYOUT_THURSDAY
    # Stable ~25% artistic: day ordinal mod 4 == 0 → artistic (1/4).
    if (day.toordinal() % 4) == 0 and len(picked) <= 1:
        return LAYOUT_ARTISTIC
    return LAYOUT_THURSDAY


def build_flyer_copy(day: date, events: Sequence[Event]) -> Dict[str, Any]:
    """Price-free copy block for a day's flyer (empty → visit day)."""
    picked = pick_events_for_flyer(events)
    weekday = day.strftime("%A").upper()
    date_line = f"{day.strftime('%B')} {day.day}, {day.year}"
    date_short = f"{weekday} · {day.strftime('%B').upper()} {day.day}"

    if not picked:
        label = "Sacred Ground — visit us"
        covers: List[str] = []
        lines = [
            "SACRED GROUND",
            "Crystals · readings · quiet wonder",
            "Come browse · Arlington Heights",
            date_short,
        ]
        slug = "visit"
        primary = "Sacred Ground Visit"
        also: List[str] = []
    else:
        primary_ev = picked[0]
        primary = _short_title(primary_ev.title)
        covers = [ev.title for ev in picked]
        # Never include cost — strip if somehow embedded in title (defensive).
        covers = [re.sub(r"\$\s*\d[\d.,]*", "", c).strip(" -·|") for c in covers]
        label = " + ".join(_short_title(e.title) for e in picked[:2])
        if len(picked) > 2:
            label += " +"
        time_line = _event_time_line(primary_ev)
        lines = [
            primary.upper() if len(primary) < 40 else primary,
            time_line,
            date_short,
            "Arlington Heights",
        ]
        also = [_short_title(e.title) for e in picked[1:]]
        slug = _slug_bit(primary_ev.title)

    # Strip empties; assert no prices anywhere.
    lines = [ln for ln in lines if ln]
    assert_price_free(label, *covers, *lines, *also, primary)

    return {
        "label": label,
        "covers": covers,
        "lines": lines,
        "primary": primary,
        "also": also,
        "date_line": date_line,
        "date_short": date_short,
        "slug": slug,
        "empty_day": not bool(picked),
    }


def build_generation_prompt(
    day: date,
    copy: Dict[str, Any],
    *,
    layout: Optional[str] = None,
    events: Optional[Sequence[Event]] = None,
    variant: str = VARIANT_A,
) -> str:
    """Prompt for mlimg / GenerateImage polish — defaults to Thursday-style cards.

    `variant` a = Facebook (cleaner gold-standard card energy OK);
    `variant` b = Instagram — same full-day cards, richer background pop required.
    """
    covers = list(copy.get("covers") or [])
    events_bit = ""
    if covers:
        events_bit = " Events on equal cards: " + " · ".join(covers[:3]) + "."
    visit = ""
    if copy.get("empty_day"):
        visit = (
            " Empty calendar visit day: warm invite to come into Sacred Ground "
            "(crystals, quiet wonder) — not a plain storefront photo."
        )
    style = layout or choose_layout_style(day, events)
    n_events = len(pick_events_for_flyer(events or []))
    # Multi-event days never use artistic hero (equal cards only).
    if n_events >= 2:
        style = LAYOUT_THURSDAY
    weekday = day.strftime("%A").upper()
    key = (variant or VARIANT_A).lower().strip()
    is_b = key in (VARIANT_B, "b", "ig", "instagram", "alt")
    equal_rule = (
        " EQUAL SPACE RULE (hard): when 2+ events appear, every event gets the "
        "SAME card size and visual weight — stacked equal rounded cards like "
        "the Aug 6 gold standard. FORBIDDEN: one large hero photo/title with a "
        "tiny ALSO TODAY / secondary corner badge for another practitioner."
    )
    free_bit = ""
    if events:
        from .classify import is_free_community_event

        free_titles = [
            _short_title(e.title)
            for e in pick_events_for_flyer(events)
            if is_free_community_event(e)
        ]
        if free_titles:
            free_bit = (
                " Free community events on equal cards must show FREE or "
                "Free Community on the card itself (OK — not a dollar price): "
                + " · ".join(free_titles)
                + "."
            )
    from . import social_proof as sp

    pride_bit = sp.designed_in_generation_brief(
        f"morning|{day.isoformat()}|{variant}",
        day=day,
        surface="morning",
        campaign="today",
    )
    anti_template = (
        " HARD BAN (Founder Aug 14 2026): NEVER the generic mystic AI wellness "
        "starter pack — no floating singing bowls, glowing healing hands, "
        "pristine tarot fan, crystal clusters on black velvet, Flower of Life "
        "wallpaper, Akashic Records prop books, ethereal purple fog, or the "
        "factory navy three-equal-dark-cards + right mystic collage + gold "
        "script when it reads like every Canva/Midjourney holistic template. "
        "Must feel completely individual / shop-made / out of the box — real "
        "Sacred Ground storefront or interior cues when possible, bold poster "
        "or typographic art, unexpected color, photography-first collage, or "
        "one strong original illustration. Nice and unusual."
    )
    shared = (
        f"Chicago date {day.isoformat()}. "
        f"Date/time text: {copy.get('date_short')}. "
        f"{events_bit}{visit}{free_bit} {equal_rule} "
        "Mixed expressive fonts (not one rigid template), circular Sacred Ground "
        f"sun-face logo, footer with {WEBSITE} and {PHONE}. Prebranded finished "
        "flyer. CRITICAL: do NOT include any prices, dollar signs, ticket costs, "
        "or dollar amounts anywhere on the graphic. FREE / Free Community for "
        "free community gatherings is allowed and preferred. No invented "
        "practitioner faces unless a real photo reference is provided. "
        "COLOR ENERGY (hard — Founder Aug 10 + Aug 14 2026): colorful, bright, "
        "interesting, engaging — jewel tones OR unexpected bold color (coral, "
        "teal, sunflower, eggplant) with strong contrast. FORBIDDEN: drab, "
        "muddy, beige, grey, desaturated purple sludge, empty near-black voids, "
        "giant blank cards, thin faint line-art on a dead field. Vary the visual "
        "language by day — never clone yesterday's plate."
        f"{anti_template}{pride_bit}"
    )
    if is_b:
        bg_energy = (
            " VARIANT B / Instagram: same full-day readable equal-weight event "
            "info as Facebook, but the FIELD must have MORE visual pop — richer "
            "multi-tone color, stronger shapes, unexpected composition that "
            "makes someone stop and read. FORBIDDEN: flat washes, mystic AI "
            "object dumps, bland muted purple voids, empty stretched cards. "
            "Schedule stays legible; originality lives in the art language."
        )
    else:
        bg_energy = (
            " VARIANT A / Facebook: clear readable equal-weight schedule, "
            "elegant contrast, polished and still colorful/bright (not beige "
            "or muddy). Still ban the generic mystic AI template — shop-"
            "individual art required even when the field is calmer."
        )
    if style == LAYOUT_ARTISTIC and n_events <= 1:
        return (
            "Sacred Ground artistic single-event hero morning flyer, square "
            f"1080x1080. Still highly readable — not collage soup. {shared}"
            f"{bg_energy} "
            "Centered hero composition OK only when there is exactly ONE event. "
            "Never use this layout to demote a second practitioner into a tiny corner."
        )
    # Default / multi-event path: equal visual weight, varied art language.
    return (
        "Sacred Ground EQUAL-WEIGHT multi-event morning flyer, square 1080x1080. "
        "Readable schedule for every event (IDENTICAL visual weight — stacked "
        "bands, equal cards, or equal poster columns OK). HEADER may use "
        f"'{weekday} AT Sacred Ground' or an original typographic treatment — "
        "do NOT default to navy+gold script factory every day. Art language must "
        "be shop-individual (poster / photo collage / illustration / storefront) "
        "— NEVER right-side mystic object dump. FOOTER logo + website + phone + "
        "come-as-you-are. "
        f"{shared}{bg_energy}"
    )


def _font(path: str, size: int):
    from PIL import ImageFont

    try:
        return ImageFont.truetype(path, size=size)
    except OSError:
        return ImageFont.load_default()


def _pick_fonts() -> Dict[str, Any]:
    serif = "/System/Library/Fonts/Supplemental/Georgia.ttf"
    serif_bold = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
    script = "/System/Library/Fonts/Supplemental/SnellRoundhand.ttc"
    sans = "/System/Library/Fonts/Helvetica.ttc"
    if not os.path.isfile(serif):
        serif = "/Library/Fonts/Arial.ttf"
    return {
        "title": _font(serif_bold if os.path.isfile(serif_bold) else serif, 54),
        "title_sm": _font(serif, 36),
        "card_title": _font(serif_bold if os.path.isfile(serif_bold) else serif, 28),
        "card_body": _font(sans, 22),
        "script": _font(script, 48) if os.path.isfile(script) else _font(serif, 48),
        "script_sm": _font(script, 36) if os.path.isfile(script) else _font(serif, 36),
        "body": _font(sans, 28),
        "small": _font(sans, 20),
        "header": _font(serif_bold if os.path.isfile(serif_bold) else serif, 42),
        "footer": _font(sans, 22),
    }


def _draw_geometry(draw, cx: int, cy: int, r: int, fill, width: int = 2) -> None:
    # Seed-of-life-ish: center + 6 petals
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=fill, width=width)
    for i in range(6):
        ang = math.radians(60 * i - 30)
        x = int(cx + r * math.cos(ang))
        y = int(cy + r * math.sin(ang))
        draw.ellipse((x - r, y - r, x + r, y + r), outline=fill, width=max(1, width - 1))


def _draw_crescent(draw, cx: int, cy: int, r: int, fill, width: int = 3) -> None:
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=fill, width=width)
    inset = int(r * 0.35)
    draw.ellipse(
        (cx - r + inset, cy - r, cx + r + inset, cy + r),
        outline=fill,
        width=max(1, width - 1),
    )


def _tina_circle_path(events: Sequence[Event]) -> Optional[str]:
    if not any("tina" in (e.title or "").lower() for e in events):
        return None
    for p in TINA_CIRCLE_REFS:
        if os.path.isfile(p):
            return p
    return None


def _variant_palette(variant: str) -> Dict[str, Any]:
    """Two Thursday-style palettes — same layout system, different color/right art.

    Variant A (FB): cleaner readable card energy — still jewel-bright.
    Variant B (IG): richer multi-tone pop — not a flat single-color wash.
    """
    key = (variant or VARIANT_A).lower().strip()
    if key in (VARIANT_B, "b", "ig", "instagram", "alt"):
        return {
            "id": VARIANT_B,
            # Jewel amethyst + teal + amber — never muddy purple sludge.
            "bg_top": (118, 42, 148),
            "bg_mid": (62, 28, 98),
            "bg_bot": (18, 36, 72),
            "orb_colors": [
                (220, 120, 255, 90),
                (40, 210, 220, 75),
                (255, 170, 70, 70),
                (160, 90, 255, 80),
                (80, 255, 180, 55),
            ],
            "gold": (255, 210, 110),
            "gold_soft": (255, 210, 110, 180),
            "accent": (255, 90, 190),
            "accent2": (40, 220, 210),
            "card_fills": [(110, 48, 120), (36, 78, 120), (78, 42, 98)],
            "card_text": (255, 250, 240),
            "muted": (235, 210, 245),
            "footer": (22, 14, 40),
            "right_mode": "crescent",
            "energy": True,
        }
    return {
        "id": VARIANT_A,
        # Emerald / sapphire / gold — readable but still colorful.
        "bg_top": (28, 58, 72),
        "bg_mid": (22, 42, 58),
        "bg_bot": (16, 30, 48),
        "orb_colors": [
            (255, 190, 80, 45),
            (60, 180, 150, 40),
            (120, 90, 200, 35),
        ],
        "gold": (235, 195, 95),
        "gold_soft": (235, 195, 95, 150),
        "accent": (50, 160, 140),
        "accent2": (90, 140, 210),
        "card_fills": [(28, 92, 72), (72, 42, 98), (28, 52, 96)],
        "card_text": (255, 250, 240),
        "muted": (200, 220, 230),
        "footer": (14, 24, 40),
        "right_mode": "seed",
        "energy": True,
    }


def _host_from_title(title: str) -> str:
    t = title or ""
    for sep in (" with ", " With ", " w/ ", " W/ ", ": "):
        if sep in t:
            bit = t.split(sep)[-1].strip()
            # Drop long descriptors after host
            for cut in (" — ", " - ", "|"):
                if cut in bit:
                    bit = bit.split(cut)[0].strip()
            return bit[:40]
    return ""


def _keywords_for_event(ev: Event) -> str:
    from .classify import is_free_community_event

    low = (ev.title or "").lower()
    # Free community gatherings: FREE is OK on-image (dollar prices are not).
    if is_free_community_event(ev):
        if "lions gate" in low:
            return "FREE · Portal · Align"
        if "meditation" in low:
            return "FREE · Community · Welcome"
        return "FREE · Community · Welcome"
    if "tai chi" in low:
        return "Move · Breathe · Flow"
    if "tarot" in low or "rune" in low:
        return "Clarity · Guidance · Insight"
    if "quantum" in low:
        return "Expand · Align · Shift"
    if "reflexology" in low:
        return "Rest · Restore · Renew"
    if "meditation" in low:
        return "Breathe · Soften · Awaken"
    if "sound" in low or "drum" in low:
        return "Sound · Journey · Release"
    if "reiki" in low:
        return "Balance · Ease · Heal"
    if "shaman" in low:
        return "Spirit · Guidance · Insight"
    if "chakra" in low:
        return "Align · Open · Restore"
    if "massage" in low:
        return "Ease · Restore · Care"
    if "akashic" in low or "angel" in low or "janel" in low:
        return "Insight · Clarity · Light"
    return "Come as you are"


def _default_flyer_paths(day: date, slug: str, variant: str) -> str:
    suffix = "" if variant == VARIANT_A else f"-{variant}"
    return os.path.join(
        ASSETS_DIR, f"sg-morning-flyer-{day.isoformat()}-{slug}{suffix}.png"
    )


def render_local_flyer(
    day: date,
    events: Sequence[Event],
    *,
    out_path: Optional[str] = None,
    variant: str = VARIANT_A,
) -> str:
    """
    Render a Thursday-style 1080 square (stacked event cards + right graphics).

    `variant` a/b changes palette + right-side art so FB and IG can diverge while
    carrying the same full-day event information. Never draws prices.
    """
    from PIL import Image, ImageDraw, ImageFilter

    copy = build_flyer_copy(day, events)
    fonts = _pick_fonts()
    pal = _variant_palette(variant)
    picked = pick_events_for_flyer(events)

    img = Image.new("RGB", (CANVAS, CANVAS), pal["bg_bot"])
    px = img.load()
    mid = pal.get("bg_mid") or pal["bg_bot"]
    for y in range(CANVAS):
        t = y / (CANVAS - 1)
        if t < 0.45:
            u = t / 0.45
            r = int(pal["bg_top"][0] * (1 - u) + mid[0] * u)
            g = int(pal["bg_top"][1] * (1 - u) + mid[1] * u)
            b = int(pal["bg_top"][2] * (1 - u) + mid[2] * u)
        else:
            u = (t - 0.45) / 0.55
            r = int(mid[0] * (1 - u) + pal["bg_bot"][0] * u)
            g = int(mid[1] * (1 - u) + pal["bg_bot"][1] * u)
            b = int(mid[2] * (1 - u) + pal["bg_bot"][2] * u)
        for x in range(CANVAS):
            # Slight horizontal warmth so B isn't a dead vertical wash.
            hx = x / (CANVAS - 1)
            px[x, y] = (
                min(255, r + int(10 * hx)),
                min(255, g + int(4 * hx)),
                min(255, b + int(14 * (1 - hx) if pal.get("energy") else 6 * hx)),
            )

    draw = ImageDraw.Draw(img, "RGBA")
    gold = pal["gold"]
    gold_soft = pal["gold_soft"]

    # Soft mist / texture wash on right half
    for y in range(120, 860):
        for x in range(620, CANVAS):
            fade = (x - 620) / 460
            base = px[x, y]
            bump = int((28 if pal.get("energy") else 18) * fade)
            px[x, y] = (
                min(255, base[0] + bump),
                min(255, base[1] + bump // 2),
                min(255, base[2] + bump // 3),
            )

    # Luminous orbs + ribbon so the field has shape & jewel energy (both variants).
    if pal.get("energy") and pal.get("orb_colors"):
        overlay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        orb_specs = [
            (860, 240, 170),
            (980, 480, 130),
            (740, 620, 110),
            (920, 760, 100),
            (700, 360, 80),
        ]
        for i, (ox, oy, orad) in enumerate(orb_specs):
            col = pal["orb_colors"][i % len(pal["orb_colors"])]
            for ring in range(orad, 0, -6):
                a = max(10, int(col[3] * (ring / orad)))
                od.ellipse(
                    (ox - ring, oy - ring, ox + ring, oy + ring),
                    fill=(col[0], col[1], col[2], a),
                )
        # Diagonal energy ribbon
        for i in range(18):
            y0 = 180 + i * 28
            od.polygon(
                [
                    (640, y0),
                    (CANVAS, y0 - 40),
                    (CANVAS, y0 - 10),
                    (640, y0 + 30),
                ],
                fill=(pal["accent2"][0], pal["accent2"][1], pal["accent2"][2], 28),
            )
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        px = img.load()
        draw = ImageDraw.Draw(img, "RGBA")

    weekday = day.strftime("%A").upper()
    draw.text((70, 48), f"{weekday} AT", font=fonts["header"], fill=gold)
    draw.text((70, 96), "Sacred Ground", font=fonts["script"], fill=gold)
    draw.text(
        (70, 155),
        "Mind • Body • Spirit • Community",
        font=fonts["small"],
        fill=pal["muted"],
    )

    # Right-side evocative graphics (variant-specific)
    if pal["right_mode"] == "crescent":
        _draw_crescent(draw, 820, 280, 100, gold_soft, 4)
        _draw_geometry(
            draw,
            900,
            500,
            70,
            (pal["accent"][0], pal["accent"][1], pal["accent"][2], 130),
            3,
        )
        a2 = pal.get("accent2") or pal["accent"]
        _draw_geometry(draw, 760, 420, 48, (a2[0], a2[1], a2[2], 110), 2)
        _draw_crescent(draw, 780, 700, 70, gold_soft, 3)
        _draw_crescent(draw, 940, 640, 40, (a2[0], a2[1], a2[2], 100), 2)
    else:
        _draw_geometry(draw, 820, 260, 75, gold_soft, 2)
        _draw_geometry(draw, 900, 480, 50, (pal["accent"][0], pal["accent"][1], pal["accent"][2], 80), 2)
        _draw_geometry(draw, 760, 680, 65, gold_soft, 2)

    # Left stacked event cards (or visit card)
    card_x0, card_x1 = 60, 620
    if copy.get("empty_day") or not picked:
        y0 = 210
        draw.rounded_rectangle(
            (card_x0, y0, card_x1, y0 + 280),
            radius=28,
            fill=(*pal["card_fills"][0], 235),
        )
        draw.text((card_x0 + 28, y0 + 36), "SACRED GROUND", font=fonts["card_title"], fill=gold)
        draw.text((card_x0 + 28, y0 + 90), "Crystals · readings · quiet wonder", font=fonts["card_body"], fill=pal["card_text"])
        draw.text((card_x0 + 28, y0 + 130), "Come browse · Arlington Heights", font=fonts["card_body"], fill=pal["card_text"])
        draw.text((card_x0 + 28, y0 + 180), str(copy["date_short"]), font=fonts["small"], fill=pal["muted"])
    else:
        n = len(picked)
        top = 200
        bottom = 860
        gap = 14
        # Single-event: do NOT stretch one empty skyscraper card (Aug 10 IG reject).
        if n == 1:
            card_h = min(MAX_SINGLE_CARD_HEIGHT, bottom - top)
        else:
            card_h = (bottom - top - gap * (n - 1)) // n
        for i, ev in enumerate(picked):
            y0 = top + i * (card_h + gap)
            fill = pal["card_fills"][i % len(pal["card_fills"])]
            draw.rounded_rectangle(
                (card_x0, y0, card_x1, y0 + card_h),
                radius=24,
                fill=(*fill, 235),
            )
            # Icon circle
            icx, icy, ir = card_x0 + 48, y0 + card_h // 2, 28
            draw.ellipse((icx - ir, icy - ir, icx + ir, icy + ir), outline=gold, width=2)
            if pal["right_mode"] == "crescent":
                _draw_crescent(draw, icx, icy, 14, gold_soft, 2)
            else:
                _draw_geometry(draw, icx, icy, 12, gold_soft, 1)

            title = _short_title(ev.title).upper()
            if len(title) > 34:
                title = title[:33] + "…"
            host = _host_from_title(ev.title)
            time_ln = _event_time_line(ev)
            keywords = _keywords_for_event(ev)
            assert_price_free(title, host, time_ln, keywords)

            tx = card_x0 + 95
            draw.text((tx, y0 + 22), title, font=fonts["card_title"], fill=pal["card_text"])
            yy = y0 + 58
            if host:
                draw.text((tx, yy), host, font=fonts["small"], fill=gold)
                yy += 28
            if time_ln:
                draw.text((tx, yy), time_ln, font=fonts["card_body"], fill=pal["card_text"])
                yy += 30
            draw.text((tx, min(yy, y0 + card_h - 36)), keywords, font=fonts["small"], fill=pal["muted"])

    # Optional Tina circle (real photo only) — top-right of photo area
    tina = _tina_circle_path(events)
    if tina:
        try:
            circ = Image.open(tina).convert("RGBA")
            circ = circ.resize((160, 160), Image.Resampling.LANCZOS)
            img.paste(circ, (860, 180), circ)
        except OSError:
            pass

    # Footer band
    footer_h = 150
    draw.rectangle((0, CANVAS - footer_h, CANVAS, CANVAS), fill=pal["footer"])
    if os.path.isfile(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo = logo.resize((110, 110), Image.Resampling.LANCZOS)
            alpha = logo.split()[-1].point(lambda a: int(a * 0.85))
            logo.putalpha(alpha)
            img.paste(logo, (36, CANVAS - footer_h + 20), logo)
        except OSError:
            pass
    draw.text(
        (170, CANVAS - footer_h + 40),
        WEBSITE,
        font=fonts["footer"],
        fill=gold,
    )
    draw.text(
        (170, CANVAS - footer_h + 78),
        PHONE,
        font=fonts["footer"],
        fill=(250, 250, 250),
    )
    draw.text(
        (520, CANVAS - footer_h + 52),
        "Come as you are",
        font=fonts["script_sm"],
        fill=gold,
    )

    # No post-hoc shop-pride overlays on flyers (Founder Aug 11 ~3:05pm CT).
    # Existing inventory stays badge-free. FUTURE AI generations may bake pride
    # into the art via social_proof.designed_in_generation_brief() in
    # build_generation_prompt — never stamp finished plates here.

    img = img.filter(ImageFilter.SMOOTH_MORE)
    assert_price_free(copy["label"], *copy.get("covers") or [], *copy.get("lines") or [])

    if not out_path:
        os.makedirs(ASSETS_DIR, exist_ok=True)
        out_path = _default_flyer_paths(day, str(copy["slug"]), pal["id"])
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    return out_path


def _rel_asset(path: str) -> str:
    if os.path.isabs(path) and path.startswith(ROOT + os.sep):
        return os.path.relpath(path, ROOT).replace("\\", "/")
    return path.replace("\\", "/")


def _day_events(day: date, events: Sequence[Event]) -> List[Event]:
    day_events: List[Event] = []
    for e in events:
        start = parse_tec_datetime(e.start_date)
        if start and start.date() == day:
            day_events.append(e)
    if not day_events and events:
        only_today = True
        for e in events:
            start = parse_tec_datetime(e.start_date)
            if start and start.date() != day:
                only_today = False
                break
        if only_today:
            day_events = list(events)
    return day_events


def register_flyer(
    day: date,
    *,
    local: str,
    url: str = "",
    media_id: Optional[int] = None,
    local_instagram: str = "",
    url_instagram: str = "",
    media_id_instagram: Optional[int] = None,
    copy: Optional[Dict[str, Any]] = None,
    events: Optional[Sequence[Event]] = None,
    merge: bool = True,
    reset_public_urls: bool = False,
) -> Dict[str, Any]:
    """Append/update a day entry in morning_flyers.json (FB url + optional IG variant)."""
    copy = copy or build_flyer_copy(day, events or [])
    assert_price_free(
        copy.get("label") or "",
        *(copy.get("covers") or []),
        *(copy.get("lines") or []),
    )

    layout = choose_layout_style(day, events or [])
    entry: Dict[str, Any] = {
        "label": copy["label"],
        "covers": list(copy.get("covers") or []),
        "local": _rel_asset(local) if local else "",
        "url": url or "",
        "prebranded": True,
        "template": "thursday-style" if layout == LAYOUT_THURSDAY else "artistic_hero",
    }
    if media_id is not None:
        entry["media_id"] = int(media_id)
    if local_instagram:
        entry["local_instagram"] = _rel_asset(local_instagram)
    if url_instagram:
        entry["url_instagram"] = url_instagram
    if media_id_instagram is not None:
        entry["media_id_instagram"] = int(media_id_instagram)
    if copy.get("empty_day"):
        entry["empty_day"] = True

    data = load_flyers_config()
    flyers = data.setdefault("flyers", {})
    prev = flyers.get(day.isoformat()) if merge else None
    if isinstance(prev, dict):
        # Preserve Founder-set fields; never wipe the other platform's URL/local
        # unless reset_public_urls (regenerate after visual-energy reject).
        preserve_keys = [
            "url",
            "media_id",
            "local",
            "url_instagram",
            "media_id_instagram",
            "local_instagram",
            "urls",
            "alt_media_ids",
            "alt_local",
            "alt_template",
            "note",
            "template",
        ]
        if reset_public_urls:
            preserve_keys = [
                k
                for k in preserve_keys
                if k
                not in (
                    "url",
                    "media_id",
                    "url_instagram",
                    "media_id_instagram",
                    "urls",
                )
            ]
        for key in preserve_keys:
            if key in prev and not entry.get(key):
                entry[key] = prev[key]
        # Explicit new locals/urls win when provided.
        if local:
            entry["local"] = _rel_asset(local)
        if url:
            entry["url"] = url
        if local_instagram:
            entry["local_instagram"] = _rel_asset(local_instagram)
        if url_instagram:
            entry["url_instagram"] = url_instagram
        if media_id is not None:
            entry["media_id"] = int(media_id)
        if media_id_instagram is not None:
            entry["media_id_instagram"] = int(media_id_instagram)
        if reset_public_urls:
            entry["url"] = url or ""
            entry["url_instagram"] = url_instagram or ""
            entry.pop("media_id", None)
            entry.pop("media_id_instagram", None)
            entry.pop("urls", None)
            if media_id is not None:
                entry["media_id"] = int(media_id)
            if media_id_instagram is not None:
                entry["media_id_instagram"] = int(media_id_instagram)
        if prev.get("template") and not events:
            entry["template"] = prev["template"]

    fb_u = str(entry.get("url") or "").strip()
    ig_u = str(entry.get("url_instagram") or "").strip()
    if fb_u and ig_u and fb_u != ig_u:
        entry["urls"] = [fb_u, ig_u]
    elif "urls" in entry and not (fb_u and ig_u and fb_u != ig_u):
        # Keep legacy urls only when dual variants are not yet both public.
        pass

    flyers[day.isoformat()] = entry
    data["layout_mix"] = {
        "thursday_cards_share": THURSDAY_CARDS_SHARE,
        "artistic_hero_share": round(1.0 - THURSDAY_CARDS_SHARE, 2),
        "default": LAYOUT_THURSDAY,
        "platform_variants": (
            "single-image mode (Founder Aug 10 2026): primary url/local "
            "posts to FB+IG; url_instagram ignored unless allow_ig_variant:true"
        ),
    }
    save_flyers_config(data)
    return entry


def _ensure_second_variant(
    day: date,
    day_events: Sequence[Event],
    existing: Dict[str, Any],
    copy: Dict[str, Any],
) -> Dict[str, Any]:
    """Build Instagram (variant B) when FB exists but IG variant is missing."""
    if day.isoformat() in PROTECTED_DAYS:
        return existing
    if has_dual_flyer_variants(existing):
        return existing
    local_ig = str(existing.get("local_instagram") or "").strip()
    abs_ig = (
        local_ig
        if os.path.isabs(local_ig)
        else os.path.join(ROOT, local_ig)
        if local_ig
        else ""
    )
    if not abs_ig or not os.path.isfile(abs_ig):
        abs_ig = render_local_flyer(
            day,
            day_events,
            variant=VARIANT_B,
            out_path=_default_flyer_paths(day, str(copy["slug"]), VARIANT_B),
        )
    return register_flyer(
        day,
        local=str(existing.get("local") or ""),
        url=str(existing.get("url") or ""),
        media_id=existing.get("media_id"),
        local_instagram=abs_ig,
        url_instagram=str(existing.get("url_instagram") or ""),
        media_id_instagram=existing.get("media_id_instagram"),
        copy=copy,
        events=day_events,
        merge=True,
    )


def ensure_flyer_for_day(
    day: date,
    events: Sequence[Event],
    *,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Ensure a primary full-day flyer exists for Chicago `day`.

    Single-image mode (Founder Aug 10 2026): one excellent `url`/`local` plate
    is shared on Facebook and Instagram. Separate IG variants are not required
    (opt-in via allow_ig_variant + url_instagram only).
    """
    day_events = _day_events(day, events)
    copy = build_flyer_copy(day, day_events)
    layout = choose_layout_style(day, day_events)
    prompt = build_generation_prompt(
        day, copy, layout=layout, events=day_events, variant=VARIANT_A
    )

    existing = flyer_entry_for_day(day)
    # Founder Aug 10: drab/muddy locals must be rebuilt (except protected gold standard).
    energy_failed = (
        entry_fails_visual_energy(existing)
        if existing and day.isoformat() not in PROTECTED_DAYS
        else []
    )
    if energy_failed and not force:
        force = True
    if existing and not force:
        fb = str(existing.get("url") or "").strip()
        missing = [] if fb else ["facebook"]
        return {
            "day": day.isoformat(),
            "action": "exists",
            "needs_upload": bool(missing),
            "needs_upload_platforms": missing,
            "entry": existing,
            "local": existing.get("local"),
            "layout": layout,
            "prompt": prompt,
            "single_image_mode": True,
        }

    if force and day.isoformat() in PROTECTED_DAYS and existing:
        # Never overwrite the Aug 6 gold standard.
        return {
            "day": day.isoformat(),
            "action": "exists",
            "needs_upload": not bool(existing.get("url")),
            "entry": existing,
            "layout": layout,
            "prompt": prompt,
            "protected": True,
            "single_image_mode": True,
        }

    out_a = render_local_flyer(day, day_events, variant=VARIANT_A)
    clear_urls = bool(energy_failed) or (
        force and existing and day.isoformat() not in PROTECTED_DAYS
    )
    keep_url = "" if clear_urls else (str((existing or {}).get("url") or "") if existing else "")
    entry = register_flyer(
        day,
        local=out_a,
        url=keep_url,
        media_id=None if clear_urls else ((existing or {}).get("media_id") if existing else None),
        copy=copy,
        events=day_events,
        merge=bool(existing),
        reset_public_urls=clear_urls,
    )
    fb = str(entry.get("url") or "")
    return {
        "day": day.isoformat(),
        "action": "created",
        "needs_upload": not bool(fb),
        "needs_upload_platforms": [] if fb else ["facebook"],
        "entry": entry,
        "local": out_a,
        "layout": layout,
        "prompt": prompt,
        "single_image_mode": True,
        "regenerated_for_visual_energy": energy_failed or None,
    }


def ensure_flyers_for_range(
    *,
    days: int = 7,
    start: Optional[date] = None,
    events: Optional[Sequence[Event]] = None,
    source: str = "cache",
    force: bool = False,
) -> Dict[str, Any]:
    """Prebuild / ensure flyers for start .. start+days-1 (America/Chicago)."""
    from . import classify
    from .ingest import load_events

    start = start or today_local()
    if events is None:
        events_list, source_used = load_events(source)
        events_list, _ = classify.filter_valid(events_list, on=start)
    else:
        events_list = list(events)
        source_used = "provided"

    results = []
    needs_upload = []
    for i in range(max(1, days)):
        day = start + timedelta(days=i)
        day_events = classify.events_on_day(events_list, day)
        info = ensure_flyer_for_day(day, day_events, force=force)
        results.append(info)
        if info.get("needs_upload"):
            needs_upload.append(info["day"])

    return {
        "ok": True,
        "source": source_used,
        "start": start.isoformat(),
        "days": days,
        "results": results,
        "needs_upload": needs_upload,
        "config": FLYERS_PATH,
    }


def set_flyer_url(
    day: date,
    url: str,
    media_id: Optional[int] = None,
    *,
    platform: str = "facebook",
) -> Dict[str, Any]:
    """Set public WP URL for facebook (`url`) or instagram (`url_instagram`)."""
    data = load_flyers_config()
    entry = (data.get("flyers") or {}).get(day.isoformat())
    if not isinstance(entry, dict):
        raise KeyError(f"No flyer entry for {day.isoformat()}")
    key = (platform or "facebook").lower().strip()
    if key in ("instagram", "ig"):
        entry["url_instagram"] = url
        if media_id is not None:
            entry["media_id_instagram"] = int(media_id)
    else:
        entry["url"] = url
        if media_id is not None:
            entry["media_id"] = int(media_id)
    fb = str(entry.get("url") or "").strip()
    ig = str(entry.get("url_instagram") or "").strip()
    if fb and ig and fb != ig:
        entry["urls"] = [fb, ig]
    save_flyers_config(data)
    return entry
