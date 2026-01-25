#!/usr/bin/env python3
"""
Sync fun.json from Google Sheets.

Usage: python3 sync-from-sheets.py
"""

import csv
import json
import subprocess
import io

SHEET_ID = "14BDuaq-ZlgN29Av2uRN2V0HYev26L3Duk4cheru2WL4"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
OUTPUT_FILE = "data/fun.json"


def fetch_csv():
    """Fetch CSV data from Google Sheets using curl."""
    result = subprocess.run(
        ["curl", "-s", "-L", CSV_URL],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"curl failed: {result.stderr}")
    return result.stdout


def csv_to_json(csv_text):
    """Convert CSV text to the fun.json format."""
    entries = []
    reader = csv.DictReader(io.StringIO(csv_text))

    for row in reader:
        # Skip empty rows
        if not row.get('url', '').strip():
            continue

        # Parse authors (semicolon-separated)
        author_names = row.get('authorName', '').split(';')
        author_urls = row.get('authorUrl', '').split(';')

        authors = []
        for i, name in enumerate(author_names):
            name = name.strip()
            if not name:
                continue
            author = {"authorName": name}
            if i < len(author_urls) and author_urls[i].strip():
                author["authorUrl"] = author_urls[i].strip()
            authors.append(author)

        entry = {
            "url": row.get('url', '').strip(),
            "title": row.get('title', '').strip(),
            "summary": row.get('summary', '').strip(),
            "datePublished": row.get('datePublished', '').strip(),
            "dateAdded": row.get('dateAdded', '').strip(),
            "authors": authors
        }
        entries.append(entry)

    return entries


def main():
    print(f"Fetching from Google Sheets...")
    csv_text = fetch_csv()

    entries = csv_to_json(csv_text)
    print(f"Parsed {len(entries)} entries")

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(entries, f, indent=2)

    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
