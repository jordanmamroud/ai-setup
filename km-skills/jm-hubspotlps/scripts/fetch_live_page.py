#!/usr/bin/env python3
"""Fetch a HubSpot/live landing page into hubspot-pulls for audit reference."""

from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in {"script", "style", "noscript"}:
            self._skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript"} and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip:
            text = " ".join(data.split())
            if text:
                self.parts.append(text)

    def text(self) -> str:
        return "\n".join(self.parts)


def slug_from_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    raw = parsed.path.strip("/") or parsed.netloc
    raw = raw.replace("/", "-")
    raw = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip("-")
    return raw[:120] or "page"


def fetch(url: str, timeout: int) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; HubSpotLandingPagesSkill/1.0)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--out-dir", default="hubspot-pulls")
    parser.add_argument("--name", help="Base output filename without extension")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    name = args.name or slug_from_url(args.url)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    base = out_dir / f"{stamp}-{name}"

    try:
        body = fetch(args.url, args.timeout)
    except urllib.error.URLError as exc:
        print(f"fetch failed: {exc}", file=sys.stderr)
        return 1

    html = body.decode("utf-8", errors="replace")
    extractor = TextExtractor()
    extractor.feed(html)

    html_path = base.with_suffix(".html")
    text_path = base.with_suffix(".txt")
    meta_path = base.with_suffix(".meta.txt")

    html_path.write_text(html, encoding="utf-8")
    text_path.write_text(extractor.text() + "\n", encoding="utf-8")
    meta_path.write_text(f"url: {args.url}\nfetched_at: {stamp}\nbytes: {len(body)}\n", encoding="utf-8")

    print(html_path)
    print(text_path)
    print(meta_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
