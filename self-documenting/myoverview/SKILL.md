---
name: myoverview
description: Create or sync overview.md — the project's high-level orientation doc. Scaffolds it from template if missing; updates code-derived sections in place while preserving the human-owned Summary and the append-only Notes zone.
---

# myoverview

Maintains a standardized `overview.md` in any project: high-level orientation for a reader trying to understand what the project is and how the pieces fit together.

## What it does

**Triggers:** the user runs `/myoverview`.

1. Check for `overview.md` at the project root.
   - If missing → write a fresh `overview.md` using the **File template** at the bottom of this document, fill in the project name, populate code-derived sections from the repo.
   - If present → re-derive code-derived sections in place. Leave **Summary** untouched. Leave everything below the `<!-- APPEND-ONLY BELOW -->` marker untouched (this includes `## Notes` and `## Checkpoint` — the latter is owned by `/mycheckpoint`).
2. Report what changed.

Scope is strictly `overview.md`. README, CLAUDE.md, spec.md, etc. are out of scope.

## Section ownership

Three tiers. Boundaries are encoded as HTML comments in the file itself — respect them.

| Zone | Sections | Permission |
|---|---|---|
| Human-owned | `## Summary` | Never modify. Read only. |
| Code-derived | Top-of-file `*Last refreshed: YYYY-MM-DD*` line, `## How it works`, `## Codebase Layout` | Rewrite in place on each run. Timestamp gets today's date; sections get re-derived from the codebase. |
| Append-only | Everything below `<!-- APPEND-ONLY BELOW -->` (currently `## Notes` and `## Checkpoint`) | Append only. Never edit or delete existing entries. One exception: marking an Open thread as `— RESOLVED YYYY-MM-DD` in place, then moving it to `### Resolved`. |

## Format: "Summary" section

Hand-written prose. Agent drafts only on first run, then never touches it again.

Rules:
- One paragraph, roughly 3–5 sentences.
- Lead sentence: what this is.
- Then: why it exists, what problem it solves, who it's for.
- Optionally close with one sentence on how to use it or current status.
- Present tense. No boilerplate ("This project aims to...").
- Prose only — no bullets, sub-headings, or links.

### Example

```markdown
## Summary
`myoverview` is a Claude Code skill that maintains a standardized `overview.md` for any project. It scaffolds the file from a template on first run and re-syncs the code-derived sections on subsequent runs, leaving the human-owned Summary and append-only Notes zones alone. Triggered with `/myoverview`.
```

## Format: "How it works" section

Describes the code as it currently exists. Do not document intended, planned, or aspirational behavior — that belongs in `spec.md`. If a feature isn't implemented yet, don't include it.

Never write abstract paragraphs. Write a numbered, chronological flow.

Defaults:
- Open with `**Triggers:**` listing what initiates the flow. One trigger inline (e.g. `**Triggers:** the user runs /refresh.`); multiple triggers as a bulleted list. Same flow with multiple triggers does NOT become multiple flows.
- Then a numbered list of steps. Each step is one line. Reference files inline using backticks where they appear, not in a separate list.
- Close with one optional tail line capturing the *why* or a key consequence.

Add structure only when complexity demands it:
- **Multiple flows:** if the project has genuinely different flows (different *steps*, not just different triggers), give each a `### Flow name` subheading and apply the above to each.
- **Branches:** if a step has meaningful non-happy-path behavior (auth failure, retry, fallback), add it as a sub-bullet prefixed with `↳ Branch:`. Don't fork the main flow.

Bias toward terse. If a step needs more than one line, the flow is wrong scope — split it or push detail elsewhere.

### Example

```markdown
## How it works

**Triggers:** use `/mycheckpoint` command, or `!mycheckpoint` from inside Claude Code.

1. Scans the current conversation for new ideas / open threads / threads now resolved.
2. Reads existing `CHECKPOINT.md` if present so it doesn't duplicate.
3. Updates `CHECKPOINT.md` in place — appends new entries, marks resolved threads `— RESOLVED YYYY-MM-DD` in place under `## Open threads`.
4. Emits a copy-pasteable fresh-session prompt that pulls `CHECKPOINT.md` + `STATUS.md`, ending with a one-line "Next:" action.

The fresh-session prompt is the proximate cause of the 50K cold-start.
```

## Format: "Codebase Layout" section

A spatial map of the repo: folders and files with a one-line description of each.

Rules:
- Do not re-list files that already appear inline in **How it works**. Focus on files and folders the main flow doesn't mention but a reader needs to navigate (configs, fixtures, tests, examples, build artifacts).
- Reflect the actual shape — nested folders get nested bullets so the indentation matches the tree.
- One line per entry. If you can't describe a file's role in one line, the file probably needs splitting or the entry should be at a folder level instead.
- Skip noise: `node_modules/`, `.git/`, lockfiles, build output, anything in `.gitignore`.

### Example

```markdown
## Codebase Layout
- `SKILL.md` — skill instructions and format rules.
- `templates/` — starter skeletons.
  - `overview.md` — overview scaffold.
