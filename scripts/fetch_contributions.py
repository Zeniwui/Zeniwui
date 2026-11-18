#!/usr/bin/env python3
"""
Fetch public daily contribution counts for a GitHub user without auth/tokens.
Writes data/contributions.json with raw days and derived stats (streaks, best day, monthly totals).
Uses only Python standard library so no pip install is required.
"""
import datetime
import json
import os
import re
import sys
import urllib.request
from html.parser import HTMLParser

USERNAME = os.environ.get("GH_PROFILE_USER", "Zeniwui")
URL = f"https://github.com/users/{USERNAME}/contributions"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "data", "contributions.json")


class _ContribParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}  # id -> {date, level}
        self.tooltips = {}  # for_id -> text
        self._current_for = None

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "td" and "ContributionCalendar-day" in attr.get("class", ""):
            date = attr.get("data-date")
            td_id = attr.get("id")
            if date and td_id:
                self.cells[td_id] = {
                    "date": date,
                    "level": int(attr.get("data-level", "0") or 0),
                }
        elif tag == "tool-tip":
            for_id = attr.get("for")
            if for_id:
                self._current_for = for_id

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self._current_for = None

    def handle_data(self, data):
        if self._current_for:
            self.tooltips[self._current_for] = (
                self.tooltips.get(self._current_for, "") + data
            )


def _parse_count(text: str) -> int:
    if not text:
        return 0
    m = re.search(r"(\d+)\s+contribution", text)
    return int(m.group(1)) if m else 0


def fetch_days():
    req = urllib.request.Request(
        URL, headers={"User-Agent": "zeniwui-profile-bot/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    parser = _ContribParser()
    parser.feed(html)

    if not parser.cells:
        print("No calendar cells found; GitHub markup may have changed.", file=sys.stderr)
        sys.exit(1)

    days = []
    for td_id, info in parser.cells.items():
        count = _parse_count(parser.tooltips.get(td_id, ""))
        days.append(
            {
                "date": info["date"],
                "count": count,
                "level": info["level"],
            }
        )

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"], default={"date": "", "count": 0})

    # Longest streak
    longest = 0
    run = 0
    for d in days:
        if d["count"] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0

    # Current streak (ignoring today if 0 so far)
    current = 0
    today_str = datetime.date.today().isoformat()
    idx = len(days) - 1
    if idx >= 0 and days[idx]["date"] == today_str and days[idx]["count"] == 0:
        idx -= 1
    while idx >= 0 and days[idx]["count"] > 0:
        current += 1
        idx -= 1

    # Monthly totals (last 12 months)
    monthly = {}
    for d in days:
        ym = d["date"][:7]
        monthly[ym] = monthly.get(ym, 0) + d["count"]

    months_sorted = [{"month": k, "count": monthly[k]} for k in sorted(monthly.keys())[-12:]]

    return {
        "username": USERNAME,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "total_contributions": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": months_sorted,
        "days": days,
    }


def main():
    days = fetch_days()
    stats = compute_stats(days)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(
        f"Saved {len(days)} days for {USERNAME}: "
        f"total={stats['total_contributions']}, "
        f"current_streak={stats['current_streak']}, "
        f"longest_streak={stats['longest_streak']}"
    )


if __name__ == "__main__":
    main()
