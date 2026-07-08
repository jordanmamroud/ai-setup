#!/usr/bin/env python3
from hook_common import (
    focused_file_checks,
    git_root,
    parse_apply_patch_paths,
    read_hook_input,
    stderr_block,
)


def main():
    hook_input = read_hook_input()
    tool_input = hook_input.get("tool_input") or {}
    command = tool_input.get("command", "")
    paths = parse_apply_patch_paths(command)
    if not paths:
        return

    root = git_root()
    if not root:
        return

    failures = focused_file_checks(root, paths)
    if failures:
        stderr_block("Focused checks failed after edit:\n\n" + "\n\n".join(failures))


if __name__ == "__main__":
    main()
