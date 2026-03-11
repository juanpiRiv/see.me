#!/usr/bin/env python3
"""Apply a dark-gold visual theme to github-metrics.svg."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SVG_PATH = Path("github-metrics.svg")

# Dark-gold palette tuned for readability in GitHub profile cards.
COLOR_MAP = {
    "#777": "#F2E9D8",
    "#666": "#D8C39A",
    "#959da5": "#C69026",
    "#0366d6": "#E0B354",
    "#007fff": "#E8B866",
    "#00ff7f": "#D39A2E",
    "#7f00ff": "#B57C1F",
    "#a933ff": "#C69026",
    "#ff7f00": "#A6671C",
    "#ebedf0": "#2A1D10",
    "#9be9a8": "#6B4A19",
    "#40c463": "#8A5D1F",
    "#30a14e": "#B57929",
    "#216e39": "#E0B354",
    "#ffee4a": "#D6A84A",
    "#ffc501": "#C69026",
    "#fe9600": "#A6671C",
    "#03001c": "#140D05",
    "#0a3069": "#6B4A19",
    "#0969da": "#8A5D1F",
    "#54aeff": "#B57929",
    "#b6e3ff": "#E0B354",
}

TEXT_MAP = {
    "rgba(27,31,35,.04)": "rgba(198,144,38,.16)",
    "rgba(27,31,35,.06)": "rgba(198,144,38,.22)",
}

SVG_STYLE_NEEDLE = (
    "svg{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif,"
    "Apple Color Emoji,Segoe UI Emoji;font-size:14px;color:#777}"
)
SVG_STYLE_REPLACEMENT = (
    "svg{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif,"
    "Apple Color Emoji,Segoe UI Emoji;font-size:14px;color:#F2E9D8;"
    "background:#1F1406;border-radius:12px}"
)


def apply_theme(svg_text: str) -> str:
    themed = svg_text

    # Give the card an intentional dark canvas to support warm light text.
    themed = themed.replace(SVG_STYLE_NEEDLE, SVG_STYLE_REPLACEMENT)

    for source, target in TEXT_MAP.items():
        themed = themed.replace(source, target)

    pattern = re.compile(
        "|".join(re.escape(color) for color in sorted(COLOR_MAP, key=len, reverse=True)),
        flags=re.IGNORECASE,
    )
    themed = pattern.sub(lambda m: COLOR_MAP[m.group(0).lower()], themed)

    return themed


def main() -> int:
    if not SVG_PATH.exists():
        print(f"{SVG_PATH} not found. Skipping theme step.")
        return 0

    original = SVG_PATH.read_text(encoding="utf-8")
    themed = apply_theme(original)

    if themed == original:
        print("No theme changes needed.")
        return 0

    SVG_PATH.write_text(themed, encoding="utf-8")
    print("Applied dark-gold theme to github-metrics.svg.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

