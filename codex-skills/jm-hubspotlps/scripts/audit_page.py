#!/usr/bin/env python3
"""Audit a live/preview HubSpot page against an optional local template."""

from __future__ import annotations

import argparse
import html
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}")
TEL_RE = re.compile(r"tel:([+0-9][+0-9().\-\s]*)", re.I)
OFFER_RE = re.compile(r"\b\d{1,2}%\s+Off\s+Installation\b", re.I)
FORM_RE = re.compile(r"(?:form_id|form-id|data-form-id)\s*[=:]\s*[\"']?([A-Za-z0-9_-]{8,})", re.I)
PORTAL_RE = re.compile(
    r"(?:form_portal_id|form-portal-id|portal_id|portal-id|data-form-portal-id|data-portal(?:-id)?)\s*[=:]\s*[\"']?([A-Za-z0-9_-]{3,})",
    re.I,
)
MODULE_RE = re.compile(r"\{%\s+module\s+\"([^\"]+)\"", re.I)
H_RE = re.compile(r"<h([1-3])[^>]*>(.*?)</h\1>", re.I | re.S)


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


def fetch_url(url: str, timeout: int) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; HubSpotLandingPagesSkill/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def visible_text(markup: str) -> str:
    parser = TextExtractor()
    parser.feed(markup)
    return parser.text()


def strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return " ".join(html.unescape(value).split())


def sorted_unique(pattern: re.Pattern[str], text: str) -> list[str]:
    values = set()
    for match in pattern.finditer(text):
        groups = [group for group in match.groups() if group is not None]
        values.add(groups[0] if groups else match.group(0))
    return sorted(values)


def normalized_offer(value: str) -> str:
    return " ".join(value.casefold().split())


def normalized_offers(values: list[str]) -> set[str]:
    return {normalized_offer(value) for value in values}


def headings(markup: str) -> list[str]:
    return [f"h{level}: {strip_tags(body)}" for level, body in H_RE.findall(markup)]


def template_strings(markup: str) -> str:
    # Keep quoted HubL values visible for simple token scans.
    values = re.findall(r"[A-Za-z0-9_]+\s*=\s*\"([^\"]*)\"|\"(?:item_text|answer|question|quote|heading|body_text|cta_text|headline)\"\s*:\s*\"([^\"]*)\"", markup)
    flattened = [a or b for a, b in values]
    return "\n".join(html.unescape(v) for v in flattened)


def emit_section(lines: list[str], title: str, items: list[str]) -> None:
    lines.append(f"## {title}")
    if items:
        lines.extend(f"- `{item}`" for item in items)
    else:
        lines.append("- None found")
    lines.append("")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Live or HubSpot preview URL")
    parser.add_argument("--html-file", help="Previously fetched HTML file")
    parser.add_argument("--template", help="Local template to compare")
    parser.add_argument("--out", help="Markdown report path, default audits/<timestamp>-audit.md")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    if not args.url and not args.html_file:
        parser.error("provide --url or --html-file")

    source = args.url or args.html_file or ""
    if args.url:
        try:
            live_html = fetch_url(args.url, args.timeout)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            print(f"fetch failed: {exc}", file=sys.stderr)
            return 1
    else:
        try:
            live_html = Path(args.html_file).read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"read failed: {exc}", file=sys.stderr)
            return 1

    live_text = visible_text(live_html)
    if args.template:
        try:
            template_raw = Path(args.template).read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"template read failed: {exc}", file=sys.stderr)
            return 1
    else:
        template_raw = ""
    template_text = template_strings(template_raw) if template_raw else ""

    live_phones = sorted_unique(PHONE_RE, live_text)
    live_tels = sorted_unique(TEL_RE, live_html)
    live_offers = sorted_unique(OFFER_RE, live_text)
    live_forms = sorted_unique(FORM_RE, live_html)
    live_portals = sorted_unique(PORTAL_RE, live_html)

    template_phones = sorted_unique(PHONE_RE, template_text)
    template_offers = sorted_unique(OFFER_RE, template_text)
    template_forms = sorted_unique(FORM_RE, template_raw)
    template_portals = sorted_unique(PORTAL_RE, template_raw)
    template_modules = sorted_unique(MODULE_RE, template_raw)

    findings: list[str] = []
    if live_phones and len(live_phones) > 1:
        findings.append(f"HIGH: multiple visible live phone numbers: {', '.join(live_phones)}")
    normalized_phone_digits = {re.sub(r"\D", "", p)[-10:] for p in live_phones}
    normalized_tel_digits = {re.sub(r"\D", "", t)[-10:] for t in live_tels}
    if normalized_phone_digits and normalized_tel_digits and normalized_phone_digits != normalized_tel_digits:
        findings.append("HIGH: live visible phone numbers and tel links differ")
    if len(normalized_offers(live_offers)) > 1:
        findings.append(f"HIGH: multiple live offer values: {', '.join(live_offers)}")
    if template_raw and normalized_offers(live_offers) != normalized_offers(template_offers):
        findings.append(f"HIGH: live/template offer mismatch: live={live_offers or ['none']} template={template_offers or ['none']}")
    if template_raw and set(template_forms) and set(live_forms) and set(template_forms) != set(live_forms):
        findings.append(f"HIGH: live/template form ID mismatch: live={live_forms} template={template_forms}")
    if template_raw and set(template_portals) and set(live_portals) and set(template_portals) != set(live_portals):
        findings.append(f"HIGH: live/template portal ID mismatch: live={live_portals} template={template_portals}")
    for token in ("TODO", "FIXME", "lorem", "{loc}"):
        if token.lower() in live_text.lower():
            findings.append(f"MED: live page contains `{token}`")

    now = time.strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = [
        "# HubSpot Landing Page Audit",
        "",
        f"- Source: {source}",
        f"- Template: {args.template or 'not provided'}",
        f"- Generated: {now}",
        "",
        "## Findings",
    ]
    if findings:
        lines.extend(f"- {item}" for item in findings)
    else:
        lines.append("- No automated high-signal findings.")
    lines.append("")

    emit_section(lines, "Live Headings", headings(live_html)[:30])
    emit_section(lines, "Live Offers", live_offers)
    emit_section(lines, "Template Offers", template_offers)
    emit_section(lines, "Live Phones", live_phones)
    emit_section(lines, "Live Tel Targets", live_tels)
    emit_section(lines, "Template Phones", template_phones)
    emit_section(lines, "Live Form IDs", live_forms)
    emit_section(lines, "Template Form IDs", template_forms)
    emit_section(lines, "Live Portal IDs", live_portals)
    emit_section(lines, "Template Portal IDs", template_portals)
    emit_section(lines, "Template Modules", template_modules)

    out = Path(args.out) if args.out else Path("audits") / f"{time.strftime('%Y%m%d-%H%M%S')}-audit.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        raise SystemExit(130)
