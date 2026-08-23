"""Living Worlds layer repo — manifests, paths, init, sync, validation.

Layer sets live in GitHub at:
  assets/living_worlds/<slug>/scene-raw.png
  assets/living_worlds/<slug>/layers/*.png
  data/living_worlds/layers/<style_id>/manifest.json + prompts/
  remotion/public/layers/<slug>/  (synced copy for Remotion)

Docs: docs/LIVING-WORLDS-LAYERS-REPO.md
Rule: .cursor/rules/living-worlds-layers.mdc
"""
from __future__ import annotations

import os
import shutil
from datetime import date
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .living_worlds import (
    LIVING_WORLDS_DATA,
    build_living_world_prompt,
    load_living_worlds_config,
    living_world_style_meta,
)
from .paths import ROOT, read_json, write_json

LAYERS_DATA = os.path.join(LIVING_WORLDS_DATA, "layers")
ASSETS_LW = os.path.join(ROOT, "assets", "living_worlds")
REMOTION_LAYERS = os.path.join(ROOT, "remotion", "public", "layers")

# Six-anchor core — every concept needs these decomposed layers.
CORE_LAYERS: Tuple[str, ...] = (
    "background-plate.png",
    "coffee-cup.png",
    "candle-body.png",
    "candle-flame.png",
    "candle-glow.png",
    "incense-holder.png",
    "hero-crystal.png",
    "pendant.png",
    "card-front.png",
    "card-back.png",
)

OPTIONAL_LAYERS: Tuple[str, ...] = (
    "foreground-frame.png",
    "reader.png",
    "reader-hand.png",
    "crystal-highlight.png",
    "coffee-steam-1.png",
    "coffee-steam-2.png",
    "coffee-steam-3.png",
    "incense-smoke-1.png",
    "incense-smoke-2.png",
    "incense-smoke-3.png",
)

# Layout-specific moving parts (see config morning_living_worlds.json → layout).
LAYOUT_EXTRAS: Dict[str, Tuple[str, ...]] = {
    "mechanism_tabletop": ("open-sign.png", "lever.png", "kettle.png", "gear.png"),
    "compartment_boxes": (
        "matchbox-1.png",
        "matchbox-2.png",
        "matchbox-3.png",
        "matchbox-4.png",
        "matchbox-5.png",
        "matchbox-lid.png",
    ),
    "paper_pop_up": (
        "book-cover.png",
        "book-spine.png",
        "popup-storefront.png",
        "popup-shelf-left.png",
        "popup-shelf-right.png",
    ),
    "theater_stage": (
        "curtain-left.png",
        "curtain-right.png",
        "marquee.png",
        "footlight-glow.png",
        "stage-crystal.png",
    ),
    "compartment_cabinet": (
        "cabinet-door-left.png",
        "cabinet-door-right.png",
        "compartment-tray.png",
    ),
    "dollhouse_cutaway": (
        "room-gallery.png",
        "room-studio.png",
        "open-sign-swing.png",
        "shopper-arm.png",
    ),
    "overhead_workbench": (
        "hands-wire-wrap.png",
        "bead-rolling.png",
        "finished-pendant.png",
    ),
    "board_game": (
        "board-base.png",
        "crystal-token.png",
        "event-space-1.png",
        "event-space-2.png",
        "finish-banner.png",
    ),
    "weather_map": (
        "map-base.png",
        "crystal-sun.png",
        "chain-rain.png",
        "fog-layer.png",
        "forecast-panel.png",
    ),
    "ornate_clock": (
        "clock-face.png",
        "clock-hour-hand.png",
        "clock-minute-hand.png",
        "pendulum.png",
        "clock-door.png",
    ),
    "museum_gallery": (
        "display-case-1.png",
        "display-case-2.png",
        "spotlight-beam.png",
        "plaque.png",
    ),
    "shadow_silhouette": (
        "shadow-backdrop.png",
        "shadow-jewelry.png",
        "shadow-reader.png",
        "shadow-storefront.png",
    ),
    "tile_mural": (
        "tile-grid.png",
        "tile-flip-1.png",
        "tile-flip-2.png",
        "tile-flip-3.png",
    ),
    "fabric_embroidery": (
        "fabric-base.png",
        "needle-thread.png",
        "embroidered-card.png",
    ),
    "patchwork_quilt": (
        "quilt-base.png",
        "patch-crystal.png",
        "patch-jewelry.png",
        "border-stitch.png",
    ),
    "blueprint_drawing": (
        "blueprint-base.png",
        "elevator-crystal.png",
        "route-glow.png",
    ),
    "surreal_miniature": (
        "oversized-object.png",
        "miniature-shop-interior.png",
        "scale-door.png",
    ),
    "comic_panels": (
        "panel-1.png",
        "panel-2.png",
        "panel-3.png",
        "panel-4.png",
        "panel-5.png",
        "panel-6.png",
    ),
    "paper_storefront": (
        "storefront-base.png",
        "window-crystal.png",
        "window-jewelry.png",
        "window-candle.png",
        "window-incense.png",
        "reader-door.png",
        "coffee-hatch.png",
        "marquee-fold.png",
    ),
    "found_object_typography": (
        "letter-g.png",
        "letter-o.png",
        "letter-d.png",
        "object-slide-1.png",
        "object-slide-2.png",
    ),
}


