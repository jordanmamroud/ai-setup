# Agent Instructions

This folder holds `skill-creator` — a skill for creating, testing, and iteratively improving other skills. Work in this folder is about improving skill-creator itself (its SKILL.md, agents/, scripts/, and viewer), not about using it to build some other skill.

## Eval mode vs. production mode

When the user gives an example prompt or scenario while discussing this skill, treat it as an eval input for skill-creator's workflow. Report what skill-creator would do next, where its instructions helped or misled, and what should change in the skill files. Do not actually build the example skill or run the full pipeline unless the user explicitly says to use skill-creator for real.

If an example exposes a workflow problem, patch skill-creator's instructions or references instead of continuing the example.

## Known failure modes being fixed (watch for regressions)

These are the behaviors the user has been burned by. The skill files now contain countermeasures — when editing, preserve them:

- **Invented grading criteria.** The skill used to draft assertions on its own and grade against them, producing pass rates on criteria the user never asked for. Countermeasure: judging criteria come from the user (`evals/criteria.md`), assertions must trace to them and be approved before any grading, and grading is skipped entirely when no approved assertions exist.
- **"Run another eval" misread as re-grading.** The skill used to respond to "do another evaluation" by re-running rubric checks on existing outputs. Countermeasure: the "What the user's words mean" section in SKILL.md maps that phrasing to a full new iteration (fresh runs → viewer → feedback). Never satisfy it with grading alone.
- **All-or-nothing workflow testing.** Multi-step skills couldn't have one step evaluated in isolation. Countermeasure: scoped test cases with a `scope` field and fixtures under `evals/fixtures/<scope>/`.

## User preference

The user wants evaluation centered on their own judgment via the viewer, with quantitative grading as an opt-in supplement — not a wall of auto-generated checks. Keep changes lean and preserve the skill's conversational, explain-the-why style.
