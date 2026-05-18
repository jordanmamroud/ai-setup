#!/usr/bin/env bash
# codex-link-commands.sh — install ai-setup Codex skills + named files into ~/.codex/.
#
# Sibling of claude-link-commands.sh. The Claude installer links per-folder
# skills from claude-skills/ into ~/.claude/commands/. This one links Codex
# prompts and packaged skills from codex-skills/ into ~/.codex/.
#
# Three things this does:
#
# 1. Each codex-skills/<name>.md becomes a Codex prompt at
#    ~/.codex/prompts/<name>.md (invoked as /<name> in Codex). Codex prompts
#    carry no frontmatter — the file is the prompt body verbatim.
#
# 2. Each codex-skills/<name>/ folder with SKILL.md becomes a Codex skill at
#    ~/.codex/skills/<name>.
#
# 3. Named file mappings:
#    AGENTS.md -> ~/.codex/AGENTS.md          (Codex global instructions; the
#    analog of CLAUDE-global.md -> ~/.claude/CLAUDE.md in the Claude installer)
#
# Idempotent. Uses `ln -sfn` so dangling or stale symlinks get refreshed.
# Will not overwrite a real (non-symlink, non-empty) file at the destination;
# an empty file at the destination is replaced.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODEX_DIR="${HOME}/.codex"

mkdir -p "${CODEX_DIR}/prompts" "${CODEX_DIR}/skills"

linked=0
unchanged=0
skipped=0

# 1. codex-skills/*.md -> Codex prompts
for src in "${REPO_DIR}/codex-skills"/*.md; do
  [ -f "$src" ] || continue
  name="$(basename "${src%.md}")"
  dst="${CODEX_DIR}/prompts/${name}.md"

  if [ -e "$dst" ] && [ ! -L "$dst" ]; then
    echo "skip (real file at $dst — not overwriting)" >&2
    skipped=$((skipped + 1))
    continue
  fi
  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    unchanged=$((unchanged + 1))
    continue
  fi
  ln -sfn "$src" "$dst"
  echo "linked: $dst -> $src"
  linked=$((linked + 1))
done

# 2. codex-skills/*/ -> Codex skills
for src in "${REPO_DIR}/codex-skills"/*/; do
  [ -d "$src" ] || continue
  src="${src%/}"
  [ -f "${src}/SKILL.md" ] || continue
  name="$(basename "$src")"
  dst="${CODEX_DIR}/skills/${name}"

  if [ -e "$dst" ] && [ ! -L "$dst" ]; then
    echo "skip (real file/dir at $dst — not overwriting)" >&2
    skipped=$((skipped + 1))
    continue
  fi
  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    unchanged=$((unchanged + 1))
    continue
  fi
  ln -sfn "$src" "$dst"
  echo "linked: $dst -> $src"
  linked=$((linked + 1))
done

# 3. Named file mappings
# Format: "<repo-relative source>:<absolute destination>"
NAMED_FILES=(
  "AGENTS.md:${CODEX_DIR}/AGENTS.md"
)

for pair in "${NAMED_FILES[@]}"; do
  src_rel="${pair%%:*}"
  dst="${pair##*:}"
  src="${REPO_DIR}/${src_rel}"
  [ -e "$src" ] || continue
  if [ -e "$dst" ] && [ ! -L "$dst" ]; then
    if [ -f "$dst" ] && [ ! -s "$dst" ]; then
      rm "$dst"  # empty file at destination — safe to replace
    else
      echo "skip (real file at $dst — not overwriting)" >&2
      skipped=$((skipped + 1))
      continue
    fi
  fi
  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    unchanged=$((unchanged + 1))
    continue
  fi
  ln -sfn "$src" "$dst"
  echo "linked: $dst -> $src"
  linked=$((linked + 1))
done

echo
echo "done. linked=${linked} unchanged=${unchanged} skipped=${skipped}"
