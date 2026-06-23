import tempfile
import unittest
from pathlib import Path

from zhenzhi_knowledge.core import Bundle, OBJECT_ROOT_NAMES, validate_bundle


def write_minimal_bundle(root: Path) -> None:
    for directory in OBJECT_ROOT_NAMES:
        (root / directory).mkdir(parents=True, exist_ok=True)
        (root / directory / "index.md").write_text(f"# {directory}\n", encoding="utf-8")
    for file_name in [
        "index.md",
        "log.md",
        "projects/index.md",
        "agents/index.md",
        "tools/index.md",
        "knowledge/index.md",
        "runs/index.md",
        "tasks/index.md",
        "sources/index.md",
        "task-results/index.md",
    ]:
        path = root / file_name
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(f"# {path.stem}\n", encoding="utf-8")


def write_task_result(root: Path, name: str, acceptance_status: str, decision: str) -> None:
    (root / "task-results" / f"{name}.md").write_text(
        f"""---
type: TaskResult
title: Contract validation fixture
createdAt: 2026-06-23T00:00:00Z
resultId: {name}
taskId: TASK-{name}
projectId: demo
status: done
summary: Contract validation fixture.
executorAgent: agent.company.development
runner: local
leaseProof: local
outputRefs: []
evidenceRefs: []
risks: []
blockers: []
nextAction: close
checks: []
approvalRequest: {{}}
acceptancePolicy:
  acceptanceStatus: {acceptance_status}
qualityEvaluation:
  decision: {decision}
---

# Summary
""",
        encoding="utf-8",
    )


def write_project_task(root: Path, task_id: str, status: str) -> None:
    project_dir = root / "projects" / "demo" / "tasks"
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / f"{task_id}.md").write_text(
        f"""---
type: ProjectTask
title: Legacy routing status fixture
timestamp: 2026-06-23T00:00:00Z
taskId: {task_id}
projectId: demo
assignee: agent.company.project-manager
status: {status}
priority: medium
workSourceType: project_setup
sourceReason: Legacy remote project task status.
---

# Task
""",
        encoding="utf-8",
    )


class TaskResultContractValidationTests(unittest.TestCase):
    def test_validate_accepts_current_task_result_lifecycle_values(self) -> None:
        fixtures = [
            ("ready-test", "ready_for_test", "complete_for_v1_test_boundary"),
            ("pm-review", "waiting_project_manager_review", "accepted"),
            ("prod-blocked", "blocked_for_production_launch", "blocked_for_production_launch"),
            ("arch-handoff", "submitted_for_architecture_handoff", "handoff_to_architecture"),
            ("historical-debt", "blocked_pending_pm_or_human_decision", "partial_due_historical_core_quality_gate"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            for name, acceptance_status, decision in fixtures:
                write_task_result(root, name, acceptance_status, decision)

            problems = validate_bundle(Bundle(root))

        self.assertFalse([problem for problem in problems if "unknown acceptancePolicy.acceptanceStatus" in problem])
        self.assertFalse([problem for problem in problems if "unknown qualityEvaluation.decision" in problem])

    def test_validate_accepts_legacy_remote_task_routing_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            write_project_task(root, "manual-runner", "manual-runner-required")
            write_project_task(root, "submitted", "submitted")

            problems = validate_bundle(Bundle(root))

        self.assertFalse([problem for problem in problems if "unknown status manual-runner-required" in problem])
        self.assertFalse([problem for problem in problems if "unknown task routing status manual-runner-required" in problem])
        self.assertFalse([problem for problem in problems if "unknown task routing status submitted" in problem])

    def test_validate_still_rejects_bad_task_result_contract_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            write_task_result(root, "bad-values", "waiting_human_acceptance", "not_a_decision")

            problems = validate_bundle(Bundle(root))

        self.assertIn(
            "task-results/bad-values.md: unknown acceptancePolicy.acceptanceStatus waiting_human_acceptance",
            problems,
        )
        self.assertIn(
            "task-results/bad-values.md: unknown qualityEvaluation.decision not_a_decision",
            problems,
        )


if __name__ == "__main__":
    unittest.main()
