from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from zhenzhi_knowledge.core import (
    Bundle,
    KnowledgeError,
    PENDING_WORKSPACE_REF,
    create_project_launch,
    create_project_manager_action,
    create_project_task,
    create_source_material,
    load_object,
    rel,
    update_frontmatter_file,
    validate_bundle,
)
from zhenzhi_knowledge.project_init_profiles import (
    PROFILE_INITIAL_TASKS,
    WORKSPACE_DIRS,
    WORKSPACE_PROFILES,
    default_project_id,
    infer_workspace_profile,
    material_dir_for_profile,
    repo_name_from_url,
    source_mirror_dir_for_profile,
)


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a project workspace plus central knowledge-core records.")
    parser.add_argument("--root", default=str(ROOT), help="company_knowledge_core root")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--goal", default="")
    parser.add_argument("--source", default="project initialization script")
    parser.add_argument("--workspace-ref", default="")
    parser.add_argument(
        "--workspace-profile",
        choices=sorted(WORKSPACE_PROFILES),
        default="delivery",
        help="workspace directory template. development=new build project; delivery=product/dev/test delivery; operations=marketing/content/material; copyright=software copyright/material.",
    )
    parser.add_argument("--source-repo-url", default="", help="Git URL for source code used as reference.")
    parser.add_argument("--source-repo-path", default="", help="Local source mirror path. Keep it separate from material outputs.")
    parser.add_argument(
        "--clone-source-repo",
        action="store_true",
        help="Clone --source-repo-url into the profile source mirror when --source-repo-path is not provided.",
    )
    parser.add_argument(
        "--source-repo-dest",
        default="",
        help="Optional clone destination. Must stay outside company_knowledge_core and outside material output folders.",
    )
    parser.add_argument("--skip-initial-tasks", action="store_true", help="Do not generate the profile-based first task queue.")
    parser.add_argument("--allow-pending-workspace", action="store_true")
    parser.add_argument("--no-create-workspace", action="store_true")
    parser.add_argument("--source-file", action="append", default=[])
    parser.add_argument("--requester", default="")
    parser.add_argument("--skip-validate", action="store_true")
    return parser.parse_args()


def pm_intake_missing_fields(args: argparse.Namespace) -> list[str]:
    missing: list[str] = []
    if not args.name.strip():
        missing.append("--name")
    if not args.owner.strip():
        missing.append("--owner")
    if not args.workspace_ref.strip() and not args.allow_pending_workspace:
        missing.append("--workspace-ref")
    return missing


def prepare_workspace(workspace_ref: str, source_files: list[str], create_workspace: bool, profile: str) -> list[Path]:
    if workspace_ref == PENDING_WORKSPACE_REF:
        return []
    workspace = Path(workspace_ref).expanduser()
    if create_workspace:
        for item in WORKSPACE_PROFILES.get(profile, WORKSPACE_DIRS):
            (workspace / item).mkdir(parents=True, exist_ok=True)
    stored_files: list[Path] = []
    raw_dir = workspace / material_dir_for_profile(profile)
    for source in source_files:
        src = Path(source).expanduser()
        if not src.exists():
            raise KnowledgeError(f"source file does not exist: {src}")
        dst = raw_dir / src.name
        if create_workspace:
            raw_dir.mkdir(parents=True, exist_ok=True)
        if src.resolve() != dst.resolve():
            shutil.copy2(src, dst)
        stored_files.append(dst)
    return stored_files


def normalize_optional_path(value: str) -> str:
    if not value.strip():
        return ""
    return str(Path(value).expanduser())


