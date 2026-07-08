# Session transcripts

## Outline

### 2026-05-11 — 8496cc3c
**Topic:** Reframe `overview.md` with a clearer purpose statement and a "How it works" section.
- Read the project (`overview.md`, `outerloop-spec.md`, `my-verify-innerloop.md`, `innerloop/`, `research/`) and summarized purpose as inner/outer self-verification loops for AI coding agents.
- Drafted a reframed top blurb ("toolkit for dropping high-level self-verification into any project with one command") and a new `## How it works` section.
- Iterated on the section after feedback: clarified that installed hooks live in the project-level `.claude/`, listed the two commands maintained in this folder, and added a hook-to-script table naming each `.sh` file.
- Applied the edits to `overview.md` — reframed intro and inserted `## How it works` above `## What we have`.

---

## Session 2026-05-11 — 8496cc3c

**Session ID:** `8496cc3c-6178-455b-9fd5-6ff436bacce2`
**Resume:** `claude --resume 8496cc3c-6178-455b-9fd5-6ff436bacce2`

### Transcript

**You:**
> read the our project files tell me its purpose.

**Claude:**
Read `overview.md`, `outerloop-spec.md`, the start of `my-verify-innerloop.md`, and listed `innerloop/` and `research/`. Summarized the project as a self-verification harness for AI coding agents with two complementary loops: an inner loop (built) — a `/my-verify-innerloop` slash command that installs PostToolUse + Stop hooks running prettier/eslint/tsc and (optionally) vitest, gated by strict ESLint rules and a strict tsconfig; and an outer loop (spec'd, not yet built) — `/my-verify-outerloop`, a Builder-Verifier pattern that records every file Claude touches and refuses to let the agent stop unless a real E2E test (Playwright/pytest/Vitest) covers the change and passes. Noted that `my-verify-innerloop.md` is canonical here and symlinked into `~/.claude/commands/`, `innerloop/` holds the hook scripts, and `outerloop-spec.md` is the design doc for the next piece.

---

**You:**
> Update the overview.md to include:
> - A description of what this is, like the best way to describe it is that we're building a way to make it easy to implement high-level self-verification in my projects.
> - How it works, describing the scripts, the commands, and overall how it works.
> Does that make sense? show me here what your gonna add first. keep it concise

**Claude:**
Proposed two changes before editing. First, a reframed top blurb: "A toolkit for dropping high-level self-verification into any of my projects with one command. AI coding agents skip checks unless something forces them — this repo builds those forcing functions: hook scripts that run on every edit and at task end, installed by slash commands that adapt to the target project." Second, a new `## How it works` section (to sit above `## What we have`) describing the command file → hook script → settings.json flow, the PostToolUse vs Stop split, and where scripts live. Asked for confirmation before applying.

---

**You:**
> How it works doesn't include:
> 1. Clarify whether the doc Claude/Hooks is project-level or global. It should be project-level.
> 2. Will those just simply be the core ones that we have in this folder?
> 3. More importantly you didn't include the actual sh files that get run for each of those hooks.

**Claude:**
Revised the "How it works" draft to address all three. Made it explicit that installed hooks live in the project's local `.claude/` (not global `~/.claude/`), and that the commands themselves are global only because their `.md` files are symlinked into `~/.claude/commands/`. Listed the two slash commands maintained in this folder — `/my-verify-innerloop` (built, scripts in `innerloop/`) and `/my-verify-outerloop` (spec'd, scripts will live in `outerloop/`). Added a hook-to-script table naming the actual files: `post-edit-check.sh` / `stop-check.sh` for the inner loop and `post-edit-record.sh` / `stop-verify.sh` for the outer loop, with a one-line description of what each does. Asked for sign-off.

---

**You:**
> yes add it

**Claude:**
Applied the edit to `overview.md`: replaced the original two-sentence intro with the reframed blurb, and inserted the new `## How it works` section (including the hook/script table) above `## What we have`. The rest of the file (notes, "Next" section) is unchanged.
