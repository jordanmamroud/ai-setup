# mydoc-overview

Maintains a standardized `overview/` folder in any project: high-level orientation for a reader trying to understand what the project is and how the pieces fit together. One file per section so an agent pointed at a single file stays on-task.

## What it does

**Triggers:** the user runs `/mydoc-overview`.

1. Check for `overview/` at the project root.
   - If missing → scaffold the folder per the **Folder template** below. Any pre-existing `overview.md` at the root is ignored (left in place, not migrated).
   - If present but incomplete → repair: write any missing file from the template. Existing files are handled per their tier (code-derived rewritten, others left alone).
   - If complete → re-derive `overview/how-it-works.md` and `overview/codebase-map.md` in place, refreshing their timestamps. Never touch `README.md` or `notes.md`.
2. Report what changed.

Scope is strictly the `overview/` folder. Project README, AGENTS.md, spec.md, etc. are out of scope.

## File ownership

Ownership is file-level. No in-file markers.

| File | Tier | Permission |
|---|---|---|
| `overview/README.md` | Human-owned | Agent drafts the Summary on first-run scaffold only. Never modify after. |
| `overview/how-it-works.md` | Code-derived | Rewrite in place each run. Refresh `*Last refreshed: ...*` timestamp. |
| `overview/codebase-map.md` | Code-derived | Rewrite in place each run. Refresh `*Last refreshed: ...*` timestamp. |
| `overview/notes.md` | Append-only | Mixed ownership. `## Observations` is user-directed (agent writes only when the user explicitly asks). The four checkpoint sections (`## Ideas`, `## Open threads`, `## Resolved`, `## AGENTS.md candidates`) are owned by `/mydoc-checkpoint`; `/mydoc-overview` scaffolds them empty and never writes there again. One allowed in-place edit: marking/moving a resolved entry. |

## Format: `overview/README.md`

Two parts: the Summary (hand-written prose) and the folder index (frozen scaffold).

The Summary is the only part the agent ever drafts — on first-run scaffold. After that, never modify.

Summary rules:
- One paragraph, roughly 3–5 sentences.
- Lead sentence: what this is.
- Then: why it exists, what problem it solves, who it's for.
- Optionally close with one sentence on how to use it or current status.
- Present tense. No boilerplate ("This project aims to...").
- Prose only — no bullets, sub-headings, or links.

The folder index is fixed by the **Folder template** below. Don't modify it.

### Example Summary

```markdown
## Summary
`mydoc-overview` is a Codex prompt that maintains a standardized `overview/` folder for any project. It scaffolds the folder from a template on first run and re-syncs the code-derived files on subsequent runs, leaving the human-owned Summary and the append-only `notes.md` alone. Triggered with `/mydoc-overview`.
```

## Format: `overview/how-it-works.md`

Describes the code as it currently exists. Do not document intended, planned, or aspirational behavior — that belongs in `spec.md`. If a feature isn't implemented yet, don't include it.

Never write abstract paragraphs. Write a numbered, chronological flow.

Defaults:
- File starts with `# How it works` followed by the `*Last refreshed: YYYY-MM-DD*` line.
- Then `**Triggers:**` listing what initiates the flow. One trigger inline (e.g. `**Triggers:** the user runs /refresh.`); multiple triggers as a bulleted list. Same flow with multiple triggers does NOT become multiple flows.
- Then a numbered list of steps. Each step is one line. Reference files inline using backticks where they appear, not in a separate list.
- Close with one optional tail line capturing the *why* or a key consequence.

Add structure only when complexity demands it:
- **Multiple flows:** if the project has genuinely different flows (different *steps*, not just different triggers), give each a `## Flow name` subheading and apply the above to each.
- **Branches:** if a step has meaningful non-happy-path behavior (auth failure, retry, fallback), add it as a sub-bullet prefixed with `↳ Branch:`. Don't fork the main flow.

Bias toward terse. If a step needs more than one line, the flow is wrong scope — split it or push detail elsewhere.

### Example

