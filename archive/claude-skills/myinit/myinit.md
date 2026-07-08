---
description: Initialize the current project with the standard mygeorge layout (CLAUDE.md with behavioral guidelines, spec.md, CHECKPOINT.md, BEDTIME.md)
disable-model-invocation: true
---

Initialize the current project directory with the standard layout. **Run from the project root.**

For each step, act only if the condition matches. Don't overwrite or modify content beyond what's specified.

## 1. CLAUDE.md

Check if `./CLAUDE.md` exists.

- **If it doesn't exist:** create it with the BEHAVIORAL_GUIDELINES_TEMPLATE below as the entire content.
- **If it exists:** check whether the file contains a section header `## Behavioral guidelines` (case-insensitive match on the heading line itself).
  - **If not:** append the BEHAVIORAL_GUIDELINES_TEMPLATE to the end of the file. Add a single leading blank line if the file doesn't already end in one.
  - **If yes:** leave the file untouched.

### BEHAVIORAL_GUIDELINES_TEMPLATE

The exact content to use. Everything between `---BEGIN TEMPLATE---` and `---END TEMPLATE---` is verbatim file content. Do not include the markers themselves.

---BEGIN TEMPLATE---
## Behavioral guidelines

Guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** these guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think before coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing.

## 2. Simplicity first

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that *your* changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

## 4. Goal-driven execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.
---END TEMPLATE---

## 2. spec.md

If `./spec.md` doesn't exist, create it as an empty file. If it exists, leave it alone.

## 3. CHECKPOINT.md

If `./CHECKPOINT.md` doesn't exist, create it as an empty file. If it exists, leave it alone.

## 4. BEDTIME.md

If `./BEDTIME.md` doesn't exist, create it as an empty file. If it exists, leave it alone.

## After completing

Report what was done. One line per file. Format:
- `created CLAUDE.md (with behavioral guidelines)` / `appended behavioral guidelines to CLAUDE.md` / `skipped CLAUDE.md (already has behavioral guidelines)`
- `created spec.md` / `skipped spec.md (already exists)`
- ... same for CHECKPOINT.md and BEDTIME.md.

Nothing else after the report.
