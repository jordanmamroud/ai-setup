#!/usr/bin/env python3
"""
Read-only Google Cloud inventory and dashboard generator for the g5-manager skill.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


READ_TIMEOUT = 45


def run_gcloud(args: list[str], project: str | None = None) -> dict[str, Any]:
    cmd = ["gcloud", "--quiet", *args]
    if project:
        cmd.extend(["--project", project])
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=READ_TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        return {"ok": False, "cmd": cmd, "error": f"Timed out after {READ_TIMEOUT}s: {exc}"}

    if proc.returncode != 0:
        return {"ok": False, "cmd": cmd, "error": (proc.stderr or proc.stdout).strip()}

    output = proc.stdout.strip()
    if "--format=json" in args:
        try:
            return {"ok": True, "cmd": cmd, "data": json.loads(output or "null")}
        except json.JSONDecodeError as exc:
            return {"ok": False, "cmd": cmd, "error": f"Invalid JSON: {exc}", "raw": output}
    return {"ok": True, "cmd": cmd, "data": output}


def list_or_empty(result: dict[str, Any], gaps: list[dict[str, str]], label: str) -> list[Any]:
    if result["ok"]:
        data = result.get("data")
        return data if isinstance(data, list) else []
    if is_service_disabled(result.get("error", "")):
        gaps.append({"area": label, "kind": "service_disabled", "error": result.get("error", "Service disabled")})
        return []
    gaps.append({"area": label, "error": result.get("error", "Unknown error")})
    return []


def object_or_empty(result: dict[str, Any], gaps: list[dict[str, str]], label: str) -> dict[str, Any]:
    if result["ok"]:
        data = result.get("data")
        return data if isinstance(data, dict) else {}
    if is_service_disabled(result.get("error", "")):
        gaps.append({"area": label, "kind": "service_disabled", "error": result.get("error", "Service disabled")})
        return {}
    gaps.append({"area": label, "error": result.get("error", "Unknown error")})
    return {}


def is_service_disabled(error: str) -> bool:
    return "SERVICE_DISABLED" in error or "has not been used" in error or "not enabled on project" in error


def collect_project(project: dict[str, Any]) -> dict[str, Any]:
    project_id = project.get("projectId", "")
    gaps: list[dict[str, str]] = []
    inventory: dict[str, Any] = {
        "project": project,
        "gaps": gaps,
        "services": [],
        "iam": {},
        "billing": {},
        "resources": {},
        "risks": [],
    }

    inventory["services"] = list_or_empty(
        run_gcloud(["services", "list", "--enabled", "--format=json"], project_id),
        gaps,
        f"{project_id}: enabled services",
    )
    inventory["iam"] = object_or_empty(
        run_gcloud(["projects", "get-iam-policy", project_id, "--format=json"]),
        gaps,
        f"{project_id}: IAM policy",
    )
    inventory["billing"] = object_or_empty(
        run_gcloud(["billing", "projects", "describe", project_id, "--format=json"]),
        gaps,
        f"{project_id}: billing",
    )

    resource_commands = {
        "cloud_run": ["run", "services", "list", "--platform=managed", "--format=json"],
        "storage_buckets": ["storage", "buckets", "list", "--format=json"],
        "secrets": ["secrets", "list", "--format=json"],
        "sql_instances": ["sql", "instances", "list", "--format=json"],
        "compute_instances": ["compute", "instances", "list", "--format=json"],
        "artifact_repositories": ["artifacts", "repositories", "list", "--format=json"],
    }
    for key, cmd in resource_commands.items():
        inventory["resources"][key] = list_or_empty(
            run_gcloud(cmd, project_id),
            gaps,
            f"{project_id}: {key.replace('_', ' ')}",
        )

    inventory["risks"] = project_risks(inventory)
    return inventory


def project_risks(project_inventory: dict[str, Any]) -> list[dict[str, str]]:
    risks: list[dict[str, str]] = []
    project_id = project_inventory["project"].get("projectId", "unknown")
    bindings = project_inventory.get("iam", {}).get("bindings", [])

    public_members = []
    owner_members = []
    for binding in bindings:
        role = binding.get("role", "")
        members = binding.get("members", [])
        if role == "roles/owner":
            owner_members.extend(members)
        public_members.extend([member for member in members if member in {"allUsers", "allAuthenticatedUsers"}])

    if len(owner_members) > 1:
        risks.append({"severity": "high", "title": "Multiple project owners", "detail": f"{project_id} has {len(owner_members)} owner members."})
    if public_members:
        risks.append({"severity": "critical", "title": "Public IAM member", "detail": f"{project_id} has public IAM members: {', '.join(sorted(set(public_members)))}."})
    if project_inventory.get("billing") and project_inventory["billing"].get("billingEnabled") is False:
        risks.append({"severity": "medium", "title": "Billing disabled", "detail": f"{project_id} has billing disabled."})
    hard_gaps = [gap for gap in project_inventory.get("gaps", []) if gap.get("kind") != "service_disabled"]
    if hard_gaps:
        risks.append({"severity": "medium", "title": "Incomplete audit", "detail": f"{project_id} had {len(hard_gaps)} inaccessible audit areas."})
    return risks


def collect(project_filter: list[str] | None) -> dict[str, Any]:
    if not shutil.which("gcloud"):
        raise SystemExit("gcloud was not found on PATH. Install the Google Cloud CLI first.")

    active_auth = run_gcloud(["auth", "list", "--filter=status:ACTIVE", "--format=json"])
    account = run_gcloud(["config", "get-value", "account"])
    project_result = run_gcloud(["projects", "list", "--format=json"])
    gaps: list[dict[str, str]] = []
    projects = list_or_empty(project_result, gaps, "projects list")

    if project_filter:
        wanted = set(project_filter)
        projects = [project for project in projects if project.get("projectId") in wanted]
        missing = sorted(wanted - {project.get("projectId") for project in projects})
        for project_id in missing:
            gaps.append({"area": f"{project_id}: project lookup", "error": "Project was not visible to the active gcloud account."})

    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "active_auth": active_auth.get("data") if active_auth["ok"] else [],
        "account": account.get("data") if account["ok"] else None,
        "gaps": gaps,
        "projects": [collect_project(project) for project in projects],
    }


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def resource_count(project: dict[str, Any], key: str) -> int:
    return len(project.get("resources", {}).get(key, []))


def render_html(report: dict[str, Any]) -> str:
    project_cards = []
    for item in report["projects"]:
        project = item["project"]
        risks = item["risks"]
        risk_html = "".join(f'<span class="badge {esc(r["severity"])}">{esc(r["severity"])}: {esc(r["title"])}</span>' for r in risks) or '<span class="badge ok">no obvious audit risks</span>'
        services = len(item.get("services", []))
        labels = project.get("labels") or {}
        label_html = " ".join(f"<span>{esc(k)}={esc(v)}</span>" for k, v in labels.items()) or "<span>none</span>"
        billing = item.get("billing") or {}
        billing_text = "enabled" if billing.get("billingEnabled") else ("disabled" if billing.get("billingEnabled") is False else "unknown")
        project_cards.append(
            f"""
            <section class="project">
              <header>
                <div>
                  <h2>{esc(project.get("projectId"))}</h2>
                  <p>{esc(project.get("name"))} · {esc(project.get("lifecycleState"))}</p>
                </div>
                <div class="riskline">{risk_html}</div>
              </header>
              <div class="meta">
                <div><strong>Billing</strong><span>{esc(billing_text)}</span></div>
                <div><strong>Enabled APIs</strong><span>{services}</span></div>
                <div><strong>Audit gaps</strong><span>{len([g for g in item.get("gaps", []) if g.get("kind") != "service_disabled"])}</span></div>
              </div>
              <div class="counts">
                <div>Cloud Run <b>{resource_count(item, "cloud_run")}</b></div>
                <div>Buckets <b>{resource_count(item, "storage_buckets")}</b></div>
                <div>Secrets <b>{resource_count(item, "secrets")}</b></div>
                <div>Cloud SQL <b>{resource_count(item, "sql_instances")}</b></div>
                <div>Compute <b>{resource_count(item, "compute_instances")}</b></div>
                <div>Artifacts <b>{resource_count(item, "artifact_repositories")}</b></div>
              </div>
              <details>
                <summary>Labels</summary>
                <div class="labels">{label_html}</div>
              </details>
              {render_resource_details(item)}
              {render_gap_details(item)}
            </section>
            """
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>G5 Manager Google Cloud Audit</title>
  <style>
    :root {{ color-scheme: light; --ink:#18212f; --muted:#5e6a7d; --line:#d9dee8; --bg:#f7f9fc; --panel:#fff; --blue:#2563eb; --red:#b42318; --amber:#a15c07; --green:#067647; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font:14px/1.45 system-ui,-apple-system,Segoe UI,sans-serif; color:var(--ink); background:var(--bg); }}
    main {{ max-width:1180px; margin:0 auto; padding:28px 18px 48px; }}
    h1 {{ margin:0 0 8px; font-size:28px; letter-spacing:0; }}
    h2 {{ margin:0; font-size:20px; }}
    h3 {{ margin:18px 0 8px; font-size:15px; }}
    p {{ margin:4px 0; color:var(--muted); }}
    .top {{ display:flex; justify-content:space-between; gap:16px; align-items:flex-end; margin-bottom:20px; }}
    .summary {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:18px 0; }}
    .summary div,.project {{ border:1px solid var(--line); background:var(--panel); border-radius:8px; }}
    .summary div {{ padding:14px; }}
    .summary strong {{ display:block; font-size:22px; }}
    .summary span {{ color:var(--muted); }}
    .project {{ padding:18px; margin:14px 0; }}
    .project header {{ display:flex; justify-content:space-between; gap:16px; align-items:flex-start; border-bottom:1px solid var(--line); padding-bottom:12px; }}
    .riskline {{ display:flex; flex-wrap:wrap; gap:6px; justify-content:flex-end; }}
    .badge {{ border-radius:999px; padding:4px 8px; font-size:12px; border:1px solid var(--line); white-space:nowrap; }}
    .critical,.high {{ color:var(--red); background:#fff4f2; border-color:#f3b5ad; }}
    .medium {{ color:var(--amber); background:#fff8eb; border-color:#f3cf99; }}
    .ok {{ color:var(--green); background:#ecfdf3; border-color:#a6f4c5; }}
    .meta,.counts {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin-top:12px; }}
    .counts {{ grid-template-columns:repeat(6,minmax(0,1fr)); }}
    .meta div,.counts div {{ border:1px solid var(--line); border-radius:6px; padding:10px; min-height:56px; }}
    .meta strong,.meta span,.counts b {{ display:block; }}
    .meta span,.counts div {{ color:var(--muted); }}
    .counts b {{ color:var(--ink); font-size:20px; }}
    details {{ margin-top:12px; }}
    summary {{ cursor:pointer; font-weight:600; }}
    .labels {{ display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; }}
    .labels span {{ background:#eef2f7; border-radius:999px; padding:4px 8px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:8px; border:1px solid var(--line); }}
    th,td {{ text-align:left; padding:8px; border-bottom:1px solid var(--line); vertical-align:top; overflow-wrap:anywhere; }}
    th {{ background:#f1f4f9; font-size:12px; color:#3f4a5c; }}
    @media (max-width: 760px) {{ .top,.project header {{ display:block; }} .summary,.meta,.counts {{ grid-template-columns:1fr 1fr; }} .riskline {{ justify-content:flex-start; margin-top:10px; }} }}
  </style>
</head>
<body>
<main>
  <div class="top">
    <div>
      <h1>G5 Manager Google Cloud Audit</h1>
      <p>Generated {esc(report.get("generated_at"))}</p>
      <p>Active account: {esc(report.get("account"))}</p>
    </div>
  </div>
  <section class="summary">
    <div><strong>{len(report["projects"])}</strong><span>visible projects</span></div>
    <div><strong>{sum(len(p.get("risks", [])) for p in report["projects"])}</strong><span>risk flags</span></div>
    <div><strong>{sum(len([g for g in p.get("gaps", []) if g.get("kind") != "service_disabled"]) for p in report["projects"]) + len(report.get("gaps", []))}</strong><span>audit gaps</span></div>
    <div><strong>{sum(len(p.get("services", [])) for p in report["projects"])}</strong><span>enabled APIs</span></div>
  </section>
  {''.join(project_cards) or '<p>No projects were visible to the active gcloud account.</p>'}
</main>
</body>
</html>
"""


