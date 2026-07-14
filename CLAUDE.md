# ai-setup

This folder is the central place for my Claude Code + Codex + terminal setup. It holds config and scripts that are version-controlled to GitHub so I can keep my environment in sync across sessions.

The `zsync` shortcut copies `~/.zshrc` into `terminal/zshrc` with API keys redacted, then pushes it. Raycast script commands live in `raycast/`.

## How I want Claude to help me

Help me navigate my file system, move files and folders around, and rename things. Also answer quick questions and do research as I work. Lean toward action over discussion when the task is clearly a file or shell operation.

## Repo Layout

- `.claude/` — Local Claude Code settings for this repo.
- `agent-rules/` — Canonical global instruction files for Claude and Codex.
- `archive/` — Legacy rollback copies from older skill layouts, plus retired skills in `archive/skills/`.
- `hooks/` — Optional Codex hook scripts and hook configuration.
- `km-skills/` — Kitchen Magic workspace skills, staged here until they get a dedicated workspace.
- `overview/` — Repo overview docs, codebase map, flow notes, and session notes.
- `raycast/` — Raycast script commands for launching Claude and related helpers.
- `skills/` — Shared global source for Claude commands, Codex prompts, and Codex packaged skills.
- `terminal/` — Shell config backup, global shortcuts, and terminal configuration.
- `tuning/` — Saved good and bad agent responses for improving agent behavior.

## Conventions

- **Naming**: use a `<group>-<verb>-<target>` pattern for files and folders so related items sort alphabetically and the action is obvious from the name alone. Bad: `claude-quickie.sh` (no verb — does it open it? delete it? sync it?). Good: `claude-open-quickie.sh` (verb in the middle; future `claude-*` scripts will group together).
- **Shared skills**: edit `skills/<name>/` first. Claude slash commands come from `claude-command.md` when present, otherwise the single clear entry `.md`; Claude packaged skills are opt-in through `CLAUDE_SKILL_FOLDERS` in `claude-link-commands.sh`; Codex prompts come from `codex-prompt.md`; Codex packaged skills come from every `SKILL.md`. When Claude and Codex need different wording, keep adapters inside the same `skills/<name>/` folder instead of recreating separate `claude-skills/` and `codex-skills/` trees.
