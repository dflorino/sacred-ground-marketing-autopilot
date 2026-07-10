from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any, Dict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_DIR = os.path.join(ROOT, "config")
DATA_DIR = os.path.join(ROOT, "data")
DRAFTS_DIR = os.path.join(DATA_DIR, "drafts")
STATE_DIR = os.path.join(DATA_DIR, "state")
FIXTURES_DIR = os.path.join(DATA_DIR, "fixtures")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
AUDIT_DIR = os.path.join(DATA_DIR, "audit")
LIVE_CACHE_PATH = os.path.join(CACHE_DIR, "live_events.json")

CONTROL_PATH = os.path.join(STATE_DIR, "control.json")
POSTED_PATH = os.path.join(STATE_DIR, "posted.json")
OVERRIDES_PATH = os.path.join(STATE_DIR, "overrides.json")


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def settings() -> Dict[str, Any]:
    return _load_json(os.path.join(CONFIG_DIR, "settings.json"))


@lru_cache(maxsize=1)
def voice() -> Dict[str, Any]:
    return _load_json(os.path.join(CONFIG_DIR, "voice.json"))


@lru_cache(maxsize=1)
def accounts() -> Dict[str, Any]:
    return _load_json(os.path.join(CONFIG_DIR, "accounts.json"))


def ensure_dirs() -> None:
    for path in (DRAFTS_DIR, STATE_DIR, FIXTURES_DIR, CACHE_DIR, AUDIT_DIR):
        os.makedirs(path, exist_ok=True)
    if not os.path.exists(CONTROL_PATH):
        write_json(
            CONTROL_PATH,
            {
                "phase": settings().get("default_phase", 1),
                "paused": False,
                "paused_at": None,
                "paused_reason": None,
                "updated_at": None,
            },
        )
    if not os.path.exists(POSTED_PATH):
        write_json(POSTED_PATH, {"fingerprints": {}, "updated_at": None})
    if not os.path.exists(OVERRIDES_PATH):
        write_json(OVERRIDES_PATH, {"skipped_fingerprints": {}, "updated_at": None})


def write_json(path: str, obj: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)


def read_json(path: str, default: Any = None) -> Any:
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)
