# KM Ad Library Reference

## Read-Only Safety

The ad library is source material, not a workspace. Do not modify any files under:

- `/Users/jordanmamroud/mylab/km/ad-assets`
- `/Users/jordanmamroud/mylab/km/ad-library`

Do not run commands that move, rename, delete, rewrite, regenerate, reindex, or restructure the library. Do not run catalog builders, report generators, `UPDATE`, `INSERT`, `DELETE`, `DROP`, `CREATE`, or file writes inside the library paths. Use only read-only queries and inspection commands.

If an asset is needed for editing, copy it from `full_path` into a separate project/export/work directory outside the library, then edit the copy.

## Database

Open the library with:

```bash
sqlite3 /Users/jordanmamroud/mylab/km/ad-library/ad_library.sqlite
```

Useful one-shot pattern:

```bash
sqlite3 -header -column /Users/jordanmamroud/mylab/km/ad-library/ad_library.sqlite "SELECT ...;"
```

Use `SELECT` queries only. Schema inspection such as `.schema` or `PRAGMA table_info(...)` is acceptable.

## Core Tables

- `assets`: one row per asset. Most searches start here or in a view.
- `projects`: completed remodeling projects, with `proof_score` and capability tags.
- `asset_groups`: non-project groupings such as editors or UGC creators.
- `reference_sets`: finished ads grouped for pacing/template reference.
- `video_briefs`: AI-generated video summaries, suggested ranges, transcript status.
- `production_roles`: secondary video roles such as `testimonial_proof`, `transformation`, `b_roll`.
- `derivatives`: contact sheets, posters, transcripts, and other generated previews.

## Main Asset Columns

- `id`: stable asset id.
- `original_filename`: filename only.
- `relative_path`: path under raw asset root.
- `full_path`: absolute file path to use when opening/copying assets.
- `media_type`: `image`, `video`, `audio`, `document`, `logo/graphic`.
- `library_type`: `production`, `reference`, or `archive`.
- `primary_role`: examples: `before-after`, `testimonial`, `timelapse`, `project-photo`, `project-footage`, `ugc-hook`, `reference-ad`.
- `project_id`: canonical project slug such as `hoffert`, `liaw`, `shaton`.
- `group_id`: non-project source grouping such as `antonina`, `kristina`, `erica`.
- `duration`, `duration_seconds`: videos.
- `width`, `height`, `orientation`, `aspect_ratio`: images and videos.
- `preview_image_path`: contact sheet or preview where available.
- `tags_json`: generated tags; safe to search with `LIKE`.

## Views

- `v_production_assets`: all usable source ingredients for new ads.
- `v_reference_ads`: finished ads for reference only.
- `v_archive_assets`: docs/misc/support files.
- `v_projects_with_before_afters`: projects with before/after image assets.
- `v_projects_with_before_after_and_testimonial`: projects with before/after plus testimonial.
- `v_production_videos`: production videos only.
- `v_production_photos`: production images only.
- `v_before_after_photos`: production images where `primary_role='before-after'`.
- `v_timelapse_videos`: production videos where `primary_role='timelapse'`.
- `v_assets_needing_transcript`: videos whose transcript is not generated.

## Discovery Queries

List strong project candidates:

```sql
SELECT id, proof_score, asset_count, capability_tags_json
FROM projects
ORDER BY proof_score DESC, asset_count DESC, id;
```

Fuzzy project or filename search:

```sql
SELECT id, original_filename, primary_role, media_type, project_id, duration, width, height, full_path
FROM assets
WHERE lower(original_filename) LIKE '%hoffert%'
   OR lower(relative_path) LIKE '%hoffert%'
   OR project_id = 'hoffert'
ORDER BY library_type, primary_role, original_filename;
```

List all production assets for one project:

```sql
SELECT id, original_filename, primary_role, media_type, duration, width, height, full_path
FROM v_production_assets
WHERE project_id = 'hoffert'
ORDER BY primary_role, media_type, original_filename;
```

## Before/After Search

Start broad:

```sql
SELECT id, original_filename, width, height, orientation, aspect_ratio, full_path
FROM v_before_after_photos
WHERE project_id = 'hoffert'
ORDER BY
  CASE
    WHEN lower(original_filename) LIKE '%before%' THEN 0
    WHEN lower(original_filename) LIKE '%after%' THEN 1
    ELSE 2
  END,
  original_filename;
```

Find explicit before/after tokens across all projects:

```sql
SELECT project_id, original_filename, width, height, orientation, full_path
FROM v_before_after_photos
WHERE lower(original_filename) LIKE '%before%'
   OR lower(original_filename) LIKE '%after%'
ORDER BY project_id, original_filename;
```

Pairing heuristic:

- Same `project_id` is required unless the user explicitly asks to mix projects.
- Prefer filenames that share the same stem with only `before`/`after` changed.
- Prefer matching `orientation` and similar `width`/`height`.
- Prefer raw high-resolution project photos over landing-page thumbnails when ad quality matters.
- If only numbered shoot files exist, inspect thumbnails/contact sheets or use image view before choosing.

## Proof Set Search

Find before/after, testimonial, and timelapse assets for a project:

```sql
SELECT id, original_filename, primary_role, media_type, duration, width, height, preview_image_path, full_path
FROM v_production_assets
WHERE project_id = 'hoffert'
  AND primary_role IN ('before-after', 'testimonial', 'timelapse', 'project-photo', 'project-footage')
ORDER BY
  CASE primary_role
    WHEN 'before-after' THEN 0
    WHEN 'testimonial' THEN 1
    WHEN 'timelapse' THEN 2
    ELSE 3
  END,
  original_filename;
```

Find projects with fuller proof sets:

```sql
SELECT id, proof_score, asset_count, capability_tags_json
FROM projects
WHERE capability_tags_json LIKE '%project-has:before-after%'
ORDER BY proof_score DESC, asset_count DESC;
```

## Video Search

Timelapses:

```sql
SELECT id, original_filename, project_id, duration, width, height, orientation, full_path
FROM v_timelapse_videos
ORDER BY project_id, original_filename;
```

Testimonials:

```sql
SELECT v.id, v.original_filename, v.project_id, v.duration, b.transcript_status, b.ai_summary, v.full_path
FROM v_production_videos v
LEFT JOIN video_briefs b ON b.asset_id = v.id
WHERE v.primary_role = 'testimonial'
ORDER BY v.project_id, v.original_filename;
```

Video contact sheets/posters:

```sql
SELECT a.original_filename, d.derivative_type, d.path, d.status
FROM assets a
JOIN derivatives d ON d.asset_id = a.id
WHERE a.id = 'c32ad74752c8'
ORDER BY d.derivative_type;
```

## Reference Ads

Use these for edit structure, not source footage:

```sql
SELECT original_filename, group_id, collection_id, duration, orientation, aspect_ratio, full_path
FROM v_reference_ads
WHERE lower(original_filename) LIKE '%learn%'
   OR tags_json LIKE '%usage:hook-reference%'
ORDER BY group_id, original_filename;
```

## Reporting Back

When answering asset search requests, include:

- The selected `full_path` values.
- The project and role tags used.
- Any uncertainty, such as multiple plausible image pairs.
- A concrete next step, such as opening files, exporting variants, or asking the user to choose between a short list.
