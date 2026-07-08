# Home directory layout

How my laptop's home directory is organized for Claude work.

## Shell aliases (`~/.zshrc`)

These are shell-level helpers. The `cd`/`source` ones can't move to
`terminal/shortcuts/` because a subshell script can't change the current shell.

- `cq` — `cd ~/mylab/quickies && claude` (fastest, default muscle memory)
- `cquickie` — same as `cq`, longer form
- `chub` — `cd ~/mylab/main && claude` (explicit, for serious work)
- `refresh` — `source ~/.zshrc` (reloads zshrc into the current shell)
- `Z` — `zopen` (open `~/.zshrc` in TextEdit)
- `ZR` — `source ~/.zshrc` (reloads zshrc into the current shell)
- `clone <url>` — wrapper around the `clone` script that also `cd`s into the new repo

Plain `claude` still works for in-place sessions in any folder.

## Shared API keys (`~/.zshrc`)

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

## Global command shortcuts

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

Skill sources live in `skills/` (global) and `km-skills/` (Kitchen Magic workspace skills,
staged here until they move to a dedicated workspace; their `~/.codex/skills/` symlinks are
hand-set — the link scripts only scan `skills/`). Claude command entries, Codex prompt
entries, and Codex packaged skill folders are installed from `skills/`; retired skills move
folder-intact to `archive/skills/`, and old split-folder copies live in
`archive/claude-skills/` and `archive/codex-skills/` for rollback.

## Auto-memory

Claude Code's auto-memory (the `MEMORY.md` injected into every system prompt)
is **disabled in `~/mylab/main/`** via a directive in `~/mylab/main/CLAUDE.md`.
Reason: don't want context injected into serious-project sessions without
knowing.

Auto-memory stays active in `~/mylab/quickies/` (it's the navigator — useful there).

Pre-rename memory snapshot archived at `~/.claude/archive/github-memory-2026-05-08/`.

## Migration history (2026-05-08)

Layout before today:

- `~/GitHub/` — held both serious projects AND a `quickie/` subfolder
- `~/GitHub/quickie/` — scratchpad subfolder

Today:

- `~/GitHub/quickie/` → `~/myquickie/` (moved up to be a sibling)
- `~/GitHub/` → `~/myhub/` → `~/myghub/` (renamed twice; final keeps `g` for "GitHub-ish")
- Hardcoded path refs in scripts/configs updated
- Auto-memory disabled at `~/myghub/`; old memory archived
- Aliases added to `~/.zshrc`

## Recreating on a new machine

1. `mkdir -p ~/mylab/main ~/mylab/quickies`
2. Clone this `ai-setup` repo into `~/mylab/ai-setup` (gives you the `terminal/shortcuts` shortcuts)
3. Clone serious repos into `~/mylab/main/`
4. Add to `~/.zshrc`:
   - The two `PATH` lines: `~/bin` and `~/mylab/ai-setup/terminal/shortcuts`
   - Shared AI provider key exports for `GEMINI_API_KEY`, `OPENAI_API_KEY`, and `OPENROUTER_API_KEY`
   - The shell aliases from "Shell aliases" above, including `cq`, `Z`, and `ZR`
5. Copy `~/mylab/main/CLAUDE.md` (auto-memory disable) and `~/mylab/quickies/CLAUDE.md`
   (navigator scope) from this `ai-setup` repo — both are version-controlled here.
