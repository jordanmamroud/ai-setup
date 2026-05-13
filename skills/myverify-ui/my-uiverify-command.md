---
description: Verify the UI feature you just built using ui-verify. Self-contained — works in any project regardless of CLAUDE.md.
---

Verify the UI work you just did using `ui-verify`. Don't ask me to check first; verify yourself, fix every ❌ finding, then ask me after `Verdict: pass`.

## What ui-verify is

`ui-verify` is a bash command at `~/bin/ui-verify` (a symlink to `~/mylab/ai-setup/skills/myverify-ui/ui-verify`). It spawns an isolated `claude -p` subprocess with a verifier system prompt inlined, drives a real Chromium browser via Playwright per a brief you provide, and returns a tight markdown pass/fail report. The isolation is the whole point — Playwright snapshots and DOM dumps stay in that subprocess, so your context window stays clean.

**Always invoke via the bash command:**

```
ui-verify http://localhost:<port> "<brief>"
```

Do NOT try to invoke a `ui-verifier` subagent via the Agent tool — the file is deliberately outside `~/.claude/agents/` so it isn't auto-discovered. The bash bridge is the only correct invocation path.

Exit codes: `0` = pass, `1` = fail/partial, `2` = tooling error.

## How

1. Confirm the dev server is running. If you don't know the URL, ask me once.
2. Compose a brief covering each applicable dimension (see below).
3. Run `ui-verify http://localhost:<port> "<brief>"`.
4. Read the report. Fix every ❌ in source. Re-run. Cap at 5 fix iterations.
5. Only after `Verdict: pass`, surface the result.

## Brief format — minimum dimensions

For every brief, include each that applies:

**Real user behavior** — list specific cases a real user would actually exercise on this feature, including ones that try to break it. The bugs live in things the feature wasn't designed for, not the happy path. The dimensions below describe how the feature should behave **for each case listed here**, not for "the feature" in the abstract.

Format each entry concretely. Not `"long input"` — `"a 150-word research-style prompt that takes >30s to process"`. Not `"rapid clicks"` — `"click Submit 5 times within 200ms"`. The verifier executes exactly what you list; vague descriptions produce vague verification.

Cover at least one entry per category. If a category genuinely does not apply to this feature, write `n/a — <one-line reason>` for that category. Silent omission counts as brief-incomplete.

1. **Input variety** — trivial input; realistic-typical input; pathological input (long paste, unicode / RTL / emoji, malformed, empty, single-character).
2. **Sequence variety** — rapid-fire clicks or submissions; cancel mid-flight; resubmit while a previous request is still running.
3. **State variety** — reload mid-flight; multi-tab concurrent same user; returning after auth/session expiry; browser back button after the action.
4. **Error states** — slow network; server returns 5xx; subprocess hangs past timeout; user goes offline mid-flight.
5. **Concurrent / conflicting state** (only if the feature has shared mutable state) — two tabs same user both editing; long-running operation from another session; cross-user contention on a shared record.

**For bug fixes:** include the EXACT input or sequence that originally triggered the bug as one of the entries above. Do not simplify it. The bug lives in the failure case, not in your reduction of it.

**Standard dimensions** (in addition to the real-user-behavior list above):

- **Feature** — one line.
- **UI appearance** — what's visible, where, label, initial state. Use stable `data-testid` selectors when available.
- **Interaction** — exact selectors and exact actions; expected visible result. Cover the sequences from "Real user behavior" above.
- **State transitions** — loading, empty, success, error. Exercise both the trivial *and* realistic input cases.
- **API / data flow** — expected method + path + status.
- **Persistence intent** — REQUIRED for any action with verbs like delete/save/create/update/sync/persist/store/write/submit, OR that touches a DB / API / localStorage / file / cookie. Either:
  - name the backing store and the verification command (e.g. `sqlite3 ./dev.db 'SELECT count(*) FROM ...'` should return 0), OR
  - explicitly state "UI-only stub — no network request should fire, no backing store should change."
  Silence is an automatic `❌ Brief incomplete` → fail. The verifier will refuse to pass.
- **Functional outcome** — the end state the user can observe.

## Final message — only after Verdict: pass

```
✅ Task complete — verified by ui-verify.
What changed: <one line>
What the verifier confirmed: <bulleted ✅ dimensions>
Please open <URL> to do your own UI check.
```

If you hit the iteration cap with `❌` findings still present, surface the verifier's last report and explicitly say the task is NOT verified.

## One ui-verify run at a time per project

Two ui-verify runs against the same dev server / backing store will race and produce false `❌` findings. If another agent in this project might also be verifying, serialize. Cross-project parallelism is fine.

## Do not edit the verifier

The verifier definition lives at `~/mylab/ai-setup/skills/myverify-ui/system-prompt.md`. The bash bridge lives at `~/mylab/ai-setup/skills/myverify-ui/ui-verify`. Don't edit either. Both have been tuned across multiple rounds of adversarial testing. If the verifier is wrong about something, surface the disagreement to me — don't patch the verifier to make a failing run pass.
