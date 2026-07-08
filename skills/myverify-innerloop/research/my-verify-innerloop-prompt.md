# Prompt to build the `/my-verify-innerloop` slash command

Paste the following into Claude Code from any project. It builds the command at `~/.claude/commands/my-verify-innerloop.md` so it's globally available.

---

Create a global slash command at `~/.claude/commands/my-verify-innerloop.md` that sets up an inner-loop verification system in the current TypeScript/React project when invoked.

The command file should be a single markdown file with frontmatter:

```
---
description: Set up self-verification hooks (PostToolUse + Stop) for a TypeScript/React project — strict ESLint rules, tsconfig settings, and hook scripts that auto-run prettier/eslint/tsc on changed files and block task completion until checks pass.
---
```

The body should instruct the agent to execute these steps in order in the current working directory:

**1. Confirm project shape.** Check for `tsconfig.json` and a `react` dependency in `package.json`. If either is missing, stop and tell the user this command only applies to TypeScript/React projects.

**2. Check for existing setup.** Look for `.claude/hooks/post-edit-check.sh`, `.claude/hooks/stop-check.sh`, existing ESLint config, existing prettier config. If hooks already exist, ask before overwriting.

**3. Detect package manager** from lockfile (pnpm-lock.yaml → pnpm, yarn.lock → yarn, bun.lockb → bun, otherwise npm). Install any missing dev dependencies: `eslint`, `@typescript-eslint/eslint-plugin`, `@typescript-eslint/parser`, `eslint-plugin-react-hooks`, `eslint-plugin-react`, `eslint-plugin-unused-imports`, `eslint-plugin-eslint-comments`, `prettier`. Note `vitest` as optional — only install if there's a test setup.

**4. Merge ESLint rules** into the existing config (preserve existing rules, don't overwrite). All at `error` level:

- Type safety: `@typescript-eslint/no-explicit-any`, `no-unsafe-assignment`, `no-unsafe-call`, `no-unsafe-member-access`, `no-unsafe-return`, `no-non-null-assertion`, `consistent-type-imports`
- Promise hygiene: `no-floating-promises`, `no-misused-promises`, `await-thenable`, `require-await`
- React hooks: `react-hooks/rules-of-hooks`, `react-hooks/exhaustive-deps` (force as error, not warn), `react/jsx-key`, `react/no-unstable-nested-components`
- Bypass detection: `@typescript-eslint/ban-ts-comment`, `prefer-ts-expect-error`, `eslint-comments/require-description` (forces any `eslint-disable` to include a justification comment — keeps escapes deliberate, not lazy)
- Dead code: `no-unused-vars`, `unused-imports/no-unused-imports`

**Do not add size/complexity rules** (`max-lines-per-function`, `max-lines`, `complexity`) to the verification config. Those are taste, not correctness, and they cause noisy refactor loops on existing codebases. They belong in a separate style check, not the agent's gate.

**5. Update tsconfig.json** to merge in `strict: true`, `noUncheckedIndexedAccess: true`, `exactOptionalPropertyTypes: true`. Preserve everything else.

**6. Create `.claude/hooks/post-edit-check.sh`** — bash, under 50 lines:

- Read JSON from stdin via `jq`, extract `tool_input.file_path`
- Exit 0 if file isn't `.ts/.tsx/.js/.jsx`
- Run in order: `prettier --check` on the file, `eslint` on the file, then **whole-project** `tsc --noEmit --incremental` (do NOT pass the file as an argument to tsc — that bypasses tsconfig and runs in default non-strict mode; whole-project incremental is fast after the first run)
- If any fail, write filtered failing output to stderr (errors only, no banners, cap at ~2000 chars) and exit 2
- Otherwise exit 0 silently
- `chmod +x` after creating

**7. Create `.claude/hooks/stop-check.sh`** — bash, under 50 lines:

- Read JSON from stdin, check `stop_hook_active` flag — if true, exit 0 immediately (prevents infinite loops)
- Get changed files (including untracked ones — important, agents often create new files):
  ```bash
  CHANGED=$({ git diff --name-only HEAD; git ls-files --others --exclude-standard; } \
    | sort -u | grep -E '\.(ts|tsx|js|jsx)$' || true)
  ```
- If no changed files, exit 0
- Run prettier and eslint on the changed files
- Run whole-project `tsc --noEmit --incremental` (not file-scoped — same reason as above)
- Run `vitest run --changed` if vitest is installed
- If any fail, write filtered failing output to stderr (cap ~2000 chars) and exit 2
- `chmod +x` after creating

**8. Register hooks** in `.claude/settings.json` — merge in PostToolUse (matcher `Write|Edit|MultiEdit`) pointing to `post-edit-check.sh` and Stop pointing to `stop-check.sh`. Preserve any existing hooks.

**9. Verify it works.** Create a temporary file with deliberate violations (`const x: any = 1; const y = 2;` — unused var + any). Manually invoke `post-edit-check.sh` against it via piped JSON, confirm it exits 2 with readable errors. Delete the temp file.

**10. Recommend follow-up skills.** After setup, tell the user that to get the most out of `exhaustive-deps: error`, they should install a React useEffect skill (Vercel's `react-best-practices` skill set or a `react-useeffect-guide` skill). The rule is strict and the agent needs the right patterns to reach for (event handlers, `useMemo`, `key` props, `useEffectEvent`) instead of fighting the linter. Without the skill, the agent may try to disable the rule — the `require-description` rule forces it to justify any such escape, but a better-equipped agent rarely needs to.

**11. Summarize what was added** — list the files created/modified, the rules now enforced, and tell the user how to disable individual rules if they get noisy. Mention they can re-run `/my-verify-innerloop` to repair if anything gets out of sync.

After building this command file, do not execute it. Just show me the file contents so I can review before invoking.