```markdown
# How it works

*Last refreshed: 2026-05-11*

**Triggers:** use `/mydoc-checkpoint` command, or `!mydoc-checkpoint` from inside Codex.

1. Scans the current conversation for new ideas / open threads / threads now resolved / AGENTS.md candidates.
2. Reads existing `overview/notes.md` if present so it doesn't duplicate.
3. Updates the four checkpoint sections in `overview/notes.md` in place — appends new entries, moves resolved threads from `## Open threads` to `## Resolved` with a `— RESOLVED YYYY-MM-DD` marker.
4. Emits a copy-pasteable fresh-session prompt that pulls `overview/notes.md`, ending with a one-line "Next:" action.

The fresh-session prompt is the proximate cause of the 50K cold-start.
```

## Format: `overview/codebase-map.md`

A spatial map of the repo, **grouped by top-level location** so it scans without wrapping into a wall of text.

Rules:
- File starts with `# Codebase Map` followed by the `*Last refreshed: YYYY-MM-DD*` line, then one short orienting sentence.
- Group by top-level location in filesystem order: a `## Root files` section first, then one `## <dir>/ — <one-line purpose>` section per top-level directory. The directory's own description lives in its heading; the bullets under it describe its immediate children.
- Blank line after each heading. Entries are terse one-line bullets, one per file or immediate subfolder. Keep each description a short phrase — short enough not to wrap (aim under ~70 chars after the backticked name).
- List everything a reader needs to navigate, **even if it's already mentioned in `how-it-works.md`** — completeness over de-duplication. (This reverses the earlier de-dup rule, by user preference.)
- Collapse siblings that share a role onto one line with `·` separators (e.g. several `claude-open-*.sh` scripts) rather than a bullet each.
- One line per entry. If a file's role won't fit in a short phrase, describe it at the folder level instead.
- Don't nest deeper than one level under a heading. A subfolder that itself needs a breakdown gets its own `##` section, not nested bullets.
- Skip noise: `node_modules/`, `.git/`, lockfiles, build output, anything in `.gitignore`.

### Example

```markdown
# Codebase Map

*Last refreshed: 2026-05-11*

Grouped by top-level location, in filesystem order.

## Root files

- `package.json` — deps and npm scripts
- `README.md` — project overview and setup
- `Makefile` — build / lint / test targets

## src/ — application source

- `api/` — REST handlers
- `db/` — schema and migrations
- `cli.ts` · `index.ts` — entry points

## tests/ — Vitest specs

- `unit/` — fast isolated tests
- `e2e/` — Playwright flows
```

## Format: `overview/notes.md`

Append-only file with two ownership zones — never delete or reword existing entries in either.

File structure (sections appear in this fixed order):

1. `## Observations` — **user-directed.** Agent writes here only when the user explicitly asks to log something. Uses prefix-line format with `ISSUE:` / `IDEA:` / `NOTE:` / `Q:` prefixes (documented below).
2. `## Ideas` — **owned by `/mydoc-checkpoint`.** Bulleted entries.
3. `## Open threads` — **owned by `/mydoc-checkpoint`.** Bulleted entries.
4. `## Resolved` — **owned by `/mydoc-checkpoint`.** Bulleted entries, arrived here by being moved out of `## Open threads`.
5. `## AGENTS.md candidates` — **owned by `/mydoc-checkpoint`.** Bulleted entries.

`/mydoc-overview` scaffolds all five section headings on first run (with the `## Observations` placeholder line) and never writes content there again. Resolution is the only allowed in-place edit, with two different mechanics: Observations entries are marked in place with ` → resolved YYYY-MM-DD`; checkpoint Open threads are marked `— RESOLVED YYYY-MM-DD —` and moved to `## Resolved`. See the per-zone rule blocks below for details.

### Rules for `## Observations` (user-directed)

- One entry per line below the legend: `PREFIX: <content>  (YYYY-MM-DD)`.
- Prefixes are uppercase and case-sensitive.
- Resolution edit: append ` → resolved YYYY-MM-DD` to the original entry. Nothing else.

Prefixes:
- `ISSUE:` known issue / heads-up for the next reader
- `IDEA:` future-version thought, not committed
- `NOTE:` random observation
- `Q:` open question

