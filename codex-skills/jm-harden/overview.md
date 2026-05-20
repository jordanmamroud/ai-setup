# JM Harden Overview

JM Harden is an explicit-invocation Codex skill for project hardening. It guides Codex to inspect a codebase or feature, identify realistic failure modes, rank them by risk, and turn the highest-value findings into concrete fixes and tests when implementation is requested.

## Why We Created It

We created this skill because Codex-generated projects can be functionally correct on the happy path while still missing the edge cases that matter in real use. The goal is to give Codex a reusable hardening routine that asks, "What would break this?" before changing code.

This skill is intentionally not tied to one project. It should work across JavaScript, TypeScript, Python, frontend, backend, CLI, API, and full-stack projects by focusing on universal reliability concerns: invalid input, missing state, async failures, network and filesystem errors, authorization gaps, environment drift, data consistency, observability, and test coverage.

It is also installed globally as an explicit-only skill so it does not get invoked accidentally. Use `$jm-harden` when a project needs a deliberate robustness pass.

## Future Iteration Note

For the next iteration, add the ability to harden projects for specific tech stacks. Keep the general workflow, but add stack-specific guidance for common ecosystems such as React, Next.js, Node/Express, Python/FastAPI, Python/Django, browser extensions, CLIs, and mobile apps.

Do not implement stack-specific hardening now; preserve this as the next improvement.
