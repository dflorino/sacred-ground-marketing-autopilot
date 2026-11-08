"""Galactic Reel first-frame engine — S1E17 Actual Martians is the bar.

Mute the first frame. If a stranger cannot name the punch in one glance,
do not generate a still and do not roll TopView. KEEP-locked episodes
are never blocked by this gate (S1E19 cabin stays on Nov 18).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .paths import CONFIG_DIR

REELS_MEDIA_PATH = Path(CONFIG_DIR) / "reels_media.json"

LOCATION_OPENERS = (
    "we've landed",
    "we landed",
    "we've arrived",
    "we arrived",
    "we're here",
    "we are here",
    "just think",
)
DISCOVERY_OPENERS = (
    "we've found",
    "we found",
    "we've found them",
    "look at their",
    "actual martians",
)


def load_reels_media() -> Dict[str, Any]:
    if not REELS_MEDIA_PATH.is_file():
        return {}
    with REELS_MEDIA_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def engine() -> Dict[str, Any]:
    return dict(load_reels_media().get("galactic_first_frame_engine") or {})


def opener_kind(text: str) -> str:
    t = (text or "").strip().lower()
    if not t:
        return "missing"
    if any(m in t for m in DISCOVERY_OPENERS):
        return "discovery"
    if any(m in t for m in LOCATION_OPENERS):
        return "location"
    return "unknown"


def will_block_new_roll(
    opener: str,
    *,
    punch_visible: bool,
    keep_locked: bool = False,
) -> List[str]:
    """Fail closed on a NEW Galactic roll. KEEP episodes pass through."""
    if keep_locked:
        return []
    blocks: List[str] = []
    kind = opener_kind(opener)
    if kind in ("location", "missing"):
        blocks.append("opener_is_location_not_discovery")
    if not punch_visible:
        blocks.append("first_frame_punch_missing")
    return blocks


def mute_first_frame_gate(
    *,
    punch_one_liner: str,
    opener: str,
    keep_locked: bool = False,
) -> Dict[str, Any]:
    punch = (punch_one_liner or "").strip()
    punch_visible = bool(punch) and len(punch.split()) <= 24
    blocks = will_block_new_roll(
        opener, punch_visible=punch_visible, keep_locked=keep_locked
    )
    return {
        "ok": not blocks,
        "will_block": blocks,
        "opener_kind": opener_kind(opener),
        "punch_one_liner": punch,
        "bar_episode": engine().get("bar_episode") or "s1e17",
    }
