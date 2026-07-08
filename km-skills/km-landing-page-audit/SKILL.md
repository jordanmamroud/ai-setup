---
name: km-landing-page-audit
description: |
  Audit Kitchen Magic landing pages from the user's perspective: grammar/typos, working forms and buttons, tel-link vs displayed phone match, phone-number uniqueness across tracking pages, offer/messaging consistency within and across pages, JS-rendered countdown deadlines, and A/B test detection. Use this skill whenever the user asks to audit, check, QA, review, or proofread landing pages, mentions "landing page audit", "check my pages", "page QA", "phone number check", "offer consistency", "messaging drift", or asks whether the live jm- pages look right. Also use when the user pastes a landing.kitchenmagic.com URL and asks if anything is wrong with it. This is a user-perspective content audit, NOT a technical/performance/SEO audit.
---

# Kitchen Magic — Landing Page Audit

You audit Kitchen Magic's live ad landing pages the way a careful visitor (or a picky proofreader) would: read everything, click everything, dial what's displayed, and notice when the page contradicts itself or its siblings. You do NOT audit technical things (page speed, Core Web Vitals, SEO scores, accessibility tooling). If a finding is invisible to a user reading the page, it's out of scope — with one exception: meta titles/descriptions, because searchers see those in results.

## Workflow

1. **Load the page list and intent map.** Read `references/pages.md`. It lists every page URL plus what that page is *supposed* to say: channel, topic, offer, expected phone behavior. The intent map is the ground truth for drift detection. If the user supplies different URLs, audit those instead, but still use the intent map for any page that's in it.
2. **Read the check definitions.** Read `references/checks.md` for the full definition, method, and severity of every check, including the JS-deadline and A/B-test handling.
3. **Fetch every page.** In rendered mode, run `scripts/capture.py` (see Capability modes) and also fetch each page's raw HTML once for the source greps. In static mode, fetch each page **twice** (the second fetch is the A/B-test diff probe — see checks.md). Either way, keep the raw HTML of each page; many checks grep the raw source (tel: hrefs, countdown scripts, A/B markers, meta tags).
4. **Run per-page checks** on each page (checks 1–6 in checks.md).
5. **Run cross-page checks** after all pages are fetched (checks 7–9).
6. **Write the report** (format below).

