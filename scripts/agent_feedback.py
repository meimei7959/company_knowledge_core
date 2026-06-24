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
    create_bugfix_task,
    create_defect,
    create_project_task,
    load_object,
    make_skill,
    rel,
    skill_storage_dir,
    slug,
)


class AgentFeedbackParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(
            2,
            "\n".join(
                [
                    f"error: {message}",
                    "",
                    "Use one feedback subcommand:",
                    "  system-issue  Report an Agent-system defect and create PM triage by default.",
                    "  skill-gap     Report a reusable skill gap for knowledge-engineering review.",
                    "",
                    "Examples:",
                    "  python3 scripts/agent_feedback.py system-issue --source-project <project-id> --title <title> --actual <what happened>",
                    "  python3 scripts/agent_feedback.py skill-gap --source-project <project-id> --skill-id <id> --name <name> --purpose <purpose> --gap <gap>",
                    "",
                ]
            ),
        )


def add_system_issue_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--central-root", default=str(ROOT), help="company_knowledge_core root on this computer.")
    parser.add_argument("--target-project", default="company-knowledge-core", help="Central project that owns Agent-system defects.")
    parser.add_argument("--source-project", required=True, help="Business project where the issue was discovered.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--actual", required=True, help="What happened.")
    parser.add_argument("--expected", default="The project Agent should understand the workflow and continue without human translation.")
    parser.add_argument("--step", action="append", default=[])
    parser.add_argument("--evidence-ref", action="append", default=[])
    parser.add_argument("--reporter", default="agent.company.project-manager")
    parser.add_argument("--severity", default="medium")
    parser.add_argument("--assignee", default="agent.company.project-manager")
    parser.add_argument("--no-fix-task", action="store_true", help="Only create Defect, do not create the PM triage task.")


def add_skill_gap_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--central-root", default=str(ROOT), help="company_knowledge_core root on this computer.")
    parser.add_argument("--target-project", default="company-knowledge-core", help="Central project that owns reusable Agent capabilities.")
    parser.add_argument("--source-project", required=True, help="Business project where the skill gap was discovered.")
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--gap", required=True, help="What the current skill cannot handle.")
    parser.add_argument("--proposed-use", default="", help="How this skill should help future projects.")
    parser.add_argument("--source-ref", default="", help="Optional local note, screenshot path, task ref, or workspace file.")
    parser.add_argument("--owner", default="agent.company.knowledge-engineering")
    parser.add_argument("--assignee", default="agent.company.knowledge-engineering")
    parser.add_argument("--scope", default="company", choices=["company", "project", "private"])
    parser.add_argument("--risk", default="L2")
    parser.add_argument("--no-review-task", action="store_true")


def parse_system_issue_args(argv: list[str] | None = None, *, prog: str = "agent_feedback.py system-issue") -> argparse.Namespace:
    parser = AgentFeedbackParser(prog=prog, description="Report an Agent-system issue from a business project back to the central project.")
    add_system_issue_arguments(parser)
    return parser.parse_args(argv)


def parse_skill_gap_args(argv: list[str] | None = None, *, prog: str = "agent_feedback.py skill-gap") -> argparse.Namespace:
    parser = AgentFeedbackParser(prog=prog, description="Report a reusable skill gap from a business project back to the central skill registry.")
    add_skill_gap_arguments(parser)
    return parser.parse_args(argv)