def concept_slug(style_id: str) -> str:
    return style_id.replace("living_", "living-").replace("_", "-")


def concept_paths(style_id: str) -> Dict[str, str]:
    slug = concept_slug(style_id)
    return {
        "style_id": style_id,
        "slug": slug,
        "data_dir": os.path.join(LAYERS_DATA, style_id),
        "manifest": os.path.join(LAYERS_DATA, style_id, "manifest.json"),
        "status": os.path.join(LAYERS_DATA, style_id, "status.json"),
        "prompts_dir": os.path.join(LAYERS_DATA, style_id, "prompts"),
        "assets_dir": os.path.join(ASSETS_LW, slug),
        "scene_raw": os.path.join(ASSETS_LW, slug, "scene-raw.png"),
        "layers_dir": os.path.join(ASSETS_LW, slug, "layers"),
        "remotion_dir": os.path.join(REMOTION_LAYERS, slug),
    }


def required_layers_for(style_id: str) -> List[str]:
    meta = living_world_style_meta(style_id)
    layout = str(meta.get("layout") or "")
    extras = list(LAYOUT_EXTRAS.get(layout, ()))
    return list(CORE_LAYERS) + extras


def scene_prompt_for_concept(style_id: str, *, sample_day: Optional[date] = None) -> str:
    """Scene-only hero plate prompt (no baked text)."""
    day = sample_day or date(2026, 8, 24)
    return build_living_world_prompt(day, style_id, [], for_ai_scene_only=True)


def decompose_brief(style_id: str) -> str:
    meta = living_world_style_meta(style_id)
    label = meta.get("label") or style_id
    movement = meta.get("movement_summary") or ""
    layers = required_layers_for(style_id)
    layer_list = "\n".join(f"  - {f}" for f in layers)
    return f"""# Layer decomposition — {label}

**Style id:** `{style_id}`
**Movement:** {movement}

## Rules
1. Export each moving object as a **transparent PNG** on checkerboard alpha.
2. `background-plate.png` = full scene with ALL moving objects removed; inpaint holes cleanly.
3. Do NOT bake schedule text, dates, reader names, website, or phone into any layer.
4. Art band target: **1080×980** (scale from scene-raw).
5. Candle: body separate from flame + glow halo.
6. Coffee steam / incense smoke may be procedural in Remotion — static wisps optional.

## Required files
{layer_list}

## Optional
{chr(10).join('  - ' + f for f in OPTIONAL_LAYERS)}
"""


def layer_prompt(style_id: str, filename: str) -> str:
    meta = living_world_style_meta(style_id)
    label = meta.get("label") or style_id
    brief = meta.get("prompt_brief") or ""
    base = (
        f"Sacred Ground Living World '{label}' — isolated layer `{filename}` only. "
        f"{brief} "
        "Transparent PNG, alpha channel, no background, no text, no watermark. "
        "Shop-made tactile jewel tones, eggplant purple accents, bright engaging color. "
        "NOT generic mystic AI purple fog."
    )
    hints = {
        "background-plate.png": "Full composition with moving objects removed; clean inpainted holes.",
        "hero-crystal.png": "Single hero quartz/amethyst crystal only, with soft shadow.",
        "pendant.png": "Silver pendant on chain; pivot point top-center of chain.",
        "candle-body.png": "Beeswax candle and wick only — NO flame.",
        "candle-flame.png": "Candle flame only, warm orange-gold.",
        "candle-glow.png": "Soft amber radial glow, transparent.",
        "incense-holder.png": "Ceramic holder + incense stick, no smoke.",
        "coffee-cup.png": "Ceramic mug with coffee, no steam.",
        "card-front.png": "Tarot/reader card face-up design, no readable words.",
        "card-back.png": "Ornate card back pattern.",
    }
    extra = hints.get(filename, "Extract only this object from the approved scene-raw.")
    return f"{base} {extra}"


