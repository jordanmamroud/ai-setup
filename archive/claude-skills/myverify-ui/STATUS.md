# STATUS — ui-verify

Project state snapshot. README.md is the spec; this file is "where we are this week."

## Current state: shipped and in daily use

The Claude-side bridge (`ui-verify`) is the only existing variant. It's installed, exercised via per-run history, and the architecture has stabilized into a single self-contained folder under `~/mylab/ai-setup/claude-skills/myverify-ui/` with two external symlinks for invocation.

## What's actually wired up right now

- **Canonical files** (all in this folder, all under git):
  - `ui-verify` — the bash bridge. Self-locates via `${BASH_SOURCE[0]}`.
  - `system-prompt.md` — verifier instructions, inlined into `claude -p` via `--append-system-prompt`. Frontmatter is informational only; live values come from the bridge's config block.
  - `mcp.json` — Playwright MCP, scoped to the verifier subprocess only via `--mcp-config` + `--strict-mcp-config`. Not loaded into other projects' main-agent contexts.
  - `config.sh` — optional overrides; ships with everything commented out.
  - `my-uiverify-command.md` — slash-command body for `/my-uiverify`.
  - `README.md` — full spec, install, brief format, caveats, drop-in CLAUDE.md block.
  - `system-prompt.md` body covers Mission, Role-in-the-loop, Approach, Bail rules, Output format.

- **External symlinks** (verified pointing at the canonical files):
  - `~/bin/ui-verify` → `~/mylab/ai-setup/claude-skills/myverify-ui/ui-verify`
  - `~/.claude/commands/my-uiverify.md` → `~/mylab/ai-setup/claude-skills/myverify-ui/my-uiverify-command.md`

- **Run history**: `~/.local/share/ui-verify/runs.jsonl` + per-run `brief.md` / `response.md` / `meta.json` under `runs/<run_id>/`. 3 runs logged so far. Path overridable via `UI_VERIFY_HISTORY_DIR`.

- **Prerequisites enforced by the bridge**: `claude`, `jq`, and (when `mcp.json` is present) `npx`. Each is checked with a clear error or warning before invocation.

## Features built since the original v1 milestone

These all landed after the early STATUS.md was written and aren't reflected in the older "6 done criteria" framing:

- Bridge moved out of `~/.claude/agents/` deliberately (no auto-discovery; invocation must go through the shell).
- Playwright MCP moved from user scope into bridge-managed `mcp.json` so other projects don't carry Playwright tool defs.
- Per-run history logging (jsonl index + per-run dirs with brief, response, meta).
- Env-var overrides: `UI_VERIFY_PROMPT_FILE`, `UI_VERIFY_MCP_CONFIG`, `UI_VERIFY_ALLOWED_TOOLS`, `UI_VERIFY_MODEL`, `UI_VERIFY_HISTORY_DIR`, `UI_VERIFY_NOTES`.
- `config.sh` precedence layer between script defaults and env vars.
- Prechecks for `mcp.json` parseability and `npx` availability with actionable error messages.
- `.gitignore` covering `.playwright-mcp/` artifacts and the auto-generated `Context.md`.
- Folder relocated into the `ai-setup` harness; all path references updated.

## Not done

- **v2 Codex CLI variant.** Not started. Open question whether it's still worth doing — discuss separately.
- **Autonomous fix-and-retry demo loop.** The integration proof (main agent + ui-verify iterating without a human relay) was sketched but never run end-to-end in a fresh session.
- **`--json` output mode.** Optional. Useful for non-LLM consumers (CI scripts, dashboards) but no concrete demand yet.
- **PostToolUse hook integration.** Optional. Auto-run `ui-verify` after Edit/Write on UI files. Trade-off: hard to know what to verify per change, so works best as a fixed smoke check.
- **Regression test for ui-verify itself.** No harness. Smoke test is "run it and eyeball the result."
- **Concurrency safety on same-project parallel runs.** Documented in README caveats. Two paths exist (`flock` quick fix, per-agent isolation real fix); neither implemented because nobody's hit the case yet.

## Open issues and context worth keeping in head

- **`--dangerously-skip-permissions` is baked into the bridge.** Fine for a local dev tool; reconsider before any shared/CI use.
- **`claude -p` inside Claude Code is implicitly recursive.** Hasn't caused problems but exit codes propagate through two process boundaries — keep in mind when debugging.
- **MCP tools may not be exposed inside `claude -p` subprocesses invoked via the Agent tool.** The verifier's system prompt has a scripted-Playwright-via-Bash fallback for this case. Slower (~60–90s vs ~30s) but works.
- **`claude -p` won't exit while Claude Code background tasks are still running.** If the calling agent leaves a dev server detached as a tracked background task, the bridge appears to hang. Fix lives in the calling project's CLAUDE.md (kill the server before final message, or `nohup … & disown` to detach).
