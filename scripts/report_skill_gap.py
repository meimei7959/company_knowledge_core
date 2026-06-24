#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from zhenzhi_knowledge.core import Bundle, KnowledgeError, create_project_task, make_skill, rel  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report a reusable skill gap from a business project back to the central skill registry.")
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle = Bundle(Path(args.central_root).expanduser().resolve())
    try:
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


if __name__ == "__main__":
    raise SystemExit(main())