def build_manifest(style_id: str) -> Dict[str, Any]:
    meta = living_world_style_meta(style_id)
    paths = concept_paths(style_id)
    required = required_layers_for(style_id)
    return {
        "version": 1,
        "style_id": style_id,
        "slug": paths["slug"],
        "label": meta.get("label"),
        "layout": meta.get("layout"),
        "medium": meta.get("medium"),
        "energy": meta.get("energy"),
        "status": meta.get("status"),
        "movement_summary": meta.get("movement_summary"),
        "paths": {
            "scene_raw": os.path.relpath(paths["scene_raw"], ROOT),
            "layers_dir": os.path.relpath(paths["layers_dir"], ROOT),
            "remotion_dir": os.path.relpath(paths["remotion_dir"], ROOT),
        },
        "required_layers": required,
        "optional_layers": list(OPTIONAL_LAYERS),
        "approval": {
            "scene_raw": "pending",
            "layers_complete": "pending",
            "founder_look": "pending",
            "assigned_date": None,
        },
    }


def default_status() -> Dict[str, Any]:
    return {
        "scene_raw": "pending",
        "layers_decomposed": "pending",
        "remotion_synced": "pending",
        "founder_look": "pending",
        "notes": "",
    }


def init_concept(style_id: str, *, force: bool = False) -> Dict[str, Any]:
    meta = living_world_style_meta(style_id)
    if not meta:
        return {"ok": False, "error": f"unknown style_id: {style_id}"}

    paths = concept_paths(style_id)
    os.makedirs(paths["data_dir"], exist_ok=True)
    os.makedirs(paths["prompts_dir"], exist_ok=True)
    os.makedirs(paths["layers_dir"], exist_ok=True)
    os.makedirs(paths["remotion_dir"], exist_ok=True)

    manifest_path = paths["manifest"]
    if force or not os.path.isfile(manifest_path):
        write_json(manifest_path, build_manifest(style_id))

    status_path = paths["status"]
    if force or not os.path.isfile(status_path):
        write_json(status_path, default_status())

    scene_prompt_path = os.path.join(paths["prompts_dir"], "scene-raw.txt")
    if force or not os.path.isfile(scene_prompt_path):
        with open(scene_prompt_path, "w", encoding="utf-8") as fh:
            fh.write(scene_prompt_for_concept(style_id))

    decompose_path = os.path.join(paths["prompts_dir"], "decompose-brief.md")
    if force or not os.path.isfile(decompose_path):
        with open(decompose_path, "w", encoding="utf-8") as fh:
            fh.write(decompose_brief(style_id))

    for layer_file in required_layers_for(style_id):
        lp = os.path.join(paths["prompts_dir"], f"layer-{layer_file.replace('.png', '')}.txt")
        if force or not os.path.isfile(lp):
            with open(lp, "w", encoding="utf-8") as fh:
                fh.write(layer_prompt(style_id, layer_file))

    # Legacy pilot asset hook — crystal morning machine
    pilot = (meta.get("pilot_assets") or {}).get("local_scene")
    if pilot and os.path.isfile(os.path.join(ROOT, pilot)) and not os.path.isfile(paths["scene_raw"]):
        os.makedirs(os.path.dirname(paths["scene_raw"]), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, pilot), paths["scene_raw"])
        st = read_json(status_path, default_status()) or default_status()
        st["scene_raw"] = "present"
        write_json(status_path, st)
        man = read_json(manifest_path, {}) or {}
        if man.get("approval"):
            man["approval"]["scene_raw"] = "present"
        write_json(manifest_path, man)

    return {"ok": True, "style_id": style_id, "slug": paths["slug"], "paths": paths}


def init_all(*, force: bool = False) -> Dict[str, Any]:
    cfg = load_living_worlds_config()
    styles = cfg.get("styles") or {}
    results = []
    for style_id in sorted(styles.keys()):
        results.append(init_concept(style_id, force=force))
    write_index()
    return {"ok": True, "count": len(results), "concepts": results}


