# General Video Catalog Guidance

Use this for non-testimonial or unclear Kitchen Magic videos.

Keep the Gemini prompt short:

```text
Create a catalog for this {video_type} video. Include: full transcript if there is speech; timestamped shot list with visual description and transcript or visual notes for each segment; strong usable moments with timestamps; ad planning notes.
```

Do not remove the Gemini transcript request. Run OpenAI `gpt-4o-transcribe` separately as a hidden confidence check, then output one selected transcript with a short confidence/review note.

After Gemini returns, normalize the shot list into roomy blocks: `### timestamp`, blank line, plain `Visual: ...`, blank line, plain `Transcript: ...`. Do not keep dense inline bullets.

Prioritize:

- Clear visual sequence.
- Before/after, transformation, product detail, or brand moments.
- Timestamped moments that can later be found and cut during ad planning.
- Honest uncertainty when speech or visuals are unclear.
