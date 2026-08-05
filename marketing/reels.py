"""Daily HeyGen reels scaffold — Instagram + Facebook Reels primary.

Does NOT publish. Does NOT touch today / week_ahead / tuesday_meditation image jobs.
Video auto-publish stays off until HeyGen → hosted MP4 → Zernio/Meta Reels is proven.
"""
from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import schedule
from .ingest import today_local
from .paths import CONFIG_DIR, ROOT, settings

REELS_CONFIG_PATH = Path(CONFIG_DIR) / "reels.json"
SCRIPTS_CONFIG_PATH = Path(CONFIG_DIR) / "reel_scripts.json"
BACKGROUNDS_DIR = Path(ROOT) / "assets" / "heygen" / "backgrounds"
EXTERIOR_PLATE = Path(ROOT) / "assets" / "heygen" / "sg-store-background.jpg"

# Prefer welcome-family scripts for rotation; observatory when beneath_surface provided.
_WELCOME_ROTATION_IDS = (
    "welcome",
    "shop_vibe",
    "come_as_you_are",
    "readings_soft_invite",
    "meditation_tuesday",
    "observatory_teaser",
)


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def reels_config() -> Dict[str, Any]:
    if not REELS_CONFIG_PATH.is_file():
        return {}
    return _load_json(REELS_CONFIG_PATH)


def reel_scripts() -> Dict[str, Any]:
    if not SCRIPTS_CONFIG_PATH.is_file():
        return {"scripts": []}
    return _load_json(SCRIPTS_CONFIG_PATH)


def campaign_config() -> Dict[str, Any]:
    return (settings().get("campaigns") or {}).get("daily_reel") or {}


def primary_platforms() -> List[str]:
    cfg = reels_config().get("publish") or {}
    platforms = list(cfg.get("platforms_primary") or cfg.get("platforms") or [])
    if platforms:
        return platforms
    camp = campaign_config()
    return list(camp.get("platforms") or ["instagram_reels", "facebook_reels"])


def optional_platforms() -> List[str]:
    cfg = reels_config().get("publish") or {}
    if cfg.get("platforms_optional_later"):
        return list(cfg["platforms_optional_later"])
    return list(campaign_config().get("optional_platforms") or [])


def zernio_account_key(platform: str) -> str:
    """Map reel platform ids to config/accounts.json keys (same FB/IG pages)."""
    mapping = (reels_config().get("publish") or {}).get("zernio_account_map") or {}
    if platform in mapping and isinstance(mapping[platform], str):
        return mapping[platform]
    if platform.endswith("_reels"):
        return platform.replace("_reels", "")
    return platform


def script_by_id(script_id: str) -> Optional[Dict[str, Any]]:
    for item in reel_scripts().get("scripts") or []:
        if item.get("id") == script_id:
            return item
    return None


def pick_script_id(day: date, *, beneath_surface: Optional[str] = None) -> str:
    """Rotate welcome-batch scripts; prefer observatory_teaser when beneath_surface given."""
    text = (beneath_surface or "").strip()
    if text:
        if script_by_id("observatory_teaser"):
            return "observatory_teaser"
    available = [sid for sid in _WELCOME_ROTATION_IDS if script_by_id(sid)]
    if not available:
        scripts = reel_scripts().get("scripts") or []
        if scripts:
            return str(scripts[0]["id"])
        return "welcome"
    # Stable day-of-year rotation (America/Chicago calendar day).
    idx = day.toordinal() % len(available)
    return available[idx]


def trim_beneath_surface(text: str, *, max_chars: int = 280) -> str:
    cleaned = " ".join((text or "").split())
    if len(cleaned) <= max_chars:
        return cleaned
    cut = cleaned[: max_chars - 1].rsplit(" ", 1)[0]
    return (cut or cleaned[: max_chars - 1]).rstrip(".,;:") + "…"


def build_spoken(
    script: Dict[str, Any],
    *,
    beneath_surface: Optional[str] = None,
) -> str:
    base = (script.get("spoken") or "").strip()
    insight = trim_beneath_surface(beneath_surface or "")
    if not insight or script.get("id") != "observatory_teaser":
        return base
    return (
        "Every day, our Observatory offers a quiet look Beneath the Surface.\n\n"
        f"{insight}\n\n"
        "Peek when you have a moment — it changes every day.\n"
        "shopsacredground.com/sacred-ground-observatory"
    )


def caption_for_reel(
    script: Dict[str, Any],
    platform: str,
    *,
    beneath_surface: Optional[str] = None,
) -> Dict[str, Any]:
    """Platform caption under the Reel (not on-image text)."""
    base = (script.get("caption") or "").strip()
    links = list(script.get("links") or ["https://shopsacredground.com/"])
    if beneath_surface and script.get("id") == "observatory_teaser":
        base = (
            "A quiet daily look Beneath the Surface — Sacred Ground Observatory. "
            "https://shopsacredground.com/sacred-ground-observatory/ · 847-749-3922"
        )
        links = ["https://shopsacredground.com/sacred-ground-observatory/"]
    tags = ["#SacredGround", "#ArlingtonHeights"]
    if platform == "instagram_reels":
        tags.extend(["#Reels", "#CrystalShop"])
    elif platform == "facebook_reels":
        tags.append("#Reels")
    text = base
    if tags:
        text = f"{base}\n\n{' '.join(tags)}"
    return {
        "text": text,
        "hook": (script.get("onscreen_text") or ["Sacred Ground"])[0],
        "script_id": script.get("id"),
        "platform": platform,
        "links": links,
    }


