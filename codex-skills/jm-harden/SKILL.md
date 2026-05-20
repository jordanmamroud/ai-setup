---
name: jm-harden
description: Review and harden software projects by identifying edge cases, failure modes, robustness gaps, missing validation, poor error handling, production-readiness risks, security-sensitive failure paths, and test gaps. Use when the user asks to harden, bulletproof, productionize, review edge cases, find what could break, improve reliability, add defensive handling, or make a JavaScript, TypeScript, Python, frontend, backend, CLI, API, or full-stack project more robust.
---

# JM Harden

## Overview

Use this skill to find realistic ways a project or feature can break, then turn that risk inventory into focused fixes and tests. Prefer concrete, code-grounded findings over generic hardening advice.

## Workflow

1. Clarify the requested mode:
   - If the user asks to list risks, review edge cases, or asks ambiguously to "harden" something, inspect first and return a prioritized hardening list before editing files.
   - If the user explicitly asks to implement fixes, still identify the highest-risk items first, then make focused changes for those items.
2. Inspect the project shape before judging it:
   - Read package/config files, entry points, routing or command surfaces, data models, error boundaries, tests, and documented environment variables.
   - Use existing scripts to understand validation commands, such as `npm test`, `npm run lint`, `npm run typecheck`, `pytest`, or project-specific equivalents.
   - Prefer `rg` and targeted file reads. Avoid broad rewrites or unrelated refactors.
3. Build a failure model for the feature or project.
4. Rank risks by likelihood, impact, and proximity to user-facing or data-corrupting behavior.
5. Report findings with enough detail that each item can be reproduced, fixed, and tested.
6. Implement only the agreed or explicitly requested fixes, then run relevant validation.

## Failure Model

Consider these categories, keeping only those relevant to the code under review:

- Invalid, missing, empty, huge, duplicated, stale, or malformed input
- Null, undefined, optional, partial, or unexpected data shapes
- Async ordering, race conditions, cancellation, retries, timeouts, and double-submit behavior
- Network, filesystem, database, cache, browser API, and third-party service failures
- Authentication, authorization, session expiry, CSRF/CORS, injection, secret leakage, and unsafe deserialization
- Environment/configuration drift, missing env vars, dev/prod differences, and version mismatches
- State persistence, migrations, schema changes, idempotency, rollback, and data corruption paths
- Resource limits, memory pressure, large payloads, slow queries, rate limits, and backpressure
- Error boundaries, user-facing error states, logging, observability, and supportability
- Test gaps around the highest-risk behavior, not just happy paths

## Output Format

When reporting a hardening review, lead with findings ordered by severity:

- `P0` data loss, security break, crash loop, or unusable core path
- `P1` likely production failure, incorrect behavior, or serious recovery gap
- `P2` edge case with moderate impact or plausible support burden
- `P3` polish, observability, or defensive improvement

For each finding, include:

- What breaks
- Where it likely happens, with file and line references when available
- Trigger or reproduction path
- Impact
- Recommended fix
- Test or validation to add

End with a short implementation order. If the user did not explicitly ask for code changes, ask before editing.

## Implementation Guidance

When implementing hardening changes:

- Fix the highest-risk concrete failure paths first.
- Add validation at trust boundaries rather than scattering broad exception handling everywhere.
- Preserve existing APIs and behavior unless the current behavior is unsafe or clearly wrong.
- Prefer typed schemas, existing validators, framework error boundaries, and local helper patterns already in the repo.
- Add targeted tests for each fixed failure mode, including negative cases and regression cases.
- Run the narrowest meaningful validation first, then broader project validation when the change touches shared code.

## Language Notes

- For JavaScript and TypeScript, inspect `package.json`, framework config, client/server boundaries, async flows, form handling, API routes, build scripts, type coverage, and browser/runtime assumptions.
- For Python, inspect packaging files, dependency pins, CLI or web entry points, exception boundaries, serialization, concurrency model, environment loading, and test configuration.
- For frontend work, check loading, empty, error, offline, slow network, mobile, accessibility, and repeated-action states.
- For backend work, check authz, input validation, idempotency, persistence consistency, timeout/retry behavior, rate limits, and logging.
