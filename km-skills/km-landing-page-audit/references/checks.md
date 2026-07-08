# Check Definitions

Nine checks. 1–6 run per page; 7–9 run across all pages after fetching. Every finding must quote exact page text. Severities follow the rubric in SKILL.md.

## Per-page checks

### 1. Grammar, spelling, and copy quality
Read every piece of user-visible text: headings, body, bullets, button labels, FAQ, footer, popup modals, offer disclaimers, and meta title/description (searchers see those). Flag:
- Typos and wrong words ("too choose from") — **nit** unless meaning changes
- Missing words ("11 warranty" → missing "year") — **nit**, but **warning** if it garbles a claim
- Broken/incomplete sentences, stray punctuation, comma splices in headlines — **nit**
- Sentences with visible holes (e.g., "call ___ to schedule" where a value failed to render) — **error** (see also check 3)

Skip customer testimonial quotes for grammar (verbatim customer voice), but DO flag template-injected errors inside them (e.g., "the we love our new bathroom" where copy was find-replaced).

### 2. Form check (user-perspective)
For each form/multi-step form on the page, verify from the source:
- The form exists where the CTAs point (anchors like `#hero-form`, `#form1` resolve to a real element) — broken anchor = **error**
- The visible step flow reads coherently (project picker → zip/service-area step → contact step → confirmation copy present)
- A confirmation/"You're all set" state exists — missing = **warning**
- HubSpot form embed or form markup is present in the source — a CTA pointing at a form that isn't in the HTML = **error**
Rendered mode adds the mechanical pass from capture.py's JSON: `form.rendered` must be true, expected fields present (firstname, lastname, zip, state, phone, email), submit button present and not disabled, and `emptySubmitTest.validationErrors` non-empty (empty = a visitor can't tell why their submission fails, or blank leads go through) — **error**. A `wizardLog` showing the zip gate refusing an in-area zip = **error**.
Static mode cannot submit; list end-to-end submission under "Unverifiable items." Browser mode may step through the UI but must never submit.

### 3. Buttons and links
Collect every `<a href>` a user can act on (CTAs, footer links, Privacy/Sitemap, phone links, "Offer Details" toggles).
- In-page anchors (`#...`): confirm the target id exists in the source. Missing target = **error**.
- External links: in rendered mode capture.py already HEAD-checks every unique link — any link with `status` ≠ 200 = **error**. In static mode, web_fetch each unique URL once; non-resolving / error page = **error**. (Dedupe — don't fetch the same Privacy Policy URL seven times.)
- Empty hrefs, `href=""`, `href="#"` on a styled CTA, or empty `tel:` = **error**. Canonical example: a "call us" sentence rendering as `call [](tel:)`.
- `javascript:void(0)` toggles (modals) are fine — not findings.

### 4. Tel link vs displayed number
For every phone occurrence: extract the `tel:` href and the display text. Normalize both to digits only (strip parens, spaces, dashes, `%20`, leading 1).
- Digits differ between href and display = **error** (user dials something other than what they read).
- Digits match but href formatting is unusual (`tel:(888)%20995-5317`) = **nit** (works, inconsistent).
- Also extract phone numbers from meta title/description. A meta phone that appears nowhere on the page = **warning** (searchers may dial it; it's likely a stale tracking number).
Record every number found per page — check 7 consumes this.

### 5. Offers, deadlines, and JS-rendered countdowns
Identify every offer statement on the page: hero, badges, FAQ answers, footer CTA banner, popup modal, offer disclaimer.

Offer text frequently hides in modals that the visible body never shows (exit-intent popups, "Offer Details" overlays, legal/disclaimer blocks). Always check these — they're a common source of stale or contradictory offers:
- Rendered mode: read the `overlays` and `disclaimers` arrays in each page's JSON (capture.py extracts them from hidden elements via `textContent`).
- Static mode: run `scripts/extract_overlays.py` over the saved HTML and read its output.
Treat overlay/disclaimer offers as first-class: a percentage or deadline there that contradicts the hero, or a past date in a disclaimer, is an **error** just as if it were visible on the page.
- All statements of the discount on one page must agree (percentage, what it applies to). Hero says 40%, FAQ/footer/modal say 30% = **error**, one finding listing all locations.
- **Countdown/deadline slots:** if visible text reads like "Ends" / "Until" with no date, do NOT immediately flag. First grep the raw source for the countdown mechanism: inline script setting a date (`deadline`, `endDate`, `countdown`, a date literal near the slot), a data attribute (`data-end-date`), or an embedded config. Then:
  - Date found in source and in the future → **no finding**; report informationally as "JS-rendered deadline, value in source: <date>".
  - Date found but in the past → **error** (expired offer still displayed).
  - No date anywhere in source → **error** ("deadline slot has no data source — renders empty for users"), plus a **warning** that the value isn't in static HTML (crawlability violation per KM build standards).
- Hard dates in disclaimers/legal copy: compare to today's date; past = **error**.
- Hero offer broader than disclaimer scope (e.g., "50% off installation" vs "applies to tub-to-shower conversion only") = **warning** unless pages.md marks it known.

### 6. On-page messaging vs intent map
Compare the page's actual topic, offer, and channel-specific copy against its row in pages.md.
- Offer on page ≠ expected offer = **error** (either the page drifted or the map is stale — say which file to fix).
- Copy clearly belonging to another page's topic (bathroom copy on a kitchen page, refacing claims framed as full-remodel claims) = **error**.
- Channel bleed (FB-campaign framing on GA pages or vice versa) = **warning**.

## Cross-page checks

### 7. Phone uniqueness
Build a table: number (digits) → pages displaying it. Any number on 2+ pages = **error**, one finding per shared number listing all pages. Present the full table in the report even when clean.

### 8. Cross-page drift and brand-fact consistency
- Brand facts (years in business, kitchens transformed, warranty length, review counts/ratings) must match across pages per pages.md global rules. Mismatch = **nit** for stale-but-true ("45+" vs "47+"), **warning** if a factual claim conflicts (different warranty lengths).
- Identical template blocks across pages (testimonials, FAQ, comparison tables) with one page carrying another page's topic words = **error** (copy was cloned and incompletely adapted — the core "drift" failure mode).

### 9. A/B test detection
Per page:
- **Markers:** grep raw source for HubSpot A/B indicators: `ab_test`, `abTest`, `content_ab_`, `hsVariant`, `mab` (adaptive testing), variant-suffixed page ids in `hsVars`. Any hit → report "A/B test signals present" (**warning**: findings apply only to the served variant).
- **Double-fetch diff:** compare the two fetches of the page. Material content differences (different headline, offer, layout — not timestamps/nonces) → A/B test almost certainly active; report what differed and audit BOTH captured variants. Identical fetches ≠ proof of no test (caching, sticky bucketing) — markers are the primary signal.
- No markers and identical fetches → "No A/B test detected" (informational).
