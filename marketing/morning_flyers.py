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

NOTES = (
    "Date-keyed Cheryl-style finished morning flyers (logo + event text + "
    f"{WEBSITE} / {PHONE} already baked in). When a flyer exists for the "
    "Chicago calendar day, Autopilot uses it first and MUST skip brand overlays "
    "(prebranded: true). NEVER include $, dollar amounts, ticket costs, or "
    '"$55"-style prices on flyer graphics, labels, or prompts — do not bake '
    "Event.cost / TEC cost onto the image. Empty days get a warm visit flyer "
    "(not storefront-only). 1–3 events max on the graphic."
)


def text_has_price(text: str) -> bool:
    """True if text looks like it contains a price / dollar amount."""
    if not text:
        return False
    return bool(PRICE_RE.search(str(text)))


def assert_price_free(*parts: str) -> None:
    bad = [p for p in parts if p and text_has_price(p)]
    if bad:
        raise ValueError(f"Morning flyer must not include prices: {bad!r}")


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
    scored: List[Tuple[int, str, Event]] = []
    for ev in events:
        score = 0
        if getattr(ev, "featured", False) or getattr(ev, "is_special", False):
            score += 10
        low = (ev.title or "").lower()
        if "meditation" in low:
            score += 4
        if any(k in low for k in ("sound bath", "shaman", "quantum", "reflexology", "chakra")):
            score += 3
        scored.append((-score, ev.start_date or "", ev))
    scored.sort()
    return [e for _, __, e in scored[: max(0, limit)]]


def build_flyer_copy(day: date, events: Sequence[Event]) -> Dict[str, Any]:
    """Price-free copy block for a day's flyer (empty → visit day)."""
    picked = pick_events_for_flyer(events)
    weekday = day.strftime("%A").upper()
    date_line = f"{day.strftime('%B')} {day.day}, {day.year}"
    date_short = f"{weekday} · {day.strftime('%B').upper()} {day.day}"

    if not picked:
        label = "Sacred Ground today — visit us"
        covers: List[str] = []
        lines = [
            "SACRED GROUND TODAY",
            "Crystals · readings · quiet wonder",
            "Come browse · Arlington Heights",
            date_short,
        ]
        slug = "visit"
        primary = "Sacred Ground Today"
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


def build_generation_prompt(day: date, copy: Dict[str, Any]) -> str:
    """Prompt for mlimg / GenerateImage polish — still hard-bans prices."""
    also = copy.get("also") or []
    also_bit = ""
    if also:
        also_bit = " Also today (secondary): " + " · ".join(also) + "."
    visit = ""
    if copy.get("empty_day"):
        visit = (
            " Empty calendar visit day: warm invite to come into Sacred Ground "
            "(crystals, quiet wonder) — not a plain storefront photo."
        )
    return (
        f"Sacred Ground Cheryl-style mystical Canva morning flyer, square 1080x1080. "
        f"Chicago date {day.isoformat()}. Primary: {copy.get('primary')}. "
        f"Date/time text: {copy.get('date_short')}. "
        f"{also_bit}{visit} "
        "Sacred geometry accents, elegant mixed fonts (script + serif), "
        "circular Sacred Ground sun-face logo, footer with shopsacredground.com "
        "and 847-749-3922. Prebranded finished flyer. "
        "CRITICAL: do NOT include any prices, dollar signs, ticket costs, or "
        "dollar amounts anywhere on the graphic. No invented practitioner faces "
        "unless a real photo reference is provided."
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
        "script": _font(script, 48) if os.path.isfile(script) else _font(serif, 48),
        "body": _font(sans, 28),
        "small": _font(sans, 22),
        "footer": _font(sans, 24),
    }


def _draw_geometry(draw, cx: int, cy: int, r: int, fill, width: int = 2) -> None:
    # Seed-of-life-ish: center + 6 petals
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=fill, width=width)
    for i in range(6):
        ang = math.radians(60 * i - 30)
        x = int(cx + r * math.cos(ang))
        y = int(cy + r * math.sin(ang))
        draw.ellipse((x - r, y - r, x + r, y + r), outline=fill, width=max(1, width - 1))


