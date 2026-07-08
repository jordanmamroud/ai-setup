#!/usr/bin/env python3
"""Capture rendered-state snapshots of landing pages for a user-perspective audit.

For each URL this renders the page in headless Chromium and writes:
  <out>/<slug>.json  - everything the audit needs (text, links, buttons, phones, form state)
  <out>/<slug>.png   - full-page screenshot (only with --screenshots; for human review)

It also writes <out>/summary.json with cross-page phone-number data.

Safety: all requests to HubSpot form-submission endpoints are blocked at the
network layer, so the empty-submit validation test can never create a real lead.

Usage:
  python3 capture.py --out <dir> <url> [<url> ...]
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

PHONE_DISPLAY_RE = re.compile(r"\(?\b\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b")
# Block only actual form *submissions* — the embed/definition fetch
# (forms.hsforms.com/embed/...) must stay reachable or the form won't render.
SUBMISSION_BLOCKLIST = [
    "**/submissions/**",
    "**/collected-forms/**",
]
FORM_SELECTOR = ".hs-form-container form, form.hs-form, form[data-form-id]"


def normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits


def slug_for(url: str) -> str:
    path = urlparse(url).path.strip("/") or "index"
    return re.sub(r"[^a-zA-Z0-9_-]", "_", path)


PAGE_EXTRACT_JS = """
() => {
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
  };
  const links = [...document.querySelectorAll('a')].map(a => ({
    text: (a.innerText || a.getAttribute('aria-label') || '').trim().replace(/\\s+/g, ' ').slice(0, 120),
    href: a.getAttribute('href') || '',
    visible: visible(a),
  }));
  const buttons = [...document.querySelectorAll('button, input[type=submit], [role=button]')].map(b => ({
    text: (b.innerText || b.value || b.getAttribute('aria-label') || '').trim().replace(/\\s+/g, ' ').slice(0, 120),
    disabled: !!b.disabled,
    type: b.getAttribute('type') || b.tagName.toLowerCase(),
    visible: visible(b),
  }));
  // For every in-page anchor link, check the target element actually exists.
  const anchorChecks = links
    .filter(l => l.href.startsWith('#') && l.href.length > 1)
    .map(l => ({
      href: l.href,
      targetExists: !!(document.getElementById(l.href.slice(1)) ||
                       document.querySelector(`a[name="${l.href.slice(1)}"]`)),
    }));
  return {
    title: document.title,
    bodyText: document.body.innerText,
    links,
    buttons,
    anchorChecks,
    htmlLang: document.documentElement.lang || null,
  };
}
"""

# Pull text from overlay elements (modals, popups, exit-intent) and disclaimer/
# offer-details blocks. Uses textContent, not innerText, so it captures modals
# that are still display:none — the exact content a fresh visitor's body text
# (and a plain screenshot) never shows. Skips nested same-kind matches and drops
# fragments contained in a longer sibling, so each block appears once.
OVERLAY_EXTRACT_JS = """
() => {
  const norm = (s) => (s || '').replace(/\\s+/g, ' ').trim();
  const TOK = {
    overlay: ['modal', 'popup', 'exit-intent', 'exit_intent', 'exitintent', 'lightbox'],
    disclaimer: ['disclaimer', 'offer-details', 'offer_details', 'legal', 'fineprint', 'fine-print'],
  };
  const kindOf = (el) => {
    const blob = ((el.id || '') + ' ' + (el.getAttribute('class') || '')).toLowerCase();
    for (const k of Object.keys(TOK)) if (TOK[k].some(t => blob.includes(t))) return k;
    return null;
  };
  const out = { overlay: [], disclaimer: [] };
  for (const el of document.querySelectorAll('*')) {
    const k = kindOf(el);
    if (!k) continue;
    let anc = el.parentElement, nested = false;
    while (anc) { if (kindOf(anc) === k) { nested = true; break; } anc = anc.parentElement; }
    if (nested) continue;
    const t = norm(el.textContent).slice(0, 1500);
    if (t.length > 1) out[k].push(t);
  }
  for (const k of Object.keys(out)) {
    const seen = out[k];
    out[k] = seen
      .filter((t, i) => !seen.some((u, j) => j !== i && u.length > t.length && u.includes(t)))
      .filter((t, i, a) => a.indexOf(t) === i);
  }
  return out;
}
"""

FORM_EXTRACT_JS = """
(form) => {
  const fields = [...form.querySelectorAll('input, select, textarea')]
    .filter(f => !['hidden'].includes(f.type))
    .map(f => {
      const wrap = f.closest('.hs-form-field, .field, fieldset, div');
      const label = wrap ? (wrap.querySelector('label')?.innerText || '').trim().replace(/\\s+/g, ' ') : '';
      return { name: f.name || f.id || '', type: f.type || f.tagName.toLowerCase(),
               required: f.required || /\\*/.test(label), label: label.slice(0, 80) };
    });
  const submit = form.querySelector('input[type=submit], button[type=submit], button:not([type])');
  return {
    fields,
    submitText: submit ? (submit.value || submit.innerText || '').trim() : null,
    submitDisabled: submit ? !!submit.disabled : null,
    submitPresent: !!submit,
  };
}
"""

VALIDATION_ERRORS_JS = """
(form) => [...form.querySelectorAll('.hs-error-msg, .hs-error-msgs label, [class*="error"]')]
  .map(e => e.innerText.trim()).filter(t => t.length > 0 && t.length < 200)
