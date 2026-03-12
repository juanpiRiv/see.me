#!/usr/bin/env python3
"""Apply a minimal futurist pro-hacker theme to github-metrics.svg."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SVG_PATH = Path("github-metrics.svg")

# Cyber/minimal palette: near-black, cyan accents, slate text.
# Includes both default lowlighter colors AND previously themed (gold) colors.
COLOR_MAP = {
    "#777": "#94a3b8",
    "#666": "#64748b",
    "#959da5": "#22d3ee",
    "#0366d6": "#22d3ee",
    "#007fff": "#38bdf8",
    "#00ff7f": "#34d399",
    "#7f00ff": "#a78bfa",
    "#a933ff": "#818cf8",
    "#ff7f00": "#fb923c",
    "#ebedf0": "#0f172a",
    "#9be9a8": "#0d9488",
    "#40c463": "#14b8a6",
    "#30a14e": "#2dd4bf",
    "#216e39": "#22d3ee",
    "#ffee4a": "#67e8f9",
    "#ffc501": "#38bdf8",
    "#fe9600": "#fb923c",
    "#03001c": "#020617",
    "#0a3069": "#0f172a",
    "#0969da": "#22d3ee",
    "#54aeff": "#38bdf8",
    "#b6e3ff": "#67e8f9",
    "#24292f": "#22d3ee",
    # Gold theme (so re-theming works on already-themed SVGs)
    "#F2E9D8": "#94a3b8",
    "#F5EDE0": "#94a3b8",
    "#E0B354": "#22d3ee",
    "#C69026": "#22d3ee",
    "#D8C39A": "#64748b",
    "#1F1406": "#0a0e14",
    "#2A1D10": "#0f172a",
    "#6B4A19": "#0d9488",
    "#8A5D1F": "#14b8a6",
    "#B57929": "#2dd4bf",
    "#D6A84A": "#67e8f9",
    "#A6671C": "#fb923c",
    "#140D05": "#020617",
    # Residual gold/rainbow colors from lowlighter animations
    "#B57C1F": "#0ea5e9",
    "#E8B866": "#67e8f9",
    "#D39A2E": "#38bdf8",
}

TEXT_MAP = {
    "rgba(27,31,35,.04)": "rgba(34,211,238,.06)",
    "rgba(27,31,35,.06)": "rgba(34,211,238,.1)",
    "rgba(198,144,38,.16)": "rgba(34,211,238,.1)",
    "rgba(198,144,38,.22)": "rgba(34,211,238,.12)",
}

# Match the root svg{...} block only (not "h1 svg,h2 svg{...}"). Root block has font-family.
SVG_STYLE_PATTERN = re.compile(r"svg\{font-family:[^}]+\}")
SVG_STYLE_REPLACEMENT = (
    "svg{font-family:ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Monaco,monospace;"
    "font-size:13px;color:#94a3b8;letter-spacing:.02em;"
    "background:#0a0e14;"
    "border-radius:8px;"
    "border:1px solid rgba(34,211,238,.12);"
    "box-shadow:0 0 0 1px rgba(34,211,238,.04),inset 0 1px 0 rgba(255,255,255,.02)}"
)

# Regex overrides for typography (match default or previously themed output).
H1_H2_PATTERN = re.compile(
    r"h1,h2\{margin:8px 0 2px;padding:0;color:#[0-9a-fA-F]+;font-size:\d+px;font-weight:\d+\}h2\{font-weight:\d+;font-size:\d+px\}",
)
H1_H2_REPLACEMENT = "h1,h2{margin:8px 0 2px;padding:0;color:#22d3ee;font-size:18px;font-weight:600;letter-spacing:.05em}h2{font-weight:500;font-size:15px}"
FIELD_SVG_PATTERN = re.compile(
    r"\.field svg\{margin:0 8px;fill:#[0-9a-fA-F]+;flex-shrink:0[^}]*\}",
)
FIELD_SVG_REPLACEMENT = ".field svg{margin:0 8px;fill:#22d3ee;flex-shrink:0;opacity:.85}"

FOOTER_PATTERN = re.compile(r"footer\{[^}]+\}")
FOOTER_REPLACEMENT = (
    "footer{margin-top:4px;font-size:9px;font-style:normal;"
    "color:#334155;text-align:right;display:flex;flex-direction:column;"
    "justify-content:flex-end;padding:0 4px;opacity:.7}"
)

FIELD_PATTERN = re.compile(r"\.field\{display:flex;align-items:center;margin-bottom:\d+px;white-space:nowrap\}")
FIELD_REPLACEMENT = ".field{display:flex;align-items:center;margin-bottom:3px;white-space:nowrap}"

CALENDAR_DAY_PATTERN = re.compile(r"\.calendar \.day\{outline:[^}]+\}")
CALENDAR_DAY_REPLACEMENT = ".calendar .day{outline:1px solid rgba(34,211,238,.08);outline-offset:-1px}"

RAINBOW_PATTERN = re.compile(r"@keyframes animation-rainbow\{[^}]+(?:\}[^}]*)*?\}\}")
RAINBOW_REPLACEMENT = (
    "@keyframes animation-rainbow{"
    "0%,to{color:#0d9488;fill:#0d9488}"
    "14%{color:#14b8a6;fill:#14b8a6}"
    "29%{color:#2dd4bf;fill:#2dd4bf}"
    "43%{color:#22d3ee;fill:#22d3ee}"
    "57%{color:#38bdf8;fill:#38bdf8}"
    "71%{color:#67e8f9;fill:#67e8f9}"
    "86%{color:#0ea5e9;fill:#0ea5e9}}"
)

# Add 10% height so footer and bottom content aren't clipped.
HEIGHT_PATTERN = re.compile(r'(<svg xmlns="[^"]+" width="\d+" )height="(\d+)"')


def _add_height_margin(m: re.Match) -> str:
    original_h = int(m.group(2))
    new_h = int(original_h * 1.10)
    return f'{m.group(1)}height="{new_h}"'

# Hide fields showing "0 ..." (e.g. "0 Issues opened").
# Uses negative lookahead (?!</svg>) so the match stays within a single <svg>...</svg>.
ZERO_FIELD_PATTERN = re.compile(
    r'<div class="field">\s*<svg[^>]*>(?:(?!</svg>).)*</svg>\s*0\s[^<]+</div>',
    re.DOTALL,
)


def apply_theme(svg_text: str) -> str:
    themed = svg_text

    # Replace rainbow animation with cyber palette before color map runs
    themed = RAINBOW_PATTERN.sub(RAINBOW_REPLACEMENT, themed)

    # Apply minimal cyber/hacker base styles (regex works on any svg block).
    themed = SVG_STYLE_PATTERN.sub(SVG_STYLE_REPLACEMENT, themed)

    for source, target in TEXT_MAP.items():
        themed = themed.replace(source, target)

    color_map_lower = {k.lower(): v for k, v in COLOR_MAP.items()}
    pattern = re.compile(
        "|".join(re.escape(color) for color in sorted(COLOR_MAP, key=len, reverse=True)),
        flags=re.IGNORECASE,
    )
    themed = pattern.sub(lambda m: color_map_lower[m.group(0).lower()], themed)

    # Hide zero-value metrics for a cleaner card
    themed = ZERO_FIELD_PATTERN.sub("", themed)

    # Typography and layout overrides for hacker aesthetic
    themed = H1_H2_PATTERN.sub(H1_H2_REPLACEMENT, themed)
    themed = FIELD_SVG_PATTERN.sub(FIELD_SVG_REPLACEMENT, themed)
    themed = FOOTER_PATTERN.sub(FOOTER_REPLACEMENT, themed)
    themed = FIELD_PATTERN.sub(FIELD_REPLACEMENT, themed)
    themed = CALENDAR_DAY_PATTERN.sub(CALENDAR_DAY_REPLACEMENT, themed)

    # Expand height by 10% so footer isn't clipped
    themed = HEIGHT_PATTERN.sub(_add_height_margin, themed)

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
    print("Applied minimal futurist pro-hacker theme to github-metrics.svg.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

