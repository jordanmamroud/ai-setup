#!/usr/bin/env bash
# Stop hook: prettier + eslint over all changed/untracked .ts/.tsx/.js/.jsx,
# plus whole-project tsc, plus vitest --changed if vitest is installed.
# Reads Claude Code stop hook JSON from stdin. Exits 0 on pass, 2 on fail.
set -uo pipefail

INPUT=$(cat)
ACTIVE=$(printf '%s' "$INPUT" | jq -r '.stop_hook_active // false')
[[ "$ACTIVE" == "true" ]] && exit 0

# Include untracked files — agents often create new files; git diff alone misses them.
CHANGED=$({ git diff --name-only HEAD; git ls-files --others --exclude-standard; } \
  | sort -u | grep -E '\.(ts|tsx|js|jsx)$' || true)

[[ -z "$CHANGED" ]] && exit 0

RUN="npx --no-install"

TSC=("tsc" "--noEmit" "--incremental")
if [[ -f tsconfig.json ]] && jq -e '.references' tsconfig.json >/dev/null 2>&1; then
  TSC=("tsc" "-b")
fi

OUT=""
add_fail() { OUT+="--- $1 ---"$'\n'"$2"$'\n'; }

if ! P_OUT=$(printf '%s\n' "$CHANGED" | tr '\n' '\0' | xargs -0 $RUN prettier --check 2>&1); then
  add_fail "prettier" "$P_OUT"
fi

if ! E_OUT=$(printf '%s\n' "$CHANGED" | tr '\n' '\0' | xargs -0 $RUN eslint 2>&1); then
  add_fail "eslint" "$E_OUT"
fi

if ! T_OUT=$($RUN "${TSC[@]}" 2>&1); then
  T_FILTERED=$(printf '%s' "$T_OUT" | grep -E 'error TS[0-9]+' | head -c 2000)
  add_fail "tsc" "$T_FILTERED"
fi

if [[ -f package.json ]] && jq -e '.devDependencies.vitest // .dependencies.vitest' package.json >/dev/null 2>&1; then
  if ! V_OUT=$($RUN vitest run --changed 2>&1); then
    add_fail "vitest" "$V_OUT"
  fi
fi

if [[ -n "$OUT" ]]; then
  printf '%s' "$OUT" | head -c 2000 >&2
  exit 2
fi
exit 0
