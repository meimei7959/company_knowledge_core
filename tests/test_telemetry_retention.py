import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from zhenzhi_knowledge.core import Bundle, load_object
from zhenzhi_knowledge.telemetry_retention import (
    TelemetryRetentionConfig,
    TelemetryRetentionWorker,
    classify_telemetry_event,
    ingest_telemetry_event,
)


NOW = datetime(2026, 6, 23, 12, 0, tzinfo=timezone.utc)


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
        "notifications",
        "actors",
    ]:
        (root / directory).mkdir(parents=True, exist_ok=True)
        (root / directory / "index.md").write_text(f"# {directory}\n", encoding="utf-8")
    (root / "knowledge" / "audit").mkdir(parents=True, exist_ok=True)
    (root / "knowledge" / "metrics").mkdir(parents=True, exist_ok=True)
    (root / "knowledge" / "agent-improvements").mkdir(parents=True, exist_ok=True)
    (root / "knowledge" / "evals").mkdir(parents=True, exist_ok=True)
    (root / "index.md").write_text("# Index\n", encoding="utf-8")
    (root / "log.md").write_text("# Log\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")


def write_object(path: Path, frontmatter: str, body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter.strip()}\n---\n\n{body}", encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TelemetryRetentionCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write_minimal_bundle(self.root)
        self.bundle = Bundle(self.root)
        self.config = TelemetryRetentionConfig(now=NOW, ephemeral_ttl_hours=1, hot_ttl_hours=1, max_timeline_entries=3)

    def tearDown(self) -> None:
        self.tmp.cleanup()


class TelemetryRetentionIngestionTests(TelemetryRetentionCase):
    def test_ingestion_classification_and_current_state_upsert_overwrite(self) -> None:
        classified = classify_telemetry_event({"eventType": "model_usage", "model": "gpt-x", "taskId": "TASK-1"})
        self.assertEqual(classified["retentionClass"], "diagnostic_metric")
        self.assertIn("metrics", classified["routes"])

        ingest_telemetry_event(
            self.bundle,
            {"eventId": "hb-1", "eventType": "heartbeat", "runnerId": "runner-a", "taskId": "TASK-1", "step": "first"},
            self.config,
        )
        ingest_telemetry_event(
            self.bundle,
            {"eventId": "hb-2", "eventType": "heartbeat", "runnerId": "runner-a", "taskId": "TASK-1", "step": "second"},
            self.config,
        )

        state = read_json(self.root / ".zhenzhi" / "telemetry" / "current-state.json")
        self.assertEqual(len(state["states"]), 1)
        row = next(iter(state["states"].values()))
        self.assertEqual(row["lastStep"], "second")
        self.assertTrue(row["lastEventRef"].endswith("hb-2.json"))

    def test_dry_run_reports_without_mutation(self) -> None:
        event_ref = ingest_telemetry_event(
            self.bundle,
            {
                "eventId": "old-heartbeat",
                "eventType": "heartbeat",
                "runnerId": "runner-a",
                "eventTime": (NOW - timedelta(hours=4)).isoformat(),
            },
            self.config,
        )["eventRef"]

        report = TelemetryRetentionWorker(self.bundle, self.config).dry_run()

        self.assertEqual(report["mode"], "dry-run")
        self.assertEqual(report["counts"]["deleteCandidates"], 1)
        self.assertEqual(report["deleteCandidates"][0]["reason"], "expired_ephemeral_state")
        self.assertTrue((self.root / event_ref).exists())
        self.assertEqual(list((self.root / "knowledge" / "audit").glob("*.md")), [])

    def test_apply_skips_protected_refs_and_writes_single_batch_audit(self) -> None:
        event_ref = ingest_telemetry_event(
            self.bundle,
            {
                "eventId": "protected-heartbeat",
                "eventType": "heartbeat",
                "runnerId": "runner-a",
                "eventTime": (NOW - timedelta(hours=4)).isoformat(),
            },
            self.config,
        )["eventRef"]
        write_object(
            self.root / "task-results" / "tr-protected.md",
            f"""
type: TaskResult
taskId: TASK-PROTECTED
executorAgent: agent.company.development
status: done
summary: Protected telemetry evidence.
outputRefs: []
evidenceRefs:
  - {event_ref}
testsOrChecks:
  - fixture
qualityEvaluation: {{"passed": true}}
commonRulesEvaluation: {{"passed": true}}
acceptancePolicy: {{"acceptanceStatus": "accepted"}}
completedAt: "2026-06-23T12:00:00Z"
""",
        )

        report = TelemetryRetentionWorker(self.bundle, self.config).apply()

        self.assertEqual(report["counts"]["deleteCandidates"], 0)
        self.assertEqual(report["counts"]["protectedSkips"], 1)
        self.assertTrue((self.root / event_ref).exists())
        audit_paths = list((self.root / "knowledge" / "audit").glob("*.md"))
        actions = [load_object(path).get("action") for path in audit_paths]
        self.assertEqual(actions, ["telemetry.retention.apply"])


