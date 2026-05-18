# How it works

*Last refreshed: 2026-05-18*

This repo is configuration, not a running program. Three flows operate on it.

## Install skills into Claude Code and Codex

**Triggers:**
- the user runs `./claude-link-commands.sh` (Claude surface)
- the user runs `./codex-link-commands.sh` (Codex surface)

1. Resolves the repo dir and ensures the target dir exists (`~/.claude/commands/`, `~/.codex/prompts/`, or `~/.codex/skills/`).
2. Picks each entry — Claude: for each subfolder in `claude-skills/`, `SKILL.md` (slash name from `name:` frontmatter) else the single non-design `.md` (trailing `-command` stripped); Codex: each flat `codex-skills/<name>.md` becomes a prompt, and each `codex-skills/<name>/` folder with `SKILL.md` becomes a packaged skill.
3. Symlinks the entry into the target with `ln -sfn`, skipping unchanged links and refusing to overwrite a real file.
4. Links named-file mappings — Claude: `CLAUDE-global.md` → `~/.claude/CLAUDE.md`; Codex: `AGENTS.md` → `~/.codex/AGENTS.md` (each replaces an empty file, never a real one).
5. Claude only: symlinks `claude-skills/myverify-ui/ui-verify` to `~/bin/ui-verify` so it lands on `PATH`.
6. Prints a `linked / unchanged / skipped` tally.

Idempotent: re-running only refreshes stale or dangling links. The two surfaces are independent — `codex-skills/` holds intentional duplicates of the three doc skills (`CLAUDE.md` retargeted to `AGENTS.md`), not symlinks to `claude-skills/`.

## Sync the shell config

**Triggers:** the user runs `zsync ["message"]`.

1. Copies the live `~/.zshrc` into `terminal/zshrc` in this repo.
2. Commits and pushes the change to GitHub.

The tracked backup is the single source of truth for the shell setup.

## Run a global shortcut

**Triggers:** the user runs `m <fuzzy-name> [args]` (or `m` alone).

1. `m` resolves `<fuzzy-name>` against the scripts in `terminal/shortcuts/` (exact → prefix → subsequence).
2. With no name, opens an interactive picker (`fzf` if installed, else a plain list).
3. Runs the matched script with the remaining args.

`terminal/shortcuts/` is on `PATH` via `~/.zshrc`, so these work in terminals, Claude's `!` prefix, scripts, and cron.
