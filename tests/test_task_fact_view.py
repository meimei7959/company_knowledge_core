import contextlib
import io
import json
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

from zhenzhi_knowledge.cli import main
from zhenzhi_knowledge.core import Bundle
from zhenzhi_knowledge.core import build_task_fact_view as build_task_fact_view_from_core
from zhenzhi_knowledge.core import workbench_project_execution_read_model
from zhenzhi_knowledge.server import KnowledgeHTTPServer
from zhenzhi_knowledge.task_fact_view import build_task_fact_view


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
        "runner-invitations",
        "tool-registration-requests",
        "credential-requests",
        "notifications",
        "actors",
    ]:
        (root / directory).mkdir(parents=True, exist_ok=True)
        (root / directory / "index.md").write_text(f"# {directory}\n", encoding="utf-8")
    (root / "index.md").write_text("# Index\n", encoding="utf-8")
    (root / "log.md").write_text("# Log\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")


def write_object(path: Path, frontmatter: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter.strip()}\n---\n", encoding="utf-8")


def add_v0_gap_tasks(root: Path) -> None:
    task_dir = root / "projects" / "qa" / "tasks"
    write_object(
        task_dir / "done-no-result.md",
        """
type: ProjectTask
taskId: DONE-NO-RESULT
projectId: qa
title: Done without result
status: done
workSourceType: feature
requirementRefs:
  - REQ-DONE
updatedAt: "2026-06-23T08:00:00Z"
""",
    )
    write_object(
        task_dir / "done-no-evidence.md",
        """
type: ProjectTask
taskId: DONE-NO-EVIDENCE
projectId: qa
title: Done without evidence
status: done
workSourceType: feature
requirementRefs:
  - REQ-DONE
sourceMaterialRefs:
  - docs/product/task-fact.md
resultRef: task-results/tr-done-no-evidence.md
updatedAt: "2026-06-23T08:00:00Z"
auditRefs:
  - knowledge/audit/audit.done.md
notificationRefs:
  - notifications/notice.done.md
""",
    )
    write_object(
        root / "task-results" / "tr-done-no-evidence.md",
        """
type: TaskResult
resultId: tr-done-no-evidence
taskId: DONE-NO-EVIDENCE
status: done
summary: Done but evidence missing
evidenceRefs: []
testsOrChecks: []
outputRefs:
  - token_abc123
qualityEvaluation: {}
commonRulesEvaluation: {}
acceptancePolicy:
  acceptanceOwner: agent.company.project-manager
  credential: secret_abc123
completedAt: "2026-06-23T08:01:00Z"
""",
    )
    write_object(
        task_dir / "waiting-runner.md",
        """
type: ProjectTask
taskId: WAITING-RUNNER
projectId: qa
title: Waiting runner
status: waiting_runner
workSourceType: feature
requirementRefs:
  - REQ-RUNNER
assignedRunner: runner.possible
updatedAt: "2026-06-23T08:00:00Z"
""",
    )


def add_v0_acceptance_tasks(root: Path) -> None:
    task_dir = root / "projects" / "qa" / "tasks"
    write_object(
        task_dir / "waiting-acceptance.md",
        """
type: ProjectTask
taskId: WAITING-ACCEPTANCE
projectId: qa
title: Waiting acceptance
status: waiting_acceptance
workSourceType: feature
requirementRefs:
  - REQ-ACCEPT
updatedAt: "2026-06-23T08:00:00Z"
""",
    )
    write_object(
        task_dir / "waiting-acceptance-with-pm.md",
        """
type: ProjectTask
taskId: WAITING-ACCEPTANCE-WITH-PM
projectId: qa
title: Waiting acceptance with PM owner
status: waiting_acceptance
workSourceType: feature
requirementRefs:
  - REQ-ACCEPT
resultRef: task-results/tr-waiting-acceptance-with-pm.md
updatedAt: "2026-06-23T08:00:00Z"
""",
    )
    write_object(
        root / "task-results" / "tr-waiting-acceptance-with-pm.md",
        """
type: TaskResult
resultId: tr-waiting-acceptance-with-pm
taskId: WAITING-ACCEPTANCE-WITH-PM
status: done
summary: Waiting for PM review
evidenceRefs:
  - evidence.md
testsOrChecks:
  - checked
qualityEvaluation: {"passed": true}
commonRulesEvaluation: {"passed": true}
acceptancePolicy: {"projectManager": "agent.company.project-manager"}
completedAt: "2026-06-23T08:01:00Z"
""",
    )
    write_object(
        task_dir / "legacy-feature.md",
        """
type: ProjectTask
taskId: LEGACY-FEATURE
projectId: qa
title: Legacy feature
status: pending
workSourceType: feature
""",
    )


