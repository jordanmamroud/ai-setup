---
description: Append the current session as a new entry to transcript.md (in the current project root), with outline + transcript section. Idempotent — re-running in the same session updates rather than duplicates.
disable-model-invocation: true
---

Synthesize a transcript of the current session and add it to `transcript.md` in the current working directory (treat `$PWD` as the project root).

## Steps

1. **Resolve session ID and date.** Run:

       PROJECT_DIR="$PWD"
       ENCODED=$(echo "$PROJECT_DIR" | sed 's|/|-|g')
       SESSION_FILE=$(ls -t ~/.claude/projects/${ENCODED}/*.jsonl 2>/dev/null | head -1)
       SESSION_ID=$(basename "$SESSION_FILE" .jsonl)
       SHORT_ID="${SESSION_ID:0:8}"
       DATE=$(date +%Y-%m-%d)
       echo "PROJECT: $PROJECT_DIR"
       echo "SESSION: $SESSION_ID"
       echo "SHORT:   $SHORT_ID"
       echo "DATE:    $DATE"

   If `SESSION_FILE` is empty, abort and tell the user no session file was found at the expected path.

2. **Read** `transcript.md` (in `$PWD`) if it exists. Detect format:
   - **New format**: file has a `## Outline` section near the top.
   - **Old format**: file exists but has no `## Outline` section.
   - **Missing**: file does not exist.

3. **Decide whether to do a full or incremental synthesis.** Full synthesis is expensive (output tokens consumed = full transcript length), so prefer incremental whenever possible.

   - **Incremental** (preferred): use this when the file is in new format AND already contains a section for the current `SESSION_ID`. Steps:
     1. In the existing session's `### Transcript`, find the **last `**You:** > ...` block** — capture its text.
     2. Locate that prompt in your conversation context. Identify all turns that come AFTER it.
     3. Synthesize ONLY those new turns (using the format below).
     4. APPEND them to the end of the existing session's transcript, prefixed with a `---` separator.
     5. Regenerate the outline bullets for this session to reflect the full session including the new turns (this is cheap — a few lines).
     6. If you can't confidently locate the resume point (e.g., the last prompt isn't found in context, file looks malformed), fall back to full synthesis.

   - **Full synthesis** (fallback / first-time): use when no existing session entry for the current `SESSION_ID` exists, or when incremental can't find a resume point. Synthesize every turn from the start of the session through right now, reading from your conversation context (NOT from the existing file).

   In both cases, format each turn as:
   - `**You:**` followed by `> blockquote` (verbatim or near-verbatim) for the user prompt.
   - `**Claude:**` followed by prose paragraphs summarizing the response.
   - Separate turns with a horizontal rule (`---`).
   - **Exclude**: file edit details ("added X lines", diffs, raw tool output), tool-call mechanics, internal system messages, lint warnings, automatic memory writes, slash-command parser stdout (e.g. `/btw` usage messages).

4. **Generate outline content for this session:**
   - **Topic**: a brief one-line description of what the session was about.
   - **3–5 bullets** of concrete accomplishments. Be specific (file names, decisions made, problems solved).

5. **Update `transcript.md`.** Use this layout exactly (most recent session at top of both outline and sections):

       # Session transcripts

       ## Outline

       ### YYYY-MM-DD — short-id
       **Topic:** brief one-line topic
       - Accomplishment 1
       - Accomplishment 2
       - Accomplishment 3

       ### <older-date> — <older-short-id>
       **Topic:** ...
       - ...

       ---

       ## Session YYYY-MM-DD — short-id

       **Session ID:** `full-uuid`
       **Resume:** `claude --resume full-uuid`

       ### Transcript

       **You:**
       > prompt 1

       **Claude:**
       response 1

       ---

       **You:**
       > prompt 2

       **Claude:**
       response 2

       ---

       ## Session <older-date> — <older-short-id>
       ...

   ### Behavior

   - **Missing file**: create from scratch with header + Outline (containing only this session) + this session's section.
   - **Old format** (file exists, no Outline section): inspect the existing content.
     - **If the prompts in the existing file match prompts from the current conversation context** (i.e., it's a stale partial snapshot of this same session): treat it as discardable. Replace the whole file with the new structure. The freshly synthesized transcript covers the whole session, so nothing is lost.
     - **If the existing content is clearly from a different/earlier session** (prompts don't match the current conversation): preserve it. Wrap it under a placeholder section header `## Session unknown — imported` (with a corresponding Outline entry noting it was imported and the session ID is unknown). Then prepend the current session's entry on top.
   - **New format**: prepend the new session's outline entry (above all existing outline entries) AND prepend the new session's section (above all existing sections).
   - **Existing entries are never edited** when adding a new session — only prepend. Don't "improve" old summaries.
   - **Dedupe by session ID**: if a section with the current `SESSION_ID` already exists in the file:
     - Use **incremental synthesis** (see step 3) to append only new turns to the existing transcript section.
     - Regenerate the outline bullets for this session to reflect the full session.
     - The session's position in the file does NOT move — it stays where it is. (It's already at the top from when it was first added; subsequent runs just extend it in place.)

6. **Confirm briefly.** State the session ID, date, and a one-line note about what changed (added new / replaced existing). Do NOT print the transcript content back to the terminal.
