---
name: jm-council
description: Fan one prompt out to a fixed council of frontier models (GPT-5.5, Gemini 3.1 Pro, Claude Fable 5, GLM-5.2) via OpenRouter and show the raw replies; `analyze` synthesizes where they agree and disagree.
argument-hint: <prompt> | send <prompt> | pa|pm <prompt> | analyze [prompt]
disable-model-invocation: true
---

# jm-council

Fan a single prompt out to a council of frontier models from different families. Two modes, chosen by the first word of the arguments:

- **Default** (`/jm-council <prompt>`): fan out and show each model's raw reply. No synthesis, no commentary.
- **Analyze** (`/jm-council analyze` or `/jm-council analyze <prompt>`): the Council thing — read the replies and synthesize consensus, disagreements, and a verdict.

Arguments: `$ARGUMENTS`

## Mode selection

- First word is `analyze` with nothing after it → **Analyze latest**: read the dir path from `~/.cache/jm-council/latest` and synthesize that run. Do NOT re-query the models. If the pointer file is missing or the dir is gone, say so and ask for a prompt instead.
- First word is `analyze` followed by more text → **Fan out + analyze**: treat the rest as the prompt, run the fan-out (steps 1–3 below, including the confirmation), then synthesize.
- First word is `send` → **Fan out, no confirmation**: treat the rest as the prompt and skip step 2 (the confirmation) — build the prompt and send immediately.
- First word is `pa` or `pm` → **Bake-off builder**: treat the rest as the request, but build the council prompt following the vendored methodology instead of the default rules — `references/vendor/prompt-architect/SKILL.md` for `pa`, `references/vendor/prompt-master/SKILL.md` for `pm` (paths relative to this file; read the vendored file and follow its process, loading any framework/template files it points to). The confirmation step ALWAYS applies in this mode, and must state which builder was used. See "Bake-off builder notes" below.
- Anything else → **Fan out only**: the whole argument string is the prompt.
- No arguments at all → fan out using the question currently under discussion in this session as the prompt.

## Fan-out steps

1. **Build the council prompt.** Default: read `prompt-rules.md` (same folder as this file) and follow its "Rules for building the council prompt" section. In `pa`/`pm` mode: follow the vendored methodology instead. Either way, expand the user's session shorthand into a fully self-contained prompt, and these non-negotiables override anything a builder says: the real artifact under discussion is pasted verbatim, the prompt references nothing from this session ("as discussed above" is meaningless to the council), and it never includes your own draft answer or leaning.

2. **Confirm the prompt** (skip in `send` mode; never skipped in `pa`/`pm` mode). State which builder was used (default / prompt-architect / prompt-master), show the exact prompt verbatim in a fenced code block, then STOP — do not run the script yet. Wait for explicit approval ("go", "send it", or equivalent). If the reply is an edit or correction instead, revise the prompt and show it again. Never send a prompt the user hasn't seen.

3. **Run the script:**

   ```bash
   /Users/jordanmamroud/mylab/ai-setup/skills/jm-council/council.sh "<prompt>"
   ```

   (Or pipe the prompt on stdin if it contains awkward quoting.) It queries all council members in parallel and writes `prompt.txt` plus one `<model>.md` per member to a run folder at `<repo-root>/.tmp/council/<timestamp>-<slug>/` (cwd-based when not in a git repo; exact path printed on the last line), and saves that path to `~/.cache/jm-council/latest`. Expect it to take roughly as long as the slowest model — up to a few minutes for hard prompts.

4. **Show the raw replies** (default mode). Read every `<model>.md` and present each one **verbatim** under a heading with the model's name — no summarizing, no trimming, no editorial remarks between them. If a model FAILED, read its `.err` file and report the failure under that model's heading; don't retry more than once. Close with one line noting the output dir path, and that `/jm-council analyze` will synthesize this run.

## Analyze steps

1. **Locate the run**: the dir from the fan-out just performed, or from `~/.cache/jm-council/latest`.

2. **Read** `prompt.txt` and every `<model>.md` in that dir (skim any `.err` files too).

3. **Synthesize.** Report, in this order:
   - **Consensus** — what all (or most) models agree on.
   - **Disagreements** — where they split, which model said what, and whose reasoning holds up better.
   - **Notable points** — anything only one model caught that seems important.
   - **Verdict** — your own final recommendation, using the council as input but applying your own judgment on top.

   Attribute positions to models by name. Keep the synthesis tight. If the raw replies were already shown in this session, don't repeat them; end by noting the output dir path so they can be read verbatim.

## Bake-off builder notes

`pa`/`pm` mode exists to test two third-party prompt-building methodologies head-to-head before committing to one. When following a vendored builder:

- The "target tool" is always the council: frontier chat models with zero session context, queried one-shot via API. Answer that question yourself — don't ask the user which tool they're targeting.
- Both builders like clarifying questions (prompt-architect 3–5, prompt-master up to 3). Ask them only if genuinely blocked; prefer answering from session context. The confirmation gate already gives the user a veto.
- The deliverable is the bare prompt text for `council.sh`. Ignore any builder instructions about output wrappers, target labels, emoji headers, or fillable `[PLACEHOLDER]`s — every placeholder must be resolved with real values before the confirmation step.
- To compare: run the same request as `/jm-council pa <request>` and `/jm-council pm <request>`, judge the prompts at the gate, then judge the council replies.

## Notes

- The council roster lives in the `MODELS` array at the top of `council.sh` — one line per model, OpenRouter IDs.
- `prompt-rules.md` holds both the prompt-building rules (top section, for Claude) and the system prompt sent to every council member (bottom section — `council.sh` extracts everything below its marker heading).
- `references/vendor/` holds the two vendored bake-off builders (prompt-architect by ckelsoe, prompt-master by nidhinjs, both MIT). They're test candidates, not dependencies — the default path never touches them.
- Everything goes through OpenRouter with `OPENROUTER_API_KEY`; no per-provider keys needed.
