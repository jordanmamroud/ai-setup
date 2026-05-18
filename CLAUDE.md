# ai-setup

This folder is the central place for my Claude Code + Codex + terminal setup. It holds config and scripts that are version-controlled to GitHub so I can keep my environment in sync across sessions.

The `zsync` zsh function copies `~/.zshrc` into `terminal/zshrc` and pushes it. Raycast script commands live in `raycast/`.

## How I want Claude to help me

Help me navigate my file system, move files and folders around, and rename things. Also answer quick questions and do research as I work. Lean toward action over discussion when the task is clearly a file or shell operation.

## Layout

See `README.md` in this folder for the home-directory layout (`~/myghub`, `~/myquickie`, aliases, auto-memory).

This folder contains: `README.md`, `CLAUDE.md` (this file), `global/CLAUDE.md` (Claude global rules → `~/.claude/CLAUDE.md`), `AGENTS.md` (Codex global rules → `~/.codex/AGENTS.md`), `claude-link-commands.sh` (links `claude-skills/` and `global/CLAUDE.md` into `~/.claude/`) and `codex-link-commands.sh` (links `codex-skills/` and `AGENTS.md` into `~/.codex/`), `claude-skills/` (Claude slash commands and SKILL.md skills, each self-contained in its own subfolder), `codex-skills/` (Codex prompts and packaged skill folders), `terminal/` (shell setup: `terminal/zshrc` backup of `~/.zshrc`, `terminal/shortcuts/` global PATH shortcuts, `terminal/ghostty/` Ghostty terminal config), `raycast/` (Raycast script commands), `tuning/` (good/bad response corpus for tuning agent behavior — see its own `README.md`).

## Conventions

- **Naming**: use a `<group>-<verb>-<target>` pattern for files and folders so related items sort alphabetically and the action is obvious from the name alone. Bad: `claude-quickie.sh` (no verb — does it open it? delete it? sync it?). Good: `claude-open-quickie.sh` (verb in the middle; future `claude-*` scripts will group together).
- **Claude vs Codex skills**: `claude-skills/<name>/` holds the Claude form (one self-contained folder per skill — `SKILL.md` with `name:` frontmatter, or a single entry `.md`; `claude-link-commands.sh` links it into `~/.claude/commands/`). `codex-skills/<name>.md` holds the flat Codex prompt installed by `codex-link-commands.sh` into `~/.codex/prompts/`; matching `codex-skills/<name>/` folders are linked into `~/.codex/skills/` for packaged skill workflows. The Codex doc skills are intentional **duplicates** of their Claude counterparts (not symlinks) so they can diverge; they retarget `CLAUDE.md` references to `AGENTS.md`.
