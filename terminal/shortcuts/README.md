# shortcuts

Global command shortcuts that live on `PATH` so they work everywhere — terminals, Claude
Code's `!` prefix, scripts, cron. Real scripts on `PATH` (not shell aliases) because
shell aliases only expand in interactive shells, while `!` opens a non-interactive shell.

The primary entry point is **`m`**, a fuzzy dispatcher — see Layout below.

## Layout

Real scripts live directly in `~/mylab/ai-setup/terminal/shortcuts/` and are on `PATH`
via line 2 of `~/.zshrc`. Copy `terminal/shortcuts/` to a new machine, add the `PATH`
line, you have all your commands.

The primary entry point is **`m`** — a fuzzy dispatcher. Type `!m <fuzzy-name> [args]`
and it resolves to the closest match (exact → prefix → subsequence), then runs it.
`!m` alone opens an interactive picker (uses `fzf` if installed, plain list otherwise).
This means short names like `sg` (for `savegood`) work automatically without any
alias file — `m` figures it out from the canonical name.

## To add a new shortcut `<name>`

1. Write the script at `~/mylab/ai-setup/terminal/shortcuts/<name>`.
2. `chmod +x ~/mylab/ai-setup/terminal/shortcuts/<name>`
3. Add a bullet to the "Existing shortcuts" list below so `mycmds` shows it.
4. New shells (and new Claude sessions) pick it up immediately. No reload.

**Existing shortcuts:**

- `m [name] [args]` — fuzzy dispatcher. Resolves `name` against this list (exact →
  prefix → subsequence) and runs the match. No args opens an interactive picker.
- `savegood` — save a good response to `~/mylab/ai-setup/tuning/good-responses.md`;
  source auto-fills to the current working directory (e.g. `~/mylab/ai-setup`)
- `savebad` — save a bad response to `~/mylab/ai-setup/tuning/bad-responses.md`;
  source auto-fills to the current working directory (e.g. `~/mylab/ai-setup`)
- `claudemd` — open every `CLAUDE.md` affecting the current directory
  (walks cwd → `/`, plus `~/.claude/CLAUDE.md`) as tabs in one VS Code window
- `newfile <name>` — create file(s) in the current directory and open them
  in VS Code (accepts multiple names)
- `mycmds` — print this list of shortcuts (reads from this README)
- `cx [args]` — launch Codex with approvals and sandbox bypassed; intended for `m cx`
- `ccd [args]` — launch Claude Code with permission checks skipped; intended for `m ccd`
- `openfolder [path]` — open the current directory (or given path) in a new VS Code window
- `zopen` — open `~/.zshrc` in TextEdit (the top of that file has the quick-reference cheat sheet)
- `zsync ["message"]` — copy live `~/.zshrc` → `ai-setup/terminal/zshrc` backup with API keys redacted, then commit and push
- `vopen [repo-name]` — open VS Code; with a repo name, opens that folder inside `~/mylab/main`
- `gp "message"` — stage all changes, commit, and push (skips empty commits, refuses outside a repo)
- `gpa "message"` — `git add . && commit && push` (one-liner, no safety checks)
- `gdf <path> ["message"]` — `git rm -r <path>`, commit, and push (commit message optional)
- `gnew <repo-name> ["message"]` — `git init` + `gh repo create` + push (uses GitHub user `jordanmamroud`)
- `grename <old> <new>` — `git mv` + auto-detect file/folder + commit + push
- `clone <url>` — `git clone` into the current directory; auto-appends `.git` if missing.
  In interactive shells, a `~/.zshrc` wrapper also `cd`s into the new repo.

## Note on `savegood` / `savebad`

The scripts live here, but they write to the agent-response corpus at
`~/mylab/ai-setup/tuning/{good,bad}-responses.md`. The corpus is separate from
the shortcut machinery — it's training material for refining how I instruct agents,
maintained in the `tuning/` folder.