def _tina_circle_path(events: Sequence[Event]) -> Optional[str]:
    if not any("tina" in (e.title or "").lower() for e in events):
        return None
    for p in TINA_CIRCLE_REFS:
        if os.path.isfile(p):
            return p
    return None


def render_local_flyer(
    day: date,
    events: Sequence[Event],
    *,
    out_path: Optional[str] = None,
) -> str:
    """
    Render a sustainable Cheryl-style 1080 square with PIL.
    Never draws prices. Includes logo + website + phone footer.
    """
    from PIL import Image, ImageDraw, ImageFilter

    copy = build_flyer_copy(day, events)
    fonts = _pick_fonts()

    # Soft mystical gradient (cream → lavender → dusk)
    img = Image.new("RGB", (CANVAS, CANVAS), (245, 236, 220))
    px = img.load()
    for y in range(CANVAS):
        t = y / (CANVAS - 1)
        r = int(245 - 40 * t)
        g = int(236 - 70 * t)
        b = int(220 + 35 * t)
        for x in range(CANVAS):
            # slight radial warmth
            dx = (x - CANVAS / 2) / CANVAS
            warm = int(12 * (1 - abs(dx)))
            px[x, y] = (min(255, r + warm), min(255, g + warm // 2), b)

    draw = ImageDraw.Draw(img, "RGBA")
    gold = (196, 155, 78, 90)
    _draw_geometry(draw, 160, 150, 70, gold, 2)
    _draw_geometry(draw, 920, 200, 55, (120, 90, 160, 70), 2)

    # Soft cream card
    card = (255, 250, 240, 210)
    draw.rounded_rectangle((60, 80, 1020, 820), radius=36, fill=card)

    # Title
    primary = str(copy["primary"])
    title_font = fonts["title"] if len(primary) < 28 else fonts["title_sm"]
    draw.text((100, 120), primary, font=title_font, fill=(35, 45, 70))

    y = 200
    if copy.get("empty_day"):
        draw.text(
            (100, y),
            "Visit us today",
            font=fonts["script"],
            fill=(140, 90, 50),
        )
        y += 70
        for ln in (
            "Crystals · tools · quiet wonder",
            "Arlington Heights",
            str(copy["date_short"]),
        ):
            draw.text((100, y), ln, font=fonts["body"], fill=(50, 55, 75))
            y += 42
    else:
        draw.text(
            (100, y),
            str(copy["date_short"]),
            font=fonts["body"],
            fill=(70, 55, 100),
        )
        y += 48
        # Time from primary event
        picked = pick_events_for_flyer(events)
        if picked:
            tl = _event_time_line(picked[0])
            if tl:
                assert_price_free(tl)
                draw.text((100, y), tl, font=fonts["title_sm"], fill=(40, 50, 80))
                y += 50
        also = copy.get("also") or []
        if also:
            y += 10
            draw.rounded_rectangle(
                (100, y, 980, y + 40 + 36 * len(also)),
                radius=18,
                fill=(40, 70, 90, 230),
            )
            draw.text(
                (120, y + 12),
                "ALSO TODAY",
                font=fonts["small"],
                fill=(220, 190, 120),
            )
            yy = y + 42
            for name in also:
                assert_price_free(name)
                draw.text((120, yy), name, font=fonts["body"], fill=(250, 248, 240))
                yy += 34

    # Optional Tina circle (real photo only)
    tina = _tina_circle_path(events)
    if tina:
        try:
            circ = Image.open(tina).convert("RGBA")
            circ = circ.resize((220, 220), Image.Resampling.LANCZOS)
            img.paste(circ, (780, 120), circ)
        except OSError:
            pass

    # Footer band
    footer_h = 160
    draw.rectangle((0, CANVAS - footer_h, CANVAS, CANVAS), fill=(25, 35, 65))
    if os.path.isfile(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo = logo.resize((120, 120), Image.Resampling.LANCZOS)
            # ~85% opacity
            alpha = logo.split()[-1].point(lambda a: int(a * 0.85))
            logo.putalpha(alpha)
            img.paste(logo, (40, CANVAS - footer_h + 20), logo)
        except OSError:
            pass
    draw.text(
        (180, CANVAS - footer_h + 45),
        WEBSITE,
        font=fonts["footer"],
        fill=(240, 220, 160),
    )
    draw.text(
        (180, CANVAS - footer_h + 85),
        PHONE,
        font=fonts["footer"],
        fill=(250, 250, 250),
    )
    draw.text(
        (620, CANVAS - footer_h + 65),
        "Your sacred space",
        font=fonts["script"],
        fill=(210, 180, 110),
    )

    # Soften slightly
    img = img.filter(ImageFilter.SMOOTH_MORE)

    # Final text safety: filenames and copy already checked; re-check copy.
    assert_price_free(copy["label"], *copy.get("covers") or [], *copy.get("lines") or [])

    if not out_path:
        os.makedirs(ASSETS_DIR, exist_ok=True)
        out_path = os.path.join(
            ASSETS_DIR, f"sg-morning-flyer-{day.isoformat()}-{copy['slug']}.png"
        )
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    return out_path


def register_flyer(
    day: date,
    *,
    local: str,
    url: str = "",
    media_id: Optional[int] = None,
    copy: Optional[Dict[str, Any]] = None,
    events: Optional[Sequence[Event]] = None,
) -> Dict[str, Any]:
    """Append/update a day entry in morning_flyers.json."""
    copy = copy or build_flyer_copy(day, events or [])
    assert_price_free(
        copy.get("label") or "",
        *(copy.get("covers") or []),
        *(copy.get("lines") or []),
    )
    rel_local = local
    if os.path.isabs(local) and local.startswith(ROOT + os.sep):
        rel_local = os.path.relpath(local, ROOT)

    entry: Dict[str, Any] = {
        "label": copy["label"],
        "covers": list(copy.get("covers") or []),
        "local": rel_local.replace("\\", "/"),
        "url": url or "",
        "prebranded": True,
    }
    if media_id is not None:
        entry["media_id"] = int(media_id)
    if copy.get("empty_day"):
        entry["empty_day"] = True

    data = load_flyers_config()
    flyers = data.setdefault("flyers", {})
    flyers[day.isoformat()] = entry
    save_flyers_config(data)
    return entry


def ensure_flyer_for_day(
    day: date,
    events: Sequence[Event],
    *,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Ensure a flyer exists for Chicago `day`.
    Returns status dict: action=exists|created, needs_upload, entry, prompt.
    """
    existing = flyer_entry_for_day(day)
    if existing and not force:
        url = str(existing.get("url") or "")
        return {
            "day": day.isoformat(),
            "action": "exists",
            "needs_upload": not bool(url),
            "entry": existing,
            "prompt": build_generation_prompt(day, build_flyer_copy(day, events)),
        }

    day_events: List[Event] = []
    for e in events:
        start = parse_tec_datetime(e.start_date)
        if start and start.date() == day:
            day_events.append(e)
    # Caller may already pass a day-scoped list (no other dates).
    if not day_events and events:
        only_today = True
        for e in events:
            start = parse_tec_datetime(e.start_date)
            if start and start.date() != day:
                only_today = False
                break
        if only_today:
            day_events = list(events)

    copy = build_flyer_copy(day, day_events)
    out = render_local_flyer(day, day_events)
    entry = register_flyer(day, local=out, url="", copy=copy, events=day_events)
    return {
        "day": day.isoformat(),
        "action": "created",
        "needs_upload": True,
        "entry": entry,
        "local": out,
        "prompt": build_generation_prompt(day, copy),
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


def set_flyer_url(day: date, url: str, media_id: Optional[int] = None) -> Dict[str, Any]:
    data = load_flyers_config()
    entry = (data.get("flyers") or {}).get(day.isoformat())
    if not isinstance(entry, dict):
        raise KeyError(f"No flyer entry for {day.isoformat()}")
    entry["url"] = url
    if media_id is not None:
        entry["media_id"] = int(media_id)
    save_flyers_config(data)
    return entry
