---
description: Set up self-verification hooks (PostToolUse + Stop) for a TypeScript/React project — strict ESLint rules, tsconfig settings, and hook scripts that auto-run prettier/eslint/tsc on changed files and block task completion until checks pass.
disable-model-invocation: true
---

Set up an inner-loop verification system in the current TypeScript/React project. Execute these steps in order in the current working directory.

## 1. Confirm project shape

Check for:
- `tsconfig.json` in the current directory
- a `react` dependency in `package.json` (either `dependencies` or `devDependencies`)
- a `.git` directory at the project root (the stop hook compares changed/untracked files via `git diff` + `git ls-files`, which only works inside a git repo)

If any of the three is missing, stop and tell the user what's missing. For the missing-git case, tell them to run `git init` and re-run the command — the inner loop assumes version control for diffs and rollback.

## 2. Check for existing setup

Look for:
- `.claude/hooks/post-edit-check.sh`
- `.claude/hooks/stop-check.sh`
- Existing ESLint config (`eslint.config.*`, `.eslintrc*`, or `eslintConfig` in `package.json`)
- Existing prettier config (`.prettierrc*`, `prettier.config.*`, or `prettier` in `package.json`)

If either hook script already exists, ask the user before overwriting.

## 3. Detect package manager and install dev dependencies

Detect from lockfile:
- `pnpm-lock.yaml` → pnpm
- `yarn.lock` → yarn
- `bun.lockb` → bun
- otherwise → npm

