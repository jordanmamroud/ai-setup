# jm-doc spec

Maintains a standardized, versioned `spec.md` in any project. Each version (`spec-v0.md`, `spec-v1.md`, ...) is its own file. The skill produces a fully filled-in spec via a guided interview — never a placeholder template. The output should match the quality bar of the gold-standard example included at the bottom of this file.

## What it does

**Triggers:** the user runs `/jm-doc spec` (optionally with a brain-dump argument: `/jm-doc spec <text>`).

State-driven. On invocation, check the current working directory for the existence of `spec-v0.md` and `spec-v1.md`:

| Disk state | Action |
|---|---|
| Neither file exists | Run **V0 flow** → write `spec-v0.md` |
| `spec-v0.md` only | Run **V1 flow** (diff-from-V0) → write `spec-v1.md` |
| Both files exist | Report state. Open `spec-v1.md`. No-op. |
| `spec-v1.md` only (unusual) | Report state. Open `spec-v1.md`. No-op. |

**Never overwrite** an existing spec file. If the file the skill would create already exists, report state and stop.

No version arguments. The skill is purely state-driven.

---

## Interview format (applies to all questions in V0 and V1 flows)

Every question asked during the interview phases must follow this format exactly:

```
**Q:** <the question>

A) <approach 1> — <one-line tradeoff>
B) <approach 2> — <one-line tradeoff>
C) <approach 3> — <one-line tradeoff>

**Recommendation: <letter>**, because <reason>.
```

