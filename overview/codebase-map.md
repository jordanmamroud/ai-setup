# Codebase Map

*Last refreshed: 2026-07-14*

Grouped by top-level location, in filesystem order.

## Root files

- `CLAUDE.md` — project instructions for this repo
- `AGENTS.md` — project instructions for Codex inside this repo
- `README.md` — current setup guide for agent rules, skills, hooks, shell aliases, and rebuild steps
- `claude-link-commands.sh` — links Claude command entries and opt-in Claude skills from `skills/` into `~/.claude/` (flow in `how-it-works.md`)
- `codex-link-commands.sh` — links Codex prompt and packaged skill entries from `skills/` into `~/.codex/` (sibling installer)

## raycast/ — Raycast script commands

- `claude-open-quickie.sh` · `claude-open-myghub.sh` · `claude-open-project.sh` — launch Claude in a target dir
- `regenerate-project-picker.sh` — rebuild the project-picker list
- `new_evernote.applescript` — create a new Evernote note

## agent-rules/ — Agent rules

- `CLAUDE.md` — Claude Code agent rules (→ `~/.claude/CLAUDE.md`)
- `AGENTS.md` — Codex agent rules (→ `~/.codex/AGENTS.md`)

## skills/ — global Claude/Codex skill source

- `brainstorming/` — design/spec discussion before creative or implementation work
- `define-outcome/` — lightweight alignment check for defining done
- `g5-manager/` — read-only audit of the personal Google Cloud setup (Codex-only)
- `google-ads-mcp-cloud-run/` — Google Ads MCP local and Cloud Run workflow notes
- `jm-council/` — OpenRouter model council fan-out and analysis workflow
- `jm-doc/` — project-doc router: `checkpoint` / `spec` / `readme` / `arc` modes behind one `/jm-doc` command (replaces the retired `mydoc-*` family)
- `jm-handoff/` — handoff command source
- `jm-skill-creator/` — create, test, and improve Codex/Claude skills
- `jm-transcript/` — append session to a project's `transcript.md`
- `myagents/` — promote polished Codex agent rules into `agent-rules/AGENTS.md` (Codex-only)
- `web-perf/` — web performance audits with Chrome DevTools MCP
- `writing-plans/` — implementation plan writing support

## km-skills/ — Kitchen Magic workspace skills

Client-scoped skills staged here until they move to a dedicated workspace.

- `ad-hook-visuals/` — Kitchen Magic ad-hook visual ideation
- `jm-hubspotlps/` — HubSpot CMS landing-page workflows for the Kitchen Magic theme
- `km-library/` — Kitchen Magic library reference workflow
- `km-landing-page-audit/` — visitor-perspective QA audit of live Kitchen Magic landing pages
- `km-video-cataloger/` · `km-video-clipper/` — Kitchen Magic video asset skills (Codex-only)

Installed via hand-set symlinks in `~/.codex/skills/` — `codex-link-commands.sh` does not scan this folder yet.

## archive/ — legacy migration copies and retired skills

- `archive/skills/` — retired skills, moved here folder-intact so they can be revived with a single `mv` (includes the superseded `mydoc-*` family, `mybedtime`, `myinit`, `myloop`, `mytodo`, `mywriter`, `jm-harden`).
- `archive/claude-skills/` and `archive/codex-skills/` are kept temporarily as rollback sources while the shared `skills/` layout proves out.
- Do not edit these first; edit `skills/<name>/` and rerun the relevant link script.

## hooks/ — optional Codex hooks

- `hooks.json` — sample/active hook config when linked into a Codex config layer
- `pre_tool_use_bash_guard.py` — shell safety guard
- `pre_tool_use_protected_files.py` — protected file guard
- `user_prompt_secret_scan.py` — prompt secret scanner
- `post_tool_use_changed_file_checks.py` and `stop_changed_tree_checks.py` — changed-file checks

## terminal/ — shell setup

- `zshrc` — redacted tracked backup of `~/.zshrc` (synced by `zsync`)
- `shortcuts/` — global PATH scripts (`mycmds` lists them)
- `ghostty/` — Ghostty terminal config

## tuning/ - for tuning agent responses and building a good/bad corpus to optimize from later

- good/bad agent-response corpus; see its own `README.md`
