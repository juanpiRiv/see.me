#!/usr/bin/env python3
"""Apply a minimal futurist pro-hacker theme to github-metrics.svg."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SVG_PATH = Path("github-metrics.svg")

# Cyber/minimal palette: near-black, cyan accents, slate text.
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
}

TEXT_MAP = {
    "rgba(27,31,35,.04)": "rgba(34,211,238,.06)",
    "rgba(27,31,35,.06)": "rgba(34,211,238,.1)",
}

SVG_STYLE_NEEDLE = (
    "svg{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif,"
    "Apple Color Emoji,Segoe UI Emoji;font-size:14px;color:#777}"
)
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
    r"\.field svg\{margin:0 8px;fill:#[0-9a-fA-F]+;flex-shrink:0\}",
)
FIELD_SVG_REPLACEMENT = ".field svg{margin:0 8px;fill:#22d3ee;flex-shrink:0;opacity:.9}"


# Remove activity fields that show "0 X" (e.g. "0 Issues opened")
ZERO_FIELD_PATTERN = re.compile(
    r'<div class="field">\s*<svg[\s\S]*?</svg>\s*0 [^<]+</div>',
    re.DOTALL,
)


def apply_theme(svg_text: str) -> str:
    themed = svg_text

    # Apply minimal cyber/hacker base styles.
    themed = themed.replace(SVG_STYLE_NEEDLE, SVG_STYLE_REPLACEMENT)

    for source, target in TEXT_MAP.items():
        themed = themed.replace(source, target)

    pattern = re.compile(
        "|".join(re.escape(color) for color in sorted(COLOR_MAP, key=len, reverse=True)),
        flags=re.IGNORECASE,
    )
    themed = pattern.sub(lambda m: COLOR_MAP[m.group(0).lower()], themed)

    # Hide metrics with zero value for a cleaner look
    themed = ZERO_FIELD_PATTERN.sub("", themed)

    # Typography overrides for hacker aesthetic
    themed = H1_H2_PATTERN.sub(H1_H2_REPLACEMENT, themed)
    themed = FIELD_SVG_PATTERN.sub(FIELD_SVG_REPLACEMENT, themed)

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

