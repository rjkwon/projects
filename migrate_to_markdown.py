#!/usr/bin/env python3
"""
One-time migration: convert data/fun.json into one markdown leaf bundle
per entry, written into the kwon.nyc content tree.

Usage: python3 migrate_to_markdown.py [--dry-run]
"""

import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

SOURCE_FILE = Path(__file__).resolve().parent / "data" / "fun.json"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "kwon.nyc" / "content" / "internet"
SLUG_MAX_LEN = 60
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def slugify(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    if len(slug) > SLUG_MAX_LEN:
        slug = slug[:SLUG_MAX_LEN].rsplit("-", 1)[0]
    return slug or "untitled"


def unique_slug(base: str, taken: Counter) -> str:
    taken[base] += 1
    if taken[base] == 1:
        return base
    return f"{base}-{taken[base]}"


def yaml_str(value: str) -> str:
    """A JSON-quoted string is also a valid YAML double-quoted scalar."""
    return json.dumps(value, ensure_ascii=False)


def build_frontmatter(entry: dict) -> str:
    lines = ["---"]
    lines.append(f"title: {yaml_str(entry['title'])}")
    # NB: "url" is a reserved Hugo front matter field (overrides the page's own
    # permalink) -> use "link" for the external article URL to avoid colliding with it
    lines.append(f"link: {yaml_str(entry['url'])}")
    # dateAdded is always a real ISO date -> used for Hugo's .Date/sorting
    lines.append(f"date: {entry['dateAdded']}")
    # datePublished is 'unknown' in the source under two different spellings
    # ('--' and 'unknown') -> omit the field entirely rather than carry a sentinel
    if DATE_RE.match(entry["datePublished"]):
        lines.append(f"datePublished: {entry['datePublished']}")

    authors = entry.get("authors") or []
    if authors:
        lines.append("authors:")
        for author in authors:
            name = author.get("authorName", "")
            url = author.get("authorUrl", "")
            lines.append(f"  - name: {yaml_str(name)}")
            if url:
                lines.append(f"    url: {yaml_str(url)}")
    else:
        lines.append("authors: []")

    lines.append("---")
    return "\n".join(lines)


def build_body(entry: dict) -> str:
    summary = entry.get("summary", "").strip()
    return f"\n{summary}\n" if summary else "\n"


def main():
    dry_run = "--dry-run" in sys.argv

    with open(SOURCE_FILE) as f:
        entries = json.load(f)

    print(f"Loaded {len(entries)} entries from {SOURCE_FILE}")

    url_counts = Counter(e["url"] for e in entries)
    dupes = [url for url, count in url_counts.items() if count > 1]
    if dupes:
        print(f"\nWARNING: {len(dupes)} URL(s) appear more than once in the source data:")
        for url in dupes:
            print(f"  - {url}")
        print("These will each get their own markdown file (not deduped). Review before/after.\n")

    taken_slugs = Counter()
    written = []

    for entry in entries:
        slug = unique_slug(slugify(entry["title"]), taken_slugs)
        entry_file = OUTPUT_DIR / f"{slug}.md"

        content = build_frontmatter(entry) + build_body(entry)

        written.append(entry_file)

        if dry_run:
            continue

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(entry_file, "w", encoding="utf-8") as f:
            f.write(content)

    verb = "Would write" if dry_run else "Wrote"
    print(f"{verb} {len(written)} files under {OUTPUT_DIR}")

    if dry_run and written:
        print("\nSample (first entry):\n")
        print(build_frontmatter(entries[0]) + build_body(entries[0]))


if __name__ == "__main__":
    main()
