# ai-setup restructure plan

> **Superseded (2026-05-18).** This documents the earlier `commands/` → `skills/` migration and is kept as a historical record — paths below are accurate *for that migration* and are intentionally NOT rewritten. Since then, `skills/` was renamed to `claude-skills/` and a `codex-skills/` folder + `codex-link-commands.sh` were added (Claude/Codex split). For the current layout see `CLAUDE.md` and `overview/`.

Plan-only. No file moves yet. Walk through one step at a time and confirm before each.

## 1. Top-level structure

```
~/mylab/ai-setup/
├── skills/        # all skills (slash-command + SKILL.md form, mixed)
├── terminal/      # shell-adjacent stuff
├── raycast/       # renamed from raycast-scripts/
├── tuning/        # renamed from agent-tuning/
│
├── README.md
├── CLAUDE.md
├── CLAUDE-global.md
├── AGENTS.md
└── claude-link-commands.sh
```

## 2. `terminal/` contents

| From | To |
|---|---|
| `myshortcuts-shell/` | `terminal/shortcuts/` |
| `ghostty/` | `terminal/ghostty/` |
| `zshrc` | `terminal/zshrc` |

Rationale: "the shell in the terminal" — same thing. `shortcuts/` is a subfolder under `terminal/`. Future shell scripts that aren't PATH shortcuts can still live in `terminal/` alongside `shortcuts/`.

## 3. Step 1 — 9 locked skill moves

| From | To |
|---|---|
| `commands/mycheckpoint/` | `skills/mydoc-checkpoint/` |
| `commands/myopen/` | `skills/myopen/` |
| `commands/myport/` | `skills/myport/` |
| `commands/mytodo/` | `skills/mytodo/` |
| `commands/myrefactor/` | `skills/myrefactor/` |
| `self-documenting/myoverview/` | `skills/mydoc-overview/` |
| `self-documenting/myspec/` | `skills/mydoc-spec/` |
| `self-verify/` | `skills/myverify-innerloop/` |
| `agents/ui-verify/` | `skills/myverify-ui/` |

## 4. Naming convention

`<group>-<thing>` prefix, but **only when a skill has peers**. Singletons stay bare until they get a sibling.

- **`mydoc-`** (documentation skills): `mydoc-overview`, `mydoc-spec`, `mydoc-checkpoint`. Future `mybedtime`, `myinit` likely join here.
- **`myverify-`** (verification skills): `myverify-innerloop`, `myverify-ui`. Future outerloop joins here.
- **Bare** (no peers yet): `myopen`, `myport`, `mytodo`, `myrefactor`.

