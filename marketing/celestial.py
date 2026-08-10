"""Dated celestial event spotlights — night-before + morning-of cadence."""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .paths import ROOT


@lru_cache(maxsize=1)
def celestial_config() -> Dict[str, Any]:
    path = Path(ROOT) / "config" / "celestial_events.json"
    if not path.is_file():
        return {"events": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_day(raw: Any) -> Optional[date]:
    if not raw:
        return None
    try:
        return datetime.strptime(str(raw), "%Y-%m-%d").date()
    except ValueError:
        return None


def _events() -> Dict[str, Dict[str, Any]]:
    raw = celestial_config().get("events") or {}
    return {str(k): v for k, v in raw.items() if isinstance(v, dict)}


def _urls_from_block(block: Dict[str, Any]) -> List[str]:
    urls = [str(u) for u in (block.get("urls") or []) if u]
    primary = str(block.get("url") or "")
    if primary and primary not in urls:
        urls.insert(0, primary)
    return urls


def _pick_url(
    urls: List[str],
    day: date,
    platform: Optional[str],
    exclude_urls: Optional[List[str]] = None,
) -> Optional[str]:
    if not urls:
        return None
    excluded = {str(u) for u in (exclude_urls or []) if u}
    available = [u for u in urls if u not in excluded] or list(urls)
    from .images import platform_salt

    return available[(day.toordinal() + platform_salt(platform)) % len(available)]


def celestial_night_for(day: date) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Publish night (week_ahead) is the day *before* the celestial event."""
    for cid, meta in sorted(_events().items(), key=lambda kv: str(kv[0])):
        if meta.get("active") is False:
            continue
        post = _parse_day(meta.get("post_night_before"))
        event_day = _parse_day(meta.get("event_date"))
        if post is None and event_day is not None:
            post = event_day - timedelta(days=1)
        if post == day:
            return cid, meta
    return None


def celestial_morning_for(day: date) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Morning-of: publish day equals the celestial event_date."""
    for cid, meta in sorted(_events().items(), key=lambda kv: str(kv[0])):
        if meta.get("active") is False:
            continue
        if _parse_day(meta.get("event_date")) == day:
            return cid, meta
    return None


def night_plan(
    day: date,
    platform: Optional[str] = None,
    exclude_urls: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    hit = celestial_night_for(day)
    if not hit:
        return None
    cid, meta = hit
    block = meta.get("night") or {}
    url = _pick_url(_urls_from_block(block), day, platform, exclude_urls)
    if not url:
        return None
    return {
        "id": cid,
        "label": str(meta.get("label") or cid),
        "event_date": str(meta.get("event_date") or ""),
        "mode": "celestial",
        "slot": "night_before",
        "image_url": url,
        "look": str(block.get("look") or meta.get("one_liner_night") or ""),
        "caption_opener": str(meta.get("caption_tomorrow") or ""),
        "sg_anchor": str(block.get("sg_anchor") or ""),
    }


def morning_plan(
    day: date,
    platform: Optional[str] = None,
    exclude_urls: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    hit = celestial_morning_for(day)
    if not hit:
        return None
    cid, meta = hit
    block = meta.get("morning") or {}
    url = _pick_url(_urls_from_block(block), day, platform, exclude_urls)
    if not url:
        return None
    return {
        "id": cid,
        "label": str(meta.get("label") or cid),
        "event_date": str(meta.get("event_date") or ""),
        "mode": "celestial",
        "slot": "morning_of",
        "image_url": url,
        "look": str(block.get("look") or meta.get("one_liner_morning") or ""),
        "caption_opener": str(meta.get("caption_today") or ""),
        "sg_anchor": str(block.get("sg_anchor") or ""),
        "prebranded": bool(block.get("prebranded", False)),
    }


def schedule_rows() -> List[Dict[str, str]]:
    """Human schedule table rows for docs / Founder report."""
    rows: List[Dict[str, str]] = []
    for cid, meta in sorted(
        _events().items(),
        key=lambda kv: str(kv[1].get("event_date") or ""),
    ):
        event_day = _parse_day(meta.get("event_date"))
        night = _parse_day(meta.get("post_night_before"))
        if night is None and event_day is not None:
            night = event_day - timedelta(days=1)
        rows.append(
            {
                "id": cid,
                "event": str(meta.get("label") or cid),
                "event_date": event_day.isoformat() if event_day else "",
                "night_before": night.isoformat() if night else "",
                "morning_of": event_day.isoformat() if event_day else "",
                "caption_tomorrow": str(meta.get("caption_tomorrow") or ""),
                "caption_today": str(meta.get("caption_today") or ""),
            }
        )
    return rows
