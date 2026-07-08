# Outer loop spec — `/my-verify-outerloop`

Design document for the outer-loop verification command. Builder-Verifier pattern with deterministic E2E tests, enforced by hooks. Sibling to `my-verify-innerloop` (lint/types/unit) — together they form the full self-verify harness.

## Goal

Make it impossible for Claude to mark a feature task done unless a real E2E test for that feature exists and passes. The Builder (Claude) writes code + test. The Verifier (shell script, no LLM) runs only that test. The Stop hook is the hard gate.

## Architecture

Four pieces, same pattern as inner loop:

| Piece | Lives at (this repo) | Installed at (target project) |
|---|---|---|
| Command file | `my-verify-outerloop.md` (symlinked to `~/.claude/commands/`) | n/a — symlink is global |
| PostToolUse hook script | `outerloop/post-edit-record.sh` | `.claude/hooks/post-edit-record.sh` (copy) |
| Stop hook script | `outerloop/stop-verify.sh` | `.claude/hooks/stop-verify.sh` (copy) |
| CLAUDE.md snippet | `outerloop/claude-md-snippet.md` | merged into target `CLAUDE.md` between markers |

Plus runtime state in the target project:

- `.verify/session-changes` — append log of every file touched by Claude in the current session (written by PostToolUse, read by Stop, cleared by Stop on pass). Gitignored.

## Locked decisions

1. **Idempotency**: markered block (`<!-- builder-verifier:start -->` ... `<!-- builder-verifier:end -->`) in CLAUDE.md; re-runs replace what's between the markers.
2. **Test runner**: auto-detect from `package.json` / `pyproject.toml`; fall back to asking the user. Initial supported runners: Playwright (`@playwright/test`), pytest, Vitest.
3. **Hook conflict**: append alongside any existing entries in `.claude/settings.json`. Do not replace.
4. **Activation**: modification-driven gating. PostToolUse records what was modified; Stop reads the log and decides whether to run the verifier. Manifest-free.
5. **Script delivery**: real `.sh` files live here, copied (not symlinked) into target projects on install. Same model as inner loop after the recent fix.

## Install flow

What `/my-verify-outerloop` does when invoked in a target project:

1. **Confirm project shape**
   - `.git` directory present (otherwise abort and ask user to `git init`).
   - One of: `package.json` (Node) or `pyproject.toml`/`setup.py` (Python).

2. **Detect test runner**
   - Node: scan `package.json` deps for `@playwright/test` → Playwright; `vitest` → Vitest (if no Playwright).
   - Python: scan `pyproject.toml`/`requirements*.txt` for `pytest` → pytest.
   - If none found, ask the user.

3. **Resolve canonical script directory**
   - `SELF_VERIFY=$(dirname "$(readlink "$HOME/.claude/commands/my-verify-outerloop.md")")`
   - If empty (command not symlinked), ask the user for the `myverify-outerloop` folder path.

4. **Copy hook scripts**
   - `cp "$SELF_VERIFY/outerloop/post-edit-record.sh" .claude/hooks/`
   - `cp "$SELF_VERIFY/outerloop/stop-verify.sh" .claude/hooks/`
   - `chmod +x` both.
   - If either already exists, ask before overwriting.

5. **Inject CLAUDE.md snippet between markers**
   - Read `outerloop/claude-md-snippet.md` from this repo.
   - Substitute `{{TEST_RUNNER}}`, `{{TEST_GLOB}}`, `{{PROD_GLOB}}` placeholders based on detected runner.
   - If `<!-- builder-verifier:start -->` ... `<!-- builder-verifier:end -->` already exists in target `CLAUDE.md`, replace the content between them.
   - Otherwise append the markered block to `CLAUDE.md`.