def add_v1_happy_path_records(root: Path) -> None:
    write_object(
        root / "runners" / "runner.pm.md",
        """
type: AgentRunner
runnerId: runner.pm
title: PM runner
status: online_readonly
agentTeamCapabilityVersionRef: agent-team.v1
""",
    )
    write_object(
        root / "projects" / "qa" / "receiver-reviews" / "receiver-review.pm-v1.md",
        """
type: ReceiverReview
reviewId: receiver-review.pm-v1
projectId: qa
upstreamRef: projects/qa/tasks/pm-v1.md
receiverAgent: agent.company.project-manager
reviewerAgent: agent.company.project-manager
status: accepted_with_assumptions
decision: accepted_with_assumptions
artifactRefs:
  - docs/product/task-fact-v1.md
issues: []
assumptions:
  - V1 fixture uses existing file refs.
timestamp: "2026-06-23T08:00:00Z"
""",
    )
    write_object(
        root / "projects" / "qa" / "receiver-reviews" / "receiver-review.worker-dev-v1.md",
        """
type: ReceiverReview
reviewId: receiver-review.worker-dev-v1
projectId: qa
upstreamRef: projects/qa/tasks/worker-dev-v1.md
receiverAgent: agent.company.development
reviewerAgent: agent.company.development
status: accepted
decision: accepted
artifactRefs:
  - projects/qa/tasks/pm-v1.md
issues: []
assumptions: []
timestamp: "2026-06-23T08:00:00Z"
""",
    )
    write_object(
        root / "knowledge" / "audit" / "audit.pm-v1.md",
        """
type: AuditLog
action: task.fact.v1.fixture
actor: agent.company.project-manager
targetRef: projects/qa/tasks/pm-v1.md
summary: PM V1 fixture audited.
timestamp: "2026-06-23T08:02:00Z"
""",
    )
    write_object(
        root / "notifications" / "notice.pm-v1.md",
        """
type: NotificationRecord
notificationId: notice.pm-v1
status: delivered
channel: workbench
recipient: agent.company.project-manager
targetRef: projects/qa/tasks/pm-v1.md
summary: PM V1 fixture notification.
timestamp: "2026-06-23T08:02:00Z"
""",
    )


def add_v1_happy_path_tasks(root: Path) -> None:
    task_dir = root / "projects" / "qa" / "tasks"
    write_object(
        task_dir / "pm-v1.md",
        """
type: ProjectTask
taskId: PM-V1
projectId: qa
title: PM controlled V1 task
status: waiting_acceptance
workSourceType: feature
requirementRefs:
  - ANOS-REQ-160-FUSION-V1
acceptanceCriteriaRefs:
  - docs/product/task-fact-v1.md
sourceReason: PM controls worker delivery.
receiverReviewRefs:
  - projects/qa/receiver-reviews/receiver-review.pm-v1.md
pmAgentId: agent.company.project-manager
workerTaskRefs:
  - projects/qa/tasks/worker-dev-v1.md
agentTeamCapabilityVersionRef: agent-team.v1
assignedRunner: runner.pm
resultRef: task-results/tr-pm-v1.md
updatedAt: "2026-06-23T08:00:00Z"
auditRefs:
  - knowledge/audit/audit.pm-v1.md
notificationRefs:
  - notifications/notice.pm-v1.md
""",
    )
    write_object(
        task_dir / "worker-dev-v1.md",
        """
type: ProjectTask
taskId: WORKER-DEV-V1
projectId: qa
title: Development worker V1
status: done
workSourceType: feature
parentTaskId: PM-V1
workerRole: development
assignee: agent.company.development
receiverReviewRefs:
  - projects/qa/receiver-reviews/receiver-review.worker-dev-v1.md
resultRef: task-results/tr-worker-dev-v1.md
updatedAt: "2026-06-23T08:00:00Z"
""",
    )