def render_resource_details(item: dict[str, Any]) -> str:
    rows = []
    specs = [
        ("cloud_run", "Cloud Run", ("metadata.name", "metadata.namespace", "status.url")),
        ("storage_buckets", "Storage Buckets", ("name", "location", "storageClass")),
        ("secrets", "Secrets", ("name", "replication", "createTime")),
        ("sql_instances", "Cloud SQL", ("name", "databaseVersion", "region")),
        ("compute_instances", "Compute Instances", ("name", "zone", "machineType")),
        ("artifact_repositories", "Artifact Registry", ("name", "format", "location")),
    ]
    for key, title, fields in specs:
        resources = item.get("resources", {}).get(key, [])
        if not resources:
            continue
        table_rows = []
        for resource in resources:
            table_rows.append("<tr>" + "".join(f"<td>{esc(get_path(resource, field))}</td>" for field in fields) + "</tr>")
        rows.append(f"<h3>{esc(title)}</h3><table><thead><tr>{''.join(f'<th>{esc(field)}</th>' for field in fields)}</tr></thead><tbody>{''.join(table_rows)}</tbody></table>")
    return f"<details><summary>Resources</summary>{''.join(rows) or '<p>No listed resources in audited categories.</p>'}</details>"


def render_gap_details(item: dict[str, Any]) -> str:
    gaps = item.get("gaps", [])
    if not gaps:
        return ""
    hard_gaps = [gap for gap in gaps if gap.get("kind") != "service_disabled"]
    disabled = [gap for gap in gaps if gap.get("kind") == "service_disabled"]
    if not hard_gaps and disabled:
        return f"<details><summary>Disabled services checked</summary><p>{len(disabled)} product APIs were disabled, so those resource categories were skipped.</p></details>"
    rows = "".join(f"<tr><td>{esc(gap.get('area'))}</td><td>{esc(gap.get('error'))}</td></tr>" for gap in hard_gaps)
    return f"<details><summary>Audit gaps</summary><table><thead><tr><th>Area</th><th>Error</th></tr></thead><tbody>{rows}</tbody></table></details>"


