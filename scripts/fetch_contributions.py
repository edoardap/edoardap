#!/usr/bin/env python3
"""
fetch_contributions.py — Scrape your public GitHub contribution calendar.

No GitHub token required. Fetches the public HTML fragment that GitHub
uses on profile pages and parses the day cells.

Usage:
    python scripts/fetch_contributions.py

Output: data/contributions.json
"""

import json
import re
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "edoardap"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path("data/contributions.json")


def fetch() -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124 Safari/537.36"
        ),
        "Accept": "text/html",
        "X-Requested-With": "XMLHttpRequest",
    }
    resp = requests.get(URL, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    days = []

    for td in soup.select("td[data-date]"):
        date_str = td["data-date"]
        # count attr may be "data-count" or inside a tooltip
        count_attr = td.get("data-count", "0")
        try:
            count = int(count_attr)
        except (ValueError, TypeError):
            # fallback: parse from tooltip text like "3 contributions on …"
            title = td.get("data-tip", "") or td.get("aria-label", "")
            m = re.match(r"(\d+)", title)
            count = int(m.group(1)) if m else 0

        level_attr = td.get("data-level", "0")
        try:
            level = int(level_attr)
        except (ValueError, TypeError):
            level = 0

        days.append({"date": date_str, "count": count, "level": level})

    if not days:
        raise ValueError("No contribution day cells found — HTML structure may have changed.")

    days.sort(key=lambda d: d["date"])

    # Derived stats
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"])

    # Streaks
    today = date.today().isoformat()
    dates_with_contribs = {d["date"] for d in days if d["count"] > 0}

    current_streak = 0
    check = date.today()
    while check.isoformat() in dates_with_contribs:
        current_streak += 1
        check -= timedelta(days=1)

    longest_streak = 0
    run = 0
    prev = None
    for d in days:
        dt = date.fromisoformat(d["date"])
        if prev and (dt - prev).days == 1 and d["count"] > 0:
            run += 1
        elif d["count"] > 0:
            run = 1
        else:
            run = 0
        longest_streak = max(longest_streak, run)
        prev = dt

    # Monthly totals (last 12 months)
    monthly: dict[str, int] = {}
    for d in days:
        ym = d["date"][:7]
        monthly[ym] = monthly.get(ym, 0) + d["count"]

    return {
        "username": USERNAME,
        "fetched": today,
        "total_last_year": total,
        "best_day": best,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "monthly": monthly,
        "days": days,
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"Fetching contributions for @{USERNAME}…")
    html = fetch()
    data = parse(html)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(
        f"Saved → {OUT}  "
        f"({data['total_last_year']:,} contributions, "
        f"streak {data['current_streak']} days)"
    )


if __name__ == "__main__":
    main()
