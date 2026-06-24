#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from zhenzhi_knowledge.core import Bundle, KnowledgeError, create_bugfix_task, create_defect, load_object, rel  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report an Agent-system issue from a business project back to the central project.")
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
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


if __name__ == "__main__":
    raise SystemExit(main())