def get_path(data: Any, path: str) -> Any:
    cur = data
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return ""
    if isinstance(cur, dict):
        return json.dumps(cur, sort_keys=True)
    if isinstance(cur, list):
        return ", ".join(str(x) for x in cur[:3])
    return cur


def render_notes(report: dict[str, Any]) -> str:
    lines = [
        "# G5 Manager Notes",
        "",
        f"- Generated: {report.get('generated_at')}",
        f"- Active account: {report.get('account')}",
        f"- Visible projects: {len(report.get('projects', []))}",
        "",
        "## Top Findings",
        "",
    ]
    findings = []
    for item in report.get("projects", []):
        project_id = item.get("project", {}).get("projectId")
        for risk in item.get("risks", []):
            findings.append(f"- `{risk.get('severity')}` `{project_id}`: {risk.get('title')} - {risk.get('detail')}")
    lines.extend(findings or ["- No obvious risks found in the audited categories."])
    lines.extend(["", "## Audit Gaps", ""])
    gaps = list(report.get("gaps", []))
    for item in report.get("projects", []):
        gaps.extend([gap for gap in item.get("gaps", []) if gap.get("kind") != "service_disabled"])
    lines.extend([f"- {gap.get('area')}: {gap.get('error')}" for gap in gaps] or ["- None."])
    lines.extend([
        "",
        "## Recommended Next Step",
        "",
        "Review the HTML dashboard, then fix authorization gaps before relying on the audit as complete.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a read-only Google Cloud audit dashboard.")
    parser.add_argument("--out", default="./g5-audit", help="Output directory.")
    parser.add_argument("--projects", help="Comma-separated project ids to audit.")
    args = parser.parse_args()

    project_filter = [p.strip() for p in args.projects.split(",") if p.strip()] if args.projects else None
    out = Path(args.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)

    report = collect(project_filter)
    (out / "g5-report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    (out / "g5-report.html").write_text(render_html(report), encoding="utf-8")
    (out / "g5-notes.md").write_text(render_notes(report), encoding="utf-8")

    print(f"Wrote {out / 'g5-report.html'}")
    print(f"Wrote {out / 'g5-report.json'}")
    print(f"Wrote {out / 'g5-notes.md'}")


if __name__ == "__main__":
    main()
