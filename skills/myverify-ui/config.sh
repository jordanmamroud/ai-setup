# Configuration for ui-verify (the bash bridge in this folder).
#
# This file is sourced by ./ui-verify on every run. Anything you set here
# overrides the script's built-in defaults. Anything set as a UI_VERIFY_*
# environment variable when ui-verify is invoked overrides whatever you set
# here.
#
# Precedence: script defaults < this file < UI_VERIFY_* env vars.
#
# Out of the box this file overrides nothing — the defaults in the script are
# already correct (prompt is a sibling, allowlist matches the verifier's needs,
# model is sonnet). Uncomment any line below if you want to change a value
# without editing the script.

# Path to the verifier's system prompt. Default: ./system-prompt.md (a sibling
# of the script, resolved via $SCRIPT_DIR which itself follows symlinks).
# PROMPT_FILE="$SCRIPT_DIR/system-prompt.md"

# Tools the spawned `claude -p` subprocess is allowed to use. Space-separated.
# The wildcard `mcp__playwright__*` allows all Playwright MCP tools.
# ALLOWED_TOOLS="Bash Read Write mcp__playwright__*"

# Model passed to `claude -p`. Use an alias (sonnet, opus, haiku) or a full
# model ID like claude-sonnet-4-6.
# MODEL="sonnet"

# Path to the MCP config file declaring servers exposed to the verifier
# subprocess (default: ./mcp.json — a sibling of the script). Bridge silently
# skips --mcp-config if this file is missing, so the verifier loses Playwright
# and falls back to scripted Bash. Override via UI_VERIFY_MCP_CONFIG env var
# for a one-shot run.
# MCP_CONFIG_FILE="$SCRIPT_DIR/mcp.json"

# Directory where per-run history is written. Layout:
#   $HISTORY_DIR/runs.jsonl              ← one JSON object per run (analytics)
#   $HISTORY_DIR/runs/<run_id>/brief.md  ← the brief sent to the verifier
#   $HISTORY_DIR/runs/<run_id>/response.md ← the verifier's full markdown report
#   $HISTORY_DIR/runs/<run_id>/meta.json ← the JSONL row, pretty-printed
# Default: ~/.local/share/ui-verify
# HISTORY_DIR="$HOME/.local/share/ui-verify"

# Free-form tag attached to this run's metadata as a `notes` field. Useful
# when running an experiment so you can later filter by it:
#   jq 'select(.notes | startswith("haiku trial"))' ~/.local/share/ui-verify/runs.jsonl
# Usually set per-invocation as an env var, not here:
#   UI_VERIFY_NOTES="haiku trial 2" ui-verify <url> "<brief>"
# NOTES=""
