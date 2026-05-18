# ai-setup

## Summary
`ai-setup` is the version-controlled home for a personal Claude Code, Codex, and terminal environment. It collects slash-command skills, global shell shortcuts, Raycast script commands, terminal config, and an agent-tuning corpus into one repo so the whole setup stays in sync and can be rebuilt on any machine. `claude-link-commands.sh` symlinks `claude-skills/` into `~/.claude/` and `codex-link-commands.sh` symlinks `codex-skills/` into `~/.codex/`, while the `zsync` shortcut backs up the live `~/.zshrc` into the repo. It exists so the author's environment is reproducible and self-documenting rather than scattered across untracked dotfiles.

## What's in this folder
- `how-it-works.md` — current code flow (auto-refreshed by `/mydoc-overview`)
- `codebase-map.md` — spatial map of the repo (auto-refreshed by `/mydoc-overview`)
- `notes.md` — append-only log. `## Observations` is user-directed (issues, ideas, notes, questions). The four checkpoint sections (Ideas, Open threads, Resolved, CLAUDE.md candidates) are managed by `/mydoc-checkpoint`.
