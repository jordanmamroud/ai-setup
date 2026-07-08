---
name: km-video-clipper
description: Select and trim raw Kitchen Magic video clips using Gemini video analysis and ffmpeg. Use when Codex needs to analyze a KM library video, recommend 3-5 ranked timestamp options for a requested clip duration, ask the user to choose, then cut only the selected raw clip while preserving the original source video.
---

# KM Video Clipper

## Core Rules

- Use the `GEMINI_API_KEY` environment variable for Gemini.
- Never print, log, echo, or ask the user to paste `GEMINI_API_KEY`.
- If `GEMINI_API_KEY` is missing, tell the user the shell/session needs to load it from `~/.zshrc`.
- Keep Gemini prompts short.
- Do not auto-cut after analysis. Ask the user to choose an option first.
- Treat the requested duration as approximate. Allow about 1 second shorter or longer when needed to complete a spoken phrase cleanly.
- Cut raw clips only: no captions, styling, music changes, overlays, resizing, color work, or edits beyond trimming.
- Keep original source videos untouched.
- Do not move, rename, or restructure source videos unless the user explicitly asks for a library-maintenance migration.

## Workflow

1. Identify the source video path from the user's request or by querying the KM library index.
2. Identify the video type from its folder, filename, indexed role, or visual content.
3. Read the relevant reference:
   - Testimonial videos: `references/testimonials.md`
   - Other or unclear videos: `references/general.md`
4. Ask Gemini for 3-5 ranked timestamp options near the requested duration.
5. Present the options with transcript first, then rank, timestamps, duration, rationale, and suggested use.
6. Ask the user which option to cut or whether to adjust the search.
7. After the user chooses, cut only that raw clip with `ffmpeg`.
8. Save the analysis notes and resulting clip beside the source video according to the layout rules below.

## Gemini Prompt Shape

Use the reference file to choose the video-type phrase, then keep the prompt close to:

```text
Find the best raw clips from this {video_type} video to use in a Facebook ad. Each clip should be about {duration}, with 1 second flexibility if needed to finish a phrase. Return 3-5 ranked timestamp options with transcript, rationale, and suggested use.
```

Do not add a long rubric unless the user asks for more control or the first result is poor.

## Output Format

Before cutting, present 3-5 ranked options:

```text
1. HH:MM:SS-HH:MM:SS (approx. Ns)
   Transcript: "..."
   Rationale: ...
   Suggested use: ...
```

Make the transcript the easiest part to scan. It is the main review signal for testimonial clips.

If Gemini returns vague timestamps or transcript snippets that do not fit the selected timestamp range, ask it once for exact start/end timestamps and matching transcript text before presenting options.

## File Layout

When the source video is already inside a per-video folder, write outputs beside the source:

```text
<video-folder>/
  source__<original-filename>.mp4
  clip-01__HH-MM-SS_to_HH-MM-SS.mp4
  analysis__clip-options__YYYY-MM-DD.md
```

When the source video is still flat in a folder, do not restructure it during clipping. Use:

```text
<source-folder>/Clips/<source-video-stem>/
  clip-01__HH-MM-SS_to_HH-MM-SS.mp4
  analysis__clip-options__YYYY-MM-DD.md
```

## Clip Naming

Use:

```text
clip-##__HH-MM-SS_to_HH-MM-SS.mp4
```

Keep purpose labels such as `facebook-ad`, `hook`, or `testimonial` out of the filename.

## ffmpeg Rules

- Use the selected timestamps exactly unless the user asks for adjustment or a phrase clearly needs up to 1 second on either side to avoid a clipped word.
- Prefer stream copy for raw fast clipping when it cuts cleanly.
- If stream copy creates an inaccurate cut, re-run with normal encoding and no other edits.
- Never overwrite an existing clip. If a filename exists, increment the clip number.

Example command shape:

```bash
ffmpeg -y -ss HH:MM:SS -to HH:MM:SS -i SOURCE.mp4 -map 0 -c copy OUTPUT.mp4
```

Use `-y` only after confirming the output path is new.
