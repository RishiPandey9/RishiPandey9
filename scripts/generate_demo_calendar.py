#!/usr/bin/env python3

import datetime as dt
import json
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "assets" / "demo-contribution-calendar.json"
OUTPUT_DIR = ROOT / "assets"

LIGHT_COLORS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
DARK_COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def svg_escape(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate(config, colors, theme):
    year = int(config["year"])
    square_count = int(config["squareCount"])
    intensity = [int(level) for level in config.get("intensity", [0, 1, 2, 3, 4])]
    seed = int(config.get("seed", year))
    date_levels = {
        str(date): int(level)
        for date, level in config.get("dateLevels", {}).items()
    }

    rng = random.Random(seed)
    start = dt.date.fromisoformat(config.get("startDate", f"{year}-01-01"))
    end = dt.date.fromisoformat(config.get("endDate", f"{year}-12-31"))
    dates = [start + dt.timedelta(days=index) for index in range((end - start).days + 1)]

    eligible = list(dates)
    rng.shuffle(eligible)
    selected = set(eligible[:square_count])
    levels = {}
    for date in dates:
        key = date.isoformat()
        if key in date_levels:
            levels[key] = max(1, min(4, date_levels[key]))
        elif date in selected:
            weighted = min(intensity) if 1 not in intensity else rng.choices(intensity[1:] or [1], weights=[4, 3, 2, 1][:len(intensity[1:] or [1])])[0]
            levels[key] = max(1, min(4, weighted))
        else:
            levels[key] = 0

    first = start - dt.timedelta(days=start.weekday())
    last = end
    week_count = ((last - first).days // 7) + 1
    cell = 10
    gap = 3
    left = 44
    top = 96
    width = 760
    height = 250
    panel_dark = "#0d1117"
    panel_light = "#ffffff"
    border_dark = "#30363d"
    border_light = "#d0d7de"
    text_dark = "#c9d1d9"
    text_light = "#24292f"
    muted_dark = "#8b949e"
    muted_light = "#57606a"

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">Simulated demo contribution calendar for {start.isoformat()} through {end.isoformat()}</title>',
        '<desc id="desc">This is independently generated demo artwork and is not a record of real GitHub contributions.</desc>',
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="8" fill="{panel_dark if theme == "dark" else panel_light}" stroke="{border_dark if theme == "dark" else border_light}"/>',
        f'<text x="16" y="28" fill="{text_dark if theme == "dark" else text_light}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="14" font-weight="600">{square_count} simulated contributions</text>',
        f'<text x="16" y="48" fill="{muted_dark if theme == "dark" else muted_light}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="10">DEMO ONLY - independently generated visual, not real GitHub activity</text>',
        f'<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="9" fill="{muted_dark if theme == "dark" else muted_light}">',
    ]

    month_labels = []
    cursor_month = dt.date(start.year, start.month, 1)
    while cursor_month <= end:
        next_month = dt.date(cursor_month.year + 1, 1, 1) if cursor_month.month == 12 else dt.date(cursor_month.year, cursor_month.month + 1, 1)
        month_start = max(cursor_month, start)
        week_index = (month_start - first).days // 7
        x = left + week_index * (cell + gap)
        month_labels.append((x, cursor_month.strftime("%b")))
        cursor_month = next_month
    for x, label in month_labels:
        svg.append(f'<text x="{x}" y="{top - 12}">{label}</text>')

    for row, label in enumerate(["Mon", "", "Wed", "", "Fri", "", ""]):
        if label:
            svg.append(f'<text x="8" y="{top + row * (cell + gap) + 10}">{label}</text>')

    week = 0
    cursor = first
    while cursor <= last:
        row = cursor.weekday()
        if cursor.year == year:
            level = levels.get(cursor.isoformat(), 0)
            x = left + week * (cell + gap)
            y = top + row * (cell + gap)
            svg.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
                f'fill="{colors[level]}" stroke="{ "#30363d" if theme == "dark" else "#d0d7de"}" '
                f'stroke-width="0.5"><title>{svg_escape(cursor.isoformat())}: demo level {level}</title></rect>'
            )
        cursor += dt.timedelta(days=1)
        if cursor.weekday() == 0:
            week += 1

    legend_y = height - 26
    legend_x = width - 112
    svg.append(f'<text x="{legend_x - 30}" y="{legend_y + 9}" fill="{muted_dark if theme == "dark" else muted_light}" font-size="9">Less</text>')
    for level in range(5):
        svg.append(f'<rect x="{legend_x + level * (cell + gap)}" y="{legend_y}" width="{cell}" height="{cell}" rx="2" fill="{colors[level]}"/>')
    svg.append(f'<text x="{legend_x + 5 * (cell + gap) + 4}" y="{legend_y + 9}" fill="{muted_dark if theme == "dark" else muted_light}" font-size="9">More</text>')
    svg.append("</g></svg>")
    return "\n".join(svg) + "\n"


def main():
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else CONFIG_PATH
    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    (OUTPUT_DIR / "demo-contribution-calendar-light.svg").write_text(
        generate(config, LIGHT_COLORS, "light"), encoding="utf-8"
    )
    (OUTPUT_DIR / "demo-contribution-calendar-dark.svg").write_text(
        generate(config, DARK_COLORS, "dark"), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
