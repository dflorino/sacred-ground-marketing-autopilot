from __future__ import annotations

import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from .models import Event
from .paths import FIXTURES_DIR, LIVE_CACHE_PATH, settings

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def strip_html(text: str) -> str:
    if not text:
        return ""
    t = _TAG_RE.sub(" ", text)
    t = html.unescape(t)
    return _WS_RE.sub(" ", t).strip()


def tzinfo() -> ZoneInfo:
    return ZoneInfo(settings()["timezone"])


def today_local(now: Optional[datetime] = None) -> date:
    now = now or datetime.now(tzinfo())
    if now.tzinfo is None:
        now = now.replace(tzinfo=tzinfo())
    return now.astimezone(tzinfo()).date()


def parse_tec_datetime(value: str) -> Optional[datetime]:
    if not value:
        return None
    value = value.strip()
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(value.replace("Z", "+0000"), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=tzinfo())
            return dt.astimezone(tzinfo())
        except ValueError:
            continue
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tzinfo())
        return dt.astimezone(tzinfo())
    except ValueError:
        return None


def _image_url(raw: Any) -> Optional[str]:
    if not raw:
        return None
    if isinstance(raw, str):
        return raw
    if isinstance(raw, dict):
        if raw.get("url"):
            return raw["url"]
        sizes = raw.get("sizes") or {}
        for key in ("large", "medium_large", "full", "medium"):
            block = sizes.get(key)
            if isinstance(block, dict) and block.get("url"):
                return block["url"]
    return None


def _names(items: Any) -> List[str]:
    out: List[str] = []
    if not items:
        return out
    for item in items:
        if isinstance(item, dict):
            name = item.get("name") or item.get("slug")
            if name:
                out.append(str(name))
        elif isinstance(item, str):
            out.append(item)
    return out


def normalize_tec_event(raw: Dict[str, Any]) -> Event:
    title = strip_html(str(raw.get("title") or ""))
    # Featured marker used on Sacred Ground: asterisk in title
    starred = "*" in title
    title_clean = title.replace("*", "").strip()
    url = (raw.get("url") or raw.get("website") or "").strip()
    desc = strip_html(str(raw.get("description") or ""))
    excerpt = strip_html(str(raw.get("excerpt") or ""))[:400]
    cats = _names(raw.get("categories"))
    tags = _names(raw.get("tags"))
    featured_flag = bool(raw.get("featured")) or starred
    venue = raw.get("venue") or {}
    venue_name = ""
    if isinstance(venue, dict):
        venue_name = venue.get("venue") or venue.get("name") or ""
    elif isinstance(venue, list) and venue:
        v0 = venue[0]
        if isinstance(v0, dict):
            venue_name = v0.get("venue") or v0.get("name") or ""

    return Event(
        id=int(raw["id"]),
        title=title_clean,
        start_date=str(raw.get("start_date") or ""),
        end_date=str(raw.get("end_date") or raw.get("start_date") or ""),
        url=url,
        description=desc,
        excerpt=excerpt,
        all_day=bool(raw.get("all_day")),
        featured=featured_flag,
        image_url=_image_url(raw.get("image")),
        categories=cats,
        tags=tags,
        cost=str(raw.get("cost") or ""),
        venue_name=venue_name or "Sacred Ground",
        timezone=str(raw.get("timezone") or settings()["timezone"]),
    )


def fetch_tec_events(
    start: Optional[date] = None,
    end: Optional[date] = None,
    per_page: int = 50,
    timeout: int = 30,
) -> List[Event]:
    """Pull upcoming events from The Events Calendar REST API."""
    cfg = settings()
    start = start or today_local()
    end = end or (start + timedelta(days=21))
    params = {
        "per_page": str(per_page),
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "status": "publish",
    }
    url = cfg["tec_events_url"] + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "SG-Marketing-Autopilot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"TEC fetch failed: {exc}") from exc

    if isinstance(payload, dict) and payload.get("code") and "events" not in payload:
        raise RuntimeError(f"TEC error: {payload.get('message') or payload}")

    raw_events = payload.get("events") if isinstance(payload, dict) else payload
    if not isinstance(raw_events, list):
        raise RuntimeError("Unexpected TEC response shape")

    return [normalize_tec_event(e) for e in raw_events if e.get("id")]


def load_fixture_events(name: str = "sample_events.json") -> List[Event]:
    path = f"{FIXTURES_DIR}/{name}"
    with open(path, encoding="utf-8") as fh:
        payload = json.load(fh)
    raw_events = payload.get("events") if isinstance(payload, dict) else payload
    return [normalize_tec_event(e) for e in raw_events]


def load_cache_events(path: Optional[str] = None) -> List[Event]:
    """Load events from a WordPress DB / MCP export cache (TEC-shaped JSON)."""
    path = path or LIVE_CACHE_PATH
    with open(path, encoding="utf-8") as fh:
        payload = json.load(fh)
    raw_events = payload.get("events") if isinstance(payload, dict) else payload
    return [normalize_tec_event(e) for e in raw_events if e.get("id")]


def save_cache_events(events: List[Event], meta: Optional[Dict[str, Any]] = None) -> str:
    """Persist normalized events for offline / blocked-network runs."""
    import os
    from .paths import CACHE_DIR, ensure_dirs

    ensure_dirs()
    payload = {
        "source": (meta or {}).get("source", "cache"),
        "site": settings().get("site_url"),
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "description": e.description,
                "excerpt": e.excerpt,
                "url": e.url,
                "start_date": e.start_date,
                "end_date": e.end_date,
                "all_day": e.all_day,
                "featured": e.featured,
                "timezone": e.timezone,
                "image": {"url": e.image_url} if e.image_url else None,
                "categories": [{"name": c} for c in e.categories],
                "tags": [{"name": t} for t in e.tags],
                "cost": e.cost,
                "venue": {"venue": e.venue_name},
            }
            for e in events
        ],
    }
    if meta:
        for k, v in meta.items():
            if k != "events":
                payload[k] = v
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(LIVE_CACHE_PATH, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return LIVE_CACHE_PATH


def load_events(source: str = "auto") -> Tuple[List[Event], str]:
    """
    source: live | live-strict | cache | fixture | auto

    live / live-strict: TEC REST only. Fail hard — never fall back to cache/fixture.
    auto: local/dev convenience (TEC → cache → fixture). Not for Automations.
    """
    if source == "fixture":
        return load_fixture_events(), "fixture"
    if source == "cache":
        return load_cache_events(), "cache"
    if source in ("live", "live-strict"):
        events = fetch_tec_events()
        try:
            save_cache_events(events, {"source": "tec_rest"})
        except Exception:
            pass
        return events, "live"
    # auto — local/dev only; Automations must use live-strict
    try:
        events = fetch_tec_events()
        try:
            save_cache_events(events, {"source": "tec_rest"})
        except Exception:
            pass
        return events, "live"
    except Exception:
        try:
            return load_cache_events(), "cache_fallback"
        except Exception:
            return load_fixture_events(), "fixture_fallback"
