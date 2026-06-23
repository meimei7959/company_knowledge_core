from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from zhenzhi_knowledge.core import (
    Bundle,
    claim_project_task,
    create_source_material,
    export_graph_snapshot,
    finish_project_task,
    graph_impact,
    load_object,
    make_agent,
    make_project,
    project_task_context_payload,
    register_agent_runner,
    set_project_task_status,
    validate_bundle,
)


def write_minimal_bundle(root: Path) -> None:
    for directory in [
        "projects",
        "agents",
        "tools",
        "knowledge",
        "runs",
        "tasks",
        "sources",
        "task-results",
        "runners",
        "credential-requests",
        "notifications",
        "graph",
    ]:
        (root / directory).mkdir(parents=True, exist_ok=True)
        (root / directory / "index.md").write_text(f"# {directory}\n", encoding="utf-8")
    (root / "index.md").write_text("# Index\n", encoding="utf-8")
    (root / "log.md").write_text("# Log\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="zhenzhi-acceptance-") as tmp:
        root = Path(tmp)
        write_minimal_bundle(root)
        bundle = Bundle(root)

        make_project(bundle, "acceptance-core", "Acceptance Core", "meimei")
        make_agent(bundle, "agent.acceptance.knowledge", "Acceptance Knowledge Agent", "meimei", "codex", "Process intake material.")
        register_agent_runner(
            bundle,
            "runner.acceptance.local-codex",
            "Acceptance Local Codex",
            host_type="mac",
            mode="manual",
            agents=["agent.acceptance.knowledge"],
            capabilities=["knowledge_capture", "codex", "knowledge_sync"],
            available_projects=["acceptance-core"],
            repo_access=["https://github.com/meimei7959/company_knowledge_core.git"],
            data_scopes=["company"],
        )

        material_result = create_source_material(
            bundle,
            "Feishu card callback lesson",
            "feishu://message/acceptance-card",
            "meimei",
            project_id="acceptance-core",
            material_type="document",
            content="Feishu interactive card callbacks must reply immediately, then update or send result asynchronously.",
            create_task_flag=True,
            assignee="agent.acceptance.knowledge",
        )
        task = load_object(root / material_result["taskRef"])
        task_id = str(task["taskId"])
        set_project_task_status(bundle, task_id, "waiting_runner", "scheduler")
        claim = claim_project_task(bundle, task_id, "runner.acceptance.local-codex")
        context = project_task_context_payload(bundle, task_id, "runner.acceptance.local-codex", str(claim["leaseToken"]))
        result_path = finish_project_task(
            bundle,
            task_id,
            "done",
            "Processed Feishu callback lesson into evidence-backed draft knowledge.",
            output_refs=[context["contextRef"]],
            evidence_refs=[material_result["sourceRef"]],
            runner_id="runner.acceptance.local-codex",
            lease_token=str(claim["leaseToken"]),
            executor_agent="agent.acceptance.knowledge",
            tests_or_checks=["production_closed_loop_acceptance.py"],
            knowledge_draft={
                "title": "Feishu interactive card callback flow",
                "category": "engineering",
                "summary": "Card callbacks should acknowledge immediately and perform durable work asynchronously.",
                "structured": "Use immediate callback acknowledgement for Feishu interactive cards. Persist task state, then update the card or notify the requester after work completes.",
                "sourceRefs": [material_result["sourceRef"]],
                "confidence": "high",
                "applicability": "Feishu interactive card workflows in Agent Hub.",
                "limits": ["Does not validate live Feishu tenant permissions."],
            },
        )
        snapshot = export_graph_snapshot(bundle, "acceptance")
        impact = graph_impact(bundle, material_result["sourceRef"], "acceptance")
        problems = validate_bundle(bundle)

        summary = {
            "ok": not problems,
            "root": str(root),
            "project": "acceptance-core",
            "material": material_result,
            "taskId": task_id,
            "contextRef": context["contextRef"],
            "resultRef": str(result_path.relative_to(root)),
            "graphSnapshot": snapshot["snapshotRef"],
            "impactCount": len(impact["affectedRefs"]),
            "problems": problems,
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
