#!/usr/bin/env python3
"""Extract modal / popup / exit-intent and disclaimer / offer-details text from
saved landing-page HTML.

This is the STATIC-MODE counterpart to capture.py's overlay extraction: when you
only have server-sent HTML (web_fetch, no Playwright), run this over the saved
.html files to surface offer text that lives in hidden modals — content the
page's visible body text never shows. In rendered mode you don't need this;
capture.py already writes `overlays` and `disclaimers` into each page's JSON.

Uses only the stdlib HTML parser (it walks the DOM rather than regexing raw
bytes), so it can't hit the regex-complexity limits that break ad-hoc greps on
these pages.

Usage:
  python3 extract_overlays.py <file_or_dir> [<file_or_dir> ...]
  python3 extract_overlays.py            # defaults to *.html in the cwd
"""
import glob
import html
import os
import re
import sys
from html.parser import HTMLParser

# An element is interesting when its id or class contains one of these tokens.
OVERLAY_TOKENS = ("modal", "popup", "exit-intent", "exit_intent", "exitintent", "lightbox")
DISCLAIMER_TOKENS = ("disclaimer", "offer-details", "offer_details", "legal", "fineprint", "fine-print")
SKIP_TAGS = {"script", "style", "template", "noscript", "svg"}
WS = re.compile(r"\s+")


def classify(attrs):
    blob = " ".join(v or "" for k, v in attrs if k in ("id", "class")).lower()
    if any(t in blob for t in OVERLAY_TOKENS):
        return "overlay"
    if any(t in blob for t in DISCLAIMER_TOKENS):
        return "disclaimer"
    return None


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, kind_or_None)
        self.capture_depth = 0   # >0 while inside a captured subtree
        self.current_kind = None
        self.skip_depth = 0
        self.buf = []
        self.found = {"overlay": [], "disclaimer": []}

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        # Don't re-open a capture while already inside one (avoids nested dupes).
        kind = None if self.capture_depth else classify(attrs)
        if kind and not self.skip_depth:
            self.current_kind = kind
            self.capture_depth = 1
            self.buf = []
            self.stack.append((tag, kind))
            return
        if self.capture_depth:
            self.capture_depth += 1
        self.stack.append((tag, None))

    def handle_endtag(self, tag):
        if self.stack:
            self.stack.pop()
        if self.capture_depth:
            self.capture_depth -= 1
            if self.capture_depth == 0 and self.current_kind:
                text = WS.sub(" ", html.unescape("".join(self.buf))).strip()
                if len(text) > 1:
                    self.found[self.current_kind].append(text[:1500])
                self.current_kind = None
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if self.capture_depth and not self.skip_depth:
            self.buf.append(data)


def dedupe(items):
    """Drop exact repeats and fragments fully contained in a kept (longer) item."""
    kept = []
    for it in sorted(items, key=len, reverse=True):
        low = it.lower()
        if any(low in k.lower() for k in kept):
            continue
        kept.append(it)
    # restore first-seen order
    order = {v: i for i, v in enumerate(items)}
    return sorted(kept, key=lambda x: order.get(x, 0))


def html_files(targets):
    if not targets:
        return sorted(glob.glob("*.html"))
    out = []
    for t in targets:
        if os.path.isdir(t):
            out.extend(sorted(glob.glob(os.path.join(t, "*.html"))))
        else:
            out.append(t)
    return out


def main():
    files = html_files(sys.argv[1:])
    if not files:
        print("no .html files found", file=sys.stderr)
        sys.exit(1)
    for path in files:
        slug = os.path.basename(path)
        if slug.endswith(".html"):
            slug = slug[:-5]
        c = Collector()
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                c.feed(fh.read())
        except OSError as e:
            print(f"\n=== {slug} === (read error: {e})")
            continue
        print(f"\n=== {slug} ===")
        for kind in ("overlay", "disclaimer"):
            items = dedupe(c.found[kind])
            print(f"-- {kind} ({len(items)}) --")
            for it in items:
                print(f"  • {it[:600]}")


if __name__ == "__main__":
    main()
