#!/usr/bin/env bash
# PostToolUse hook: prettier + eslint on the edited file, plus whole-project tsc.
# Reads Claude Code tool JSON from stdin. Exits 0 on pass, 2 on fail.
set -uo pipefail

INPUT=$(cat)
FILE=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')

[[ -z "$FILE" ]] && exit 0
case "$FILE" in
  *.ts|*.tsx|*.js|*.jsx) ;;
  *) exit 0 ;;
esac

RUN="npx --no-install"

# tsc -b for projects with TS references, otherwise tsc --noEmit --incremental.
# Never pass the file as an arg — that bypasses tsconfig and runs non-strict.
TSC=("tsc" "--noEmit" "--incremental")
if [[ -f tsconfig.json ]] && jq -e '.references' tsconfig.json >/dev/null 2>&1; then
  TSC=("tsc" "-b")
fi

OUT=""
add_fail() { OUT+="--- $1 ---"$'\n'"$2"$'\n'; }

if ! P_OUT=$($RUN prettier --check "$FILE" 2>&1); then
  add_fail "prettier" "$P_OUT"
fi

if ! E_OUT=$($RUN eslint "$FILE" 2>&1); then
  add_fail "eslint" "$E_OUT"
fi

if ! T_OUT=$($RUN "${TSC[@]}" 2>&1); then
  T_FILTERED=$(printf '%s' "$T_OUT" | grep -E 'error TS[0-9]+' | head -c 2000)
  add_fail "tsc" "$T_FILTERED"
fi

if [[ -n "$OUT" ]]; then
  printf '%s' "$OUT" | head -c 2000 >&2
  exit 2
fi
exit 0
