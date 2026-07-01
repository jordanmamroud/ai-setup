# Agent Instructions

This folder holds `skill-creator` — a skill for creating, testing, and iteratively improving other skills. Work in this folder is about improving skill-creator itself (its SKILL.md, scripts/, and viewer), not about using it to build some other skill.

## Eval mode vs. production mode

When the user gives an example prompt or scenario while discussing this skill, treat it as an eval input for skill-creator's workflow. Report what skill-creator would do next, where its instructions helped or misled, and what should change in the skill files. Do not actually build the example skill or run the full pipeline unless the user explicitly says to use skill-creator for real.

If an example exposes a workflow problem, patch skill-creator's instructions or references instead of continuing the example.

## Design decision: no automated grading (do not reintroduce it)

The upstream skill-creator had assertions, a grader agent, benchmarking with baselines, an analyst pass, and blind comparison. The user removed all of it deliberately (the pre-strip snapshot is preserved in git history). It kept misfiring: the skill invented grading criteria the user never asked for and reported meaningless pass rates. The fix chosen was removal, not gating.

What remains is the loop the user actually wants: test runs → transcript friction skim → viewer → user feedback → a proposed change plan the user OKs → apply → repeat. The user's judgment in the viewer IS the evaluation. Baseline (without-skill) runs are offered once, on the first iteration of a brand-new skill, and otherwise skipped.

When editing this skill, do not add back rubrics, assertions, pass rates, quality scores, or auto-grading in any form — and don't drift toward them under other names ("checks", "validations", "scorecards").

## Known failure modes (watch for regressions)

- **"Run another eval" misread.** "Do another evaluation" means a full new iteration (fresh runs → viewer → feedback), never re-examining existing outputs. The "What the user's words mean" section in SKILL.md encodes this — keep it.
- **Skipping the change-plan checkpoint.** The skill must present a short "here's what I plan to change and why" and get the user's OK before editing the skill under iteration. Silent edits are a regression.
- **All-or-nothing workflow testing.** Multi-step skills need one step evaluable in isolation: scoped test cases with a `scope` field and fixtures under `evals/fixtures/<scope>/`. Keep that machinery.

## User preference

Evaluation centered on the user's own judgment via the viewer. Keep changes lean and preserve the skill's conversational, explain-the-why style.
