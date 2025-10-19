#!/usr/bin/env python3
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FAILURES = []


def collect_markdown_files():
    doc_root = ROOT / "docs"
    if not doc_root.exists():
        return []
    return doc_root.rglob("*.md")


def analyze_file(path):
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        FAILURES.append((path, "non-utf8"))
        return

    if "\r" in text:
        FAILURES.append((path, "crlf"))

    if re.search(r"[^\x00-\x7F]", text):
        FAILURES.append((path, "non-ascii"))


def main():
    for md_file in collect_markdown_files():
        analyze_file(md_file)

    if FAILURES:
        for path, reason in FAILURES:
            print(f"FAIL: {path} -> {reason}")
        sys.exit(1)


if __name__ == "__main__":
    main()
