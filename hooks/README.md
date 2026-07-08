# Codex Hooks

Review-only Codex hook bundle for this setup. These files are not active unless
`hooks/hooks.json` is linked or copied into an active Codex config layer.

- `pre_tool_use_bash_guard.py` blocks common destructive shell commands.
- `pre_tool_use_protected_files.py` blocks edits to env, credential, and key files.
- `user_prompt_secret_scan.py` blocks prompts that appear to include secrets.
- `post_tool_use_changed_file_checks.py` runs focused checks on edited files.
- `stop_changed_tree_checks.py` runs final changed-tree checks before Codex stops.

The check hooks intentionally no-op when a repository does not have matching
local tools such as `node_modules/.bin/eslint`, `node_modules/.bin/prettier`, or
package scripts named `lint`, `typecheck`, `test:run`, or `test:ci`.
