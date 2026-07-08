# mydoc-readme

Maintains a concise root `README.md` for a project. The README is the first human entry point: what this project is, why it exists, how to use or run it if that is clear from the repo, and where the important docs live.

## What it does

**Triggers:** the user runs `/mydoc-readme` or explicitly invokes `$mydoc-readme`.

1. Identify the project root from the current working directory.
2. Read the repo before writing:
   - Existing `README.md`, if present.
   - Project metadata: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `composer.json`, or similar.
   - Top-level docs such as `SPEC.md`, `Handoff.md`, `AGENTS.md`, and `overview/*.md` when present.
   - Top-level source, scripts, deploy docs, and tests enough to verify claims.
3. Apply the state rule:
   - If root `README.md` is missing and `overview/README.md` exists, migrate it to root `README.md`, adjust any index paths to point into `overview/`, then remove `overview/README.md`.
   - If root `README.md` is missing, create one from the format below.
   - If root `README.md` exists and the user did not explicitly ask to refresh, report that it exists and stop.
   - If root `README.md` exists and the user explicitly asked to refresh, update it in place while preserving useful human-authored sections. Do not delete custom content unless it is clearly stale and replaced by a better current version.
4. Report exactly what changed.

Scope is strictly root `README.md`, except for deleting legacy `overview/README.md` after a migration when root `README.md` was missing. Do not create or edit `overview/how-it-works.md`, `overview/codebase-map.md`, `overview/notes.md`, `SPEC.md`, or `AGENTS.md`.

## Safety rules

- Prefer verified facts over helpful-looking guesses.
- Do not invent install commands, deploy commands, URLs, schedules, credentials, service names, or architecture.
- If a section cannot be supported from the repo, omit it or use a visible placeholder.
- Existing root `README.md` is human-owned. Invocation alone is not permission to rewrite it; the user must ask to refresh, rewrite, update, or replace it.
- Keep it concise. A README that tries to duplicate every overview doc is doing the wrong job.

## README format

Use this order. Omit optional sections that are not supported by repo evidence.

```markdown
# <project name>

## Summary

<One paragraph, 3-5 sentences. Say what this is, why it exists, who it is for, and the current operating posture if relevant.>

## Quick Start

<Only include commands that are directly supported by project metadata or docs. Use fenced shell blocks.>

## Common Tasks

- `<command or file>` - <short purpose>

## What's Here

- `<path>` - <short purpose>
- `<path>` - <short purpose>

## Related Docs

- `overview/how-it-works.md` - current code flow
- `overview/codebase-map.md` - repo map
- `overview/notes.md` - open notes and checkpoint log
```

## Section rules

### Summary

- One paragraph only.
- Present tense.
- No boilerplate like "This project aims to..."
- Mention production status only if the repo has evidence for it.

### Quick Start

- Include only commands found in metadata or docs, such as `npm test`, `npm start`, `make test`, or a documented deploy command.
- If setup requires secrets or external auth, say so briefly and point to the relevant file; do not paste secret names unless already documented.
- If no safe command is clear, omit this section.

### Common Tasks

- Include when the repo has obvious scripts, test commands, deployment commands, or operator workflows.
- Keep each bullet one line.
- Do not turn this into a full runbook.

### What's Here

- List the files and folders a new reader needs first.
- Prefer top-level entries.
- If `overview/` exists, include it, but do not duplicate the whole `overview/codebase-map.md`.

### Related Docs

- Include only docs that exist.
- If `overview/` exists, link to its files from root-relative paths.
- If no related docs exist, omit this section.

## Migration cleanup

When migrating `overview/README.md` to root `README.md`:

- Preserve the Summary.
- Change a heading like `## What's in this folder` to `## What's in overview/`.
- Prefix overview file links with `overview/`.
- Delete `overview/README.md` after root `README.md` is written successfully.
- If root `README.md` already exists, do not migrate. Report the conflict and stop.
