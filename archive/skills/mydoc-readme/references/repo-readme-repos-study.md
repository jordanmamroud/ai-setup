# Repo README: repos-study / README.md

- Source repo: `repos-study`
- Source path: `README.md`
- Original file: `/Users/jordanmamroud/mylab/repos-study/README.md`

## Original README

# repos-study

Local copies of repos I want to study. Git history stripped (`.git` removed) — these are study snapshots, not tracked clones. Pulled 2026-06-03.

| Folder | Source | What it is | Scope |
|---|---|---|---|
| `superpowers/` | https://github.com/obra/superpowers | Claude Code skills/hooks framework | Full repo |
| `google-ads-mcp/` | https://github.com/googleads/google-ads-mcp | Official Google Ads MCP server (Python) | Full repo |
| `itallstartedwithaidea-agent-skills/` | https://github.com/itallstartedwithaidea/agent-skills/tree/main/skills | Collection of agent skills across 10 categories | `skills/` subfolder only |
| `adk-python-skills/` | https://github.com/google/adk-python/tree/main/.agents/skills | Google ADK's own Claude Code skills (adk-agent-builder, adk-architecture, etc.) | `.agents/skills` subfolder only |

## Notes

- **adk-python-skills** are *Claude Code style* skills (each has a `SKILL.md`), not ADK Python agent samples. To actually use them rather than read them, they'd live in a project-level `.claude/skills/` directory.
- To refresh any of these against upstream, re-clone from the URL above (history was intentionally dropped, so `git pull` won't work in place).
