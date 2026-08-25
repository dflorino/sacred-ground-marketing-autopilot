"""Cheryl-style date-keyed morning flyers — generate, validate, register."""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .ingest import parse_tec_datetime, today_local
from .models import Event
from .paths import CONFIG_DIR, ROOT, _load_json, write_json

FLYERS_PATH = os.path.join(CONFIG_DIR, "morning_flyers.json")
LIVING_WORLDS_PATH = os.path.join(CONFIG_DIR, "morning_living_worlds.json")
STYLES_PATH = os.path.join(CONFIG_DIR, "morning_flyer_styles.json")
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
# Visual *art language* rotates via config/morning_flyer_styles.json (Founder
# Aug 14 2026) — Magritte / Folk / Da Vinci / Einstein — not mystic AI navy.
THURSDAY_CARDS_SHARE = 0.75
LAYOUT_THURSDAY = "thursday_cards"
LAYOUT_ARTISTIC = "artistic_hero"

# Default mixed pool if styles config missing (Founder Aug 14 ~2:31pm CT).
DEFAULT_STYLE_ROTATION = (
    "magritte_floating_door",
    "folk_outsider_night",
    "davinci_storefront_sketch",
    "einstein_chalkboard_map",
    "thursday_cards_shop_made",
    "artistic_hero_shop_made",
)

NOTES = (
    "Sacred Ground morning flyers (Founder Aug 14 2026): MIXED visual pool — "
    "four approved art languages (Magritte, Folk, Da Vinci, Einstein) PLUS "
    "existing shop-made Thursday equal-card + artistic hero approaches, "
    "interleaved with unused date-keyed queued plates. TRUE RANDOM "
    "(day-seeded) pick among series-eligible styles — do NOT run new styles "
    "only for two weeks then dump old approaches. SERIES LIMITS: max 1 "
    "consecutive day per style id, max 2 per style in any rolling 7 Chicago "
    "days. BAN Bauhaus + Victorian (archived). BAN generic mystic AI navy "
    "template (series_limit 0). EVERY plate MUST bake in Chicagoland #1 / "
    "Premier / Voted pride (NEW gens via designed_in_generation_brief; "
    "queued plates missing pride → NEW url with pride band). Gold standard "
    "readability: assets/sg-morning-flyer-2026-08-06-today-collage.png. "
    f"FOOTER logo + {WEBSITE} + {PHONE}. NEVER prices. Never-reuse URLs "
    "absolute. Do not replace a live morning post unless Founder asks."
)

# Series-limit defaults (Founder Aug 14 ~2:29pm CT) — config overrides.
DEFAULT_MAX_CONSECUTIVE_DAYS = 1
DEFAULT_ROLLING_WINDOW_DAYS = 7
DEFAULT_MAX_PER_STYLE_IN_WINDOW = 2

# Legacy template → mixed-pool style id (for series history).
LEGACY_TEMPLATE_TO_STYLE = {
    "thursday-style": "thursday_cards_shop_made",
    "thursday_cards": "thursday_cards_shop_made",
    "artistic_hero": "artistic_hero_shop_made",
    "artistic-hero": "artistic_hero_shop_made",
}

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


# Deprecated PIL compositor palette — Founder Aug 14 banned this navy equal-card factory.
_PIL_CARD_FILLS_A = frozenset({(28, 92, 72), (72, 42, 98), (28, 52, 96)})
_PIL_CARD_FILLS_B = frozenset({(110, 48, 120), (36, 78, 120), (78, 42, 98)})


def flyer_is_banned_mystic_navy_pil(path: str) -> bool:
    """Detect the deprecated render_local_flyer navy equal-card template.

    Founder Aug 14 2026: NEVER ship the generic mystic AI navy three-equal-dark-cards
    + right sacred-geometry collage factory. Approved mornings use mixed-pool AI art
    (Magritte / Folk / Da Vinci / Einstein / colorful shop-made), not this PIL stub.
    """
    if not path or not os.path.isfile(path):
        return False
    from PIL import Image

    im = Image.open(path).convert("RGB")
    if im.size != (CANVAS, CANVAS):
        return False
    px = im.load()
    # Left stacked cards use exact compositor fill colors (within tolerance).
    card_hits = 0
    for x in range(80, 580, 24):
        for y in range(220, 820, 24):
            r, g, b = px[x, y]
            for cr, cg, cb in _PIL_CARD_FILLS_A | _PIL_CARD_FILLS_B:
                if abs(r - cr) <= 8 and abs(g - cg) <= 8 and abs(b - cb) <= 8:
                    card_hits += 1
                    break
    if card_hits < 40:
        return False
    header = [px[x, y] for x in range(60, 280, 16) for y in range(40, 170, 16)]
    hr = sum(p[0] for p in header) / len(header)
    hg = sum(p[1] for p in header) / len(header)
    hb = sum(p[2] for p in header) / len(header)
    lum = (hr + hg + hb) / 3
    return lum < 95 and hb >= hr - 5 and hb >= hg - 10


def flyer_passes_publish_gates(path: str) -> bool:
    """All gates required before a morning plate may publish."""
    if flyer_is_banned_mystic_navy_pil(path):
        return False
    return flyer_passes_visual_energy(path)


