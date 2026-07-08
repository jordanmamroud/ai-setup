# Landing Page Audit Checklist

Use this checklist for HubSpot landing-page audits and template-vs-live comparisons.

## Required Context

- Read `references/landing-page-map.md` before choosing a live URL or judging
  phone, portal ID, form ID, or geo-policy drift.
- Read `references/page-rules.md` before editing files.
- If repo-local `docs/landing-page-map.md` or `docs/page-rules.md` exists,
  inspect it as a working copy and surface any conflict with the bundled
  reference.
- Treat HubSpot preview URLs as live evidence for that preview only.
- Treat A/B-tested URLs as non-deterministic unless the URL is a specific preview or variant URL.

## Checks

1. Vertical/topic consistency: kitchen, bath, refacing, and remodeling copy must not bleed into the wrong page.
2. Offer consistency: headline, hero eyebrow, CTA, FAQ, footer/legal, and exit popup must agree on discount and deadline.
3. Phone consistency: visible phone numbers and generated `tel:` digits must agree.
4. Form config: portal ID and form ID must match the stable audit contract for
   the intended page/traffic source.
5. Geo policy: Google pages may use geo; Facebook/Meta pages should not show
   geo-personalized copy unless explicitly requested. Hidden scripts alone are
   not a finding when rendered copy stays static.
6. Module order and paths: variant templates should keep intentional module order and module paths.
7. Placeholder content: flag TODO/FIXME/lorem, empty URLs, empty form IDs, placeholder links, and literal `{loc}` on live pages.
8. Image checks: flag missing `src`, empty alt text, broken-looking domains, and wrong-vertical images.
9. Link integrity: flag `href="#"`, empty links, wrong vertical links, bad legal/footer links, and mismatched CTA targets.
10. Accessibility/SEO basics: title, meta description, one sensible H1, heading sequence, lang, canonical/OG when relevant.
11. Cross-page collision: flag unexpected reuse of headline, hero asset, form config, or major copy across different verticals.
12. Copy-sense pass: flag text that technically matches patterns but does not belong on the page.

## Severity

- CRIT: wrong vertical, live shared module damage, default bleed into production.
- HIGH: offer, form, phone, geo, HubL, or live-vs-template drift that can hurt conversion or tracking.
- MED: broken assets, links, copy collisions, grammar, or SEO basics.
- LOW: polish and wording issues that do not affect function or offer correctness.

## Report Shape

Lead with required template updates or findings. Include evidence and file/line references when available. Keep raw fetched output in `hubspot-pulls/` and write the final report to `audits/`.