6. **Register hooks in `.claude/settings.json`**
   - Add a `PostToolUse` entry, matcher `Write|Edit|MultiEdit`, command `.claude/hooks/post-edit-record.sh`.
   - Add a `Stop` entry, command `.claude/hooks/stop-verify.sh`.
   - Merge (don't replace) — inner loop's hooks must keep working.

7. **Create `.verify/` and gitignore it**
   - `mkdir -p .verify && touch .verify/session-changes`
   - Append `.verify/` to `.gitignore` if not already present.

8. **Verify the install**
   - Echo a fake PostToolUse JSON into `post-edit-record.sh`; confirm the path lands in `.verify/session-changes`.
   - Echo a fake Stop JSON into `stop-verify.sh` with no production changes recorded; confirm it exits 0.
   - Clean the session-changes log.

9. **Summarize**
   - Files created/modified.
   - The runner detected and the test glob it expects.
   - Reminder that uninstalling means removing the two hook entries + the markered block.

## Runtime flow

What happens during a normal Claude session in a target project:

1. User asks Claude to build a feature.
2. Claude reads `CLAUDE.md`, sees the builder-verifier rules in the markered block.
3. Claude writes production code at, e.g., `src/login.ts`.
   - PostToolUse fires → `post-edit-record.sh` appends `src/login.ts` to `.verify/session-changes`.
4. Claude writes a test at, e.g., `tests/e2e/login.spec.ts`.
   - PostToolUse fires again → records that path too.
5. Claude tries to stop.
   - Stop hook fires → `stop-verify.sh` runs.
   - Reads `.verify/session-changes`, classifies entries into production / test / ignored.
   - If production touched + no valid test touched → block with `"you modified production code but didn't write a passing test"`.
   - If a valid test was touched → run the verifier on it: `npx playwright test <files> --reporter=line` (or pytest equivalent).
   - On pass: clear `.verify/session-changes`, exit 0 → Claude stops.
   - On fail: write filtered failure output to stderr, exit 2 → Claude reads the failure, keeps working.
6. If only docs/config were touched (no production code) → Stop hook is a no-op, exit 0.

## Script contracts

### `post-edit-record.sh` (PostToolUse)

- Reads tool JSON from stdin.
- Extracts `tool_input.file_path`. If empty, exit 0.
- Resolves to a path relative to the project root.
- Appends one line to `.verify/session-changes` (one path per line, deduped on read, not on write).
- Always exits 0. **Never blocks.** This hook records, does not gate.
- Under 30 lines.

### `stop-verify.sh` (Stop)

- Reads stop hook JSON from stdin; honors `stop_hook_active` (exit 0 if true).
- Reads `.verify/session-changes`, dedupes, classifies each path:
  - **Production**: matches `{{PROD_GLOB}}` (default: `src/**/*.{ts,tsx,js,jsx,py}`).
  - **Test**: matches `{{TEST_GLOB}}` (default for Playwright: `tests/e2e/**/*.spec.{ts,tsx,js}`; pytest: `tests/**/test_*.py`).
  - **Ignored**: anything else (`*.md`, `*.json`, `*.css`, lockfiles, configs).
- If no production paths → exit 0 (nothing to verify).
- If production paths exist but no test paths → exit 2 with message: `"production code modified but no test file modified — write an E2E test that exercises the change"`.
- Validate each test file:
  - Contains at least one `test(` / `test.describe(` (Playwright) or `def test_` (pytest).
  - Contains at least one `expect(` (Playwright) or `assert` (pytest).
  - No `test.skip` / `test.only` / `test.fixme` / `@pytest.mark.skip` / `pytest.skip`.
  - Body non-trivial (file ≥ 5 lines after stripping comments).
- If validation fails → exit 2 with the specific reason.
- Run the verifier:
  - Playwright: `npx --no-install playwright test <test-files> --reporter=line`
  - pytest: `pytest <test-files> -q`
  - Vitest: `npx --no-install vitest run <test-files>`
- On pass: clear `.verify/session-changes`, exit 0.
- On fail: filter to ~2000 chars, write to stderr, exit 2.
- Under 60 lines (more complex than `post-edit-record.sh`).

### `claude-md-snippet.md`

A markered block injected into the target's CLAUDE.md. Approximately:

```markdown
<!-- builder-verifier:start -->
## Builder-Verifier rules

When the user asks you to build, change, or fix a feature, you must:

1. Write a real E2E test in `{{TEST_GLOB}}` that exercises the change.
2. The test must have real `expect(` / `assert` calls. No `.skip`, no `.only`, no empty bodies.
3. The Stop hook will run that test. You cannot mark the task done until it passes.

If you only modify config, docs, or styling (no `{{PROD_GLOB}}` files), no test is required.

If the test fails, read the verifier output from the hook and fix the code or test. Do not loosen the test to make it pass.
<!-- builder-verifier:end -->
```

Placeholders (`{{TEST_GLOB}}`, `{{PROD_GLOB}}`) are substituted per project at install time.

## Coexistence with inner loop

Both loops install Stop + PostToolUse hooks in the same `settings.json`. Claude Code supports multiple entries per event; all of them run. Naming keeps them distinct:

| | Inner loop | Outer loop |
|---|---|---|
| PostToolUse script | `.claude/hooks/post-edit-check.sh` | `.claude/hooks/post-edit-record.sh` |
| Stop script | `.claude/hooks/stop-check.sh` | `.claude/hooks/stop-verify.sh` |
| Failure mode | Lint/type/unit errors block stop | Missing/failing E2E test blocks stop |

Inner-loop failures (lint/types) usually fire first because they're cheap; outer-loop verifier is the heavier gate. Both must pass for Claude to stop.

## Open questions

1. **Production vs. test globs per project.** Defaults work for standard layouts. For non-standard layouts (`apps/web/src/...`, monorepos), the install needs to detect or ask. v1: hardcode sensible defaults; revisit if it breaks on the user's real projects.

2. **Test gaming.** Claude could write a test that technically passes the validity checks (`test('x', async ({ page }) => { await page.goto('/'); expect(1).toBe(1); })`) but doesn't actually verify the feature. Validity rules catch the obvious cases; precision is the prompt's job, not the hook's. Worth flagging this as a known limitation rather than over-engineering the hook.

3. **Dev server.** Playwright's `webServer` config in `playwright.config.ts` handles starting/stopping the dev server hermetically. If the project doesn't have one, the test will fail with a connection error and Claude will need to add it. The install could detect missing `webServer` config and warn during step 8.

4. **Escape hatch for genuinely broken infra.** If E2E is broken for reasons unrelated to the code (Playwright crashed, port conflict, etc.), Claude gets stuck. Options: a `.verify/skip` sentinel file the user can `touch` to bypass the gate for one session, or an environment variable. v1: skip — add only if it becomes a real problem.

5. **Should the install offer to write `playwright.config.ts` if Playwright isn't already configured?** Leans no — that's the inner loop's pattern of staying out of project setup. Outer loop installs hooks only; user is responsible for the test infrastructure.

## Build order

When implementing:

1. Write `outerloop/post-edit-record.sh` (simplest, no decisions).
2. Write `outerloop/stop-verify.sh` (the hard one — classification, validation, runner dispatch).
3. Write `outerloop/claude-md-snippet.md` template.
4. Write `my-verify-outerloop.md` command file (install flow steps 1–9).
5. Symlink the command into `~/.claude/commands/`.
6. Test in a throwaway project: run `/my-verify-outerloop`, then ask Claude to build a trivial feature, confirm the gate fires.
