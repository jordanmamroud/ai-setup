#!/usr/bin/env bash
# claude-link-commands.sh — install ai-setup Claude commands + named files into ~/.claude/.
#
# Three things this does:
#
# 1. Each subfolder in shared skills/ can become a slash command at
#    ~/.claude/commands/<name>.md. Algorithm per folder:
#    - If claude-command.md exists: read `name:` from frontmatter when present;
#      otherwise use the folder name.
#    - Else: pick the single entry .md file by filtering out
#      README/CLAUDE/overview/STATUS/Context/transcript/spec/brainstorm/
#      CHECKPOINT/BEDTIME/SKILL/codex-prompt/*-spec/*-prompt. If the filename
#      ends in "-command", that suffix is stripped for the slash name.
#    - Ignore Codex-only packaged skill folders; warn only when a likely Claude
#      command folder has no clear entry.
#
# 2. Folders listed in CLAUDE_SKILL_FOLDERS are Claude skills (model-invocable,
#    SKILL.md entry), not slash commands: the whole folder is symlinked to
#    ~/.claude/skills/<name> and excluded from command linking.
#
# 3. Named file mappings:
#    agent-rules/CLAUDE.md -> ~/.claude/CLAUDE.md
#
# Idempotent. Uses `ln -sfn` so dangling or stale symlinks get refreshed.
# Will not overwrite a real (non-symlink, non-empty) file at the destination.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && /bin/pwd -P)"
CLAUDE_DIR="${HOME}/.claude"
SKILLS_DIR="${REPO_DIR}/skills"

mkdir -p "${CLAUDE_DIR}/commands" "${CLAUDE_DIR}/skills"

# Folders in skills/ that install as Claude skills (~/.claude/skills/<name>)
# instead of slash commands. Opt-in by name so existing folders keep their
# command behavior.
CLAUDE_SKILL_FOLDERS=(
  brainstorming
  define-outcome
  jm-council
  jm-skill-creator
  web-perf
  writing-plans
)

is_claude_skill_folder() {
  local n
  for n in "${CLAUDE_SKILL_FOLDERS[@]}"; do
    [ "$1" = "$n" ] && return 0
  done
  return 1
}

is_non_entry() {
  case "$1" in
    README.md|CLAUDE.md|overview.md|STATUS.md|Context.md) return 0 ;;
    transcript.md|spec.md|brainstorm.md|CHECKPOINT.md|BEDTIME.md) return 0 ;;
    SKILL.md|codex-prompt.md|claude-command.md) return 0 ;;
    *-spec.md|*-prompt.md) return 0 ;;
  esac
  return 1
}

frontmatter_name() {
  awk '/^name:[[:space:]]*/ {
    sub(/^name:[[:space:]]*/, "");
    sub(/[[:space:]]+$/, "");
    print;
    exit
  }' "$1"
}

linked=0
unchanged=0
skipped=0

# 1. Shared skills -> slash commands
for dir in "${SKILLS_DIR}"/*/; do
  [ -d "$dir" ] || continue
  dir="${dir%/}"  # strip trailing slash for clean path output
  name="$(basename "$dir")"

  if is_claude_skill_folder "$name"; then
    continue  # handled by the Claude-skills section below
  fi

  entry=""
  slash=""

  if [ -f "$dir/claude-command.md" ]; then
    entry="$dir/claude-command.md"
    slash="$(frontmatter_name "$entry")"
    [ -n "$slash" ] || slash="$name"
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
        if [ -f "$dir/SKILL.md" ] || [ -f "$dir/codex-prompt.md" ]; then
          continue
        fi
        echo "warn: $name has no Claude command entry .md — skipping" >&2
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

# 2. Claude skill folders -> ~/.claude/skills/<name>
for name in "${CLAUDE_SKILL_FOLDERS[@]}"; do
  src="${SKILLS_DIR}/${name}"
  if [ ! -f "${src}/SKILL.md" ]; then
    echo "warn: ${name} listed in CLAUDE_SKILL_FOLDERS but has no SKILL.md — skipping" >&2
    skipped=$((skipped + 1))
    continue
  fi
  dst="${CLAUDE_DIR}/skills/${name}"
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
  "agent-rules/CLAUDE.md:${CLAUDE_DIR}/CLAUDE.md"
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
