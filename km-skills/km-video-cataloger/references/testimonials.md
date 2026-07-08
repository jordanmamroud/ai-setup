# Testimonial Catalog Guidance

Use this for Kitchen Magic testimonial videos.

Keep the Gemini prompt short:

```text
Create a catalog for this testimonial video. Include: full transcript as one paragraph; timestamped shot list with visual description and word-for-word transcript for each segment; strong quotes with timestamps; ad planning notes.
```

Do not remove the Gemini transcript request. Run OpenAI `gpt-4o-transcribe` separately as a hidden confidence check, then output one selected transcript with a short confidence/review note.

After Gemini returns, normalize the shot list into roomy blocks: `### timestamp`, blank line, plain `Visual: ...`, blank line, plain `Transcript: ...`. Do not keep dense inline bullets.

Prioritize:

- Word-for-word customer language.
- Clear recommendation, trust, quality, professionalism, convenience, storage, cleaning, and transformation claims.
- Visual moments that match or strengthen the spoken point.
- Notes that help later ad planning without cutting clips yet.
