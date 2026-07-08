---
name: km-ad-library
description: >
  Read-only search and navigation for the local Kitchen Magic ad asset library.
  Use this whenever the user asks for ad library assets, Kitchen Magic production
  assets, before/after photos, testimonials, timelapses, project visuals,
  reference ads, proof sets, asset paths, or asks you to "find one" without
  manually providing files. Always query the local SQLite library before asking
  the user for an asset. Never move, rename, delete, rewrite, regenerate,
  reindex, restructure, or otherwise modify the ad library or its media/catalog
  files. Copy assets out of the library before editing.
---

# KM Ad Library

## Core Rule

Query the local library before asking the user for asset choices. Ask only after you have searched and found either no plausible match or multiple plausible creative choices that require human preference.

## Non-Negotiable Read-Only Rule

Treat the ad library as a read-only source. Do not modify anything under:

- `/Users/jordanmamroud/mylab/km/ad-assets`
- `/Users/jordanmamroud/mylab/km/ad-library`

Forbidden actions include moving, renaming, deleting, editing, compressing, transcoding in place, creating derivatives in place, changing Finder tags, rebuilding SQLite, regenerating JSON catalogs, updating reports, or restructuring folders.

Allowed actions:

- Read/query metadata.
- Inspect/open media.
- Copy assets out of the library into a separate working/export location.
- Create new edited/exported files only outside the library, unless the user starts a separate explicit maintenance task that is not using this skill.

## Library Locations

- Workspace root: `/Users/jordanmamroud/mylab/km`
- SQLite index: `/Users/jordanmamroud/mylab/km/ad-library/ad_library.sqlite`
- Raw media root: `/Users/jordanmamroud/mylab/km/ad-assets/raw`
- Derived previews: `/Users/jordanmamroud/mylab/km/ad-assets/derived`
- Browser report: `/Users/jordanmamroud/mylab/km/ad-library/reports/library-browser.html`

Treat SQLite as the searchable source of truth for asset metadata. Media files are referenced by absolute `full_path` values.

## Workflow

1. Start with SQLite queries against the views listed in `references/library-reference.md`.
2. Run only read-only database operations such as `SELECT` and schema inspection.
3. Prefer `library_type='production'` assets for new ad ingredients.
4. Use `reference` assets only for pacing, structure, hook, offer, or CTA inspiration unless the user explicitly asks for finished ads.
5. Use `project_id`, `primary_role`, `media_type`, `tags_json`, filename text, duration, dimensions, and preview paths to narrow candidates.
6. Inspect actual media when selection quality matters: use image viewing for photos/contact sheets, `ffprobe` for video metadata, and `open` when the user needs to watch a clip.
7. Return concrete asset paths and explain why each was selected.
8. If work requires edits, duplicate selected assets to a non-library destination first.

## Common Tasks

Use `references/library-reference.md` for exact schema and query examples.

- Find before/after assets: query `v_before_after_photos` by project or fuzzy filename, then pair files by shared project and before/after filename tokens.
- Find a proof set: combine before/after photos with `v_production_videos` rows where `primary_role` is `testimonial` or `timelapse`.
- Find process/transformation footage: query `v_timelapse_videos`, then filter by project, room, duration, orientation, or filename.
- Find testimonials: query `v_production_videos` where `primary_role='testimonial'`; check transcript status in `video_briefs` if quote extraction matters.
- Find reusable project visuals: query `v_production_assets` with `primary_role IN ('project-photo','project-footage')`.
- Find reference ads: query `v_reference_ads`; do not confuse these with production source footage.

## Selection Guidance

For before/after photo pairs, prefer:

1. Same `project_id`.
2. Obvious filename pair, such as `before` and `after`, `lp-before` and `lp-after`, or same numbered project shoot naming.
3. Matching orientation or compatible aspect ratio.
4. Higher resolution source files over landing-page thumbnails when ad quality matters.
5. A concise shortlist with paths when the "best" pair is subjective.

Never invent missing assets. If no match exists, say what was searched and what was absent.
