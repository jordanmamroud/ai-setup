# ai-setup

Version-controlled source of truth for my local Claude Code, Codex, and terminal setup.

## What This Repo Owns

- `agent-rules/` stores global Claude and Codex instructions.
- `skills/` stores shared global skills, Claude command adapters, and Codex prompt adapters.
- `km-skills/` stores Kitchen Magic workspace skills until they move to a dedicated workspace.
- `hooks/` stores optional Codex hook scripts and `hooks.json`; they are inactive unless linked or copied into an active Codex config layer.
- `terminal/` stores the redacted `~/.zshrc` backup, global shortcut scripts, and terminal config.
- `raycast/` stores Raycast script commands.
- `tuning/` stores good/bad response examples for tuning agent behavior.
- `overview/` stores repo maps, flow notes, and session notes.

## Shell Setup

`terminal/zshrc` is a redacted tracked backup of `~/.zshrc`. The live file owns local-only values such as API keys.

Shell-level helpers stay in `~/.zshrc` when they need to affect the current shell:

- `cq` - `cd ~/mylab/quickies && claude`
- `cquickie` - same as `cq`
- `chub` - `cd ~/mylab/main && claude`
- `refresh` - reload `~/.zshrc`
- `Z` - open `~/.zshrc` through `zopen`
- `ZR` - reload `~/.zshrc`
- `clone <url>` - wrapper around the `clone` shortcut that also `cd`s into the new repo

Shared AI provider keys are loaded from the shell environment, with the local
values owned by `~/.zshrc`:

- `GEMINI_API_KEY` for Gemini
- `OPENAI_API_KEY` for OpenAI
- `OPENROUTER_API_KEY` for OpenRouter

The actual key values stay out of this repo and out of agent output. Global
agent rules in `agent-rules/AGENTS.md` and `agent-rules/CLAUDE.md` tell agents to
load `~/.zshrc` when a task needs a key, use the exported environment variable
directly, and never print/log/request/save the keys.

`zsync` redacts `*_API_KEY` exports before writing the tracked
`terminal/zshrc` backup.

## Shortcuts

Real shell scripts on `PATH` (work from terminals, Claude `!` prefix, scripts, cron).
Source of truth: [`terminal/shortcuts/README.md`](terminal/shortcuts/README.md). Run
`mycmds` for the live list.

## Agent rules

Agent instruction files live in `agent-rules/` so they do not get picked up as project-level
rules inside this repo:

- `agent-rules/CLAUDE.md` → `~/.claude/CLAUDE.md`
- `agent-rules/AGENTS.md` → `~/.codex/AGENTS.md`

Run `./claude-link-commands.sh` or `./codex-link-commands.sh` after changes to refresh
symlinks.

Skill sources live in `skills/` and `km-skills/`:

- `skills/` is scanned by the link scripts.
- Claude slash commands come from `claude-command.md` or a single clear entry `.md`.
- Claude packaged skills are opt-in through `CLAUDE_SKILL_FOLDERS` in `claude-link-commands.sh`.
- Codex prompts come from `codex-prompt.md`.
- Codex packaged skills come from every `skills/<name>/SKILL.md`.
- `km-skills/` is client-scoped and not scanned by the link scripts; its active symlinks are hand-set.
- Retired skills move folder-intact to `archive/skills/`; old split-layout rollback copies live in `archive/claude-skills/` and `archive/codex-skills/`.

## Optional Codex Hooks

`hooks/hooks.json` wires the hook scripts into Codex, but nothing in `hooks/` is active unless that config is linked or copied into an active Codex config layer.

- `pre_tool_use_bash_guard.py` blocks common destructive shell commands.
- `pre_tool_use_protected_files.py` blocks edits to env, credential, and key files.
- `user_prompt_secret_scan.py` blocks prompts that appear to include secrets.
- `post_tool_use_changed_file_checks.py` runs focused checks after edits.
- `stop_changed_tree_checks.py` runs final changed-tree checks before Codex stops.

## Auto-memory

Claude Code's auto-memory (the `MEMORY.md` injected into every system prompt)
is **disabled in `~/mylab/main/`** via a directive in `~/mylab/main/CLAUDE.md`.
Reason: don't want context injected into serious-project sessions without
knowing.

Auto-memory stays active in `~/mylab/quickies/` (it's the navigator — useful there).

Pre-rename memory snapshot archived at `~/.claude/archive/github-memory-2026-05-08/`.

## Recreating on a new machine

1. `mkdir -p ~/mylab/main ~/mylab/quickies`
2. Clone this `ai-setup` repo into `~/mylab/ai-setup` (gives you the `terminal/shortcuts` shortcuts)
3. Clone serious repos into `~/mylab/main/`
4. Add to `~/.zshrc`:
   - The two `PATH` lines: `~/bin` and `~/mylab/ai-setup/terminal/shortcuts`
   - Shared AI provider key exports for `GEMINI_API_KEY`, `OPENAI_API_KEY`, and `OPENROUTER_API_KEY`
   - The shell aliases from "Shell Setup" above, including `cq`, `Z`, and `ZR`
5. Run `./claude-link-commands.sh` and `./codex-link-commands.sh` from this repo.