# Generation sources that must never reach Facebook / Instagram.
BANNED_GENERATION_SOURCES = frozenset(
    {
        "pil_compositor_preview",
        "needs_ai_art",
        "needs_ai_generation",
    }
)


def _abs_asset(path: str) -> str:
    if not path:
        return ""
    if os.path.isabs(path):
        return path
    return os.path.join(ROOT, path)


def entry_generation_source(entry: Optional[Dict[str, Any]]) -> str:
    if not isinstance(entry, dict):
        return ""
    return str(
        entry.get("generation_source")
        or entry.get("generation_source")
        or entry.get("source")
        or ""
    ).strip()


def entry_publish_block_reason(entry: Optional[Dict[str, Any]]) -> Optional[str]:
    """
    Why this morning_flyers entry must not be planned or published.

    Founder Aug 25 2026: morning automation pride-baked + uploaded the banned
    navy PIL compositor (`…astrology-tarot-pride…`) to Zernio. Block at every
    gate — generation_source, local pixels, and remote URL bytes.

    Missing local alone is NOT a block here (URL-only plates can still ship);
    `entry_fails_publish_blockers` remains the stricter ensure-path check.
    """
    if not isinstance(entry, dict):
        return "missing_flyer_entry"
    src = entry_generation_source(entry)
    if src in BANNED_GENERATION_SOURCES:
        return f"banned_generation_source:{src}"
    for key in ("local", "local_instagram", "local_path", "path"):
        local = str(entry.get(key) or "").strip()
        if not local:
            continue
        abs_path = _abs_asset(local)
        if abs_path and os.path.isfile(abs_path) and flyer_is_banned_mystic_navy_pil(
            abs_path
        ):
            return f"banned_mystic_navy_pil_local:{local}"
    for key in ("url", "url_instagram"):
        url = str(entry.get(key) or "").strip()
        if url and image_url_is_banned_mystic_navy_pil(url):
            return f"banned_mystic_navy_pil_url:{key}"
    return None