"""


def walk_wizard(page, zip_code: str) -> list:
    """Advance a multi-step lead wizard (choice tiles -> zip gate) far enough
    for the real HubSpot form to be created. Returns a log of steps taken."""
    log = []
    try:
        # Step type 1: clickable choice tiles (e.g. "What best describes your project?")
        tile = page.query_selector(".step.active .style-tile, .step.active [onclick*='selectTile']")
        if tile:
            label = (tile.inner_text() or "").strip().replace("\n", " ")[:60]
            tile.click()
            page.wait_for_timeout(1500)
            log.append(f"clicked choice tile: {label}")
        # Step type 2: zip-code gate (auto-advances when 5 digits entered)
        zip_input = page.query_selector(
            ".step.active input[autocomplete='postal-code'], .step.active input[maxlength='5']")
        if zip_input:
            zip_input.fill(zip_code)
            page.wait_for_timeout(2500)
            log.append(f"entered zip {zip_code}")
            active = page.evaluate("() => document.querySelector('.step.active')?.id || null")
            log.append(f"active step after zip: {active}")
            # Some variants need an explicit continue button.
            if zip_input.is_visible():
                for txt in ("Continue", "Next", "Check"):
                    btn = page.query_selector(f".step.active button:has-text('{txt}')")
                    if btn:
                        btn.click()
                        page.wait_for_timeout(2000)
                        log.append(f"clicked '{txt}' button")
                        break
    except Exception as e:
        log.append(f"wizard error: {str(e)[:150]}")
    return log


def capture_page(context, url: str, out_dir: Path, zip_code: str, screenshots: bool) -> dict:
    slug = slug_for(url)
    page = context.new_page()
    result = {"url": url, "slug": slug, "errors": []}
    blocked_submissions = []

    def block_submission(route):
        blocked_submissions.append(route.request.url)
        route.abort()

    for pattern in SUBMISSION_BLOCKLIST:
        page.route(pattern, block_submission)

    console_errors = []
    page.on("pageerror", lambda e: console_errors.append(str(e)[:200]))

    try:
        resp = page.goto(url, wait_until="domcontentloaded", timeout=45000)
        result["httpStatus"] = resp.status if resp else None
        result["finalUrl"] = page.url
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass  # busy pages (chat widgets etc.) may never go idle; proceed anyway

        # Capture page content BEFORE interacting with the wizard, so bodyText
        # reflects what a fresh visitor sees.
        snap = page.evaluate(PAGE_EXTRACT_JS)
        result.update(snap)
        overlays = page.evaluate(OVERLAY_EXTRACT_JS)
        result["overlays"] = overlays.get("overlay", [])
        result["disclaimers"] = overlays.get("disclaimer", [])
        result["geoState"] = page.evaluate("() => window.JM_GEO_STATE || null")
        if screenshots:
            page.screenshot(path=str(out_dir / f"{slug}.png"), full_page=True)
            result["screenshot"] = f"{slug}.png"

        # The HubSpot form may only be created after walking the lead wizard
        # (choice tile -> zip gate). Try direct render first, then walk.
        form_rendered = False
        try:
            page.wait_for_selector(FORM_SELECTOR, timeout=8000)
            form_rendered = True
        except Exception:
            result["wizardLog"] = walk_wizard(page, zip_code)
            try:
                page.wait_for_selector(FORM_SELECTOR, timeout=15000)
                form_rendered = True
            except Exception:
                pass

        # Phones: displayed in visible text vs tel: hrefs.
        displayed = sorted({normalize_phone(m) for m in PHONE_DISPLAY_RE.findall(snap["bodyText"])})
        tel_hrefs = sorted({normalize_phone(l["href"][4:]) for l in snap["links"]
                            if l["href"].lower().startswith("tel:")})
        result["phones"] = {
            "displayed": displayed,
            "telLinks": tel_hrefs,
            "displayedNotInTel": [p for p in displayed if p not in tel_hrefs],
            "telNotDisplayed": [p for p in tel_hrefs if p not in displayed],
        }

        # Form: fields, then the empty-submit validation test (submission endpoint blocked).
        form_info: dict = {"rendered": form_rendered}
        result["form"] = form_info
        if form_rendered:
            form = page.query_selector(FORM_SELECTOR)
            form_info.update(page.evaluate(FORM_EXTRACT_JS, form))
            try:
                submit = form.query_selector("input[type=submit], button[type=submit], button:not([type])")
                if submit:
                    submit.click(timeout=5000)
                    page.wait_for_timeout(2500)
                    still_there = page.query_selector(FORM_SELECTOR)
                    form_info["emptySubmitTest"] = {
                        "validationErrors": page.evaluate(VALIDATION_ERRORS_JS, still_there) if still_there else [],
                        "formStillPresent": bool(still_there),
                        "submissionAttemptsBlocked": list(blocked_submissions),
                        "urlAfter": page.url,
                    }
            except Exception as e:
                form_info["emptySubmitTest"] = {"error": str(e)[:200]}

        result["consoleErrors"] = console_errors[:10]
    except Exception as e:
        result["errors"].append(str(e)[:300])
    finally:
        page.close()
    return result


def check_external_links(playwright, pages: list) -> None:
    """HEAD/GET every unique external link once; annotate each page's links with status."""
    urls = {}
    for p in pages:
        for l in p.get("links", []):
            href = l["href"]
            if href.startswith("http"):
                urls.setdefault(href, None)
    req = playwright.request.new_context()
    for href in urls:
        try:
            r = req.head(href, timeout=10000)
            if r.status in (403, 405):  # some servers reject HEAD
                r = req.get(href, timeout=15000)
            urls[href] = r.status
        except Exception:
            urls[href] = "unreachable"
    req.dispose()
    for p in pages:
        for l in p.get("links", []):
            if l["href"] in urls:
                l["status"] = urls[l["href"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--zip", default="06410",
                    help="Zip code used to pass service-area gates (default: Kitchen Magic HQ area)")
    ap.add_argument("--screenshots", action="store_true",
                    help="Also save a full-page PNG per page (off by default; for human review only)")
    ap.add_argument("urls", nargs="+")
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 900})
        for url in args.urls:
            print(f"capturing {url} ...", file=sys.stderr)
            results.append(capture_page(context, url, out_dir, args.zip, args.screenshots))
        browser.close()
        check_external_links(pw, results)

    phone_map = {}
    for r in results:
        for ph in r.get("phones", {}).get("displayed", []):
            phone_map.setdefault(ph, []).append(r["slug"])
    summary = {
        "capturedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pages": [r["slug"] for r in results],
        "phoneNumberToPages": phone_map,
        "duplicatePhones": {p: s for p, s in phone_map.items() if len(s) > 1},
        "captureErrors": {r["slug"]: r["errors"] for r in results if r["errors"]},
    }

    for r in results:
        (out_dir / f"{r['slug']}.json").write_text(json.dumps(r, indent=2))
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
