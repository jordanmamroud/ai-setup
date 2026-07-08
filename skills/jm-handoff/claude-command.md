---
name: jm-handoff
description: Write a handoff document to .tmp/handoffs/ in the current repo so a new session can continue this work, then print a concise continuation prompt.
disable-model-invocation: true
---

# jm-handoff

Capture the current session's work into a handoff document so a fresh session can pick up exactly where this one left off.

## Steps

1. **Find the repo root** of the project where this session is working (`git rev-parse --show-toplevel`; if not a git repo, use the current working directory).

2. **Ensure the folder exists**: create `<repo-root>/.tmp/handoffs/` if it doesn't already exist.

3. **Write the handoff doc** to `.tmp/handoffs/<task-slug>.md`, where `<task-slug>` is a short kebab-case name for the task (e.g. `fix-auth-redirect.md`, `refactor-billing-hooks.md`). If a file with that name already exists, overwrite it — it's the same task, updated. Include:
   - **Task** — one or two sentences: what we're working on and why.
   - **Current state** — what's done, what's in progress, what's verified vs. untested.
   - **Key decisions** — choices made during the session and the reasoning, so the next session doesn't re-litigate them.
   - **Files touched** — paths of files created/modified/deleted, with a phrase on what changed in each.
   - **Next steps** — the concrete remaining work, in order, starting with the very next action.
   - **Gotchas** — anything surprising learned along the way (weird APIs, failing tests, env quirks).

   Write it for a reader with zero context from this conversation. Prefer specifics (paths, names, commands) over summaries.

4. **Print the continuation prompt.** After writing the file, output a short copy-paste prompt for the next session, clearly set off in a code block. Format:

   ```
   Read .tmp/handoffs/<task-slug>.md and continue the work. Next up: <one-line very next action>.
   ```

   Keep it to one or two sentences — the detail lives in the handoff file, not the prompt.
