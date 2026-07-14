# How it works

*Last refreshed: 2026-07-14*

This repo is configuration, not a running program. Four flows operate on it.

## Install skills into Claude Code and Codex

**Triggers:**
- the user runs `./claude-link-commands.sh` (Claude surface)
- the user runs `./codex-link-commands.sh` (Codex surface)

1. Resolves the physical repo dir and ensures the target dirs exist.
2. Claude: folders listed in `CLAUDE_SKILL_FOLDERS` are linked as whole folders into `~/.claude/skills/<name>`.
3. Claude: the remaining `skills/<name>/` folders can become slash commands in `~/.claude/commands/` when they have `claude-command.md` or exactly one clear entry `.md`.
4. Codex: `skills/<name>/codex-prompt.md` becomes `~/.codex/prompts/<name>.md`, and every `skills/<name>/SKILL.md` folder becomes `~/.codex/skills/<name>`.
5. Named agent-rule files are linked: `agent-rules/CLAUDE.md` → `~/.claude/CLAUDE.md`; `agent-rules/AGENTS.md` → `~/.codex/AGENTS.md`.
6. The scripts use `ln -sfn`, skip unchanged links, and refuse to overwrite real files.
7. Each script prints a `linked / unchanged / skipped` tally.

`km-skills/` is intentionally not scanned by either link script; its active Codex symlinks are hand-set until those skills move to a dedicated workspace.

Old split-layout copies live only under `archive/` for rollback. The current source of truth is `skills/`.

## Optional Codex hooks

**Trigger:** `hooks/hooks.json` is linked or copied into an active Codex config layer.

1. `PreToolUse` can block destructive shell commands and edits to env/credential/key files.
2. `UserPromptSubmit` can block prompts that appear to include secrets.
3. `PostToolUse` runs focused checks on edited files when local tools are available.
4. `Stop` runs final changed-tree checks before Codex stops.

The hooks no-op when matching local tools are absent. They are review/safety helpers, not part of normal repo runtime.

## Sync the shell config

**Triggers:** the user runs `zsync ["message"]`.

1. Copies the live `~/.zshrc` into `terminal/zshrc` in this repo with `*_API_KEY` exports redacted.
2. Commits and pushes the change to GitHub.

The tracked backup is the shareable source of truth for the shell setup; actual API key values live only in the local `~/.zshrc`.

## Run a global shortcut

**Triggers:** the user runs `m <fuzzy-name> [args]` (or `m` alone).

1. `m` resolves `<fuzzy-name>` against the scripts in `terminal/shortcuts/` (exact → prefix → subsequence).
2. With no name, opens an interactive picker (`fzf` if installed, else a plain list).
3. Runs the matched script with the remaining args.

`terminal/shortcuts/` is on `PATH` via `~/.zshrc`, so these work in terminals, Claude's `!` prefix, scripts, and cron.
