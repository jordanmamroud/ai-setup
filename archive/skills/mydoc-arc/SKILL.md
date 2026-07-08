---
name: mydoc-arc
description: Explicit-only skill for creating or refreshing a project root ARCHITECTURE.md from verified repo evidence. Use only when the user invokes $mydoc-arc or explicitly asks to create, refresh, migrate, or update architecture documentation.
---

# mydoc-arc

Maintains root `ARCHITECTURE.md`: the current, code-derived explanation of how the project works and where the important pieces live.

This replaces the old `mydoc-overview` pattern of separate `overview/how-it-works.md` and `overview/codebase-map.md` files. Do not create or update `overview/` files.

## What it does

**Triggers:** the user runs `/mydoc-arc` or explicitly invokes `$mydoc-arc`.

1. Identify the project root from the current working directory.
2. Read before writing:
   - Existing `ARCHITECTURE.md`, if present.
   - Legacy `overview/how-it-works.md` and `overview/codebase-map.md`, if present.
   - Root `README.md`, specs such as `SPEC.md` or `spec-v*.md`, and `AGENTS.md` when present.
   - Project metadata such as `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or similar.
   - Top-level source, scripts, deploy files, prompts, configs, and tests enough to verify architecture claims.
3. Apply the state rule:
   - If `ARCHITECTURE.md` is missing, create it from the format below.
   - If `ARCHITECTURE.md` exists, refresh it in place from current repo evidence.
   - If legacy `overview/` architecture docs exist, use them as source context only after verifying claims against the repo.
   - Do not delete legacy `overview/` docs unless the user explicitly asks for cleanup.
4. Report exactly what changed and mention any legacy docs that now look superseded.

Scope is strictly root `ARCHITECTURE.md`. Do not edit `README.md`, `MEMORY.md`, `SPEC.md`, `AGENTS.md`, or files under `overview/`.

## Ownership

`ARCHITECTURE.md` is code-derived and agent-owned. It may be rewritten on every run.

If the existing file contains durable decisions, unresolved threads, or user notes, do not silently preserve them inside `ARCHITECTURE.md`. Report that they belong in `MEMORY.md` or the relevant spec before rewriting.

## Safety rules

- Prefer verified facts over helpful-looking guesses.
- Do not document intended, planned, or aspirational behavior unless it is clearly marked in a spec section being summarized as intent.
- Do not invent commands, deploy targets, schedules, service names, credentials, data stores, or architecture.
- If a section cannot be supported from the repo, omit it or use a visible placeholder.
- Skip noise: `.git/`, `node_modules/`, lockfiles, build output, caches, run artifacts, ignored temp files, and generated dependency docs.
- If a legacy overview doc names a file or flow that no longer exists, fix the claim instead of copying it.

## ARCHITECTURE.md format

Use this order. Omit optional sections that are not supported by repo evidence.

```markdown
# Architecture

*Last refreshed: YYYY-MM-DD*

## System Summary

<One short paragraph explaining what the project is at runtime, what boundary it owns, and the main external systems it touches.>

## Runtime Flow

**Triggers:** <one trigger inline, or a bulleted list for multiple triggers>

1. <Chronological step with concrete component, action, artifact, safety gate, or result.>
2. <Next step.>

## Key Components

- `<path>` - <short purpose>
- `<path>` - <short purpose>

## Data And State

- <Where important input, output, persisted state, artifacts, config, or secrets live.>

## External Systems

- <External API, service, database, queue, scheduler, model, or platform integration.>

## Codebase Map

Grouped by top-level location, in filesystem order.

### Root files

- `<file>` - <short purpose>

### `<dir>/` - <one-line purpose>

- `<child>` - <short purpose>
```

## Section rules

### System Summary

- Keep it to one paragraph.
- Describe implemented runtime behavior, not goals.
- Include the main boundary: CLI, service, job, library, app, script, skill, or workflow.

### Runtime Flow

- Use a numbered, chronological flow.
- Reference files inline with backticks where they appear.
- Each step should be one line when possible.
- Use multiple flow subsections only when the project has genuinely different flows.
- For important non-happy paths, add a sub-bullet prefixed with `Branch:`.

### Key Components

- List the small set of files or folders a maintainer needs to understand first.
- Prefer operational components over generic folder listings.
- Do not duplicate the full codebase map.

### Data And State

- Include only if the repo shows meaningful inputs, outputs, persisted state, artifacts, config, secrets, caches, or schemas.
- Mention secret names or env var names only when already documented or present in committed examples.
- Never include secret values.

### External Systems

- Include only verified external systems.
- Name auth boundaries and failure behavior when the repo documents them.

### Codebase Map

- Group by top-level location in filesystem order.
- Use `### Root files` first, then one `### <dir>/ - <purpose>` section per important top-level directory.
- List immediate children only.
- Keep entries one line and terse.
- Collapse related siblings onto one line when that scans better.
- Skip vendored, generated, ignored, or build output directories.

## Placeholder rule

If the repo is too sparse to derive real content, create `ARCHITECTURE.md` with this visible placeholder after the timestamp:

```markdown
*Placeholder - re-run `/mydoc-arc` once the codebase is established to populate this from real code.*
```