If a fetch fails, retry once; if it still fails, report the page as UNREACHABLE (severity: error — a user can't see the page at all) and continue with the rest.

## Capability modes

State which mode you're in at the top of the report.

- **Rendered mode (preferred — `scripts/capture.py` when Bash + Python with Playwright/Chromium are available):** Run:

  ```bash
  mkdir -p artifacts/lp-audit/<date>
  /opt/homebrew/opt/python@3.14/bin/python3.14 \
    ~/.codex/skills/km-landing-page-audit/scripts/capture.py \
    --out artifacts/lp-audit/<date> --zip 06410 \
    <url1> <url2> ...
  ```

  (Any Python 3 with the `playwright` package and Chromium installed works. The zip must be inside Kitchen Magic's service area — 06410, Cheshire CT — or the form wizard's zip gate won't advance.)

  Per page it writes `<slug>.json` (rendered bodyText, links with HTTP statuses, buttons, anchor-target checks, displayed-vs-tel phone diff, form fields, wizard log, empty-submit validation test, console errors, geoState, plus `overlays` and `disclaimers` — text pulled from hidden modals/popups/exit-intent and offer-details/legal blocks that `bodyText` never shows), plus `summary.json` with the cross-page phone map and `duplicatePhones`. The script network-blocks HubSpot's `/submissions/` endpoints, so the empty-submit test can never create a real lead — never test forms any other way. If a page errors (`captureErrors` in summary.json), retry it once before reporting UNREACHABLE.

  In this mode, checks 2–4 and 7 consume the JSON fields directly (`form.rendered`, `emptySubmitTest.validationErrors` non-empty, `anchorChecks.targetExists`, link `status` ≠ 200, `phones.displayedNotInTel`/`telNotDisplayed`, `summary.duplicatePhones`), and check 5 reads `overlays`/`disclaimers` for offer text and deadlines hidden in modals. Pages geo-personalize (`geoState` records the run's geo); if a finding could be geo-specific — phone numbers especially — say so rather than asserting it's wrong everywhere. Still grep each page's raw HTML for source-only checks (countdown dates, A/B markers, meta tags).

  **Screenshots are NOT part of the default audit.** Do not pass `--screenshots`, do not open, tile, or read screenshot images, and do not report visual/layout findings unless the user explicitly asks for a visual check. (Full-page captures of these pages are ~10,000px tall; reading them into context once took ~9 minutes of a 10-minute run.) If the user does ask for a visual pass, run capture with `--screenshots` and tell them the PNGs are in the output folder for their own review — only read an image into context for a page whose JSON already signals something visually suspect (console errors, missing form, broken anchors).

- **Static mode (web_fetch in chat/Cowork, no Bash/Playwright):** You see the server-sent HTML, not the browser-rendered page. Per Kitchen Magic's own build standard, all user-visible content must be in static HTML for Google Ads crawlability — so a static fetch should see everything a user sees. Two consequences:
  - JS-rendered values (countdown deadlines) are verified by grepping the page source for the script's embedded date, not by reading the visible slot. See check 5.
  - User-visible content that is genuinely absent from raw HTML is itself a **warning** ("crawlability violation per KM build standards"), separate from whatever the missing content was.
  - You cannot click-test form submission end-to-end. Verify the form's presence, fields, and destination instead, and say so.
  - Offer text often lives in hidden modals (exit-intent popups, offer-details/disclaimer overlays) that aren't in the visible body. After saving the raw HTML, run `scripts/extract_overlays.py <saved-html-files-or-dir>` to pull that text out for check 5 — don't rely on the rendered body alone.
- **Browser mode (Claude in Chrome or any rendered-DOM tool available):** Prefer the rendered DOM. You can read live countdown values directly, observe which A/B variant rendered, and optionally step through the form UI (do NOT submit real lead data — stop before final submission).

## Severity rubric

- **error** — A user sees something broken, contradictory, or false: dead/empty links, conflicting offer percentages on the same page, expired dates, wrong phone wired into tel:, duplicate tracking numbers across pages, missing page.
- **warning** — Likely wrong but possibly intentional; or correct-but-risky: hero offer broader than the legal disclaimer's scope, content missing from static HTML, meta description contradicting page content, A/B test active (audit covers one variant only).
- **nit** — Cosmetic or consistency-level: typos that don't change meaning, inconsistent tel: href formatting that still dials correctly, "45+ years" vs "47+ years" style drift, trailing spaces in headings.

When unsure between two severities, pick the lower one and say why. Never invent findings; every finding must quote the exact text from the fetched page.

## Report format

Write one markdown report to `artifacts/lp-audit/<date>/report.md`, relative to the current working directory — the same dated folder the rendered-mode captures land in. Never hardcode an absolute path; the folder is created wherever the skill is run. If the user names a different output location, use that instead. The chat reply is just the triage list plus the report's file path.

Report structure, in this order:

```
# Landing Page Audit — <date>
Mode: rendered | static | browser. Pages audited: N. Errors: X, Warnings: Y, Nits: Z.

## Triage list
(every finding as one line: page → severity → issue. Sorted errors first,
then warnings, then nits. This is the skimmable "what's wrong" list;
evidence lives in the per-page sections below.)

## Cross-page findings
(phone uniqueness table, drift, brand-fact inconsistencies)

## <page URL> (one section per page)
A/B test: detected/not detected (and which variant signals, if any)
| # | Severity | Check | Finding | Exact quote / location |

## Unverifiable items
(things that need browser mode or a human click — listed, never guessed)
```

Rules for the report:
- Every finding includes the **exact quoted text** and where it sits (hero, FAQ #6, footer, popup modal, meta description).
- Phone numbers are compared **digits-only** (strip parens, dashes, spaces, %20). `tel:(888)%20995-5317` and `tel:8889955317` are the same number; the formatting difference is a nit, not an error.
- Counts in the summary line must match the body. Recount before finishing.
- If a check produced nothing on any page, say so in one line ("No tel/display mismatches found") — silence reads as "not checked."
- Compare new findings against `references/example-findings.md` for calibration: it contains real past findings per category with their assigned severity. Match its judgment style.

## Scope guardrails

- Do not report: page speed, image weight, alt-text coverage, schema markup, GTM/pixel configuration, HubSpot module internals, CSS issues. (Tracking pixels and GTM snippets in the source are not findings.)
- Do not submit forms or send any data to the pages.
- Do not "fix" anything — this skill reports. If the user asks to fix a finding in a module, hand off to the km-hubl-module skill.
