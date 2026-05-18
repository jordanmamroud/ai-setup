---
description: Promote a polished global Claude Code behavior rule into global/CLAUDE.md, refresh the symlink, then commit and push.
disable-model-invocation: true
---

# myclaude

Promote a polished global Claude Code behavior rule into `/Users/jordanmamroud/mylab/ai-setup/global/CLAUDE.md`, then commit and push it.

Use only when the user explicitly invokes `/myclaude` or asks to add/update global Claude rules.

## Source of truth

- Canonical file: `/Users/jordanmamroud/mylab/ai-setup/global/CLAUDE.md`
- Live global file: `~/.claude/CLAUDE.md`
- The live file should be a symlink to the canonical file. Run `/Users/jordanmamroud/mylab/ai-setup/claude-link-commands.sh` after edits to refresh it.
- Do not edit `~/.claude/CLAUDE.md` directly.
- Do not use repo-root `/Users/jordanmamroud/mylab/ai-setup/CLAUDE.md` for global rules; that file is project-level context for this repo.

## Workflow

1. Read the canonical `global/CLAUDE.md`.
2. Take the user's proposed rule, complaint, or rough snippet from the invocation. If it is missing, ask for the rule and stop.
3. Rewrite it in the existing global Claude voice:
   - direct, brief, concrete
   - no corporate policy phrasing
   - no vague virtue words unless they create a testable behavior
   - one rule should change one agent behavior
4. Brainstorm 2-4 candidate phrasings internally. Choose the strongest one; mention alternatives only if the tradeoff matters.
5. Insert the rule into the best existing section. Create a new section only when no existing heading fits.
6. Run:
   - `./claude-link-commands.sh`
   - `test "$(readlink "$HOME/.claude/CLAUDE.md")" = "/Users/jordanmamroud/mylab/ai-setup/global/CLAUDE.md"`
7. Review `git diff -- global/CLAUDE.md`.
8. Commit and push the change:
   - stage only files intentionally changed for this request
   - commit message format: `Update global Claude agent rules`
   - if the change is clearly narrower, use `Add <specific behavior> to global CLAUDE`
   - push the current branch

## Guardrails

- Do not add scratchpad notes, one-off preferences, or project-specific rules.
- If the proposed rule conflicts with an existing rule, stop and explain the conflict instead of papering over it.
- If the rule is too broad, narrow it before writing.
- Keep the final response short: changed file, commit hash, pushed status.