Rules:
- **One question at a time.** Wait for the user's reply before asking the next.
- **A, B, C** (sometimes D) format. The user replies with a single letter.
- **Always recommend one option.** Put the reason inline so the tradeoff is visible at a glance.
- **Free-form override always allowed.** If the user types prose instead of a letter, treat that as their answer.
- If a question genuinely has no good options to propose (it's purely "tell me X"), ask it openly — but prefer the A/B/C format whenever there's a choice to be made.

---

## V0 flow

### Phase 0 — Brain dump intake

If the user invoked `/jm-doc spec <text>`, that text is the brain dump. Skip to Phase 1.

If the user invoked `/jm-doc spec` with no argument, ask:

> Paste your brain dump of what you want to build — voice-to-text is fine, multi-line is fine. When you're done, just send.

Wait for their reply. That reply is the brain dump.

### Phase 1 — Understanding playback

Read the brain dump carefully. Then play back your understanding **in plain prose** (no headings, no bullets — just 2–4 short paragraphs). Cover:
- What is being built and the core problem it solves.
- Who uses it and how (at a high level).
- Any constraints, opinions, or non-goals you picked up.

End with: "Did I get this right? Correct anything that's off, or say 'looks good' and I'll move on."

If the user corrects you, integrate the correction and play it back again. Loop until they're satisfied.

### Phase 2 — Adaptive interview with checkpoint

Once the understanding is locked, tell the user (briefly) which sections of the spec the brain dump already covers and which sections you'll need to ask about. Format:

> The dump covers: <comma-separated list of sections, e.g. "the core problem, rough user flow, stack preference">.
>
> I'll ask you about: <comma-separated list, e.g. "the v0 success criterion, scope discipline (must-do/must-not-do), definition of done, v1 parking lot">.
>
> Want me to also revisit anything from the first list, or anything not on either list? Otherwise I'll start asking.

Wait for the user. If they add topics, fold them into your question plan.

Then run the interview, **one question at a time**, in the **Interview format** above. Use the **V0 question bank** below as your starting point. Skip questions whose answers are already obvious from the brain dump or earlier answers. Add follow-up questions when an answer raises a new ambiguity.

Sections to cover (in order):
1. **Overview** — V0 success criterion, DO discipline, DO NOT discipline.
2. **User flow** — fill in any steps the brain dump skipped.
3. **Technical details** — stack, storage, entry point, file structure, data shape.
4. **Scope** — must-do, must-not-do.
5. **Definition of done** — verifiable items.
6. **Notes for next version** — parking-lot ideas.

### Phase 3 — Draft and write

When all sections have enough information, draft the full `spec-v0.md` matching the structure and quality of the gold-standard example below. Write it to `./spec-v0.md` (project root). Then report:

> Wrote `spec-v0.md`. Open it in your editor and tweak anything that's off — that's faster than iterating in chat.

**Do not** offer to walk through it section by section in chat. **Do not** show the spec inline before writing. Write to disk, point the user to it, stop.

---

## V0 question bank (Phase 2 starter)

Use these as the seed for V0 questions. Phrase them in the **Interview format** with A/B/C options and a recommendation tailored to the brain dump's specifics. Skip any whose answer is already clear.

**§1 Overview — Current version block**
- What's the v0 success criterion? (One sentence — what end-to-end thing must work for v0 to be "done.")
- DO: what's the code-quality bar for v0? (e.g. "structured and readable but not production-hardened" vs. "throwaway prototype" vs. "production-ready from day one")
- DO NOT: what tempting features should v0 explicitly refuse?

**§2 User flow**
- How does the user start the app? (CLI script, double-click, web URL, etc.)
- Walk through the first session step by step — what does the user see and do?
- What persists across sessions, and what resets?

**§3 Technical details**
- Stack — language, framework, build tool?
- Where does state live? (DB, localStorage, JSON files, in-memory)
- Entry point — what command launches it?
- File structure — any opinions about layout, or let the implementer choose?
- Core data shape — what's the central object/schema? (Often best as a JSON example.)
- Any external services / models / APIs involved? How are they invoked?

**§4 Scope**
- Beyond what's already in the user flow, what else must v0 do?
- What tempting features should v0 explicitly NOT do? (Often these are things from your brain dump that should be deferred.)

**§5 Definition of done**
- For each must-do item, what's the manual test that proves it works?
- (The standard: each DoD item must be independently verifiable by a human in 30 seconds.)

**§6 Notes for next version**
- What ideas came up during this conversation (or in the dump) that you want to defer?
- Any obvious next-step features that aren't v0 scope?

---

## V1 flow

Triggered when `spec-v0.md` exists and `spec-v1.md` does not.

### Phase 0 — Read V0

Read `./spec-v0.md` in full before doing anything else. You need it to anchor every subsequent question.

### Phase 1 — Brain dump intake (optional for V1)

If the user invoked `/jm-doc spec <text>`, that text is the V1 brain dump. Skip to Phase 2.

Otherwise ask:

> V0 spec exists. For V1, what's the brain dump? (Could be: what shipped, what didn't, what you want to change, what's new on your mind. Or paste a fresh transcription. Or just say "no dump" and I'll lead with questions.)

### Phase 2 — Understanding playback (V0→V1 delta)

Play back, in prose, your understanding of:
- What V0 was meant to be (from `spec-v0.md`).
- What seems to have shipped vs. not (from the brain dump or, if no dump, leave this open and ask).
- What appears to be changing in V1 (new scope, deprecated scope, evolved goals).
- Which "Notes for next version" items from V0 look like graduation candidates.

End with: "Did I get the V0→V1 picture right? Correct anything, or say 'looks good'."

Loop until the user is satisfied.

### Phase 3 — Adaptive interview with checkpoint

Tell the user which V1 topics you'll ask about (centered on the diff, not the full V0 spec restated). Same checkpoint pattern as V0 Phase 2. Then run the interview one question at a time, A/B/C format.

Use the **V1 question bank** below.

### Phase 4 — Draft and write

Draft a full `spec-v1.md` with the same 6-section structure as V0. The V1 spec is **written fresh** (not a copy-and-edit of V0), but it's **informed by V0** — it should reference what shipped, what was deferred, and what's now in scope. Write to `./spec-v1.md`. Report:

> Wrote `spec-v1.md`. Open it and refine.

`spec-v0.md` stays on disk untouched as the historical record.

---

## V1 question bank (Phase 3 starter)

