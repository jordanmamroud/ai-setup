# myverify-innerloop

A toolkit for dropping high-level self-verification into any of my projects with one command. AI coding agents skip checks unless something forces them — this repo builds those forcing functions: hook scripts that run on every edit and at task end, installed by slash commands that adapt to the target project.

## How it works

### 1. Initiation

In any target project, the user runs one of the slash commands:

- `/my-verify-innerloop` — for lint, types, and unit tests (built).
- `/my-verify-outerloop` — for E2E feature verification (spec'd, not yet built).

The command `.md` files live in this repo and are symlinked into `~/.claude/commands/`, which is what makes them globally invokable. Everything they install, though, is project-local.

### 2. Action / Installation

The slash command inspects the target project (package manager, framework, existing config) and then:

- Installs any missing dev dependencies (ESLint, Prettier, TypeScript plugins, etc.).
- Writes or updates project config — strict `tsconfig.json` and `eslint.config.js` for the inner loop; a markered CLAUDE.md snippet for the outer loop.
- Copies the hook `.sh` scripts from this repo into the target's `.claude/hooks/` (copied, not symlinked, so each project stays self-contained).
- Registers those scripts in the target's `.claude/settings.json` under `PostToolUse` and `Stop`, merging with whatever's already there.

After install, the target project's local `.claude/` folder is wired up; nothing global to the user's machine has been touched besides the original command symlink.

### 3. Execution / Result

During a normal Claude session in the installed project:

- After every `Write` / `Edit` / `MultiEdit`, the **PostToolUse hook** fires and runs cheap checks on the file that just changed. If anything fails, it exits non-zero and the error is fed back to Claude.
- When Claude tries to end the turn, the **Stop hook** fires and runs the heavier gate across everything changed in the session (all modified + untracked files for the inner loop; the recorded session-changes log for the outer loop). Non-zero exit blocks Claude from stopping.
- Claude reads the failure output and keeps working until the gate passes.

### 4. File reference

In this repo:

- `my-verify-innerloop.md` — the slash command that installs the inner loop into a target project.
- `my-verify-outerloop.md` *(planned)* — the slash command that installs the outer loop.
- `innerloop/post-edit-check.sh` — PostToolUse: runs Prettier + ESLint on the edited file, then whole-project `tsc --noEmit --incremental`.
- `innerloop/stop-check.sh` — Stop: runs the same checks across all changed/untracked files, plus `vitest run --changed` if vitest is present.
- `outerloop/post-edit-record.sh` *(planned)* — PostToolUse: appends every edited path to `.verify/session-changes` so the Stop hook knows what was touched.
- `outerloop/stop-verify.sh` *(planned)* — Stop: classifies session changes into production / test / ignored, requires a real E2E test for production changes, and runs the verifier (Playwright / pytest / Vitest).
- `outerloop-spec.md` — design doc for the outer loop, locked decisions, install flow, and script contracts.
- `research/my-verify-innerloop-prompt.md` — the original prompt that produced the inner-loop command.

Installed into the target project at:

- `.claude/hooks/post-edit-check.sh` and `.claude/hooks/stop-check.sh` *(inner loop)*
- `.claude/hooks/post-edit-record.sh` and `.claude/hooks/stop-verify.sh` *(outer loop)*
- `.claude/settings.json` — hook entries registered so Claude Code runs them automatically.

## What we have

### Inner loop — `/my-verify-innerloop`

A global Claude Code slash command. The canonical file lives in this repo at `my-verify-innerloop.md`; `~/.claude/commands/my-verify-innerloop.md` is a symlink to it, so edits here flow through to the global command. Installs a per-project self-verification harness in any TypeScript/React project:

- **PostToolUse hook** (`.claude/hooks/post-edit-check.sh`) — runs prettier + eslint on the edited file, then whole-project `tsc --noEmit --incremental`. Blocks if anything fails.
- **Stop hook** (`.claude/hooks/stop-check.sh`) — runs the same checks across all changed/untracked files, plus `vitest run --changed` if vitest is present. Blocks task completion until clean.
- **Strict ESLint rules** at `error` level — type safety, promise hygiene, React hooks, bypass detection, dead code.
- **Strict tsconfig** — `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`.

The original prompt that builds the command lives in `research/my-verify-innerloop-prompt.md`.

## Notes

Carried over from the original prompt:

- **Skip size/complexity rules in the verification gate.** `max-lines-per-function`, `max-lines`, `complexity` are taste, not correctness. They cause noisy refactor loops on existing codebases. If we want them, put them in a separate style check — not the agent's gate.
- **Pair with a React useEffect skill.** `react-hooks/exhaustive-deps: error` is strict. Without the right patterns to reach for (event handlers, `useMemo`, `key` props, `useEffectEvent`), the agent will try to disable the rule. The `eslint-comments/require-description` rule forces a justification, but a better-equipped agent rarely needs to escape. Look at Vercel's `react-best-practices` skill set or build a `react-useeffect-guide` skill.
- **`tsc` is whole-project, not file-scoped.** Passing a file to `tsc` bypasses tsconfig and runs in default non-strict mode. Whole-project `--incremental` is fast after the first run.
- **Stop hook must include untracked files.** Agents often create new files; `git diff` alone misses them. Combine with `git ls-files --others --exclude-standard`.
- **Stop hook must respect `stop_hook_active`** to avoid infinite loops.

## Next

- **Outer loop.** The inner loop catches type/lint/test failures while the agent works. We still need an outer loop that verifies the *feature* — behavior, UI, end-to-end. Likely some combination of headless browser checks, screenshot diffs, and/or a separate review agent that runs against the finished change. To design.
