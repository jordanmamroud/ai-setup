---
name: km-video-cataloger
description: Retrieve or create Kitchen Magic video catalogs. Use when Codex needs to get an existing video transcript, shot list, strong quotes, or ad-planning notes from analysis__catalog.md, or create/update that catalog beside a KM library video using Gemini video analysis plus OpenAI gpt-4o-transcribe as a hidden transcript confidence check.
---

# KM Video Cataloger

## Core Rules

- Use the `GEMINI_API_KEY` environment variable for Gemini.
- Never print, log, echo, or ask the user to paste `GEMINI_API_KEY`.
- If `GEMINI_API_KEY` is missing, tell the user the shell/session needs to load it from `~/.zshrc`.
- Use the `OPENAI_API_KEY` environment variable for OpenAI transcription.
- Never print, log, echo, or ask the user to paste `OPENAI_API_KEY`.
- If `OPENAI_API_KEY` is missing, tell the user the shell/session needs to load it from `~/.zshrc`.
- Keep Gemini prompts short and direct.
- Keep Gemini returning its own transcript; do not remove transcript requests from the Gemini prompt.
- Use OpenAI `gpt-4o-transcribe` as a hidden speech-transcription confidence check.
- Catalog only. Do not cut clips, move files, rename sources, or modify source videos.
- Do not transcode source videos for library output. Temporary audio extraction/compression under `/tmp` for OpenAI transcription is allowed when needed for upload safety; delete temporary files after use.
- Treat `analysis__catalog.md` as the canonical per-video catalog file.
- Read an existing `analysis__catalog.md` before calling Gemini or OpenAI.
- Save catalog files beside the source video when it is already in a per-video folder.
- Save only the final catalog by default; do not keep raw transcription sidecar files unless the user asks or there is a meaningful mismatch to audit.

## Workflow

1. Identify the source video path from the user's request or by querying the KM library index.
2. Resolve the expected catalog path:
   - Testimonial/timelapse from the KM index: prefer the category placement video path from `asset_placements.folder_key='testimonials'` or `asset_placements.folder_key='timelapses'`, then save/read `<placement-video-folder>/analysis__catalog.md`.
   - Per-video folder: `<video-folder>/analysis__catalog.md`
   - Flat source fallback: `<source-folder>/Catalogs/<source-video-stem>/analysis__catalog.md`
3. If the user gives a canonical `remodels` video path for a testimonial/timelapse, query `km-library.sqlite` by `assets.full_path` or `asset_placements.full_path` and switch to the matching category placement when it exists. Do not create duplicate catalogs under `remodels` when a per-video `testimonials` or `timelapses` folder exists.
4. If `analysis__catalog.md` exists, read it and answer from the relevant section. Do not regenerate unless the user explicitly asks or the file lacks the requested section.
5. If no catalog exists, identify the video type from its folder, filename, indexed role, or content.
6. Read the relevant reference:
   - Testimonial videos: `references/testimonials.md`
   - Other or unclear videos: `references/general.md`
7. Ask Gemini to produce a video catalog using the relevant reference prompt. Gemini should still return its own transcript.
8. Run OpenAI `gpt-4o-transcribe` on the same source video as an independent speech transcript check using the upload-safe workflow below.
9. Choose one final transcript for `analysis__catalog.md`:
   - Prefer Gemini when both transcripts broadly agree, because Gemini also has visual context.
   - Use OpenAI when it is clearly more accurate or cleaner overall.
   - Make only obvious phrase-level corrections when the two transcripts and video context make the correction clear.
   - Do not expose both full transcripts by default.
10. Build the final `analysis__catalog.md` with one selected transcript, a concise confidence/review note, Gemini's shot list, strong quotes, and ad planning notes.
   - If Gemini returns bold labels such as `**Full Transcript:**` instead of Markdown headings, normalize them into the required final section structure.
11. Review the catalog for obvious gaps: missing selected transcript, missing confidence note, missing timestamps, shot-list items without visuals, or transcript segments that are summaries instead of word-for-word speech.
12. If Gemini misses required visual sections, ask Gemini once for a corrected catalog using the same prompt shape. If OpenAI transcription fails or is unavailable, say so clearly and mark transcript confidence as lower.

