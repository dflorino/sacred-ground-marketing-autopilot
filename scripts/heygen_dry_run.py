#!/usr/bin/env python3
"""HeyGen reels dry-run — check secrets + optionally probe API (no video spend by default).

Does NOT touch morning/evening FB/IG autopilot.

Usage:
  python3 scripts/heygen_dry_run.py           # status + checklist
  python3 scripts/heygen_dry_run.py --probe   # GET /v3/avatars + /v3/voices if HEYGEN_API_KEY set
  python3 scripts/heygen_dry_run.py --script welcome --generate   # create video (needs IDs + key)

Env (never commit):
  HEYGEN_API_KEY          required for --probe / --generate
  HEYGEN_AVATAR_ID        Digital Twin / avatar look id
  HEYGEN_VOICE_ID         cloned Fish/HeyGen voice id
  HEYGEN_BACKGROUND_ASSET_ID   optional HeyGen asset id for store plate
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
REELS_CONFIG = ROOT / "config" / "reels.json"
SCRIPTS_CONFIG = ROOT / "config" / "reel_scripts.json"
BACKGROUNDS_DIR = ROOT / "assets" / "heygen" / "backgrounds"
EXTERIOR_PLATE = ROOT / "assets" / "heygen" / "sg-store-background.jpg"
API_BASE = "https://api.heygen.com"


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _env(name: str) -> str:
    return (os.environ.get(name) or "").strip()


def _image_files(directory: Path) -> List[Path]:
    if not directory.is_dir():
        return []
    exts = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
    return sorted(
        p
        for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in exts and not p.name.startswith(".")
    )


def _api_get(path: str, api_key: str) -> Tuple[int, Any]:
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        headers={"X-Api-Key": api_key, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"raw": raw}
        return exc.code, payload


def _api_post(path: str, api_key: str, payload: Dict[str, Any]) -> Tuple[int, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        data=data,
        headers={
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload_err = json.loads(raw)
        except json.JSONDecodeError:
            payload_err = {"raw": raw}
        return exc.code, payload_err


def status_report() -> Dict[str, Any]:
    reels = _load_json(REELS_CONFIG) if REELS_CONFIG.exists() else {}
    scripts = _load_json(SCRIPTS_CONFIG) if SCRIPTS_CONFIG.exists() else {}
    interiors = _image_files(BACKGROUNDS_DIR)
    key = _env("HEYGEN_API_KEY")
    avatar = _env("HEYGEN_AVATAR_ID") or (reels.get("heygen") or {}).get("avatar_id") or ""
    voice = _env("HEYGEN_VOICE_ID") or (reels.get("heygen") or {}).get("voice_id") or ""

    blocked: List[str] = []
    if not key:
        blocked.append("HEYGEN_API_KEY missing (add to .env / Cloud Agent secrets — never commit)")
    if not avatar:
        blocked.append("HEYGEN_AVATAR_ID missing (copy from HeyGen Digital Twin / avatar look)")
    if not voice:
        blocked.append("HEYGEN_VOICE_ID missing (copy from HeyGen Voices — Fish/clone)")
    if not interiors:
        blocked.append(
            "No interior plates yet in assets/heygen/backgrounds/ (Founder shooting today)"
        )

    return {
        "stack": reels.get("stack"),
        "status": reels.get("status"),
        "publish": reels.get("publish"),
        "scripts_batch": scripts.get("batch"),
        "script_count": len(scripts.get("scripts") or []),
        "exterior_plate": str(EXTERIOR_PLATE.relative_to(ROOT)) if EXTERIOR_PLATE.exists() else None,
        "interior_backgrounds": [str(p.relative_to(ROOT)) for p in interiors],
        "env": {
            "HEYGEN_API_KEY": "set" if key else "missing",
            "HEYGEN_AVATAR_ID": "set" if avatar else "missing",
            "HEYGEN_VOICE_ID": "set" if voice else "missing",
            "HEYGEN_BACKGROUND_ASSET_ID": "set" if _env("HEYGEN_BACKGROUND_ASSET_ID") else "optional/missing",
        },
        "blocked_for_api_generate": blocked,
        "manual_path_ready": True,
        "manual_steps": [
            "1. Drop interior photos in assets/heygen/backgrounds/",
            "2. HeyGen UI: avatar + Fish/clone voice + script from data/reels/scripts-batch-01.md (#1 welcome)",
            "3. Custom background: exterior plate or new interior",
            "4. Export 9:16 → Founder approve → post TikTok + YouTube Shorts",
            "5. Optional later: set HEYGEN_API_KEY + avatar/voice IDs → --probe / --generate",
        ],
        "note": "FB/IG morning+evening autopilot is unchanged — this script is reels-only.",
    }


def pick_script(script_id: str) -> Optional[Dict[str, Any]]:
    scripts = _load_json(SCRIPTS_CONFIG)
    for item in scripts.get("scripts") or []:
        if item.get("id") == script_id:
            return item
    return None


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Sacred Ground HeyGen reels dry-run")
    parser.add_argument("--probe", action="store_true", help="List avatars/voices via API")
    parser.add_argument(
        "--generate",
        action="store_true",
        help="POST /v3/videos (uses credits; needs key + avatar + voice)",
    )
    parser.add_argument("--script", default="welcome", help="Script id from reel_scripts.json")
    args = parser.parse_args(argv)

    report = status_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))

    api_key = _env("HEYGEN_API_KEY")
    if args.probe or args.generate:
        if not api_key:
            print("\nBLOCKED: set HEYGEN_API_KEY to probe or generate.", file=sys.stderr)
            return 2

    if args.probe:
        print("\n--- GET /v3/avatars ---")
        code, body = _api_get("/v3/avatars?limit=20", api_key)
        print(f"HTTP {code}")
        print(json.dumps(body, indent=2, ensure_ascii=False)[:4000])
        print("\n--- GET /v3/voices ---")
        code, body = _api_get("/v3/voices?limit=20&type=private", api_key)
        print(f"HTTP {code}")
        print(json.dumps(body, indent=2, ensure_ascii=False)[:4000])

    if args.generate:
        avatar = _env("HEYGEN_AVATAR_ID")
        voice = _env("HEYGEN_VOICE_ID")
        script = pick_script(args.script)
        if not avatar or not voice:
            print("\nBLOCKED: HEYGEN_AVATAR_ID and HEYGEN_VOICE_ID required.", file=sys.stderr)
            return 2
        if not script:
            print(f"\nBLOCKED: unknown script id {args.script!r}", file=sys.stderr)
            return 2
        payload: Dict[str, Any] = {
            "type": "avatar",
            "avatar_id": avatar,
            "script": script["spoken"],
            "voice_id": voice,
            "title": f"SG reel · {script['id']}",
            "aspect_ratio": "9:16",
            "resolution": "1080p",
        }
        bg_asset = _env("HEYGEN_BACKGROUND_ASSET_ID")
        if bg_asset:
            payload["background"] = {"type": "image", "image_asset_id": bg_asset}
            payload["remove_background"] = True
        print(f"\n--- POST /v3/videos (script={args.script}) ---")
        code, body = _api_post("/v3/videos", api_key, payload)
        print(f"HTTP {code}")
        print(json.dumps(body, indent=2, ensure_ascii=False))
        if code >= 400:
            return 1

    if not api_key and not args.probe and not args.generate:
        print(
            "\nDry path OK without API: use manual_steps above. "
            "API generate is blocked until HEYGEN_API_KEY (+ avatar/voice IDs) are set.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
