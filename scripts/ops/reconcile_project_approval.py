#!/usr/bin/env python3
"""Fixed Feishu project approval reconciliation command.

Use this instead of ad-hoc `python -c` snippets from Agent Runner sessions.
The script has a narrow purpose:

1. Find a recorded project approval request by project or instance code.
2. Query Feishu approval status through the existing production code path.
3. Update local approval/project state when Feishu reports a final status.
4. Send the normal submitter and project-owner notification cards.

It does not accept arbitrary Python and does not expose secrets.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from zhenzhi_knowledge.core import Bundle, KnowledgeError, create_audit_log  # noqa: E402
from zhenzhi_knowledge.feishu import (  # noqa: E402
    approval_request_dir,
    load_feishu_settings,
    notify_approval_result,
    reconcile_approval_request_if_needed,
)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def find_request(bundle: Bundle, project: str, instance_code: str) -> tuple[Path, dict[str, Any]]:
    directory = approval_request_dir(bundle)
    if not directory.exists():
        raise KnowledgeError(f"approval request directory not found: {directory}")

    candidates = sorted(directory.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    for path in candidates:
        item = read_json(path)
        if not item:
            continue
        if instance_code and instance_code in {str(item.get("instanceCode", "")), path.stem}:
            return path, item
        if project and project in {str(item.get("projectId", "")), str(item.get("projectName", ""))}:
            return path, item

    target = f"instance-code={instance_code}" if instance_code else f"project={project}"
    raise KnowledgeError(f"approval request not found for {target}")


def compact_request(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "projectId": item.get("projectId", ""),
        "projectName": item.get("projectName", ""),
        "approvalType": item.get("approvalType", ""),
        "instanceCode": item.get("instanceCode", ""),
        "requestedStatus": item.get("requestedStatus", ""),
        "finalStatus": item.get("finalStatus", "") or "pending",
        "externalStatus": item.get("externalStatus", ""),
        "targetRef": item.get("targetRef", ""),
        "hasSubmitter": bool(item.get("submitterOpenId")),
        "hasOwner": bool(item.get("ownerOpenId") or item.get("ownerUserId") or item.get("ownerName")),
        "reconciledAt": item.get("reconciledAt", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile a Feishu project approval request through a fixed safe command.")
    parser.add_argument("--root", default=".", help="Knowledge bundle root. On server usually /knowledge or repo mounted root.")
    parser.add_argument("--project", default="", help="Project id or project name.")
    parser.add_argument("--instance-code", default="", help="Feishu approval instance code.")
    parser.add_argument("--renotify-final", action="store_true", help="If request is already final, resend submitter/owner notification cards.")
    args = parser.parse_args()

    if not args.project and not args.instance_code:
        raise SystemExit("error: provide --project or --instance-code")

    bundle = Bundle(Path(args.root).expanduser().resolve())
    settings = load_feishu_settings()
    request_path, request = find_request(bundle, args.project, args.instance_code)
    before = compact_request(request)

    if request.get("approvalType") != "project_init":
        raise SystemExit(f"error: only project_init approvals are supported, got {request.get('approvalType')}")

    if request.get("finalStatus"):
        updated = request
        action = "renotify_final" if args.renotify_final else "already_final"
        if args.renotify_final:
            status = str(updated.get("finalStatus") or "")
            notify_approval_result(bundle, settings, updated, status != "rejected", str(updated.get("instanceCode") or request_path.stem), status)
    else:
        updated = reconcile_approval_request_if_needed(bundle, settings, request)
        action = "reconciled" if updated.get("finalStatus") else "not_final"

    create_audit_log(
        bundle,
        "ops.reconcile_project_approval",
        "feishu.approval.ops_reconcile",
        str(updated.get("targetRef") or updated.get("instanceCode") or request_path.name),
        after=str(updated.get("finalStatus") or "pending"),
        policy_result=str(updated.get("approvalType") or ""),
        details=f"action: {action}\nrequestFile: {request_path.name}",
    )

    print(
        json.dumps(
            {
                "ok": True,
                "action": action,
                "requestFile": str(request_path.relative_to(bundle.root)),
                "before": before,
                "after": compact_request(updated),
                "notificationAttempted": bool(args.renotify_final or (not before.get("finalStatus") and updated.get("finalStatus"))),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
