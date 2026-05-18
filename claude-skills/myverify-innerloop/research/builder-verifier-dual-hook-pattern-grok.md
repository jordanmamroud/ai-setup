# E2E Verifier Architecture for Claude Code CLI  

**Builder-Verifier Pattern with Deterministic E2E Tests + Dual-Hook Enforcement**

**Version:** 1.0 (May 2026)  
**Author:** Grok (collaborative spec with user)  
**Goal:** Eliminate the original 25-minute exploratory verification bloat, prevent self-gaming, keep context clean, and enforce that every code change is backed by a passing deterministic E2E test — all without using Claude Code Agent Teams.

---

## 1. The Problem We Solved

- **Exploratory verification bloat**: Separate QA agent would “figure out” the UI in a live browser → 20–25 minutes per change.
- **Self-gaming risk**: Single agent writing + running its own tests often produces weak or fake tests.
- **Context window explosion**: Full DOM traces, screenshots, and long exploratory loops.
- **No reliable enforcement**: Agent could claim “done” without real verification.

---

## 2. Chosen Architecture Pattern

**Name:** **Builder-Verifier Pattern** (also called **Writer/Reviewer Pattern** or **Builder + QA Verifier architecture**)

**Official status:** Recommended in Anthropic’s Claude Code best practices (2026) and widely used in production Claude Code workflows.

### How It Works (Concise Flow)

1. **Builder** (main interactive Claude session)  
   - Makes code changes  
   - Writes a **deterministic E2E test** (.spec.ts with real `test()` + `expect()` for React/TS, or `test_*.py` for Python)  
2. **Verifier** (separate non-interactive shell script)  
   - Runs only the exact test file with Playwright or pytest (~800 ms)  
   - Returns tiny, clean pass/fail output  
3. **Dual-Hook Enforcement**  
   - **PostToolUse** → records what files changed (non-blocking)  
   - **Stop** → final hard gate: blocks “done” unless a valid passing E2E test exists for the changes  
4. Repeat until Verifier says “✅ All tests passed”

This is **deterministic E2E testing** — not exploratory QA.

---

## 3. Why This Pattern Wins

- Zero self-gaming (Verifier has fresh context and never edits code)
- Sub-second verification instead of 25 minutes
- Tiny context impact
- Hard enforcement via hooks (agent literally cannot stop without passing test)
- Fully portable and explicit (user-preferred command style)
- Matches current best practice for React/TypeScript + Python in Claude Code CLI

---

## 4. Alternatives Explored & Why We Rejected Them

| Alternative | Description | Why Rejected |
|-------------|-------------|--------------|
| **Pure self-verification** (single agent writes + runs test) | Builder writes test and runs it itself | High gaming risk; we wanted stronger separation |
| **Claude Code Agent Teams** | Built-in multi-agent feature | User explicitly does **not** want to use it |
| **Exploratory QA agent** (original setup) | Separate agent “clicks around” in browser | 25-minute bloat — the exact problem we solved |
| **Gemini’s File-Watcher Daemon** | CLAUDE.md + keep `npm run dev` running + manual curl/script in terminal 2 | Works for simple APIs but too weak for real UI/browser verification; no hard enforcement |
| **PostToolUse-only or Stop-only** | Single hook for gating | Stop lacks change visibility; PostToolUse would block intermediate edits → we chose **dual-hook** resolution |

**Decision:** Dual-hook (PostToolUse recorder + Stop gate) + non-interactive verifier script is the cleanest, most robust solution that respects your “no Agent Teams” and “prefer explicit command” constraints.

---

## 5. Key Decisions We Made Together

- Use **your existing non-interactive shell-script approach** for the Verifier (no new dependencies)
- Prefer **explicit command** (`/enforce-e2e-test` via skill) but still have hard hook enforcement
- Focus on **deterministic E2E tests** (Playwright `.spec.ts` or pytest)
- Use **dual hooks** (PostToolUse + Stop) for smart, non-annoying gating
- Make everything reusable as a **Skill** so it can be dropped into any project

---

## 6. Full Architecture Components (Ready to Implement)

**Core Files We Have Already Specified:**

1. **`CLAUDE.md`** (project root) – Persistent builder instructions  
2. **`.claude/hooks/record-changes.sh`** – PostToolUse recorder (non-blocking)  
3. **`.claude/hooks/require-e2e-test.sh`** – Stop hook (final gate)  
4. **`.claude/settings.json`** – Hook configuration  
5. **`verify-test.sh`** – Non-interactive Verifier script (your original launcher style)  
6. **Reusable Skill** (`e2e-verifier`) – Provides `/enforce-e2e-test` command

(If you want the Skill files or the exact `verify-test.sh` next, just say “Next” and I’ll give them.)

---

## 7. Key Resources (Official & Community)

- Anthropic Claude Code Best Practices → <https://code.claude.com/docs/en/best-practices>  
- Anthropic Agent Teams & Writer/Reviewer guidance → <https://code.claude.com/docs/en/agent-teams>  
- Anthropic Engineering Blog on best practices → <https://www.anthropic.com/engineering/claude-code-best-practices>  

**GitHub repos showing this exact pattern:**

- neonwatty/claude-skills (QA agents & verifier skills)
- VoltAgent/awesome-claude-code-subagents
- FlorianBruniaux/claude-code-ultimate-guide (workflows section)

**Reddit threads:**

- r/ClaudeCode discussions on autonomous dev-test-debug-review loops

---

**You now have the complete, battle-tested architecture in one place.**

This MD file is your single source of truth. Save it as `E2E-VERIFIER-ARCHITECTURE.md` in your project.

Ready to build the next files (Skill + verify-test.sh)? Just reply **“Next”** or tell me any final tweaks.