Matches the documented `<group>-<verb>-<target>` convention in `CLAUDE.md` (here it's `<group>-<thing>` since the "verb" is implicit in the skill name).

## 5. Self-contained skill folders + runtime constraint

**Rule:** every skill's folder holds runtime + sidecars + design docs together. No splitting into a separate `docs/` subtree. Subfolders inside a skill only where the existing tool already uses them (`innerloop/`, `research/`).

**Why it's locked:** two skills self-locate at runtime and read sibling files:

- **`ui-verify`**: bash script uses `${BASH_SOURCE[0]}` to find itself, then reads sibling `system-prompt.md`, `mcp.json`, `config.sh`. Move any of those out of the folder and it breaks. Its README explicitly says **do not edit the bash script or system prompt** — tuned across adversarial testing.
- **`my-verify-innerloop`**: install step uses `SELF_VERIFY=$(dirname "$(readlink "$HOME/.claude/commands/my-verify-innerloop.md"))"` to find sibling `innerloop/*.sh` hook scripts. `innerloop/` must stay sibling of the `.md`.

Self-contained also matches the stated preference: easier for AI sessions to work on a skill without cross-referencing across the repo.

## 6. Deferred (explicitly punted)

- **Entry-point filename convention** — `SKILL.md` (current: `mydoc-overview`, `mydoc-spec`) vs `<name>.md` (current: most others). Recommendation when revisited: **keep mixed**, have `claude-link-commands.sh` detect which is inside each skill folder.
- **Dead files** flagged, not yet authorized to delete:
  - `CLAUDE-sytems.md` (typo, 1 line)
  - `CLAUDE-global-full.md.bak`
  - `self-documenting/mydocs-command.md` (empty)
- **`outerloop-spec.md`** — travels with `self-verify/` into `myverify-innerloop/` for now; splits into its own `skills/myverify-outerloop/` when that skill actually gets built.
- **`commands/overview.md`** (workshop-pattern doc) — `commands/` is dissolving. Either move its content to `skills/README.md` or discard. Decide before Step 4.

## 7. Step sequence

### Phase A — Moves (folder relocations only)

**Step 1 — LOCKED.** 9 skill moves (see §3). Use `git mv` to preserve history.

**Step 2.** `terminal/` consolidation:
- `myshortcuts-shell/` → `terminal/shortcuts/`
- `ghostty/` → `terminal/ghostty/`
- `zshrc` → `terminal/zshrc`

**Step 3.** Top-level renames: `raycast-scripts/` → `raycast/`, `agent-tuning/` → `tuning/`.

**Step 4.** Remove now-empty source folders (`commands/`, `self-documenting/`, `agents/`). Decide `commands/overview.md` fate first.

### Phase B — Update path strings INSIDE moved files

**Step 5a — Skill folder internal refs.**

| File | Refs to update |
|---|---|
| `skills/myverify-ui/README.md` | ~12 refs to `~/mylab/ai-setup/agents/ui-verify/` → `~/mylab/ai-setup/skills/myverify-ui/`. Includes the install snippet's path. |
| `skills/myverify-ui/my-uiverify-command.md` | Lines 9, 17, 77 — same path swap. |
| `skills/myverify-ui/STATUS.md` | Lines 7, 21, 22, 39 — same path swap. |
| `skills/myverify-innerloop/my-verify-innerloop.md` | `readlink` lookup at line 114 stays as-is (it reads `~/.claude/commands/my-verify-innerloop.md`); folder-name prose at line 121 (`self-verify`) → `myverify-innerloop`. |
| `skills/myverify-innerloop/outerloop-spec.md` | `self-verify` mentions → `myverify-innerloop` / `myverify-outerloop` as appropriate. |
| `skills/myverify-innerloop/overview.md` | `self-verify` references → `myverify-innerloop`. |
| `skills/myverify-innerloop/CLAUDE.md` | `self-verify` references → `myverify-innerloop`. |
| `skills/mydoc-checkpoint/overview.md` | Line 15: `~/mylab/ai-setup/commands/mycheckpoint/mycheckpoint.md` → `skills/mydoc-checkpoint/mycheckpoint.md`. Line 53: `~/mylab/ai-setup/self-documenting/myoverview/SKILL.md` → `skills/mydoc-overview/SKILL.md`. |

**Step 5b — terminal/ internal refs.**

| File | Refs to update |
|---|---|
| `terminal/shortcuts/README.md` | All `~/mylab/ai-setup/myshortcuts-shell/` → `terminal/shortcuts/`. All `~/mylab/ai-setup/agent-tuning/` → `terminal/../tuning/` (or absolute). `ai-setup/zshrc` → `terminal/zshrc`. |
| `terminal/ghostty/README.md` | Line 12: `~/mylab/ai-setup/ghostty/config` → `~/mylab/ai-setup/terminal/ghostty/config`. Line 40: `~/mylab/ai-setup/zshrc` → `~/mylab/ai-setup/terminal/zshrc`. |
| `terminal/zshrc` | Line 3 `export PATH=`: `myshortcuts-shell` → `terminal/shortcuts`. Comments on lines 14, 22, 49, 60 mentioning `myshortcuts-shell` → `terminal/shortcuts`. Mirror these edits to live `~/.zshrc` (see Step 7). |

**Step 5c — tuning/ internal refs.**

| File | Refs to update |
|---|---|
| `tuning/README.md` | `agent-tuning/` → `tuning/`. `~/mylab/ai-setup/myshortcuts-shell/` → `~/mylab/ai-setup/terminal/shortcuts/`. |

**Step 5d — Files to leave alone (historical state).**

Do NOT rewrite these — they capture state at the time of writing:
- `tuning/good-responses.md`, `tuning/bad-responses.md` (`**Source:**` lines from past sessions)
- `skills/myverify-innerloop/transcript.md` (historical session log)
- `skills/myport/brainstorm.md`, `skills/myrefactor/CHECKPOINT.md` (design notes that reference paths in their original context)

### Phase C — Update scripts with hardcoded paths

**Step 6 — Scripts in `terminal/shortcuts/`.**

| Script | Line | Change |
|---|---|---|
| `savegood` | 4 | `agent-tuning/good-responses.md` → `tuning/good-responses.md` |
| `savebad` | 4 | `agent-tuning/bad-responses.md` → `tuning/bad-responses.md` |
| `zsync` | 8 | `target="$HOME/mylab/ai-setup/zshrc"` → `terminal/zshrc` |
| `zsync` | 9 | `repo="$HOME/mylab/ai-setup"` — unchanged (the repo root is still ai-setup) |
| `mycmds` | 4 | `myshortcuts-shell/README.md` → `terminal/shortcuts/README.md` |
| `m` | — | Self-locates via `$0` / `BASH_SOURCE`; no hardcoded ai-setup path. Verify with `which m` post-move. |

`myshortcuts-shell/.claude/settings.local.json` — pre-existing stale entries (point at a never-existed `bin/m`). Either delete the file (it's just Bash permission allow-list for the workshop folder) or update paths to `terminal/shortcuts/m`. Recommend delete; ask before doing so.

**Step 7 — Raycast scripts in `raycast/`.**

| Script | Line | Change |
|---|---|---|
| `regenerate-project-picker.sh` | 9 | `SCRIPT_PATH=".../raycast-scripts/claude-open-project.sh"` → `raycast/claude-open-project.sh` |

The other Raycast scripts (`claude-open-myghub.sh`, `claude-open-quickie.sh`, `claude-open-project.sh`, `new_evernote.applescript`) reference `~/mylab/main` and `~/mylab/quickies` only — no ai-setup paths. Safe.

### Phase D — Update path strings OUTSIDE ai-setup

**Step 8 — Live system files.**

| File | Change |
|---|---|
| `~/.zshrc` line 3 | `export PATH="$HOME/mylab/ai-setup/myshortcuts-shell:$PATH"` → `terminal/shortcuts` |
| `~/.zshrc` lines 14, 22, 49, 60 (comments) | `myshortcuts-shell` → `terminal/shortcuts` |
| `~/.claude/CLAUDE.md` lines 80, 81 | `~/mylab/ai-setup/myshortcuts-shell/` and `~/mylab/ai-setup/myshortcuts-shell/README.md` → `terminal/shortcuts/` and `terminal/shortcuts/README.md` |

These must match the `terminal/zshrc` edits from Step 5b. After updating, run `source ~/.zshrc` to reload PATH in the current shell.

**Step 9 — Root-level docs.**

| File | Refs |
|---|---|
| `README.md` lines 7, 21, 53, 56, 59 | All `myshortcuts-shell` → `terminal/shortcuts` |
| `CLAUDE.md` line 5 | `raycast-scripts/` → `raycast/` |
| `CLAUDE.md` line 15 | Inventory list — rewrite to reflect new top-level shape (`skills/`, `terminal/`, `raycast/`, `tuning/`) |
| `CLAUDE-global.md` lines 80, 81 | Same edits as `~/.claude/CLAUDE.md` (this is the version-controlled mirror) |
| `AGENTS.md` | Check for any path refs (none found in audit, but verify) |

### Phase E — Rewrite the deploy script

**Step 10 — `claude-link-commands.sh` rewrite.**

Current state: assumes flat `commands/*.md` and `skills/*/SKILL.md`. Broken even today.

New behavior:
- For each subdir `D` in `skills/`:
  - If `D/SKILL.md` exists → symlink `~/.claude/commands/<D>.md` → `D/SKILL.md` (or `~/.claude/skills/<D>/SKILL.md`, decide entry convention)
  - Else if `D/<dirname>.md` exists → symlink `~/.claude/commands/<dirname>.md` → that file
  - Else if `D/<dirname>-command.md` exists (ui-verify pattern) → symlink with the bare name
  - Skip if neither exists; warn.
- Idempotent (use `ln -sf`); never delete unrelated files.

### Phase F — Re-point external pointers

**Step 11 — Symlinks.**

Run the rewritten `claude-link-commands.sh` to refresh `~/.claude/commands/*` automatically. Then manually:

| Symlink | New target |
|---|---|
| `~/bin/ui-verify` | `~/mylab/ai-setup/skills/myverify-ui/ui-verify` |
| `~/.claude/commands/my-uiverify.md` | `skills/myverify-ui/my-uiverify-command.md` (the symlink filename `my-uiverify.md` determines the slash command name — keep it) |
| `~/.claude/commands/my-verify-innerloop.md` | `skills/myverify-innerloop/my-verify-innerloop.md` |
| `~/.claude/commands/mycheckpoint.md` | `skills/mydoc-checkpoint/mycheckpoint.md` |
| `~/.claude/commands/myopen.md` | `skills/myopen/myopen.md` |
| `~/.claude/commands/myoverview.md` | `skills/mydoc-overview/SKILL.md` |
| `~/.claude/commands/myport.md` | `skills/myport/myport.md` |
| `~/.claude/commands/myspec.md` | `skills/mydoc-spec/SKILL.md` |
| `~/.claude/commands/mytodo.md` | `skills/mytodo/mytodo.md` |
| `~/.claude/commands/myrefactor.md` | **NEW** — `skills/myrefactor/myrefactor.md` (not currently symlinked; install during this step) |

Also note: `~/.claude/commands/` has unrelated **real** files (not symlinks) that the rewrite ignores: `mybedtime.md`, `myinit.md`, `myloop.md`, `mywriter.md`, `jm-transcript.md`. Leave them alone — they're outside the workshop.

**Step 12 — Raycast (manual UI step).**

Raycast stores Script Commands by absolute path. After `raycast-scripts/` → `raycast/`:
1. Open Raycast → Settings → Extensions → Script Commands.
2. Remove the old `raycast-scripts/` folder entry.
3. Add `~/mylab/ai-setup/raycast/` as a new Script Commands directory.
4. Verify the 4 commands (myghub opener, quickie opener, project picker, new_evernote) all show up and run.

### Phase G — Verify

**Step 13 — Smoke tests.**

Open a fresh shell (so `~/.zshrc` reloads cleanly), then:

- `which m` → `~/mylab/ai-setup/terminal/shortcuts/m`
- `mycmds` → prints the shortcuts list (proves `mycmds` resolved its new README path)
- `m savegood` → opens prompt; cancel; check `tuning/good-responses.md` would be the write target
- `zsync "test"` → backup ends up at `terminal/zshrc` and commits cleanly
- `ui-verify --help` (or smallest invocation) → bash bridge starts, finds its siblings
- `/myverify-innerloop` in a TS project → install path resolves through new symlink + readlink
- `/myoverview`, `/myspec`, `/mycheckpoint`, `/myopen`, `/myport`, `/mytodo`, `/myrefactor`, `/my-uiverify` — all resolve in a fresh Claude Code session
- Raycast: trigger each of the 4 script commands once

## Working agreements

- One step at a time. Confirm before each.
- Plan-only — no actual file moves yet.
- No deletions (including the three dead files in §6 and `myshortcuts-shell/.claude/settings.local.json`) without explicit authorization.
- "Each skill self-contained" is locked.
- Use `git mv` for every move so history follows the files.
- Phase B (Step 5) edits live inside files that are about to be referenced by the deploy script — order matters: complete all path-string updates before running the rewritten `claude-link-commands.sh` in Phase F.
