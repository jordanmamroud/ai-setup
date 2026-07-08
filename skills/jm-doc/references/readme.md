# jm-doc readme

Maintain a concise root `README.md` for a project. The README is the first human entry point: what this project is, why it exists, how to use or run it if that is clear from the repo, what a successful outcome looks like, and where the important docs live.

For README pattern research only, use the archived research corpus at `~/mylab/ai-setup/archive/skills/mydoc-readme/references/` (`readme-patterns.md` and `repo-readmes-index.md`). Do not load those example READMEs during normal runs unless the user asks to study README examples or update the default README guidance.

## What it does

1. Identify the project root from the current working directory.
2. Read the repo before writing:
   - Existing `README.md`, if present.
   - Project metadata: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `composer.json`, or similar.
   - Licensing and contribution files such as `LICENSE`, `CONTRIBUTING*`, `.github/ISSUE_TEMPLATE*`, or similar.
   - Top-level docs such as `SPEC.md`, `Handoff.md`, `AGENTS.md`, `ARCHITECTURE.md`, and `overview/*.md` when present.
   - Config examples such as `.env.example`, config templates, deployment docs, or client setup docs when present.
   - Top-level source, scripts, deploy docs, and tests enough to verify claims.
3. Apply the state rule:
   - If root `README.md` is missing and `overview/README.md` exists, migrate it to root `README.md`, adjust any index paths to point into `overview/`, then remove `overview/README.md`.
   - If root `README.md` is missing, create one from the format below.
   - If root `README.md` exists and the user did not explicitly ask to refresh, report that it exists and stop.
   - If root `README.md` exists and the user explicitly asked to refresh, update it in place while preserving useful human-authored content, the successful outcome, and operational safety or verification details. Do not delete custom content unless it is clearly stale and replaced by a better current version.
4. Report exactly what changed.

Scope is strictly root `README.md`, except for deleting legacy `overview/README.md` after a migration when root `README.md` was missing. Do not create or edit `ARCHITECTURE.md`, `overview/notes.md`, `SPEC.md`, or `AGENTS.md` — architecture belongs to `/jm-doc arc`, session notes to `/jm-doc checkpoint`.

## Safety rules

- Prefer verified facts over helpful-looking guesses.
- Do not invent install commands, deploy commands, URLs, schedules, credentials, service names, or architecture.
- Always include `Successful Outcome`. If no successful outcome can be verified from the repo, include a clearly marked placeholder instead of guessing.
- Existing root `README.md` is human-owned. Invocation alone is not permission to rewrite it; the user must ask to refresh, rewrite, update, or replace it.
- Keep it concise. A README that tries to duplicate every overview doc or runbook is doing the wrong job.
- Do not add badges, star charts, sponsorship sections, language switchers, or community links unless they already exist or are explicitly documented as important for this repo.

## Operational content

For jobs, automations, deployable services, production tools, and pipelines, preserve or include concise operational truth:

- Safe-operation defaults, write/apply warnings, dry-run behavior, and release gates.
- Manual execution, deploy, scheduler, recent-execution, health, or verification commands when documented.
- Runtime configuration, secret sources, state backends, notification behavior, and required external services when documented.
- Failure, fail-closed, quarantine, artifact, logging, or alert behavior when it is central to operating the project.
- Links to deeper deployment or production checklist docs instead of copying a full runbook.

Do not strip operational warnings or verification commands just to make the README cleaner. Structure and wording can improve; safety and success semantics must survive the refresh.

## README format

Use this order. Always include `Successful Outcome`; omit other optional sections that are not supported by repo evidence.

```markdown
# <project name>

## Status

<Current state in 1-3 bullets or one short paragraph. Use only repo-supported facts: production readiness, active/inactive state, deployment posture, major blockers, or maintenance state.>

## Summary

<One paragraph, 3-5 sentences. Say what this is, why it exists, and who it is for.>

## Capabilities

- <Concrete tool, service, command, API, skill, or workflow this project provides>
- <Another user-facing capability>

## How It Works

<For jobs, automations, CLIs, services, and pipelines, use numbered steps with bold step titles: `1. **Trigger starts the run.** Explain the concrete action, component, artifact, or safety gate.` For simpler projects, use a short explanation only when a step-by-step flow would add noise.>

## Successful Outcome

- <Observable result that means the project worked>
- <Important artifact, state change, report, user-visible behavior, or safety outcome>

## Requirements

- <Runtime, CLI, external account, credential, platform, or service requirement>

## Quick Start

<Only include commands that are directly supported by project metadata or docs. Use fenced shell blocks.>

## Configuration

<Only include documented environment variables, config files, auth setup, credential setup, or client setup. Link to deeper docs when setup is long.>

## Common Tasks

- `<command or file>` - <short purpose>

## What's Here

- `<path>` - <short purpose>
- `<path>` - <short purpose>

## Related Docs

- `ARCHITECTURE.md` - code-derived architecture and repo map
- `overview/notes.md` - open notes and checkpoint log
- `spec-v0.md` / `spec-v1.md` - versioned specs

## Support

- `<issue tracker, troubleshooting doc, or support channel>` - <short purpose>

## Contributing

See `CONTRIBUTING.md` or the documented contribution workflow.

## License

<License name, if verified from `LICENSE` or project metadata.>
```

