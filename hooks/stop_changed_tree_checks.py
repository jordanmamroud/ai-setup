#!/usr/bin/env python3
import json

from hook_common import changed_git_paths, focused_file_checks, git_root, project_checks, read_hook_input


def continue_with(reason):
    print(json.dumps({"decision": "block", "reason": reason}))
    raise SystemExit(0)


def main():
    hook_input = read_hook_input()
    if hook_input.get("stop_hook_active"):
        print("{}")
        return

    root = git_root()
    if not root:
        print("{}")
        return

    changed_paths = changed_git_paths(root)
    if not changed_paths:
        print("{}")
        return

    failures = []
    failures.extend(focused_file_checks(root, changed_paths))
    failures.extend(project_checks(root))

    if failures:
        continue_with("Final checks failed. Fix these before stopping:\n\n" + "\n\n".join(failures))

    print("{}")


if __name__ == "__main__":
    main()
