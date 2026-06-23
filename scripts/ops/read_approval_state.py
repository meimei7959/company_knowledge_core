#!/usr/bin/env python3
"""Read-only approval diagnostics for the Agent Hub Feishu flow.

This script is intentionally narrow: it only scans local bundle files and prints
summaries. It must not mutate approval requests, audit logs, project files, or
notification state. It is safe to run through SSH from a local Agent Runner.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_ROOT_CANDIDATES = [
    Path.cwd(),
    Path("/knowledge"),
    Path("/opt/projects/company_knowledge_core/repo"),
    Path("/opt/projects/company_knowledge_core/data"),
]


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def first_existing_root(explicit_root: str | None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    for root in DEFAULT_ROOT_CANDIDATES:
        if (root / ".zhenzhi").exists() or (root / "knowledge").exists():
            return root
    return Path.cwd()


def safe_tail(value: str, keep: int = 8) -> str:
    text = str(value or "")
    if not text:
        return ""
    return text if len(text) <= keep else text[-keep:]


def approval_requests(root: Path, project: str, limit: int) -> list[dict[str, Any]]:
    directory = root / ".zhenzhi" / "approval-requests"
    if not directory.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        item = read_json(path)
        if not item:
            continue
        if project and project not in {str(item.get("projectId", "")), str(item.get("projectName", ""))}:
            continue
        rows.append(
            {
                "file": path.name,
                "projectId": item.get("projectId", ""),
                "projectName": item.get("projectName", ""),
                "approvalType": item.get("approvalType", ""),
                "approvalCodeTail": safe_tail(str(item.get("approvalCode", ""))),
                "instanceCode": item.get("instanceCode", ""),
                "requestedStatus": item.get("requestedStatus", ""),
                "finalStatus": item.get("finalStatus", "") or "pending",
                "externalStatus": item.get("externalStatus", ""),
                "targetRef": item.get("targetRef", ""),
                "hasSubmitter": bool(item.get("submitterOpenId")),
                "owner": item.get("ownerName") or safe_tail(str(item.get("ownerOpenId") or item.get("ownerUserId") or "")),
                "updatedAt": item.get("reconciledAt") or item.get("createdAt") or "",
            }
        )
        if len(rows) >= limit:
            break
    return rows


def parse_frontmatter_value(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def audit_rows(root: Path, project: str, limit: int) -> list[dict[str, str]]:
    directory = root / "knowledge" / "audit"
    if not directory.exists():
        return []
    rows: list[dict[str, str]] = []
    for path in sorted(directory.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "feishu.approval" not in text:
            continue
        if project and project not in text:
            continue
        rows.append(
            {
                "file": path.name,
                "action": parse_frontmatter_value(text, "action"),
                "after": parse_frontmatter_value(text, "after"),
                "policyResult": parse_frontmatter_value(text, "policyResult"),
                "targetRef": parse_frontmatter_value(text, "targetRef"),
                "detailsSnippet": compact(text.split("---", 2)[-1], 220),
            }
        )
        if len(rows) >= limit:
            break
    return rows


def compact(text: str, limit: int) -> str:
    normalized = " ".join(str(text or "").split())
    return normalized if len(normalized) <= limit else normalized[: limit - 3] + "..."


def project_state(root: Path, project: str) -> dict[str, Any]:
    if not project:
        return {}
    candidates = [
        root / "projects" / project / "project.md",
    ]
    for base in root.glob("projects/*/project.md"):
        candidates.append(base)
    for path in candidates:
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        project_id = parse_frontmatter_value(text, "projectId")
        title = parse_frontmatter_value(text, "title")
        if project not in {project_id, title, path.parent.name}:
            continue
        return {
            "file": str(path.relative_to(root)),
            "projectId": project_id,
            "title": title,
            "status": parse_frontmatter_value(text, "status"),
            "approvalStatus": parse_frontmatter_value(text, "approvalStatus"),
            "reviewedAt": parse_frontmatter_value(text, "reviewedAt"),
            "humanOwner": parse_frontmatter_value(text, "humanOwner"),
        }
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Read Feishu approval diagnostics without mutating state.")
    parser.add_argument("--root", default="", help="Bundle root. Defaults to cwd, /knowledge, or deployed repo paths.")
    parser.add_argument("--project", default="", help="Project id or project name filter.")
    parser.add_argument("--limit", type=int, default=8, help="Maximum approval/audit rows.")
    args = parser.parse_args()

    root = first_existing_root(args.root or None)
    output = {
        "ok": True,
        "mode": "read_only",
        "root": str(root),
        "project": args.project,
        "projectState": project_state(root, args.project),
        "approvalRequests": approval_requests(root, args.project, args.limit),
        "approvalAudits": audit_rows(root, args.project, args.limit),
        "nextCheck": [
            "approvalRequests[].finalStatus should become verified/approved/rejected after callback or reconciliation.",
            "approvalAudits should include feishu.approval.callback or feishu.approval.reconciled.",
            "If finalStatus is set but no notification arrived, inspect feishu.approval.notify_failed audits.",
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
