# mydoc-checkpoint

## purpose

`/mydoc-checkpoint` captures the *uncommitted* substance of a session — ideas surfaced, threads opened, decisions made, items worth considering for `CLAUDE.md` — by appending to the four checkpoint sections (`## Ideas`, `## Open threads`, `## Resolved`, `## CLAUDE.md candidates`) of the project's `overview/notes.md`. Distinct from `/mydoc-overview` (which owns the rest of the `overview/` folder) and `/mystatus` (still writes `STATUS.md` for now). The sections accumulate over the life of the project; resolved threads get moved from `## Open threads` to `## Resolved` rather than deleted.

Personal trigger: the fresh-session prompt emitted after each run, pasted into a new session, used to burn ~50K tokens before producing meaningful work. V2 cuts this by dropping `STATUS.md` from the default pull and capping the first response at ~200 words with A/B/C/D next-step options.

## status

Deployed. `/mydoc-checkpoint` writes to the four checkpoint sections of `overview/notes.md` — top-level `## Ideas` / `## Open threads` / `## Resolved` / `## CLAUDE.md candidates` — instead of maintaining its own `CHECKPOINT.md`. It is self-sufficient: if `overview/notes.md` (or the `overview/` directory) is missing it scaffolds it, and it repairs a missing `# Notes` h1, `## Observations` placeholder, or any missing checkpoint heading. It no longer requires `/mydoc-overview` to have run first. `/mydoc-overview` owns the rest of the `overview/` folder and scaffolds these four sections empty in `notes.md`.

Architecture history: V1 used a standalone `CHECKPOINT.md`. V2 (2026-05-11) moved capture into a single `overview.md` `## Checkpoint` section with `###` subsections. The current model supersedes both — a dedicated `overview/notes.md` with top-level `##` sections, no `<!-- APPEND-ONLY BELOW -->` marker, ownership enforced file-level by `/mydoc-overview`.

`/mystatus` is unchanged — still writes `STATUS.md`. Will revisit consolidation later once we've used the new flow.

Tech stack: single markdown file at `~/mylab/ai-setup/claude-skills/mydoc-checkpoint/SKILL.md`, symlinked from `~/.claude/commands/mydoc-checkpoint.md`. No code.

Codex twin: `~/mylab/ai-setup/codex-skills/mydoc-checkpoint.md` is a hand-maintained Codex duplicate of this skill — frontmatter stripped, `CLAUDE.md` references retargeted to `AGENTS.md` — symlinked to `~/.codex/prompts/mydoc-checkpoint.md` by `codex-link-commands.sh`. It is a separate file, **not a symlink**: the Claude and Codex forms may diverge, and a behavior change here must be ported by hand. Consequence: the Codex form scaffolds `## AGENTS.md candidates` in `overview/notes.md` while the Claude form scaffolds `## CLAUDE.md candidates`, so a project driven by both agents will carry two differently-named candidate sections.

## next

- Migrate existing `CHECKPOINT.md` files across projects (mygeorge, mybrain, mycli, myteacher) into their respective `overview.md` `## Checkpoint` sections. Manual one-time op per project.
- After ~2 weeks of use, decide whether `/mystatus` also folds into `overview.md` (probably into `## status` if it stays a snapshot section, or gets deleted if redundant).

## how it works

When invoked, the deployed command:

1. Ensures `overview/notes.md` exists at project root. If missing, creates it (and the `overview/` directory) with `# Notes`, `## Observations` + the `(user observations / notes go here)` placeholder, then the four empty checkpoint headings. If it exists but lacks the `# Notes` h1, `## Observations`, or any checkpoint heading, repairs the missing piece(s) without reordering. Never requires `/mydoc-overview` first.
2. Reads `overview/notes.md` so it doesn't duplicate, then scans the current conversation for: new ideas, open threads, threads resolved in this session, CLAUDE.md candidates.
3. Appends new entries to the bottom of the matching section. Moves newly-resolved threads from `## Open threads` to `## Resolved` with a `— RESOLVED YYYY-MM-DD — <resolution + pointer>` marker. Never writes to `## Observations`; never edits or deletes any other entry.
4. Emits a summary line (absolute path + one-line of what changed) + a copy-pasteable fresh-session prompt pointing at the full `overview/` docs for context and `overview/notes.md` for in-flight checkpoint sections, ending with a one-line "Next:" action and the fixed-phrasing constraint capping the first response at ~200 words with A/B/C/D options.

## known issues

- Cold-start cost is now ~5–10K lower vs. V1 (no STATUS.md pull, ≤200-word first response, A/B/C/D structure suppresses extended thinking on turn one). Structural cold-start (~20–30K from system prompt + tool schemas + global CLAUDE.md) is unchanged — that's Lever C, still deferred.
- Existing `CHECKPOINT.md` files in legacy projects are not auto-migrated. They sit alongside the new `## Checkpoint` section until manually moved.

## notes

decision: Subsection headings (`### Ideas` / `### Open threads` / `### Resolved` / `### CLAUDE.md candidates`) instead of prefixed lines. Easier to scan when the section grows; matches the mental model from CHECKPOINT.md.

decision: `## Checkpoint` lives in `/mydoc-overview`'s append-only zone, below `<!-- APPEND-ONLY BELOW -->`. `/mydoc-overview` scaffolds the empty section and never writes content there again. `/mydoc-checkpoint` is the only writer.

decision: CLAUDE.md candidates are *captured*, never *promoted*. The human decides what graduates to CLAUDE.md.

decision: `/mystatus` stays as a separate command writing `STATUS.md` for now. Two commands, but only one shared file (`overview.md`) for the captured material. Consolidate later if it becomes friction.

open: should existing `CHECKPOINT.md` files in mygeorge / mybrain / mycli / myteacher be migrated now, or left until the next time `/mydoc-checkpoint` is run in each? Closes when we pick a migration approach (or decide migration isn't needed).

open: does `/mystatus` get deleted, merged, or kept after a few weeks of running the new flow? Closes when we re-evaluate.

## pointers

- `SKILL.md` (in this folder) — the deployed source. Symlinked from `~/.claude/commands/mydoc-checkpoint.md`.
- `~/mylab/ai-setup/claude-skills/mydoc-overview/SKILL.md` — owns the `overview/` folder; scaffolds the four checkpoint sections of `overview/notes.md` empty and defines their file-level ownership and format rules. Coordinates with this skill.
- `~/mylab/ai-setup/codex-skills/mydoc-checkpoint.md` — the Codex duplicate (`CLAUDE.md`→`AGENTS.md`). Separate file; keep in sync with this skill by hand if behavior changes.
