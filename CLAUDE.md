# ai-setup

This folder is the central place for my Claude Code + terminal setup. It holds config and scripts that are version-controlled to GitHub so I can keep my environment in sync across sessions.

The `zsync` zsh function copies `~/.zshrc` into `terminal/zshrc` and pushes it. Raycast script commands live in `raycast/`.

## How I want Claude to help me

Help me navigate my file system, move files and folders around, and rename things. Also answer quick questions and do research as I work. Lean toward action over discussion when the task is clearly a file or shell operation.

## Layout

See `README.md` in this folder for the home-directory layout (`~/myghub`, `~/myquickie`, aliases, auto-memory).

This folder contains: `README.md`, `CLAUDE.md` (this file), `AGENTS-system.md` (Codex voice rules), `claude-link-commands.sh` (symlink installer for skills), `skills/` (slash commands and SKILL.md skills, each self-contained in its own subfolder), `terminal/` (shell setup: `terminal/zshrc` backup of `~/.zshrc`, `terminal/shortcuts/` global PATH shortcuts, `terminal/ghostty/` Ghostty terminal config), `raycast/` (Raycast script commands), `tuning/` (good/bad response corpus for tuning agent behavior — see its own `README.md`).

## Conventions

- **Naming**: use a `<group>-<verb>-<target>` pattern for files and folders so related items sort alphabetically and the action is obvious from the name alone. Bad: `claude-quickie.sh` (no verb — does it open it? delete it? sync it?). Good: `claude-open-quickie.sh` (verb in the middle; future `claude-*` scripts will group together).

