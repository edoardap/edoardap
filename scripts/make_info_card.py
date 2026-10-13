#!/usr/bin/env python3
"""
make_info_card.py — Generate a neofetch-style animated info card SVG.

Usage:
    python scripts/make_info_card.py

Output: info-card.svg

Set env STATIC=1 to emit a frozen frame (for quick preview).
"""

import os
from pathlib import Path

STATIC = os.environ.get("STATIC", "0") == "1"

OUTPUT = Path("info-card.svg")

# --------------------------------------------------------------------------- #
# Card content — edit this to match your details
# --------------------------------------------------------------------------- #
TITLE = "edoardap@github"
TAGLINE = "~/dev"

ROWS = [
    # (key_color, key, value_color, value)
    ("#39d353", "user",     "#e6edf3", "Maria Eduarda"),
    ("#39d353", "role",     "#e6edf3", "Computer Engineering student"),
    ("#39d353", "uni",      "#e6edf3", "CEFET-MG"),
    ("#58a6ff", "now",      "#e6edf3", "AI Agents · Cloud · Backend"),
    ("#58a6ff", "prev",     "#e6edf3", "Web Dev · Embedded Systems"),
    ("#58a6ff", "stack",    "#e6edf3", "Python · JS · C · Java · C++"),
    ("#f78166", "contact",  "#e6edf3", "mariaeduardapereirasm@gmail.com"),
    ("#f78166", "linkedin", "#e6edf3", "linkedin.com/in/mariaeduardapsm"),
    ("#f78166", "discord",  "#e6edf3", "discord.gg/rzvgKwC6"),
]

# --------------------------------------------------------------------------- #
# Layout constants
# --------------------------------------------------------------------------- #
W = 490
FONT_MONO = '"Courier New", Courier, monospace'
FONT_SIZE = 13
LINE_H = 22
PAD_X = 16
TITLE_H = 38
BODY_TOP = TITLE_H + 12
H = BODY_TOP + len(ROWS) * LINE_H + 20

BG = "#0d1117"
BORDER = "#30363d"
TITLE_BG = "#161b22"

FADE_DUR = "0.3s"
SLIDE_DX = 8  # px slide-in


def row_svg(i: int, key_color: str, key: str, val_color: str, val: str) -> str:
    y = BODY_TOP + (i + 1) * LINE_H
    delay = f"{0.15 + i * 0.07:.2f}s"

    if STATIC:
        anim = ""
        opacity = "1"
        transform = ""
    else:
        anim = (
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="-{SLIDE_DX} 0;0 0" dur="{FADE_DUR}" begin="{delay}" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0;1" '
            f'dur="{FADE_DUR}" begin="{delay}" fill="freeze"/>'
        )
        opacity = "0"
        transform = ""

    return (
        f'<g opacity="{opacity}" transform="{transform}">'
        f'{anim}'
        f'<text x="{PAD_X}" y="{y}" fill="{key_color}" '
        f'font-family={FONT_MONO} font-size="{FONT_SIZE}">'
        f'{key}</text>'
        f'<text x="{PAD_X + 80}" y="{y}" fill="#586069" '
        f'font-family={FONT_MONO} font-size="{FONT_SIZE}">:</text>'
        f'<text x="{PAD_X + 92}" y="{y}" fill="{val_color}" '
        f'font-family={FONT_MONO} font-size="{FONT_SIZE}">{val}</text>'
        f'</g>'
    )


def build_svg() -> str:
    rows_svg = "\n".join(row_svg(i, *r) for i, r in enumerate(ROWS))

    title_anim = "" if STATIC else (
        f'<animate attributeName="opacity" values="0;1" '
        f'dur="0.4s" begin="0.05s" fill="freeze"/>'
    )
    title_opacity = "1" if STATIC else "0"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" rx="6" ry="6" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>

<!-- Title bar -->
<rect x="0" y="0" width="{W}" height="{TITLE_H}" rx="6" ry="6" fill="{TITLE_BG}"/>
<rect x="0" y="{TITLE_H - 6}" width="{W}" height="6" fill="{TITLE_BG}"/>
<rect x="0" y="{TITLE_H}" width="{W}" height="1" fill="{BORDER}"/>

<!-- Traffic lights -->
<circle cx="16" cy="19" r="5" fill="#ff5f57"/>
<circle cx="32" cy="19" r="5" fill="#febc2e"/>
<circle cx="48" cy="19" r="5" fill="#28c840"/>

<!-- Title text -->
<text opacity="{title_opacity}" x="{W // 2}" y="24" text-anchor="middle"
  fill="#8b949e" font-family={FONT_MONO} font-size="{FONT_SIZE}">
  {TITLE} — {TAGLINE}{title_anim}
</text>

<!-- Rows -->
{rows_svg}
</svg>'''


def main() -> None:
    svg = build_svg()
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Saved → {OUTPUT}  (STATIC={STATIC})")


if __name__ == "__main__":
    main()
