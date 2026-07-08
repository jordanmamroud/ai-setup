---
name: jm-transcript
description: Explicit-only. Use only when the user directly invokes $jm-transcript or selects jm-transcript from /skills. Append the active Codex session to transcript.md in the current project root.
---

# JM Transcript

This skill is explicit-only. Do not use it unless the user invokes `$jm-transcript` or selects it from `/skills`.

Create or update `transcript.md` in the current working directory, treating `$PWD` as the project root. This is the Codex adapter for this skill; leave the Claude slash-command file `jm-transcript.md` untouched.

## Resolve Active Codex Session

Identify the current Codex session before writing anything.

1. Set `PROJECT_DIR="$PWD"`.
2. Search `~/.codex/sessions/**/*.jsonl` for session files whose `session_meta.payload.cwd` equals `PROJECT_DIR` or whose latest `turn_context.payload.cwd` equals `PROJECT_DIR`.
3. Prefer the matching file with the newest filesystem mtime.
4. Verify the selected file contains a recent `turn_context` for `PROJECT_DIR`.
5. If more than one matching file has the same newest mtime, or if the newest match does not clearly correspond to the active session, abort and tell the user the session could not be identified safely.

Do not use Claude paths such as `~/.claude/projects`.

Useful probe:

```sh
PROJECT_DIR="$PWD"
rg -l "\"cwd\":\"${PROJECT_DIR}\"" "$HOME/.codex/sessions"
```

Extract from the selected file:

- `SESSION_ID`: `session_meta.payload.session_id`
- `SHORT_ID`: first 8 characters of `SESSION_ID`
- `DATE`: local date from `current_date` in the latest matching `turn_context`, falling back to `date +%Y-%m-%d`
- `RESUME`: `codex resume SESSION_ID`

## Source Material

Use the active Codex session JSONL and the current conversation context. Prefer clean conversation events over raw tool mechanics:

- User prompts: `event_msg.payload.user_message.message`, or `response_item.payload.role == "user"` when no clean event exists.
- Assistant responses: final assistant messages and substantive summaries from `response_item.payload.role == "assistant"`.
- Ignore system/developer instructions, `turn_context`, tool calls, tool outputs, token counts, rate-limit events, patch events, and duplicate `task_complete` summaries.
- Do not print the transcript content back to the terminal.

The transcript is a readable record, not a raw log. Summarize assistant work in prose. Preserve user prompts verbatim or near-verbatim.

## Update Mode

Read `transcript.md` in `PROJECT_DIR` if it exists.

- New format: file has a `## Outline` section near the top.
- Old format: file exists but has no `## Outline` section.
- Missing: file does not exist.

Prefer incremental updates when possible.

Incremental update:

- Use this when `transcript.md` is in the new format and already contains `**Session ID:** \`SESSION_ID\``.
- In that session section, find the last `**You:**` block.
- Locate that prompt in the active session JSONL.
- Synthesize only turns after that prompt.
- Append the new turns to that existing session section, separated by `---`.
- Regenerate only that session's outline entry.
- Do not move the session section.
- If the resume point is unclear, fall back to full synthesis for that same session section.

Full update:

- Use this when no section for `SESSION_ID` exists, or when incremental matching is unsafe.
- Synthesize the session from the start of the active Codex session through the current invocation.
- Add the new session at the top of both the outline and the session sections.

## Transcript Format

Use this layout exactly for new-format files:

```md
# Session transcripts

## Outline

### YYYY-MM-DD - short-id
**Topic:** brief one-line topic
- Concrete accomplishment 1
- Concrete accomplishment 2
- Concrete accomplishment 3

---

## Session YYYY-MM-DD - short-id

**Session ID:** `full-session-id`
**Resume:** `codex resume full-session-id`

### Transcript

**You:**
> prompt 1

**Codex:**
response 1

---

**You:**
> prompt 2

**Codex:**
response 2
```

For each session outline, include:

- Topic: one brief line.
- 3-5 bullets with concrete accomplishments, decisions, or problems solved.

For each transcript turn:

- `**You:**` followed by a blockquote for the user prompt.
- `**Codex:**` followed by concise prose summarizing the response.
- Separate turns with `---`.

Exclude raw diffs, raw command output, internal reasoning, tool-call mechanics, lint noise, automatic memory writes, and slash-command parser messages.

## Existing File Behavior

Missing file:

- Create `transcript.md` from scratch with the new-format layout.

Old format:

- If existing prompts clearly match the active Codex session, replace the file with the new-format transcript for this session.
- If existing content appears to be from a different or unknown session, preserve it under `## Session unknown - imported` and add a matching outline entry, then prepend the current session above it.

New format:

- New session: prepend the new outline entry and session section.
- Existing session ID: update that section in place and refresh only its outline entry.
- Never rewrite or improve unrelated older session sections.

## Final Response

Confirm briefly with:

- session ID
- date
- whether the transcript was created, prepended, or updated in place

Do not include the transcript body in the final response.
