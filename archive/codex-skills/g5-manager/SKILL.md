---
name: g5-manager
description: Audit and visualize Google Cloud Platform setups for AI-friendly operations. Use only when the user explicitly asks to use g5-manager or $g5-manager. Do not invoke implicitly for general Google Cloud, BigQuery, Google Ads, IAM, billing, Cloud Run, Storage, Secret Manager, Cloud SQL, Compute, Artifact Registry, or related GCP tasks. This skill starts read-only and must prefer proper local gcloud authorization over workaround access paths.
---

# G5 Manager

## Overview

Use this skill to help the user understand and maintain their Google Cloud setup through read-only inventory, visual reporting, and plain-English notes. Treat the AI as an operator interface, not an autonomous root admin.

## Safety Rules

- Start read-only unless the user explicitly asks for an approved apply workflow.
- Never add backend endpoints, temporary scripts, service account keys, broad IAM grants, or indirect access paths to work around missing auth.
- If `gcloud` lacks required permissions or scopes, stop the affected operation and tell the user which permission or login refresh is needed.
- Record inaccessible resources as audit gaps instead of guessing.
- Do not run destructive or mutating commands such as `delete`, `set-iam-policy`, `add-iam-policy-binding`, `remove-iam-policy-binding`, `services enable/disable`, `deploy`, `create`, `update`, or `apply` during audits.

## Read-Only Audit Workflow

1. Confirm `gcloud` is installed and an account is active:
   - `gcloud auth list --filter=status:ACTIVE --format=json`
   - `gcloud config get-value account`
2. Run the bundled audit script:
   - `python3 <skill-dir>/scripts/g5_audit.py --out ./g5-audit`
   - To restrict scope: `python3 <skill-dir>/scripts/g5_audit.py --projects project-a,project-b --out ./g5-audit`
3. Review generated files:
   - `g5-report.html` visual dashboard
   - `g5-report.json` machine-readable inventory
   - `g5-notes.md` summary, risks, and follow-up recommendations
4. Summarize the highest-risk findings for the user and point to the HTML report.

## Dashboard Expectations

The HTML report should prioritize quick re-orientation after months away:

- Active gcloud account and audit timestamp
- Project cards with project id, name, lifecycle state, labels, and billing status when available
- Risk badges for owner-heavy IAM, public IAM members, missing billing visibility, and inaccessible data
- Enabled API/service count
- Resource counts for Cloud Run, Storage buckets, Secret Manager, Cloud SQL, Compute Engine, and Artifact Registry
- Plain resource tables that favor scannability over console-like completeness

## Recommended Structure Guidance

When suggesting cleanup, prefer this progression:

1. Document what exists before changing anything.
2. Separate projects by environment or purpose only when there is a real operational reason.
3. Keep IAM least-privilege and group-based where possible.
4. Prefer infrastructure as code for repeatable resources once the current setup is understood.
5. Add naming conventions and labels before large migrations.

## Output Style

Be brief and concrete. Lead with whether the audit completed, where the files are, and the top risks or gaps. If permissions blocked inspection, name the exact blocked area and recommend the proper authorization path.