def add_v1_happy_path_results(root: Path) -> None:
    write_object(
        root / "task-results" / "tr-worker-dev-v1.md",
        """
type: TaskResult
resultId: tr-worker-dev-v1
taskId: WORKER-DEV-V1
status: done
summary: Worker completed implementation.
outputRefs:
  - zhenzhi_knowledge/core.py
evidenceRefs:
  - tests/test_task_fact_view.py
testsOrChecks:
  - python3 -m unittest tests.test_task_fact_view
qualityEvaluation: {"passed": true}
commonRulesEvaluation: {"passed": true}
completedAt: "2026-06-23T08:03:00Z"
""",
    )
    write_object(
        root / "task-results" / "tr-pm-v1.md",
        """
type: TaskResult
resultId: tr-pm-v1
taskId: PM-V1
status: done
summary: PM consolidated worker output.
outputRefs:
  - task-results/tr-worker-dev-v1.md
evidenceRefs:
  - tests/test_task_fact_view.py
testsOrChecks:
  - python3 -m unittest tests.test_task_fact_view
qualityEvaluation: {"passed": true}
commonRulesEvaluation: {"passed": true}
acceptancePolicy: {"projectManager": "agent.company.project-manager"}
workerResultRefs:
  - task-results/tr-worker-dev-v1.md
agentImprovementProposalRefs:
  - knowledge/agent-improvements/aip.pm-v1.md
evalCaseRefs:
  - eval-cases/eval.pm-v1.md
completedAt: "2026-06-23T08:04:00Z"
""",
    )


def add_v1_sparse_records(root: Path) -> None:
    task_dir = root / "projects" / "qa" / "tasks"
    write_object(
        task_dir / "sparse-v1.md",
        """
type: ProjectTask
taskId: SPARSE-V1
projectId: qa
title: Sparse V1 task
status: processing
workSourceType: feature
requirementRefs:
  - ANOS-REQ-160-FUSION-V1
pmAgentId: agent.company.project-manager
workerTaskRefs:
  - projects/qa/tasks/sparse-worker-missing-result.md
  - projects/qa/tasks/sparse-worker-no-evidence.md
growthSignalRequired: true
resultRef: task-results/tr-sparse-v1.md
updatedAt: "2026-06-23T08:00:00Z"
""",
    )
    write_object(
        task_dir / "sparse-worker-missing-result.md",
        """
type: ProjectTask
taskId: SPARSE-WORKER-MISSING-RESULT
projectId: qa
title: Sparse worker missing result
status: done
workSourceType: feature
parentTaskId: SPARSE-V1
workerRole: development
updatedAt: "2026-06-23T08:00:00Z"
""",
    )
    write_object(
        task_dir / "sparse-worker-no-evidence.md",
        """
type: ProjectTask
taskId: SPARSE-WORKER-NO-EVIDENCE
projectId: qa
title: Sparse worker no evidence
status: done
workSourceType: feature
parentTaskId: SPARSE-V1
workerRole: test
resultRef: task-results/tr-sparse-worker-no-evidence.md
updatedAt: "2026-06-23T08:00:00Z"
""",
    )
    write_object(
        root / "task-results" / "tr-sparse-worker-no-evidence.md",
        """
type: TaskResult
resultId: tr-sparse-worker-no-evidence
taskId: SPARSE-WORKER-NO-EVIDENCE
status: done
summary: Worker result lacks evidence.
evidenceRefs: []
testsOrChecks:
  - checked
qualityEvaluation: {"passed": true}
commonRulesEvaluation: {"passed": true}
completedAt: "2026-06-23T08:03:00Z"
""",
    )
    write_object(
        root / "task-results" / "tr-sparse-v1.md",
        """
type: TaskResult
resultId: tr-sparse-v1
taskId: SPARSE-V1
status: failed
summary: Sparse task requires growth signal.
qualityEvaluation: {"passed": false}
commonRulesEvaluation: {"passed": true}
qualitySignals:
  - failed_quality
completedAt: "2026-06-23T08:04:00Z"
""",
    )


def create_task_fact_fixture(root: Path) -> None:
    write_minimal_bundle(root)
    (root / "projects" / "qa" / "tasks").mkdir(parents=True, exist_ok=True)
    add_v0_gap_tasks(root)
    add_v0_acceptance_tasks(root)
    add_v1_happy_path_records(root)
    add_v1_happy_path_tasks(root)
    add_v1_happy_path_results(root)
    add_v1_sparse_records(root)


