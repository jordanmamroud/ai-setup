# myverify-ui

A user-level tool that gives any AI coding agent a way to verify UI behavior in a running web app — autonomously, with bounded context cost.

## The problem it solves

When AI agents (Claude Code, Codex CLI, Cursor, etc.) make UI changes, they need to confirm the result actually works. Two common options both fall short:

1. **Inline Playwright MCP.** Calling the browser MCP from the main agent's session works but blows context: each accessibility-tree snapshot is 5k–100k tokens, and it accumulates across every action. A few clicks on a real SPA can consume 100k+ tokens just on observation overhead.
2. **Unit tests.** Agents either skip writing them, write hollow ones that pass without verifying anything real, or pass tests that don't reflect actual UI behavior.

`ui-verify` puts the Playwright work inside an isolated subagent, so all the snapshot bloat lives in that subagent's own context window. The main agent only sees the verdict (~10 lines of markdown), can iterate fix → verify → fix, and stays under ~5% of its context spent on verification.

## Goal

Make UI verification cheap, autonomous, and trustworthy enough that an agent can confidently say "this is done" — and be right.

## Using it

### Prerequisites

- Claude Code installed (`claude` on PATH).
- `jq` on PATH (for parsing Claude's JSON output and writing the run-history index). Install via `brew install jq` (macOS) or `apt-get install jq` (Linux).
- Node.js with `npx` available (so the bridge can launch Playwright MCP on demand).

Playwright MCP itself does **not** need to be installed at user scope. The bridge ships an `mcp.json` (sibling of the script) that wires Playwright MCP in for the verifier subprocess only, via `claude -p --mcp-config`. Other projects' main-agent sessions never load Playwright. If you previously installed it user-wide via `claude mcp add --scope user playwright …`, you can (and probably should) remove it: `claude mcp remove playwright`.
- The four source files in their canonical locations (all in this repo):
  - `~/mylab/ai-setup/skills/myverify-ui/system-prompt.md` — the verifier's system prompt. Read by the bash bridge and inlined into a fresh `claude -p` subprocess. Deliberately NOT in `~/.claude/agents/` so Claude Code does not auto-discover it as a subagent.
  - `~/mylab/ai-setup/skills/myverify-ui/ui-verify` — the bash bridge (the script itself). Symlinked into `~/bin/` so the command is on PATH.
  - `~/mylab/ai-setup/skills/myverify-ui/mcp.json` — declares Playwright MCP for the verifier subprocess only. Wired in via `claude -p --mcp-config "$SCRIPT_DIR/mcp.json"`. Means Playwright MCP is **not** loaded into your other projects' main-agent contexts, only into ui-verify runs.
  - `~/mylab/ai-setup/skills/myverify-ui/my-uiverify-command.md` — the slash-command source. Symlinked into `~/.claude/commands/my-uiverify.md` so `/my-uiverify` works in any Claude Code session. (The repo filename and the symlink filename differ deliberately — the symlink filename is what determines the typed slash-command name.)

### Invoking it

From any shell, any CI step, any agent's Bash tool:

```
ui-verify http://localhost:<port> "<brief>"
```

Output is a markdown report on stdout. Exit codes: `0` = pass, `1` = fail/partial, `2` = tooling error. Composable with `&&`.

### Writing a brief

The brief is the only thing the verifier sees — no source code, no commit history, just the URL and your description. Cover every applicable dimension:

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
- **State transitions** — loading, empty, success, error. For each, exercise both the trivial *and* realistic input cases.
- **API / data flow** — expected method + path + status.
- **Persistence intent** — REQUIRED for actions with verbs like delete/save/create/update/sync/persist/store/write/submit, OR that touch a DB / API / localStorage / file / cookie. Either:
    - name the backing store and the verification command (e.g. `sqlite3 ./dev.db 'SELECT count(*) FROM ...'` should return 0), OR
    - explicitly state "UI-only stub — no network request should fire, no backing store should change."
  Silence is an automatic `❌ Brief incomplete` → fail.
- **Functional outcome** — the end state the user can observe.

A vague brief gets a vague verification. Spell out every dimension that applies.

### File layout

Everything ui-verify-related lives in this folder. Two symlinks elsewhere on disk make the bash command typeable from any shell and the slash command typeable in any Claude Code session — but the *real* files all live here as a single source of truth.

```
~/mylab/ai-setup/skills/myverify-ui/
├── README.md          ← you are here
├── system-prompt.md   ← canonical verifier instructions (read by the bridge)
├── ui-verify          ← canonical bash bridge (the actual executable)
├── mcp.json           ← MCP servers exposed to the verifier subprocess (Playwright)
├── my-uiverify-command.md  ← canonical slash-command body (description + how-to)
├── config.sh          ← optional overrides (prompt path, allowlist, model)
└── STATUS.md          ← session-by-session status snapshot

~/bin/
└── ui-verify  →  ~/mylab/ai-setup/skills/myverify-ui/ui-verify          ← puts the bash command on PATH

~/.claude/commands/
└── my-uiverify.md  →  ~/mylab/ai-setup/skills/myverify-ui/my-uiverify-command.md  ← exposes /my-uiverify in any Claude Code session
```

To inspect or edit anything: open the file in `~/mylab/ai-setup/skills/myverify-ui/`. The two symlinks elsewhere are "views" — touching either through its symlink modifies the real file here.

The bridge **self-locates** at runtime: it follows `${BASH_SOURCE[0]}` through the symlink to find the directory it physically lives in, then reads `system-prompt.md`, `mcp.json`, and `config.sh` as siblings of that directory. So renaming or moving this folder doesn't require touching anything inside the script. (The symlinks themselves still need re-creating on rename — see "Moving, renaming, or losing files" below.)

### Install (or re-create after clone / rename)

Two symlinks. Run once after first checkout, or whenever you've moved the folder:

```
ln -sf "$(pwd)/ui-verify" ~/bin/ui-verify
ln -sf "$(pwd)/my-uiverify-command.md" ~/.claude/commands/my-uiverify.md
```

(Run from inside `~/mylab/ai-setup/skills/myverify-ui/`. `-f` overwrites any stale symlink.)

### Configuration

Four values are configurable: the path to `system-prompt.md`, the path to `mcp.json`, the tool allowlist passed to `claude -p`, and the model. Precedence:

```
script defaults  <  config.sh (sibling of the script)  <  UI_VERIFY_* env vars
```

The defaults assume `system-prompt.md` and `mcp.json` are siblings and the allowlist + model are what the verifier needs out of the box, so for normal use you don't need to do anything — `config.sh` ships with everything commented out. Uncomment a line in there if you want a persistent override; set `UI_VERIFY_PROMPT_FILE`, `UI_VERIFY_MCP_CONFIG`, `UI_VERIFY_ALLOWED_TOOLS`, or `UI_VERIFY_MODEL` if you want a one-shot override at runtime.

### Run history

Every invocation writes a record to `~/.local/share/ui-verify/` (override with `UI_VERIFY_HISTORY_DIR`):

```
~/.local/share/ui-verify/
├── runs.jsonl                  ← one JSON row per run (analytics index)
└── runs/<run_id>/
    ├── brief.md                ← the brief that was sent to the verifier
    ├── response.md             ← the verifier's full markdown report
    └── meta.json               ← the same row from runs.jsonl, pretty-printed
```

`run_id` is a UTC timestamp + 4-hex-char random suffix, e.g. `20260509T124500Z-a3f1`.

Each `runs.jsonl` row carries: `run_id`, `ts_start`/`ts_end`, `url`, `brief`, `exit_code`, `verdict_pass`, `model`, `allowed_tools`, `prompt_file`, `system_prompt_sha` (8-char prefix; lets you group runs by verifier-prompt version), `config_signature`, `caller_cwd` and `caller_git_sha` + `caller_git_dirty` (so you can tie a verdict to the exact code state that produced it), `notes` (see below), and the full `claude` payload from `claude -p --output-format json` (cost, duration_ms, num_turns, token usage, the response text).

To tag a run for later filtering, set `UI_VERIFY_NOTES`:

```
UI_VERIFY_NOTES="haiku trial 2" ui-verify http://localhost:7878 "<brief>"
```

Then query with `jq`:

```
jq 'select(.notes | startswith("haiku trial"))' ~/.local/share/ui-verify/runs.jsonl
jq 'select(.exit_code != 0) | {run_id, brief, cost: .claude.total_cost_usd, dur_ms: .claude.duration_ms}' \
    ~/.local/share/ui-verify/runs.jsonl
```

The `.claude.*` field names depend on what Claude Code's `--output-format json` emits at the time of the run; the bridge stores the raw payload so future field renames don't lose data.

Logging is best-effort — if writing the history fails (disk full, permission issue), the bridge prints a warning to stderr and the verification itself still succeeds or fails per its own verdict.

### Moving, renaming, or losing files

The bridge self-locates via `${BASH_SOURCE[0]}`, so the folder can move freely — only the two external symlinks (`~/bin/ui-verify`, `~/.claude/commands/my-uiverify.md`) need re-pointing.

| Change | Effect | Fix |
|---|---|---|
| Folder renamed/moved | Both symlinks dangle | `cd <new-path>`, re-run Install snippet |
| `ui-verify` renamed | `~/bin/ui-verify` dangles | `ln -sf "$(pwd)/<new-name>" ~/bin/ui-verify` |
| `my-uiverify-command.md` renamed | `~/.claude/commands/my-uiverify.md` dangles | Re-create the symlink (its filename = the typed `/my-uiverify` name) |
| `system-prompt.md` renamed/moved | Bridge exits 2 — required file missing | `UI_VERIFY_PROMPT_FILE=…` or set `PROMPT_FILE` in `config.sh` |
| `mcp.json` renamed/moved/deleted | Bridge prints `Warning:` to stderr and continues; verifier loses Playwright and falls back to scripted Bash. Malformed JSON in `mcp.json` is a hard `Error:` (exit 2). | `UI_VERIFY_MCP_CONFIG=…` or set `MCP_CONFIG_FILE` in `config.sh` |
| `config.sh` renamed/deleted | Silent: bridge uses defaults | Restore, or use `UI_VERIFY_*` env vars |
| History dir deleted | Past runs lost | None — recreated on next run |
| History dir moved | New runs write to default path | `UI_VERIFY_HISTORY_DIR=…` or set `HISTORY_DIR` in `config.sh` |

### The iteration loop

1. Make the UI change.
2. Run `ui-verify <url> "<brief>"`.
3. Read the report. For each `❌`, fix in source.
4. Re-run.
5. Cap at 5 code-fix iterations. If still failing, surface the report and stop.

### Final message — only after Verdict: pass

```
✅ Task complete — verified by ui-verify.
What changed: <one line>
What the verifier confirmed: <bulleted ✅ dimensions>
Please open <URL> to do your own UI check.
```

If the iteration cap is hit with `❌` findings still present, surface the verifier's last report and explicitly say the task is NOT verified.

### Don't invoke the subagent directly

`ui-verify` (the shell wrapper) is the only correct entry point. Calling `Agent(subagent_type='ui-verifier')` from inside a Claude Code session technically works — Claude Code auto-discovers the subagent file — but it runs the verifier in your *main* session's process, defeating the context isolation that's the entire reason for the wrapper. Always go through the shell command.

## Drop-in CLAUDE.md content for your project

To enable this policy in a project, append the block below to that project's `CLAUDE.md` (or to `~/.claude/CLAUDE.md` for user-wide enablement). It declares what `ui-verify` is, when to use it, the brief format, the iteration loop, and the "do not edit the verifier" prohibition. Copy-paste verbatim.

```markdown
## UI verification — use ui-verify before claiming a UI task done

### What ui-verify is

`ui-verify` is a bash command at `~/bin/ui-verify` that spawns an
isolated `claude -p` subprocess with the verifier's system prompt
(at `~/mylab/ai-setup/skills/myverify-ui/system-prompt.md`) inlined via
`--append-system-prompt`. The verifier drives a real Chromium browser
via Playwright, exercises the page per a brief you provide, and returns
a tight markdown pass/fail report.

Why an isolated subprocess: the verifier produces verbose tool output
(Playwright snapshots, screenshots, DOM dumps) that would balloon your
context window if inlined. The bash bridge spawns a fresh `claude -p`,
runs the verifier there, and returns only the markdown report — your
context stays clean.

**Always invoke via the `ui-verify` bash command.** The verifier prompt
lives outside `~/.claude/agents/` deliberately, so it is not
auto-discovered as a Claude Code subagent — the bash bridge is the only
invocation path. Tool allowlist (`Bash Read Write mcp__playwright__*`)
and model (`sonnet`) are enforced as `claude -p` CLI flags inside the
bridge.

    Usage:    ui-verify http://localhost:<port> "<brief>"
    Exits:    0 on pass, 1 on fail/partial

### When to use it

When you finish a frontend / UI task — anything where the artifact is
something the user would see in a browser — verify it via `ui-verify`
before declaring the task done. Don't ask the user to check it themselves
first; do the verification yourself, fix every ❌ finding, then ask the
user to check after a `Verdict: pass`.

Applies to: new components, new pages, new buttons or forms, render-bug
fixes, refactors that touch UI code paths, any change to rendered DOM /
layout / styling / interaction / browser-visible state.

Doesn't apply to: pure backend changes, library or CLI code with no local
dev server, docs / comments / build config without behavior change.

### How

1. Get the dev server running. Discover the URL from the project's README,
   package.json scripts, or ask the user once per session.
2. Compose a brief covering each applicable dimension (see below).
3. Run `ui-verify http://localhost:<port> "<brief>"`.
4. Read the report. Fix every ❌ in source. Re-run. Cap at 5 code-fix
   iterations.
5. Only after `Verdict: pass`, surface the result to the user and ask them
   to do their own UI check.

### Brief format — minimum dimensions

For every brief, include each that applies:

**Real user behavior** — list specific cases a real user would actually
exercise on this feature, including ones that try to break it. The bugs
live in things the feature wasn't designed for, not the happy path. The
dimensions below describe how the feature should behave **for each case
listed here**, not for "the feature" in the abstract.

Format each entry concretely. Not `"long input"` — `"a 150-word
research-style prompt that takes >30s to process"`. Not `"rapid clicks"`
— `"click Submit 5 times within 200ms"`. The verifier executes exactly
what you list; vague descriptions produce vague verification.

Cover at least one entry per category. If a category genuinely does not
apply, write `n/a — <one-line reason>` for that category. Silent
omission counts as brief-incomplete.

1. **Input variety** — trivial input; realistic-typical input;
   pathological input (long paste, unicode / RTL / emoji, malformed,
   empty, single-character).
2. **Sequence variety** — rapid-fire clicks or submissions; cancel
   mid-flight; resubmit while a previous request is still running.
3. **State variety** — reload mid-flight; multi-tab concurrent same
   user; returning after auth/session expiry; browser back button.
4. **Error states** — slow network; server returns 5xx; subprocess
   hangs past timeout; user goes offline mid-flight.
5. **Concurrent / conflicting state** (only if the feature has shared
   mutable state) — two tabs same user both editing; long-running
   operation from another session; cross-user contention on a shared
   record.

**For bug fixes:** include the EXACT input or sequence that originally
triggered the bug as one of the entries above. Do not simplify it.

**Standard dimensions** (in addition to the real-user-behavior list above):

- **Feature** — one line.
- **UI appearance** — what's visible, where, label, initial state. Use
  stable `data-testid` selectors when available.
- **Interaction** — exact selectors and exact actions; expected visible
  result. Cover the sequences from "Real user behavior" above.
- **State transitions** — loading, empty, success, error. Exercise both
  the trivial *and* realistic input cases.
- **API / data flow** — expected method + path + status.
- **Persistence intent** — REQUIRED for any action with verbs like
  delete/save/create/update/sync/persist/store/write/submit, OR that
  touches a DB / API / localStorage / file / cookie. Either:
    - name the backing store and the verification command (e.g.
      `sqlite3 ./dev.db 'SELECT count(*) FROM ...'` should return 0), OR
    - explicitly state "UI-only stub — no network request should fire,
      no backing store should change."
  Silence is an automatic `❌ Brief incomplete` → fail.
- **Functional outcome** — the end state the user can observe.

### Final message — only after Verdict: pass

    ✅ Task complete — verified by ui-verify.
    What changed: <one line>
    What the verifier confirmed: <bulleted ✅ dimensions>
    Please open <URL> to do your own UI check.

If the iteration cap is hit with `❌` findings still present, surface the
verifier's last report and explicitly say the task is NOT verified.

### Do not edit the verifier definition

`~/mylab/ai-setup/skills/myverify-ui/system-prompt.md` is the verifier's standing
instruction set. It's been tuned across multiple rounds of adversarial
testing and is load-bearing — every project's verification depends on it.

**Do not edit it, and do not edit `~/bin/ui-verify`.** If you think the
verifier is wrong about something, that's almost always (a) a bug in the
brief you sent it, or (b) a real finding you should address in source.
Editing the verifier to make a failing run pass is exactly the
Goodhart-law shortcut the adversarial design is built to prevent. Surface
the disagreement to the user — they decide whether the verifier needs
adjusting.
```

### Pair it with a Validation Requirements preface (optional but useful)

If your project doesn't already have one, the verifier-block pairs naturally with a short preface that tells the agent what "done" means and what other signals to check:

```markdown
## Validation Requirements

"Done" means the task is verifiable in the UI, not "the code looks right."

UI verification is the primary loop. Don't write or run unit / integration tests unless explicitly requested. The agent must verify its own work via `ui-verify` before declaring done — see the section below.

Two adjacent signals must also be clean before declaring done:

- **Lint + typecheck** — run on every change.
- **Server logs** — check the terminal running the dev server for any errors, warnings, or unhandled promise rejections produced during the UI interaction. The verifier sees the browser; you have to see the server.
```

The "server logs" signal matters because the verifier sees the *browser* — console errors, page errors, failed HTTP responses on the page's origin — but not the dev server's own stdout. A backend silently logging `[ERROR] Database connection lost` to its own terminal slips past the verifier entirely. Catching that is on you.

## Or — the `/my-uiverify` slash command

For one-shot invocations in a project that *doesn't* have the drop-in CLAUDE.md block (yet, or by choice), there's a user-level slash command. Type `/my-uiverify` in any Claude Code session and the agent gets the same how-to injected as a user message — same self-contained content as the drop-in block (what ui-verify is, the brief format including the persistence-intent gate, the iteration loop, final-message format, "don't edit the verifier"). The agent doesn't need any prior priming.

When to use which:

- **Drop-in CLAUDE.md block** — for projects where every UI task should *always* go through ui-verify. Standing rule, loaded into every session in that project automatically.
- **`/my-uiverify` slash command** — for one-off use in a project that's intentionally lean (or a project you haven't gotten around to dropping the block into yet). User-triggered each time.

The two are complementary, not exclusive. A project can have both — the standing rule does the work most of the time; the slash command is a manual reset if a green agent ever forgets.

The command's source file lives in this repo at `my-uiverify-command.md` and is symlinked into `~/.claude/commands/my-uiverify.md` (Claude Code's user-level command directory; the symlink filename is what determines the typed `/my-uiverify` name, not the repo filename). To update it, edit the canonical file here — the symlink picks up the change automatically. To set it up on a fresh machine, run the `Install` snippet from the "File layout" section above.

## Architecture

Two files plus a pre-installed MCP server. Everything lives at user scope so it works in any project.

| Component | Location | Purpose |
|---|---|---|
| Verifier system prompt | `~/mylab/ai-setup/skills/myverify-ui/system-prompt.md` | The "brain" — drives Playwright, returns the markdown report. Read by the bash bridge and inlined into a fresh `claude -p` subprocess via `--append-system-prompt`. Deliberately NOT in `~/.claude/agents/` so Claude Code does not auto-discover it as a subagent. |
| Bash bridge (canonical) | `~/mylab/ai-setup/skills/myverify-ui/ui-verify` | The actual executable. Spawns `claude -p` with the verifier prompt + tool allowlist + model baked in as flags. |
| Bash bridge (PATH-accessible name) | `~/bin/ui-verify` → symlink to the canonical path | Symlink so `ui-verify <url> "<check>"` is typeable from any shell, CI step, Makefile, or Bash tool. |
| Playwright MCP | Declared in `~/mylab/ai-setup/skills/myverify-ui/mcp.json` and passed to `claude -p` via `--mcp-config` | Browser driver. Loaded only inside the verifier subprocess — not user-scope, so other projects' main-agent contexts don't carry the Playwright tool definitions. Auto-installed on first run via `npx -y @playwright/mcp@latest`. |
| Runtime artifacts | `/tmp/ui-verify/` | Screenshots saved here per run. Auto-cleared on reboot. |

## How it works

```
[ main agent makes a UI change ]
              ↓
[ main agent calls: ui-verify <url> "<check>" ]   ← shell, or Agent tool inside Claude Code
              ↓
[ subagent drives headless Chromium via Playwright MCP ]
              ↓
[ markdown report on stdout: Verdict + ✅/❌ findings + screenshot paths ]
              ↓
[ main agent reads, fixes ❌ items, re-runs ]
              ↓
[ loop until Verdict: pass ]
```

Shell exit codes: `0` = pass, `1` = fail/partial, `2` = tooling error. Composable: `ui-verify ... && git commit ...`.

## Key design choices

- **Subagent, not inline MCP.** Context isolation is the entire point. Snapshot bloat lives in the subagent's window, not the main agent's.
- **Adversarial mission, not happy-path verification.** The agent is told to *try to break the app* — find races, edge cases, silent no-ops, concurrency bugs.
- **Autonomous; never pauses for approval.** Pre-authorized for destructive actions (delete, cancel, log out). Cost rule: under ~$10 per run, just do it.
- **Markdown output, not JSON.** LLMs parse markdown natively. The next-agent contract is "find lines starting with ❌."
- **Locator-specific findings.** Every ❌ names a selector, button label, or DOM id so the calling agent can find the relevant code without guessing.
- **No project-level state.** The tool is global; project-specific knowledge (which port, which flows) lives in each project's `CLAUDE.md`.

## Validated

- Smoke test on a controlled static fixture — passed cleanly end-to-end via a fresh `claude -p` subprocess (proves the auto-discovery + MCP path work).
- Full adversarial run on a real Next.js SPA (the `researcher` app on `localhost:7777`):
  - Smoke check: pass
  - 4-LLM research session with synthesis tab: functional pass, surfaced 1 UX nuance
  - Hover-and-delete with autonomous target picking: pass
  - Adversarial parallel + cancel, follow-up, regenerate: **15 substantive bugs surfaced across 3 runs** — including a broken Cancel button, a Round 2 visibility issue, and a silent-no-op pattern repeated in 3 separate inputs.

## Known caveats

- **`claude -p` will not exit while Claude Code background tasks are still running.** If the calling agent starts a dev server via `Bash(run_in_background=true)`, then declares the task done, `claude -p` hangs indefinitely waiting for that background task to terminate — and no stdout is flushed in the meantime, so it looks like the verifier itself hung. The fix lives in the calling project's `CLAUDE.md`: explicitly kill the dev server before emitting the final assistant message (`lsof -ti:<PORT> | xargs kill 2>/dev/null`). Alternative: detach the server with `nohup ./serve.sh > /dev/null 2>&1 & disown` so it isn't tracked as a Claude Code task.

- **MCP tools may not be exposed inside `claude -p` subprocesses invoked via the Agent tool.** The verifier's frontmatter authorizes `mcp__playwright__*`, but in nested-subprocess contexts those tools can be absent. The verifier handles this by falling back to scripted Playwright via Bash + Write — works, but more fragile (LLM-generated scripts sometimes have syntax errors and require iteration). Verifications that take ~30s with MCP can take ~60-90s on the script fallback path while the agent figures out which Playwright runtime is installed (`node` vs `python3`).

- **Don't trust the example port numbers in any prompt.** The verifier's system prompt and `~/bin/ui-verify` usage examples deliberately use varied placeholder ports (`<PORT>`, 8080, 3000, 5173) precisely because earlier versions hardcoded `:7777` everywhere and risked priming the verifier toward that port in unrelated projects. Always pass the URL explicitly in the brief.

- **One ui-verify run at a time per project.** The bridge itself has no locks — every `ui-verify` invocation runs in a fully isolated `claude -p` subprocess, so *cross-project* parallelism is fine (mybrain on `:3002` and researcher on `:7777` running simultaneously, no conflict). But two runs against the *same* project share the dev server, the backing store, and the session state, so any persistence-flavored verification races against itself. If both runs write to `bank.json`, the post-step `cat` assertions see whichever write committed last and you get false `❌` findings on both runs. Today's workaround: if two coding agents on the same project both want to verify, serialize them — agent B waits for agent A to finish. In practice you usually only have one agent per project at a time, so this rarely matters.

  **Future fix, when "multiple agents per project" becomes a real workflow** — two paths, increasing effort:

  1. **Queue via flock (one-line change to the bridge).** Wrap the `claude -p` invocation in `flock /tmp/ui-verify-<project-hash>.lock`. Concurrent invocations block until the previous run releases the lock. Doesn't actually parallelize — just serializes safely so no run sees stale state. Easy and removes races without any per-project setup.
  2. **Per-agent isolation (real parallelism).** Spawn one dev server per agent on its own port, with its own copy of the backing store (a temp-dir snapshot of `v0/data/` for mybrain, a per-agent SQLite file elsewhere, etc.). Each agent calls `ui-verify http://localhost:<its-port>` against its own instance. True parallelism. Requires the project's dev server to support being instantiated multiple times with isolated state — for Next.js + JSON files this is straightforward (different `PORT` env var + different working directory); for projects with an external service or shared DB, it's more work and may need a `--profile=<id>` flag in the dev server itself.

  Pick path 1 if you just want safety and don't care about wall time. Pick path 2 if verification latency is the bottleneck and the project's state model supports clean replication.

## Roadmap

- **v1 (done):** Claude Code subagent + shell wrapper around `claude -p`.
- **v2 (next):** Codex CLI variant — same subagent contract but invokable via `codex exec` for non-Claude tooling paths.
- **Optional:** `--json` output mode for programmatic consumers; PostToolUse hook integration for auto-verify after UI file edits.
