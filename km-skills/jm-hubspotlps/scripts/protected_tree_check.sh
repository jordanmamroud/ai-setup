#!/usr/bin/env bash
set -euo pipefail

mode="${1:---local}"
base="${2:-main}"

paths=(
  "jm-theme/templates"
  "jm-theme/modules"
  "jm-theme/assets"
  "jm-theme/theme.json"
  "jm-theme/fields.json"
)

case "$mode" in
  --local)
    git diff --find-renames --diff-filter=MDR --name-status HEAD -- "${paths[@]}"
    ;;
  --branch)
    git diff --find-renames --diff-filter=MDR --name-status "$base" HEAD -- "${paths[@]}"
    ;;
  *)
    echo "Usage: protected_tree_check.sh [--local | --branch <base-ref>]" >&2
    exit 2
    ;;
esac