def report_system_issue(args: argparse.Namespace) -> int:
    bundle = Bundle(Path(args.central_root).expanduser().resolve())
    evidence_refs = [
        f"sourceProject:{args.source_project}",
        *[item for item in args.evidence_ref if item.strip()],
    ]
    steps = args.step or [
        f"User found the issue while working in project `{args.source_project}`.",
        "User asked the project manager Agent to sync the issue to the central system.",
        "Project manager Agent did not know the concrete writeback action.",
    ]
    try:
        defect_path = create_defect(
            bundle,
            title=args.title,
            project_id=args.target_project,
            reporter=args.reporter,
            severity=args.severity,
            evidence_refs=evidence_refs,
            expected_behavior=args.expected,
            actual_behavior=args.actual,
            reproduction_steps=steps,
        )
        result = {
            "defectRef": rel(defect_path, bundle.root),
            "fixTaskRef": "",
        }
        if not args.no_fix_task:
            defect_id = str(load_object(defect_path).get("defectId"))
            fix_task = create_bugfix_task(
                bundle,
                defect_id=defect_id,
                title=f"项目经理分诊体系问题：{args.title}",
                requester=args.reporter,
                assignee=args.assignee,
                task_type="project_management",
                priority="high",
            )
            result["fixTaskRef"] = rel(fix_task, bundle.root)
        print(result["defectRef"])
        if result["fixTaskRef"]:
            print(result["fixTaskRef"])
        return 0
    except KnowledgeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


def report_skill_gap(args: argparse.Namespace) -> int:
    bundle = Bundle(Path(args.central_root).expanduser().resolve())
    try:
        skill_id = slug(args.skill_id)
        skill_path = skill_storage_dir(bundle) / f"{skill_id}.md"
        if skill_path.exists():
            raise KnowledgeError(
                f"SkillAsset already exists for --skill-id {skill_id}: {rel(skill_path, bundle.root)}. "
                "Choose a new --skill-id or ask Knowledge Engineering to review the existing SkillAsset."
            )
        skill_path = make_skill(
            bundle,
            skill_id=args.skill_id,
            name=args.name,
            owner=args.owner,
            purpose=args.purpose,
            scope=args.scope,
            risk=args.risk,
            project_id=args.source_project if args.scope == "project" else "",
            source_ref=args.source_ref or f"sourceProject:{args.source_project}",
        )
        task_ref = ""
        if not args.no_review_task:
            task_path = create_project_task(
                bundle,
                title=f"知识工程评审并沉淀可复用 Skill：{args.name}",
                project_id=args.target_project,
                requester=args.owner,
                assignee=args.assignee,
                task_type="knowledge_capture",
                priority="high",
                expected_output=[
                    "SkillAsset input/output contracts, examples, evaluation cases, rollout scope, and reuse guidance are ready.",
                    f"Source project: {args.source_project}",
                    f"Skill gap: {args.gap}",
                    f"Proposed use: {args.proposed_use or 'TBD'}",
                ],
                work_source_type="maintenance",
                source_reason=(
                    f"Reusable skill gap discovered in project {args.source_project}. "
                    "Draft SkillAsset must be reviewed before company-wide reuse."
                ),
            )
            task_ref = rel(task_path, bundle.root)
        print(rel(skill_path, bundle.root))
        if task_ref:
            print(task_ref)
        return 0
    except KnowledgeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


def system_issue_main(argv: list[str] | None = None, *, prog: str = "agent_feedback.py system-issue") -> int:
    return report_system_issue(parse_system_issue_args(argv, prog=prog))


def skill_gap_main(argv: list[str] | None = None, *, prog: str = "agent_feedback.py skill-gap") -> int:
    return report_skill_gap(parse_skill_gap_args(argv, prog=prog))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = AgentFeedbackParser(description="Report Agent-system feedback from business projects back to company_knowledge_core.")
    subparsers = parser.add_subparsers(
        dest="feedback_type",
        metavar="{system-issue,skill-gap}",
        required=True,
        parser_class=AgentFeedbackParser,
    )

    system_issue = subparsers.add_parser("system-issue", help="Create a central Defect plus PM triage task.")
    add_system_issue_arguments(system_issue)
    system_issue.set_defaults(handler=report_system_issue)

    skill_gap = subparsers.add_parser("skill-gap", help="Create a draft SkillAsset plus Knowledge Engineering review task.")
    add_skill_gap_arguments(skill_gap)
    skill_gap.set_defaults(handler=report_skill_gap)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
