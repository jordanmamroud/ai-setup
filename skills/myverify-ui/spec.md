# spec — ui-verify family

## Current focus: a fast deterministic checker (working name: `ui-check`)

**The problem.** `ui-verify` takes ~25 min per run. That's fine as a pre-commit gate but unworkable as the inner-loop signal an agent uses while iterating on a feature.

**The fix.** Add a *separate* sibling tool. The two coexist; neither replaces the other.

- **`ui-verify`** (existing) → exploratory, LLM-driven, open-ended. Runs at pre-commit.
- **`ui-check`** (new) → deterministic, no LLM in the loop. Runs during development.

**How `ui-check` works.**

1. The build agent (main Claude session) writes a Playwright test file describing the behaviour it just built.
2. `ui-check <path-to-test>` runs that file via Playwright and returns:
   - pass/fail
   - short error trace on failure (one failing assertion + the relevant lines, not the full reporter dump)
3. That's the entire job. No exploration, no judgement, no LLM call.

**Why this is fast.** No agentic loop. A single Playwright spec runs in seconds. The cost moves from "25 min every iteration" to "one-time test-writing cost + seconds per iteration."

**Where test files live.** Project's own Playwright suite (e.g. `tests/`, `e2e/`). They become real artifacts that also run in CI — not throwaway temp files.

**Relationship to existing `ui-verify`.**

- Pre-commit / final-check pass: `ui-verify` (catches things the agent didn't think to test).
- Inner-loop iteration: `ui-check` (fast feedback on the specific thing being built).
- Neither blocks the other. Both live in this folder.

**Success criteria (what "done" means for v1 of `ui-check`).**

- [ ] `ui-check <test-file>` runs in under 60s for a typical single-spec file.
- [ ] Output is concise enough for an LLM to consume without truncation (pass line + ≤20-line failure trace).
- [ ] Works in a project that already has Playwright installed; clear error message if not.
- [ ] Per-run history logged in the same shape as `ui-verify` (jsonl index + per-run dir).
- [ ] Installed via symlink pattern parallel to `ui-verify`: `~/bin/ui-check` → this folder.
- [ ] Slash command `/my-uicheck` mirrors `/my-uiverify`.

**Open questions (resolve before building).**

- Naming: `ui-check` vs `ui-test` vs something else.
- Does the tool need to be a script at all, or is `npx playwright test <file>` + a tiny output filter enough?
- Should the agent's brief include the test file path only, or also a one-line "what this test covers" note for history?
- What happens when the project has no Playwright setup? Refuse, or scaffold?

---

## Background: the existing `ui-verify`

`ui-verify` (shipped, in daily use) is the Claude-side bash bridge that spawns a sub-agent with scoped Playwright MCP, an explicit system prompt, and per-run history. See `README.md` for the full spec and `STATUS.md` for current state.

It exists to give a main Claude session a way to ask "does this UI feature actually work end-to-end?" without the main agent driving the browser itself. It's intentionally open-ended — the verifier figures out *what* to check, not just *whether* a specific assertion passes.

That open-endedness is what makes it slow, and what makes it valuable as a pre-commit safety net.