## Section rules

### Status

- First section after the title.
- Use bullets when there are multiple concrete status facts; otherwise use one short paragraph.
- Include production readiness, active/inactive state, deployment posture, major blockers, or maintenance state only when supported by repo evidence.
- If no status can be verified, omit this section.

### Summary

- One paragraph only.
- Present tense.
- No boilerplate like "This project aims to..."
- Do not duplicate details already covered in Status.

### Capabilities

- Include when the repo exposes obvious tools, skills, services, commands, APIs, integrations, or user workflows.
- Keep bullets user-facing; do not list implementation internals.
- Use a more specific existing heading only if the repo already clearly uses one, such as `Tools`, `Skills`, or `Services`.

### How It Works

- Include when the repo has a workflow, lifecycle, architecture, or mental model that helps a new reader use it correctly.
- For jobs, automations, CLIs, services, and pipelines, prefer numbered steps that follow the real execution path from trigger to outcome.
- Match this style for each step: `1. **Short step title.** One concrete sentence with the component, action, artifact, external service, safety gate, or result.`
- Write step titles as user-readable actions, not implementation labels: `Runtime config is loaded`, `Search terms are cleaned`, `Safe exact negatives are written`.
- Name the important components, external services, artifacts, safety gates, and notification/reporting steps when repo evidence supports them.
- Keep each step one sentence. A concrete 8-12 step flow is better than a vague 3-5 bullet summary for operational systems.
- Link to deeper architecture or explanation docs when they exist.
- Omit if it would repeat the Summary or guess at internals.

### Successful Outcome

- Always include this section.
- State what observable result means the project worked, not another process summary.
- For jobs, automations, services, and pipelines, include final state changes, preserved review artifacts, skipped unsafe work, persisted state, notifications, logs, or other audit outputs when supported.
- For apps, libraries, CLIs, skills, and docs projects, define the user-visible result, generated artifact, command behavior, or validation outcome that means the work succeeded.
- Use bullets when there are multiple outcomes; use one short paragraph only for simple projects.
- If no reliable outcome can be verified, write a visible placeholder such as `TODO: Define the successful outcome for this project.` Do not invent it.

### Requirements

- Include when setup or usage depends on runtimes, CLIs, external accounts, credentials, auth scopes, services, platforms, or non-obvious tools.
- Include versions only when documented.
- Put prerequisites here instead of burying them inside Quick Start.

### Quick Start

- Include only commands found in metadata or docs, such as `npm test`, `npm start`, `make test`, or a documented deploy command.
- If setup requires secrets or external auth, say so briefly and point to the relevant file; do not paste secret names unless already documented.
- If no safe command is clear, omit this section.

### Configuration

- Include when documented environment variables, config files, credentials, OAuth setup, client setup, or platform settings are required.
- Keep examples short and safe; do not paste credentials or invent placeholder values beyond documented examples.
- Link to deeper setup docs instead of copying long auth or deployment walkthroughs.

### Common Tasks

- Include when the repo has obvious scripts, test commands, deployment commands, or operator workflows.
- Include operational check commands when documented, such as manual dry-runs, scheduler status checks, recent execution checks, or health checks.
- Keep each bullet one line unless the documented command needs a fenced block.
- Do not turn this into a full runbook.

### What's Here

- List the files and folders a new reader needs first.
- Prefer top-level entries.
- If `overview/` exists, include it, but do not duplicate its contents.

### Related Docs

- Include only docs that exist.
- Prefer `ARCHITECTURE.md`, `overview/notes.md`, and spec files when present; link legacy `overview/how-it-works.md` / `overview/codebase-map.md` only if they still exist and no `ARCHITECTURE.md` has replaced them.
- If no related docs exist, omit this section.

### Support

- Include only when the repo documents issue trackers, troubleshooting docs, support channels, or known failure-mode docs.
- Prefer links to troubleshooting docs over writing a new troubleshooting guide.

### Contributing

- Include only when `CONTRIBUTING*`, contribution docs, PR templates, or existing README content support it.
- Keep it to one or two sentences or a link.

### License

- Include only when `LICENSE`, package metadata, or existing docs identify the license.
- Do not infer licensing from repository visibility.

## Migration cleanup

When migrating `overview/README.md` to root `README.md`:

- Preserve the Summary.
- Change a heading like `## What's in this folder` to `## What's in overview/`.
- Prefix overview file links with `overview/`.
- Delete `overview/README.md` after root `README.md` is written successfully.
- If root `README.md` already exists, do not migrate. Report the conflict and stop.