## OpenAI Transcription Check

Use the OpenAI transcription API with `gpt-4o-transcribe`. OpenAI file uploads are limited to 25 MB, so do not assume a KM source video can be uploaded directly. Prefer a temporary compressed audio extract for video sources.

Create the temporary audio outside the library, transcribe that file, then delete it:

```bash
source="/path/to/source__video.mp4"
tmpdir="$(mktemp -d /tmp/km-openai-transcribe.XXXXXX)"
trap 'rm -rf "$tmpdir"' EXIT

audio="$tmpdir/audio.m4a"
ffmpeg -v error -y -i "$source" -vn -ac 1 -ar 16000 -b:a 64k "$audio"

bytes="$(wc -c < "$audio" | tr -d ' ')"
if [ "$bytes" -ge 25000000 ]; then
  echo "Temporary audio is still over OpenAI's 25 MB upload limit; compress further or split into sentence-aware chunks." >&2
  exit 1
fi

curl --silent --show-error --fail-with-body \
  --request POST \
  --url https://api.openai.com/v1/audio/transcriptions \
  --header "Authorization: Bearer $OPENAI_API_KEY" \
  --header "Content-Type: multipart/form-data" \
  --form file=@"$audio" \
  --form model=gpt-4o-transcribe \
  --form response_format=text
```

If the compressed audio is still too large, lower the bitrate or split the temporary audio into chunks under 25 MB. Avoid splitting mid-sentence when practical because that can lose transcription context.

Capture the transcript text for comparison only. Do not print the API key, and do not keep the raw transcript file unless the user asks or there is a meaningful mismatch to audit.

## Required Final Catalog Structure

Use this exact section order:

Normalize the shot list into roomy Markdown blocks. Do not use compact bullets with inline bold labels for `Visual` and `Transcript`.

```md
# Video Catalog

Source: `source__example.mp4`

## Transcript

One selected transcript as a continuous paragraph.

## Transcript Confidence

- State which source was selected and why. If there are meaningful disagreements, include only the disputed phrase(s), not both full transcripts.

## Shot List

### HH:MM:SS-HH:MM:SS
Visual: ...
Transcript: "..."

### HH:MM:SS-HH:MM:SS
Visual: ...
Transcript: "..."

## Strong Quotes

- HH:MM:SS-HH:MM:SS: "..."

## Ad Planning Notes

- ...
```

For videos without speech, replace transcript sections with concise notes that say there is no spoken transcript, and make the shot list visual-first.

## Output Location

When the source video is in a per-video folder:

```text
<video-folder>/
  source__<original-filename>.mp4
  analysis__catalog.md
```

When the source video is still flat, do not restructure it. Save to:

```text
<source-folder>/Catalogs/<source-video-stem>/
  analysis__catalog.md
```

Only save optional raw sidecar files such as `analysis__openai-transcript.txt` when the user asks for audit artifacts or when the transcript comparison shows a meaningful mismatch.

## Quality Bar

- Gemini and OpenAI transcripts should each be readable as one paragraph for fast review/search.
- Treat Gemini as the visual catalog plus primary transcript when it is clearly more accurate; use OpenAI as the independent speech-transcription confidence check.
- Differences do not need to be exhaustive punctuation diffs; focus on wording that could affect ad copy or quote selection.
- The final catalog should show one `## Transcript`, not separate Gemini and OpenAI transcript sections.
- The shot list should be easy to scan: each shot gets its own `### timestamp` heading, a blank line, a `Visual:` line, a blank line, and a `Transcript:` line.
- Use plain `Visual:` and `Transcript:` labels in shot-list blocks. Do not bold those labels.
- Do not leave shot-list entries as dense bullets such as `* **0:00 - 0:04:** **Visual:** ... **Transcript:** ...`.
- The shot list should explain what is visually happening, not only what is said.
- Shot-list transcript text should be word-for-word whenever speech is present.
- Strong quotes should be useful for ad planning and include timestamps.
- Do not invent details that are not visible or audible in the video.
