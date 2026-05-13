# mydoc-checkpoint

## purpose

`/mycheckpoint` captures the *uncommitted* substance of a session — ideas surfaced, threads opened, decisions made, items worth considering for `CLAUDE.md` — by appending to the `## Checkpoint` section of the project's `overview.md`. Distinct from `/mydoc-overview` (which owns the rest of `overview.md`) and `/mystatus` (still writes `STATUS.md` for now). The Checkpoint section accumulates over the life of the project; resolved threads get moved to a `### Resolved` subsection rather than deleted.

Personal trigger: the fresh-session prompt emitted after each run, pasted into a new session, used to burn ~50K tokens before producing meaningful work. V2 cuts this by dropping `STATUS.md` from the default pull and capping the first response at ~200 words with A/B/C/D next-step options.

## status

V2 deployed (2026-05-11). `/mycheckpoint` now writes to `overview.md`'s `## Checkpoint` section instead of maintaining its own `CHECKPOINT.md`. `/mydoc-overview` was updated in lockstep to scaffold the empty `## Checkpoint` section with four subsections (`### Ideas`, `### Open threads`, `### Resolved`, `### CLAUDE.md candidates`) in the append-only zone.

`/mystatus` is unchanged — still writes `STATUS.md`. Will revisit consolidation later once we've used the new flow.

Tech stack: single markdown file at `~/mylab/ai-setup/skills/mydoc-checkpoint/mycheckpoint.md`, symlinked from `~/.claude/commands/mycheckpoint.md`. No code.

## next

- Migrate existing `CHECKPOINT.md` files across projects (mygeorge, mybrain, mycli, myteacher) into their respective `overview.md` `## Checkpoint` sections. Manual one-time op per project.
- After ~2 weeks of use, decide whether `/mystatus` also folds into `overview.md` (probably into `## status` if it stays a snapshot section, or gets deleted if redundant).

## how it works

When invoked, the deployed command:

1. Reads `overview.md` at project root. If missing, tells the user to run `/mydoc-overview` first and stops. If `## Checkpoint` or any of its four subsections is missing, tells the user to re-run `/mydoc-overview` and stops.
2. Scans the current conversation for: new ideas, open threads, threads resolved in this session, CLAUDE.md candidates.
3. Appends new entries to the bottom of the appropriate subsection. Moves newly-resolved threads from `### Open threads` to `### Resolved` with a `— RESOLVED YYYY-MM-DD —` marker. Never edits or deletes any other entry.
4. Emits a summary line + a copy-pasteable fresh-session prompt pointing at `overview.md` only, ending with a one-line "Next:" action and a fixed-phrasing constraint capping the first response at ~200 words with A/B/C/D options.

## known issues

- Cold-start cost is now ~5–10K lower vs. V1 (no STATUS.md pull, ≤200-word first response, A/B/C/D structure suppresses extended thinking on turn one). Structural cold-start (~20–30K from system prompt + tool schemas + global CLAUDE.md) is unchanged — that's Lever C, still deferred.
- Existing `CHECKPOINT.md` files in legacy projects are not auto-migrated. They sit alongside the new `## Checkpoint` section until manually moved.

## notes

decision: Subsection headings (`### Ideas` / `### Open threads` / `### Resolved` / `### CLAUDE.md candidates`) instead of prefixed lines. Easier to scan when the section grows; matches the mental model from CHECKPOINT.md.

decision: `## Checkpoint` lives in `/mydoc-overview`'s append-only zone, below `<!-- APPEND-ONLY BELOW -->`. `/mydoc-overview` scaffolds the empty section and never writes content there again. `/mycheckpoint` is the only writer.

decision: CLAUDE.md candidates are *captured*, never *promoted*. The human decides what graduates to CLAUDE.md.

decision: `/mystatus` stays as a separate command writing `STATUS.md` for now. Two commands, but only one shared file (`overview.md`) for the captured material. Consolidate later if it becomes friction.

open: should existing `CHECKPOINT.md` files in mygeorge / mybrain / mycli / myteacher be migrated now, or left until the next time `/mycheckpoint` is run in each? Closes when we pick a migration approach (or decide migration isn't needed).

open: does `/mystatus` get deleted, merged, or kept after a few weeks of running the new flow? Closes when we re-evaluate.

## pointers

- `mycheckpoint.md` (in this folder) — the deployed V2 source. Symlinked from `~/.claude/commands/mycheckpoint.md`.
- `~/mylab/ai-setup/skills/mydoc-overview/SKILL.md` — defines the `## Checkpoint` section's protection zone and format rules; coordinates with this skill.