def plan_daily_reel(
    day: Optional[date] = None,
    *,
    beneath_surface: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a dry plan for one calendar day (no drafts written, no publish)."""
    day = day or today_local()
    camp = campaign_config()
    script_id = pick_script_id(day, beneath_surface=beneath_surface)
    script = script_by_id(script_id) or {
        "id": script_id,
        "spoken": "",
        "caption": "Sacred Ground — Arlington Heights. shopsacredground.com",
        "links": ["https://shopsacredground.com/"],
        "onscreen_text": ["Sacred Ground"],
    }
    spoken = build_spoken(script, beneath_surface=beneath_surface)
    sched = schedule.schedule_daily_reel(day)
    platforms = primary_platforms()
    drafts = []
    for platform in platforms:
        drafts.append(
            {
                "campaign": "daily_reel",
                "platform": platform,
                "zernio_account_key": zernio_account_key(platform),
                "format": camp.get("format") or "9:16",
                "media_type": "video",
                "schedule_recommendation": sched.to_dict(),
                "caption": caption_for_reel(
                    script, platform, beneath_surface=beneath_surface
                ),
                "spoken": spoken,
                "script_id": script_id,
                "auto_publish": bool(camp.get("auto_publish")),
                "publish_blocked_reason": "reels_video_path_not_ready",
            }
        )
    return {
        "ok": True,
        "campaign": "daily_reel",
        "day": day.isoformat(),
        "timezone": "America/Chicago",
        "enabled": bool(camp.get("enabled")),
        "auto_publish": bool(camp.get("auto_publish")),
        "script_id": script_id,
        "content_source": (
            "observatory_beneath_surface"
            if (beneath_surface or "").strip()
            else "welcome_batch"
        ),
        "platforms_primary": platforms,
        "platforms_optional_later": optional_platforms(),
        "schedule": sched.to_dict(),
        "draft_plans": drafts,
        "note": (
            "Scaffold only — no video publish. "
            "Image Today/week-ahead/tuesday_meditation jobs unchanged."
        ),
    }


def _env_set(name: str) -> bool:
    return bool((os.environ.get(name) or "").strip())


def _interior_count() -> int:
    if not BACKGROUNDS_DIR.is_dir():
        return 0
    exts = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
    return sum(
        1
        for p in BACKGROUNDS_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in exts and not p.name.startswith(".")
    )


def readiness() -> Dict[str, Any]:
    """Honest checklist: what works vs what blocks daily IG+FB Reels auto-run."""
    camp = campaign_config()
    pub = reels_config().get("publish") or {}
    blocked: List[str] = []
    if not _env_set("HEYGEN_API_KEY"):
        blocked.append(
            "HEYGEN_API_KEY missing for API generate (manual HeyGen UI still OK)"
        )
    if not _env_set("HEYGEN_AVATAR_ID"):
        blocked.append("HEYGEN_AVATAR_ID missing (API generate)")
    if not _env_set("HEYGEN_VOICE_ID"):
        blocked.append("HEYGEN_VOICE_ID missing (API generate)")
    if _interior_count() == 0:
        blocked.append("No interior plates in assets/heygen/backgrounds/ yet")
    blocked.append(
        "Video publish path unproven: need hosted 9:16 MP4 URL + "
        "Zernio/ML Social (or Meta) Reels support — image posts work today"
    )
    if camp.get("auto_publish"):
        blocked.append("daily_reel.auto_publish is true but video path is not ready")

    next_steps = [
        "Drop interior backgrounds → assets/heygen/backgrounds/",
        "Generate first 9:16 reel in HeyGen (script: welcome)",
        "Founder approve → post manually to Instagram Reels + Facebook Reels",
        "Host MP4 at HTTPS URL; confirm Zernio/ML Social accepts type=video for FB+IG",
        "Only then: enable campaign + Cloud Agent (see AUTOMATION-DRAFT.md scaffold)",
    ]
    return {
        "stack": reels_config().get("stack"),
        "status": reels_config().get("status"),
        "timezone": "America/Chicago",
        "works_today": {
            "image_posts_zernio": True,
            "campaigns": ["today", "week_ahead", "tuesday_meditation"],
            "secret": "ZERNIO_API_KEY",
            "media_type": "image",
        },
        "target": {
            "platforms_primary": primary_platforms(),
            "platforms_optional_later": optional_platforms(),
            "format": "9:16",
            "schedule_local_time": camp.get("schedule_local_time")
            or pub.get("schedule_local_time")
            or "10:30",
            "auto_publish": bool(camp.get("auto_publish")),
            "campaign_enabled": bool(camp.get("enabled")),
        },
        "assets": {
            "exterior_plate": EXTERIOR_PLATE.exists(),
            "interior_background_count": _interior_count(),
            "script_count": len(reel_scripts().get("scripts") or []),
        },
        "env": {
            "ZERNIO_API_KEY": "set" if _env_set("ZERNIO_API_KEY") else "missing",
            "HEYGEN_API_KEY": "set" if _env_set("HEYGEN_API_KEY") else "missing",
            "HEYGEN_AVATAR_ID": "set" if _env_set("HEYGEN_AVATAR_ID") else "missing",
            "HEYGEN_VOICE_ID": "set" if _env_set("HEYGEN_VOICE_ID") else "missing",
        },
        "blocked_for_auto_reels": blocked,
        "next_concrete_steps": next_steps,
        "isolation": reels_config().get("isolation"),
        "yesterday_observatory_hint": {
            "wp_option_pattern": "eeo_daily_YYYY-MM-DD",
            "field": "beneath_surface",
            "example_day": (today_local() - timedelta(days=1)).isoformat(),
        },
    }
