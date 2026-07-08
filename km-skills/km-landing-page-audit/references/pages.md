# Pages & Intent Map

This file is the ground truth for what each page is *supposed* to say. Update it whenever offers, phones, or pages change. Drift detection compares page content against this map.

## Global rules

- **Phone uniqueness:** Every page must display its own unique tracking number. The same number appearing on two or more pages is an **error** (call attribution gets blended).
- **Brand facts (must match on every page):** Kitchen Magic, since 1979, 47+ years, 60,000+ kitchens, HQ Nazareth PA, service areas CT / DE / MA / NJ / NY / PA / RI, 11-year warranty on refacing products & craftsmanship. ("45+ years" on any page is stale copy — nit.)
- **Channel hygiene:** FB-specific copy (e.g., "Summer Special … Ends 6/30" framing built for the FB campaign) must not appear on GA pages, and vice versa, unless the intent map says otherwise.

## GA Main Ad Landing Pages (clean URLs containing `/jm-`)

| URL | Topic | Expected offer | Template | Notes |
|---|---|---|---|---|
| https://landing.kitchenmagic.com/jm-remodeling-special1 | Kitchen remodel | 30% off installation | New 2026 (form picker) | Hero countdown is JS-rendered |
| https://landing.kitchenmagic.com/jm-bathroom-remodeling | Bathroom remodel | 50% off installation | New 2026 | Hero countdown is JS-rendered. Disclaimer scopes offer to tub-to-shower conversions — hero/disclaimer scope gap is a known **warning** |
| https://landing.kitchenmagic.com/jm-refacing-ppc | Cabinet refacing | 30% off installation | New 2026 | Hero countdown is JS-rendered |
| https://landing.kitchenmagic.com/jm-remarketing-special | Cabinet refacing (remarketing) | Free design; up to 30% off door collections per disclaimer | Legacy | Disclaimer contains a hard date — verify not expired |

## FB Landing Pages

| URL | Topic | Expected offer | Template | Notes |
|---|---|---|---|---|
| https://landing.kitchenmagic.com/jm-remodeling-fbspecial | Kitchen remodel | Free design; 40% off installation, ends 6/30; $299/mo financing hook | New 2026 | |
| https://landing.kitchenmagic.com/jm-refacing-fbspecial | Cabinet refacing | 40% off refacing installation, ends 6/30 | Legacy | |
| https://landing.kitchenmagic.com/jm-fbbath | Bathroom | 50% off installation, ends 6/30 | Legacy | |

## Audit settings

- **Service-area zip for form testing (rendered mode)**: 06410 (Cheshire, CT). The lead wizard has a zip gate; this zip must be inside Kitchen Magic's service area or the wizard won't advance to the real form.

## Maintenance

- When a page is added: add a row with topic, expected offer, template, and any known JS-rendered slots.
- When an offer changes: update the row **before** running the audit, or the audit will flag the new offer as drift.
- Expected phone numbers are intentionally NOT listed here (they rotate with tracking campaigns). The audit enforces *uniqueness across pages* and *tel/display match within a page*, not specific values. If you want value-level enforcement later, add an "Expected phone" column and the audit will use it.