Install any of these that are missing as dev dependencies:
- `eslint`
- `typescript-eslint` (umbrella package — pulls in both `@typescript-eslint/eslint-plugin` and `@typescript-eslint/parser`. If the project already has the separate packages installed, leave them; don't install duplicates.)
- `eslint-plugin-react-hooks`
- `eslint-plugin-react`
- `eslint-plugin-unused-imports`
- `@eslint-community/eslint-plugin-eslint-comments` (the original `eslint-plugin-eslint-comments` is unmaintained and crashes on modern ESLint — use the community fork)
- `prettier`

`vitest` is optional — only install it if the project already has a test setup.

## 4. Generate the ESLint config (rewrite, not merge)

Any existing config is almost certainly wired for "simple mode" — no `parserOptions.project`, no TypeScript service. The strict rules below need "smart mode" (type-aware linting), which requires a different parser, plugin wiring, and parser options. The two modes don't share structure, so there's nothing useful to merge into.

Rewrite the config from scratch. Preserve **only** the rules array from the previous config:

1. Extract custom rule entries from the existing `eslint.config.*` / `.eslintrc*` (if one exists).
2. Generate a fresh `eslint.config.js` (flat config) that loads `typescript-eslint`, `eslint-plugin-react-hooks`, `eslint-plugin-react`, `eslint-plugin-unused-imports`, and `@eslint-community/eslint-plugin-eslint-comments`, with the parser pointed at the project's tsconfig for type-aware linting (`parserOptions.project: true` for simple setups, `projectService: true` for projects with TS references).
3. Add all rules below at `error` level.
4. Append the preserved custom rules from step 1 last — their settings win on conflict, since the user chose them deliberately.

For `no-restricted-syntax`: the rule's value is an array. The new selector entry (`TSAsExpression > TSAsExpression`) must be added to the array, not replace it — so any preserved user selectors coexist with ours.

**Type safety**
- `@typescript-eslint/no-explicit-any`
- `@typescript-eslint/no-unsafe-assignment`
- `@typescript-eslint/no-unsafe-call`
- `@typescript-eslint/no-unsafe-member-access`
- `@typescript-eslint/no-unsafe-return`
- `@typescript-eslint/no-non-null-assertion`
- `@typescript-eslint/consistent-type-imports`
- `@typescript-eslint/no-unnecessary-type-assertion` — flags redundant casts (e.g. `(x as string)` when `x` is already `string`).
- `@typescript-eslint/consistent-type-assertions` — config: `{ "assertionStyle": "as", "objectLiteralTypeAssertions": "never" }`. Bans `{ foo: 1 } as Bar` on object literals; forces `const x: Bar = { foo: 1 }` so the type-checker actually validates the shape.
- `no-restricted-syntax` — config: `[{ "selector": "TSAsExpression > TSAsExpression", "message": "Avoid double type assertions like 'as unknown as X'. Use a type guard or a typed transformer function instead." }]`. Catches the `as unknown as X` antipattern by matching nested `TSAsExpression` nodes. The other two assertion rules don't catch this because the double-cast is neither unnecessary nor on an object literal.

**Promise hygiene**
- `@typescript-eslint/no-floating-promises`
- `@typescript-eslint/no-misused-promises`
- `@typescript-eslint/await-thenable`
- `@typescript-eslint/require-await`

**React hooks**
- `react-hooks/rules-of-hooks`
- `react-hooks/exhaustive-deps` (force as `error`, not `warn`)
- `react/jsx-key`
- `react/no-unstable-nested-components`

**Bypass detection**
- `@typescript-eslint/ban-ts-comment` — config: `{ "ts-ignore": true, "ts-expect-error": "allow-with-description", "minimumDescriptionLength": 3 }`. Forbids `@ts-ignore` outright and forces a written reason on every `@ts-expect-error`. (Replaces `@typescript-eslint/prefer-ts-expect-error`, which was removed in typescript-eslint v8 — `ban-ts-comment` options now cover the same enforcement.)
- `eslint-comments/require-description` (forces any `eslint-disable` to include a justification comment — keeps escapes deliberate, not lazy)

**Dead code**
- `no-unused-vars`
- `unused-imports/no-unused-imports`

**Do not add size/complexity rules** (`max-lines-per-function`, `max-lines`, `complexity`) to the verification config. Those are taste, not correctness, and they cause noisy refactor loops on existing codebases. They belong in a separate style check, not the agent's gate.

## 5. Update tsconfig.json

Merge in:
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

Preserve everything else.

## 6. Install hook scripts

The canonical hook scripts live in this repo at `innerloop/post-edit-check.sh` and `innerloop/stop-check.sh`. Copy them into the target project — don't regenerate them.

Resolve the canonical directory by following the symlink on this command file:

```bash
SELF_VERIFY=$(dirname "$(readlink "$HOME/.claude/commands/my-verify-innerloop.md")")
mkdir -p .claude/hooks
cp "$SELF_VERIFY/innerloop/post-edit-check.sh" .claude/hooks/post-edit-check.sh
cp "$SELF_VERIFY/innerloop/stop-check.sh" .claude/hooks/stop-check.sh
chmod +x .claude/hooks/post-edit-check.sh .claude/hooks/stop-check.sh
```

If `readlink` returns empty (the command isn't symlinked, e.g. running from a clone), fall back to asking the user for the path to the `myverify-innerloop` folder, then use that.

If either hook script already exists (from a previous install), ask before overwriting — the existing copy may have diverged.

What the scripts do, for reference:

- **`post-edit-check.sh`** (PostToolUse): reads tool JSON from stdin, extracts the edited file path, exits 0 if not `.ts`/`.tsx`/`.js`/`.jsx`. Otherwise runs `prettier --check`, `eslint`, and a whole-project `tsc` (auto-detects `tsc -b` vs `tsc --noEmit --incremental` based on whether `tsconfig.json` has a `references` array). Never passes the file as a tsc arg — that bypasses tsconfig and runs non-strict. Writes filtered failing output to stderr (capped ~2000 chars) and exits 2 on fail.
- **`stop-check.sh`** (Stop): respects the `stop_hook_active` flag to avoid loops. Collects changed and untracked `.ts`/`.tsx`/`.js`/`.jsx` files via `git diff --name-only HEAD` + `git ls-files --others --exclude-standard`. Runs prettier + eslint on those, whole-project tsc, and `vitest run --changed` if vitest is in `devDependencies`. Same fail behavior.

## 7. Register hooks in `.claude/settings.json`

Merge in:
- `PostToolUse` with matcher `Write|Edit|MultiEdit` pointing to `.claude/hooks/post-edit-check.sh`
- `Stop` pointing to `.claude/hooks/stop-check.sh`

Preserve any existing hooks.

## 8. Verify it works

Create a temporary file with deliberate violations:
```ts
const x: any = 1;
const y = 2;
```
(unused var + `any`)

Manually invoke `post-edit-check.sh` against it via piped JSON, confirm it exits 2 with readable errors. Delete the temp file.

## 9. Recommend follow-up skills

After setup, tell the user that to get the most out of `exhaustive-deps: error`, they should install a React useEffect skill (Vercel's `react-best-practices` skill set or a `react-useeffect-guide` skill). The rule is strict and the agent needs the right patterns to reach for (event handlers, `useMemo`, `key` props, `useEffectEvent`) instead of fighting the linter. Without the skill, the agent may try to disable the rule — the `require-description` rule forces it to justify any such escape, but a better-equipped agent rarely needs to.

## 10. Summarize what was added

List:
- Files created/modified
- The rules now enforced
- How to disable individual rules if they get noisy
- That they can re-run `/my-verify-innerloop` to repair if anything gets out of sync