def task_fact_cli_view(root: Path, task_id: str) -> dict:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exit_code = main(["--root", str(root), "task", "fact", task_id, "--project", "qa"])
    if exit_code != 0:
        raise AssertionError(f"task fact CLI failed with exit code {exit_code}")
    return json.loads(out.getvalue())


class TaskFactViewCompatibilityTests(unittest.TestCase):
    def test_core_wrapper_preserves_v0_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            write_object(
                root / "projects" / "qa" / "tasks" / "legacy.md",
                """
type: ProjectTask
taskId: LEGACY
projectId: qa
title: Legacy task
status: done
workSourceType: feature
resultRef: task-results/tr-legacy.md
updatedAt: "2026-06-23T08:00:00Z"
""",
            )
            write_object(
                root / "task-results" / "tr-legacy.md",
                """
type: TaskResult
resultId: tr-legacy
taskId: LEGACY
status: done
summary: Done.
evidenceRefs:
  - evidence.md
testsOrChecks:
  - focused
qualityEvaluation: {"passed": true}
commonRulesEvaluation: {"passed": true}
outputRefs:
  - token_abc123
""",
            )

            bundle = Bundle(root)
            direct = build_task_fact_view(bundle, "qa", "LEGACY")
            wrapped = build_task_fact_view_from_core(bundle, "qa", "LEGACY")

            self.assertEqual(direct, wrapped)
            self.assertEqual("task-fact-view.v0", wrapped["schemaVersion"])
            self.assertEqual("TaskFactView", wrapped["kind"])
            self.assertNotIn("token_abc123", str(wrapped))


class TaskFactViewV0Tests(unittest.TestCase):
    def test_v0_current_gaps_redaction_and_status_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_task_fact_fixture(root)
            bundle = Bundle(root)

            done_no_result = build_task_fact_view(bundle, "qa", "DONE-NO-RESULT")
            self.assertIn(("resultRef", "current gap"), {(gap["field"], gap["type"]) for gap in done_no_result["gaps"]})
            self.assertIn(("evidenceRefs", "current gap"), {(gap["field"], gap["type"]) for gap in done_no_result["gaps"]})

            done_no_evidence = build_task_fact_view(bundle, "qa", "DONE-NO-EVIDENCE")
            gap_fields = {gap["field"] for gap in done_no_evidence["gaps"]}
            self.assertIn("evidenceRefs", gap_fields)
            self.assertIn("testsOrChecks", gap_fields)
            self.assertEqual("DONE-NO-EVIDENCE", done_no_evidence["facts"]["identity"]["taskId"])
            self.assertEqual(["docs/product/task-fact.md"], done_no_evidence["facts"]["source"]["sourceMaterialRefs"])
            rendered = json.dumps(done_no_evidence, ensure_ascii=False)
            self.assertNotIn("token_abc123", rendered)
            self.assertNotIn("secret_abc123", rendered)
            self.assertIn("[redacted]", rendered)
            self.assertEqual(done_no_evidence["facts"]["status"], done_no_evidence["statusExplanation"])

    def test_v0_waiting_and_legacy_gap_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_task_fact_fixture(root)
            bundle = Bundle(root)

            waiting_runner = build_task_fact_view(bundle, "qa", "WAITING-RUNNER")
            self.assertIn("waitingRunnerReason", {gap["field"] for gap in waiting_runner["gaps"]})

            waiting_acceptance = build_task_fact_view(bundle, "qa", "WAITING-ACCEPTANCE")
            self.assertIn("resultRef", {gap["field"] for gap in waiting_acceptance["gaps"]})
            self.assertIn("acceptanceOwner", {gap["field"] for gap in waiting_acceptance["gaps"]})

            with_pm = build_task_fact_view(bundle, "qa", "WAITING-ACCEPTANCE-WITH-PM")
            self.assertNotIn("acceptanceOwner", {gap["field"] for gap in with_pm["gaps"]})
            self.assertEqual("agent.company.project-manager", with_pm["facts"]["status"]["nextStepOwner"])

            legacy = build_task_fact_view(bundle, "qa", "LEGACY-FEATURE")
            self.assertIn(("requirementRefs", "legacy gap"), {(gap["field"], gap["type"]) for gap in legacy["gaps"]})