**Diff from V0**
- What from V0's "Definition of done" actually shipped? Anything that didn't?
- What from V0's "Must do" or "Must not do" lists has changed your mind?
- What in the V0 user flow turned out wrong or insufficient?

**Graduating parking-lot items**
- For each item in V0's "Notes for next version" — does it graduate to V1 scope, stay parked, or get killed?
- (Walk through them one by one if there are <8; batch into a single A/B/C question if there are more.)

**New scope**
- What's the V1 success criterion? (One sentence.)
- New DO discipline, new DO NOT discipline?
- New user flow steps, or modifications to existing ones?
- New technical decisions (stack changes, storage migrations, new dependencies)?
- New definition-of-done items?
- New parking lot for V2?

---

## Spec quality bar (applies to both V0 and V1 drafts)

Every spec the skill writes must hit these properties:

- **6 sections in this exact order:** Overview, User flow, Technical details, Scope, Definition of done, Notes for next version.
- **Title format:** `# <Project Name> — Spec` where `<Project Name>` is derived from the project root folder name (basename, title-cased with spaces). Example: folder `task-with-memory` → "Task With Memory — Spec".
- **§1 Overview** opens with one paragraph explaining the problem and intent. Then a `**Current version: vN**` block with bulleted `Goal:`, `DO:`, `DO NOT:` lines, and an optional pinned reminder about scope discipline.
- **§2 User flow** is a numbered list of concrete user actions and system responses. Cover the happy path end-to-end. Reference exact UI elements and file/script names where relevant.
- **§3 Technical details** is bulleted, with bold sub-labels (`**Stack:**`, `**Storage:**`, etc.). Include code/JSON blocks for data shapes and prompt assemblies. Be concrete — names of files, names of endpoints, names of functions.
- **§4 Scope** has two sub-blocks: `**Must do**` and `**Must not do**`, each as a bulleted list. The "must not" list is as important as the "must" list.
- **§5 Definition of done** opens with: "Each item must be independently verifiable by manual testing." Then a checkbox list (`- [ ]`). Each item must be testable by a human in under a minute, no automation required.
- **§6 Notes for next version** opens with: "**DO NOT BUILD ANY OF THIS NOW.** This section is a parking lot for ideas that came up during v\<N\> design. They are out of scope until v\<N\> is working and a refactor pass has been done." Then a bulleted list of `**Idea name.** Description.`

Separate sections with `---` horizontal rules. Use `##` for section headings (numbered: `## 1. Overview`, etc.).

---

## Behavior summary

- **Never write to disk during the interview.** Only Phase 3 (V0) / Phase 4 (V1) writes the spec.
- **Never overwrite.** If `spec-vN.md` exists when you'd write it, stop and report.
- **One question at a time.** A/B/C format with tradeoffs and a recommendation. Free-form override allowed.
- **Don't iterate the spec in chat after writing.** Tell the user to edit in their editor.
- **Self-contained.** This reference file is the only file this mode needs.

---

## Reference: gold-standard example

Below is the spec the skill should aim to match in shape, density, and quality. It is a **reference**, not a template — do not copy phrasing or content. Match the structural rigor and the level of concreteness.

````markdown
# Task With Memory — Spec

## 1. Overview

Recurring LLM tasks keep making the same mistakes. This tool lets the user correct outputs once and have the model automatically learn from those corrections on every future run — no fine-tuning, no manually editing prompts.

**Current version: v0**
- Goal: end-to-end loop works — create a task, run it, give feedback, future runs improve.
- DO: structure code sensibly. Separated concerns. Readable. Navigable.
- DO NOT: add scaling features, retrieval, vector DB, tests, or production hardening.
- Refactor is a later phase, not a license for sloppy code.

---

## 2. User flow

1. User runs `./start.sh` (or equivalent launcher). It starts a local server and opens the app in the browser.
2. If no tasks exist, user sees a "create new task" form.
3. User creates a task by providing:
   - Name (free text).
   - Instructions (plain English: what should the model do).
   - Output type: pick from a list of categories, OR free-form text.
   - If categories: the list (one per line).
   - CLI to use: Claude, Gemini, or Codex.
