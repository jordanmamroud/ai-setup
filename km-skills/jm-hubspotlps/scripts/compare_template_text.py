#!/usr/bin/env python3
"""Compare two HubSpot templates for high-signal landing-page differences."""

from __future__ import annotations

import argparse
import html
import re
import time
from pathlib import Path


PATTERNS = {
    "module_order": re.compile(r"\{%\s+module\s+\"([^\"]+)\"", re.I),
    "module_paths": re.compile(r"path\s*=\s*\"([^\"]+)\"", re.I),
    "phones": re.compile(r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}"),
    "tel_targets": re.compile(r"tel:([+0-9][+0-9().\-\s]*)", re.I),
    "offers": re.compile(r"\b\d{1,2}%\s+Off\s+Installation\b", re.I),
    "deadline_copy": re.compile(
        r"(?:[A-Za-z0-9_]+\s*=\s*\"([^\"]*(?:deadline|ends|\b\d{1,2}/\d{1,2}\b)[^\"]*)\""
        r"|\"[^\"]+\"\s*:\s*\"([^\"]*(?:deadline|ends|\b\d{1,2}/\d{1,2}\b)[^\"]*)\")",
        re.I,
    ),
    "show_deadline": re.compile(r"\bshow_deadline\s*=\s*[\"']?([A-Za-z0-9_-]+)[\"']?", re.I),
    "form_ids": re.compile(r"(?:form_id|form-id|data-form-id)\s*[=:]\s*[\"']?([A-Za-z0-9_-]{8,})", re.I),
    "portal_ids": re.compile(
        r"(?:form_portal_id|form-portal-id|portal_id|portal-id|data-form-portal-id|data-portal(?:-id)?)\s*[=:]\s*[\"']?([A-Za-z0-9_-]{3,})",
        re.I,
    ),
    "image_srcs": re.compile(r"(?:\bsrc\s*=\s*[\"']([^\"']+)[\"']|\"src\"\s*:\s*\"([^\"]*)\")", re.I),
    "image_alts": re.compile(r"(?:\balt\s*=\s*[\"']([^\"']*)[\"']|\"alt\"\s*:\s*\"([^\"]*)\")", re.I),
    "geo": re.compile(r"JM_GEO_STATE|loc_id|geoip_region|data-loc-insert", re.I),
    "cta_targets": re.compile(r"cta_target\s*=\s*\"([^\"]+)\"|href\s*=\s*\"(#[^\"]+)\"", re.I),
    "auto_popup": re.compile(r"\benable_auto_popup\s*=\s*[\"']?([A-Za-z0-9_-]+)[\"']?", re.I),
}


def values(pattern: re.Pattern[str], text: str) -> list[str]:
    out: list[str] = []
    for match in pattern.finditer(text):
        groups = [g for g in match.groups() if g is not None]
        out.append(html.unescape(groups[0] if groups else match.group(0)))
    return out


def compare(name: str, base: str, candidate: str) -> tuple[bool, list[str], list[str]]:
    base_values = values(PATTERNS[name], base)
    candidate_values = values(PATTERNS[name], candidate)
    return base_values == candidate_values, base_values, candidate_values


def append_values(lines: list[str], items: list[str]) -> None:
    if not items:
        lines.append("- None")
        return
    lines.extend(f"- `{v}`" for v in items[:80])
    if len(items) > 80:
        lines.append(f"- ... {len(items) - 80} more")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--out", help="Markdown output path, default audits/<timestamp>-template-compare.md")
    args = parser.parse_args()

    base_path = Path(args.base)
    candidate_path = Path(args.candidate)
    base = base_path.read_text(encoding="utf-8", errors="replace")
    candidate = candidate_path.read_text(encoding="utf-8", errors="replace")

    lines = [
        "# HubSpot Template Comparison",
        "",
        f"- Base: `{base_path}`",
        f"- Candidate: `{candidate_path}`",
        f"- Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    changed = False
    for name in PATTERNS:
        same, base_values, candidate_values = compare(name, base, candidate)
        status = "unchanged" if same else "changed"
        if not same:
            changed = True
        lines.append(f"## {name} ({status})")
        lines.append("")
        lines.append("Base:")
        append_values(lines, base_values)
        lines.append("")
        lines.append("Candidate:")
        append_values(lines, candidate_values)
        lines.append("")

    out = Path(args.out) if args.out else Path("audits") / f"{time.strftime('%Y%m%d-%H%M%S')}-template-compare.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out)
    return 1 if changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
