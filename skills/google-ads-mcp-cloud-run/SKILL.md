---
name: google-ads-mcp-cloud-run
description: Validate, operate, and deploy the Kitchen Magic Google Ads MCP fork from /Users/jordanmamroud/mylab/km/mcps/ga-mcp. Use when working on this Python FastMCP server, local project-scoped MCP config, fixed GOOGLE_ADS_CUSTOMER_ID behavior, ADC or server-side Google Ads OAuth auth, bearer-token MCP access, Cloud Run deployment in project km-ga-mcp, or docs such as OVERVIEW.md, LOCAL_SETUP.md, .env.example, and cloud-run.env.example.
---

# Google Ads MCP Cloud Run

## Overview

Use this skill to keep the local fork of `googleads/google-ads-mcp` aligned with its intended deployment model: local stdio over project-scoped config, and hosted Cloud Run over Streamable HTTP with bearer-token MCP auth. Protect the auth boundary: agents authenticate to MCP with `Authorization: Bearer <MCP_BEARER_TOKEN>`; the server authenticates to Google Ads with server-side OAuth env vars.

Default repo root:

```text
/Users/jordanmamroud/mylab/km/mcps/ga-mcp
```

## Workflow

Start with local state, then validate, then deploy only after auth and tests are clean.

1. Read repo instructions first: `AGENTS.md` if present, then `OVERVIEW.md`; read `LOCAL_SETUP.md` and `cloud-run.env.example` when the task touches setup or deployment.
2. Inspect `git status --short --branch` before edits and preserve all existing work.
3. Use local project-scoped MCP config only: `.codex/config.toml`, `.gemini/settings.json`, and `scripts/run-google-ads-mcp`.
4. Prefer the correct authorization path. If ADC or Google Ads OAuth scopes are missing, stop and ask the user to grant or refresh the proper scope. Do not add workaround endpoints, scripts, or indirect backend access just to dodge re-authentication.
5. Keep the MCP private in practice: Cloud Run may need `--allow-unauthenticated` so MCP clients can reach it, but every MCP request must be rejected unless it carries the configured bearer token.
6. Run unit tests before deployment:

```shell
.venv/bin/python -m unittest discover -s tests -p '*_test.py'
```

## Stack Rules

- Local auth uses ADC at `~/.config/gcloud/application_default_credentials.json`.
- Local `.env` should keep account-level values only: `GOOGLE_PROJECT_ID`, `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_CUSTOMER_ID`, `GOOGLE_ADS_MCP_BASE_URL`, `PORT`, and `FASTMCP_HOST`.
- Do not add `GOOGLE_ADS_CLIENT_SECRET` or `GOOGLE_ADS_REFRESH_TOKEN` to local stdio `.env`.
- Cloud Run auth uses `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`, `GOOGLE_ADS_REFRESH_TOKEN`, `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_CUSTOMER_ID`, and `MCP_BEARER_TOKEN`.
- `GOOGLE_ADS_CUSTOMER_ID` is fixed for this stack. Tools should resolve to it automatically and should not prompt agents for a customer ID when it is configured.
- Do not set `GOOGLE_ADS_LOGIN_CUSTOMER_ID` unless the account is accessed through a manager account.
- Keep exposed tools read-oriented unless the user explicitly asks for write tooling and the auth/security model is updated.

## Deployment Reference

For Cloud Run commands, env var handling, smoke checks, and client config snippets, read `references/deployment.md`.

If running `gcloud` commands and a local `gcloud` skill is available, read it first and follow its command-safety rules.

## Validation Checklist

- Confirm unit tests pass.
- Confirm bearer middleware rejects missing or wrong tokens and accepts the correct `Authorization` header.
- Confirm `/mcp` is the hosted MCP URL path.
- Confirm sensitive Cloud Run env vars are mapped from Secret Manager, not committed files or raw deploy flags.
- Confirm no globally usable unauthenticated MCP access exists.

## User-Facing Guidance

Be direct and brief. When presenting alternatives, use A/B/C/D only for real decision options and end with a recommended next step.
