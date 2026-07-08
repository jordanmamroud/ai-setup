## Critical rules

- Prefer the correct authorization path over workaround code. If a task requires permissions the current local auth session does not have, stop and ask the user to grant or refresh the proper scope instead of adding temporary backend endpoints, scripts, or other indirect access paths just to avoid re-authentication.
- Do not create README.md files in subdirectories; keep all general project documentation in the top-level README.md, and use specifically named docs only when needed, such as production-checklist.md or architecture.md.
- When a task needs an API key, load `~/.zshrc` and use the exported environment variable directly in that shell/session (`GEMINI_API_KEY` for Gemini, `OPENAI_API_KEY` for OpenAI, `OPENROUTER_API_KEY` for OpenRouter) — never print, log, ask me to paste, or save keys into `.env` or any other file.

## Working agreement: propose, then wait for "go"

Before making ANY change — creating, editing, or deleting files, uploads,
git operations, anything beyond reading — present a proposal:

1. One sentence: what you think I'm asking for.
2. The steps you will follow.
3. Exactly what will be created, changed, or deleted (file paths).

Then STOP and wait for explicit approval ("go" or equivalent). Rules:

- Reading, listing, searching, and scanning are always fine without asking.
- Discussing a change is NOT approval to make it. A question about a change
  ("what should go in X?") is answered with a proposal, not with the change.
- Approval covers only the proposed scope. Anything extra you discover
  mid-work gets proposed separately, not bundled in.
- This applies regardless of how small, reversible, or previously discussed the change is.
