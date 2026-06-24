#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from zhenzhi_knowledge.project_init import (  # noqa: E402
    WORKSPACE_PROFILES,
    default_project_id,
    infer_workspace_profile,
    initialize_project,
    pm_intake_missing_fields,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Project Manager intake entry for initializing a project from a short user request."
    )
    parser.add_argument("--root", default=str(ROOT), help="company_knowledge_core root")
    parser.add_argument("--request", default="", help="Natural-language project initialization request.")
    parser.add_argument("--project-id", default="")
    parser.add_argument("--name", default="")
    parser.add_argument("--owner", default="")
    parser.add_argument("--goal", default="")
    parser.add_argument("--source", default="project manager intake")
    parser.add_argument("--workspace-ref", default="")
    parser.add_argument("--workspace-profile", choices=["auto", *sorted(WORKSPACE_PROFILES)], default="auto")
    parser.add_argument("--source-repo-url", default="")
    parser.add_argument("--source-repo-path", default="")
    parser.add_argument("--source-repo-dest", default="")
    parser.add_argument("--clone-source-repo", action="store_true")
    parser.add_argument("--allow-pending-workspace", action="store_true")
    parser.add_argument("--no-create-workspace", action="store_true")
    parser.add_argument("--source-file", action="append", default=[])
    parser.add_argument("--requester", default="")
    parser.add_argument("--skip-validate", action="store_true")
    parser.add_argument("--skip-initial-tasks", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    explicit_profile = "" if args.workspace_profile == "auto" else args.workspace_profile
    args.workspace_profile = infer_workspace_profile(args.request, explicit_profile)
    missing = pm_intake_missing_fields(args)
    if missing:
        print("project intake is missing required fields: " + ", ".join(missing), file=sys.stderr)
        print(
            "No project was created. Provide the missing fields, then rerun this Project Manager intake command.",
            file=sys.stderr,
        )
        return 2
    if not args.project_id.strip():
        args.project_id = default_project_id(args.name, args.source_repo_url)
    if not args.goal.strip():
        args.goal = args.request.strip() or f"Initialize {args.name}"
    return initialize_project(args)


if __name__ == "__main__":
    raise SystemExit(main())
