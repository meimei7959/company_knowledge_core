#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from zhenzhi_knowledge.core import (  # noqa: E402
    Bundle,
    KnowledgeError,
    PENDING_WORKSPACE_REF,
    create_project_launch,
    create_source_material,
    load_object,
    rel,
    update_frontmatter_file,
    validate_bundle,
)


WORKSPACE_DIRS = [
    "00_原始资料",
    "01_产品需求",
    "02_架构方案",
    "03_研发实现",
    "04_测试验收",
    "05_运营上线",
    "99_项目管理",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a project workspace plus central knowledge-core records.")
    parser.add_argument("--root", default=str(ROOT), help="company_knowledge_core root")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--goal", default="")
    parser.add_argument("--source", default="project initialization script")
    parser.add_argument("--workspace-ref", default="")
    parser.add_argument("--allow-pending-workspace", action="store_true")
    parser.add_argument("--no-create-workspace", action="store_true")
    parser.add_argument("--source-file", action="append", default=[])
    parser.add_argument("--requester", default="")
    parser.add_argument("--skip-validate", action="store_true")
    return parser.parse_args()


def prepare_workspace(workspace_ref: str, source_files: list[str], create_workspace: bool) -> list[Path]:
    if workspace_ref == PENDING_WORKSPACE_REF:
        return []
    workspace = Path(workspace_ref).expanduser()
    if create_workspace:
        for item in WORKSPACE_DIRS:
            (workspace / item).mkdir(parents=True, exist_ok=True)
    stored_files: list[Path] = []
    raw_dir = workspace / "00_原始资料"
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


def write_workspace_entrypoint(workspace_ref: str, project_id: str, project_name: str, root: Path, source_refs: list[str]) -> None:
    if workspace_ref == PENDING_WORKSPACE_REF:
        return
    workspace = Path(workspace_ref).expanduser()
    agent_entry = "\n".join(
        [
            "---",
            f"projectId: {project_id}",
            f"projectName: {project_name}",
            f"centralRoot: {root}",
            f"centralProjectRef: projects/{project_id}/project.md",
            f"taskIndexRef: projects/{project_id}/tasks/index.md",
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
            "项目经理 Agent 先确认 workspace、SourceMaterial、任务队列和阻塞，再调度第一个业务角色。实体材料、长日志、截图、PRD 原文留在本目录或外部存储；中枢只写精简项目记录、任务流、TaskResult 摘要、证据引用和审计。",
            "",
        ]
    )
    (workspace / "AGENTS.md").write_text(agent_entry, encoding="utf-8")
    (workspace / "START_HERE.md").write_text(start_here, encoding="utf-8")


def main() -> int:
    args = parse_args()
    workspace_ref = args.workspace_ref.strip()
    if not workspace_ref:
        if not args.allow_pending_workspace:
            print(
                "workspace path is not confirmed. Pass --workspace-ref <absolute path> after user confirmation, "
                "or pass --allow-pending-workspace to create central records with workspaceRef=pending_confirmation.",
                file=sys.stderr,
            )
            return 2
        workspace_ref = PENDING_WORKSPACE_REF

    bundle = Bundle(Path(args.root).resolve())
    try:
        stored_files = prepare_workspace(workspace_ref, args.source_file, not args.no_create_workspace)
        result = create_project_launch(
            bundle,
            project_name=args.name,
            owner=args.owner,
            goal=args.goal,
            source=args.source,
            requester=args.requester or args.owner,
            project_id=args.project_id,
            workspace_ref=workspace_ref,
        )
        source_refs: list[str] = []
        for stored_file in stored_files:
            material = create_source_material(
                bundle,
                title=stored_file.name,
                source_ref=str(stored_file),
                project_id=args.project_id,
                submitter=args.requester or args.owner,
                material_type=stored_file.suffix.lstrip(".") or "file",
                storage_ref=str(stored_file),
                license_hint="internal",
                sensitivity="internal",
                extraction_tool="project_init_script",
                extraction_status="registered",
            )
            source_refs.append(material["sourceRef"])
        if source_refs:
            project_path = bundle.root / result["projectRef"]
            project = load_object(project_path)
            update_frontmatter_file(project_path, {"sourceMaterialRefs": source_refs, "updatedAt": project.get("updatedAt", "")})
        write_workspace_entrypoint(workspace_ref, args.project_id, args.name, bundle.root, source_refs)
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
        return 0
    except KnowledgeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