```

## Format: "Notes" section

Append-only zone. Agent never deletes or rewords existing entries.

Rules:
- One entry per line: `PREFIX: <content>  (YYYY-MM-DD)`.
- Prefixes are uppercase and case-sensitive.
- Legend line is permanent — preserved across runs.
- One allowed in-place edit: appending ` → resolved YYYY-MM-DD` to an existing entry when it's done. Nothing else.

Prefixes:
- `ISSUE:` known issue / heads-up for the next reader
- `IDEA:` future-version thought, not committed
- `NOTE:` random observation
- `Q:` open question

### Example

```markdown
## Notes
Legend: `ISSUE:` known issue · `IDEA:` future thought · `NOTE:` observation · `Q:` open question
Append entries with a `(YYYY-MM-DD)` suffix.

ISSUE: cache invalidates silently on macOS  (2026-04-12)
IDEA: add a --dry-run flag  (2026-04-18) → resolved 2026-05-01
NOTE: tested on macOS only  (2026-05-01)
Q: should overview link to spec or stay independent?  (2026-05-11)
```

## Format: "Checkpoint" section

Append-only zone. Owned by `/mycheckpoint`, not `/myoverview`. `/myoverview` creates the empty scaffold on first run and never touches it again. `/mycheckpoint` is the only thing that writes here.

Rules:
- Four subsections, in this order: `### Ideas`, `### Open threads`, `### Resolved`, `### CLAUDE.md candidates`. Keep all four headings even when empty.
- Each entry is a bulleted line. New entries append to the **bottom** of their subsection (chronological). Don't reorder existing ones.
- **For Ideas:** name what's worth remembering and *why* (the implication, risk, or surprise), not just the observation.
- **For Open threads:** name what closing the thread looks like, so the next reader knows when it's done.
- **For Resolved:** entry format is `<title> — RESOLVED YYYY-MM-DD — <one-line resolution + pointer>`. Items arrive here by being moved out of Open threads, not by being written here directly.
- **For CLAUDE.md candidates:** captured suggestions only. Never auto-promoted to CLAUDE.md — the human decides.
- One allowed in-place edit: moving an Open thread to Resolved when it closes (append RESOLVED marker, move the line). Nothing else.

### Example

```markdown
## Checkpoint

### Ideas
- Caching the parsed AST would cut cold-start by ~30%. Risk: invalidation on file change is non-trivial.

### Open threads
- Should the fresh-session prompt include a "no extended thinking" hint? Closes when we A/B test once.

### Resolved
- Drop STATUS.md from fresh-session prompt — RESOLVED 2026-05-11 — applied in mycheckpoint.md.

### CLAUDE.md candidates
- Add: "when editing the zshrc backup, always test in a new shell before committing."
```

## First-run scaffolding

When creating a new `overview.md` from the template below:
1. Replace `<project name>` placeholder with the actual project name (folder name, then `package.json` / `pyproject.toml` / `Cargo.toml` if available).
2. Set the `*Last refreshed: ...*` line to today's date.
3. Write a draft **Summary** inferred from the repo (README, project metadata, top-level code). One paragraph. The human will revise; subsequent runs must never touch Summary again.
4. Populate code-derived sections from the repo.
5. Leave **Notes** empty except for the legend line.
6. Leave **Checkpoint** as the four empty subsection headings. `/mycheckpoint` fills it; `/myoverview` never writes content here after first-run scaffolding.

On every subsequent run, refresh the timestamp to today's date regardless of whether code-derived sections changed.

## File template

The starter skeleton. Write this verbatim to `overview.md` on first run, then populate as described above. Preserve the HTML comment markers exactly — they define the protection zones.

````markdown
# <project name>

*Last refreshed: YYYY-MM-DD*

<!-- HUMAN-OWNED: agent must not modify the Summary section. -->
## Summary
<Written by hand. Purpose, how to use, anything else worth saying up front.>

## How it works
<Agent rewrites from the codebase. Format: **Triggers:** line(s), then a numbered list of steps (one line each, files in `backticks` inline), optional tail line for the why. Use `### Flow name` subheadings only when the project has genuinely different flows. See SKILL.md for full rules.>

## Codebase Layout
<Agent rewrites from the codebase. Spatial map of the repo. Skip files already referenced inline in **How it works** — focus on files and folders the main flow doesn't mention. Nested folders get nested bullets. See SKILL.md for full rules.>

<!-- APPEND-ONLY BELOW: agent must not edit or delete existing entries, only append new ones. -->

## Notes
Legend: `ISSUE:` known issue · `IDEA:` future thought · `NOTE:` observation · `Q:` open question
Append entries with a `(YYYY-MM-DD)` suffix.

## Checkpoint
<Owned by `/mycheckpoint`. `/myoverview` scaffolds the four empty subsection headings and never writes here again.>

### Ideas

### Open threads

### Resolved

### CLAUDE.md candidates
````
