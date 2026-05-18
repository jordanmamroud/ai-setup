#!/usr/bin/env bash
# claude-link-commands.sh — install ai-setup skills + named files into ~/.claude/.
#
# Three things this does:
#
# 1. Each subfolder in claude-skills/ becomes a slash command at
#    ~/.claude/commands/<name>.md. Algorithm per folder:
#    - If SKILL.md exists: read `name:` from frontmatter; link SKILL.md as
#      <name>.md.
#    - Else: pick the single entry .md file by filtering out
#      README/CLAUDE/overview/STATUS/Context/transcript/spec/brainstorm/
#      CHECKPOINT/BEDTIME/*-spec/*-prompt. If the filename ends in
#      "-command", that suffix is stripped for the slash name.
#    - Skip with warning if no clear entry can be picked.
#
# 2. Named file mappings:
#    CLAUDE-global.md -> ~/.claude/CLAUDE.md
#
# 3. ~/bin/ui-verify -> claude-skills/myverify-ui/ui-verify (puts the shell command
#    on PATH).
#
# Idempotent. Uses `ln -sfn` so dangling or stale symlinks get refreshed.
# Will not overwrite a real (non-symlink, non-empty) file at the destination.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${HOME}/.claude"

mkdir -p "${CLAUDE_DIR}/commands"

is_non_entry() {
  case "$1" in
    README.md|CLAUDE.md|overview.md|STATUS.md|Context.md) return 0 ;;
    transcript.md|spec.md|brainstorm.md|CHECKPOINT.md|BEDTIME.md) return 0 ;;
    *-spec.md|*-prompt.md) return 0 ;;
  esac
  return 1
}

linked=0
unchanged=0
skipped=0

# 1. Skills -> slash commands
for dir in "${REPO_DIR}/claude-skills"/*/; do
  [ -d "$dir" ] || continue
  dir="${dir%/}"  # strip trailing slash for clean path output
  name="$(basename "$dir")"

  entry=""
  slash=""

  if [ -f "$dir/SKILL.md" ]; then
    slash="$(awk '/^name:[[:space:]]*/ {
      sub(/^name:[[:space:]]*/, "");
      sub(/[[:space:]]+$/, "");
      print;
      exit
    }' "$dir/SKILL.md")"
    if [ -z "$slash" ]; then
      echo "warn: $name/SKILL.md has no 'name:' frontmatter — skipping" >&2
      skipped=$((skipped + 1))
      continue
    fi
    entry="$dir/SKILL.md"
  else
    candidates=()
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      base="$(basename "$f")"
      if ! is_non_entry "$base"; then
        candidates+=("$f")
      fi
    done < <(find "$dir" -maxdepth 1 -type f -name '*.md')

    case "${#candidates[@]}" in
      0)
        echo "warn: $name has no entry .md (only design docs / READMEs) — skipping" >&2
        skipped=$((skipped + 1))
        continue
        ;;
      1)
        entry="${candidates[0]}"
        base="$(basename "${entry%.md}")"
        slash="${base%-command}"
        ;;
      *)
        echo "warn: $name has multiple entry candidates — skipping:" >&2
        printf '  %s\n' "${candidates[@]}" >&2
        skipped=$((skipped + 1))
        continue
        ;;
    esac
  fi

  dst="${CLAUDE_DIR}/commands/${slash}.md"
  if [ -e "$dst" ] && [ ! -L "$dst" ]; then
    echo "skip (real file at $dst — not overwriting)" >&2
    skipped=$((skipped + 1))
    continue
  fi
  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$entry" ]; then
    unchanged=$((unchanged + 1))
    continue
  fi
  ln -sfn "$entry" "$dst"
  echo "linked: $dst -> $entry"
  linked=$((linked + 1))
done

# 2. Named file mappings
# Format: "<repo-relative source>:<absolute destination>"
NAMED_FILES=(
  "CLAUDE-global.md:${CLAUDE_DIR}/CLAUDE.md"
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

# 3. ~/bin/ui-verify
ui_verify="${REPO_DIR}/claude-skills/myverify-ui/ui-verify"
if [ -f "$ui_verify" ]; then
  mkdir -p "${HOME}/bin"
  bin_dst="${HOME}/bin/ui-verify"
  if [ -e "$bin_dst" ] && [ ! -L "$bin_dst" ]; then
    echo "skip (real file at $bin_dst — not overwriting)" >&2
    skipped=$((skipped + 1))
  elif [ -L "$bin_dst" ] && [ "$(readlink "$bin_dst")" = "$ui_verify" ]; then
    unchanged=$((unchanged + 1))
  else
    ln -sfn "$ui_verify" "$bin_dst"
    echo "linked: $bin_dst -> $ui_verify"
    linked=$((linked + 1))
  fi
fi

echo
echo "done. linked=${linked} unchanged=${unchanged} skipped=${skipped}"
