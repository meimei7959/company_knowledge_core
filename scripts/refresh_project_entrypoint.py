#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import NamedTuple

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


class RefreshOutcome(NamedTuple):
    project_id: str
    status: str
    workspace_ref: str
    project_ref: str
    message: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh AGENTS.md and START_HERE.md for an existing project workspace.")
    parser.add_argument("--root", default=str(ROOT), help="company_knowledge_core root")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--project-id")
    mode.add_argument("--all", action="store_true", help="Refresh every registered project with a confirmed local workspaceRef.")
    parser.add_argument("--workspace-ref", default="", help="Override existing Project.workspaceRef.")
    parser.add_argument("--workspace-profile", choices=sorted(WORKSPACE_PROFILES), default="")
    parser.add_argument("--source-repo-url", default="")
    parser.add_argument("--source-repo-path", default="")
    parser.add_argument("--dry-run", action="store_true", help="Report projects that would be refreshed without writing files.")
    parser.add_argument("--skip-validate", action="store_true")
    args = parser.parse_args()
    if args.all and any([args.workspace_ref, args.workspace_profile, args.source_repo_url, args.source_repo_path]):
        parser.error("--all uses each Project record as source of truth; do not pass per-project overrides")
    return args


def _first_related_repo(project: dict) -> str:
    repos = as_list(project.get("relatedRepos"))
    return str(repos[0]) if repos else ""


def _project_id(project: dict, fallback: str) -> str:
    return str(project.get("projectId") or fallback)


def _source_repo_path(project: dict, override: str = "") -> str:
    return override.strip() or str(project.get("sourceRepoRef") or project.get("sourceRepoPath") or "")


def _local_workspace_path(bundle: Bundle, workspace_ref: str) -> Path | None:
    if workspace_ref.startswith(("workspace://", "git@", "http://", "https://")):
        return None
    path = Path(workspace_ref).expanduser()
    if not path.is_absolute():
        path = bundle.root / path
    return path.resolve()


