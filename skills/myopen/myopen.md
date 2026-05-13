---
description: Open a file in TextEdit. With no argument, opens the file currently in focus in the conversation. With an argument, resolves it within the user's known folders only — never searches the whole filesystem.
---

Open a file in TextEdit using `open -a TextEdit "<absolute path>"`.

Argument (may be empty):

$ARGUMENTS

## Hard rules

- **Never** search outside the scope below. No `find /`, no `mdfind`, no `locate`, no recursive search of `~`.
- **Never** read the file before opening — just open it. This command is `open`, not `read`.
- If you cannot resolve to exactly one file, **stop and ask** — don't guess and don't widen scope.

## Search scope

Only these paths exist for this command:

- `~/myghub/`     — graduated / serious projects
- `~/myquickie/` — scratch / in-progress ideas
- `~/.claude/`    — Claude Code config, memory, settings, hooks
- `~/.codex/`     — Codex CLI config
- `~/.zshrc`      — single file

## Resolution

### No argument

Open the file currently in focus in this conversation — the file most recently read, edited, or named by the user. If multiple plausible candidates, list them numbered and ask which. If none, ask the user to specify.

### With argument

The argument is dictated by voice, so be tolerant of spacing and homophones. It can be:

1. **A folder + filename** (e.g. "plot.md in myghub", "myghub plot.md", "my G hub plot dot M D"):
   - Resolve the folder via the alias table below.
   - `find <folder> -iname "<filename>"` (recursive, case-insensitive).
2. **A filename only** (e.g. "plot.md"):
   - Run the same `find -iname` across **all scope folders**.
3. **A folder only** (rare): ask which file.

If exactly one match → open it. If multiple → numbered list, ask. If zero → say "not found in scope" and stop.

## Voice-to-text fuzziness

The user dictates these names, so the input is often misheard. The canonical targets are the entries in **Search scope** above; your job is to map the spoken phrase to whichever of those targets it most plausibly meant.

Be liberal: ignore spacing, case, punctuation, and obvious homophones. The lists below are *examples of the kind of drift to expect*, not a closed set — extrapolate from them. The rule isn't "match this list," it's "use these to calibrate how loose to be."

**Folders** (target ← examples of how it might be heard):

- `~/myghub/`    ← "my g hub", "my get hub", "my G up you", "my hub", "myg hub", "my gee hub"
- `~/myquickie/` ← "my quickie", "my quicky", "my quick", "myquick"
- `~/.claude/`   ← "claude", "dot claude", "cloud", "clawed"
- `~/.codex/`    ← "codex", "dot codex", "co decks"
- `~/.zshrc`     ← "zshrc", "z shirt see", "dot zshrc", "shell config"

**Filenames** (target ← examples):

- `CLAUDE.md` ← "claude dot M D", "cloud M D", "cloud dot M D", "claude M D"
- `plot.md`   ← "plot dot M D", "plot M D"
- General rule: spelled-out extensions map to dotted ones ("dot M D" / "M D" → `.md`, "dot T S" → `.ts`, "dot J S O N" → `.json`, etc.).

If a spoken phrase is genuinely ambiguous between two scope targets — or doesn't plausibly point at any of them — ask. Don't widen the search to compensate.

## Opening

```
open -a TextEdit "<absolute path>"
```

## Output

- **Success:** one line — `Opened <absolute path>`.
- **Ambiguous:** numbered list of matches, then "Which one?".
- **Miss:** one sentence — `Not found in scope: <what you looked for>`.

Nothing else.
