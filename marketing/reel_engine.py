#!/usr/bin/env python3
"""Sacred Ground Reel Engine — end-card overlay (thought + SACRED GROUND)."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
AVENIR = Path("/System/Library/Fonts/Avenir Next.ttc")
LOGO = ROOT / "config/brand/sacred-ground-logo-circle-transparent.png"


def _font(size: int, *, index: int = 5) -> ImageFont.FreeTypeFont:
    """House type: Avenir Next Medium (5) / Regular (7). Never italic serif."""
    return ImageFont.truetype(str(AVENIR), size, index=index)


def _center(draw: ImageDraw.ImageDraw, y: int, text: str, fnt, fill, width: int) -> int:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((width - tw) / 2, y - bbox[1]), text, font=fnt, fill=fill)
    return th


def _center_tracked(draw: ImageDraw.ImageDraw, y: int, text: str, fnt, fill, width: int, tracking: float = 6) -> int:
    widths = []
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=fnt)
        widths.append(bbox[2] - bbox[0])
    total = sum(widths) + tracking * max(0, len(text) - 1)
    x = (width - total) / 2
    bbox = draw.textbbox((0, 0), "Ag", font=fnt)
    py = y - bbox[1]
    for ch, w in zip(text, widths):
        draw.text((x, py), ch, font=fnt, fill=fill)
        x += w + tracking
    return bbox[3] - bbox[1]


def _wrap(text: str, fnt, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), trial, font=fnt)
        if bbox[2] - bbox[0] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def overlay_thought(
    src: Path,
    dest: Path,
    line: str,
    *,
    brand: str = "SACRED GROUND",
    thought_starts_at: float = 7.5,
    brand_starts_at: float = 8.7,
    line_size: int = 72,
    brand_size: int = 28,
    width: int = 1080,
    height: int = 1920,
) -> Path:
    cap = cv2.VideoCapture(str(src))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    dest.parent.mkdir(parents=True, exist_ok=True)
    out = cv2.VideoWriter(str(dest), fourcc, fps, (width, height))

    f_line = _font(line_size, index=5)
    f_brand = _font(brand_size, index=7)
    white = (255, 250, 242, 255)
    thought_lines = _wrap(line, f_line, width - 80)

    logo = Image.open(LOGO).convert("RGBA")
    logo_w = 54
    logo = logo.resize((logo_w, logo_w), Image.Resampling.LANCZOS)
    alpha = logo.split()[-1].point(lambda a: int(a * 0.82))
    logo.putalpha(alpha)

    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        t = i / fps
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(rgb).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
        layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)

        if t >= thought_starts_at:
            fade = min(1.0, (t - thought_starts_at) / 0.7)
            a = int(255 * fade)
            fill = (white[0], white[1], white[2], a)
            y = 1460
            for piece in thought_lines:
                y += _center(draw, y, piece, f_line, fill, width) + 10
        if t >= brand_starts_at:
            fade = min(1.0, (t - brand_starts_at) / 0.55)
            a = int(235 * fade)
            fill = (white[0], white[1], white[2], a)
            _center_tracked(draw, 1688, brand, f_brand, fill, width, tracking=8)
            lx, ly = 20, height - logo_w - 28
            stamped = logo.copy()
            la = stamped.split()[-1].point(lambda p, f=fade: int(p * f))
            stamped.putalpha(la)
            layer.paste(stamped, (lx, ly), stamped)

        im = Image.alpha_composite(im, layer).convert("RGB")
        out.write(cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR))
        i += 1

    cap.release()
    out.release()
    print(f"{dest} frames={i} n={n} fps={fps:.2f}")
    return dest


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("src")
    p.add_argument("dest")
    p.add_argument("--line", required=True)
    p.add_argument("--thought-at", type=float, default=7.5)
    p.add_argument("--brand-at", type=float, default=8.7)
    args = p.parse_args()
    overlay_thought(Path(args.src), Path(args.dest), args.line, thought_starts_at=args.thought_at, brand_starts_at=args.brand_at)
