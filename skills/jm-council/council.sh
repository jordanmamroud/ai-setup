#!/usr/bin/env bash
# council.sh — fan one prompt out to a fixed council of models via OpenRouter, in parallel.
#
# Usage: council.sh "<prompt>"    (or pipe the prompt on stdin)
#
# Writes prompt.txt plus one <model>.md reply per council member into a fresh
# run folder at <repo-root>/.tmp/council/<timestamp>-<slug>/ (cwd-based when
# not in a git repo), and prints per-model status followed by the dir path on
# the last line. Failures land in <model>.err instead. The system prompt is
# extracted from the bottom section of prompt-rules.md. Requires
# OPENROUTER_API_KEY in the environment (falls back to sourcing ~/.zshrc).
#
# The run dir path is also saved to ~/.cache/jm-council/latest so
# `/jm-council analyze` can find the most recent run.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
# The system prompt sent to every council member lives at the bottom of
# prompt-rules.md, below the marker heading; everything above it is
# prompt-building rules for Claude and is NOT sent to the models.
BASE_PROMPT_FILE="${SCRIPT_DIR}/prompt-rules.md"
BASE_PROMPT_MARKER="## System prompt sent to every council member"

# The council. Edit this list to change who gets asked.
MODELS=(
  openai/gpt-5.5
  google/gemini-3.1-pro-preview
  anthropic/claude-fable-5
  z-ai/glm-5.2
)

prompt="${1:-}"
if [ -z "$prompt" ] && [ ! -t 0 ]; then
  prompt="$(cat)"
fi
if [ -z "$prompt" ]; then
  echo "usage: council.sh \"<prompt>\"  (or pipe the prompt on stdin)" >&2
  exit 1
fi

if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  OPENROUTER_API_KEY="$(zsh -c 'source ~/.zshrc >/dev/null 2>&1; printf %s "${OPENROUTER_API_KEY:-}"')"
fi
if [ -z "$OPENROUTER_API_KEY" ]; then
  echo "error: OPENROUTER_API_KEY not set (checked environment and ~/.zshrc)" >&2
  exit 1
fi
export OPENROUTER_API_KEY

root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
slug="$(printf '%s' "$prompt" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | cut -c1-40 | sed 's/^-//; s/-$//')"
outdir="${root}/.tmp/council/$(date +%Y-%m-%d-%H%M%S)${slug:+-$slug}"
mkdir -p "$outdir"
printf '%s' "$prompt" > "$outdir/prompt.txt"
mkdir -p "${HOME}/.cache/jm-council"
printf '%s' "$outdir" > "${HOME}/.cache/jm-council/latest"

ask() {
  local model="$1" out="$2"
  python3 - "$model" "$outdir/prompt.txt" "$BASE_PROMPT_FILE" "$BASE_PROMPT_MARKER" > "$out" 2> "${out%.md}.err" <<'PY'
import json, os, sys, urllib.request

model, prompt_file, base_file, marker = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
with open(prompt_file) as f:
    prompt = f.read()

messages = []
try:
    with open(base_file) as f:
        raw = f.read()
    # Only the part below the marker heading is the system prompt; the rest of
    # the file is prompt-building guidance for Claude, not for the council.
    idx = raw.rfind(marker)
    base = raw[idx + len(marker):].strip() if idx != -1 else ""
    if base:
        messages.append({"role": "system", "content": base})
except OSError:
    pass  # missing rules file degrades to a plain user message

messages.append({"role": "user", "content": prompt})

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/chat/completions",
    data=json.dumps({
        "model": model,
        "messages": messages,
    }).encode(),
    headers={
        "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
        "Content-Type": "application/json",
    },
)
with urllib.request.urlopen(req, timeout=600) as r:
    body = json.load(r)

if "error" in body:
    sys.exit(f"API error: {body['error']}")
print(body["choices"][0]["message"]["content"])
PY
}

pids=()
for model in "${MODELS[@]}"; do
  ask "$model" "$outdir/${model//\//_}.md" &
  pids+=($!)
done
for pid in "${pids[@]}"; do
  wait "$pid" || true
done

for model in "${MODELS[@]}"; do
  out="$outdir/${model//\//_}.md"
  if [ -s "$out" ]; then
    echo "ok:     $model -> $out"
    rm -f "${out%.md}.err"
  else
    echo "FAILED: $model (see ${out%.md}.err)"
  fi
done
echo "$outdir"
