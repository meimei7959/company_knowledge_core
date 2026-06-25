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
    read_text,
    rel,
    update_frontmatter_file,
    validate_bundle,
    write_text,
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


def localize_project_initialization_labels(bundle: Bundle, project_id: str, project_name: str) -> None:
    """Keep human-facing initialization labels on the project display name.

    `project_id` stays in paths, task ids, and machine refs. People should see
    the project name first.
    """
    pid = project_id.strip()
    old_task_title = f"Initialize project: {project_name}"
    new_task_title = f"{project_name} 项目初始化"
    old_expected = [
        "Confirm project scope, milestones, Agent team, Runner, repo, project group, and first tasks.",
        "Write TaskResult with handoff, blockers, and first executable backlog.",
    ]
    new_expected = [
        "确认项目范围、里程碑、Agent 团队、Runner、仓库、项目群和首批任务。",
        "写回 TaskResult，说明交接、阻塞和第一批可执行任务队列。",
    ]

    task_path = bundle.root / "projects" / pid / "tasks" / f"project-init-{pid}.md"
    if task_path.exists():
        update_frontmatter_file(task_path, {"title": new_task_title, "expectedOutput": new_expected})
        text = read_text(task_path)
        text = text.replace(old_task_title, new_task_title)
        for old, new in zip(old_expected, new_expected):
            text = text.replace(old, new)
        write_text(task_path, text)

    task_index_path = bundle.root / "projects" / pid / "tasks" / "index.md"
    if task_index_path.exists():
        text = read_text(task_index_path).replace(
            f"- [{old_task_title}](project-init-{pid}.md)",
            f"- [{new_task_title}](project-init-{pid}.md)",
        )
        write_text(task_index_path, text)

    launch_path = bundle.root / "projects" / pid / "launch.md"
    if launch_path.exists():
        text = read_text(launch_path)
        replacements = {
            "## Project Intake": "## 项目接入信息",
            "## Suggested Agent Team": "## 建议 Agent 团队",
            "## Initialization Checklist": "## 初始化检查清单",
            "- Confirm scope, milestone, Agent team, Runner, repo, project group, approval state.": "- 确认范围、里程碑、Agent 团队、Runner、仓库、项目群和审批状态。",
            "- Confirm entity workspace path; if not confirmed, keep workspaceRef=pending_confirmation.": "- 确认实体项目目录；未确认时保持 workspaceRef=pending_confirmation。",
            "- Existing repo: inspect README/AGENTS/directory/review rules before changes.": "- 已有仓库项目：变更前先读取 README、AGENTS、目录结构和评审规则。",
            "- New repo: create repo request from project name; do not ask user to provide repository name.": "- 新开发项目：按项目名称创建工程请求，不让用户反复提供仓库名。",
            "- Operations project: create operating cadence and feedback loop instead of forcing a code repo.": "- 运营类项目：建立运营节奏和反馈闭环，不强行套代码仓库流程。",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        write_text(launch_path, text)

    for log_path in [bundle.root / "log.md", bundle.root / "projects" / pid / "log.md"]:
        if log_path.exists():
            text = read_text(log_path).replace(
                f"registered Project {pid}",
                f"registered project {project_name} ({pid})",
            )
            write_text(log_path, text)


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


def workspace_source_rule(source_repo_note: str, *, workspace_ref: str = "", source_repo_path: str = "") -> str:
    if source_repo_note == "none":
        return "No source repository was registered during initialization."
    if workspace_ref.strip() and source_repo_path.strip():
        workspace = Path(workspace_ref).expanduser().resolve()
        source_repo = Path(source_repo_path).expanduser().resolve()
        if workspace == source_repo:
            return (
                "This workspace is the active source repository. Keep normal code, docs, AGENTS.md, and START_HERE.md here. "
                "Do not dump raw materials, long logs, screenshots, or unrelated delivery archives into the source tree; store them externally and reference them from central records."
            )
    return (
        "Source code is a reference mirror. Do not write project materials into it. "
        "When source code must be refreshed, update only the source mirror, then keep soft-copyright, operations, screenshots, and delivery materials in this workspace."
    )


def workspace_delivery_thinking_rules(root: Path, project_id: str) -> list[str]:
    return [
        "## Delivery Thinking",
        "",
        "Before producing role output, use the central Agent Delivery Thinking Framework:",
        "",
        f"- `{root}/docs/agent-team/agent-delivery-thinking-framework.md`",
        "",
        "Do not just fill templates. Think like the role owner: target, receiver, current state, path, exceptions, dependencies, evidence, gates, and next action. Choose the clearest delivery form for the downstream receiver.",
        "",
        "Before downstream work starts, the receiving Agent must create ReceiverReview. ReceiverReview checks whether the upstream output can be used, whether role boundaries are respected, and whether evidence is ready enough to continue. It is not final acceptance.",
        "",
        "Every TaskResult should make the framework self-check visible in `commonRulesEvaluation` or `qualityEvaluation`, without forcing a fixed table.",
        "",
        f"Central project rules for this workspace remain `projects/{project_id}/AGENTS.md`.",
        "",
    ]


def workspace_agent_feedback_rules(root: Path, project_id: str) -> list[str]:
    return [
        "## Report System Issues Back To Central",
        "",
        "When the user says this project exposed a problem in the Agent system, do not ask what `sync to central` means. Run the central issue reporter:",
        "",
        "```bash",
        f"cd {root}",
        "python3 scripts/agent_feedback.py system-issue \\",
        f"  --source-project {project_id} \\",
        "  --title \"<short issue title>\" \\",
        "  --actual \"<what happened>\" \\",
        "  --expected \"<what should happen>\" \\",
        "  --evidence-ref \"<optional local note, screenshot path, task ref, or conversation summary>\"",
        "```",
        "",
        "This creates a central Defect plus a Project Manager triage task in `company-knowledge-core`. Continue the business project after the issue is reported; do not fix central-system behavior inside this business workspace.",
        "",
        "When a role Agent needs a new reusable skill during this project, it may use a temporary local approach for the current delivery. Temporary local work is not reusable company capability. To reuse the skill in other projects, report it in the central repository on a feedback branch:",
        "",
        "```bash",
        f"cd {root}",
        f"git switch -c feedback/{project_id}-<stable-skill-id>",
        "python3 scripts/agent_feedback.py skill-gap \\",
        f"  --source-project {project_id} \\",
        "  --skill-id \"<stable-skill-id>\" \\",
        "  --name \"<skill name>\" \\",
        "  --purpose \"<what reusable capability is needed>\" \\",
        "  --gap \"<what the current skill cannot handle>\" \\",
        "  --proposed-use \"<how future projects will reuse it>\" \\",
        "  --source-ref \"<optional local note, task ref, or evidence>\"",
        "```",
        "",
        "You may reuse an existing central `feedback/*` or `codex/*` branch instead of creating a new one. Do not write skill-gap feedback directly on `main`. Push the feedback branch and ask Knowledge Engineering / PM to review it.",
        "",
        "This creates a draft central SkillAsset and a Knowledge Engineering review task. Do not treat a project-local skill as company-wide reusable until the central review/evaluation promotes it.",
        "",
    ]


def workspace_start_feedback_rules(root: Path, project_id: str) -> list[str]:
    return [
        "如果在本项目里发现 Agent 体系本身的问题，例如项目经理不知道怎么同步问题、任务流转不清楚、工具入口不好用，对 Codex 说：",
        "",
        "```txt",
        "把这个体系问题上报到中枢，标题是……，实际发生了……，期望应该是……",
        "```",
        "",
        "项目经理 Agent 应执行：",
        "",
        "```bash",
        f"cd {root}",
        f"python3 scripts/agent_feedback.py system-issue --source-project {project_id} --title \"<问题标题>\" --actual \"<实际发生>\" --expected \"<期望行为>\"",
        "```",
        "",
        "如果是某个岗位 Agent 发现 Skill 不够用，比如知识工程 Agent 做软著时缺少软著材料整理能力，对 Codex 说：",
        "",
        "```txt",
        "把这个 Skill 缺口上报到中枢复用。来源项目是 <项目ID>，Skill ID 是 <稳定英文ID>，名称是 <中文名>，用途是 <用途>，当前缺口是 <缺口>，未来项目复用方式是 <复用方式>。",
        "```",
        "",
        "项目经理 Agent 或发现缺口的岗位 Agent 应回到中枢仓库，先切到反馈分支，再执行：",
        "",
        "```bash",
        f"cd {root}",
        f"git switch -c feedback/{project_id}-<skill-id>",
        f"python3 scripts/agent_feedback.py skill-gap --source-project {project_id} --skill-id \"<skill-id>\" --name \"<Skill 名称>\" --purpose \"<用途>\" --gap \"<当前缺口>\" --proposed-use \"<复用方式>\"",
        "```",
        "",
        "如果中枢已经在 `feedback/*` 或 `codex/*` 分支上，也可以沿用那个分支；不要直接写 `main`。写完后推送这个分支，请知识工程/PM 评审。",
        "",
        "当前项目可以先用临时方案完成交付，但要复用给其他项目，必须进入中枢 `SkillAsset`，先作为 draft，经知识工程评审和测试后再推广。",
        "",
    ]


def workspace_start_delivery_thinking_rules(root: Path) -> list[str]:
    return [
        "## 交付思考",
        "",
        "正式开工前，先读取中枢思考框架：",
        "",
        "```txt",
        f"{root}/docs/agent-team/agent-delivery-thinking-framework.md",
        "```",
        "",
        "不要只填模板。每个岗位 Agent 先判断目标、对象、状态、路径、异常、依赖、证据、门禁和下一步，再自主选择最清楚的表达方式。",
        "",
        "交给下游前，下游接收 Agent 必须做 ReceiverReview：能接就继续，带假设就写清假设，不能接就退回或交 PM/人类决策。ReceiverReview 不是最终验收。",
        "",
    ]


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
            f"# {project_name} 项目入口",
            "",
            "You are working in the entity project workspace, not the central knowledge repository.",
            "",
            "## 开始方式",
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
            "## 工作区边界",
            "",
            f"- workspaceProfile: `{profile}`",
            f"- sourceRepoRef: `{source_repo_note}`",
            f"- rule: {workspace_source_rule(source_repo_note, workspace_ref=workspace_ref, source_repo_path=source_repo_path)}",
            "",
            "The user may keep working from this entity workspace. The Project Manager Agent coordinates role handoff. Only compact project records, task flow, TaskResult summaries, evidence refs, and AuditLog are written back to the central repository. Raw artifacts, long logs, screenshots, and PRD files stay in this workspace or external storage and are referenced through storageRef.",
            "",
            *workspace_delivery_thinking_rules(root, project_id),
            *workspace_agent_feedback_rules(root, project_id),
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
            *workspace_start_delivery_thinking_rules(root),
            *workspace_start_feedback_rules(root, project_id),
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
        localize_project_initialization_labels(bundle, args.project_id, args.name)
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
