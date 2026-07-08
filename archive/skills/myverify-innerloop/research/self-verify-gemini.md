# Architecture Decision Record: Agentic UI Verification Pipeline

## Executive Summary

This document outlines the architectural patterns, decisions, and alternatives explored for building a robust "Outer-Loop Verification" system for AI coding agents. The primary objective is to solve the chronic "false positive done" failure mode—where an agent successfully writes code that passes static type-checks but fails to achieve the desired functional or visual state in the running application.

The finalized architecture shifts away from slow, agent-driven exploratory testing (which suffered from 25-minute execution times and context contamination) toward a **Deterministic Escalation Pipeline**. This pipeline enforces code quality and runtime verification through a strict hierarchy of hooks, standard POSIX interfaces, and ephemeral validation scripts.

---

## 1. The Core Architecture: Deterministic Escalation Pipeline

To balance execution speed with high-fidelity verification, the system abandons LLM-based "smart routing" in favor of a tiered escalation model. Verification is triggered mechanically at specific lifecycle events of the agent's execution loop.

### Tier 1: The `edit` Hook (Sub-Second Static Quality)

* **Trigger:** Intercepts the agent's file save (`edit`) command.
* **Mechanism:** Runs auto-formatters and static analyzers (e.g., Biome, Ruff, TypeScript compiler) immediately before the file is committed to the agent's working state.
* **Auto-Fix Protocol:** If the linter can auto-fix the issue (e.g., formatting, missing imports), the edit is accepted silently, and the agent's context is updated.
* **The "3-Strike" Circuit Breaker:** To prevent infinite linter-chasing loops, the hook tracks consecutive rejections for a file. Upon the 3rd failure, the hook issues a hard override prompt, forcing the agent to stop executing `edit`, use `read_file` to review interfaces, and write a step-by-step resolution plan.

### Tier 2: The `ui-verify` CLI (The Scoped Ephemeral Verifier)

* **Trigger:** Invoked manually by the Builder agent when a UI feature is complete.
* **Mechanism:** A CLI tool (`ui-verify <url> "<brief>" "<spatial_hints>"`) spawns an isolated subprocess.
* **Execution Flow:**
    1. The subprocess acts as a **Compiler**, not an explorer. It takes the brief and a single DOM snapshot.
    2. It generates an *ephemeral* Playwright/Cypress test script.
    3. A dumb runner executes the script at machine speed.
    4. The script is immediately deleted to prevent the codebase from filling with brittle, LLM-generated test artifacts.
    5. The subprocess returns a markdown pass/fail report and an exit code (0 or 1) to the Builder agent.

### Tier 3: The `stop` Hook (Data & API Layer Validation)

* **Trigger:** Intercepts the agent's attempt to exit the task (`stop` or `finish_task`).
* **Mechanism:** Runs domain-specific integration suites to verify "invisible" side effects (e.g., database persistence, correct API payload structures) that UI verification cannot catch. If this fails, the exit is blocked, and the agent must resolve the backend regression.

### Tier 4: Asynchronous Pre-Commit (The Heavy Lift)

* **Trigger:** standard Git commit/push operations after the agent has successfully exited the inner loop.
* **Mechanism:** Heavyweight verification—such as comprehensive multi-page visual regression crawls (which take 20+ minutes) or full E2E suites—runs asynchronously in a CI pipeline. If regressions are found, a *new* agentic session is spawned to address them, preventing the current interactive session from hanging.

---

## 2. Key Architectural Decisions & Rationale

### ADR 1: Subprocess Isolation over Multi-Agent Chat

* **Context:** Allowing a builder agent and a verifier agent to communicate directly often results in "agentic arguing" and context bloat (e.g., flooding the builder's window with DOM trees).
* **Decision:** The verifier must operate as an isolated subprocess wrapped in a standard CLI interface.
* **Rationale:** Forces an asymmetric, deterministic boundary. The builder only sees stdout (markdown verdict) and an exit code. This maintains a pristine context window for the builder and forces it into a standard developer feedback loop (build failed -> read logs -> write fix).

### ADR 2: Ephemeral Assertion Scripts over Agentic Exploration

* **Context:** The initial Playwright MCP verifier took 25 minutes per run because it operated in a "Look -> Think -> Click -> Think" exploratory loop.
* **Decision:** Shift from runtime agentic crawling to compiling single-use assertion scripts.
* **Rationale:** Writing a script and running it via Playwright reduces execution time from 25 minutes to roughly 30 seconds. Deleting the script immediately after prevents the "Goodhart's Law" anti-pattern where the builder agent alters the application code simply to satisfy a poorly written, immutable test script.

### ADR 3: "Scoped Interaction" over "Blind Verification"

* **Context:** Completely blind verifiers struggle to find specific components, leading to test failures caused by poor test generation rather than bad application code.
* **Decision:** The Builder agent is required to provide "Spatial Hints" (e.g., test-ids, specific DOM selectors touched) in the `ui-verify` brief.
* **Rationale:** The Verifier remains blind to the *source code logic* (preserving its adversarial objectivity) but is given a map to the UI component, turning a slow "search and rescue" operation into a fast "targeted strike."

### ADR 4: Rejection of LLM-Based Verification Routing

* **Context:** Proposed using an LLM to evaluate the size/scope of a task to route it to either a "fast" or "slow" verifier.
* **Decision:** Explicitly rejected.
* **Rationale:** LLMs cannot accurately estimate the blast radius of their own code changes (e.g., a "small" CSS tweak breaking a global layout). Verification routing must be deterministic (tied to lifecycle hooks), not heuristic.

---

## 3. Alternative Options Explored (The Design Space)

Before arriving at the pipeline above, several alternative patterns were evaluated:

1. **Contextual Mandates (`CLAUDE.md` / System Prompts):** Injecting strict rules requiring the agent to run `curl` or manual test commands. *Tradeoff:* Prone to instruction decay; agents forget the rules in long contexts.
2. **Dynamic E2E Test Synthesis ("Write-to-Verify"):** The builder agent writes its own test scripts. *Tradeoff:* Suffers from "Self-Correction Bias." The agent will often modify the test to pass the broken code rather than fixing the code to match the requirements.
3. **The Critic / Verifier Sidecar (Multi-Agent Chat):** Two agents debating the UI state. *Tradeoff:* Token-heavy, slow, and prone to conversational loops.
4. **File-Watcher Daemons (TDD Watch Mode):** Piping `vitest --watch` or `nodemon` directly to the agent's terminal. *Tradeoff:* Excellent for backend logic, but useless for visual state. Prone to flooding the context window with stack traces.
5. **Ephemeral Preview Environments (PR Bot Model):** Pushing code to a CI pipeline that spins up Vercel/Docker previews for testing. *Tradeoff:* The highest fidelity verification, but far too slow (minutes per iteration) for inner-loop micro-iterations. Poor debuggability for the agent.