def write_index() -> str:
    cfg = load_living_worlds_config()
    styles = cfg.get("styles") or {}
    rows: List[Dict[str, Any]] = []
    for style_id in sorted(styles.keys()):
        meta = styles[style_id]
        paths = concept_paths(style_id)
        st = read_json(paths["status"], {}) or {}
        man = read_json(paths["manifest"], {}) or {}
        req = required_layers_for(style_id)
        present = 0
        if os.path.isdir(paths["layers_dir"]):
            present = sum(
                1 for f in req if os.path.isfile(os.path.join(paths["layers_dir"], f))
            )
        rows.append(
            {
                "style_id": style_id,
                "slug": paths["slug"],
                "label": meta.get("label"),
                "layout": meta.get("layout"),
                "scene_raw": "present" if os.path.isfile(paths["scene_raw"]) else "pending",
                "layers": f"{present}/{len(req)}",
                "founder_look": (man.get("approval") or {}).get("founder_look", "pending"),
                "assigned_date": (man.get("approval") or {}).get("assigned_date"),
                "manifest": os.path.relpath(paths["manifest"], ROOT),
            }
        )
    index_path = os.path.join(LAYERS_DATA, "index.json")
    write_json(index_path, {"generated_at": date.today().isoformat(), "concepts": rows})
    return index_path


def validate_concept(style_id: str) -> Dict[str, Any]:
    paths = concept_paths(style_id)
    required = required_layers_for(style_id)
    missing_scene = not os.path.isfile(paths["scene_raw"])
    missing_layers = [
        f for f in required if not os.path.isfile(os.path.join(paths["layers_dir"], f))
    ]
    ok = not missing_scene and not missing_layers
    return {
        "ok": ok,
        "style_id": style_id,
        "slug": paths["slug"],
        "scene_raw": paths["scene_raw"] if not missing_scene else None,
        "missing_scene": missing_scene,
        "missing_layers": missing_layers,
        "required_count": len(required),
        "present_count": len(required) - len(missing_layers),
    }


def validate_all() -> Dict[str, Any]:
    cfg = load_living_worlds_config()
    styles = cfg.get("styles") or {}
    results = [validate_concept(sid) for sid in sorted(styles.keys())]
    ready = [r for r in results if r["ok"]]
    return {
        "ok": len(ready) == len(results),
        "ready_count": len(ready),
        "total": len(results),
        "concepts": results,
    }


def sync_to_remotion(style_id: str) -> Dict[str, Any]:
    paths = concept_paths(style_id)
    os.makedirs(paths["remotion_dir"], exist_ok=True)
    copied: List[str] = []
    if os.path.isfile(paths["scene_raw"]):
        dest = os.path.join(paths["remotion_dir"], "scene-raw.png")
        shutil.copy2(paths["scene_raw"], dest)
        copied.append("scene-raw.png")
    if os.path.isdir(paths["layers_dir"]):
        for name in os.listdir(paths["layers_dir"]):
            if name.endswith(".png"):
                shutil.copy2(
                    os.path.join(paths["layers_dir"], name),
                    os.path.join(paths["remotion_dir"], name),
                )
                copied.append(name)
    st_path = paths["status"]
    st = read_json(st_path, default_status()) or default_status()
    st["remotion_synced"] = "yes" if copied else "no"
    write_json(st_path, st)
    return {"ok": bool(copied), "style_id": style_id, "copied": copied}


def sync_all() -> Dict[str, Any]:
    cfg = load_living_worlds_config()
    styles = cfg.get("styles") or {}
    return {
        "ok": True,
        "results": [sync_to_remotion(sid) for sid in sorted(styles.keys())],
    }


def register_scene_raw(style_id: str, source_path: str) -> Dict[str, Any]:
    """Copy a generated scene plate into the canonical assets path."""
    paths = concept_paths(style_id)
    os.makedirs(os.path.dirname(paths["scene_raw"]), exist_ok=True)
    shutil.copy2(source_path, paths["scene_raw"])

    st = read_json(paths["status"], default_status()) or default_status()
    st["scene_raw"] = "present"
    write_json(paths["status"], st)

    man = read_json(paths["manifest"], build_manifest(style_id)) or build_manifest(style_id)
    man.setdefault("approval", {})["scene_raw"] = "present"
    write_json(paths["manifest"], man)
    write_index()
    return {"ok": True, "style_id": style_id, "scene_raw": paths["scene_raw"]}


def list_pending_scenes() -> List[Dict[str, str]]:
    cfg = load_living_worlds_config()
    pending = []
    for style_id in sorted((cfg.get("styles") or {}).keys()):
        paths = concept_paths(style_id)
        if not os.path.isfile(paths["scene_raw"]):
            pending.append(
                {
                    "style_id": style_id,
                    "slug": paths["slug"],
                    "label": living_world_style_meta(style_id).get("label", style_id),
                    "prompt_file": os.path.join(paths["prompts_dir"], "scene-raw.txt"),
                }
            )
    return pending
