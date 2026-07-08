#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ESLINT_EXTS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
PRETTIER_EXTS = {
    ".css",
    ".html",
    ".js",
    ".jsx",
    ".json",
    ".md",
    ".mdx",
    ".mjs",
    ".scss",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
}
SHELL_EXTS = {".bash", ".sh", ".zsh"}


def read_hook_input():
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def pretool_deny(reason):
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    raise SystemExit(0)


def stderr_block(reason):
    print(reason, file=sys.stderr)
    raise SystemExit(2)


def git_root(cwd=None):
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=cwd or os.getcwd(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip())


def parse_apply_patch_paths(command):
    prefixes = (
        "*** Add File: ",
        "*** Delete File: ",
        "*** Update File: ",
        "*** Move to: ",
    )
    paths = []
    seen = set()
    for line in command.splitlines():
        for prefix in prefixes:
            if line.startswith(prefix):
                path = line[len(prefix) :].strip()
                if path and path not in seen:
                    paths.append(path)
                    seen.add(path)
                break
    return paths


def changed_git_paths(root):
    commands = (
        ["git", "diff", "--name-only", "--diff-filter=ACMRT"],
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    )
    paths = []
    seen = set()
    for command in commands:
        result = subprocess.run(
            command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode != 0:
            continue
        for line in result.stdout.splitlines():
            path = line.strip()
            if path and path not in seen:
                paths.append(path)
                seen.add(path)
    return paths


def run_checked(label, command, cwd, timeout=60):
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"{label} failed to run: {exc}"

    if result.returncode == 0:
        return None

    output = (result.stdout or "").strip()
    if len(output) > 4000:
        output = output[:4000] + "\n... output truncated ..."
    return f"{label} failed:\n{output}"


def local_node_bin(root, name):
    path = root / "node_modules" / ".bin" / name
    if path.exists():
        return str(path)
    return None


def package_scripts(root):
    package_json = root / "package.json"
    if not package_json.exists():
        return {}
    try:
        data = json.loads(package_json.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    scripts = data.get("scripts", {})
    return scripts if isinstance(scripts, dict) else {}


def package_manager_command(root):
    candidates = (
        ("pnpm-lock.yaml", "pnpm"),
        ("yarn.lock", "yarn"),
        ("bun.lockb", "bun"),
        ("bun.lock", "bun"),
        ("package-lock.json", "npm"),
    )
    for lockfile, command in candidates:
        if (root / lockfile).exists() and shutil.which(command):
            return command
    if (root / "package.json").exists() and shutil.which("npm"):
        return "npm"
    return None


def package_run_command(manager, script):
    if manager == "npm":
        return ["npm", "run", script]
    return [manager, "run", script]


def full_path_for(root, path):
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        return candidate.resolve()
    except OSError:
        return candidate


def focused_file_checks(root, paths):
    failures = []
    prettier = local_node_bin(root, "prettier")
    eslint = local_node_bin(root, "eslint")
    shellcheck = shutil.which("shellcheck")

    for path in paths:
        full_path = full_path_for(root, path)
        if not full_path.exists() or not full_path.is_file():
            continue
        try:
            rel = str(full_path.relative_to(root))
        except ValueError:
            continue
        suffix = full_path.suffix.lower()

        if suffix == ".py":
            failure = run_checked(
                f"python compile {rel}",
                [sys.executable, "-m", "py_compile", rel],
                root,
                timeout=30,
            )
            if failure:
                failures.append(failure)

        if prettier and suffix in PRETTIER_EXTS:
            failure = run_checked(
                f"prettier --check {rel}",
                [prettier, "--check", rel],
                root,
                timeout=30,
            )
            if failure:
                failures.append(failure)

        if eslint and suffix in ESLINT_EXTS:
            failure = run_checked(
                f"eslint {rel}",
                [eslint, rel],
                root,
                timeout=60,
            )
            if failure:
                failures.append(failure)

        if shellcheck and suffix in SHELL_EXTS:
            failure = run_checked(
                f"shellcheck {rel}",
                [shellcheck, rel],
                root,
                timeout=30,
            )
            if failure:
                failures.append(failure)

    return failures


def project_checks(root):
    scripts = package_scripts(root)
    manager = package_manager_command(root)
    if not scripts or not manager:
        return []

    failures = []
    for script in ("typecheck", "lint", "test:run", "test:ci"):
        if script not in scripts:
            continue
        failure = run_checked(
            f"{manager} run {script}",
            package_run_command(manager, script),
            root,
            timeout=180,
        )
        if failure:
            failures.append(failure)
    return failures
