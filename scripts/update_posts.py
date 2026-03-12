#!/usr/bin/env python3
"""Update the Latest Blog Posts block inside README.md from an RSS feed."""

from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path


README_PATH = Path("README.md")
START_MARKER = "<!-- BLOG-POST-LIST:START -->"
END_MARKER = "<!-- BLOG-POST-LIST:END -->"
DEFAULT_MAX_POSTS = 5


def _parse_max_posts(value: str | None) -> int:
    if value is None or not value.strip():
        return DEFAULT_MAX_POSTS
    try:
        parsed = int(value)
        return parsed if parsed > 0 else DEFAULT_MAX_POSTS
    except ValueError:
        return DEFAULT_MAX_POSTS


def _clean_title(title: str) -> str:
    # Keep markdown list stable and avoid accidental formatting issues.
    clean = html.unescape(title or "").strip()
    clean = re.sub(r"\s+", " ", clean)
    clean = clean.replace("[", r"\[").replace("]", r"\]")
    return clean or "Untitled post"


def _build_post_lines(feed_url: str, max_posts: int) -> list[str]:
    if not feed_url:
        return ["- RSS feed not configured yet."]

    try:
        import feedparser  # pylint: disable=import-outside-toplevel
    except Exception:
        return ["- RSS reader dependency is missing in this environment."]

    try:
        parsed = feedparser.parse(feed_url)
    except Exception:
        return ["- RSS feed could not be loaded right now."]

    if getattr(parsed, "bozo", False) and not getattr(parsed, "entries", []):
        return ["- RSS feed could not be loaded right now."]

    entries = getattr(parsed, "entries", [])[:max_posts]
    if not entries:
        return ["- No posts found in the RSS feed yet."]

    lines: list[str] = []
    for entry in entries:
        title = _clean_title(getattr(entry, "title", "Untitled post"))
        link = (getattr(entry, "link", "") or "").strip()
        if not link:
            continue
        lines.append(f"- [{title}]({link})")

    if not lines:
        return ["- No valid post links found in the RSS feed."]

    return lines


def _replace_block(readme_text: str, lines: list[str]) -> str:
    if START_MARKER not in readme_text or END_MARKER not in readme_text:
        raise ValueError("README markers were not found.")

    pattern = re.compile(
        rf"({re.escape(START_MARKER)}\n)(.*?)(\n{re.escape(END_MARKER)})",
        re.DOTALL,
    )
    replacement = r"\1" + "\n".join(lines) + r"\3"
    updated, count = pattern.subn(replacement, readme_text, count=1)
    if count != 1:
        raise ValueError("README markers could not be replaced.")
    return updated


def main() -> int:
    if not README_PATH.exists():
        print("README.md not found.", file=sys.stderr)
        return 1

    feed_url = os.getenv("FEED_URL", "").strip()
    max_posts = _parse_max_posts(os.getenv("MAX_POSTS"))

    readme = README_PATH.read_text(encoding="utf-8")
    lines = _build_post_lines(feed_url=feed_url, max_posts=max_posts)

    try:
        updated = _replace_block(readme, lines)
    except ValueError as exc:
        print(f"Skipping: {exc}")
        return 0

    if updated != readme:
        README_PATH.write_text(updated, encoding="utf-8")
        print("README updated.")
    else:
        print("No README changes needed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
