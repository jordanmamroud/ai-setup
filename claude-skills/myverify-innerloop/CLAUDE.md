# myverify-innerloop

Project for building AI coding agent self-verification — inner loop (lint/types/tests) and outer loop (architecture/feature review). The canonical command file `my-verify-innerloop.md` lives here and is symlinked from `~/.claude/commands/`.

## Lessons

### Match rules to the specific example, not the category

When the user names an antipattern (e.g. "no `as unknown as X`"), don't search the rule catalog by category ("type assertion rules") and ship the first plausible matches. Check that each rule's actual trigger condition fires on the exact example given.

I missed the `no-restricted-syntax` selector `TSAsExpression > TSAsExpression` because I framed the problem as "find typescript-eslint rules for bad assertions" instead of "what AST shape is `as unknown as X` and what catches that shape." Reframing the antipattern as a *syntax* problem rather than a *rule-name* problem opens up `no-restricted-syntax`, which I'd otherwise never reach for.

Checklist before recommending a rule:
- Does the rule's documented trigger match the specific example, not just the category name?
- If the user's example slips past every rule I'm proposing, the proposal is incomplete — say so rather than shipping it.
- Consider AST-level tools (`no-restricted-syntax`, custom selectors) when a named rule doesn't fit.
