---
description: Create or update BEDTIME.md so a fresh session can resume this work exactly where it left off
disable-model-invocation: true
---

Create or update `BEDTIME.md` in the current project root. If it already exists, overwrite it with the current state — do not append.

Goal: a future session (or the user after sleep, a crash, or a closed terminal) can read this file and resume without re-deriving context.

## Before writing

Gather context from:
- Recent conversation in this session (what was just being worked on, decisions made, things tried).
- `git status`, `git diff`, and `git log -10` if it's a git repo.
- Any obviously in-progress files (uncommitted changes, files mentioned in conversation).

## Required sections, in this order

1. **Current version** — Which version are we on (e.g., V0, V1)? State your best inference. If unclear, write your guess and flag the uncertainty explicitly.

2. **What "done" looks like for this version** — *This is the most important section.* A concrete description of the finished state of the version currently being worked on: what features exist, what behavior ships, what the user can do once complete. Specific enough that a fresh session knows when to stop.

3. **Where we are right now** — Progress against the "done" definition above. What's built, what's partially built, what hasn't been started. Reference real file paths and function/component names.

4. **Next steps** — Ordered list of what to do next. Concrete enough that a fresh session can act without re-deriving context. Include file paths, function names, and the specific change to make at each step.

5. **Open issues, questions, and context the user might be forgetting** — Anything the user didn't explicitly mention but you think matters: unresolved decisions, blockers, ideas they floated, edge cases not yet handled, questions you have for them. This section is for the things they'd kick themselves for forgetting.

## Style

- Be specific. "Finish the auth flow" is useless. "Wire `src/routes/auth.ts` to call `validateSession()` on POST and redirect to `/dashboard` on success" is useful.
- Write for someone with zero session memory. Don't reference "what we discussed" — say what was discussed.
- If you genuinely don't know something (e.g., which version we're on), write what you do know and mark gaps with `// TODO: confirm with user`.

## After writing

Tell the user the absolute path to `BEDTIME.md` and a one-line summary of what's in it. Nothing else.
