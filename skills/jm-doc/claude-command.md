---
name: jm-doc
description: One doc skill, four modes — checkpoint (session notes), spec (versioned spec interview), readme (root README), arc (ARCHITECTURE.md). `/jm-doc <mode>` runs a mode directly; bare `/jm-doc` assesses the project and proposes a mode.
disable-model-invocation: true
---

# jm-doc

Router for the project-documentation modes. Mode instructions live in this skill's `references/` folder:

`/Users/jordanmamroud/mylab/ai-setup/skills/jm-doc/references/`

- `checkpoint.md` — capture the session's in-flight substance into `overview/notes.md`
- `spec.md` — guided interview producing versioned `spec-v0.md` / `spec-v1.md`
- `readme.md` — create or refresh the root `README.md`
- `arc.md` — create or refresh the root `ARCHITECTURE.md`

## Routing

Look at the first word of `$ARGUMENTS`:

- `checkpoint` → read `references/checkpoint.md` and follow it.
- `spec` → read `references/spec.md` and follow it. Everything after the word `spec` is the brain-dump argument.
- `readme` → read `references/readme.md` and follow it.
- `arc` (also accept `architecture`) → read `references/arc.md` and follow it.
- Anything else → say the mode isn't recognized, list the four modes with one-line purposes, and stop.

Read only the one reference file for the chosen mode — never load the others.

## Bare invocation (`/jm-doc` with no arguments)

Assess the project, then **propose a mode and wait for confirmation — never run a mode unasked**.

Check, in order:

1. **Checkpoint bias.** If the current session contains uncommitted substance — decisions made, ideas surfaced, threads opened or closed — checkpoint is the default proposal. When in doubt, propose checkpoint.
2. If the session is clearly about designing something new and no `spec-v0.md` exists → propose spec.
3. If the repo has real code but no root `README.md` → propose readme.
4. If the repo has no `ARCHITECTURE.md` (or the session made structural changes that make it stale) → propose arc.

Propose exactly one mode with a one-line reason, and list the runners-up in one line each (e.g. "also plausible: readme — this repo has no README"). On confirmation, read that mode's reference file and follow it.

## Notes

- Each mode's reference file defines its own scope and safety rules; those rules win over anything here.
- Under Codex this skill is installed at `~/.codex/skills/jm-doc/` — same references, same routing.
