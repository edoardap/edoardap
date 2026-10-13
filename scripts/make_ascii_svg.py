#!/usr/bin/env python3
"""
make_ascii_svg.py — Convert source-prepped.png into an animated ASCII SVG.

Usage:
    python scripts/make_ascii_svg.py

Input:  source-prepped.png
Output: edoardap-ascii.svg

The SVG uses SMIL animations so GitHub renders it inside <img> tags.
Each row is revealed left-to-right (wipe clip), staggered top-to-bottom.
The portrait prints once and freezes — no loop.
"""

from pathlib import Path

import numpy as np
from PIL import Image

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
RAMP = " .`:-=+*cs#%@"   # bright (sparse) → dark (dense)
COLS = 100                # character grid width
FONT_W = 6.6              # px per char (monospace estimate)
FONT_H = 13               # px per row (line-height)
CHAR_FILL = "#b0b8c8"     # monochrome fill — light gray on dark bg
BG_COLOR = "#0d1117"      # GitHub dark background
WIPE_SPEED = 0.18         # seconds per row reveal
STAGGER = 0.045           # stagger between rows (s)

INPUT = Path("source-prepped.png")
OUTPUT = Path("edoardap-ascii.svg")


def image_to_ascii(img_path: Path, cols: int) -> list[str]:
    img = Image.open(img_path).convert("L")
    w, h = img.size
    # Maintain aspect — terminal chars are ~2× taller than wide
    rows = int(h / w * cols * 0.45)
    img = img.resize((cols, rows), Image.LANCZOS)
    pixels = np.array(img)
    ramp_len = len(RAMP) - 1
    lines = []
    for row in pixels:
        line = "".join(RAMP[int(p / 255 * ramp_len)] for p in row)
        lines.append(line)
    return lines


def build_svg(lines: list[str]) -> str:
    n_rows = len(lines)
    n_cols = max(len(l) for l in lines)
    vw = n_cols * FONT_W
    vh = n_rows * FONT_H + FONT_H  # +1 row padding at bottom
    total_anim = n_rows * STAGGER + WIPE_SPEED + 0.3

    defs_parts = []
    text_parts = []

    for i, line in enumerate(lines):
        clip_id = f"c{i}"
        delay = i * STAGGER
        # clip rect that wipes left-to-right
        defs_parts.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="0" y="{i * FONT_H}" width="0" height="{FONT_H}">'
            f'<animate attributeName="width" values="0;{vw}" '
            f'dur="{WIPE_SPEED}s" begin="{delay:.3f}s" '
            f'fill="freeze" calcMode="linear"/>'
            f'</rect>'
            f'</clipPath>'
        )
        safe = (
            line
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        text_parts.append(
            f'<text clip-path="url(#{clip_id})" '
            f'x="0" y="{(i + 1) * FONT_H}" '
            f'fill="{CHAR_FILL}">{safe}</text>'
        )

    defs = "\n  ".join(defs_parts)
    texts = "\n  ".join(text_parts)

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{vw:.0f}" height="{vh:.0f}" '
        f'viewBox="0 0 {vw:.2f} {vh:.2f}">\n'
        f'<style>\n'
        f'  text {{ font-family: "Courier New", Courier, monospace; '
        f'font-size: {FONT_H - 2}px; white-space: pre; }}\n'
        f'</style>\n'
        f'<rect width="100%" height="100%" fill="{BG_COLOR}"/>\n'
        f'<defs>\n  {defs}\n</defs>\n'
        f'{texts}\n'
        f'</svg>'
    )
    return svg


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(
            f"{INPUT} not found — run prep_photo.py first."
        )
    print(f"Converting {INPUT} → ASCII ({COLS} cols)…")
    lines = image_to_ascii(INPUT, COLS)
    print(f"Grid: {len(lines)} rows × {max(len(l) for l in lines)} cols")
    svg = build_svg(lines)
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Saved → {OUTPUT}")


if __name__ == "__main__":
    main()
