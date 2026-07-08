# ai-setup

## Summary
`ai-setup` is the version-controlled home for a personal Claude Code, Codex, and terminal environment. It collects agent rules, slash-command skills, Codex prompts, global shell shortcuts, Raycast script commands, terminal config, and an agent-tuning corpus into one repo so the whole setup stays in sync and can be rebuilt on any machine. Agent instructions live under `agent-rules/` so they do not load as repo-local project rules; `claude-link-commands.sh` and `codex-link-commands.sh` symlink them plus the tool-specific skills into `~/.claude/` and `~/.codex/`. It exists so the author's environment is reproducible and self-documenting rather than scattered across untracked dotfiles.

## What's in this folder
- `how-it-works.md` — current code flow (maintained manually; the `/mydoc-overview` skill that refreshed it is retired)
- `codebase-map.md` — spatial map of the repo (maintained manually)
- `notes.md` — append-only log. `## Observations` is user-directed (issues, ideas, notes, questions). The four checkpoint sections (Ideas, Open threads, Resolved, CLAUDE.md candidates) are managed by `/jm-doc checkpoint`.
