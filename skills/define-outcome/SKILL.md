---
name: define-outcome
description: >-
  Lightweight alignment check for the middle of a working session with an agent:
  turns a fuzzy ask into a crisp, outcome-angle definition of done — described
  from the perspective of whoever lives with the result (what they'll be able to
  do, what it'll feel like, what's true after), not implementation steps. Reach
  for this DURING the back-and-forth — right before handing the agent the next
  task, or when a thread has been drifting and you suspect you and the agent are
  picturing different end states. Triggers on things like "wait, let me be clear
  about what I actually want here," "I don't think we're building the same
  thing," "before you do that — what's the actual outcome," "help me pin down
  what done looks like for this." Ends with a short verbal read-back, and on
  request a paste-ready outcome definition that pairs well with the /goal
  command. This is the LIGHT alternative to a full brainstorming / planning /
  spec process — a few sharp exchanges, not a giant plan doc. Don't use it for
  detailed step-by-step implementation planning, or when the outcome is already
  clearly defined and you're just executing.
---

# Define Outcome

## Why this exists

This is for the middle of a working session, not the start of a project. You're
already going back and forth with the agent, and the expensive failure isn't a
bad plan up front — it's that somewhere in the thread you and the agent quietly
drifted into picturing two different end states. The agent confidently builds
the thing it imagined, you meant something else, and you find out twenty minutes
and three tool calls later.

This skill removes that failure mode cheaply. It is **not** a planning phase, a
spec doc, or a requirements interview. It's a quick gut-check you run before
handing over the next task — or the moment a thread starts feeling off: surface
what the user actually wants out of this next move, agree on what *done* looks
and feels like, name what's explicitly not the point — then get back to working
through it together.

Keep the whole thing to a few exchanges. If it starts feeling like a process,
you've overshot — the point is to get unstuck and back to the work, not to pause
it for ceremony.

## The stance: talk, don't interrogate

Work the way you'd talk it through with a sharp colleague at a whiteboard — not
the way you'd fill out a form.

- **Infer aggressively, ask sparingly.** Most of what you need is already in what
  they said or in the surrounding context. Reflect your best understanding back
  and let them correct it. A good read-back they tweak beats five questions they
  have to answer.
- **One or two sharp questions at a time, max.** If you're tempted to ask a
  list, you're treating this like requirements gathering. Pick the single
  question whose answer would most change what you build, and ask only that.
- **Stay at outcome altitude.** The moment you're discussing databases, file
  structures, or step ordering, you've dropped too low — this skill is done and
  the real work has started. Pull back up: "what does this *do for you*," not
  "how do we build it."

## What you're drawing out

You're after a definition of *done* described from the outside — from the
perspective of whoever lives with the result (often an end user, sometimes the
user themselves). Not "the code compiles," but "what's now true in the world."

These are facets, not a checklist to march through. Cover the ones that matter
for this particular thing; skip what's obvious. Usually two or three are enough:

- **The problem.** What's annoying, broken, or missing right now — the reason
  this is worth doing at all. If you can't name the problem, you don't yet know
  what done means.
- **What done looks like.** The concrete observable state when it works.
  Described as an outcome ("you can reschedule a job in two taps without leaving
  the calendar"), not a task list.
- **What it'll feel like.** The experience from the inside. Faster? Calmer? One
  less thing to babysit? This is what makes "done" recognizable when you get
  there.
- **What's now possible / true after.** What this unlocks or settles. What you
  stop worrying about, or what you can finally do next.
- **What's explicitly NOT the point.** The single most useful drift-preventer.
  Naming what you're *not* chasing keeps the work from quietly sprawling. ("Not
  trying to redesign the whole dashboard — just this one flow.")

## End with a read-back

Once it's clear, mirror it back in a few tight lines and ask if it's right.
Short and outcome-shaped — not a document:

```
Okay, here's what I think we're actually doing:

• Problem: scheduling a callback takes too many clicks and people drop off
• Done = a customer can book a callback in under 30 seconds, on mobile, without signing in
• Feels like: effortless — no form fatigue, no dead ends
• Not chasing: account creation, payments, or desktop polish right now

That match what's in your head? Then let's get into it.
```

If they confirm, you're done — start the actual work. If they correct you, fold
it in and move on. Don't ceremonially re-read-back three times; one good mirror
and a tweak is plenty.

## The optional brief (only when asked)

Default footprint is the verbal read-back above — nothing written. Only if the
user asks to "write it down" / "save this" / "give me the brief," produce a clean
outcome definition they can paste straight into the `/goal` command. Keep it
outcome-shaped and free of implementation detail, since `/goal` will handle the
how:

```
## Outcome

**Problem:** <what's broken or missing today, and who feels it>

**Done looks like:** <the concrete observable end state, from the user's POV>

**Experience:** <what it feels like to use / live with once it works>

**True after:** <what's now unlocked, settled, or no longer a worry>

**Not in scope:** <what we're deliberately not chasing in this pass>
```

This skill produces the *what* and *why*. `/goal` and the work itself produce the
*how* — don't blur the line by sneaking steps or tech choices into the brief.

## Stay light — what this is not

If you catch yourself doing any of these, stop and pull back up:

- Writing a spec, a plan, or a numbered step list
- Asking a long battery of questions before saying anything yourself
- Debating implementation (tools, schemas, architecture, sequencing)
- Treating the read-back as a contract to review and re-review
- Turning a five-minute alignment into a planning meeting

The win condition is simple: in a few exchanges, you and the user can both say
the same sentence about what you're making and why — and then you go make it.