def is_relative_to_path(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_workspace_boundary(workspace_ref: str, root: Path) -> None:
    if workspace_ref == PENDING_WORKSPACE_REF:
        return
    workspace = Path(workspace_ref).expanduser().resolve()
    central_root = root.resolve()
    if not ((central_root / "zhenzhi_knowledge").is_dir() and (central_root / "scripts" / "init_project.py").is_file()):
        return
    if workspace == central_root or is_relative_to_path(workspace, central_root):
        raise KnowledgeError(
            f"project workspace must not be inside company_knowledge_core: {workspace}. "
            "Create it as a separate folder, for example under ~/Documents/<project-id>."
        )


def git_remote_origin(path: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), "config", "--get", "remote.origin.url"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.stdout.strip()


def clone_source_repo_if_requested(
    *,
    workspace_ref: str,
    profile: str,
    project_id: str,
    source_repo_url: str,
    source_repo_path: str,
    source_repo_dest: str,
    clone_source_repo: bool,
    root: Path,
) -> str:
    if source_repo_path:
        return source_repo_path
    if not clone_source_repo:
        return ""
    if not source_repo_url:
        raise KnowledgeError("--clone-source-repo requires --source-repo-url")
    if workspace_ref == PENDING_WORKSPACE_REF:
        raise KnowledgeError("--clone-source-repo requires a confirmed --workspace-ref")
    workspace = Path(workspace_ref).expanduser()
    if source_repo_dest.strip():
        target = Path(source_repo_dest).expanduser()
    else:
        target = workspace / source_mirror_dir_for_profile(profile) / repo_name_from_url(source_repo_url, project_id)
    validate_workspace_boundary(str(target), root)
    target = target.resolve()
    if target.exists():
        if not target.is_dir():
            raise KnowledgeError(f"source repo clone target exists but is not a directory: {target}")
        if any(target.iterdir()):
            remote = git_remote_origin(target)
            if not remote:
                raise KnowledgeError(f"source repo clone target exists but is not a git repository: {target}")
            if remote != source_repo_url:
                raise KnowledgeError(
                    f"source repo clone target remote mismatch: {target} has {remote}, expected {source_repo_url}"
                )
            return str(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["git", "clone", source_repo_url, str(target)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()[-1:] or ["unknown git clone error"]
        raise KnowledgeError(f"source repo clone failed: {detail[0]}")
    return str(target)


def register_source_repo(
    bundle: Bundle,
    project_id: str,
    project_name: str,
    submitter: str,
    source_repo_url: str,
    source_repo_path: str,
) -> list[str]:
    if not source_repo_path and not source_repo_url:
        return []
    if source_repo_path:
        source_path = Path(source_repo_path).expanduser()
        if not source_path.exists():
            raise KnowledgeError(f"source repo path does not exist: {source_path}")
        material = create_source_material(
            bundle,
            title=f"{project_name} source mirror",
            source_ref=source_repo_url or str(source_path),
            project_id=project_id,
            submitter=submitter,
            material_type="git_repository",
            storage_ref=str(source_path),
            license_hint="source_reference",
            sensitivity="internal",
            extraction_tool="project_init_script",
            extraction_status="registered",
        )
        return [material["sourceRef"]]
    material = create_source_material(
        bundle,
        title=f"{project_name} source repository",
        source_ref=source_repo_url,
        project_id=project_id,
        submitter=submitter,
        material_type="git_repository",
        storage_ref=source_repo_url,
        license_hint="source_reference",
        sensitivity="internal",
        extraction_tool="project_init_script",
        extraction_status="registered",
    )
    return [material["sourceRef"]]


def create_initial_task_queue(
    bundle: Bundle,
    project_id: str,
    requester: str,
    workspace_profile: str,
    source_refs: list[str],
) -> list[str]:
    task_refs: list[str] = []
    for suffix, title, assignee, task_type, expected_output in PROFILE_INITIAL_TASKS.get(
        workspace_profile, PROFILE_INITIAL_TASKS["delivery"]
    ):
        task_path = create_project_task(
            bundle,
            title=title,
            project_id=project_id,
            requester=requester,
            assignee=assignee,
            task_type=task_type,
            task_id=f"project-init-{project_id}-{suffix}",
            priority="normal",
            source_material_refs=source_refs,
            expected_output=[expected_output],
            work_source_type="project_setup",
            requirement_refs=["PROJECT-INIT"],
            source_reason=(
                f"Project Manager generated a profile-based first task queue for workspaceProfile={workspace_profile}. "
                "This is a PM-confirmation queue; downstream agents must produce receiver review before formal execution."
            ),
        )
        task_refs.append(rel(task_path, bundle.root))
    return task_refs


def register_source_files(bundle: Bundle, project_id: str, submitter: str, stored_files: list[Path]) -> list[str]:
    source_refs: list[str] = []
    for stored_file in stored_files:
        material = create_source_material(
            bundle,
            title=stored_file.name,
            source_ref=str(stored_file),
            project_id=project_id,
            submitter=submitter,
            material_type=stored_file.suffix.lstrip(".") or "file",
            storage_ref=str(stored_file),
            license_hint="internal",
            sensitivity="internal",
            extraction_tool="project_init_script",
            extraction_status="registered",
        )
        source_refs.append(material["sourceRef"])
    return source_refs


def update_project_workspace_metadata(
    bundle: Bundle,
    project_ref: str,
    source_refs: list[str],
    workspace_profile: str,
    source_repo_url: str,
    source_repo_path: str,
) -> None:
    project_path = bundle.root / project_ref
    project = load_object(project_path)
    updates = {
        "workspaceProfile": workspace_profile,
        "workspaceMaterialPolicy": "workspace_keeps_materials_source_repo_is_reference_only",
        "updatedAt": project.get("updatedAt", ""),
    }
    if source_refs:
        updates["sourceMaterialRefs"] = source_refs
    if source_repo_url:
        updates["sourceRepoUrl"] = source_repo_url
    if source_repo_path:
        updates["sourceRepoRef"] = source_repo_path
    update_frontmatter_file(project_path, updates)


def record_project_manager_initialization(
    bundle: Bundle,
    project_id: str,
    project_name: str,
    result: dict[str, str],
    source_refs: list[str],
    initial_task_refs: list[str],
    workspace_profile: str,
    source_repo_path: str,
    source_repo_url: str,
) -> None:
    source_note = source_repo_path or source_repo_url or "none"
    summary = (
        f"项目经理完成 {project_name} 项目初始化接管：workspaceProfile={workspace_profile}，"
        f"sourceRepoRef={source_note}；项目工作区承载交付/运营/软著材料，源码镜像只作为参考源。"
    )
    create_project_manager_action(
        bundle,
        project_id=project_id,
        actor="agent.company.project-manager",
        intent="dispatch",
        current_state="project_registered",
        allowed_transition="initialize_project_workspace",
        exit_state="dispatched",
        summary=summary,
        task_id=f"project-init-{project_id}",
        requirement_refs=["PROJECT-INIT"],
        records_written=[result["projectRef"], result["launchRef"], result["initTaskRef"], *initial_task_refs],
        evidence_refs=source_refs,
        next_action="Project Manager Agent confirms workspace boundary, source refs, and the profile-based first task queue before assigning downstream execution.",
    )


def workspace_source_rule(source_repo_note: str) -> str:
    if source_repo_note == "none":
        return "No source repository was registered during initialization."
    return (
        "Source code is a reference mirror. Do not write project materials into it. "
        "When source code must be refreshed, update only the source mirror, then keep soft-copyright, operations, screenshots, and delivery materials in this workspace."
    )


def write_workspace_entrypoint(
    workspace_ref: str,
    project_id: str,
    project_name: str,
    root: Path,
    source_refs: list[str],
    *,
    profile: str,
    source_repo_url: str = "",
    source_repo_path: str = "",
) -> None:
    if workspace_ref == PENDING_WORKSPACE_REF:
        return
    workspace = Path(workspace_ref).expanduser()
    source_repo_note = source_repo_path or source_repo_url or "none"
    agent_entry = "\n".join(
        [
            "---",
            f"projectId: {project_id}",
            f"projectName: {project_name}",
            f"workspaceProfile: {profile}",
            f"centralRoot: {root}",
            f"centralProjectRef: projects/{project_id}/project.md",
            f"taskIndexRef: projects/{project_id}/tasks/index.md",
            f"sourceRepoRef: {source_repo_note}",
            *(f"sourceMaterialRef: {item}" for item in source_refs[:1]),
            "---",
            "",
            f"# {project_name} Agent Entry",
            "",
            "You are working in the entity project workspace, not the central knowledge repository.",
            "",
            "## Start",
            "",
            "When the user asks to start or continue this project, the Project Manager Agent must take control first. Do not jump directly to product, architecture, development, or testing.",
            "",
            "First read the central project context:",
            "",
            "```bash",
            f"cd {root}",
            "python3 -m zhenzhi_knowledge.cli validate",
            "```",
            "",
            "Then read:",
            "",
            f"- `projects/{project_id}/project.md`",
            f"- `projects/{project_id}/tasks/index.md`",
            f"- `projects/{project_id}/AGENTS.md`",
            "",
            "## Workspace Boundary",
            "",
            f"- workspaceProfile: `{profile}`",
            f"- sourceRepoRef: `{source_repo_note}`",
            f"- rule: {workspace_source_rule(source_repo_note)}",
            "",
            "The user may keep working from this entity workspace. The Project Manager Agent coordinates role handoff. Only compact project records, task flow, TaskResult summaries, evidence refs, and AuditLog are written back to the central repository. Raw artifacts, long logs, screenshots, and PRD files stay in this workspace or external storage and are referenced through storageRef.",
            "",
        ]
    )
    start_here = "\n".join(
        [
            f"# {project_name} 怎么开始",
            "",
            "在这个项目目录里直接对 Codex 说：",
            "",
            "```txt",
            "启动这个项目，让项目经理按体系接管并调度第一棒。",
            "```",
            "",
            "Codex 应该读取本目录的 `AGENTS.md`，再到中枢项目记录继续：",
            "",
            "```txt",
            f"{root}/projects/{project_id}/",
            "```",
            "",
            f"工作区模板：`{profile}`。",
            f"源码/资料引用：`{source_repo_note}`。",
            "",
            "项目经理 Agent 先确认 workspace、SourceMaterial、任务队列和阻塞，再调度第一个业务角色。实体材料、长日志、截图、PRD 原文留在本目录或外部存储；中枢只写精简项目记录、任务流、TaskResult 摘要、证据引用和审计。",
            "",
            "不要把软著、运营、截图、说明书或过程材料写入源码镜像。源码镜像只用于读取和按需更新。",
            "",
        ]
    )
    (workspace / "AGENTS.md").write_text(agent_entry, encoding="utf-8")
    (workspace / "START_HERE.md").write_text(start_here, encoding="utf-8")


def confirmed_workspace_ref(args: argparse.Namespace) -> tuple[str, int]:
    workspace_ref = args.workspace_ref.strip()
    if workspace_ref:
        return workspace_ref, 0
    if args.allow_pending_workspace:
        return PENDING_WORKSPACE_REF, 0
    print(
        "workspace path is not confirmed. Pass --workspace-ref <absolute path> after user confirmation, "
        "or pass --allow-pending-workspace to create central records with workspaceRef=pending_confirmation.",
        file=sys.stderr,
    )
    return "", 2


def initialize_project(args: argparse.Namespace) -> int:
    workspace_ref, status = confirmed_workspace_ref(args)
    if status:
        return status
    bundle = Bundle(Path(args.root).resolve())
    submitter = args.requester or args.owner
    source_repo_path = normalize_optional_path(args.source_repo_path)
    source_repo_url = args.source_repo_url.strip()
    try:
        validate_workspace_boundary(workspace_ref, bundle.root)
        stored_files = prepare_workspace(workspace_ref, args.source_file, not args.no_create_workspace, args.workspace_profile)
        source_repo_path = clone_source_repo_if_requested(
            workspace_ref=workspace_ref,
            profile=args.workspace_profile,
            project_id=args.project_id,
            source_repo_url=source_repo_url,
            source_repo_path=source_repo_path,
            source_repo_dest=args.source_repo_dest,
            clone_source_repo=args.clone_source_repo,
            root=bundle.root,
        )
        result = create_project_launch(
            bundle,
            project_name=args.name,
            owner=args.owner,
            goal=args.goal,
            source=args.source,
            repo_url=source_repo_url,
            requester=submitter,
            project_id=args.project_id,
            workspace_ref=workspace_ref,
        )
        source_refs = register_source_repo(bundle, args.project_id, args.name, submitter, source_repo_url, source_repo_path)
        source_refs.extend(register_source_files(bundle, args.project_id, submitter, stored_files))
        update_project_workspace_metadata(bundle, result["projectRef"], source_refs, args.workspace_profile, source_repo_url, source_repo_path)
        initial_task_refs: list[str] = []
        if not args.skip_initial_tasks:
            initial_task_refs = create_initial_task_queue(bundle, args.project_id, submitter, args.workspace_profile, source_refs)
        record_project_manager_initialization(
            bundle,
            args.project_id,
            args.name,
            result,
            source_refs,
            initial_task_refs,
            args.workspace_profile,
            source_repo_path,
            source_repo_url,
        )
        write_workspace_entrypoint(
            workspace_ref,
            args.project_id,
            args.name,
            bundle.root,
            source_refs,
            profile=args.workspace_profile,
            source_repo_url=source_repo_url,
            source_repo_path=source_repo_path,
        )
        if not args.skip_validate:
            problems = validate_bundle(bundle)
            if problems:
                for problem in problems:
                    print(problem, file=sys.stderr)
                return 1
        print(result["projectRef"])
        if workspace_ref != PENDING_WORKSPACE_REF:
            print(workspace_ref)
        for source_ref in source_refs:
            print(source_ref)
        for task_ref in initial_task_refs:
            print(task_ref)
        return 0
    except KnowledgeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


def main() -> int:
    return initialize_project(parse_args())
