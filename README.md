# Home directory layout

How my laptop's home directory is organized for Claude work.

## Shell aliases (`~/.zshrc`)

These can't move to `terminal/shortcuts/` because they `cd` the current shell —
a subshell script's `cd` evaporates on exit.

- `cq` — `cd ~/mylab/quickies && claude` (fastest, default muscle memory)
- `cquickie` — same as `cq`, longer form
- `chub` — `cd ~/mylab/main && claude` (explicit, for serious work)
- `refresh` — `source ~/.zshrc` (reloads zshrc into the current shell)
- `clone <url>` — wrapper around the `clone` script that also `cd`s into the new repo

Plain `claude` still works for in-place sessions in any folder.

## Global command shortcuts

Real shell scripts on `PATH` (work from terminals, Claude `!` prefix, scripts, cron).
Source of truth: [`terminal/shortcuts/README.md`](terminal/shortcuts/README.md). Run
`mycmds` for the live list.

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
   - The `cq` / `cquickie` / `chub` aliases (see "Shell aliases" above)
5. Copy `~/mylab/main/CLAUDE.md` (auto-memory disable) and `~/mylab/quickies/CLAUDE.md`
   (navigator scope) from this `ai-setup` repo — both are version-controlled here.
