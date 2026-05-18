# Codebase Map

*Last refreshed: 2026-05-18*

Grouped by top-level location, in filesystem order.

## Root files

- `CLAUDE.md` — project instructions for this repo
- `AGENTS.md` — Codex global rules (→ `~/.codex/AGENTS.md`)
- `README.md` — home-directory layout (`~/mylab`, aliases, auto-memory)
- `restructure-plan.md` — restructure planning doc (historical; superseded note at top)
- `claude-link-commands.sh` — links `claude-skills/` into `~/.claude/` (flow in `how-it-works.md`)
- `codex-link-commands.sh` — links `codex-skills/` into `~/.codex/` (sibling installer)

## raycast/ — Raycast script commands

- `claude-open-quickie.sh` · `claude-open-myghub.sh` · `claude-open-project.sh` — launch Claude in a target dir
- `regenerate-project-picker.sh` — rebuild the project-picker list
- `new_evernote.applescript` — create a new Evernote note

## global/ — Global agent rules

- `CLAUDE.md` — Claude Code global rules (→ `~/.claude/CLAUDE.md`)

## claude-skills/ — Claude skills folder. symlinked too

- `jm-transcript/` — append session to a project's `transcript.md`
- `mybedtime/` — write `BEDTIME.md` to resume a fresh session
- `myclaude/` — promote polished global Claude rules into `global/CLAUDE.md`
- `mydoc-checkpoint/` — capture in-flight work into `overview/notes.md`
- `mydoc-overview/` — create/sync the `overview/` folder (this skill)
- `mydoc-spec/` — guided interview to create a versioned `spec-vN.md`
- `myinit/` — initialize a project with the standard layout
- `myloop/` — run 5 rule variants through Codex CLI, report the best
- `myopen/` — open a file in TextEdit (defaults to in-focus file)
- `myport/` — open the localhost dev server in Safari
- `mytodo/` — capture a quick item to the mygeorge `todos.md` Inbox
- `myverify-innerloop/` — self-verification hooks for a TS/React project
- `myverify-ui/` — verify a just-built UI feature via `ui-verify`
- `mywriter/` — rewrite text per the external `jm-writer` rules

## codex-skills/ — Codex prompt and skill copies

- `mydoc-overview.md` · `mydoc-checkpoint.md` · `mydoc-spec.md` — flat Codex prompts installed by `codex-link-commands.sh`
- `myagents.md` — flat prompt for promoting polished global rules into `AGENTS.md`
- `mydoc-overview/` · `mydoc-checkpoint/` · `mydoc-spec/` · `myagents/` — packaged skill-form copies (`SKILL.md`, `references/`, `agents/`)

## terminal/ — shell setup

- `zshrc` — tracked backup of `~/.zshrc` (synced by `zsync`)
- `shortcuts/` — global PATH scripts (`mycmds` lists them)
- `ghostty/` — Ghostty terminal config

## tuning/ - for tuning agent responses and building a good/bad corpus to optimize from later

- good/bad agent-response corpus; see its own `README.md`
