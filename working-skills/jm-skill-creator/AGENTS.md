# Agent Instructions


This folder contains an experimental skill, not an active project that we are currently working on we are improving the skill itself.  The goal is to improve the skill itself. But we're using prompts and stuff that can make that, like, the chat kid can get confused and think we're working on the thing that's being prompted on. 

## Primary Goal

When the user gives example ad prompts while discussing this skill, treat them as workflow eval inputs unless they explicitly ask to use the skill for real production work.

The goal is to improve how `ad-brief-brainstorm` behaves with the user, not to complete the example ad.

## Eval Mode Rules

- Do not turn eval prompts into production creative work by default.
- Do not write a full ad brief unless the user explicitly asks for a real brief.
- Do not move into mockups, storyboards, scene builds, renders, or asset mining during eval.
- Report what the skill should do next, where it behaved well or poorly, and what should change in the skill.
- If the example prompt exposes a workflow problem, patch the skill instructions or references instead of continuing the ad.
- Keep the output centered on interaction behavior: what question should be asked, what options should be offered, what gate should trigger, and what the terminal artifact should be.

## Production Mode

Only treat a prompt as production work when the user clearly says to use the skill to create an actual approved ad brief.

In production mode, follow `SKILL.md` and stop at the approved brief gate.

## User Preference

The user is testing whether this skill can turn messy ad starts into a better briefing workflow. Preserve that distinction.
