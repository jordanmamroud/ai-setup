---
description: Generate 5 rule variants AND run them through Codex CLI in parallel, then report which variant performed best. Asks for intended outcome + test task before running. Uses the jm-writer rewriter rules.
disable-model-invocation: true
---

You are running the jm-writer rewriter bake-off loop.

## Steps

1. **Check `$ARGUMENTS` is non-empty.** If empty, tell the user briefly to pass text after `/myloop` (example: `/myloop Don't use mocks in tests`) and stop.

2. **Read the rewriter rules** from `/Users/jordanmamroud/GitHub/jm-writer/CLAUDE.md`. These define pre-passes, decision rule, the five explicitness axes, principles every rewrite must embody, and what NOT to do.

3. **Apply the pre-passes** to `$ARGUMENTS`:
   - Classify the rule as **invariant** (safety, correctness, format, security boundary) or **judgment** (style, prioritization, coverage, "thoroughness"). Surface the classification to the user — it determines the v5 ceiling.
   - Reformulate negations where possible.
   - Surface any contradictions you spot.
   - Concretize vague triggers.
   - Verify the input is **<300 words**. If ≥300 words, tell the user to use `/mywriter` instead (which produces a single rewrite for long inputs) and stop.

4. **Ask the user two questions** in chat, then **stop and wait for their reply** before doing anything else:

   - **Intended outcome**: if a Codex agent followed this rule perfectly, what would its output look like or do? What's the success criterion you'll judge variants by?
   - **Test task**: what task should Codex be asked to perform, in a context where this rule should apply? (Same task is used for all 5 variants — apples-to-apples.)

   Tell the user that once they reply with both, you'll generate 5 variants, set up a session dir at `~/.cache/myloop/<timestamp>/`, run all 5 in parallel through Codex CLI (`gpt-5.5` at `reasoning.effort=high`, against sandboxed copies of `/Users/jordanmamroud/GitHub/llm-playground/` — the original is never touched), then analyze the outputs against the intended outcome.

5. **Once the user replies** with the intended outcome and test task, do the following in order:

   a. **Create the session directory.** Use `date +%Y%m%d-%H%M%S` for the timestamp. Path: `~/.cache/myloop/<timestamp>/`.

   b. **Write to the session dir:**
      - `intended-outcome.md` — the user's intended outcome, verbatim.
      - `test-task.md` — the user's test task, verbatim.
      - `variants/v1.md`, `v2.md`, `v3.md`, `v4.md`, `v5.md` — the 5 variants per the rewriter spec. **File contents: ONLY the variant rewrite text** (no `**vN**` labels, no "what changed" notes — each file should be ready to drop in as the content of `AGENTS.md`).

   c. **Print the 5 variants to chat** in standard `/mywriter` format (with `**vN** — <one-line note>` labels and the rewrite text), so the user can see what's about to be tested.

   d. **Tell the user the bake-off is starting** and that 5 parallel `codex exec` runs are about to spawn against sandboxed copies of llm-playground/. Give the session dir path so they can browse it during/after.

   e. **Run the bake-off:** `bash /Users/jordanmamroud/GitHub/jm-writer/scripts/bakeoff.sh <session-dir>`. This blocks until all 5 finish (or hit the 1800s per-variant timeout). Stream its output to the user so they can see progress.

   f. **After it returns, read:**
      - `<session-dir>/status/v1`..`v5` (each contains: `done` | `error` | other)
      - `<session-dir>/outputs/v1.md`..`v5.md` (Codex's final assistant text per variant)
      - `<session-dir>/errors/v1.err`..`v5.err` (only if status != `done`)

6. **Analyze the outputs against the intended outcome:**
   - For each variant: a one-paragraph judgment of how well its Codex output matched the intended outcome. Be specific about what the rule was trying to make Codex do and whether the output reflects that. Quote relevant excerpts from the output if helpful.
   - Flag any variant whose status is not `done` (errored or timed out) — read its `errors/vN.err` to summarize what went wrong.
   - Pick a **winner** — the variant whose output came closest to the intended outcome — and explain why in 2–3 sentences. If multiple are tied or none clearly won, say so explicitly.

7. **Print artifact paths** at the end so the user can browse:
   - Session dir: `~/.cache/myloop/<timestamp>/`
   - Variants: `<session-dir>/variants/`
   - Codex outputs: `<session-dir>/outputs/`
   - Sandboxed run dirs (for debugging Codex behavior): `<session-dir>/runs/`
   - Errors (per variant): `<session-dir>/errors/`

User input (rule to test):
$ARGUMENTS