4. Task appears as a tab in the top navigation. User can have multiple tasks, switch between them, create more (+ New task tab), or delete a task.
5. With a task selected, user enters an input and clicks Run.
6. Frontend posts the prompt + chosen CLI to the local server. Server spawns the CLI subprocess in headless/non-interactive mode, pipes the prompt in, captures stdout, returns it. Frontend displays the model's output.
7. User gives feedback:
   - **Category task:** Mark Correct, or pick the correct category from a dropdown and provide a one-sentence reason → save correction.
   - **Free-text task:** Mark as Good (optionally add why it works), or Reject (provide a reason, optionally a better version) → save.
8. Feedback persists. Next run of the same task includes all stored feedback in the prompt automatically.
9. User can inspect the task's stored examples and the exact prompt that was last sent to the model (collapsible sections).
10. User can reset a task's memory or delete the task entirely.

---

## 3. Technical details

- **Stack:** React + TypeScript frontend, built with Vite. A small local Node.js server (TypeScript, run via `tsx`) handles CLI subprocess calls.
- **Storage:** JSON, persisted in `localStorage` under a single key (e.g. `task_with_memory_v0`). Entire app state lives in that one JSON blob.
- **Model access:** the local server spawns a headless CLI subprocess to call the model. No hosted API calls, no API keys.
- **Entry point:** a `start.sh` that launches the Node server (via `npm run server`) in the background and the Vite dev server in the foreground.
- **File structure:**
  - `server.ts` — the local server.
  - `vite.config.ts` — Vite config.
  - `src/App.tsx` — top-level component.
  - `src/state/` — task storage, prompt assembly, `/run` calls, feedback handling.
  - `src/components/` — UI components.
  - `start.sh` — launcher.
- **Data shape:**
  ```json
  {
    "tasks": [
      {
        "id": "t_<timestamp>_<rand>",
        "name": "string",
        "instructions": "string",
        "outputType": "categories" | "freetext",
        "categories": ["string", ...] | null,
        "cli": "claude" | "gemini" | "codex",
        "examples": [...],
        "lastPrompt": "string"
      }
    ]
  }
  ```

---

## 4. Scope

**Must do**
- Run entirely locally. No hosted services.
- Use locally-installed CLI subscriptions for all model calls.
- Persist all state across browser reloads.
- Support unlimited user-defined tasks, each isolated.
- Always inject all stored feedback into every future run.

**Must not do**
- No hosted API calls. No API keys.
- No authentication or multi-user features.
- No retrieval, embeddings, or "smart" example selection.
- No automatic lesson generation via a second LLM call.
- No tests, CI, or eval harness.
- No real database. JSON in localStorage only.

---

## 5. Definition of done

Each item must be independently verifiable by manual testing.

- [ ] `./start.sh` launches the local server and opens the browser.
- [ ] On first load, the "create new task" form is shown.
- [ ] User can create a category-type task and see it appear as a tab.
- [ ] User can run a task on an input; CLI is invoked headlessly and stdout is displayed.
- [ ] User can submit a correction; the example is stored.
- [ ] After saving a correction, re-running the same input produces a different answer.
- [ ] Reloading the browser preserves all tasks and examples.
- [ ] One task's examples do not leak into another task's prompt.

---

## 6. Notes for next version

**DO NOT BUILD ANY OF THIS NOW.** This section is a parking lot for ideas that came up during v0 design. They are out of scope until v0 is working and a refactor pass has been done.

- **Retrieval.** Once a task has ~50+ examples, sending all of them in every prompt becomes wasteful. Add embeddings + a small local vector store.
- **Auto-generated lessons.** Optional second CLI call after a correction asks the model to introspect.
- **Confidence-based routing.** If a task emits low confidence, surface it for the user to label.
- **Eval harness.** Use stored corrections as a labeled test set.
- **Editing existing tasks.** v0 only supports create/delete. v1 could allow editing without losing memory.
- **Export / import.** Let the user download tasks + memory as JSON.
````