### Rules for the four checkpoint sections (owned by `/mydoc-checkpoint`)

- Each entry is a bulleted line. New entries append to the **bottom** of their subsection (chronological). Don't reorder existing ones.
- **For Ideas:** name what's worth remembering and *why* (the implication, risk, or surprise), not just the observation.
- **For Open threads:** name what closing the thread looks like, so the next reader knows when it's done.
- **For Resolved:** entry format is `<title> — RESOLVED YYYY-MM-DD — <one-line resolution + pointer>`. Items arrive here only by being moved out of `## Open threads`, not by being written here directly.
- **For AGENTS.md candidates:** captured suggestions only. Never auto-promoted to AGENTS.md — the human decides.
- Resolution edit: move an Open thread to Resolved (append RESOLVED marker, move the line). Nothing else.

### Example

```markdown
# Notes

## Observations
(user observations / notes go here)

ISSUE: cache invalidates silently on macOS  (2026-04-12)
NOTE: tested on macOS only  (2026-05-01)
Q: should overview link to spec or stay independent?  (2026-05-11)

## Ideas
- Caching the parsed AST would cut cold-start by ~30%. Risk: invalidation on file change is non-trivial.

## Open threads
- Should the fresh-session prompt include a "no extended thinking" hint? Closes when we A/B test once.

## Resolved
- Drop STATUS.md from fresh-session prompt — RESOLVED 2026-05-11 — applied in mydoc-checkpoint/SKILL.md.

## AGENTS.md candidates
- Add: "when editing the zshrc backup, always test in a new shell before committing."
```

## First-run scaffolding

When creating a new `overview/` folder from the template:

1. Create the `overview/` directory at the project root.
2. Write all four files using the **Folder template** below as starting content.
3. `README.md`: replace `<project name>` with the actual project name (folder name, then `package.json` / `pyproject.toml` / `Cargo.toml` if available). Replace the Summary placeholder with a one-paragraph draft inferred from the repo (README, project metadata, top-level code). If the repo is too sparse to draft a meaningful Summary, keep the visible placeholder. Subsequent runs must never touch Summary again.
4. `how-it-works.md` and `codebase-map.md`: replace the placeholder with content derived from the repo; set `*Last refreshed: ...*` to today's date. If the repo is too sparse to derive real content, keep the visible placeholder.
5. `notes.md`: write verbatim from the template.

On every subsequent run, refresh the timestamps in `how-it-works.md` and `codebase-map.md` to today's date regardless of whether content changed.

## Placeholder rule

When `/mydoc-overview` can't derive real content for a section (empty project, no flows yet, sparse repo), leave a visible italic placeholder rather than fabricating thin content. Use the same wording as in the **Folder template** so a reader can't mistake it for real content.

## Folder template

The starter scaffold. On first run, create `overview/` with these four files.

### `overview/README.md`

```markdown
# <project name>

## Summary
*Placeholder — to be drafted from the repo on first `/mydoc-overview` run, or by hand.*

## What's in this folder
- `how-it-works.md` — current code flow (auto-refreshed by `/mydoc-overview`)
- `codebase-map.md` — spatial map of the repo (auto-refreshed by `/mydoc-overview`)
- `notes.md` — append-only log. `## Observations` is user-directed (issues, ideas, notes, questions). The four checkpoint sections (Ideas, Open threads, Resolved, AGENTS.md candidates) are managed by `/mydoc-checkpoint`.
```

### `overview/how-it-works.md`

```markdown
# How it works

*Last refreshed: YYYY-MM-DD*

*Placeholder — re-run `/mydoc-overview` once the codebase is established to populate this from real code.*
```

### `overview/codebase-map.md`

```markdown
# Codebase Map

*Last refreshed: YYYY-MM-DD*

*Placeholder — re-run `/mydoc-overview` once the codebase is established to populate this from real code.*
```

### `overview/notes.md`

```markdown
# Notes

## Observations
(user observations / notes go here)

## Ideas

## Open threads

## Resolved

## AGENTS.md candidates
```
