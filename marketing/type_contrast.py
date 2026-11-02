"""Park overlay type on the darkest readable band of THIS photo.

Founder Oct 31 2026: look at the picture. White (or gold) sits on the
dark wood / water / asphalt — not on yellow linen, pale sky, or a
template Y. Tea-table lock: below the tabletop, on the apron.
"""

from __future__ import annotations

from typing import Tuple

from PIL import Image

# Leave room for the circular sun in the photo's lower-left.
_TOP_PAD = 40
_BOTTOM_PAD = 170
_SIDE_PAD = 80
_BAND_H = 96


def _luma_band(rgb: Image.Image, y: int, h: int, side: int) -> float:
    w, _ = rgb.size
    crop = rgb.crop((side, y, w - side, min(rgb.size[1], y + h))).convert("L")
    hist = crop.histogram()
    total = sum(hist) or 1
    return sum(i * n for i, n in enumerate(hist)) / total


def darkest_type_y(
    photo: Image.Image,
    *,
    line_h: int = _BAND_H,
    top_pad: int = _TOP_PAD,
    bottom_pad: int = _BOTTOM_PAD,
    side_pad: int = _SIDE_PAD,
) -> int:
    """Return a Y (in photo pixels) for the start of overlay type.

    Scans horizontal bands and picks the darkest mean luma. Skips the
    top edge and the sun / footer-adjacent strip at the bottom.
    """
    rgb = photo.convert("RGB")
    _, h = rgb.size
    y0 = max(0, top_pad)
    y1 = max(y0 + line_h, h - bottom_pad)
    if y1 <= y0:
        return y0
    best_y = y0
    best_luma = 256.0
    step = 10
    y = y0
    while y + line_h <= y1:
        luma = _luma_band(rgb, y, line_h, side_pad)
        if luma < best_luma:
            best_luma = luma
            best_y = y
        y += step
    return int(best_y)


def band_luma(photo: Image.Image, y: int, h: int = _BAND_H) -> float:
    return _luma_band(photo.convert("RGB"), y, h, _SIDE_PAD)


def type_fill_for_band(photo: Image.Image, y: int, h: int = _BAND_H) -> Tuple[int, int, int]:
    """White on a dark band; black if the best band is still light."""
    luma = band_luma(photo, y, h)
    if luma >= 140:
        return (8, 8, 8)
    return (255, 255, 255)