class TelemetryRetentionApplyTests(TelemetryRetentionCase):
    def test_learning_signals_are_promoted_and_not_deleted(self) -> None:
        event_ref = ingest_telemetry_event(
            self.bundle,
            {
                "eventId": "learning-error",
                "eventType": "error_report",
                "taskId": "TASK-LEARN",
                "eventTime": (NOW - timedelta(hours=4)).isoformat(),
                "learningReason": "quality_gate_failure",
                "errorSummary": "Quality gate failed after manual correction.",
            },
            self.config,
        )["eventRef"]

        report = TelemetryRetentionWorker(self.bundle, self.config).apply()

        self.assertTrue((self.root / event_ref).exists())
        self.assertEqual(report["counts"]["learningCandidates"], 1)
        self.assertEqual(len(report["promotionRefs"]), 2)
        promoted_types = {load_object(self.root / ref).get("type") for ref in report["promotionRefs"]}
        self.assertEqual(promoted_types, {"AgentImprovementProposal", "EvalCase"})

    def test_terminal_task_timeline_compacts_and_expired_hot_event_deletes(self) -> None:
        write_object(
            self.root / "projects" / "qa" / "tasks" / "task-done.md",
            """
type: ProjectTask
taskId: TASK-DONE
projectId: qa
title: Done task
status: done
workSourceType: feature
requirementRefs:
  - ANOS-REQ-161
""",
        )
        event_ref = ingest_telemetry_event(
            self.bundle,
            {
                "eventId": "old-progress",
                "eventType": "progress_update",
                "taskId": "TASK-DONE",
                "eventTime": (NOW - timedelta(hours=4)).isoformat(),
                "phase": "implementation",
                "message": "Implemented retention worker.",
            },
            self.config,
        )["eventRef"]

        report = TelemetryRetentionWorker(self.bundle, self.config).apply()

        self.assertFalse((self.root / event_ref).exists())
        self.assertEqual(len(report["summaryRefs"]), 1)
        summary = read_json(self.root / report["summaryRefs"][0])
        self.assertEqual(summary["type"], "TaskExecutionSummary")
        self.assertEqual(summary["taskId"], "TASK-DONE")
        self.assertEqual(summary["phaseTrail"], ["implementation"])

    def test_apply_writes_metrics_rollup_that_survives_raw_cleanup(self) -> None:
        ingest_telemetry_event(
            self.bundle,
            {
                "eventId": "tool-usage",
                "eventType": "tool_usage",
                "taskId": "TASK-METRIC",
                "eventTime": (NOW - timedelta(hours=4)).isoformat(),
                "tool": "pytest",
            },
            self.config,
        )
        ingest_telemetry_event(
            self.bundle,
            {
                "eventId": "model-usage",
                "eventType": "model_usage",
                "taskId": "TASK-METRIC",
                "eventTime": (NOW - timedelta(hours=4)).isoformat(),
                "model": "gpt-x",
            },
            self.config,
        )

        report = TelemetryRetentionWorker(self.bundle, self.config).apply()

        rollup = load_object(self.root / report["rollupRef"])
        self.assertEqual(rollup["type"], "MetricsReport")
        self.assertEqual(rollup["telemetryRetentionBatchRef"], report["batchRef"])
        self.assertEqual(rollup["eventsScanned"], 2)
        self.assertTrue((self.root / report["rollupRef"]).exists())


if __name__ == "__main__":
    unittest.main()
