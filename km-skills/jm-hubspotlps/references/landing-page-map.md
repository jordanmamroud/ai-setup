# Landing Page Map And Stable Contracts

Portable source of truth for Kitchen Magic HubSpot landing-page mappings and
stable audit contracts. A repo may contain a local copy under
`docs/landing-page-map.md`, but this bundled reference lets the skill operate in
a fresh or disposable workspace.

## Template To Live URL Map

| Template | Branch | Live URL | Status |
|---|---|---|---|
| `template-google-kitchen.html` | `main` | https://landing.kitchenmagic.com/jm-remodeling-special1 | **Live** |
| `template-bath-google.html` | `main` | https://landing.kitchenmagic.com/jm-bathroom-remodeling | **Live** |
| `template-facebook-bath.html` | `main` | — | Not deployed |
| `template-google-refacing.html` | `feat/refacing-template` | https://landing.kitchenmagic.com/jm-refacing-ppc | **Live (A/B test)** |
| `template-facebook-kitchen-remodeling-1.html` | `feat/facebook-kitchen-template` | — | Not deployed |

## Stable Audit Contracts

Use these values as the audit baseline for fields that should almost never
change. If a fresh HubSpot pull differs from this table, treat the pull as
suspect until the change is confirmed. If a local template differs from this
table, treat the local template as stale or wrong. Offer copy and deadlines are
not included here because they change by campaign.

| Page / template | Traffic | Phone | Portal ID | Hero form ID | Exit/popup form ID | Geo audit rule |
|---|---|---|---|---|---|---|
| `template-google-kitchen.html` / `jm-remodeling-special1` | Google | `(888) 995-5317` | `126868` | `cd58390b-6a62-40be-8eb0-02e93ff0bc9e` | `cd58390b-6a62-40be-8eb0-02e93ff0bc9e` | Geo allowed |
| `template-bath-google.html` / `jm-bathroom-remodeling` | Google | `(888) 995-5317` | `126868` | `cd58390b-6a62-40be-8eb0-02e93ff0bc9e` | `cd58390b-6a62-40be-8eb0-02e93ff0bc9e` | Geo allowed |
| `template-facebook-bath.html` | Facebook/Meta draft | `(888) 995-5317` | `126868` | `cd58390b-6a62-40be-8eb0-02e93ff0bc9e` | — | Flag only visible geo-personalized copy |
| `template-google-refacing.html` / `jm-refacing-ppc` | Google | Not recorded | Not recorded | Not recorded | Not recorded | Geo allowed; A/B-tested URL is non-deterministic |
| `template-facebook-kitchen-remodeling-1.html` / `-ab-variant-826672c9-0ac5-47fb-916a-b55173e341df` preview | Facebook/Meta | `(833) 741-5008` | `126868` | `d211cba7-e7c5-4753-87f3-73468cc88723` | `d211cba7-e7c5-4753-87f3-73468cc88723` | Flag only visible geo-personalized copy |

## Caveats For Auditing

- **`template-google-kitchen.html` ↔ `jm-remodeling-special1`**
  This is the live page. `template-facebook-kitchen-remodeling-1.html` is a
  not-yet-deployed Git variant that mirrors this page's content. The real
  Git-vs-live drift check for this content is `template-google-kitchen.html` vs
  the URL, but treat existing theme files as protected copy-on-write files.

- **`template-google-refacing.html` ↔ `jm-refacing-ppc`**
  Deployed, but A/B tested against the old/legacy refacing page. Fetching the
  URL is non-deterministic; you may get the new template or the old version
  depending on A/B bucketing. A single scrape is not a reliable drift signal for
  this page. Sample multiple times or disable the test before auditing.

- **`template-facebook-bath.html`**
  Not deployed. The current live Facebook bath page is
  https://landing.kitchenmagic.com/jm-fbbath, which runs a different/legacy
  template. Do not do a strict Git-vs-live diff between them; treat `jm-fbbath`
  as a content reference for the Facebook bath vertical only.

- **`template-facebook-kitchen-remodeling-1.html`**
  Not deployed as a named live URL. The known preview/variant URL in the stable
  contract uses the Facebook kitchen form and phone contract.

- Feature-branch templates may not exist in a new checkout. Check the listed
  branch before concluding a template is missing.

- Live pages are edited in the HubSpot UI after deploy, so Git templates may be
  stale relative to their live URLs. Treat stable contract values as the audit
  baseline for phone, portal, and form IDs.

_Last updated: 2026-05-18_
