# mydoc-checkpoint

Update `overview/notes.md` at the project root by appending to its four checkpoint sections (`## Ideas`, `## Open threads`, `## Resolved`, `## AGENTS.md candidates`). Capture the *uncommitted* substance of this session: ideas surfaced but not acted on, threads opened but followed by other work, decisions that aren't yet reflected anywhere else, and items worth considering for `AGENTS.md`.

A future session reads the full `overview/` docs for project context, then uses those four sections to know what's still in flight.

## Bootstrap

`/mydoc-checkpoint` is self-sufficient — it never requires `/mydoc-overview` to have run first.

- If `overview/notes.md` is missing, create it (and the `overview/` directory if needed) with `# Notes` as the h1, `## Observations` followed by the placeholder line `(user observations / notes go here)`, then the four checkpoint section headings (`## Ideas`, `## Open threads`, `## Resolved`, `## AGENTS.md candidates`) empty.
- If `overview/notes.md` exists but is missing the `# Notes` h1, add it at the top.
- If `## Observations` is missing, add it with the placeholder `(user observations / notes go here)` immediately under `# Notes`.
- If any of the four checkpoint section headings is missing, add the missing heading(s) in canonical order at the bottom of the file. Don't reorder existing sections.
- Never write entries to `## Observations` — that section is user-directed and outside `/mydoc-checkpoint`'s scope. The scaffold placeholder is fine to write once; after that, only the user (or the agent at their request) adds content there.
- Scope is strictly `overview/notes.md`. Don't create `README.md` or the other `overview/` files (`how-it-works.md`, `codebase-map.md`) — that's `/mydoc-overview`'s job.

## When to update

- A substantive decision is made
- An idea surfaces that isn't immediately acted on
- A thread opens but another is followed first
- A previously-open thread is now resolved (mark it, move it — don't delete)
- An observation surfaces that belongs in `AGENTS.md`
- A long session is about to end

## Before writing

1. Read `overview/notes.md` so you don't duplicate entries.
2. Scan the current conversation for:
   - New ideas, observations, or surprises not already captured
   - Threads opened in this session and not yet closed
   - Existing Open threads that are now resolved in this session (look for explicit decisions or completion markers)
   - Items the user said or implied should go into `AGENTS.md`

## Writing rules

The four checkpoint sections are **append-only** with one exception: moving an Open thread to Resolved when it closes. Nothing else may be edited or deleted.

- Never write to `## Observations` — that section is user-directed and outside `/mydoc-checkpoint`'s scope.
- New entries append to the **bottom** of their section (chronological). Don't reorder existing ones.
- Each entry is a bulleted line.
- **Ideas:** name what's worth remembering and *why* (the implication, risk, or surprise). Not just the observation.
- **Open threads:** name what closing the thread looks like, so the next reader knows when it's done.
- **Resolved:** when a thread closes, append `— RESOLVED YYYY-MM-DD — <one-line resolution + pointer>` to the line and move it from `## Open threads` to `## Resolved`. Don't delete the original line; move it.
- **AGENTS.md candidates:** captured suggestions only. Never auto-write to AGENTS.md — the human decides whether to promote.
- Keep the four checkpoint section headings present even if a section is empty.

## After writing

Two outputs, in order:

1. **Summary line** — absolute path to `overview/notes.md` + one-line of what changed (e.g., `+2 ideas, +1 thread, marked 1 resolved, +1 AGENTS.md candidate`).

2. **Fresh-session prompt** — a copy-pasteable block the user can paste into a new session if they want to resume there. Ignorable if they're staying in the current session. Format:

       ---

       **Fresh-session prompt** (copy if starting a new session):

       Read every Markdown doc in `overview/` (relative to the project root; absolute fallback: `<absolute path to overview/>`) for full project context. Use `overview/notes.md` (absolute fallback: `<absolute path to overview/notes.md>`) to identify `## Ideas` and `## Open threads`. Next: <one-line concrete next action>.

       In your first response, orient briefly (≤200 words), then propose 2–4 concrete next-step options as A/B/C/D (one line each).

Rules for the fresh-session prompt:

- tell it to read the overview docs for context, with relative path /overview.
- give concise short summary of where we are for continuity of session  < 200 words.
- List 2–4 concrete next-step options as A/B/C/D (one line each). These should be specific and actionable, not vague or high-level. They should be the most logical next steps based on the updated notes, not just generic options. The user will pick one to continue with in the new session.

Nothing else after that.
