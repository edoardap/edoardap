#!/usr/bin/env python3
"""
render_heatmap_svg.py — Render data/contributions.json as an animated SVG heatmap.

Usage:
    python scripts/render_heatmap_svg.py

Input:  data/contributions.json
Output: contrib-heatmap.svg

Animation: boxes slide in diagonally (CSS keyframes), play once and freeze.
"""

import json
import math
from pathlib import Path

IN = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")

# --------------------------------------------------------------------------- #
# Palette  (level 0→5)
# --------------------------------------------------------------------------- #
PALETTE = [
    "#161b22",  # 0 — empty
    "#0e4429",  # 1
    "#006d32",  # 2
    "#26a641",  # 3
    "#39d353",  # 4
    "#69f0a0",  # 5 — neon top end
]

# --------------------------------------------------------------------------- #
# Layout
# --------------------------------------------------------------------------- #
BOX = 11        # px per box
GAP = 2         # gap between boxes
CELL = BOX + GAP
PAD_LEFT = 28   # space for month labels
PAD_TOP = 24    # space for month labels
PAD_BOTTOM = 46 # space for legend + footer
CORNER = 2      # border-radius of each box
ANIM_DUR = 0.25 # box slide-in duration (s)
DIAG_STEP = 0.02 # diagonal stagger per (col+row)


def build_svg(data: dict) -> str:
    days = data["days"]
    total = data["total_last_year"]
    streak = data["current_streak"]
    longest = data["longest_streak"]
    best = data["best_day"]

    # --- Group days into ISO weeks (Mon start) ----------------------------- #
    from datetime import date, timedelta

    # Find start: Sunday of the first week that contains days[0]
    first_date = date.fromisoformat(days[0]["date"])
    # Align to Sunday
    start = first_date - timedelta(days=(first_date.weekday() + 1) % 7)

    last_date = date.fromisoformat(days[-1]["date"])
    # Build week → day dict
    day_map = {d["date"]: d for d in days}

    weeks = []
    cur = start
    while cur <= last_date + timedelta(days=6):
        week_days = []
        for _ in range(7):
            ds = cur.isoformat()
            if ds in day_map:
                week_days.append(day_map[ds])
            else:
                week_days.append({"date": ds, "count": 0, "level": 0})
            cur += timedelta(days=1)
        weeks.append(week_days)

    n_weeks = len(weeks)
    svg_w = PAD_LEFT + n_weeks * CELL + 4
    svg_h = PAD_TOP + 7 * CELL + PAD_BOTTOM

    # --- Collect month label positions ------------------------------------- #
    month_labels = []
    prev_month = None
    for wi, week in enumerate(weeks):
        # Use the first real day of the week
        for d in week:
            if d["count"] >= 0:
                m = d["date"][5:7]
                break
        if m != prev_month:
            month_labels.append((wi, d["date"][:7]))
            prev_month = m

    MONTHS = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
        "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
        "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
    }

    parts = []

    # Background
    parts.append(
        f'<rect width="{svg_w}" height="{svg_h}" fill="#0d1117" rx="8" ry="8"/>'
    )

    # Month labels
    for wi, ym in month_labels:
        x = PAD_LEFT + wi * CELL
        mo = ym[5:7]
        parts.append(
            f'<text x="{x}" y="{PAD_TOP - 6}" fill="#8b949e" '
            f'font-family="\'Courier New\', monospace" font-size="10">'
            f'{MONTHS.get(mo, mo)}</text>'
        )

    # Day-of-week labels
    DOW = ["", "Mon", "", "Wed", "", "Fri", ""]
    for di, label in enumerate(DOW):
        if label:
            y = PAD_TOP + (di + 0.75) * CELL
            parts.append(
                f'<text x="{PAD_LEFT - 4}" y="{y}" fill="#8b949e" '
                f'font-family="\'Courier New\', monospace" font-size="9" '
                f'text-anchor="end">{label}</text>'
            )

    # CSS keyframe animation
    parts.insert(1, """<defs>
  <style>
    .box {
      animation: slide-in var(--dur) var(--delay) both;
    }
    @keyframes slide-in {
      from { opacity: 0; transform: translate(-4px, -4px); }
      to   { opacity: 1; transform: translate(0, 0); }
    }
  </style>
</defs>""")

    # Boxes
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            level = min(day["level"], len(PALETTE) - 1)
            color = PALETTE[level]
            x = PAD_LEFT + wi * CELL
            y = PAD_TOP + di * CELL
            delay = (wi + di) * DIAG_STEP
            tooltip = f'{day["count"]} contributions on {day["date"]}'
            parts.append(
                f'<rect class="box" x="{x}" y="{y}" width="{BOX}" height="{BOX}" '
                f'rx="{CORNER}" ry="{CORNER}" fill="{color}" '
                f'style="--dur:{ANIM_DUR}s;--delay:{delay:.3f}s">'
                f'<title>{tooltip}</title></rect>'
            )

    # Legend
    legend_y = svg_h - 26
    parts.append(
        f'<text x="{PAD_LEFT}" y="{legend_y}" fill="#8b949e" '
        f'font-family="\'Courier New\', monospace" font-size="10">Less</text>'
    )
    lx = PAD_LEFT + 30
    for lvl in range(len(PALETTE)):
        parts.append(
            f'<rect x="{lx + lvl * (BOX + 2)}" y="{legend_y - BOX}" '
            f'width="{BOX}" height="{BOX}" rx="{CORNER}" ry="{CORNER}" fill="{PALETTE[lvl]}"/>'
        )
    parts.append(
        f'<text x="{lx + len(PALETTE) * (BOX + 2) + 4}" y="{legend_y}" fill="#8b949e" '
        f'font-family="\'Courier New\', monospace" font-size="10">More</text>'
    )

    # Footer stats
    footer_y = svg_h - 8
    best_date = best["date"] if best else "—"
    best_count = best["count"] if best else 0
    stats_text = (
        f'{total:,} contributions · '
        f'streak {streak}d (longest {longest}d) · '
        f'best day: {best_count} on {best_date}'
    )
    parts.append(
        f'<text x="{svg_w // 2}" y="{footer_y}" text-anchor="middle" '
        f'fill="#484f58" font-family="\'Courier New\', monospace" font-size="10">'
        f'{stats_text}</text>'
    )

    inner = "\n".join(parts)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_w}" height="{svg_h}" '
        f'viewBox="0 0 {svg_w} {svg_h}">\n'
        f'{inner}\n'
        f'</svg>'
    )


def main() -> None:
    if not IN.exists():
        raise FileNotFoundError(f"{IN} not found — run fetch_contributions.py first.")
    data = json.loads(IN.read_text())
    svg = build_svg(data)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Saved → {OUT}")


if __name__ == "__main__":
    main()
