# Page Rules

Use this file as the portable operating contract for Kitchen Magic HubSpot
landing-page template work. A repo may contain a local copy under
`docs/page-rules.md`, but the skill reference is the baseline when starting in a
fresh or disposable workspace.

## Protected HubSpot Theme Files

Treat these paths as copy-on-write when they exist:

- `jm-theme/templates/**`
- `jm-theme/modules/**`
- `jm-theme/assets/**`
- `jm-theme/theme.json`
- `jm-theme/fields.json`

Do not edit, delete, rename, or move existing files in those paths unless the
user explicitly names the file and asks for an in-place edit. Create new
template files or new module folders instead.

Verify local uncommitted protected-tree changes before finishing protected-tree
work:

```sh
~/.codex/skills/jm-hubspotlps/scripts/protected_tree_check.sh --local
```

Verify committed branch changes against `main` before commit review, merge, or
deploy:

```sh
~/.codex/skills/jm-hubspotlps/scripts/protected_tree_check.sh --branch main
```

No output means existing protected files were not modified, deleted, or renamed
in that comparison.

Do not run this check after every docs-only or workbench-only edit. For changes
under `docs/`, `workbench/`, `hubspot-pulls/`, or `audits/`, use narrow
validation for the file being edited. If any edit touches `jm-theme/`, run the
protected-tree check before finishing that turn.

## URL And Contract Authority

Use `references/landing-page-map.md` from this skill as the portable source of
truth for template-to-live URL mapping and stable audit contracts. Do not
re-derive live URLs, phone numbers, portal IDs, or form IDs from template names.

If a repo-local `docs/landing-page-map.md` exists and differs from the bundled
reference, surface the discrepancy instead of silently choosing one.

## Working Structure

Use local working folders for new assets and keep HubSpot pull/audit output
separate from source files.

```text
workbench/
  new-templates/
  new-modules/

hubspot-pulls/
audits/
```

Use `workbench/new-templates/` for draft templates being made for new pages or
A/B variants.

Use `workbench/new-modules/` for draft modules being made for new pages or A/B
variants.

Use `hubspot-pulls/` for disposable HubSpot theme/page/live-render snapshots.

Use `audits/` for disposable comparison reports, page diffs, screenshots, and
findings.

Do not create a local `ab-tests/` folder by default. A/B tests live in HubSpot;
locally, the artifact is the new template or module variation that will be
uploaded to HubSpot.

Do not create shared content files for offers, forms, phones, copy, images, or
module settings unless the user explicitly asks for shared config.

## Traffic Source Rules

Google landing pages should use geo personalization when the template supports
it.

Facebook/Meta landing pages should not show geo-personalized copy unless the
user explicitly asks for a new geo-enabled Facebook variant. Do not flag hidden
geo scripts or HubSpot-rendered geo variables by themselves if the rendered copy
stays static.

## Live Page Drift

HubSpot live pages may be edited after Git deployment. Treat Git templates as
implementation inputs, not guaranteed runtime truth. Use the stable contracts in
`references/landing-page-map.md` before deciding whether live or local is wrong.

## Generated Template Diff Gate

Every generated template should be compared against its base template before
use.

The diff gate should fail if changes appear outside the explicit change
contract. At minimum it should check:

- module order
- module paths
- form IDs and portal IDs
- phone display values and `tel:` targets
- offer percent and deadline language
- geo policy scripts and geo-visible fields
- CTA targets
- image `src` and `alt` fields

For small changes, such as changing only one image or one copy field, the
verifier should report exactly those changed fields and reject all other
differences.