class TaskFactViewV1Tests(unittest.TestCase):
    def test_v1_complete_projection_worker_growth_and_capability(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_task_fact_fixture(root)

            view = build_task_fact_view(Bundle(root), "qa", "PM-V1")
            self.assertEqual("task-fact-view.v1", view["schemaVersion"])
            self.assertEqual("agent.company.project-manager", view["facts"]["workerParticipation"]["pmController"])
            self.assertEqual(["projects/qa/tasks/worker-dev-v1.md"], view["facts"]["workerParticipation"]["workerTaskRefs"])
            self.assertEqual("WORKER-DEV-V1", view["facts"]["workerParticipation"]["workers"][0]["task"]["taskId"])
            self.assertEqual(["knowledge/agent-improvements/aip.pm-v1.md"], view["facts"]["growthSignals"]["proposalRefs"])
            self.assertEqual(["eval-cases/eval.pm-v1.md"], view["facts"]["growthSignals"]["evalCaseRefs"])
            self.assertTrue(view["facts"]["capabilityVersion"]["match"])
            self.assertEqual(view["facts"]["result"], view["facts"]["resultEvidence"])
            self.assertNotIn("capability_version_mismatch", {gap.get("reason") for gap in view["gaps"]})
            self.assertNotIn("missing_worker_result", {gap.get("reason") for gap in view["gaps"]})

    def test_v1_projection_keeps_worker_and_capability_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_task_fact_fixture(root)

            view = build_task_fact_view(Bundle(root), "qa", "SPARSE-V1")
            reasons = {gap.get("reason") for gap in view["gaps"]}

            self.assertEqual("task-fact-view.v1", view["schemaVersion"])
            self.assertIn("missing_receiver_review", reasons)
            self.assertIn("missing_worker_review", reasons)
            self.assertIn("missing_worker_result", reasons)
            self.assertIn("growth_signal_gap", reasons)
            self.assertIn("capability_version_mismatch", reasons)
            self.assertIn("missing_audit", reasons)
            self.assertIn(("worker.evidenceRefs", "result evidence gap"), {(gap["field"], gap["type"]) for gap in view["gaps"]})

    def test_workbench_uses_same_v1_fact_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_task_fact_fixture(root)

            workbench = workbench_project_execution_read_model(Bundle(root), "qa", "PM-V1")

            self.assertEqual("task-fact-view.v1", workbench["selectedTaskFactView"]["schemaVersion"])
            self.assertEqual("agent.company.project-manager", workbench["selectedTaskFactView"]["facts"]["workerParticipation"]["pmController"])


class TaskFactViewAdapterTests(unittest.TestCase):
    def test_cli_returns_v0_and_v1_fact_views(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_task_fact_fixture(root)

            v0_view = task_fact_cli_view(root, "DONE-NO-EVIDENCE")
            v1_view = task_fact_cli_view(root, "PM-V1")

            self.assertEqual("TaskFactView", v0_view["kind"])
            self.assertEqual("task-fact-view.v0", v0_view["schemaVersion"])
            self.assertEqual("task-fact-view.v1", v1_view["schemaVersion"])
            self.assertEqual("agent.company.project-manager", v1_view["facts"]["workerParticipation"]["pmController"])

    def test_http_api_returns_v0_and_v1_fact_views(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_task_fact_fixture(root)
            try:
                with mock.patch("zhenzhi_knowledge.server.ensure_database_schema"), mock.patch("zhenzhi_knowledge.server.ensure_operational_schema"):
                    server = KnowledgeHTTPServer(("127.0.0.1", 0), Bundle(root), api_token="test-token")
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                v0_view = self._api_fact_view(server.server_port, "WAITING-ACCEPTANCE")
                v1_view = self._api_fact_view(server.server_port, "PM-V1")

                self.assertEqual("TaskFactView", v0_view["kind"])
                self.assertIn("acceptanceOwner", {gap["field"] for gap in v0_view["gaps"]})
                self.assertEqual("task-fact-view.v1", v1_view["schemaVersion"])
                self.assertEqual("agent.company.project-manager", v1_view["facts"]["workerParticipation"]["pmController"])
            finally:
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()

    def _api_fact_view(self, port: int, task_id: str) -> dict:
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/v0/projects/qa/tasks/{task_id}/fact-view",
            headers={"Authorization": "Bearer test-token"},
        )
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
