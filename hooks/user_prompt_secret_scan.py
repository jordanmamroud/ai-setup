#!/usr/bin/env python3
import json
import re

from hook_common import read_hook_input


SECRET_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("OpenAI API key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("Google API key", re.compile(r"\bAIza[A-Za-z0-9_-]{35}\b")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("Stripe secret key", re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}\b")),
    (
        "generic secret assignment",
        re.compile(
            r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|secret|credential)"
            r"\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+=:-]{20,}"
        ),
    ),
)


def block(reason):
    print(
        json.dumps(
            {
                "decision": "block",
                "reason": (
                    f"Prompt appears to contain a {reason}. Remove the secret or replace it "
                    "with a placeholder before sending."
                ),
            }
        )
    )
    raise SystemExit(0)


def main():
    hook_input = read_hook_input()
    prompt = hook_input.get("prompt", "")
    if not prompt:
        return

    for label, pattern in SECRET_PATTERNS:
        if pattern.search(prompt):
            block(label)


if __name__ == "__main__":
    main()
