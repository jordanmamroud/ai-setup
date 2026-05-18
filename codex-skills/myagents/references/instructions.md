# myagents

Promote a polished global Codex behavior rule into `/Users/jordanmamroud/mylab/ai-setup/global/AGENTS.md`, then commit and push it.

## Source of truth

- Canonical file: `/Users/jordanmamroud/mylab/ai-setup/global/AGENTS.md`
- Live global file: `~/.codex/AGENTS.md`
- The live file should be a symlink to the canonical file. Run `/Users/jordanmamroud/mylab/ai-setup/codex-link-commands.sh` after edits to refresh it.
- Do not edit `~/.codex/AGENTS.md` directly.

## Workflow

1. Read the canonical `global/AGENTS.md`.
2. Take the user's proposed rule, complaint, or rough snippet from the invocation. If it is missing, ask for the rule and stop.
3. Rewrite it in the existing AGENTS voice:
   - direct, brief, concrete
   - no corporate policy phrasing
   - no vague virtue words unless they create a testable behavior
   - one rule should change one agent behavior
4. Brainstorm 2-4 candidate phrasings internally. Choose the strongest one; mention alternatives only if the tradeoff matters.
5. Insert the rule into the best existing section. Create a new section only when no existing heading fits.
6. Run:
   - `./codex-link-commands.sh`
   - `test "$(readlink "$HOME/.codex/AGENTS.md")" = "/Users/jordanmamroud/mylab/ai-setup/global/AGENTS.md"`
7. Review `git diff -- global/AGENTS.md`.
8. Commit and push the change:
   - stage only files intentionally changed for this request
   - commit message format: `Update global Codex agent rules`
   - if the change is clearly narrower, use `Add <specific behavior> to AGENTS`
   - push the current branch

## Guardrails

- Do not add scratchpad notes, one-off preferences, or project-specific rules.
- If the proposed rule conflicts with an existing rule, stop and explain the conflict instead of papering over it.
- If the rule is too broad, narrow it before writing.
- Keep the final response short: changed file, commit hash, pushed status.
