# spec — myopen

A voice-friendly slash command that opens a single file in TextEdit, scoped to a small set of known paths.

## Purpose

The user dictates file requests by voice. Speech-to-text mangles names ("my g hub", "claude dot M D"). `myopen` maps that fuzzy input to one of a small set of known paths and opens it — fast, no search, no guessing outside scope.

## Scope

Resolves only within these paths:

- `~/myghub/`     — graduated projects
- `~/myquickie/`  — scratch / in-progress
- `~/.claude/`    — Claude Code config
- `~/.codex/`     — Codex CLI config
- `~/.zshrc`

Anything outside this list is out of bounds. The command refuses rather than widens.

## Behavior

Opens with `open -a TextEdit "<absolute path>"`. Always TextEdit, always one file at a time.

### Two modes

**No argument** — opens the file currently in focus in the conversation (most recently read, edited, or named). If multiple plausible candidates, lists them numbered and asks which.

**With argument** — treated as voice-dictated, so it tolerates spacing, case, punctuation, and homophones. The argument can be:

- **Folder + filename** ("plot.md in myghub", "my G hub plot dot M D") → resolves the folder via the alias table, then `find <folder> -iname "<filename>"` recursively.
- **Filename only** ("plot.md") → same `find -iname` across all scope folders.
- **Folder only** → asks which file.

### Resolution rules

- One match → open.
- Multiple → numbered list, ask "Which one?".
- Zero → "Not found in scope: <what>". Stop, don't widen.

### Hard rules

- Never searches outside the scope paths. No `find /`, no `mdfind`, no `locate`, no recursive search of `~`.
- Never reads the file before opening — just opens.
- If it can't resolve to exactly one file, it stops and asks rather than guessing or widening scope.

## Voice-fuzziness

Handled inline today via a calibration table embedded in the command prompt:

- Folder aliases (e.g. "my get hub" → `~/myghub/`, "co decks" → `~/.codex/`).
- Filename aliases (e.g. "claude dot M D" → `CLAUDE.md`).
- General rule: spelled-out extensions map to dotted ones ("dot M D" → `.md`, "dot T S" → `.ts`, "dot J S O N" → `.json`).

The table is illustrative, not exhaustive — the command extrapolates from it and asks if genuinely ambiguous between two scope targets.

## Output

- **Success:** `Opened <abs path>`.
- **Ambiguous:** numbered list + "Which one?".
- **Miss:** `Not found in scope: <what>`.

Nothing else.

## Backlog

- **Externalize voice-fuzziness.** Once a dedicated voice-text / fuzzy-resolver utility exists in its own folder (likely `~/myquickie/mycommands/<voice-resolver>/` or graduated to `~/myghub/`), strip the inline alias table from `myopen.md` and call into the shared resolver. Keeps voice-mapping logic in one place across commands that need it (e.g. any future `myedit`, `myread`, etc.).
