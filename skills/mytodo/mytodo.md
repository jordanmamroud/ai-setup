---
description: Capture a quick item to mygeorge's todos.md Inbox from any session. Date, time, and current project auto-included. Multi-line pastes preserved.
---

# mytodo

Append the user's text as one entry to the Inbox section of `~/mylab/mygeorge/todos.md`. **Don't read the file. Don't categorize. Don't try to do the task itself.** This command exists to keep capture cheap and zero-friction — drop it in the inbox and stop.

## Steps

1. The user's text is in `$ARGUMENTS`. If empty, reply `/mytodo needs text — try /mytodo fix the broken link` and stop.

2. Run **one** Bash command. The user's text goes inside a single-quoted heredoc, so no escaping is needed — substitute `$ARGUMENTS` literally on its own lines between the heredoc markers:

   ```bash
   cat > /tmp/mytodo_input <<'MYTODO_EOF'
   $ARGUMENTS
   MYTODO_EOF
   {
     printf -- '- %s [%s] — %s\n' "$(date '+%Y-%m-%d %H:%M')" "$(basename "$PWD")" "$(head -1 /tmp/mytodo_input)"
     tail -n +2 /tmp/mytodo_input | sed -E 's/^(.+)/  \1/'
   } > /tmp/mytodo_entry
   awk '/<!-- inbox:end -->/ { while ((getline l < "/tmp/mytodo_entry") > 0) print l; print "" } { print }' ~/mylab/mygeorge/todos.md > /tmp/mytodo_new && mv /tmp/mytodo_new ~/mylab/mygeorge/todos.md
   rm /tmp/mytodo_input /tmp/mytodo_entry
   ```

   If `$ARGUMENTS` happens to contain a line that is exactly `MYTODO_EOF`, change the heredoc tag to something else (e.g. `MYTODO_EOF_2`) on both lines.

3. Reply with exactly one line: `added to mygeorge inbox`. Nothing else.

## Notes

- The **first line** of `$ARGUMENTS` becomes the bullet headline (after `— `). Remaining lines are preserved verbatim and indented 2 spaces so they nest visually under the bullet. Blank lines stay blank.
- Convention for clean entries: type your gripe first, press Enter (creating a blank line), then paste any context. The blank line comes through as the separator between headline and context.
- Entry slots in immediately before the `<!-- inbox:end -->` sentinel in the Inbox section. Sentinel must stay in place for future appends.
- Project name = `basename "$PWD"` — the directory the user invoked `/mytodo` from.
- Don't open or read `todos.md` content. The point is zero context cost.
