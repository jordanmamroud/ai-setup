# General Video Guidance

Use this for non-testimonial or unclear Kitchen Magic videos.

Keep the Gemini prompt short:

```text
Find the best raw clips from this {video_type} video to use in a Facebook ad. Each clip should be about {duration}, with 1 second flexibility if needed for a clean start or end. Return 3-5 ranked timestamp options with transcript or visual moment, rationale, and suggested use.
```

Choose `{video_type}` plainly, such as `timelapse`, `remodel footage`, `finished ad`, `UGC`, or `Kitchen Magic`.

Prefer clips with:

- Immediate visual clarity.
- Strong before/after, transformation, product detail, or brand moment.
- A clean start and end point.
- Minimal dead time.

For videos without speech, use `Visual moment` instead of `Transcript` in the returned options.
