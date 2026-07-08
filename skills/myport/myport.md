---
description: Open the current localhost dev server in Safari, reusing an existing tab for the same port.
disable-model-invocation: true
---

# myport

Open the current localhost dev server in Safari. If a tab for that port is
already open, focus it. Otherwise, open a new tab in the frontmost Safari
window. Never reload (preserves page state). Never kill another process to
free a port.

## Steps

1. **Find the port.**
   - Check this session for a dev server you (or the user) started on a
     localhost port. If one exists, use that port.
   - Otherwise, start one using the project's own tooling (`npm run dev`,
     `pnpm dev`, `vite`, `bun dev`, `python3 -m http.server`, whatever the
     project uses). Run it in the **background** with Bash's
     `run_in_background: true` — `npm run dev` and friends block otherwise.
   - Read the **actual** port from the tool's stdout. Don't assume the
     default — Vite, Next, etc. auto-fall-back when the default is taken
     (5173 → 5174). If the dev tool prints `127.0.0.1:<port>` instead of
     `localhost:<port>`, that's fine — use the port number; the
     AppleScript matches on `localhost:<port>` regardless.
   - If the project has no obvious dev-server command (no `package.json`,
     no dev script, etc.), **stop and ask** the user. Don't guess.

2. **Validate the port.** It must match `^[0-9]+$`. If it doesn't, abort
   and report the bad value. (This is the only injection guard for the
   AppleScript — don't skip it.)

3. **Open / focus the tab.** Run this AppleScript via `osascript -e`,
   substituting `<PORT>` with the validated digits:

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
     return found
   end tell
   ```

   The script returns `true` if it focused an existing tab, `false` if it
   opened a new one. Capture stdout to decide which message to report.

4. **Report back.** One line:
   - `opened existing tab → http://localhost:<PORT>/` (focused), or
   - `opened new tab → http://localhost:<PORT>/`.

   If you started a dev server in step 1, also note that on a separate
   line (e.g., `started dev server on port <PORT>`).

## Errors

- **`osascript` exits with error -1743** ("not authorized to send Apple
  events to Safari"): macOS Automation permission hasn't been granted yet.
  Tell the user to approve the prompt (System Settings → Privacy &
  Security → Automation → Claude Code → Safari), then re-run `/myport`.
  Don't swallow the error.
- **Any other AppleScript error**: report stderr verbatim. Don't retry.

## Notes

- Safari only. Don't substitute Chrome/Arc/Firefox even if asked — the
  user wants Safari specifically.
- The match rule is host:port (`localhost:<PORT>` substring). Path is
  ignored, so SPA routes and Vite's `/index.html` redirect still match.
  `127.0.0.1:<PORT>` tabs **won't** match — that's accepted.
- Private browsing windows are included in the scan. If the focused tab
  ends up being a private one, mention it in the report.
- First match wins if multiple tabs share the port.
- If the server has died but a tab still exists, the tab gets focused and
  shows a browser error. That's correct — the user sees real state.
