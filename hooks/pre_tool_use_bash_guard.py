#!/usr/bin/env python3
import re
import shlex

from hook_common import pretool_deny, read_hook_input


SAFE_READONLY_COMMANDS = {
    "awk",
    "cat",
    "echo",
    "egrep",
    "fgrep",
    "grep",
    "printf",
    "rg",
    "sed",
}


FULL_COMMAND_RULES = (
    (
        re.compile(r":\s*\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;?\s*:", re.I),
        "Fork bomb blocked.",
    ),
    (
        re.compile(r"\b(?:curl|wget)\b[^;\n]*\|\s*(?:sudo\s+)?(?:bash|sh|zsh)\b", re.I),
        "Piping an internet download into a shell is blocked.",
    ),
    (
        re.compile(r"\b(?:bash|sh|zsh)\s+<\(\s*(?:curl|wget)\b", re.I),
        "Running a shell from curl/wget process substitution is blocked.",
    ),
    (
        re.compile(r"\b(?:bash|sh|zsh)\s+-c\s+[\"']\s*\$\(\s*(?:curl|wget)\b", re.I),
        "Running a shell from curl/wget command substitution is blocked.",
    ),
)


SEGMENT_RULES = (
    (
        re.compile(
            r"\b(?:sudo\s+)?rm\b(?=[^;&|\n]*\s-[^\s;&|\n]*r)(?=[^;&|\n]*\s-[^\s;&|\n]*f)"
            r"[^;&|\n]*(?:\s|^)(?:/|~|\$HOME|\$\{HOME\})(?:\s|$|[;&|])",
            re.I,
        ),
        "Recursive force remove of root or home is blocked.",
    ),
    (
        re.compile(r"\bsudo\s+rm\b", re.I),
        "sudo rm is blocked.",
    ),
    (
        re.compile(r"\bmkfs(?:\.[a-z0-9_+-]+)?\b", re.I),
        "Disk format command blocked.",
    ),
    (
        re.compile(r"\bdd\b(?=[^;&|\n]*\bof=/dev/)", re.I),
        "Raw disk write with dd is blocked.",
    ),
    (
        re.compile(r"\bgit\s+reset\s+--hard\b", re.I),
        "git reset --hard is blocked.",
    ),
    (
        re.compile(r"\bgit\s+clean\b(?=[^;&|\n]*-[^\s;&|\n]*f)(?=[^;&|\n]*-[^\s;&|\n]*d)", re.I),
        "git clean -fd is blocked.",
    ),
    (
        re.compile(r"\bgit\s+checkout\s+(?:--\s+)?\.(?:\s|$)", re.I),
        "git checkout . is blocked.",
    ),
    (
        re.compile(r"\bgit\s+checkout\b(?=[^;&|\n]*\s-f(?:\s|$))", re.I),
        "git checkout -f is blocked.",
    ),
    (
        re.compile(r"\bgit\s+restore\s+(?:--\s+)?\.(?:\s|$)", re.I),
        "git restore . is blocked.",
    ),
    (
        re.compile(
            r"\bgit\s+push\b(?=[^;&|\n]*(?:--force(?:-with-lease)?|-f)\b)"
            r"(?=[^;&|\n]*\b(?:main|master)\b)",
            re.I,
        ),
        "Force push to main/master is blocked.",
    ),
    (
        re.compile(
            r"\b(?:psql|mysql|mariadb|sqlite3|duckdb|sqlcmd)\b"
            r"(?=[\s\S]*\b(?:drop\s+table|truncate\s+table)\b)",
            re.I,
        ),
        "Dangerous direct database statement is blocked.",
    ),
    (
        re.compile(r"\bchmod\s+(?:-R\s+777|777\s+-R)\b", re.I),
        "chmod -R 777 is blocked.",
    ),
)


def first_word(segment):
    stripped = segment.strip()
    if not stripped:
        return ""
    try:
        parts = shlex.split(stripped)
    except ValueError:
        parts = re.findall(r"[A-Za-z0-9_./-]+", stripped)
    if not parts:
        return ""
    word = parts[0]
    if word in {"command", "env"} and len(parts) > 1:
        word = parts[1]
    return word.rsplit("/", 1)[-1]


def main():
    hook_input = read_hook_input()
    tool_input = hook_input.get("tool_input") or {}
    command = tool_input.get("command", "")
    if not command:
        return

    for pattern, reason in FULL_COMMAND_RULES:
        if pattern.search(command):
            pretool_deny(reason)

    for segment in re.split(r"&&|\|\||[;|\n]", command):
        if first_word(segment) in SAFE_READONLY_COMMANDS:
            continue
        for pattern, reason in SEGMENT_RULES:
            if pattern.search(segment):
                pretool_deny(reason)


if __name__ == "__main__":
    main()
