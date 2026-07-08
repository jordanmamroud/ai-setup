#!/usr/bin/env python3
from pathlib import PurePosixPath

from hook_common import parse_apply_patch_paths, pretool_deny, read_hook_input


SENSITIVE_SUFFIXES = {".key", ".pem", ".p12", ".pfx"}
SENSITIVE_FILENAMES = {
    ".netrc",
    "credentials",
    "credentials.json",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
    "secrets.json",
}
SENSITIVE_DIRS = {".aws", ".gnupg", ".ssh", "credentials", "secrets"}


def protection_reason(path):
    normalized = path.replace("\\", "/")
    parts = [part for part in PurePosixPath(normalized).parts if part not in {"", "."}]
    lowered_parts = [part.lower() for part in parts]
    basename = lowered_parts[-1] if lowered_parts else normalized.lower()

    if basename.startswith(".env"):
        return ".env files are protected"
    if any(part in SENSITIVE_DIRS for part in lowered_parts):
        return "credential and key directories are protected"
    if basename in SENSITIVE_FILENAMES:
        return "credential and key files are protected"
    if any(basename.endswith(suffix) for suffix in SENSITIVE_SUFFIXES):
        return "private key material is protected"
    if basename.endswith((".json", ".yaml", ".yml", ".toml", ".ini")) and (
        "credential" in basename or basename.startswith("secret") or basename.startswith("secrets")
    ):
        return "credential and secret config files are protected"
    return None


def main():
    hook_input = read_hook_input()
    tool_input = hook_input.get("tool_input") or {}
    command = tool_input.get("command", "")
    paths = parse_apply_patch_paths(command)

    for path in paths:
        reason = protection_reason(path)
        if reason:
            pretool_deny(f"{reason}: {path}")


if __name__ == "__main__":
    main()
