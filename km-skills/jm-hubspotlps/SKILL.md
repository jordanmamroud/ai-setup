---
name: jm-hubspotlps
description: HubSpot landing page creation and audit workflows for Kitchen Magic-style CMS themes. Use when Codex needs to create a new HubSpot template, module, page variation, or A/B-test artifact; audit or compare a live/preview landing page against a local template; fetch HubSpot/live page reference HTML; prepare an hs cms upload command; or protect live/shared HubSpot theme files from accidental edits.
---

# JM HubSpot LPs

## Core Rule

Treat existing HubSpot theme files as live-sensitive reference material. Most work should add a new template or module variation instead of editing deployed files in place.

Use existing files in `jm-theme/` as sources to copy from. Edit an existing file under `jm-theme/templates`, `jm-theme/modules`, `jm-theme/assets`, `jm-theme/theme.json`, or `jm-theme/fields.json` only when the user explicitly asks to edit that exact file.

## Portable References

This skill should be enough to work in a fresh or disposable HubSpot theme
workspace. Treat bundled references as the portable baseline:

- `references/page-rules.md` for protected-file, workbench, traffic-source, and
  validation rules.
- `references/landing-page-map.md` for template/live URL mapping and stable
  audit contracts, including phone numbers, portal IDs, form IDs, and geo audit
  rules.
- `references/audit-checklist.md` for detailed page audit passes.

A repo may contain local copies under `docs/`. If local docs exist and differ
from the bundled references, surface the discrepancy instead of silently
choosing one. Do not invent or re-derive live URLs, phone numbers, portal IDs,
or form IDs.

## Repo Discovery

Before working, inspect:

- `references/page-rules.md` and `references/landing-page-map.md` in this skill.
- Repo-local `docs/page-rules.md` and `docs/landing-page-map.md`, if present, as
  optional working copies or overrides to reconcile.
- `workbench/new-templates/` and `workbench/new-modules/` for draft artifacts.
- `hubspot-pulls/` for disposable fetched reference snapshots.
- `audits/` for disposable audit reports.

If these folders do not exist, create only the ones needed.

## Workflow Choice

Choose one workflow:

- **New template / A/B variant**: copy the nearest source template into `workbench/new-templates/`, edit there, then move or upload the finished new template when approved.
- **New module**: copy or create a module under `workbench/new-modules/`, keep module files together, then move or upload the finished new module when approved.
- **Live sync / audit**: fetch the live or preview URL, compare against the stable contracts and optional local template, and write findings to `audits/`.
- **Explicit live-file edit**: only edit the named existing `jm-theme` file when the user explicitly asks. Keep the diff narrow and verify the protected-tree change before finishing.
- **Upload**: provide or run `hs cms upload` only for the explicit artifact. Avoid `--clean` unless the user explicitly asks.

## Scripts

Use scripts from this skill directory when helpful:

```sh
python3 ~/.codex/skills/jm-hubspotlps/scripts/fetch_live_page.py <url> --out-dir hubspot-pulls
python3 ~/.codex/skills/jm-hubspotlps/scripts/audit_page.py --url <url> --template <template.html> --out audits/<name>.md
python3 ~/.codex/skills/jm-hubspotlps/scripts/compare_template_text.py --base <old.html> --candidate <new.html> --out audits/<name>.md
~/.codex/skills/jm-hubspotlps/scripts/protected_tree_check.sh --local
```

Read `references/audit-checklist.md` before doing a detailed landing-page audit.

## Safety Checks

For workbench-only or docs-only changes, use focused validation for the file being edited.

When editing any existing `jm-theme` file, run the local protected-tree check before finishing:

```sh
~/.codex/skills/jm-hubspotlps/scripts/protected_tree_check.sh --local
```

Before merge, commit review, or deploy, compare branch changes against `main`:

```sh
~/.codex/skills/jm-hubspotlps/scripts/protected_tree_check.sh --branch main
```

No output from the underlying git check means no existing protected file was modified, deleted, or renamed in that comparison.

## Traffic Rules

Default Facebook/Meta variants to no visible geo-personalized copy. Do not add Google Ads `loc_id` behavior or HubSpot GeoIP fallback that changes rendered Facebook copy unless the user explicitly asks.

Default Google variants to geo personalization when the source template supports it.

## Upload Pattern

Use this pattern for finished template uploads:

```sh
hs cms upload <local-template.html> JM/jm-theme/templates/<template-name.html> --cms-publish-mode publish
```

Use this pattern for finished module uploads:

```sh
hs cms upload <local-module.module> JM/jm-theme/modules/<module-name.module> --cms-publish-mode publish
```

Add `--account <account-name-or-id>` when the repo or user requires a specific HubSpot account.

## Output Discipline

Keep source changes in `jm-theme/`, `docs/`, or `workbench/`.

Write fetched HTML/text snapshots to `hubspot-pulls/`.

Write audit reports, diffs, screenshots, and findings to `audits/`.

Do not create a local `ab-tests/` folder by default. The A/B test lives in HubSpot; locally, the artifact is the new template or module variation.