def _is_inside_path(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _refresh_project(
    bundle: Bundle,
    project_path: Path,
    *,
    requested_project_id: str = "",
    workspace_ref_override: str = "",
    workspace_profile_override: str = "",
    source_repo_url_override: str = "",
    source_repo_path_override: str = "",
    dry_run: bool = False,
) -> RefreshOutcome:
    project = load_object(project_path)
    pid = _project_id(project, requested_project_id or project_path.parent.name)
    workspace_ref = workspace_ref_override.strip() or str(project.get("workspaceRef") or "")
    project_ref = str(project_path.relative_to(bundle.root))
    if not workspace_ref or workspace_ref == PENDING_WORKSPACE_REF:
        raise KnowledgeError("project workspaceRef is not confirmed; pass --workspace-ref before refreshing entrypoint")

    profile = workspace_profile_override or str(project.get("workspaceProfile") or "delivery")
    source_repo_url = source_repo_url_override.strip() or str(project.get("sourceRepoUrl") or _first_related_repo(project))
    source_repo_path = _source_repo_path(project, source_repo_path_override)
    source_refs = as_list(project.get("sourceMaterialRefs"))
    if not dry_run:
        write_workspace_entrypoint(
            workspace_ref,
            pid,
            str(project.get("title") or pid),
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
            project_id=pid,
            actor="agent.company.project-manager",
            intent="status_query",
            current_state="workspace_entrypoint_existing",
            allowed_transition="refresh_existing_project_entrypoint",
            exit_state="waiting_acceptance",
            summary="项目经理刷新已有项目入口规则，使进行中的项目可上报体系问题和可复用 Skill 缺口到中枢。",
            task_id=f"project-entrypoint-refresh-{pid}",
            requirement_refs=["PROJECT-INIT"],
            records_written=[],
            evidence_refs=[],
            next_action="Project Agent reads refreshed AGENTS.md/START_HERE.md before reporting system issues or skill gaps.",
        )
    return RefreshOutcome(pid, "refreshed", workspace_ref, project_ref)


def _refreshable_project_paths(bundle: Bundle) -> list[Path]:
    projects_dir = bundle.root / "projects"
    return sorted(projects_dir.glob("*/project.md"))


def _batch_outcome(bundle: Bundle, project_path: Path, *, dry_run: bool) -> RefreshOutcome:
    project = load_object(project_path)
    pid = _project_id(project, project_path.parent.name)
    project_ref = str(project_path.relative_to(bundle.root))
    workspace_ref = str(project.get("workspaceRef") or "").strip()
    if not workspace_ref:
        return RefreshOutcome(pid, "skipped", workspace_ref, project_ref, "workspaceRef missing")
    if workspace_ref == PENDING_WORKSPACE_REF:
        return RefreshOutcome(pid, "skipped", workspace_ref, project_ref, "workspaceRef pending_confirmation")
    workspace_path = _local_workspace_path(bundle, workspace_ref)
    if workspace_path is None:
        return RefreshOutcome(pid, "skipped", workspace_ref, project_ref, "workspaceRef is not a local filesystem path")
    if _is_inside_path(workspace_path, bundle.root):
        return RefreshOutcome(pid, "skipped", workspace_ref, project_ref, "workspaceRef points inside central repository")
    if not workspace_path.exists():
        return RefreshOutcome(pid, "skipped", workspace_ref, project_ref, f"workspace path does not exist: {workspace_path}")
    try:
        return _refresh_project(bundle, project_path, workspace_ref_override=str(workspace_path), dry_run=dry_run)
    except Exception as exc:  # noqa: BLE001 - batch mode must finish and summarize every project.
        return RefreshOutcome(pid, "failed", workspace_ref, project_ref, str(exc))


def _print_summary(outcomes: list[RefreshOutcome], *, dry_run: bool) -> None:
    refreshed = [item for item in outcomes if item.status == "refreshed"]
    skipped = [item for item in outcomes if item.status == "skipped"]
    failed = [item for item in outcomes if item.status == "failed"]
    if dry_run:
        print("dry-run: no files written")
        print("would refresh:")
    else:
        print("refreshed:")
    for item in refreshed:
        suffix = " (dry-run)" if dry_run else ""
        print(f"  - {item.project_id}: {item.workspace_ref} [{item.project_ref}]{suffix}")
    print("skipped:")
    for item in skipped:
        print(f"  - {item.project_id}: {item.message} [{item.project_ref}]")
    print("failed:")
    for item in failed:
        print(f"  - {item.project_id}: {item.message} [{item.project_ref}]")
    refreshed_count = 0 if dry_run else len(refreshed)
    would_refresh_count = len(refreshed) if dry_run else 0
    print(
        "summary: "
        f"refreshed={refreshed_count} "
        f"would_refresh={would_refresh_count} "
        f"skipped={len(skipped)} "
        f"failed={len(failed)}"
    )


def _validate(bundle: Bundle) -> int:
    problems = validate_bundle(bundle)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    return 0


def main() -> int:
    args = parse_args()
    bundle = Bundle(Path(args.root).expanduser().resolve())
    if args.all:
        outcomes = [_batch_outcome(bundle, path, dry_run=args.dry_run) for path in _refreshable_project_paths(bundle)]
        _print_summary(outcomes, dry_run=args.dry_run)
        validate_status = 0 if args.skip_validate else _validate(bundle)
        return 1 if [item for item in outcomes if item.status == "failed"] or validate_status else 0
    try:
        project_path = find_project(bundle, args.project_id)
        outcome = _refresh_project(
            bundle,
            project_path,
            requested_project_id=args.project_id,
            workspace_ref_override=args.workspace_ref,
            workspace_profile_override=args.workspace_profile,
            source_repo_url_override=args.source_repo_url,
            source_repo_path_override=args.source_repo_path,
            dry_run=args.dry_run,
        )
        if not args.skip_validate:
            validate_status = _validate(bundle)
            if validate_status:
                return validate_status
        print(outcome.workspace_ref)
        print(outcome.project_ref)
        return 0
    except (KnowledgeError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
