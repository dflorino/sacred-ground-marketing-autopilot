from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional

from .paths import (
    ensure_dirs,
    read_json,
    write_json,
)
from . import paths as _paths
from .ingest import tzinfo


def _drafts_dir() -> str:
    return _paths.DRAFTS_DIR


def _posted_path() -> str:
    return _paths.POSTED_PATH


def _overrides_path() -> str:
    return _paths.OVERRIDES_PATH


def fingerprint(campaign: str, date_key: str, platform: str, event_ids: List[int], extra: str = "") -> str:
    ids = ",".join(str(i) for i in sorted(event_ids))
    base = f"{campaign}|{date_key}|{platform}|{ids}"
    if extra:
        base = f"{base}|{extra}"
    return base


def draft_id(fingerprint_str: str, created_at: str) -> str:
    digest = hashlib.sha1(f"{fingerprint_str}|{created_at}".encode()).hexdigest()[:8]
    # readable prefix from fingerprint
    parts = fingerprint_str.split("|")
    campaign = parts[0] if parts else "x"
    date_key = parts[1] if len(parts) > 1 else "nodate"
    platform = parts[2] if len(parts) > 2 else "x"
    plat = {"facebook": "fb", "instagram": "ig"}.get(platform, platform[:2])
    return f"sgma-{date_key}-{campaign}-{plat}-{digest}"


def load_posted() -> Dict[str, Any]:
    ensure_dirs()
    return read_json(_posted_path(), {"fingerprints": {}, "updated_at": None})


def load_overrides() -> Dict[str, Any]:
    ensure_dirs()
    return read_json(_overrides_path(), {"skipped_fingerprints": {}, "updated_at": None})


def is_reviewed(draft: Dict[str, Any]) -> bool:
    """True once a human (or system) has touched the draft beyond pending draft."""
    if draft.get("locked") or draft.get("edited") or draft.get("reviewed_at"):
        return True
    if draft.get("approval_status") in ("approved", "rejected", "overridden"):
        return True
    if draft.get("status") in ("approved", "rejected", "skipped", "scheduled", "posted"):
        return True
    return False


def is_blocked(fp: str) -> Optional[str]:
    """Return reason if fingerprint should not create a new draft.

    Never recreate or overwrite a fingerprint that already has any draft on disk —
    including pending, approved, rejected, skipped, edited, or posted.
    """
    posted = load_posted().get("fingerprints") or {}
    if fp in posted:
        return "already_posted"
    skipped = load_overrides().get("skipped_fingerprints") or {}
    if fp in skipped:
        return "manual_override"
    for d in list_drafts():
        if d.get("fingerprint") != fp:
            continue
        if is_reviewed(d):
            return "reviewed_draft_exists"
        return "draft_exists"
    return None


def mark_posted(fp: str, draft_id_str: str, meta: Optional[Dict] = None) -> None:
    data = load_posted()
    data.setdefault("fingerprints", {})[fp] = {
        "draft_id": draft_id_str,
        "posted_at": datetime.now(tzinfo()).isoformat(),
        **(meta or {}),
    }
    data["updated_at"] = datetime.now(tzinfo()).isoformat()
    write_json(_posted_path(), data)


def skip_fingerprint(fp: str, reason: str) -> None:
    data = load_overrides()
    data.setdefault("skipped_fingerprints", {})[fp] = {
        "reason": reason,
        "at": datetime.now(tzinfo()).isoformat(),
    }
    data["updated_at"] = datetime.now(tzinfo()).isoformat()
    write_json(_overrides_path(), data)


def save_draft(draft: Dict[str, Any], *, allow_overwrite: bool = False) -> str:
    """Write a draft file. Refuses to overwrite reviewed drafts unless explicitly allowed."""
    ensure_dirs()
    path = f"{_drafts_dir()}/{draft['id']}.json"
    existing = read_json(path)
    if existing and is_reviewed(existing) and not allow_overwrite:
        raise PermissionError(
            f"Refusing to overwrite reviewed draft {draft['id']} "
            f"(status={existing.get('status')}, approval={existing.get('approval_status')})"
        )
    # Also refuse if another file with same fingerprint is reviewed
    fp = draft.get("fingerprint")
    if fp and not allow_overwrite:
        for d in list_drafts():
            if d.get("id") == draft.get("id"):
                continue
            if d.get("fingerprint") == fp and is_reviewed(d):
                raise PermissionError(
                    f"Refusing to write draft for reviewed fingerprint {fp}"
                )
    write_json(path, draft)
    return path


def get_draft(draft_id_str: str) -> Optional[Dict[str, Any]]:
    ensure_dirs()
    path = f"{_drafts_dir()}/{draft_id_str}.json"
    return read_json(path)


def list_drafts(status: Optional[str] = None) -> List[Dict[str, Any]]:
    ensure_dirs()
    import os

    drafts_dir = _drafts_dir()
    if not os.path.isdir(drafts_dir):
        return []

    out: List[Dict[str, Any]] = []
    for name in sorted(os.listdir(drafts_dir)):
        if not name.endswith(".json"):
            continue
        d = read_json(f"{drafts_dir}/{name}")
        if not d:
            continue
        if status and d.get("status") != status:
            continue
        out.append(d)
    return out


def update_draft(
    draft_id_str: str,
    *,
    allow_content_update: bool = False,
    **fields: Any,
) -> Dict[str, Any]:
    """Status / approval updates. Content is immutable once reviewed unless allowed."""
    d = get_draft(draft_id_str)
    if not d:
        raise KeyError(f"Unknown draft: {draft_id_str}")
    # Content fields are immutable once reviewed
    content_keys = {"caption", "image", "events", "links", "fingerprint", "campaign", "platform"}
    if (
        is_reviewed(d)
        and content_keys.intersection(fields.keys())
        and not allow_content_update
    ):
        raise PermissionError(
            f"Refusing to change content on reviewed draft {draft_id_str}"
        )
    d.update(fields)
    d["updated_at"] = datetime.now(tzinfo()).isoformat()
    # allow_overwrite for intentional status transitions (approve/reject/schedule)
    save_draft(d, allow_overwrite=True)
    return d
