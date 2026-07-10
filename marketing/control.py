from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from .ingest import tzinfo
from .paths import ensure_dirs, read_json, settings, write_json
from . import paths as _paths


def _control_path() -> str:
    return _paths.CONTROL_PATH


def load_control() -> Dict[str, Any]:
    ensure_dirs()
    data = read_json(_control_path())
    if not data:
        data = {
            "phase": settings().get("default_phase", 1),
            "paused": False,
            "paused_at": None,
            "paused_reason": None,
            "updated_at": None,
        }
        write_json(_control_path(), data)
    return data


def save_control(data: Dict[str, Any]) -> Dict[str, Any]:
    ensure_dirs()
    data["updated_at"] = datetime.now(tzinfo()).isoformat()
    write_json(_control_path(), data)
    return data


def is_paused() -> bool:
    return bool(load_control().get("paused"))


def phase() -> int:
    return int(load_control().get("phase") or 1)


def pause(reason: str = "manual") -> Dict[str, Any]:
    data = load_control()
    data["paused"] = True
    data["paused_at"] = datetime.now(tzinfo()).isoformat()
    data["paused_reason"] = reason
    return save_control(data)


def resume() -> Dict[str, Any]:
    data = load_control()
    data["paused"] = False
    data["paused_at"] = None
    data["paused_reason"] = None
    return save_control(data)


def set_phase(n: int) -> Dict[str, Any]:
    if n not in (1, 2, 3):
        raise ValueError("phase must be 1, 2, or 3")
    data = load_control()
    data["phase"] = n
    return save_control(data)


def publish_allowed() -> tuple[bool, Optional[str]]:
    """Phase 1 never publishes. Pause blocks all publish/schedule."""
    if is_paused():
        return False, "autopilot_paused"
    p = phase()
    if p < 2:
        return False, "phase_1_drafts_only"
    return True, None
