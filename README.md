# Home directory layout

How my laptop's home directory is organized for Claude work.

## The two top-level folders

- **`~/myghub/`** — main projects folder. Graduated / serious work.
- **`~/myquickie/`** — scratchpad + filesystem navigator. New ideas, quick
  questions, throwaway tests. Default home for anything new.

When something in `~/myquickie/` proves itself, graduate it:
`mv ~/myquickie/<name> ~/myghub/<name>`.

## Shell aliases (`~/.zshrc`)

- `cq` — `cd ~/myquickie && claude` (fastest, default muscle memory)
- `cquickie` — same as `cq`, longer form
- `chub` — `cd ~/myghub && claude` (explicit, for serious work)

Plain `claude` still works for in-place sessions in any folder.

## Auto-memory

Claude Code's auto-memory (the `MEMORY.md` injected into every system prompt)
is **disabled in `~/myghub/`** via a directive in `~/myghub/CLAUDE.md`.
Reason: don't want context injected into serious-project sessions without
knowing.

Auto-memory stays active in `~/myquickie/` (it's the navigator — useful there).

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

1. `mkdir ~/myghub ~/myquickie`
2. Clone serious repos into `~/myghub/`
3. Add the aliases above to `~/.zshrc`
4. Copy `~/myghub/CLAUDE.md` (auto-memory disable) and `~/myquickie/CLAUDE.md`
   (navigator scope) from this `ai-setup` repo — both are version-controlled here.
