# /myport — brainstorm

Date: 2026-05-09
Status: design approved, not yet built

## What it is

A Claude Code slash command that opens a localhost dev server in Safari,
reusing the existing tab for that port if one is already open. Intended to
end the "agent reports a port → I copy/paste into a new Safari window every
time" papercut.

Final artifact: a single markdown file at `~/.claude/commands/myport.md`.
Dev folder (this folder): `/Users/jordanmamroud/myquickie/mycommands/myport/`.

## Behavior

When the user types `/myport` in any Claude Code session, the agent:

1. Checks the current session for a dev server it (or the user) has already
   started on a localhost port.
   - **If one exists** → use that port.
   - **If not** → start one on a free port using the project's own tooling
     (`npm run dev`, `pnpm dev`, `vite`, `bun dev`, whatever the project
     uses). Run it in the background. Read the actual port the server
     reports — don't assume — because tools auto-fallback when the default
     is taken (Vite 5173 → 5174, etc.).
   - **Never kill** an existing process to free a port. Other agents may be
     running servers; leave them alone.
2. Runs an AppleScript via `osascript` that:
   - Scans every tab in every Safari window for a URL whose host:port is
     `localhost:<PORT>` (any path — Vite-style redirects from `/` to
     `/index.html` or SPA routes still match).
   - **Match found** → focus that window, switch to that tab, activate Safari.
     No reload (preserves page state; user can Cmd+R if they want fresh).
   - **No match** → in the frontmost Safari window, open a new tab at
     `http://localhost:<PORT>/`. If Safari has zero windows open, create one
     first.
3. Reports back: "opened existing tab" vs "opened new tab", and the port.

## Decisions (and what was rejected)

| Decision | Chosen | Rejected |
|---|---|---|
| Command name | `/myport` | `/myopenport`, `/openport`, `/port` |
| Input | None — agent uses session context | Bare port arg, URL arg, lenient parser |
| Tab match rule | host:port, ignore path | Exact URL, port-only |
| Browser | Safari, hardcoded | Configurable via flag or env |
| Path opened | `/` (root) | Honor agent-supplied path |
| Reload existing tab? | No, just focus | Yes, reload on every invocation |

## The AppleScript

The slash command file embeds this. `<PORT>` is substituted by the agent
before invocation.

```applescript
tell application "Safari"
  set targetPort to "<PORT>"
  set found to false
  repeat with w in windows
    repeat with t in tabs of w
      if URL of t contains "localhost:" & targetPort then
        set current tab of w to t
        set index of w to 1
        set found to true
        exit repeat
      end if
    end repeat
    if found then exit repeat
  end repeat
  if not found then
    if (count of windows) = 0 then make new document
    tell front window to set current tab to ¬
      (make new tab with properties {URL:"http://localhost:" & targetPort & "/"})
  end if
  activate
end tell
```

Invocation from the agent: `osascript -e '<script with PORT substituted>'`.

## Edge cases — think through before/while building

1. **First run prompts for Automation permission.** macOS will pop up
   "Claude Code wants to control Safari" the first time. User must approve.
   The command should mention this in its output if `osascript` fails with
   error -1743 (not authorized). Don't silently swallow.

2. **Safari is not running.** `tell application "Safari"` launches it. The
   `if (count of windows) = 0 then make new document` line covers the
   "Safari just launched, no windows" state. `activate` brings it forward.

3. **Safari has multiple windows, target tab is in a background window.**
   `set index of w to 1` raises that window to front. Verified behavior.

4. **Multiple tabs match the same port** (e.g., user manually duplicated).
   First match wins, loop exits. Acceptable.

5. **Private browsing windows.** They appear in `windows`. A private tab
   could match the port and get focused, which is probably what the user
   wants — but worth flagging in the command's output ("focused private
   window"). Low priority; ignore unless it actually bites.

6. **Server died but tab still exists.** Tab gets focused, page shows a
   browser error. Correct behavior — user sees the real state. Don't try
   to detect this; not worth the complexity.

7. **Port conflict — desired port taken.** Don't fight it. Let the dev
   tool fall back (most do automatically). Read the *actual* port from the
   tool's stdout, not the one you asked for.

8. **No dev server tooling in the project.** If the agent can't find an
   obvious "start dev server" command (no package.json, no dev script,
   etc.), it should report that and ask — not guess.

9. **Background process management.** `npm run dev` blocks. The agent must
   use Bash's `run_in_background: true` so the dev server keeps running
   after the command returns. Worth a one-line reminder in `myport.md`.

10. **Multiple agents, one Safari window.** This is the headline use case.
    Each agent runs `/myport` in its own session, finds its own port,
    opens a tab. AppleScript-by-design uses whichever Safari window is
    frontmost, so all five agents' tabs land in the same window. ✓

11. **`localhost` vs `127.0.0.1` in tab URL.** Some tools open with
    `127.0.0.1`. The match rule is `localhost:<PORT>` — won't match a
    `127.0.0.1:5173` tab. Decision: accept this gap. If it bites, broaden
    the AppleScript to check both substrings. Don't pre-build for it.

12. **AppleScript shell-escaping.** Port is digits-only (validate with a
    regex before substitution). No injection risk if validated.

## File layout

The logic lives in this folder. `~/.claude/commands/myport.md` is *only* a
pointer — never edit it directly.

```
~/myquickie/mycommands/myport/         ← source of truth (edit here)
  brainstorm.md                          this file
  myport.md                              the slash command (TO BUILD)

~/.claude/commands/                    ← Claude Code reads from here
  myport.md → ~/myquickie/mycommands/myport/myport.md   (symlink, do not edit)
```

The symlink points *from* `.claude/commands/` *to* the real file in `myport/`.
Edits in the dev folder are picked up instantly because Claude Code follows
the link.

## Build steps for the next session

When you open a fresh session in `~/myquickie/mycommands/myport/`:

1. Read this file.
2. Write `myport.md` — the slash command body. It should:
   - Tell the agent the behavior (steps 1–3 above).
   - Embed the AppleScript with a clear `<PORT>` substitution point.
   - Validate the port is digits-only before substituting.
   - Report back the port and whether the tab was new or existing.
3. Create the symlink so Claude Code can find the command. The real file
   stays in this folder; only a pointer goes into `.claude/commands/`:
   ```
   ln -s ~/myquickie/mycommands/myport/myport.md ~/.claude/commands/myport.md
   #     └── source (real file) ──┘ └── link (pointer) ──┘
   ```
   Verify with `ls -l ~/.claude/commands/myport.md` — output should show
   `myport.md -> /Users/jordanmamroud/myquickie/mycommands/myport/myport.md`.
4. Test in a real session: start a dummy server (`python3 -m http.server 8765`),
   run `/myport`, confirm a tab opens. Run `/myport` again, confirm it
   reuses the tab. Open a second port in another session, confirm it
   becomes a sibling tab not a new window.
5. Approve macOS Automation permission for Safari when prompted.

## Out of scope (do not build)

- Chrome / Arc / Firefox support
- Path or query-string handling beyond `/`
- Port detection from pasted URLs or LLM output
- Killing other servers to free a port
- Cross-platform support (this is macOS / Safari only)