def image_url_is_banned_mystic_navy_pil(url: str, *, timeout: float = 20.0) -> bool:
    """Download a candidate morning image and run the navy-PIL pixel detector."""
    u = (url or "").strip()
    if not u.startswith(("http://", "https://")):
        return False
    # Fast path: pride-baked banned compositor filenames (Aug 25 Zernio incident).
    low = u.lower()
    if "sg-morning-flyer-" in low and "-pride-" in low:
        return True
    if "pil_compositor" in low or "navy-equal-card" in low:
        return True
    if "astrology-tarot.png" in low and "morning-flyer" in low:
        return True
    import tempfile
    import urllib.request

    try:
        req = urllib.request.Request(
            u,
            headers={"User-Agent": "SacredGroundMarketingAutopilot/1.0"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
    except Exception:
        # Fail closed for morning publish only when caller treats True as block;
        # here network errors return False so offline tests still plan from local.
        return False
    suffix = ".png"
    if ".jpg" in low or ".jpeg" in low:
        suffix = ".jpg"
    elif ".webp" in low:
        suffix = ".webp"
    fd, tmp = tempfile.mkstemp(prefix="sg-morning-gate-", suffix=suffix)
    try:
        os.close(fd)
        with open(tmp, "wb") as fh:
            fh.write(data)
        return flyer_is_banned_mystic_navy_pil(tmp)
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def entry_fails_publish_blockers(entry: Optional[Dict[str, Any]]) -> List[str]:
    """Hard blockers — banned PIL template, or no usable local/URL plate.

    A non-banned public URL alone is enough (Founder Aug 25: after detaching a
    banned local and wiring real AI art, ensure must treat the day as ready).
    """
    if not isinstance(entry, dict):
        return []
    failed: List[str] = []
    keys = [("facebook", "local", "url")]
    if entry.get(ALLOW_IG_VARIANT_KEY):
        keys.append(("instagram", "local_instagram", "url_instagram"))
    for platform, local_key, url_key in keys:
        local = str(entry.get(local_key) or "").strip()
        abs_path = _abs_asset(local)
        url = str(entry.get(url_key) or entry.get("url") or "").strip()
        local_ok = bool(abs_path and os.path.isfile(abs_path))
        if local_ok and flyer_is_banned_mystic_navy_pil(abs_path):
            failed.append(platform)
            continue
        if image_url_is_banned_mystic_navy_pil(url):
            failed.append(platform)
            continue
        if not local_ok and not url:
            failed.append(platform)
    return failed


def entry_fails_visual_energy(entry: Optional[Dict[str, Any]]) -> List[str]:
    """Platforms whose local flyer PNGs fail soft color-energy gate (muddy/drab).

    Does not include banned PIL (see entry_fails_publish_blockers) or approved
    dark chalkboard styles that intentionally run low saturation.
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
        if not abs_path or not os.path.isfile(abs_path):
            continue
        if flyer_is_banned_mystic_navy_pil(abs_path):
            continue
        style_id = str(entry.get("visual_style") or "").strip()
        if style_id in ("einstein_chalkboard_map",):
            continue
        if not flyer_passes_visual_energy(abs_path):
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

    Never returns a URL when the entry is a banned navy PIL plate.
    """
    if entry_publish_block_reason(entry):
        return "", False
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


def load_styles_config() -> Dict[str, Any]:
    """Founder-approved morning visual style catalog (Aug 14 2026)."""
    if not os.path.isfile(STYLES_PATH):
        return {
            "rotation_order": list(DEFAULT_STYLE_ROTATION),
            "styles": {},
            "archived_out": {},
            "pride_on_morning": {},
        }
    with open(STYLES_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def active_style_rotation() -> List[str]:
    """Active mixed-pool style ids (approved art + legacy shop-made approaches)."""
    return active_mixed_pool()


def active_mixed_pool() -> List[str]:
    """
    Full morning visual mix (Founder Aug 14 ~2:31pm CT).

    Four approved art languages + existing Thursday equal-card / artistic hero
    approaches. Not 'new styles only.'
    """
    data = load_styles_config()
    raw = (
        data.get("mixed_pool")
        or data.get("rotation_order")
        or list(DEFAULT_STYLE_ROTATION)
    )
    styles = data.get("styles") or {}
    archived = set((data.get("archived_out") or {}).keys())
    banned = set(
        ((data.get("series_limits") or {}).get("banned_series_limit_0") or {}).keys()
    )
    out: List[str] = []
    for sid in raw:
        key = str(sid).strip()
        if not key or key in archived or key in banned:
            continue
        meta = styles.get(key) or {}
        if str(meta.get("status") or "active").lower() == "archived":
            continue
        out.append(key)
    return out or list(DEFAULT_STYLE_ROTATION)


def style_family(style_id: str) -> str:
    """Series-limit family key (defaults to style id)."""
    meta = style_meta(style_id)
    fam = str(meta.get("family") or style_id or "").strip()
    return fam or str(style_id)


def style_meta(style_id: str) -> Dict[str, Any]:
    styles = load_styles_config().get("styles") or {}
    meta = styles.get(style_id)
    if isinstance(meta, dict):
        return dict(meta)
    if os.path.isfile(LIVING_WORLDS_PATH):
        lw = _load_json(LIVING_WORLDS_PATH).get("styles") or {}
        meta = lw.get(style_id)
        if isinstance(meta, dict):
            return dict(meta)
    return {"id": style_id}


def normalize_queued_style_id(entry: Dict[str, Any]) -> str:
    """Map a morning_flyers.json entry to a mixed-pool style id when possible."""
    vs = str(entry.get("visual_style") or "").strip()
    if vs:
        return vs
    tmpl = str(entry.get("template") or "").strip().lower()
    return LEGACY_TEMPLATE_TO_STYLE.get(tmpl, "")


def pride_option_for_style(style_id: str) -> str:
    """On-image Option A/B/C preferred for this visual style (morning plates)."""
    pride = load_styles_config().get("pride_on_morning") or {}
    by_style = pride.get("by_style") or {}
    opt = str(by_style.get(style_id) or "").strip().upper()
    if opt in ("A", "B", "C"):
        return opt
    # Founder: prefer visible #1 Chicagoland on morning art.
    return "B"


def series_limit_config() -> Dict[str, Any]:
    """
    Founder Aug 14 ~2:29–2:31pm CT series caps for the mixed morning pool.

    max_consecutive_days=1 → never the same style/family two Chicago days in a row.
    max_per_style_in_window=2 over rolling_window_days=7 → at most twice/week.
    per_style_max_in_window overrides (Founder Aug 25 2026): folk_outsider_night → 1
    so folk never appears twice in the same rolling 7 Chicago days.
    Banned / archived ids have series_limit 0 (never generate).
    """
    raw = load_styles_config().get("series_limits") or {}
    banned = set((raw.get("banned_series_limit_0") or {}).keys())
    banned.update((load_styles_config().get("archived_out") or {}).keys())
    per_style_raw = raw.get("per_style_max_in_window") or {}
    per_style: Dict[str, int] = {}
    if isinstance(per_style_raw, dict):
        for sid, val in per_style_raw.items():
            try:
                per_style[str(sid).strip()] = int(val)
            except (TypeError, ValueError):
                continue
    return {
        "max_consecutive_days": int(
            raw.get("max_consecutive_days", DEFAULT_MAX_CONSECUTIVE_DAYS)
        ),
        "rolling_window_days": int(
            raw.get("rolling_window_days", DEFAULT_ROLLING_WINDOW_DAYS)
        ),
        "max_per_style_in_window": int(
            raw.get("max_per_style_in_window", DEFAULT_MAX_PER_STYLE_IN_WINDOW)
        ),
        "per_style_max_in_window": per_style,
        "banned_ids": banned,
    }


def queued_visual_style_history(
    day: date,
    *,
    lookback_days: int = DEFAULT_ROLLING_WINDOW_DAYS,
    extra: Optional[Dict[date, str]] = None,
) -> Dict[date, str]:
    """
    Recent Chicago days → style id from the morning_flyers queue.

    Uses explicit visual_style when present; else maps legacy template
    (thursday-style / artistic_hero) into mixed-pool ids for series counting.
    """
    flyers = load_flyers_config().get("flyers") or {}
    out: Dict[date, str] = {}
    window = max(1, int(lookback_days))
    for i in range(1, window + 1):
        d = day - timedelta(days=i)
        entry = flyers.get(d.isoformat())
        if not isinstance(entry, dict):
            continue
        vs = normalize_queued_style_id(entry)
        if vs:
            out[d] = vs
    if extra:
        for d, vs in extra.items():
            if d < day and vs:
                out[d] = str(vs).strip()
    return out


def style_passes_series_limits(
    style_id: str,
    day: date,
    history: Dict[date, str],
    *,
    limits: Optional[Dict[str, Any]] = None,
) -> bool:
    """True when assigning style_id on day would respect consecutive + rolling caps."""
    lim = limits or series_limit_config()
    key = str(style_id).strip()
    if not key or key in lim["banned_ids"]:
        return False
    fam = style_family(key)

    def _hist_family(d: date) -> str:
        prev = history.get(d)
        return style_family(prev) if prev else ""

    max_consec = max(1, int(lim["max_consecutive_days"]))
    run = 0
    cursor = day - timedelta(days=1)
    while _hist_family(cursor) == fam:
        run += 1
        cursor -= timedelta(days=1)
        if run >= max_consec:
            return False

    window = max(1, int(lim["rolling_window_days"]))
    per_style = lim.get("per_style_max_in_window") or {}
    if key in per_style:
        max_in = max(0, int(per_style[key]))
    elif fam in per_style:
        max_in = max(0, int(per_style[fam]))
    else:
        max_in = max(0, int(lim["max_per_style_in_window"]))
    prior = 0
    for i in range(1, window):
        if _hist_family(day - timedelta(days=i)) == fam:
            prior += 1
    if prior + 1 > max_in:
        return False
    return True


def _day_style_rng(day: date) -> random.Random:
    """Stable per-Chicago-day RNG so dry-runs / reruns pick the same mix."""
    digest = hashlib.sha256(f"sg-morning-mixed|{day.isoformat()}".encode()).hexdigest()
    return random.Random(int(digest[:16], 16))


def choose_visual_style(
    day: date,
    *,
    force: Optional[str] = None,
    history: Optional[Dict[date, str]] = None,
    respect_series_limits: bool = True,
    events: Optional[Sequence[Event]] = None,
) -> str:
    """
    Random mix among the full morning visual pool (Founder Aug 14 ~2:31pm CT).

    Pool = Magritte / Folk / Da Vinci / Einstein + Thursday equal-card shop-made
    + artistic hero shop-made. Day-seeded shuffle among series-eligible ids
    (max 1 consecutive, max 2 in rolling 7). Not a rigid new-styles-only block.

    Date-keyed queue entries are separate: ensure_flyer_for_day keeps unused
    queued plates when present; this chooser applies to NEW generation / remake.
    """
    pool = active_mixed_pool()
    lim = series_limit_config()
    if force:
        key = str(force).strip()
        if key in lim["banned_ids"]:
            raise ValueError(
                f"visual style {key!r} is banned (series_limit 0) — "
                "cannot force for morning generation"
            )
        if key in pool:
            return key
        if key in (load_styles_config().get("styles") or {}):
            return key
        raise ValueError(f"unknown visual style force={key!r}")

    # Artistic hero only when ≤1 event; drop from pool on multi-event days.
    n_events = len(pick_events_for_flyer(events or []))
    candidates = []
    for sid in pool:
        meta = style_meta(sid)
        if meta.get("single_event_only") and n_events >= 2:
            continue
        candidates.append(sid)
    if not candidates:
        candidates = list(pool)

    if not respect_series_limits:
        return _day_style_rng(day).choice(candidates)

    hist = history
    if hist is None:
        hist = queued_visual_style_history(
            day, lookback_days=int(lim["rolling_window_days"])
        )

    eligible = [
        sid
        for sid in candidates
        if style_passes_series_limits(sid, day, hist, limits=lim)
    ]
    if not eligible:
        # Fail soft: least-used families in the window.
        window = int(lim["rolling_window_days"])
        counts: Dict[str, int] = {sid: 0 for sid in candidates}
        for i in range(1, window):
            prev = hist.get(day - timedelta(days=i))
            if not prev:
                continue
            fam = style_family(prev)
            for sid in candidates:
                if style_family(sid) == fam:
                    counts[sid] += 1
        eligible = sorted(candidates, key=lambda s: (counts[s], s))

    rng = _day_style_rng(day)
    # Shuffle then pick first — true mix, not ordinal lockstep.
    shuffled = list(eligible)
    rng.shuffle(shuffled)
    return shuffled[0]


def visual_style_prompt_bit(style_id: str) -> str:
    """Art-language fragment for build_generation_prompt."""
    meta = style_meta(style_id)
    label = meta.get("label") or style_id
    brief = str(meta.get("prompt_brief") or "").strip()
    pride_place = str(meta.get("pride_placement") or "").strip()
    fix = str(meta.get("readability_fix") or "").strip()
    pool_kind = str(meta.get("pool") or "mixed").strip()
    parts = [
        f" VISUAL STYLE (Founder Aug 14 mixed pool — required): '{label}' "
        f"({style_id}, pool={pool_kind})."
    ]
    if brief:
        parts.append(f" {brief}")
    if fix:
        parts.append(f" READABILITY FIX: {fix}")
    if pride_place:
        parts.append(f" Pride placement: {pride_place}")
    parts.append(
        " Do NOT use Bauhaus Swiss goldleaf or Victorian botanical ledger "
        "(Founder OUT). Do NOT use the banned mystic AI navy template. "
        "Chicagoland #1 / Premier / Voted pride MUST be baked into this plate."
    )
    return "".join(parts)


def choose_layout_style(
    day: date,
    events: Optional[Sequence[Event]] = None,
    *,
    force: Optional[str] = None,
    visual_style: Optional[str] = None,
) -> str:
    """
    Equal-weight vs artistic-hero structure.

    Multi-event days (2+) always prefer equal cards/bands for readability.
    Visual style may request artistic_hero only for single-event days.
    Art *language* is separate — see choose_visual_style().
    """
    if force in (LAYOUT_THURSDAY, LAYOUT_ARTISTIC):
        return force
    picked = pick_events_for_flyer(events or [])
    if len(picked) >= 2:
        return LAYOUT_THURSDAY
    if visual_style:
        layout_hint = str(style_meta(visual_style).get("layout") or "").strip()
        if layout_hint == LAYOUT_ARTISTIC and len(picked) <= 1:
            return LAYOUT_ARTISTIC
        if layout_hint == LAYOUT_THURSDAY:
            return LAYOUT_THURSDAY
    # Stable ~25% artistic: day ordinal mod 4 == 0 → artistic (1/4).
    if (day.toordinal() % 4) == 0 and len(picked) <= 1:
        return LAYOUT_ARTISTIC
    return LAYOUT_THURSDAY


def entry_has_pride_baked(entry: Optional[Dict[str, Any]]) -> bool:
    """True when a queued flyer already records designed-in Chicagoland pride."""
    if not isinstance(entry, dict):
        return False
    if entry.get("pride_baked_in") is True:
        return True
    # Explicit false / missing → needs bake for Founder Aug 14 every-plate rule.
    return False


def bake_pride_band_new_asset(
    src_path: str,
    *,
    day: date,
    style_id: str = "",
    out_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Bake Chicagoland pride into a NEW local file (Founder Aug 14 ~2:31pm CT).

    Never overwrites the source path / old media URL in place. Used when a
    queued flyer will ship but lacks pride_baked_in — creates a new asset that
    must be uploaded as a fresh URL (never-reuse still absolute).
    """
    if not src_path or not os.path.isfile(src_path):
        return None
    from . import social_proof as sp

    pride_opt = pride_option_for_style(style_id or "thursday_cards_shop_made")
    claim = sp.option_on_image_text(pride_opt) or sp.option_on_image_text("B")
    if not claim:
        return None
    abs_src = src_path if os.path.isabs(src_path) else os.path.join(ROOT, src_path)
    if not os.path.isfile(abs_src):
        return None
    # Never pride-stamp the banned navy PIL factory — that is how Aug 25 shipped.
    if flyer_is_banned_mystic_navy_pil(abs_src):
        return None
    if not out_path:
        base, ext = os.path.splitext(abs_src)
        out_path = f"{base}-pride-{day.isoformat()}{ext or '.png'}"
    if os.path.abspath(out_path) == os.path.abspath(abs_src):
        raise ValueError("pride bake must write a NEW path — refuse in-place stamp")
    result = sp.bake_designed_in_pride_new_asset(
        abs_src,
        out_path=out_path,
        text=claim,
        style="footer_band",
        seed=f"morning-pride|{day.isoformat()}|{style_id}",
    )
    if not result:
        return None
    result["pride_baked_in"] = True
    result["pride_option"] = pride_opt
    result["local"] = _rel_asset(str(result.get("path") or out_path))
    return result


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
    visual_style: Optional[str] = None,
) -> str:
    """Prompt for mlimg / GenerateImage polish — mixed pool + equal cards.

    `variant` a = Facebook (cleaner card energy OK);
    `variant` b = Instagram — same full-day cards, richer background pop required.
    `visual_style` overrides the day-seeded random mixed-pool pick.
    """
    covers = list(copy.get("covers") or [])
    events_bit = ""
    if events:
        picked = pick_events_for_flyer(events)
        card_lines = []
        for ev in picked[:3]:
            host = _host_from_title(ev.title) or "use real practitioner name from title"
            time_ln = _event_time_line(ev)
            title = (ev.title or "").lstrip("*").strip()
            card_lines.append(f"{title} — host {host} — {time_ln}")
        if card_lines:
            events_bit = (
                " EQUAL CARDS (exact text — never invent 'Host Name' or wrong times): "
                + " | ".join(card_lines)
                + "."
            )
    elif covers:
        events_bit = " Events on equal cards: " + " · ".join(covers[:3]) + "."
    visit = ""
    if copy.get("empty_day"):
        visit = (
            " Empty calendar visit day: warm invite to come into Sacred Ground "
            "(crystals, quiet wonder) — not a plain storefront photo."
        )
    art_id = visual_style or choose_visual_style(day, events=events)
    style = layout or choose_layout_style(day, events, visual_style=art_id)
    art_bit = visual_style_prompt_bit(art_id)
    n_events = len(pick_events_for_flyer(events or []))
    # Multi-event days never use artistic hero (equal cards only).
    if n_events >= 2:
        style = LAYOUT_THURSDAY
    weekday = day.strftime("%A").upper()
    key = (variant or VARIANT_A).lower().strip()
    is_b = key in (VARIANT_B, "b", "ig", "instagram", "alt")
    equal_rule = (
        " EQUAL SPACE RULE (hard): when 2+ events appear, every event gets the "
        "SAME card size and visual weight — stacked equal rounded cards / equal "
        "bands / equal columns. FORBIDDEN: one large hero photo/title with a "
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

    pride_opt = pride_option_for_style(art_id)
    pride_bit = sp.designed_in_generation_brief(
        f"morning|{day.isoformat()}|{variant}|{art_id}",
        day=day,
        surface="morning",
        campaign="today",
        force_option=pride_opt,
    )
    # Founder Aug 14: morning plates must show clear #1 / Chicagoland pride.
    pride_bit += (
        " MORNING PRIDE EMPHASIS (Founder Aug 14): on-image claim must read as "
        "number-one / premier / voted Chicagoland at a glance — prefer visible "
        f"'#1 Chicagoland' or Option {pride_opt} phrasing for this style. "
        "Never omit store pride from a NEW morning plate."
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
        "language by day via the approved style rotation — never clone "
        "yesterday's plate."
        f"{art_bit}{anti_template}{pride_bit}"
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
    # Default / multi-event path: equal visual weight inside the day's art style.
    return (
        "Sacred Ground EQUAL-WEIGHT multi-event morning flyer, square 1080x1080 "
        "(Thursday-style readable schedule energy inside the day's art style). "
        "Readable schedule for every event (IDENTICAL visual weight — stacked "
        "bands, equal cards, or equal poster columns OK). HEADER may use "
        f"'{weekday} AT Sacred Ground' or an original typographic treatment — "
        "do NOT default to navy+gold script factory every day. Art language MUST "
        f"follow the rotated style '{art_id}' — NEVER right-side mystic object "
        "dump. FOOTER logo + website + phone + come-as-you-are. "
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


# Title-only TEC cards that do not encode the host in the title.
TITLE_HOST_OVERRIDES = {
    "frequency reset": "Eve",
    "*frequency reset": "Eve",
    "shaman medium melissa": "Melissa",
    "amber | customized therapeutic massage sessions": "Amber",
    "amber | customized therapeutic massage sessions".lower(): "Amber",
}


def _host_from_title(title: str) -> str:
    t = title or ""
    key = t.strip().lstrip("*").strip().lower()
    if key in TITLE_HOST_OVERRIDES:
        return TITLE_HOST_OVERRIDES[key]
    for override_key, host in TITLE_HOST_OVERRIDES.items():
        clean = override_key.lstrip("*").strip().lower()
        if key == clean or key.startswith(clean.split("|")[0].strip()):
            return host
    # "Amber | Customized…" / "Name | Role"
    if "|" in t:
        left = t.split("|", 1)[0].strip().lstrip("*").strip()
        if 2 <= len(left.split()) <= 3 and len(left) <= 24:
            return left[:40]
    # "Tina's Intuitive Tarot…" → Tina
    if "'s " in t or "’s " in t:
        head = t.replace("’s ", "'s ").split("'s ", 1)[0]
        head = head.lstrip("*").strip()
        if head:
            return head.split()[-1][:40]
    for sep in (" with ", " With ", " w/ ", " W/ ", ": "):
        if sep in t:
            bit = t.split(sep)[-1].strip()
            for cut in (" — ", " - ", "|", " • ", "·"):
                if cut in bit:
                    bit = bit.split(cut)[0].strip()
            if sep.strip().lower() in {"with", "w/"} and ":" in bit:
                bit = bit.split(":", 1)[0].strip()
            return bit[:40]
    low = t.lstrip("*").strip().lower()
    if "free community" in low or low.startswith("free "):
        return ""
    # "Shaman Medium Melissa" → last token if 2–4 words
    words = t.lstrip("*").strip().split()
    if 2 <= len(words) <= 4 and words[-1][:1].isupper():
        return words[-1][:40]
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
    """PIL preview path — always under `_pil_preview/` (never publishable assets root)."""
    suffix = "" if variant == VARIANT_A else f"-{variant}"
    preview_dir = os.path.join(ASSETS_DIR, "_pil_preview")
    os.makedirs(preview_dir, exist_ok=True)
    return os.path.join(
        preview_dir, f"sg-morning-flyer-{day.isoformat()}-{slug}{suffix}.png"
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
    art_id = choose_visual_style(day, events=events or [])
    layout = choose_layout_style(day, events or [], visual_style=art_id)
    entry: Dict[str, Any] = {
        "label": copy["label"],
        "covers": list(copy.get("covers") or []),
        "local": _rel_asset(local) if local else "",
        "url": url or "",
        "prebranded": True,
        "template": "thursday-style" if layout == LAYOUT_THURSDAY else "artistic_hero",
        "visual_style": art_id,
        "pride_baked_in": True,
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
            "visual_style",
            "pride_baked_in",
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

    # Queue priority: keep an existing visual_style unless regenerating.
    prev_vs = ""
    prev_pride = False
    if isinstance(prev, dict):
        prev_vs = str(prev.get("visual_style") or "").strip()
        prev_pride = bool(prev.get("pride_baked_in"))
    if reset_public_urls or not prev_vs:
        entry["visual_style"] = art_id
        entry["pride_baked_in"] = True
    else:
        entry["visual_style"] = prev_vs
        entry["pride_baked_in"] = prev_pride or bool(entry.get("pride_baked_in"))

    fb_u = str(entry.get("url") or "").strip()
    ig_u = str(entry.get("url_instagram") or "").strip()
    if fb_u and ig_u and fb_u != ig_u:
        entry["urls"] = [fb_u, ig_u]
    elif "urls" in entry and not (fb_u and ig_u and fb_u != ig_u):
        # Keep legacy urls only when dual variants are not yet both public.
        pass

    flyers[day.isoformat()] = entry
    lim = series_limit_config()
    data["layout_mix"] = {
        "thursday_cards_share": THURSDAY_CARDS_SHARE,
        "artistic_hero_share": round(1.0 - THURSDAY_CARDS_SHARE, 2),
        "default": LAYOUT_THURSDAY,
        "visual_style_mixed_pool": active_mixed_pool(),
        "visual_styles_config": "config/morning_flyer_styles.json",
        "selection_mode": "random_mixed",
        "queue_and_reuse": (
            "keep unused queued plates + legacy approaches in the mix; "
            "never-reuse URLs absolute; pride baked into every morning plate"
        ),
        "series_limits": {
            "max_consecutive_days": lim["max_consecutive_days"],
            "rolling_window_days": lim["rolling_window_days"],
            "max_per_style_in_window": lim["max_per_style_in_window"],
        },
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
    allow_pil_preview: bool = False,
) -> Dict[str, Any]:
    """
    Ensure a primary full-day flyer exists for Chicago `day`.

    Mixed pool (Founder Aug 14 ~2:31pm CT): unused date-keyed queue entries stay
    in the mix; NEW gens pick randomly among Magritte/Folk/Da Vinci/Einstein +
    Thursday shop-made + artistic hero (series-limited). Every plate must have
    Chicagoland pride baked in — queued plates missing pride get a NEW local
    (and cleared public URL for re-upload). Never-reuse URLs remain absolute.

    Single-image mode (Founder Aug 10 2026): one excellent `url`/`local` plate
    is shared on Facebook and Instagram. Separate IG variants are not required
    (opt-in via allow_ig_variant + url_instagram only).
    """
    day_events = _day_events(day, events)
    copy = build_flyer_copy(day, day_events)
    art_id = choose_visual_style(day, events=day_events)
    layout = choose_layout_style(day, day_events, visual_style=art_id)
    prompt = build_generation_prompt(
        day,
        copy,
        layout=layout,
        events=day_events,
        variant=VARIANT_A,
        visual_style=art_id,
    )

    existing = flyer_entry_for_day(day)
    publish_blockers = (
        entry_fails_publish_blockers(existing)
        if existing and day.isoformat() not in PROTECTED_DAYS
        else []
    )
    energy_failed = (
        entry_fails_visual_energy(existing)
        if existing and day.isoformat() not in PROTECTED_DAYS
        else []
    )
    # Hard blockers always force. Soft energy fails only when there is no
    # shippable public URL yet — a wired AI/shop URL must win over a leftover
    # `_pil_preview` local that fails color-energy (Aug 25 ensure regression).
    if publish_blockers and not force:
        force = True
    elif energy_failed and not force:
        url_ok = bool(str((existing or {}).get("url") or "").strip()) and not (
            entry_publish_block_reason(existing) if existing else True
        )
        if not url_ok:
            force = True

    # Pride guarantee: queued plate without pride_baked_in → bake NEW local.
    pride_baked_now = False
    if (
        existing
        and not force
        and day.isoformat() not in PROTECTED_DAYS
        and not entry_has_pride_baked(existing)
        and (load_styles_config().get("pride_on_morning") or {}).get(
            "bake_missing_into_new_url", True
        )
    ):
        local_rel = str(existing.get("local") or "").strip()
        abs_local = (
            local_rel
            if os.path.isabs(local_rel)
            else os.path.join(ROOT, local_rel)
            if local_rel
            else ""
        )
        style_for_pride = (
            normalize_queued_style_id(existing) or art_id or "thursday_cards_shop_made"
        )
        baked = bake_pride_band_new_asset(
            abs_local, day=day, style_id=style_for_pride
        )
        if baked:
            # NEW asset → clear public URL so upload creates a fresh never-used URL.
            existing = register_flyer(
                day,
                local=str(baked.get("local") or baked.get("path") or ""),
                url="",
                media_id=None,
                copy=copy,
                events=day_events,
                merge=True,
                reset_public_urls=True,
            )
            existing["pride_baked_in"] = True
            existing["visual_style"] = style_for_pride
            # Persist pride flag (register may have set it True for reset path).
            data = load_flyers_config()
            flyers = data.setdefault("flyers", {})
            flyers[day.isoformat()] = existing
            save_flyers_config(data)
            pride_baked_now = True

    if existing and not force and not publish_blockers:
        fb = str(existing.get("url") or "").strip()
        missing = [] if fb else ["facebook"]
        return {
            "day": day.isoformat(),
            "action": "exists" if not pride_baked_now else "pride_baked",
            "needs_upload": bool(missing),
            "needs_upload_platforms": missing,
            "entry": existing,
            "local": existing.get("local"),
            "layout": layout,
            "visual_style": existing.get("visual_style")
            or normalize_queued_style_id(existing)
            or art_id,
            "prompt": prompt,
            "single_image_mode": True,
            "pride_baked_in": entry_has_pride_baked(existing) or pride_baked_now,
        }

    if force and day.isoformat() in PROTECTED_DAYS and existing:
        # Never overwrite the Aug 6 gold standard.
        return {
            "day": day.isoformat(),
            "action": "exists",
            "needs_upload": not bool(existing.get("url")),
            "entry": existing,
            "layout": layout,
            "visual_style": existing.get("visual_style") or art_id,
            "prompt": prompt,
            "protected": True,
            "single_image_mode": True,
            "pride_baked_in": entry_has_pride_baked(existing),
        }

    clear_urls = bool(publish_blockers or energy_failed) or (
        force and existing and day.isoformat() not in PROTECTED_DAYS
    )

    if not allow_pil_preview:
        # Never ship the deprecated navy PIL compositor — require mixed-pool AI art.
        entry = register_flyer(
            day,
            local=str((existing or {}).get("local") or "") if existing else "",
            url="",
            media_id=None,
            copy=copy,
            events=day_events,
            merge=bool(existing),
            reset_public_urls=True,
        )
        entry["visual_style"] = art_id
        entry["generation_source"] = "needs_ai_art"
        entry["banned_pil_cleared"] = True
        data = load_flyers_config()
        flyers = data.setdefault("flyers", {})
        flyers[day.isoformat()] = entry
        save_flyers_config(data)
        return {
            "day": day.isoformat(),
            "action": "needs_ai_generation",
            "needs_upload": True,
            "needs_upload_platforms": ["facebook"],
            "needs_ai_generation": True,
            "entry": entry,
            "local": entry.get("local") or "",
            "layout": layout,
            "visual_style": art_id,
            "prompt": prompt,
            "single_image_mode": True,
            "pride_baked_in": True,
            "regenerated_for_visual_energy": energy_failed or None,
            "error": (
                "Banned generic navy PIL template removed — generate mixed-pool AI "
                f"art ({art_id}) via mlimg / GenerateImage, then upload."
            ),
        }

    out_a = render_local_flyer(day, day_events, variant=VARIANT_A)
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
    entry["generation_source"] = "pil_compositor_preview"
    data = load_flyers_config()
    flyers = data.setdefault("flyers", {})
    flyers[day.isoformat()] = entry
    save_flyers_config(data)
    fb = str(entry.get("url") or "")
    return {
        "day": day.isoformat(),
        "action": "created",
        "needs_upload": not bool(fb),
        "needs_upload_platforms": [] if fb else ["facebook"],
        "entry": entry,
        "local": out_a,
        "layout": layout,
        "visual_style": art_id,
        "prompt": prompt,
        "single_image_mode": True,
        "pride_baked_in": True,
        "regenerated_for_visual_energy": energy_failed or None,
        "pil_preview_only": True,
    }


def ensure_flyers_for_range(
    *,
    days: int = 7,
    start: Optional[date] = None,
    events: Optional[Sequence[Event]] = None,
    source: str = "cache",
    force: bool = False,
    allow_pil_preview: bool = False,
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
        info = ensure_flyer_for_day(
            day, day_events, force=force, allow_pil_preview=allow_pil_preview
        )
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
    if image_url_is_banned_mystic_navy_pil(url):
        raise ValueError(
            "refusing to wire banned mystic navy PIL URL into morning_flyers"
        )
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
    # Real AI / shop upload replaces any prior PIL preview provenance.
    src = entry_generation_source(entry)
    if src in BANNED_GENERATION_SOURCES:
        entry["generation_source"] = "external_ai_or_shop_upload"
        entry.pop("pil_preview_only", None)
        entry.pop("banned_pil_cleared", None)
    # Detach banned / preview locals so plan/publish cannot revive them.
    local = str(entry.get("local") or "").strip()
    abs_local = _abs_asset(local) if local else ""
    local_norm = local.replace("\\", "/")
    detach_why = ""
    if abs_local and os.path.isfile(abs_local) and flyer_is_banned_mystic_navy_pil(
        abs_local
    ):
        detach_why = "detached banned navy PIL local after real URL wire"
    elif entry.get("pil_preview_only") or "/_pil_preview/" in local_norm:
        detach_why = "detached pil_preview local after real URL wire"
    if detach_why:
        entry["local"] = ""
        entry.pop("pil_preview_only", None)
        entry["note"] = (str(entry.get("note") or "") + " | " + detach_why).strip(
            " |"
        )
    fb = str(entry.get("url") or "").strip()
    ig = str(entry.get("url_instagram") or "").strip()
    if fb and ig and fb != ig:
        entry["urls"] = [fb, ig]
    save_flyers_config(data)
    return entry
