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
    start = dt.date(year, 1, 1)
    end = dt.date(year, 12, 31)
    dates = [start + dt.timedelta(days=index) for index in range((end - start).days + 1)]

    eligible = [date for date in dates if date.month == date.month]
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
    cell = 12
    gap = 3
    left = 44
    top = 32
    width = left + week_count * (cell + gap) + 12
    height = top + 7 * (cell + gap) + 32

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">Simulated demo contribution calendar for {year}</title>',
        '<desc id="desc">This is independently generated demo artwork and is not a record of real GitHub contributions.</desc>',
        f'<rect width="{width}" height="{height}" rx="8" fill="{ "#0d1117" if theme == "dark" else "#ffffff"}"/>',
        '<text x="44" y="18" fill="' + ("#c9d1d9" if theme == "dark" else "#24292f") + '" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="12" font-weight="600">Demo contribution calendar - not real GitHub activity</text>',
        '<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="9" fill="' + ("#8b949e" if theme == "dark" else "#57606a") + '">',
    ]

    for index, label in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
        month = dt.date(year, index + 1, 1)
        x = left + ((month - first).days // 7) * (cell + gap)
        svg.append(f'<text x="{x}" y="{top - 8}">{label}</text>')
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

    legend_y = height - 16
    legend_x = width - 92
    svg.append(f'<text x="{legend_x - 34}" y="{legend_y + 9}" fill="' + ("#8b949e" if theme == "dark" else "#57606a") + '" font-size="9">Less</text>')
    for level in range(5):
        svg.append(f'<rect x="{legend_x + level * (cell + gap)}" y="{legend_y}" width="{cell}" height="{cell}" rx="2" fill="{colors[level]}"/>')
    svg.append(f'<text x="{legend_x + 5 * (cell + gap) + 4}" y="{legend_y + 9}" fill="' + ("#8b949e" if theme == "dark" else "#57606a") + '" font-size="9">More</text>')
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
