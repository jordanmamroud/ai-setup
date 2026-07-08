# Codebase Map

*Last refreshed: 2026-07-07*

Grouped by top-level location, in filesystem order.

## Root files

- `CLAUDE.md` — project instructions for this repo
- `README.md` — home-directory layout (`~/mylab`, aliases, auto-memory)
- `claude-link-commands.sh` — links Claude command entries from `skills/` into `~/.claude/` (flow in `how-it-works.md`)
- `codex-link-commands.sh` — links Codex prompt and packaged skill entries from `skills/` into `~/.codex/` (sibling installer)

## raycast/ — Raycast script commands

- `claude-open-quickie.sh` · `claude-open-myghub.sh` · `claude-open-project.sh` — launch Claude in a target dir
- `regenerate-project-picker.sh` — rebuild the project-picker list
- `new_evernote.applescript` — create a new Evernote note

## agent-rules/ — Agent rules

- `CLAUDE.md` — Claude Code agent rules (→ `~/.claude/CLAUDE.md`)
- `AGENTS.md` — Codex agent rules (→ `~/.codex/AGENTS.md`)

## skills/ — global Claude/Codex skill source

- `g5-manager/` — read-only audit of the personal Google Cloud setup (Codex-only)
- `jm-doc/` — project-doc router: `checkpoint` / `spec` / `readme` / `arc` modes behind one `/jm-doc` command (replaces the retired `mydoc-*` family)
- `jm-transcript/` — append session to a project's `transcript.md`
- `myagents/` — promote polished Codex agent rules into `agent-rules/AGENTS.md` (Codex-only)
- `myclaude/` — promote polished Claude agent rules into `agent-rules/CLAUDE.md`
- `myopen/` — open a file in TextEdit (defaults to in-focus file)
- `myport/` — open the localhost dev server in Safari
- `myverify-innerloop/` — self-verification hooks for a TS/React project
- `myverify-ui/` — verify a just-built UI feature via `ui-verify`

## km-skills/ — Kitchen Magic workspace skills

Client-scoped skills staged here until they move to a dedicated workspace.

- `jm-hubspotlps/` — HubSpot CMS landing-page workflows for the Kitchen Magic theme
- `km-landing-page-audit/` — visitor-perspective QA audit of live Kitchen Magic landing pages
- `km-video-cataloger/` · `km-video-clipper/` — Kitchen Magic video asset skills (Codex-only)

Installed via hand-set symlinks in `~/.codex/skills/` — `codex-link-commands.sh` does not scan this folder yet.

## archive/ — legacy migration copies and retired skills

- `archive/skills/` — retired skills, moved here folder-intact so they can be revived with a single `mv` (includes the superseded `mydoc-*` family, `mybedtime`, `myinit`, `myloop`, `mytodo`, `mywriter`, `jm-harden`).
- `archive/claude-skills/` and `archive/codex-skills/` are kept temporarily as rollback sources while the shared `skills/` layout proves out.
- Do not edit these first; edit `skills/<name>/` and rerun the relevant link script.

## terminal/ — shell setup

- `zshrc` — redacted tracked backup of `~/.zshrc` (synced by `zsync`)
- `shortcuts/` — global PATH scripts (`mycmds` lists them)
- `ghostty/` — Ghostty terminal config

## tuning/ - for tuning agent responses and building a good/bad corpus to optimize from later

- good/bad agent-response corpus; see its own `README.md`
