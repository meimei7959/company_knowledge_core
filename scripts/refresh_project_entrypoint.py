#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from zhenzhi_knowledge.core import (  # noqa: E402
    Bundle,
    KnowledgeError,
    PENDING_WORKSPACE_REF,
    as_list,
    create_project_manager_action,
    find_project,
    load_object,
    update_frontmatter_file,
    validate_bundle,
)
from zhenzhi_knowledge.project_init import write_workspace_entrypoint  # noqa: E402
from zhenzhi_knowledge.project_init_profiles import WORKSPACE_PROFILES  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh AGENTS.md and START_HERE.md for an existing project workspace.")
    parser.add_argument("--root", default=str(ROOT), help="company_knowledge_core root")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--workspace-ref", default="", help="Override existing Project.workspaceRef.")
    parser.add_argument("--workspace-profile", choices=sorted(WORKSPACE_PROFILES), default="")
    parser.add_argument("--source-repo-url", default="")
    parser.add_argument("--source-repo-path", default="")
    parser.add_argument("--skip-validate", action="store_true")
    return parser.parse_args()


def _first_related_repo(project: dict) -> str:
    repos = as_list(project.get("relatedRepos"))
    return str(repos[0]) if repos else ""


def main() -> int:
    args = parse_args()
    bundle = Bundle(Path(args.root).expanduser().resolve())
    try:
        project_path = find_project(bundle, args.project_id)
        project = load_object(project_path)
        workspace_ref = args.workspace_ref.strip() or str(project.get("workspaceRef") or "")
        if not workspace_ref or workspace_ref == PENDING_WORKSPACE_REF:
            raise KnowledgeError("project workspaceRef is not confirmed; pass --workspace-ref before refreshing entrypoint")
        profile = args.workspace_profile or str(project.get("workspaceProfile") or "delivery")
        source_repo_url = args.source_repo_url.strip() or str(project.get("sourceRepoUrl") or _first_related_repo(project))
        source_repo_path = args.source_repo_path.strip() or str(project.get("sourceRepoRef") or "")
        source_refs = as_list(project.get("sourceMaterialRefs"))
        write_workspace_entrypoint(
            workspace_ref,
            str(project.get("projectId") or args.project_id),
            str(project.get("title") or args.project_id),
            bundle.root,
            source_refs,
            profile=profile,
            source_repo_url=source_repo_url,
            source_repo_path=source_repo_path,
        )
        updates = {"workspaceProfile": profile, "updatedAt": str(project.get("updatedAt") or "")}
        if source_repo_url:
            updates["sourceRepoUrl"] = source_repo_url
        if source_repo_path:
            updates["sourceRepoRef"] = source_repo_path
        update_frontmatter_file(project_path, updates)
        create_project_manager_action(
            bundle,
            project_id=str(project.get("projectId") or args.project_id),
            actor="agent.company.project-manager",
            intent="status_query",
            current_state="workspace_entrypoint_existing",
            allowed_transition="refresh_existing_project_entrypoint",
            exit_state="waiting_acceptance",
            summary="项目经理刷新已有项目入口规则，使进行中的项目可上报体系问题和可复用 Skill 缺口到中枢。",
            task_id=f"project-entrypoint-refresh-{args.project_id}",
            requirement_refs=["PROJECT-INIT"],
            records_written=[],
            evidence_refs=[],
            next_action="Project Agent reads refreshed AGENTS.md/START_HERE.md before reporting system issues or skill gaps.",
        )
        if not args.skip_validate:
            problems = validate_bundle(bundle)
            if problems:
                for problem in problems:
                    print(problem, file=sys.stderr)
                return 1
        print(workspace_ref)
        print(project_path.relative_to(bundle.root))
        return 0
    except KnowledgeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
