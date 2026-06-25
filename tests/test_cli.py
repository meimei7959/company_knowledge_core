import tempfile
import threading
import unittest
import urllib.request
import urllib.error
import json
import contextlib
import io
import importlib.util
import os
import sys
import time
import types
from dataclasses import replace
from pathlib import Path

import zhenzhi_knowledge.feishu as feishu_module
import zhenzhi_knowledge.core as core_module
from zhenzhi_knowledge.cli import main
from zhenzhi_knowledge.core import Bundle, KnowledgeError, accept_project_task_result, append_log, apply_knowledge_approval_result, apply_knowledge_review_result, claim_project_task, create_audit_log, create_bugfix_task, create_defect, create_discussion_session, create_operations_feedback, create_outcome_slice, create_project_launch, create_project_manager_action, create_project_task, create_receiver_review, create_runner_invitation, create_task_notification, create_tool_registration_request, create_workbench_project, finalize_discussion_session, finish_project_task, heartbeat_agent_runner, list_notifications, list_review_queue, load_object, mark_notification_delivery, project_task_context_payload, publish_knowledge_bundle, pull_project_task, register_workbench_tool, schedule_project_tasks, search_index, search_retrieval, set_project_task_status, submit_discussion_turn, submit_runner_registration, update_frontmatter_file, validate_bundle, workbench_project_execution_read_model
from zhenzhi_knowledge.feishu import save_approval_request
from zhenzhi_knowledge.operational_store import backup_readiness, compact_error, ensure_operational_schema, live_readiness_report, operational_store_status, redact_url, rollback_operational_schema
from zhenzhi_knowledge.server import KnowledgeHTTPServer


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_minimal_bundle(root: Path) -> None:
    for directory in ["projects", "agents", "tools", "knowledge", "runs", "tasks", "sources", "task-results", "runners", "runner-invitations", "tool-registration-requests", "credential-requests", "notifications", "actors"]:
        (root / directory).mkdir(parents=True, exist_ok=True)
        (root / directory / "index.md").write_text(f"# {directory}\n", encoding="utf-8")
    (root / "index.md").write_text("# Index\n", encoding="utf-8")
    (root / "log.md").write_text("# Log\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")


def audit_actions(root: Path) -> list[str]:
    audit_dir = root / "knowledge" / "audit"
    if not audit_dir.exists():
        return []
    return [str(load_object(path).get("action", "")) for path in sorted(audit_dir.glob("*.md"))]


_FAKE_POSTGRES_DATABASES: dict[str, dict[str, list[dict[str, object]]]] = {}


class FakePostgresCursor:
    def __init__(self, rows: list[tuple], columns: list[str]):
        self._rows = rows
        self.description = [(column,) for column in columns]

    def fetchall(self) -> list[tuple]:
        return list(self._rows)

    def fetchone(self):
        return self._rows[0] if self._rows else None


class FakePostgresConnection:
    def __init__(self, url: str):
        self.storage = _FAKE_POSTGRES_DATABASES.setdefault(url, {})

    def execute(self, sql: str, params=()):
        normalized = " ".join(sql.lower().split())
        params = tuple(params or ())
        if normalized.startswith("select to_regclass"):
            table = str(params[0]).split(".")[-1]
            value = table if table in self.storage else None
            return FakePostgresCursor([(value,)], ["to_regclass"])
        if normalized.startswith("drop table if exists"):
            table = normalized.removeprefix("drop table if exists").strip().split()[0].strip('"')
            self.storage.pop(table, None)
            return FakePostgresCursor([], [])
        if normalized.startswith("create table") and (" objects " in f" {normalized} " or " objects(" in normalized):
            self.storage.setdefault("objects", [])
            return FakePostgresCursor([], [])
        if normalized.startswith("create table") and (" chunks " in f" {normalized} " or " chunks(" in normalized):
            self.storage.setdefault("chunks", [])
            return FakePostgresCursor([], [])
        if normalized.startswith("create table") and (" retrieval_index_meta " in f" {normalized} " or " retrieval_index_meta(" in normalized):
            self.storage.setdefault("retrieval_index_meta", [])
            return FakePostgresCursor([], [])
        for table in ["migration_versions", "operational_events", "api_command_envelopes", "feishu_delivery_attempts"]:
            if normalized.startswith("create table") and (f" {table} " in f" {normalized} " or f" {table}(" in normalized):
                self.storage.setdefault(table, [])
                return FakePostgresCursor([], [])
        if normalized.startswith("create index"):
            return FakePostgresCursor([], [])
        if normalized.startswith("insert into objects"):
            columns = ["path", "type", "title", "status", "owner", "scope", "projectId", "agentId", "toolId", "riskLevel", "updatedAt"]
            self.storage.setdefault("objects", []).append(dict(zip(columns, params)))
            return FakePostgresCursor([], [])
        if normalized.startswith("insert into chunks"):
            columns = ["path", "chunkId", "type", "title", "status", "owner", "scope", "projectId", "agentId", "toolId", "text", "vector", "sourceRef"]
            self.storage.setdefault("chunks", []).append(dict(zip(columns, params)))
            return FakePostgresCursor([], [])
        if normalized.startswith("insert into retrieval_index_meta"):
            columns = ["key", "value"]
            self.storage.setdefault("retrieval_index_meta", []).append(dict(zip(columns, params)))
            return FakePostgresCursor([], [])
        if normalized.startswith("insert into migration_versions"):
            columns = ["version", "appliedAt", "appliedBy", "checksum", "rollbackNotes"]
            self._upsert("migration_versions", "version", dict(zip(columns, params)))
            return FakePostgresCursor([], [])
        if normalized.startswith("insert into operational_events"):
            columns = ["eventId", "sourceChannel", "idempotencyKey", "actorRef", "projectRef", "targetRef", "status", "errorClass", "summary", "createdAt", "updatedAt"]
            self._upsert("operational_events", "eventId", dict(zip(columns, params)))
            return FakePostgresCursor([], [])
        if normalized.startswith("insert into api_command_envelopes"):
            columns = ["commandId", "route", "actorRef", "permissionDecision", "idempotencyKey", "requestHash", "responseHash", "auditRef", "notificationRefs", "status", "createdAt", "updatedAt"]
            self._upsert("api_command_envelopes", "commandId", dict(zip(columns, params)))
            return FakePostgresCursor([], [])
        if normalized.startswith("insert into feishu_delivery_attempts"):
            columns = ["attemptId", "eventId", "messageId", "cardId", "jobKey", "deliveryMethod", "responseCode", "retryCount", "finalStatus", "errorClass", "summary", "createdAt", "updatedAt"]
            self._upsert("feishu_delivery_attempts", "attemptId", dict(zip(columns, params)))
            return FakePostgresCursor([], [])
        if normalized.startswith("select count(*) from"):
            table = normalized.removeprefix("select count(*) from").strip().split()[0].strip('"')
            return FakePostgresCursor([(len(self.storage.get(table, [])),)], ["count"])
        if normalized.startswith('select version, "appliedat", "appliedby", checksum, "rollbacknotes" from migration_versions'):
            columns = ["version", "appliedAt", "appliedBy", "checksum", "rollbackNotes"]
            return FakePostgresCursor([tuple(row.get(column, "") for column in columns) for row in self.storage.get("migration_versions", [])], columns)
        if normalized.startswith("select value from retrieval_index_meta"):
            key = params[0] if params else "sourceFingerprint"
            rows = [row for row in self.storage.get("retrieval_index_meta", []) if row.get("key") == key]
            return FakePostgresCursor([(row["value"],) for row in rows], ["value"])
        if normalized.startswith("select path,") and " from objects" in normalized:
            rows = list(self.storage.get("objects", []))
            rows = self._filter_objects(sql, rows, params)
            rows.sort(key=lambda row: str(row["path"]))
            columns = ["path", "type", "title", "status", "owner", "scope", "projectId", "agentId", "toolId", "riskLevel"]
            return FakePostgresCursor([tuple(row[column] for column in columns) for row in rows], columns)
        if normalized.startswith("select path,") and " from chunks" in normalized:
            rows = list(self.storage.get("chunks", []))
            columns = ["path", "chunkId", "type", "title", "status", "owner", "scope", "projectId", "agentId", "toolId", "text", "vector", "sourceRef"]
            return FakePostgresCursor([tuple(row[column] for column in columns) for row in rows], columns)
        raise AssertionError(f"unexpected SQL: {sql}")

    def _upsert(self, table: str, key: str, row: dict[str, object]) -> None:
        rows = self.storage.setdefault(table, [])
        for index, existing in enumerate(rows):
            if existing.get(key) == row.get(key):
                rows[index] = {**existing, **row}
                return
        rows.append(row)

    def _filter_objects(self, sql: str, rows: list[dict[str, object]], params: tuple) -> list[dict[str, object]]:
        index = 0
        filtered = rows
        for marker, column in [
            ('"type" = %s', "type"),
            ("status = %s", "status"),
            ('"projectId" = %s', "projectId"),
            ('"agentId" = %s', "agentId"),
            ('"toolId" = %s', "toolId"),
            ('"riskLevel" = %s', "riskLevel"),
            ("owner = %s", "owner"),
            ("scope = %s", "scope"),
        ]:
            if marker in sql:
                value = params[index]
                index += 1
                filtered = [row for row in filtered if row.get(column) == value]
        if "path ilike %s or title ilike %s" in sql.lower():
            needle = str(params[index]).strip("%").lower()
            filtered = [
                row
                for row in filtered
                if needle in str(row.get("path", "")).lower() or needle in str(row.get("title", "")).lower()
            ]
        return filtered

    def commit(self) -> None:
        return None

    def close(self) -> None:
        return None


def fake_psycopg_module() -> types.ModuleType:
    module = types.ModuleType("psycopg")
    module.connect = lambda url: FakePostgresConnection(url)
    return module


def minimal_feishu_settings(**overrides):
    values = {
        "app_id": "",
        "app_secret": "",
        "verification_token": "expected-token",
        "reply_enabled": False,
        "token_auto_approve": False,
        "approval_enabled": False,
        "approval_code_project": "",
        "approval_code_common": "",
        "approval_code_security": "",
        "approval_node_approver_key": "",
        "common_reviewer_open_ids": [],
        "security_reviewer_open_ids": [],
        "project_reviewer_open_ids": {},
        "token_send_on_approval": False,
        "approval_doc_folder_token": "",
        "approval_doc_folder_tokens": {},
        "approval_doc_domain": "https://xcn68awb7dsi.feishu.cn",
        "approval_doc_share_names": [],
        "user_open_id_map": {},
    }
    values.update(overrides)
    return feishu_module.FeishuSettings(**values)


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self._previous_database_url = os.environ.get("DATABASE_URL")
        self._previous_psycopg = sys.modules.get("psycopg")
        self._test_database_url = f"postgresql://test/{self.id().replace('.', '_')}"
        os.environ["DATABASE_URL"] = self._test_database_url
        _FAKE_POSTGRES_DATABASES.pop(self._test_database_url, None)
        sys.modules["psycopg"] = fake_psycopg_module()

    def tearDown(self) -> None:
        if self._previous_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = self._previous_database_url
        if self._previous_psycopg is None:
            sys.modules.pop("psycopg", None)
        else:
            sys.modules["psycopg"] = self._previous_psycopg
        _FAKE_POSTGRES_DATABASES.pop(self._test_database_url, None)

    def test_append_log_strips_trailing_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            append_log(Bundle(root), "finished task DEMO status=done \t\nhandoff=agent.company.test  ")

            log_lines = (root / "log.md").read_text(encoding="utf-8").splitlines()
            self.assertTrue(log_lines[-1].endswith("handoff=agent.company.test"))
            self.assertTrue(all(line == line.rstrip(" \t") for line in log_lines))

    def test_task_source_traceability_validation_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            feature = create_project_task(
                bundle,
                "Feature without requirement",
                "qa",
                "agent.company.project-manager",
                "agent.company.development",
                task_type="engineering_action",
                task_id="TSRR-FEATURE-MISSING",
                work_source_type="feature",
                source_material_refs=["docs/product/example.md"],
            )
            problems = validate_bundle(bundle)
            self.assertTrue(any("feature task requires requirementRefs" in problem for problem in problems))
            update_frontmatter_file(feature, {"requirementRefs": ["REQ-001"], "updatedAt": "2026-06-23T00:00:00Z"})

            bugfix = create_project_task(
                bundle,
                "Bugfix without defect",
                "qa",
                "agent.company.project-manager",
                "agent.company.development",
                task_type="engineering_action",
                task_id="TSRR-BUGFIX-MISSING",
                work_source_type="bugfix",
                source_reason="Fix observed bug",
            )
            problems = validate_bundle(bundle)
            self.assertTrue(any("bugfix task requires defectRefs" in problem for problem in problems))
            defect = create_defect(bundle, "Broken flow", "qa", "agent.company.test", defect_id="DEFECT-001")
            update_frontmatter_file(
                bugfix,
                {
                    "defectRefs": ["DEFECT-001"],
                    "defectObjectRefs": [str(defect.relative_to(root))],
                    "updatedAt": "2026-06-23T00:00:00Z",
                },
            )
            maintenance = root / "projects" / "qa" / "tasks" / "tsrr-maintenance-missing.md"
            maintenance.parent.mkdir(parents=True, exist_ok=True)
            maintenance.write_text(
                """---
type: ProjectTask
title: Maintenance without source
taskId: TSRR-MAINTENANCE-MISSING
taskType: maintenance
projectId: qa
workSourceType: maintenance
requirementRefs: []
defectRefs: []
sourceReason: ""
sourceMaterialRefs: []
expectedOutput: []
requester: agent.company.project-manager
assignee: agent.company.development
status: pending
---

## Request

Maintenance task missing source inputs.
""",
                encoding="utf-8",
            )
            problems = validate_bundle(bundle)
            self.assertTrue(any("maintenance task requires sourceReason, sourceMaterialRefs, or expectedOutput" in problem for problem in problems))
            update_frontmatter_file(maintenance, {"sourceReason": "Scheduled cleanup has operational evidence.", "updatedAt": "2026-06-23T00:00:00Z"})
            self.assertFalse([problem for problem in validate_bundle(bundle) if "TSRR-" in problem])

    def test_receiver_review_decision_rules_and_task_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            task = create_project_task(
                bundle,
                "Implement reviewed input",
                "qa",
                "agent.company.project-manager",
                "agent.company.development",
                task_type="engineering_action",
                task_id="TSRR-REVIEWED",
                work_source_type="feature",
                requirement_refs=["REQ-001"],
            )
            accepted = create_receiver_review(
                bundle,
                "qa",
                str(task.relative_to(root)),
                "agent.company.development",
                "agent.company.development",
                "accepted_for_work",
                artifact_refs=[str(task.relative_to(root))],
                checklist=["Upstream task has requirementRefs."],
            )
            self.assertIn(str(accepted.relative_to(root)), load_object(task)["receiverReviewRefs"])
            create_receiver_review(
                bundle,
                "qa",
                str(task.relative_to(root)),
                "agent.company.development",
                "agent.company.development",
                "accepted_with_assumptions",
                assumptions=["API naming may be adjusted during implementation."],
                checklist=["Assumption recorded."],
            )
            with self.assertRaises(KnowledgeError):
                create_receiver_review(bundle, "qa", str(task.relative_to(root)), "agent.company.development", "agent.company.development", "accepted_with_assumptions")
            with self.assertRaises(KnowledgeError):
                create_receiver_review(bundle, "qa", str(task.relative_to(root)), "agent.company.development", "agent.company.development", "needs_rework")
            self.assertFalse([problem for problem in validate_bundle(bundle) if "ReceiverReview" in problem])

    def test_pm_delivery_gate_blocks_premature_closeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            requirement_ref = "REQ-PM-GATE-001"
            dev_task = create_project_task(
                bundle,
                "Implement gated feature",
                "qa",
                "agent.company.project-manager",
                "agent.company.development",
                task_type="implementation",
                task_id="PM-GATE-DEV",
                work_source_type="feature",
                requirement_refs=[requirement_ref],
            )
            test_task = create_project_task(
                bundle,
                "Test gated feature",
                "qa",
                "agent.company.project-manager",
                "agent.company.test",
                task_type="test_validation",
                task_id="PM-GATE-TEST",
                work_source_type="feature",
                requirement_refs=[requirement_ref],
            )
            update_frontmatter_file(test_task, {"status": "blocked", "updatedAt": "2026-06-23T00:00:00Z"})
            closeout_task = create_project_task(
                bundle,
                "PM closeout gated feature",
                "qa",
                "agent.company.project-manager",
                "agent.company.project-manager",
                task_type="pm_closeout",
                task_id="PM-GATE-CLOSEOUT",
                work_source_type="feature",
                requirement_refs=[requirement_ref],
            )
            closeout_result = finish_project_task(
                bundle,
                "PM-GATE-CLOSEOUT",
                "done",
                "Closing should be blocked by delivery gate.",
                output_refs=["release-note.md"],
                evidence_refs=["pm-review.md"],
                tests_or_checks=["pm review attempted"],
                executor_agent="agent.company.project-manager",
            )
            problems = validate_bundle(bundle)
            self.assertTrue(any("PM closeout TaskResult requires pmDeliveryGate.enforce true" in problem for problem in problems))
            review_dir = root / "projects" / "qa" / "reviews"
            review_dir.mkdir(parents=True, exist_ok=True)
            closeout_review = review_dir / "pm-final-closeout.md"
            closeout_review.write_text(
                """---
type: ReviewRecord
title: PM final closeout
projectId: qa
taskId: PM-GATE-CLOSEOUT
reviewAgent: agent.company.project-manager
status: done
decision: accepted
evidenceRefs:
  - pm-review.md
---

# Review
""",
                encoding="utf-8",
            )
            problems = validate_bundle(bundle)
            self.assertTrue(any("PM closeout artifact requires pmDeliveryGate.enforce true or pmCloseoutScope process_status_only" in problem for problem in problems))
            update_frontmatter_file(closeout_review, {"pmCloseoutScope": "process_status_only", "updatedAt": "2026-06-23T00:00:00Z"})
            update_frontmatter_file(
                closeout_result,
                {
                    "pmDeliveryGate": {"enforce": True, "requirementRefs": [requirement_ref]},
                    "qualityEvaluation": {"status": "passed", "decision": "close"},
                    "acceptancePolicy": {"acceptanceStatus": "accepted"},
                    "updatedAt": "2026-06-23T00:00:00Z",
                },
            )

            problems = validate_bundle(bundle)
            self.assertTrue(any("cannot close while Development task PM-GATE-DEV is pending without TaskResult" in problem for problem in problems))
            self.assertTrue(any("cannot close while Test task PM-GATE-TEST is blocked without TaskResult" in problem for problem in problems))
            self.assertTrue(any("requires Product Manager acceptance TaskResult" in problem for problem in problems))

            dev_result = finish_project_task(
                bundle,
                "PM-GATE-DEV",
                "done",
                "Implemented gated feature.",
                output_refs=["src/feature.py"],
                evidence_refs=["tests/dev.log"],
                tests_or_checks=["unit passed"],
                executor_agent="agent.company.development",
            )
            update_frontmatter_file(
                dev_result,
                {
                    "status": "failed",
                    "qualityEvaluation": {"status": "failed", "decision": "repair_required"},
                    "acceptancePolicy": {"acceptanceStatus": "rejected"},
                    "updatedAt": "2026-06-23T00:00:00Z",
                },
            )
            problems = validate_bundle(bundle)
            self.assertTrue(any("requires passing Development TaskResult for PM-GATE-DEV" in problem for problem in problems))
            update_frontmatter_file(
                dev_result,
                {
                    "status": "done",
                    "qualityEvaluation": {"status": "passed", "decision": "close"},
                    "acceptancePolicy": {"acceptanceStatus": "accepted"},
                    "updatedAt": "2026-06-23T00:00:00Z",
                },
            )
            pm_aggregate = finish_project_task(
                bundle,
                "PM-GATE-CLOSEOUT",
                "done",
                "PM aggregates delegated delivery outputs.",
                output_refs=["src/feature.py", "src/unowned.py"],
                evidence_refs=[str(dev_result.relative_to(root))],
                tests_or_checks=["delegated output provenance checked"],
                executor_agent="agent.company.project-manager",
            )
            update_frontmatter_file(
                pm_aggregate,
                {
                    "pmDeliveryGate": {"enforce": True, "requirementRefs": [requirement_ref]},
                    "qualityEvaluation": {"status": "passed", "decision": "close"},
                    "acceptancePolicy": {"acceptanceStatus": "accepted"},
                    "updatedAt": "2026-06-23T00:00:00Z",
                },
            )
            problems = validate_bundle(bundle)
            self.assertFalse(any("src/feature.py" in problem and "owning Agent TaskResult provenance" in problem for problem in problems))
            self.assertTrue(any("src/unowned.py" in problem and "owning Agent TaskResult provenance" in problem for problem in problems))
            delegated_task = create_project_task(
                bundle,
                "Implement delegated unowned output",
                "qa",
                "agent.company.project-manager",
                "agent.company.development",
                task_type="implementation",
                task_id="PM-GATE-DELEGATED-DEV",
                work_source_type="feature",
                requirement_refs=[requirement_ref],
            )
            delegated_result = finish_project_task(
                bundle,
                "PM-GATE-DELEGATED-DEV",
                "done",
                "Implemented second delegated output.",
                output_refs=["src/unowned.py"],
                evidence_refs=["tests/delegated.log"],
                tests_or_checks=["unit passed"],
                executor_agent="agent.company.development",
            )
            update_frontmatter_file(
                delegated_result,
                {
                    "status": "done",
                    "qualityEvaluation": {"status": "passed", "decision": "close"},
                    "acceptancePolicy": {"acceptanceStatus": "accepted"},
                    "updatedAt": "2026-06-23T00:00:00Z",
                },
            )
            test_result = finish_project_task(
                bundle,
                "PM-GATE-TEST",
                "done",
                "Validated gated feature.",
                output_refs=["test-report.md"],
                evidence_refs=["tests/test.log"],
                tests_or_checks=["acceptance passed"],
                executor_agent="agent.company.test",
            )
            update_frontmatter_file(
                test_result,
                {
                    "status": "done",
                    "qualityEvaluation": {"status": "passed", "decision": "close"},
                    "acceptancePolicy": {"acceptanceStatus": "accepted"},
                    "updatedAt": "2026-06-23T00:00:00Z",
                },
            )
            product_task = create_project_task(
                bundle,
                "Product acceptance gated feature",
                "qa",
                "agent.company.project-manager",
                "agent.company.product-manager",
                task_type="product_acceptance",
                task_id="PM-GATE-PRODUCT",
                work_source_type="feature",
                requirement_refs=[requirement_ref],
            )
            product_result = finish_project_task(
                bundle,
                "PM-GATE-PRODUCT",
                "done",
                "Product accepted gated feature.",
                output_refs=["product-review.md"],
                evidence_refs=["test-report.md"],
                tests_or_checks=["product acceptance passed"],
                executor_agent="agent.company.product-manager",
            )
            update_frontmatter_file(
                product_result,
                {
                    "status": "done",
                    "qualityEvaluation": {"status": "passed", "decision": "close"},
                    "acceptancePolicy": {"acceptanceStatus": "accepted"},
                    "updatedAt": "2026-06-23T00:00:00Z",
                },
            )
            self.assertFalse([problem for problem in validate_bundle(bundle) if "pmDeliveryGate" in problem])

    def test_pm_action_runtime_records_and_validates_state_transition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "project",
                        "outcome-slice",
                        "--project",
                        "qa",
                        "--title",
                        "QA implementation slice",
                        "--stage-goal",
                        "Move approved requirement into implementable development work.",
                        "--main-deliverable",
                        "Development Agent owned implementation TaskResult.",
                        "--current-state",
                        "clarified",
                        "--target-state",
                        "implementable",
                        "--outcome-slice-id",
                        "qa-implementation-slice",
                        "--primary-agent",
                        "agent.company.development",
                        "--upstream-agent",
                        "agent.company.product-manager",
                        "--downstream-agent",
                        "agent.company.test",
                        "--handoff-agent",
                        "agent.company.architecture",
                        "--handoff-agent",
                        "agent.company.development",
                        "--handoff-agent",
                        "agent.company.test",
                        "--escalation-agent",
                        "agent.company.architecture",
                        "--escalation-rule",
                        "Architecture risk or data model boundary is unclear.",
                        "--stop-condition",
                        "Stop when development ownership or evidence is missing.",
                        "--token-budget",
                        "20000",
                        "--wip-limit",
                        "2",
                    ]
                ),
                0,
            )
            outcome_ref = "projects/qa/outcome-slices/qa-implementation-slice.md"
            outcome = load_object(root / outcome_ref)
            self.assertEqual(outcome["primaryAgent"], "agent.company.development")
            self.assertEqual(outcome["upstreamAgent"], "agent.company.product-manager")
            self.assertEqual(outcome["downstreamAgent"], "agent.company.test")
            self.assertEqual(outcome["handoffChain"], ["agent.company.architecture", "agent.company.development", "agent.company.test"])
            self.assertEqual(outcome["escalationAgents"], ["agent.company.architecture"])
            task_path = create_project_task(
                bundle,
                "Implement delegated feature",
                "qa",
                "agent.company.project-manager",
                "agent.company.development",
                task_type="implementation",
                task_id="PM-ACTION-DEV",
                work_source_type="feature",
                requirement_refs=["REQ-PM-ACTION-001"],
                outcome_slice_ref=outcome_ref,
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "project",
                        "pm-action",
                        "--project",
                        "qa",
                        "--actor",
                        "agent.company.project-manager",
                        "--intent",
                        "dispatch",
                        "--current-state",
                        "requirement_ready",
                        "--allowed-transition",
                        "dispatch_to_development",
                        "--exit-state",
                        "dispatched",
                        "--summary",
                        "Dispatch implementation to Development Agent.",
                        "--cost-summary",
                        "One PM dispatch write; cost is bounded because evidence and target owner are already known.",
                        "--record-written",
                        str(task_path.relative_to(root)),
                        "--delegated-owner",
                        "agent.company.development",
                        "--next-action",
                        "Development Agent writes TaskResult.",
                    ]
                ),
                0,
            )
            actions = [path for path in (root / "projects" / "qa" / "pm-actions").glob("*.md") if path.name != "index.md"]
            self.assertEqual(len(actions), 1)
            action = load_object(actions[0])
            self.assertEqual(action["type"], "ProjectManagerAction")
            self.assertEqual(action["exitState"], "dispatched")
            self.assertTrue(any("ProjectManagerAction intent dispatch requires outcomeSliceRef" in problem for problem in validate_bundle(bundle)))
            update_frontmatter_file(
                actions[0],
                {
                    "outcomeSliceRef": outcome_ref,
                    "outcomeStateBefore": "clarified",
                    "outcomeStateAfter": "implementable",
                    "outcomeValueChange": "Development Agent can now accept concrete implementation work.",
                    "guardrailDecision": "continue",
                    "updatedAt": "2026-06-25T00:00:00Z",
                },
            )
            self.assertFalse([problem for problem in validate_bundle(bundle) if "ProjectManagerAction" in problem])

            unowned_task = create_project_task(
                bundle,
                "Unplanned design work",
                "qa",
                "agent.company.project-manager",
                "agent.company.design",
                task_type="design_action",
                task_id="PM-ACTION-DESIGN-UNOWNED",
                work_source_type="feature",
                requirement_refs=["REQ-PM-ACTION-001"],
                outcome_slice_ref=outcome_ref,
            )
            problems = validate_bundle(bundle)
            self.assertTrue(any("is not allowed by OutcomeSlice agent ownership" in problem for problem in problems))
            update_frontmatter_file(unowned_task, {"assignee": "agent.company.architecture", "updatedAt": "2026-06-25T00:00:00Z"})
            self.assertFalse([problem for problem in validate_bundle(bundle) if "OutcomeSlice agent ownership" in problem])

            update_frontmatter_file(root / outcome_ref, {"downstreamAgent": "agent.company.architecture, agent.company.development", "updatedAt": "2026-06-25T00:00:00Z"})
            self.assertTrue(any("OutcomeSlice downstreamAgent must be one canonical Agent id" in problem for problem in validate_bundle(bundle)))

            with self.assertRaises(KnowledgeError):
                create_outcome_slice(
                    bundle,
                    "qa",
                    "Bad human labels",
                    "agent.company.project-manager",
                    "Check invalid labels.",
                    "Invalid labels should be rejected.",
                    "clarified",
                    "implementable",
                    stop_conditions=["Stop immediately."],
                    primary_agent="QA Agent",
                    downstream_agent="PM Agent / Development Agent",
                )

            blocked = create_project_manager_action(
                bundle,
                "qa",
                "agent.company.project-manager",
                "blocker_record",
                "test_waiting",
                "record_blocker",
                "blocked_with_owner",
                "Blocked without owner should fail validation.",
                blocker="Missing external environment.",
                cost_summary="One blocker record; cost is bounded because missing environment is already known.",
            )
            problems = validate_bundle(bundle)
            self.assertTrue(any("blocked_with_owner PM action requires blocker and blockerOwner" in problem for problem in problems))
            update_frontmatter_file(root / blocked["actionRef"], {"blockerOwner": "meimei", "updatedAt": "2026-06-23T00:00:00Z"})
            self.assertFalse([problem for problem in validate_bundle(bundle) if "ProjectManagerAction" in problem])
            bad_record = create_project_manager_action(
                bundle,
                "qa",
                "agent.company.project-manager",
                "dispatch",
                "implementation_needed",
                "record_written_artifact",
                "waiting_acceptance",
                "PM cannot record code as written without owning Agent provenance.",
                records_written=["src/unowned.py"],
                next_action="Route to Development Agent.",
                outcome_slice_ref=outcome_ref,
                outcome_state_before="clarified",
                outcome_state_after="implementable",
                outcome_value_change="Unowned record should still fail provenance before the outcome can advance.",
                cost_summary="One provenance validation record; no extra Agent dispatch until ownership is fixed.",
                guardrail_decision="continue",
            )
            problems = validate_bundle(bundle)
            self.assertTrue(any("ProjectManagerAction recordsWritten lacks owning Agent TaskResult provenance: src/unowned.py" in problem for problem in problems))
            update_frontmatter_file(root / bad_record["actionRef"], {"recordsWritten": [], "evidenceRefs": ["src/unowned.py"], "updatedAt": "2026-06-23T00:00:00Z"})
            self.assertFalse([problem for problem in validate_bundle(bundle) if "ProjectManagerAction" in problem])

    def test_finish_project_task_inherits_traceability_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            defect = create_defect(bundle, "Regression bug", "qa", "agent.company.test", defect_id="DEFECT-002")
            task = create_bugfix_task(bundle, "DEFECT-002", "Fix regression bug", "agent.company.test", "agent.company.development")
            review = create_receiver_review(
                bundle,
                "qa",
                str(task.relative_to(root)),
                "agent.company.development",
                "agent.company.development",
                "accepted_for_work",
                checklist=["Defect has reproduction evidence or explicit TBD."],
            )
            result = finish_project_task(
                bundle,
                str(load_object(task)["taskId"]),
                "done",
                "Fixed defect and ran regression.",
                output_refs=["src/fix.py"],
                evidence_refs=["tests/regression.log"],
                tests_or_checks=["regression passed"],
                executor_agent="agent.company.development",
            )
            result_fm = load_object(result)
            self.assertEqual("bugfix", result_fm["workSourceType"])
            self.assertEqual(["DEFECT-002"], result_fm["defectRefs"])
            self.assertEqual([str(defect.relative_to(root))], result_fm["defectObjectRefs"])
            self.assertIn(str(review.relative_to(root)), result_fm["receiverReviewRefs"])
            defect_fm = load_object(defect)
            self.assertEqual("fixed", defect_fm["status"])
            self.assertIn(str(result.relative_to(root)), defect_fm["regressionEvidenceRefs"])

    def test_project_health_reports_traceability_receiver_review_and_defect_risks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            task = create_project_task(
                bundle,
                "Bad feature",
                "qa",
                "agent.company.project-manager",
                "agent.company.development",
                task_type="engineering_action",
                task_id="TSRR-HEALTH-FEATURE",
                work_source_type="feature",
                source_material_refs=["docs/product/example.md"],
            )
            create_receiver_review(
                bundle,
                "qa",
                str(task.relative_to(root)),
                "agent.company.development",
                "agent.company.development",
                "human_decision_required",
                issues=["Product owner must decide missing scope."],
            )
            defect = create_defect(bundle, "Fixed but not regressed", "qa", "agent.company.test", defect_id="DEFECT-003")
            update_frontmatter_file(defect, {"status": "fixed", "fixTaskRefs": ["projects/qa/tasks/fix.md"]})
            health = core_module.run_project_manager_health_check(bundle, "qa", "agent.company.project-manager")
            review_body = (root / health["reviewRef"]).read_text(encoding="utf-8")
            self.assertIn("feature task requires requirementRefs", review_body)
            self.assertIn("ReceiverReview needs human decision", review_body)
            self.assertIn("fixed but has no regression evidence", review_body)

    def test_cli_defect_receiver_review_and_task_source_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "create",
                        "--title",
                        "CLI feature",
                        "--project",
                        "qa",
                        "--requester",
                        "agent.company.project-manager",
                        "--assignee",
                        "agent.company.development",
                        "--type",
                        "engineering_action",
                        "--task-id",
                        "CLI-FEATURE",
                        "--work-source-type",
                        "feature",
                        "--requirement-ref",
                        "REQ-CLI",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(["--root", str(root), "defect", "create", "--title", "CLI defect", "--project", "qa", "--reporter", "agent.company.test", "--defect-id", "DEFECT-CLI", "--actual-behavior", "broken"]),
                0,
            )
            self.assertEqual(
                main(["--root", str(root), "defect", "create-fix-task", "DEFECT-CLI", "--requester", "agent.company.test", "--assignee", "agent.company.development", "--title", "Fix CLI defect"]),
                0,
            )
            self.assertEqual(
                main(["--root", str(root), "receiver-review", "create", "--project", "qa", "--upstream-ref", "projects/qa/tasks/cli-feature.md", "--receiver-agent", "agent.company.development", "--decision", "accepted_for_work", "--check", "Requirement ref present"]),
                0,
            )
            self.assertFalse(validate_bundle(Bundle(root)))

    def test_api_task_defect_receiver_review_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            try:
                server = KnowledgeHTTPServer(("127.0.0.1", 0), bundle, api_token="test-token")
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"

            def post(path: str, payload: dict) -> dict:
                request = urllib.request.Request(base + path, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"}, method="POST")
                with urllib.request.urlopen(request) as response:
                    return json.loads(response.read().decode("utf-8"))

            def get(path: str) -> dict:
                request = urllib.request.Request(base + path, headers={"Authorization": "Bearer test-token"}, method="GET")
                with urllib.request.urlopen(request) as response:
                    return json.loads(response.read().decode("utf-8"))

            try:
                lease_response = post(
                    "/v0/pm-control-lease/acquire",
                    {"projectId": "qa", "pmAgentId": "agent.company.project-manager", "runnerId": "runner.pm", "deviceId": "device.local", "idempotencyKey": "api-source-acquire"},
                )
                lease = lease_response["lease"]
                task = post(
                    "/v0/tasks/create",
                    {
                        "projectId": "qa",
                        "title": "API source task",
                        "requester": "agent.company.project-manager",
                        "assignee": "agent.company.development",
                        "taskType": "engineering_action",
                        "taskId": "API-SOURCE",
                        "workSourceType": "feature",
                        "requirementRefs": ["REQ-API"],
                        "acceptanceCriteriaRefs": ["AC-API"],
                        "pmAgentId": "agent.company.project-manager",
                        "leaseId": lease["leaseId"],
                        "leaseGeneration": lease["leaseGeneration"],
                    },
                )
                self.assertEqual("feature", task["task"]["workSourceType"])
                defect = post(
                    "/v0/defects",
                    {
                        "projectId": "qa",
                        "title": "API defect",
                        "reporter": "agent.company.test",
                        "defectId": "DEFECT-API",
                        "actualBehavior": "broken",
                    },
                )
                self.assertEqual("DEFECT-API", defect["defect"]["defectId"])
                fix = post(
                    "/v0/defects/create-fix-task",
                    {"defectId": "DEFECT-API", "requester": "agent.company.test", "assignee": "agent.company.development"},
                )
                self.assertEqual("bugfix", fix["task"]["workSourceType"])
                review = post(
                    "/v0/receiver-reviews",
                    {
                        "projectId": "qa",
                        "upstreamRef": task["taskRef"],
                        "receiverAgent": "agent.company.development",
                        "decision": "accepted_for_work",
                        "checklist": ["API task has requirementRefs."],
                    },
                )
                self.assertEqual("accepted_for_work", review["receiverReview"]["decision"])
                self.assertTrue(get("/v0/defects?projectId=qa")["defects"])
                self.assertTrue(get("/v0/receiver-reviews?projectId=qa")["receiverReviews"])
            finally:
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()

    def test_phase2_workbench_registration_core_is_idempotent_audited_and_readonly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)

            project = create_workbench_project(
                bundle,
                "phase2-core",
                "Phase 2 Core",
                "user.meimei",
                repository_refs=[str(root)],
                default_assignees=["agent.company.project-manager"],
                actor="user.meimei",
                idempotency_key="idem-project",
                permissions=["project.create"],
            )
            self.assertEqual("WorkbenchProject", project["kind"])
            self.assertFalse(project["idempotent"])
            self.assertEqual("active", load_object(root / project["projectRef"])["status"])
            duplicate_project = create_workbench_project(
                bundle,
                "phase2-core",
                "Phase 2 Core Duplicate",
                "user.meimei",
                actor="user.meimei",
                idempotency_key="idem-project",
                permissions=["project.create"],
            )
            self.assertTrue(duplicate_project["idempotent"])
            self.assertEqual(project["projectRef"], duplicate_project["projectRef"])

            with self.assertRaises(KnowledgeError):
                create_runner_invitation(
                    bundle,
                    "phase2-core",
                    "Denied Laptop",
                    actor="user.meimei",
                    idempotency_key="idem-denied-runner",
                    permissions=[],
                )
            self.assertIn("workbench.permission.denied", audit_actions(root))

            invitation = create_runner_invitation(
                bundle,
                "phase2-core",
                "Meimei MacBook Pro",
                ["development", "git"],
                runner_owner="user.meimei",
                actor="user.meimei",
                idempotency_key="idem-runner-invite",
                permissions=["runner.invitation.create"],
            )
            self.assertEqual("RunnerInvitation", invitation["kind"])
            self.assertIn("pairingCode", invitation)
            self.assertEqual("auto_approved", invitation["approvalStatus"])
            duplicate_invitation = create_runner_invitation(
                bundle,
                "phase2-core",
                "Meimei MacBook Pro",
                actor="user.meimei",
                idempotency_key="idem-runner-invite",
                permissions=["runner.invitation.create"],
            )
            self.assertTrue(duplicate_invitation["idempotent"])

            pending_runner = submit_runner_registration(
                bundle,
                "runner.uninvited",
                "Uninvited Runner",
                available_projects=["phase2-core"],
                idempotency_key="idem-runner-uninvited",
            )
            self.assertEqual("pending_authorization", pending_runner["approvalStatus"])
            self.assertEqual([], pending_runner["allowedProjects"])
            registered_runner = submit_runner_registration(
                bundle,
                "runner.meimei-mbp",
                "Meimei MBP",
                pairing_code=invitation["pairingCode"],
                capabilities=["development", "git"],
                available_projects=["phase2-core"],
                repo_access=[str(root)],
                owner="user.meimei",
                idempotency_key="idem-runner-register",
            )
            self.assertEqual("auto_approved", registered_runner["approvalStatus"])
            self.assertEqual(["phase2-core"], registered_runner["allowedProjects"])
            self.assertTrue(registered_runner["runnerToken"].startswith("runner-token."))
            runner_object = load_object(root / registered_runner["runnerRef"])
            self.assertEqual("online_readonly", runner_object["status"])
            self.assertEqual("", runner_object.get("leaseTokenHash", ""))

            tool = register_workbench_tool(
                bundle,
                "phase2-core",
                "local-git-status",
                "cli",
                "low",
                ["read_repo_status"],
                ["runner.meimei-mbp"],
                owner="user.meimei",
                actor="user.meimei",
                idempotency_key="idem-tool-register",
                permissions=["tool.register.low_risk"],
            )
            self.assertEqual("ToolAsset", tool["kind"])
            self.assertEqual("auto_approved", tool["approvalStatus"])
            self.assertEqual("approved", load_object(root / tool["toolRef"])["status"])
            with self.assertRaises(KnowledgeError):
                register_workbench_tool(
                    bundle,
                    "phase2-core",
                    "writer",
                    "cli",
                    "high",
                    ["write_repo"],
                    actor="user.meimei",
                    idempotency_key="idem-tool-high",
                    permissions=["tool.register.low_risk"],
                )

            tool_request = create_tool_registration_request(
                bundle,
                "phase2-core",
                "lark-approval-writer",
                "lark_api",
                "high",
                ["create_approval_instance"],
                "secret_ref_required",
                "user.meimei",
                "审批闭环需要写入飞书审批实例。",
                data_scopes=["approval"],
                runner_scopes=["runner.meimei-mbp"],
                actor="user.meimei",
                idempotency_key="idem-tool-request",
                permissions=["tool.registration_request.create"],
            )
            self.assertEqual("ToolRegistrationRequest", tool_request["kind"])
            self.assertEqual("pending_review", tool_request["approvalStatus"])
            self.assertTrue(tool_request["approvalTaskRef"])
            self.assertEqual("pending_review", load_object(root / tool_request["requestRef"])["status"])

            read_model = workbench_project_execution_read_model(bundle, "phase2-core")
            self.assertTrue(read_model["readOnly"])
            self.assertFalse(read_model["commandSurface"]["dispatchTask"])
            self.assertFalse(read_model["commandSurface"]["repairTask"])
            self.assertFalse(read_model["commandSurface"]["overwriteTaskResult"])
            self.assertFalse(read_model["commandSurface"]["editAgentRun"])
            self.assertFalse(read_model["commandSurface"]["forceCompleteTask"])
            self.assertFalse(read_model["commandSurface"]["claimAsWorkbench"])
            self.assertNotIn("dispatchTask", json.dumps(read_model["allowedRequestObjects"]))

            actions = audit_actions(root)
            for expected_action in [
                "workbench.project.create",
                "runner.invitation.create",
                "runner.registration_request.create",
                "runner.register",
                "runner.pairing.consume",
                "tool.register",
                "tool.registration_request.create",
            ]:
                self.assertIn(expected_action, actions)

    def test_phase2_workbench_api_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            try:
                server = KnowledgeHTTPServer(("127.0.0.1", 0), Bundle(root), api_token="test-token")
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"

            def post(path: str, payload: dict) -> dict:
                request = urllib.request.Request(
                    base + path,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"},
                    method="POST",
                )
                with urllib.request.urlopen(request) as response:
                    return json.loads(response.read().decode("utf-8"))

            def get(path: str) -> dict:
                request = urllib.request.Request(base + path, headers={"Authorization": "Bearer test-token"})
                with urllib.request.urlopen(request) as response:
                    return json.loads(response.read().decode("utf-8"))

            try:
                project = post(
                    "/v0/workbench/projects",
                    {
                        "projectId": "api-phase2",
                        "name": "API Phase 2",
                        "owner": "user.meimei",
                        "repositoryRefs": [str(root)],
                        "idempotencyKey": "api-project",
                        "permissions": ["project.create"],
                    },
                )
                self.assertEqual("WorkbenchProject", project["kind"])
                self.assertTrue(post("/v0/workbench/projects", {"projectId": "api-phase2", "name": "API Phase 2", "owner": "user.meimei", "idempotencyKey": "api-project", "permissions": ["project.create"]})["idempotent"])

                invitation = post(
                    "/v0/workbench/runner-invitations",
                    {
                        "projectId": "api-phase2",
                        "runnerLabel": "API Runner",
                        "requestedCapabilities": ["development"],
                        "idempotencyKey": "api-runner-invite",
                        "permissions": ["runner.invitation.create"],
                    },
                )
                self.assertEqual("RunnerInvitation", invitation["kind"])
                runner = post(
                    "/v0/runners/register",
                    {
                        "runnerId": "runner.api",
                        "name": "API Runner",
                        "pairingCode": invitation["pairingCode"],
                        "capabilities": ["development"],
                        "availableProjects": ["api-phase2"],
                        "idempotencyKey": "api-runner-register",
                    },
                )
                self.assertEqual("RunnerRegistrationResult", runner["kind"])
                self.assertEqual("auto_approved", runner["approvalStatus"])

                tool = post(
                    "/v0/workbench/tools",
                    {
                        "projectId": "api-phase2",
                        "toolName": "local-git-status",
                        "toolType": "cli",
                        "riskLevel": "low",
                        "allowedOperations": ["read_repo_status"],
                        "idempotencyKey": "api-tool-register",
                        "permissions": ["tool.register.low_risk"],
                    },
                )
                self.assertEqual("ToolAsset", tool["kind"])
                request = post(
                    "/v0/workbench/tool-registration-requests",
                    {
                        "projectId": "api-phase2",
                        "toolName": "lark-approval-writer",
                        "toolType": "lark_api",
                        "riskLevel": "high",
                        "requestedOperations": ["create_approval_instance"],
                        "credentialPolicy": "secret_ref_required",
                        "owner": "user.meimei",
                        "justification": "需要审批闭环。",
                        "idempotencyKey": "api-tool-request",
                        "permissions": ["tool.registration_request.create"],
                    },
                )
                self.assertEqual("ToolRegistrationRequest", request["kind"])
                read_model = get("/v0/workbench/projects/api-phase2/execution-read-model")
                self.assertEqual("WorkbenchExecutionReadModel", read_model["kind"])
                self.assertTrue(read_model["readOnly"])
                self.assertFalse(read_model["commandSurface"]["claimAsWorkbench"])
            finally:
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()

    def test_pm_control_lease_core_guard_takeover_and_read_model(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "ops", "--name", "Ops", "--owner", "meimei"]), 0)

            lease_result = core_module.acquire_pm_control_lease(
                bundle,
                "qa",
                "agent.company.project-manager",
                runner_id="runner.pm",
                device_id="device.local",
                lease_seconds=900,
                idempotency_key="pm-acquire-qa",
                source_channel="test",
            )
            lease = lease_result["lease"]
            self.assertEqual("active", lease["status"])
            self.assertEqual(1, lease["leaseGeneration"])
            self.assertEqual(lease["leaseGeneration"], lease["fencingToken"])
            self.assertTrue(lease_result["pmLeaseToken"].startswith("pm-token."))
            persisted_lease = (root / lease_result["leaseRef"]).read_text(encoding="utf-8")
            self.assertFalse("pm-token." in persisted_lease)
            self.assertNotIn("fencingToken:", persisted_lease)
            self.assertNotIn("idempotencyKey:", persisted_lease)
            self.assertNotIn("leaseTokenHash:", persisted_lease)
            self.assertIn("leaseGeneration:", persisted_lease)
            self.assertIn("deduplicationRef:", persisted_lease)
            self.assertFalse(core_module.scan_for_secret_values(root / lease_result["leaseRef"]))
            core_module.upsert_pm_participant(bundle, "qa", "agent.company.product-manager", "collaborator", capabilities=["product_management"])
            core_module.upsert_pm_participant(bundle, "qa", "agent.company.project-manager.standby", "standby", standby_priority=1)

            task_path = create_project_task(
                bundle,
                "Lease protected task",
                "qa",
                "agent.company.project-manager",
                "agent.company.development",
                task_type="engineering_action",
                task_id="PM-LEASE-OK",
                pm_agent_id="agent.company.project-manager",
                pm_lease_id=lease["leaseId"],
                pm_fencing_token=lease["leaseGeneration"],
                pm_source_channel="test",
            )
            task = load_object(task_path)
            self.assertEqual(lease["leaseId"], task["pmControlLeaseId"])
            self.assertEqual(lease["leaseGeneration"], task["pmControlLeaseGeneration"])
            self.assertEqual("agent.company.project-manager", task["pmControlPrimaryPm"])

            with self.assertRaises(core_module.PMControlLeaseError) as missing:
                create_project_task(
                    bundle,
                    "Missing lease denied",
                    "qa",
                    "agent.company.product-manager",
                    "agent.company.development",
                    task_type="engineering_action",
                    task_id="PM-LEASE-MISSING",
                    pm_source_channel="test",
                )
            self.assertEqual("pm_control_lease_missing", missing.exception.error_code)
            self.assertFalse((root / "projects" / "qa" / "tasks" / "pm-lease-missing.md").exists())

            with self.assertRaises(core_module.PMControlLeaseError) as non_primary:
                create_project_task(
                    bundle,
                    "Collaborator denied",
                    "qa",
                    "agent.company.product-manager",
                    "agent.company.development",
                    task_type="engineering_action",
                    task_id="PM-LEASE-COLLAB",
                    pm_agent_id="agent.company.product-manager",
                    pm_lease_id=lease["leaseId"],
                    pm_fencing_token=lease["leaseGeneration"],
                    pm_source_channel="test",
                )
            self.assertEqual("pm_control_lease_not_primary", non_primary.exception.error_code)

            with self.assertRaises(core_module.PMControlLeaseError) as mismatch:
                create_project_task(
                    bundle,
                    "Project mismatch denied",
                    "ops",
                    "agent.company.project-manager",
                    "agent.company.development",
                    task_type="engineering_action",
                    task_id="PM-LEASE-MISMATCH",
                    pm_agent_id="agent.company.project-manager",
                    pm_lease_id=lease["leaseId"],
                    pm_fencing_token=lease["leaseGeneration"],
                    pm_source_channel="test",
                )
            self.assertEqual("pm_control_lease_project_mismatch", mismatch.exception.error_code)

            takeover = core_module.takeover_pm_control_lease(
                bundle,
                "qa",
                "agent.company.project-manager.standby",
                "user.owner",
                "主控健康时人工确认接管。",
                runner_id="runner.pm.standby",
                device_id="device.standby",
                confirm_healthy=True,
                source_channel="test",
            )
            self.assertEqual("PMControlLeaseTakeover", takeover["kind"])
            core_module.upsert_pm_participant(bundle, "qa", "agent.company.project-manager.backup2", "standby", standby_priority=2)
            with self.assertRaises(core_module.PMControlLeaseError) as old_token:
                create_project_task(
                    bundle,
                    "Old primary denied",
                    "qa",
                    "agent.company.project-manager",
                    "agent.company.development",
                    task_type="engineering_action",
                    task_id="PM-LEASE-OLD",
                    pm_agent_id="agent.company.project-manager",
                    pm_lease_id=lease["leaseId"],
                    pm_fencing_token=lease["leaseGeneration"],
                    pm_source_channel="test",
                )
            self.assertIn(old_token.exception.error_code, {"pm_control_lease_expired", "pm_control_lease_stale_fencing_token"})
            model = core_module.pm_control_lease_read_model(bundle, "qa")
            self.assertEqual("healthy", model["currentLease"]["status"])
            self.assertTrue(model["takeoverRecords"])
            self.assertTrue(model["denialSummaries"])
            self.assertTrue(any(item["role"] == "standby" for item in model["participants"]))
            self.assertEqual("已记录防旧写入代际", model["currentLease"]["leaseGenerationLabel"])
            self.assertIn("pm_control_lease.denied", audit_actions(root))
            self.assertFalse([problem for problem in validate_bundle(bundle) if "pm-control-leases" in problem and "possible secret value" in problem])

    def test_pm_control_lease_api_routes_and_protected_task_create(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            try:
                server = KnowledgeHTTPServer(("127.0.0.1", 0), Bundle(root), api_token="test-token")
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"

            def post(path: str, payload: dict) -> dict:
                request = urllib.request.Request(base + path, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"}, method="POST")
                with urllib.request.urlopen(request) as response:
                    return json.loads(response.read().decode("utf-8"))

            def post_error(path: str, payload: dict) -> tuple[int, dict]:
                request = urllib.request.Request(base + path, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"}, method="POST")
                try:
                    urllib.request.urlopen(request)
                except urllib.error.HTTPError as exc:
                    return exc.code, json.loads(exc.read().decode("utf-8"))
                self.fail(f"{path} unexpectedly succeeded")

            try:
                missing_status, missing_response = post_error(
                    "/v0/tasks/create",
                    {"projectId": "qa", "title": "API missing lease", "requester": "agent.company.product-manager", "assignee": "agent.company.development", "taskType": "engineering_action", "taskId": "API-PM-MISSING"},
                )
                self.assertEqual(409, missing_status)
                self.assertEqual("pm_control_lease_missing", missing_response["errorCode"])
                self.assertTrue(missing_response["auditRef"])

                acquire = post(
                    "/v0/pm-control-lease/acquire",
                    {"projectId": "qa", "pmAgentId": "agent.company.project-manager", "runnerId": "runner.pm", "deviceId": "device.local", "idempotencyKey": "api-pm-acquire"},
                )
                lease = acquire["lease"]
                self.assertEqual(lease["leaseGeneration"], lease["fencingToken"])
                persisted_lease = (root / acquire["leaseRef"]).read_text(encoding="utf-8")
                self.assertNotIn("fencingToken:", persisted_lease)
                self.assertNotIn("idempotencyKey:", persisted_lease)
                self.assertNotIn("leaseTokenHash:", persisted_lease)
                self.assertFalse(core_module.scan_for_secret_values(root / acquire["leaseRef"]))
                created = post(
                    "/v0/tasks/create",
                    {
                        "projectId": "qa",
                        "title": "API protected task",
                        "requester": "agent.company.project-manager",
                        "assignee": "agent.company.development",
                        "taskType": "engineering_action",
                        "taskId": "API-PM-OK",
                        "pmAgentId": "agent.company.project-manager",
                        "leaseId": lease["leaseId"],
                        "fencingToken": lease["fencingToken"],
                    },
                )
                self.assertEqual("ProjectTask", created["kind"])
                self.assertEqual(lease["leaseId"], created["task"]["pmControlLeaseId"])
                self.assertEqual(lease["leaseGeneration"], created["task"]["pmControlLeaseGeneration"])
                status = post("/v0/pm-control-lease/heartbeat", {"projectId": "qa", "pmAgentId": "agent.company.project-manager", "leaseId": lease["leaseId"], "pmLeaseToken": acquire["pmLeaseToken"], "leaseGeneration": lease["leaseGeneration"]})
                self.assertEqual("PMControlLease", status["kind"])
            finally:
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()

    def test_task_fact_cli_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)

            task_path = root / "projects" / "qa" / "tasks" / "task-fact-smoke.md"
            task_path.parent.mkdir(parents=True, exist_ok=True)
            task_path.write_text(
                """---
type: ProjectTask
taskId: TASK-FACT-SMOKE
projectId: qa
title: Task fact smoke
status: done
workSourceType: feature
resultRef: task-results/tr-task-fact-smoke.md
updatedAt: "2026-06-23T08:00:00Z"
---
""",
                encoding="utf-8",
            )
            result_path = root / "task-results" / "tr-task-fact-smoke.md"
            result_path.write_text(
                """---
type: TaskResult
resultId: tr-task-fact-smoke
taskId: TASK-FACT-SMOKE
status: done
summary: Smoke result.
evidenceRefs:
  - tests/test_task_fact_view.py
testsOrChecks:
  - python3 -m unittest tests.test_task_fact_view
qualityEvaluation: {"passed": true}
commonRulesEvaluation: {"passed": true}
---
""",
                encoding="utf-8",
            )

            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(main(["--root", str(root), "task", "fact", "TASK-FACT-SMOKE", "--project", "qa"]), 0)
            view = json.loads(out.getvalue())
            self.assertEqual("TaskFactView", view["kind"])
            self.assertEqual("task-fact-view.v0", view["schemaVersion"])
            self.assertEqual("TASK-FACT-SMOKE", view["facts"]["identity"]["taskId"])


    def test_pm_control_lease_cli_commands_and_task_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(
                    main(["--root", str(root), "pm-lease", "acquire", "--project", "qa", "--pm-agent", "agent.company.project-manager", "--runner-id", "runner.pm", "--device-id", "device.local", "--idempotency-key", "cli-pm-acquire"]),
                    0,
                )
            acquire = json.loads(out.getvalue())
            lease = acquire["lease"]
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(
                    main(["--root", str(root), "task", "create", "--title", "CLI missing lease", "--project", "qa", "--requester", "agent.company.product-manager", "--assignee", "agent.company.development", "--type", "engineering_action", "--task-id", "CLI-PM-MISSING", "--pm-source", "cli"]),
                    2,
                )
            self.assertIn("pm_control_lease_missing", err.getvalue())
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "create",
                        "--title",
                        "CLI protected task",
                        "--project",
                        "qa",
                        "--requester",
                        "agent.company.project-manager",
                        "--assignee",
                        "agent.company.development",
                        "--type",
                        "engineering_action",
                        "--task-id",
                        "CLI-PM-OK",
                        "--pm-agent",
                        "agent.company.project-manager",
                        "--pm-lease-id",
                        lease["leaseId"],
                        "--pm-lease-generation",
                        str(lease["leaseGeneration"]),
                        "--pm-source",
                        "cli",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "start",
                        "CLI-PM-OK",
                        "--actor",
                        "agent.company.project-manager",
                        "--pm-agent",
                        "agent.company.project-manager",
                        "--pm-lease-id",
                        lease["leaseId"],
                        "--pm-lease-generation",
                        str(lease["leaseGeneration"]),
                        "--pm-source",
                        "cli",
                    ]
                ),
                0,
            )
            task = load_object(root / "projects" / "qa" / "tasks" / "cli-pm-ok.md")
            self.assertEqual("processing", task["status"])
            self.assertEqual(lease["leaseGeneration"], task["pmControlLeaseGeneration"])
            self.assertFalse(core_module.scan_for_secret_values(root / acquire["leaseRef"]))

    def test_phase2_workbench_permission_gate_rejects_api_and_cli_missing_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            try:
                server = KnowledgeHTTPServer(("127.0.0.1", 0), Bundle(root), api_token="test-token")
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"

            def post_error(path: str, payload: dict) -> tuple[int, dict]:
                request = urllib.request.Request(
                    base + path,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"},
                    method="POST",
                )
                try:
                    urllib.request.urlopen(request)
                except urllib.error.HTTPError as exc:
                    return exc.code, json.loads(exc.read().decode("utf-8"))
                self.fail(f"{path} unexpectedly succeeded")

            try:
                api_cases = [
                    (
                        "/v0/workbench/projects",
                        {"projectId": "api-denied", "name": "API Denied", "owner": "user.meimei", "idempotencyKey": "api-denied-project"},
                    ),
                    (
                        "/v0/workbench/runner-invitations",
                        {"projectId": "api-denied", "runnerLabel": "API Denied Runner", "idempotencyKey": "api-denied-runner"},
                    ),
                    (
                        "/v0/workbench/tools",
                        {"projectId": "api-denied", "toolName": "api-denied-tool", "toolType": "cli", "riskLevel": "low", "idempotencyKey": "api-denied-tool"},
                    ),
                    (
                        "/v0/workbench/tool-registration-requests",
                        {
                            "projectId": "api-denied",
                            "toolName": "api-denied-high-tool",
                            "toolType": "external_api",
                            "riskLevel": "high",
                            "justification": "Need explicit approval.",
                            "idempotencyKey": "api-denied-tool-request",
                        },
                    ),
                ]
                for path, payload in api_cases:
                    status, response = post_error(path, payload)
                    self.assertEqual(400, status)
                    self.assertIn("permission denied", json.dumps(response, ensure_ascii=False))
            finally:
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()

            cli_cases = [
                [
                    "--root",
                    str(root),
                    "workbench",
                    "create-project",
                    "--project-id",
                    "cli-denied",
                    "--name",
                    "CLI Denied",
                    "--owner",
                    "user.meimei",
                    "--idempotency-key",
                    "cli-denied-project",
                ],
                [
                    "--root",
                    str(root),
                    "workbench",
                    "invite-runner",
                    "--project",
                    "cli-denied",
                    "--runner-label",
                    "CLI Denied Runner",
                    "--idempotency-key",
                    "cli-denied-runner",
                ],
                [
                    "--root",
                    str(root),
                    "workbench",
                    "register-tool",
                    "--project",
                    "cli-denied",
                    "--tool-name",
                    "cli-denied-tool",
                    "--tool-type",
                    "cli",
                    "--idempotency-key",
                    "cli-denied-tool",
                ],
                [
                    "--root",
                    str(root),
                    "workbench",
                    "request-tool",
                    "--project",
                    "cli-denied",
                    "--tool-name",
                    "cli-denied-high-tool",
                    "--tool-type",
                    "external_api",
                    "--justification",
                    "Need explicit approval.",
                    "--idempotency-key",
                    "cli-denied-tool-request",
                ],
            ]
            for argv in cli_cases:
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    rc = main(argv)
                self.assertNotEqual(0, rc)
                self.assertIn("permission denied", stderr.getvalue())

            actions = audit_actions(root)
            self.assertEqual(8, actions.count("workbench.permission.denied"))
            self.assertNotIn("workbench.project.create", actions)
            self.assertNotIn("runner.invitation.create", actions)
            self.assertNotIn("tool.register", actions)
            self.assertNotIn("tool.registration_request.create", actions)
            self.assertFalse((root / "projects" / "api-denied" / "project.md").exists())
            self.assertFalse((root / "projects" / "cli-denied" / "project.md").exists())
            self.assertEqual([], [path.name for path in (root / "runner-invitations").glob("*.md") if path.name != "index.md"])
            self.assertEqual([], [path.name for path in (root / "tools").glob("*.md") if path.name != "index.md"])
            self.assertEqual([], [path.name for path in (root / "tool-registration-requests").glob("*.md") if path.name != "index.md"])
            denied_audit = load_object(sorted((root / "knowledge" / "audit").glob("*.md"))[0])
            self.assertEqual("not_created", denied_audit["before"])
            self.assertEqual("denied", denied_audit["after"])
            self.assertEqual("permission_denied", denied_audit["policyResult"])
            self.assertTrue(denied_audit["targetRef"])

    def register_runner_fixture(self, root: Path, runner_id: str, agent: str, capability: str, project_id: str) -> None:
        self.assertEqual(
            main(
                [
                    "--root",
                    str(root),
                    "runner",
                    "register",
                    "--runner-id",
                    runner_id,
                    "--name",
                    runner_id,
                    "--agent",
                    agent,
                    "--capability",
                    capability,
                    "--project",
                    project_id,
                ]
            ),
            0,
        )

    def grant_agent_write_policy(self, root: Path, agent_id: str) -> None:
        agent_slug = agent_id.replace(".", "-")
        self.assertEqual(
            main(
                [
                    "--root",
                    str(root),
                    "agent",
                    "register",
                    "--agent-id",
                    agent_id,
                    "--name",
                    agent_id,
                    "--owner",
                    "test-owner",
                    "--purpose",
                    "test fixture",
                ]
            ),
            0,
        )
        self.assertEqual(
            main(
                [
                    "--root",
                    str(root),
                    "policy",
                    "register",
                    "--policy-id",
                    f"policy.{agent_slug}",
                    "--title",
                    f"{agent_id} Write Policy",
                    "--agent-id",
                    agent_id,
                    "--owner",
                    "test-owner",
                    "--allow-project",
                    "agent-hub",
                    "--allow-project",
                    "core",
                    "--allow-project",
                    "review-flow",
                    "--allow-scope",
                    "engineering",
                    "--allow-risk",
                    "L1",
                ]
            ),
            0,
        )
        update_frontmatter_file(root / "knowledge" / "policies" / f"policy.{agent_slug}.md", {"status": "active"})

    def assert_cli_ok(self, argv: list[str], message: str = "") -> None:
        try:
            exit_code = main(argv)
        except SystemExit as exc:
            self.fail(message or f"CLI exited before completing: argv={argv} exit={exc.code}")
        self.assertEqual(exit_code, 0, message or f"CLI failed: argv={argv}")

    def create_reviewable_knowledge_fixture(self, root: Path, suffix: str = "FLOW") -> tuple[Bundle, str, str]:
        bundle = Bundle(root)
        project_id = f"review-{suffix.lower()}"
        task_id = f"KT-REVIEW-{suffix}"
        runner_id = f"runner.review.{suffix.lower()}"
        source_ref = f"projects/{project_id}/sources/source.md"
        self.grant_agent_write_policy(root, "agent.company-knowledge-core.knowledge-engineering")
        self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", project_id, "--name", f"Review {suffix}", "--owner", "meimei"]), 0)
        self.assertEqual(
            main(
                [
                    "--root",
                    str(root),
                    "runner",
                    "register",
                    "--runner-id",
                    runner_id,
                    "--name",
                    f"Review Runner {suffix}",
                    "--capability",
                    "knowledge_capture",
                    "--project",
                    project_id,
                ]
            ),
            0,
        )
        self.assertEqual(
            main(
                [
                    "--root",
                    str(root),
                    "task",
                    "create",
                    "--task-id",
                    task_id,
                    "--title",
                    f"Extract source {suffix}",
                    "--project",
                    project_id,
                    "--requester",
                    "ou_submitter",
                    "--assignee",
                    runner_id,
                    "--source",
                    source_ref,
                ]
            ),
            0,
        )
        claim = claim_project_task(bundle, task_id, runner_id)
        result_path = finish_project_task(
            bundle,
            task_id,
            "done",
            f"Extracted source {suffix}.",
            evidence_refs=[source_ref],
            runner_id=runner_id,
            lease_token=claim["leaseToken"],
            executor_agent="agent.company-knowledge-core.knowledge-engineering",
            knowledge_draft={
                "title": f"Reviewable knowledge {suffix}",
                "summary": f"Summary {suffix}",
                "structured": f"Structured knowledge {suffix}",
                "sourceRefs": [source_ref],
                "confidence": "high",
                "scope": "engineering",
                "limits": ["Review fixture only."],
            },
        )
        result = load_object(result_path)
        return bundle, f"{task_id.lower()}-review", result["knowledgeRefs"][0]

    def run_cli_path(self, argv: list[str]) -> Path:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.assertEqual(main(argv), 0)
        return Path(buffer.getvalue().strip().splitlines()[-1])

    def test_ai_native_os_requirement_prd_decision_domain_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "reqprd", "--name", "Requirement PRD", "--owner", "human.pm"]), 0)
            requirement_path = self.run_cli_path(["--root", str(root), "requirement", "create", "--project", "reqprd", "--source", "sources/customer-request.md", "--title", "Launch pricing workflow", "--submitter", "human.requester", "--summary", "Customer-facing pricing workflow needs product discovery."])
            requirement = load_object(requirement_path)
            self.assertEqual(requirement["type"], "Requirement")
            self.assertEqual(requirement["status"], "clarifying")
            self.assertTrue(requirement["auditRefs"])
            state = json.loads((root / requirement["requirementStateRef"]).read_text(encoding="utf-8"))
            self.assertIn("businessModel", state["missingFields"])

            clarification_path = self.run_cli_path(["--root", str(root), "requirement", "clarify", requirement["requirementId"], "--agent", "agent.company.product-manager"])
            clarification = load_object(clarification_path)
            self.assertEqual(clarification["type"], "ClarificationRound")
            self.assertGreaterEqual(len(clarification["questionRefs"]), 1)
            self.assertLessEqual(len(clarification["questionRefs"]), 3)
            self.assertEqual(main(["--root", str(root), "requirement", "approve", requirement["requirementId"], "--owner", "human.pm"]), 2)
            self.assertIn("requirement.approval.blocked", audit_actions(root))

            state_patch = {
                "targetUser": "Finance operators",
                "problem": {"value": "Pricing approvals are slow and inconsistent.", "clarity": "known", "basis": "evidence"},
                "scenario": "Operator reviews pricing request and routes owner decision.",
                "alternative": "Keep spreadsheet approval.",
                "value": "Reduce pricing approval cycle time.",
                "marketPosition": {"value": "internal workflow differentiator", "clarity": "known", "basis": "inference", "notes": "Derived from project goal."},
                "businessModel": "subscription expansion support",
                "scope": "Pricing request intake, owner review, audit trace.",
                "nonGoals": "No billing engine or contract generation.",
                "constraints": "Security and permission changes need human review.",
                "metric": "90% pricing requests receive owner decision within two business days.",
                "acceptanceCriteria": "Owner can see request status, decision, audit, and next action.",
                "evidence": {"value": "Customer request source", "clarity": "known", "basis": "evidence"},
                "assumptions": {"value": "Initial requester can answer product questions.", "clarity": "assumed", "basis": "assumption"},
                "decisionOwner": "human.pm",
                "prdQualityProtocol": {
                    "value": {
                        "requirementClarifier": {
                            "firstPrinciples": {
                                "user": "Finance operators",
                                "problem": "Pricing approvals are slow and inconsistent.",
                                "value": "Reduce pricing approval cycle time.",
                                "successMetric": "90% pricing requests receive owner decision within two business days.",
                            },
                            "socraticQuestions": [
                                "Who is blocked by the current pricing approval workflow?",
                                "What observable outcome proves the workflow improved?",
                            ],
                            "summary": "明确目标用户、问题、场景、商业模式和成功指标。",
                        },
                        "evidencePackGenerator": "证据、推断、假设和待决策事项已分离。",
                        "productPlanGenerator": "完整上线方案已产出。",
                        "adversarialReviewer": "已检查问题真实性、场景完整性、商业闭环、边界异常和可测试性。",
                        "prdQualityChecker": "已确认需求不混入技术实现，验收标准可观察。",
                        "deliveryPackGenerator": "已准备测试方向、验收清单和开发交付包。",
                    },
                    "clarity": "known",
                    "basis": "evidence",
                },
            }
            self.assertEqual(main(["--root", str(root), "requirement", "update-state", requirement["requirementId"], "--patch", json.dumps(state_patch), "--actor", "agent.company.product-manager"]), 0)
            criteria_path = self.run_cli_path(["--root", str(root), "requirement", "add-criteria", requirement["requirementId"], "--description", "Owner sees pricing request decision state.", "--observable-signal", "CLI or UI response includes status, owner, audit ref, and next action.", "--verification-method", "automated_test", "--owner", "agent.company.test", "--status", "approved"])
            criteria = load_object(criteria_path)
            self.assertEqual(criteria["type"], "AcceptanceCriteria")
            self.assertEqual(criteria["status"], "approved")
            self.assertTrue(criteria["observableSignal"])
            self.assertEqual(main(["--root", str(root), "requirement", "approve", requirement["requirementId"], "--owner", "human.pm"]), 0)

            prd_v1_path = self.run_cli_path(["--root", str(root), "prd", "generate", requirement["requirementId"], "--author-agent", "agent.company.product-manager", "--reviewer", "human.pm"])
            prd_v1 = load_object(prd_v1_path)
            self.assertEqual(prd_v1["version"], "v1")
            self.assertTrue(prd_v1["qualityGate"]["passed"])
            self.assertEqual(main(["--root", str(root), "prd", "approve", prd_v1["prdId"], "--reviewer", "human.pm"]), 0)

            task_path = self.run_cli_path(["--root", str(root), "requirement", "create-task", requirement["requirementId"], "--title", "Implement pricing workflow", "--assignee", "agent.company.development", "--requester", "human.pm", "--criteria-ref", str(criteria_path.relative_to(root))])
            task = load_object(task_path)
            self.assertEqual(task["requirementRefs"], [requirement["requirementId"]])
            self.assertEqual(task["acceptanceCriteriaRefs"], [str(criteria_path.relative_to(root))])

            self.assertEqual(main(["--root", str(root), "requirement", "update-state", requirement["requirementId"], "--patch", json.dumps({"scope": "Pricing request intake, owner review, audit trace, and downstream task notifications."}), "--actor", "agent.company.product-manager"]), 0)
            prd_v2_path = self.run_cli_path(["--root", str(root), "prd", "generate", requirement["requirementId"], "--author-agent", "agent.company.product-manager", "--reviewer", "human.pm"])
            prd_v2 = load_object(prd_v2_path)
            self.assertEqual(prd_v2["version"], "v2")
            self.assertEqual(prd_v2["supersedesPrdRef"], str(prd_v1_path.relative_to(root)))
            self.assertEqual(main(["--root", str(root), "prd", "approve", prd_v2["prdId"], "--reviewer", "human.pm"]), 2)
            impact_path = self.run_cli_path(["--root", str(root), "requirement", "impact-review", requirement["requirementId"], "--from", str(prd_v1_path.relative_to(root)), "--to", str(prd_v2_path.relative_to(root)), "--owner", "human.pm", "--status", "accepted"])
            impact = load_object(impact_path)
            self.assertEqual(impact["type"], "ImpactReview")
            self.assertIn(str(task_path.relative_to(root)), impact["affectedTaskRefs"])
            self.assertEqual(main(["--root", str(root), "prd", "approve", prd_v2["prdId"], "--reviewer", "human.pm"]), 0)
            self.assertEqual(load_object(prd_v1_path)["status"], "superseded")

            decision_path = self.run_cli_path(["--root", str(root), "decision", "create", "--requirement", requirement["requirementId"], "--impact", "high", "--owner", "human.pm", "--area", "pricing", "--context", "Pricing launch scope changes customer commitment.", "--option", "Launch with owner approval", "--option", "Hold launch", "--recommendation", "Launch only with explicit owner approval."])
            decision = load_object(decision_path)
            self.assertEqual(decision["type"], "Decision")
            self.assertEqual(decision["impactLevel"], "high")
            self.assertEqual(decision["status"], "decision_needed")
            self.assertTrue(decision["deadline"])
            self.assertEqual(main(["--root", str(root), "validate"]), 0)

    def test_prd_quality_gate_blocks_missing_high_quality_protocol(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "prdgate", "--name", "PRD Gate", "--owner", "human.pm"]), 0)
            requirement_path = self.run_cli_path([
                "--root",
                str(root),
                "requirement",
                "create",
                "--project",
                "prdgate",
                "--source",
                "sources/customer-request.md",
                "--title",
                "Agent PRD quality gate",
                "--submitter",
                "human.requester",
                "--owner",
                "human.pm",
                "--summary",
                "PM Agent must produce a complete PRD package.",
            ])
            requirement = load_object(requirement_path)
            state_patch = {
                "targetUser": "Company operators",
                "problem": "PRDs are inconsistent when the internal quality protocol is skipped.",
                "scenario": "Operator asks Product Manager Agent to produce a launch-ready PRD.",
                "alternative": "Manual review after the fact.",
                "value": "Improve PRD quality before design, development, and test work starts.",
                "marketPosition": "AI-native operating system product quality control.",
                "businessModel": "internal productivity and delivery quality improvement.",
                "scope": "PRD generation quality gate.",
                "nonGoals": "No new company-level Controller or Reviewer Agent.",
                "constraints": "Must remain inside Product Manager Agent.",
                "metric": "PRD approval is blocked when protocol evidence is missing.",
                "acceptanceCriteria": "Approval fails with a readable blocker.",
                "evidence": {"value": "User requested enforceable PM Agent behavior.", "clarity": "known", "basis": "evidence"},
                "assumptions": {"value": "Existing PRD quality gate is the enforcement point.", "clarity": "assumed", "basis": "assumption"},
                "decisionOwner": "human.pm",
            }
            self.assertEqual(main(["--root", str(root), "requirement", "update-state", requirement["requirementId"], "--patch", json.dumps(state_patch), "--actor", "agent.company.product-manager"]), 0)
            self.run_cli_path([
                "--root",
                str(root),
                "requirement",
                "add-criteria",
                requirement["requirementId"],
                "--description",
                "PRD approval blocks missing high-quality protocol evidence.",
                "--observable-signal",
                "qualityGate.blockers includes prd-high-quality-generation protocol missing or incomplete.",
                "--verification-method",
                "automated_test",
                "--owner",
                "agent.company.test",
                "--status",
                "approved",
            ])
            prd_path = self.run_cli_path(["--root", str(root), "prd", "generate", requirement["requirementId"], "--author-agent", "agent.company.product-manager", "--reviewer", "human.pm"])
            prd = load_object(prd_path)
            self.assertFalse(prd["qualityGate"]["passed"])
            self.assertEqual(prd["qualityGate"]["prdHighQualityProtocolLevel"], "light")
            self.assertIn("prd-high-quality-generation protocol light missing or incomplete", "; ".join(prd["qualityGate"]["blockers"]))
            self.assertEqual(main(["--root", str(root), "prd", "approve", prd["prdId"], "--reviewer", "human.pm"]), 2)
            self.assertIn("prd.approval.blocked", audit_actions(root))
            light_protocol_patch = {
                "prdQualityProtocol": {
                    "value": {
                        "requiredProtocolLevel": "light",
                        "requirementClarifier": {
                            "firstPrinciples": {
                                "user": "Company operators",
                                "problem": "PRDs are inconsistent when the internal quality protocol is skipped.",
                                "value": "Improve PRD quality before downstream work starts.",
                                "successMetric": "PRD approval is blocked when protocol evidence is missing.",
                            },
                            "socraticQuestions": [
                                "Which user is harmed when PRD quality is inconsistent?",
                                "What observable gate proves Product Manager Agent followed the protocol?",
                            ],
                            "summary": "已明确用户、场景、问题和成功指标。",
                        },
                        "prdQualityChecker": "已确认需求可测试，且未混入技术实现。",
                        "deliveryPackGenerator": "已给出验收方向和开发交付要点。",
                    },
                    "clarity": "known",
                    "basis": "evidence",
                }
            }
            self.assertEqual(main(["--root", str(root), "requirement", "update-state", requirement["requirementId"], "--patch", json.dumps(light_protocol_patch), "--actor", "agent.company.product-manager"]), 0)
            prd_light_path = self.run_cli_path(["--root", str(root), "prd", "generate", requirement["requirementId"], "--author-agent", "agent.company.product-manager", "--reviewer", "human.pm"])
            prd_light = load_object(prd_light_path)
            self.assertTrue(prd_light["qualityGate"]["passed"])
            self.assertEqual(prd_light["qualityGate"]["prdHighQualityProtocolLevel"], "light")
            self.assertEqual(main(["--root", str(root), "prd", "approve", prd_light["prdId"], "--reviewer", "human.pm"]), 0)

    def test_agent_team_guide_gate_blocks_impacted_task_without_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            guide_path = root / "docs" / "agent-team" / "company-agent-team-operating-guide.md"
            guide_path.parent.mkdir(parents=True)
            guide_path.write_text("# 公司 Agent Team 工作指南\n", encoding="utf-8")
            task_path = create_project_task(
                bundle,
                "Update Product Manager Agent skill pack",
                "agent-hub",
                "meimei",
                "runner.this-mac",
                task_type="engineering_action",
                task_id="KT-GUIDE-001",
            )
            task = load_object(task_path)
            self.assertTrue(task["guideUpdateRequired"])
            with self.assertRaisesRegex(KnowledgeError, "agent team guide update required"):
                finish_project_task(
                    bundle,
                    "KT-GUIDE-001",
                    "done",
                    "Updated product manager Agent skill pack.",
                )
            audit_path = create_audit_log(
                bundle,
                "agent.company-knowledge-core.knowledge-engineering",
                "agent_team.guide.updated",
                "docs/agent-team/company-agent-team-operating-guide.md",
                after="guide gate evidence",
            )
            result_path = finish_project_task(
                bundle,
                "KT-GUIDE-001",
                "done",
                "Updated product manager Agent skill pack and synchronized the operating guide.",
                guide_updated=True,
                guide_revision="Updated product manager Agent skill pack responsibilities.",
                guide_audit_refs=[str(audit_path.relative_to(root))],
            )
            result = load_object(result_path)
            self.assertTrue(result["guideUpdated"])
            self.assertEqual(result["guideRef"], "docs/agent-team/company-agent-team-operating-guide.md")
            self.assertFalse(validate_bundle(bundle))

    def test_validate_flags_closed_guide_impacted_task_without_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            task_dir = root / "projects" / "agent-hub" / "tasks"
            task_dir.mkdir(parents=True)
            (task_dir / "kt-guide-gate.md").write_text(
                """---
type: ProjectTask
title: Update Agent workflow
timestamp: 2026-06-19T13:05:00Z
taskId: KT-GUIDE-GATE
taskType: workflow_change
projectId: agent-hub
requester: meimei
assignee: runner.this-mac
status: done
guideUpdateRequired: true
guideUpdated: false
---

## Request

Update Agent workflow.
""",
                encoding="utf-8",
            )
            problems = validate_bundle(Bundle(root))
            self.assertIn(
                "projects/agent-hub/tasks/kt-guide-gate.md: agent team guide update required but guideUpdated is not true",
                problems,
            )

    def test_validate_flags_invalid_task_result_acceptance_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            result_dir = root / "task-results"
            result_dir.mkdir(parents=True, exist_ok=True)
            (result_dir / "tr-bad-acceptance.md").write_text(
                """---
type: TaskResult
title: Bad acceptance policy
timestamp: 2026-06-21T00:00:00Z
resultId: TR-BAD-ACCEPTANCE
taskId: BAD-ACCEPTANCE
projectId: demo
status: done
acceptancePolicy: {"status":"waiting_acceptance","acceptanceStatus":"waiting_human_acceptance"}
qualityEvaluation: {"decision":"not_a_decision"}
---

## Summary

Bad status names.
""",
                encoding="utf-8",
            )
            problems = validate_bundle(Bundle(root))
            self.assertIn(
                "task-results/tr-bad-acceptance.md: acceptancePolicy must use acceptanceStatus, not status",
                problems,
            )
            self.assertIn(
                "task-results/tr-bad-acceptance.md: unknown acceptancePolicy.acceptanceStatus waiting_human_acceptance",
                problems,
            )
            self.assertIn(
                "task-results/tr-bad-acceptance.md: unknown qualityEvaluation.decision not_a_decision",
                problems,
            )

    def test_validate_enforces_product_verdict_role_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            task_dir = root / "projects" / "demo" / "tasks"
            task_dir.mkdir(parents=True, exist_ok=True)
            (task_dir / "product-acceptance.md").write_text(
                """---
type: ProjectTask
title: Product acceptance
timestamp: 2026-06-21T00:00:00Z
taskId: PRODUCT-ACCEPTANCE-001
taskType: product_review
taskRuntime: {"taskType":"product_review","category":"product","productEvidenceRequired":true}
projectId: demo
requester: agent.company.project-manager
assignee: agent.company.product-manager
status: waiting_acceptance
---

## Request

Validate product scope.
""",
                encoding="utf-8",
            )
            result_dir = root / "task-results"
            result_dir.mkdir(parents=True, exist_ok=True)
            result_path = result_dir / "tr-product-acceptance.md"
            result_template = """---
type: TaskResult
title: Product acceptance result
timestamp: 2026-06-21T00:00:00Z
completedAt: 2026-06-21T00:05:00Z
createdAt: 2026-06-21T00:05:00Z
resultId: TR-PRODUCT-ACCEPTANCE-001
taskId: PRODUCT-ACCEPTANCE-001
projectId: demo
status: done
summary: Product verdict.
executorAgent: {executor}
runner: runner.local
leaseProof: lease.local
outputRefs: []
evidenceRefs: []
risks: []
blockers: []
nextAction: close
checks: []
approvalRequest: {{}}
acceptancePolicy: {{"acceptanceStatus":"waiting_acceptance"}}
qualityEvaluation: {{"decision":"handoff_ready"}}
---

## Summary

Product verdict.
"""
            result_path.write_text(result_template.format(executor="agent.company.project-manager"), encoding="utf-8")
            problems = validate_bundle(Bundle(root))
            self.assertIn(
                "task-results/tr-product-acceptance.md: product verdict TaskResult must be executed by agent.company.product-manager, not agent.company.project-manager",
                problems,
            )

            result_path.write_text(result_template.format(executor="agent.company.product-manager"), encoding="utf-8")
            problems = validate_bundle(Bundle(root))
            self.assertFalse([problem for problem in problems if "product verdict TaskResult must be executed" in problem])

    def test_skill_validate_accepts_registered_executable_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            docs = root / "docs" / "agent-team"
            docs.mkdir(parents=True)
            (docs / "skill-system-architecture.md").write_text("# Skill System\n", encoding="utf-8")
            (docs / "skill-delivery-standard.md").write_text("# Skill Delivery Standard\n", encoding="utf-8")
            (docs / "skill-quality-sources.json").write_text(
                json.dumps(
                    {
                        "sources": [
                            {"repo": "one", "url": "https://example.com/one"},
                            {"repo": "two", "url": "https://example.com/two"},
                            {"repo": "three", "url": "https://example.com/three"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (root / "skills" / "_shared").mkdir(parents=True)
            (root / "skills" / "_shared" / "skill-output-contract.md").write_text("# Contract\n", encoding="utf-8")
            (root / "skills" / "_shared" / "references").mkdir(parents=True)
            (root / "skills" / "_shared" / "templates").mkdir(parents=True)
            (root / "skills" / "_shared" / "examples").mkdir(parents=True)
            (root / "skills" / "_shared" / "references" / "mature-skill-package.md").write_text(
                "# Mature Skill Package\n\nShared mature skill package reference for tests.\n", encoding="utf-8"
            )
            (root / "skills" / "_shared" / "templates" / "skill-output-template.md").write_text(
                "# Skill Output Template\n\nShared output template for tests.\n", encoding="utf-8"
            )
            (root / "skills" / "_shared" / "examples" / "skill-quality-example.md").write_text(
                "# Skill Quality Example\n\nShared quality example for tests.\n", encoding="utf-8"
            )
            skill_dir = root / "skills" / "demo-skill"
            skill_dir.mkdir(parents=True)
            skill_dir.joinpath("SKILL.md").write_text(
                """---
name: demo-skill
description: Use when validating a production executable skill in tests.
---

# Demo Skill

## Purpose

Do one reusable task.

## Triggers

- Demo trigger.

## Inputs

- Demo input.

## Workflow

1. Read input.
2. Produce output.

## Outputs

- Demo output.

## Quality Gate

- Output is checkable.

## Failure Routes

- Return missing input.
""",
                encoding="utf-8",
            )
            (skill_dir / "references").mkdir()
            (skill_dir / "templates").mkdir()
            (skill_dir / "examples").mkdir()
            (skill_dir / "references" / "delivery-card.md").write_text(
                "# Demo Skill Delivery Card\n\nThis card binds demo-skill to the demo role and defines done means, references, handoff, and failure routing for a mature skill package.\n",
                encoding="utf-8",
            )
            (skill_dir / "templates" / "output-template.md").write_text(
                "# Demo Skill Output Template\n\nThe demo skill output includes request, inputs, result, evidence, quality gate, and next step for handoff.\n",
                encoding="utf-8",
            )
            (skill_dir / "examples" / "quality-example.md").write_text(
                "# Demo Skill Quality Example\n\nA good demo result includes concrete output, evidence, quality gate result, and a failure route when blocked.\n",
                encoding="utf-8",
            )
            (docs / "company-skill-registry.json").write_text(
                json.dumps(
                    {
                        "version": "test",
                        "skillDeliveryStandardRef": "docs/agent-team/skill-delivery-standard.md",
                        "qualitySourcesRef": "docs/agent-team/skill-quality-sources.json",
                        "sharedContractRef": "skills/_shared/skill-output-contract.md",
                        "skills": [
                            {
                                "skillId": "demo-skill",
                                "name": "Demo Skill",
                                "ownerRole": "demo",
                                "skillDir": "skills/demo-skill",
                                "status": "active",
                                "allowedRoles": ["demo"],
                                "aliases": ["demo-alias"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (docs / "role-operating-specs.json").write_text(
                json.dumps(
                    {
                        "version": "test",
                        "roles": [
                            {
                                "roleId": "demo",
                                "name": "Demo Agent",
                                "defaultAgentId": "agent.company.demo",
                                "primaryOwner": "agent.company.demo",
                                "roleProfileRef": "docs/agent-team/demo-role.md",
                                "skillRegistryRef": "docs/agent-team/company-skill-registry.json",
                                "skillRefs": ["demo-skill"],
                                "capabilityTags": ["demo-alias"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (docs / "demo-role.md").write_text("# Demo Role\n", encoding="utf-8")

            self.assertEqual(main(["--root", str(root), "skill", "validate"]), 0)
            self.assertFalse([problem for problem in validate_bundle(Bundle(root)) if "skill" in problem.lower()])

    def test_skill_validate_flags_unregistered_and_non_executable_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            docs = root / "docs" / "agent-team"
            docs.mkdir(parents=True)
            (docs / "skill-system-architecture.md").write_text("# Skill System\n", encoding="utf-8")
            (docs / "skill-delivery-standard.md").write_text("# Skill Delivery Standard\n", encoding="utf-8")
            (docs / "skill-quality-sources.json").write_text(json.dumps({"sources": []}), encoding="utf-8")
            (root / "skills" / "_shared").mkdir(parents=True)
            (root / "skills" / "_shared" / "skill-output-contract.md").write_text("# Contract\n", encoding="utf-8")
            (root / "skills" / "_shared" / "references").mkdir(parents=True)
            (root / "skills" / "_shared" / "templates").mkdir(parents=True)
            (root / "skills" / "_shared" / "examples").mkdir(parents=True)
            (root / "skills" / "_shared" / "references" / "mature-skill-package.md").write_text("# Shared\n", encoding="utf-8")
            (root / "skills" / "_shared" / "templates" / "skill-output-template.md").write_text("# Shared\n", encoding="utf-8")
            (root / "skills" / "_shared" / "examples" / "skill-quality-example.md").write_text("# Shared\n", encoding="utf-8")
            skill_dir = root / "skills" / "bad-skill"
            skill_dir.mkdir(parents=True)
            skill_dir.joinpath("SKILL.md").write_text(
                """---
name: bad-skill
description: Too short.
---

# Bad Skill

## Agent Identity

agent.company.bad
""",
                encoding="utf-8",
            )
            (root / "skills" / "unregistered-skill").mkdir(parents=True)
            (docs / "company-skill-registry.json").write_text(
                json.dumps(
                    {
                        "version": "test",
                        "sharedContractRef": "skills/_shared/skill-output-contract.md",
                        "skills": [
                            {
                                "skillId": "bad-skill",
                                "name": "Bad Skill",
                                "ownerRole": "demo",
                                "skillDir": "skills/bad-skill",
                                "status": "active",
                                "allowedRoles": ["demo"],
                                "aliases": [],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (docs / "role-operating-specs.json").write_text(
                json.dumps(
                    {
                        "version": "test",
                        "roles": [
                            {
                                "roleId": "demo",
                                "name": "Demo Agent",
                                "defaultAgentId": "agent.company.demo",
                                "primaryOwner": "agent.company.demo",
                                "roleProfileRef": "docs/agent-team/demo-role.md",
                                "skillRegistryRef": "docs/agent-team/company-skill-registry.json",
                                "skillRefs": ["bad-skill"],
                                "capabilityTags": [],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (docs / "demo-role.md").write_text("# Demo Role\n", encoding="utf-8")

            problems = validate_bundle(Bundle(root))
            self.assertIn("skills/bad-skill/SKILL.md: description must explain when to use the skill", problems)
            self.assertTrue(any(problem.startswith("skills/bad-skill/SKILL.md: missing required sections") for problem in problems))
            self.assertIn(
                "skills/unregistered-skill: production skill directory is not registered in docs/agent-team/company-skill-registry.json",
                problems,
            )

    def test_validate_allows_legacy_task_result_runtime_metadata_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            result_dir = root / "task-results"
            result_dir.mkdir(parents=True, exist_ok=True)
            (result_dir / "tr-legacy-runtime-metadata.md").write_text(
                """---
type: TaskResult
title: Legacy runtime metadata
timestamp: 2026-06-18T00:00:00Z
completedAt: 2026-06-18T00:05:00Z
resultId: TR-LEGACY-RUNTIME-METADATA
taskId: KT-LEGACY-RUNTIME-METADATA
projectId: demo
status: done
summary: Legacy result predates TaskResult runtime metadata fields.
executorAgent: agent.company.development
runnerId: runner.legacy
outputRefs: []
evidenceRefs: []
testsOrChecks: []
nextActions: []
acceptancePolicy: {"acceptanceStatus":"auto_accepted"}
qualityEvaluation: {"decision":"close"}
---

## Summary

Legacy result.
""",
                encoding="utf-8",
            )
            problems = validate_bundle(Bundle(root))
            self.assertFalse([problem for problem in problems if "TaskResult missing required field" in problem])

    def test_validate_keeps_current_task_result_contract_strict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            result_dir = root / "task-results"
            result_dir.mkdir(parents=True, exist_ok=True)
            (result_dir / "tr-current-missing-runtime-metadata.md").write_text(
                """---
type: TaskResult
title: Current result missing runtime metadata
createdAt: 2026-06-21T00:00:00Z
taskResultContract: current
timestamp: 2026-06-21T00:00:00Z
completedAt: 2026-06-21T00:05:00Z
resultId: TR-CURRENT-MISSING-RUNTIME-METADATA
taskId: KT-CURRENT-MISSING-RUNTIME-METADATA
projectId: demo
status: done
summary: Current result must include runner and lease proof.
executorAgent: agent.company.development
outputRefs: []
evidenceRefs: []
risks: []
blockers: []
nextAction: close
checks: []
approvalRequest: ""
qualityEvaluation: {"decision":"close"}
---

## Summary

Current result.
""",
                encoding="utf-8",
            )
            problems = validate_bundle(Bundle(root))
            self.assertIn(
                "task-results/tr-current-missing-runtime-metadata.md: TaskResult missing required field runner",
                problems,
            )
            self.assertIn(
                "task-results/tr-current-missing-runtime-metadata.md: TaskResult missing required field leaseProof",
                problems,
            )

    def test_project_intake_creates_launch_and_manual_initialization_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            result = create_project_launch(
                bundle,
                project_name="Agent Hub 与知识工程中枢",
                owner="梅晓华",
                goal="建设公司 Agent Hub、中央调度器和知识工程底座",
                source="已有仓库接入",
                repo_url="https://github.com/meimei7959/company_knowledge_core.git",
                requested_agents="产品/研发/测试/知识工程",
                requester="ou_meimei",
                ring_enabled=False,
            )
            self.assertEqual(result["projectId"], "agent-hub")
            project = load_object(root / result["projectRef"])
            self.assertEqual(project["projectSourceMode"], "existing_repo")
            self.assertEqual(project["status"], "project_draft")
            launch = load_object(root / result["launchRef"])
            self.assertEqual(launch["type"], "ProjectDraft")
            init_task = load_object(root / result["initTaskRef"])
            self.assertEqual(init_task["status"], "waiting_runner")
            self.assertEqual(init_task["taskType"], "project_initialization")
            self.assertTrue(init_task["qualityGateRequired"])
            self.assertIn("handoffContract", init_task)
            self.assertFalse(validate_bundle(bundle))

    def test_project_intake_new_project_generates_repository_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            result = create_project_launch(
                Bundle(root),
                project_name="小红书运营助手",
                owner="运营 Agent",
                goal="搭建长期运营项目，沉淀选题、发布和复盘流程",
                source="运营长期项目",
                requester="ou_ops",
            )
            project = load_object(root / result["projectRef"])
            self.assertEqual(project["projectSourceMode"], "operations_long_running")
            self.assertTrue(str(project["repositoryName"]).startswith("project-"))
            self.assertEqual(project["workspaceRef"], "pending_confirmation")
            self.assertEqual(project["workspaceConfirmation"], "pending")

    def test_project_workspace_ref_validation_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            project_dir = root / "projects" / "demo"
            project_dir.mkdir(parents=True)
            project_path = project_dir / "project.md"
            project_path.write_text(
                """---
type: Project
title: Demo
projectId: demo
owner: meimei
status: draft
---

## Goal

Demo.
""",
                encoding="utf-8",
            )
            problems = validate_bundle(Bundle(root))
            self.assertIn(
                "projects/demo/project.md: Project missing workspaceRef; use an explicit path/ref or pending_confirmation",
                problems,
            )
            update_frontmatter_file(project_path, {"workspaceRef": "pending_confirmation"})
            problems = validate_bundle(Bundle(root))
            self.assertFalse([problem for problem in problems if "workspaceRef" in problem])
            update_frontmatter_file(project_path, {"status": "active"})
            problems = validate_bundle(Bundle(root))
            self.assertIn(
                "projects/demo/project.md: Project workspaceRef pending_confirmation cannot be used after project activation",
                problems,
            )
            update_frontmatter_file(project_path, {"workspaceRef": "/tmp/demo-workspace", "workspaceConfirmation": "confirmed"})
            problems = validate_bundle(Bundle(root))
            self.assertFalse([problem for problem in problems if "workspaceRef" in problem])

    def test_project_register_records_workspace_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            workspace = str(root / "workspace-demo")
            self.assertEqual(
                main(["--root", str(root), "project", "register", "--project-id", "demo", "--name", "Demo", "--owner", "meimei", "--workspace-ref", workspace]),
                0,
            )
            project = load_object(root / "projects" / "demo" / "project.md")
            self.assertEqual(project["workspaceRef"], workspace)
            self.assertEqual(project["workspaceConfirmation"], "confirmed")
            self.assertFalse(validate_bundle(Bundle(root)))

    def test_central_record_size_guard_blocks_bulky_project_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            project_dir = root / "projects" / "demo"
            project_dir.mkdir(parents=True)
            (project_dir / "project.md").write_text(
                """---
type: Project
title: Demo
projectId: demo
owner: meimei
status: draft
workspaceRef: /tmp/demo
---

## Goal

Demo.
""",
                encoding="utf-8",
            )
            big_result = project_dir / "task-results" / "tr-big.md"
            big_result.parent.mkdir(parents=True)
            big_result.write_text(
                """---
type: TaskResult
title: Big result
taskId: BIG
projectId: demo
runner: local
leaseProof: ""
executorAgent: agent.company.development
status: submitted
blockers: []
nextAction: done
checks: []
approvalRequest: {}
qualityEvaluation: {"decision":"close"}
acceptancePolicy: {"acceptanceStatus":"accepted"}
---

"""
                + ("x" * (70 * 1024)),
                encoding="utf-8",
            )
            problems = validate_bundle(Bundle(root))
            self.assertTrue(any("central record is" in problem and "storageRef" in problem for problem in problems))

    def test_source_material_bulky_types_require_storage_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            source_dir = root / "sources"
            source = source_dir / "prd.md"
            source.write_text(
                """---
type: SourceMaterial
title: PRD
sourceId: source-prd
status: draft
materialType: docx
sourceRef: /tmp/prd.docx
storageRef: ""
---

## Original Text

metadata only.
""",
                encoding="utf-8",
            )
            problems = validate_bundle(Bundle(root))
            self.assertIn(
                "sources/prd.md: bulky SourceMaterial type docx requires storageRef; central record must not store raw artifact data",
                problems,
            )

    def test_init_project_script_requires_confirmed_or_pending_workspace(self) -> None:
        spec = importlib.util.spec_from_file_location("init_project_script", REPO_ROOT / "scripts" / "init_project.py")
        self.assertIsNotNone(spec)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            old_argv = sys.argv
            try:
                sys.argv = [
                    "init_project.py",
                    "--root",
                    str(root),
                    "--project-id",
                    "demo",
                    "--name",
                    "Demo",
                    "--owner",
                    "meimei",
                ]
                with contextlib.redirect_stderr(io.StringIO()) as err:
                    self.assertEqual(module.main(), 2)
                self.assertIn("workspace path is not confirmed", err.getvalue())

                workspace = root / "Demo Workspace"
                sys.argv = [
                    "init_project.py",
                    "--root",
                    str(root),
                    "--project-id",
                    "demo",
                    "--name",
                    "Demo",
                    "--owner",
                    "meimei",
                    "--workspace-ref",
                    str(workspace),
                    "--goal",
                    "Initialize Demo",
                ]
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(module.main(), 0)
                project = load_object(root / "projects" / "demo" / "project.md")
                self.assertEqual(project["workspaceRef"], str(workspace))
                self.assertTrue((workspace / "00_原始资料").is_dir())
                self.assertTrue((workspace / "AGENTS.md").is_file())
                self.assertTrue((workspace / "START_HERE.md").is_file())
                self.assertIn("centralRoot", (workspace / "AGENTS.md").read_text(encoding="utf-8"))
                self.assertFalse(validate_bundle(Bundle(root)))
            finally:
                sys.argv = old_argv

    def test_role_handoff_creates_next_role_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "demo", "--name", "Demo", "--owner", "meimei"]), 0)
            task_path = create_project_task(
                bundle,
                "Clarify MVP requirements",
                "demo",
                "meimei",
                "agent.company.product-manager",
                task_type="product_requirement",
                task_id="PT-HANDOFF-001",
                expected_output=["Requirement brief and acceptance criteria."],
            )
            self.assertEqual(load_object(task_path)["handoffContract"]["to"], "agent.company.design")
            result_path = finish_project_task(
                bundle,
                "PT-HANDOFF-001",
                "done",
                "需求已澄清，包含核心用户场景、范围边界和验收标准。",
                output_refs=["projects/demo/product/prd.md"],
                evidence_refs=["projects/demo/decisions.md"],
                handoff_to="agent.company.design",
                next_suggested_task="Create UX flow and state spec",
            )
            result = load_object(result_path)
            self.assertEqual(result["qualityEvaluation"]["decision"], "handoff_ready")
            self.assertEqual(result["handoffContract"]["handoffTo"], "agent.company.design")
            self.assertEqual(result["acceptancePolicy"]["acceptanceStatus"], "waiting_acceptance")
            self.assertTrue(result["acceptancePolicy"]["humanAcceptanceRequired"])
            self.assertEqual(load_object(task_path)["status"], "waiting_acceptance")
            self.assertFalse(result["followupTaskRefs"])
            notifications = [load_object(path) for path in (root / "notifications").glob("*.md") if path.name != "index.md"]
            self.assertTrue(any(item.get("messageType") == "task_result_pm_review_required" for item in notifications))
            acceptance = accept_project_task_result(
                bundle,
                "PT-HANDOFF-001",
                "accepted",
                "meimei",
                reason="符合需求，可以进入设计",
                human=True,
            )
            self.assertEqual(acceptance["taskStatus"], "done")
            result = load_object(result_path)
            self.assertTrue(result["followupTaskRefs"])
            followup = load_object(root / result["followupTaskRefs"][0])
            self.assertEqual(followup["assignee"], "agent.company.design")
            self.assertEqual(followup["taskType"], "role_handoff")

    def test_scheduler_tick_claims_project_manager_handoff_when_runner_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "demo", "--name", "Demo", "--owner", "meimei"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "runner",
                        "register",
                        "--runner-id",
                        "runner.pm",
                        "--name",
                        "PM Runner",
                        "--agent",
                        "agent.company.project-manager",
                        "--capability",
                        "project_coordination",
                        "--project",
                        "demo",
                    ]
                ),
                0,
            )
            create_project_task(
                bundle,
                "Project Manager Agent handoff",
                "demo",
                "agent.company.product-manager",
                "agent.company.project-manager",
                task_type="project_coordination",
                task_id="PM-HANDOFF-001",
                expected_output=["Implementation coordination plan."],
            )

            result = schedule_project_tasks(bundle, "demo", claim=True, lease_seconds=120)

            self.assertEqual(result["counts"]["claimed"], 1)
            self.assertEqual(result["items"][0]["taskId"], "PM-HANDOFF-001")
            self.assertEqual(result["items"][0]["runnerId"], "runner.pm")
            task = load_object(root / "projects/demo/tasks/pm-handoff-001.md")
            self.assertEqual(task["status"], "processing")
            self.assertEqual(task["assignedRunner"], "runner.pm")
            self.assertEqual(task["leaseOwner"], "runner.pm")
            self.assertTrue(result["items"][0]["leaseToken"].startswith("lease."))

    def test_scheduler_tick_marks_downstream_task_waiting_runner_when_no_runner_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "demo", "--name", "Demo", "--owner", "meimei"]), 0)
            create_project_task(
                bundle,
                "Implement downstream feature",
                "demo",
                "agent.company.project-manager",
                "agent.company.development",
                task_type="development",
                task_id="DEV-DOWNSTREAM-001",
                expected_output=["Code change and tests."],
            )

            result = schedule_project_tasks(bundle, "demo")

            self.assertEqual(result["counts"]["waitingRunner"], 1)
            self.assertEqual(result["items"][0]["action"], "waiting_runner")
            task = load_object(root / "projects/demo/tasks/dev-downstream-001.md")
            self.assertEqual(task["status"], "waiting_runner")
            notifications = [load_object(path) for path in (root / "notifications").glob("*.md") if path.name != "index.md"]
            self.assertTrue(any(item.get("messageType") == "task_waiting_runner" for item in notifications))

    def test_scheduler_tick_cli_assigns_matching_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "demo", "--name", "Demo", "--owner", "meimei"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "runner",
                        "register",
                        "--runner-id",
                        "runner.dev",
                        "--name",
                        "Dev Runner",
                        "--agent",
                        "agent.company.development",
                        "--capability",
                        "development",
                        "--project",
                        "demo",
                    ]
                ),
                0,
            )
            create_project_task(
                bundle,
                "Implement dispatchable work",
                "demo",
                "agent.company.project-manager",
                "agent.company.development",
                task_type="development",
                task_id="DEV-DISPATCH-001",
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["--root", str(root), "scheduler", "tick", "--project", "demo"]), 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result["counts"]["assigned"], 1)
            task = load_object(root / "projects/demo/tasks/dev-dispatch-001.md")
            self.assertEqual(task["assignedRunner"], "runner.dev")

    def test_scheduler_claim_prefers_high_priority_development_technical_solution_before_design(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "demo", "--name", "Demo", "--owner", "meimei"]), 0)
            self.register_runner_fixture(root, "runner.dev", "agent.company.development", "development", "demo")
            self.register_runner_fixture(root, "runner.design", "agent.company.design", "design", "demo")
            design_task_path = create_project_task(
                bundle,
                "Medium priority design task",
                "demo",
                "agent.company.project-manager",
                "agent.company.design",
                task_type="design",
                task_id="AAA-DESIGN-001",
                priority="medium",
                expected_output=["Design exploration."],
            )
            dev_task_path = create_project_task(
                bundle,
                "High priority development technical solution",
                "demo",
                "agent.company.project-manager",
                "agent.company.development",
                task_type="development",
                task_id="ZZZ-DEV-001",
                priority="high",
                expected_output=["Technical solution before implementation."],
            )
            update_frontmatter_file(design_task_path, {"currentStage": "design_solution"})
            update_frontmatter_file(
                dev_task_path,
                {
                    "currentStage": "technical_solution",
                    "technicalSolutionRequired": True,
                    "requirementRefs": ["ANOS-REQ-010"],
                },
            )

            result = schedule_project_tasks(bundle, "demo", claim=True, lease_seconds=120, limit=1)

            self.assertEqual(result["counts"]["claimed"], 1)
            self.assertEqual(result["items"][0]["taskId"], "ZZZ-DEV-001")
            dev_task = load_object(dev_task_path)
            design_task = load_object(design_task_path)
            self.assertEqual(dev_task["status"], "processing")
            self.assertNotEqual(design_task["status"], "processing")

    def test_scheduler_autopilot_cli_runs_limited_rounds_and_returns_decision_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "demo", "--name", "Demo", "--owner", "meimei"]), 0)
            self.register_runner_fixture(root, "runner.dev", "agent.company.development", "development", "demo")
            task_path = create_project_task(
                bundle,
                "Autopilot development technical solution",
                "demo",
                "agent.company.project-manager",
                "agent.company.development",
                task_type="development",
                task_id="DEV-AUTO-001",
                priority="high",
                expected_output=["Technical solution TaskResult."],
            )
            update_frontmatter_file(
                task_path,
                {
                    "currentStage": "technical_solution",
                    "technicalSolutionRequired": True,
                    "requirementRefs": ["ANOS-REQ-010"],
                },
            )

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assert_cli_ok(
                    [
                        "--root",
                        str(root),
                        "scheduler",
                        "autopilot",
                        "--project",
                        "demo",
                        "--max-rounds",
                        "2",
                        "--lease-seconds",
                        "120",
                    ],
                    "scheduler autopilot must support finite --max-rounds and return a JSON decision summary.",
                )
            summary = json.loads(output.getvalue())
            self.assertEqual(summary["projectId"], "demo")
            self.assertLessEqual(summary["roundsRun"], 2)
            self.assertTrue(summary["dryRun"])
            self.assertEqual(summary["counts"]["claimed"], 0)
            self.assertGreaterEqual(summary["counts"]["assigned"], 1)
            self.assertTrue(summary["decisions"])
            self.assertTrue(any(item.get("taskId") == "DEV-AUTO-001" for item in summary["decisions"]))

            claim_output = io.StringIO()
            with contextlib.redirect_stdout(claim_output):
                self.assert_cli_ok(
                    [
                        "--root",
                        str(root),
                        "scheduler",
                        "autopilot",
                        "--project",
                        "demo",
                        "--max-rounds",
                        "1",
                        "--lease-seconds",
                        "120",
                        "--claim",
                    ],
                    "scheduler autopilot must require explicit --claim before leasing work.",
                )
            claimed_summary = json.loads(claim_output.getvalue())
            self.assertFalse(claimed_summary["dryRun"])
            self.assertGreaterEqual(claimed_summary["counts"]["claimed"], 1)
            claimed_task = load_object(task_path)
            self.assertEqual(claimed_task["status"], "processing")
            self.assertEqual(claimed_task["leaseAttempt"], 1)
            self.assertTrue(claimed_task["leaseTokenHash"])
            self.assertTrue(claimed_task["leaseHeartbeatAt"])

    def test_worker_run_development_technical_solution_writes_task_result_for_pm_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "demo", "--name", "Demo", "--owner", "meimei"]), 0)
            self.register_runner_fixture(root, "runner.dev", "agent.company.development", "development", "demo")
            task_path = create_project_task(
                bundle,
                "Development technical solution",
                "demo",
                "agent.company.project-manager",
                "agent.company.development",
                task_type="development",
                task_id="DEV-WORKER-001",
                priority="high",
                expected_output=["Technical solution with evidence and next actions."],
            )
            update_frontmatter_file(
                task_path,
                {
                    "currentStage": "technical_solution",
                    "technicalSolutionRequired": True,
                    "requirementRefs": ["ANOS-REQ-010", "ANOS-REQ-011"],
                },
            )

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assert_cli_ok(
                    [
                        "--root",
                        str(root),
                        "worker",
                        "run",
                        "--project",
                        "demo",
                        "--agent",
                        "agent.company.development",
                        "--runner",
                        "runner.dev",
                        "--stage",
                        "technical_solution",
                        "--limit",
                        "1",
                    ],
                    "worker run must claim and execute one technical_solution task for the requested agent.",
                )
            summary = json.loads(output.getvalue())
            self.assertEqual(summary["projectId"], "demo")
            self.assertEqual(summary["counts"]["resultsSubmitted"], 1)
            self.assertTrue(any(item.get("taskId") == "DEV-WORKER-001" for item in summary["items"]))
            task = load_object(task_path)
            self.assertNotEqual(task["status"], "processing")
            self.assertIn(task["status"], ["waiting_pm_review", "waiting_acceptance"])
            self.assertTrue(task["resultRef"])
            result = load_object(root / task["resultRef"])
            self.assertEqual(result["type"], "TaskResult")
            self.assertEqual(result["taskId"], "DEV-WORKER-001")
            self.assertEqual(result["executorAgent"], "agent.company.development")
            self.assertIn(result.get("runner") or result.get("runnerId"), ["runner.dev"])
            self.assertEqual(result["requirementRefs"], ["ANOS-REQ-010", "ANOS-REQ-011"])
            self.assertTrue(result.get("nextActions"))
            self.assertTrue(result.get("evidenceRefs") or result.get("evidence"))
            self.assertEqual(main(["--root", str(root), "validate"]), 0)

    def test_worker_run_product_requirement_writes_task_result_before_technical_solution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "demo", "--name", "Demo", "--owner", "meimei"]), 0)
            self.register_runner_fixture(root, "runner.product", "agent.company.product-manager", "product_requirement", "demo")
            task_path = create_project_task(
                bundle,
                "V1 product requirement structure",
                "demo",
                "agent.company.project-manager",
                "agent.company.product-manager",
                task_type="product_requirement",
                task_id="PROD-WORKER-001",
                priority="critical",
                expected_output=["V1 product package and acceptance matrix."],
            )
            update_frontmatter_file(
                task_path,
                {
                    "currentStage": "product_requirement",
                    "technicalSolutionRequired": False,
                    "requiredCapabilities": ["product_requirement"],
                },
            )

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assert_cli_ok(
                    [
                        "--root",
                        str(root),
                        "worker",
                        "run",
                        "--project",
                        "demo",
                        "--agent",
                        "agent.company.product-manager",
                        "--runner",
                        "runner.product",
                        "--stage",
                        "product_requirement",
                        "--limit",
                        "1",
                    ],
                    "worker run must claim and execute one product_requirement task before technical_solution work is released.",
                )
            summary = json.loads(output.getvalue())
            self.assertEqual(summary["counts"]["resultsSubmitted"], 1)
            self.assertEqual(summary["items"][0]["action"], "submitted_product_requirement")
            task = load_object(task_path)
            self.assertIn(task["status"], ["waiting_pm_review", "waiting_acceptance"])
            result = load_object(root / task["resultRef"])
            self.assertEqual(result["type"], "TaskResult")
            self.assertEqual(result["executorAgent"], "agent.company.product-manager")
            self.assertIn("product_requirement_package_generated", result["testsOrChecks"])
            self.assertTrue(any("Product Manager Agent lock V1 scope" in item for item in result["nextActions"]))
            self.assertEqual(main(["--root", str(root), "validate"]), 0)

    def test_claim_task_with_docx_source_keeps_binary_reference_in_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            attachment = root / "input.docx"
            attachment.write_bytes(b"\xd0\xcf\x11\xe0 binary doc payload")
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "demo", "--name", "Demo", "--owner", "meimei"]), 0)
            self.register_runner_fixture(root, "runner.product", "agent.company.product-manager", "product_requirement", "demo")
            task_path = create_project_task(
                bundle,
                "V1 product requirement with document source",
                "demo",
                "agent.company.project-manager",
                "agent.company.product-manager",
                task_type="product_requirement",
                task_id="PROD-DOCX-001",
                priority="critical",
                source_material_refs=[str(attachment)],
            )
            update_frontmatter_file(
                task_path,
                {
                    "currentStage": "product_requirement",
                    "requiredCapabilities": ["product_requirement"],
                },
            )

            claim = claim_project_task(bundle, "PROD-DOCX-001", "runner.product")

            context_ref = claim.get("contextRef")
            self.assertTrue(context_ref)
            context_text = (root / context_ref).read_text(encoding="utf-8")
            self.assertIn("Binary or rich document source retained by reference", context_text)
            self.assertIn(str(attachment), context_text)

    def test_worker_run_product_review_locks_scope_before_development_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "demo", "--name", "Demo", "--owner", "meimei"]), 0)
            self.register_runner_fixture(root, "runner.product", "agent.company.product-manager", "product_review", "demo")
            task_path = create_project_task(
                bundle,
                "V1 product scope review",
                "demo",
                "agent.company.project-manager",
                "agent.company.product-manager",
                task_type="product_review",
                task_id="PROD-REVIEW-001",
                priority="high",
                expected_output=["V1 scope acceptance criteria."],
            )
            update_frontmatter_file(
                task_path,
                {
                    "currentStage": "solution_review",
                    "requiredCapabilities": ["product_review"],
                },
            )

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assert_cli_ok(
                    [
                        "--root",
                        str(root),
                        "worker",
                        "run",
                        "--project",
                        "demo",
                        "--agent",
                        "agent.company.product-manager",
                        "--runner",
                        "runner.product",
                        "--stage",
                        "solution_review",
                        "--limit",
                        "1",
                    ],
                    "worker run must execute product_review and lock scope before development release.",
                )
            summary = json.loads(output.getvalue())
            self.assertEqual(summary["counts"]["resultsSubmitted"], 1)
            self.assertEqual(summary["items"][0]["action"], "submitted_product_review")
            result = load_object(root / load_object(task_path)["resultRef"])
            self.assertIn("v1_scope_locked", result["testsOrChecks"])
            self.assertTrue(any("release Development Agent technical solution" in item for item in result["nextActions"]))

    def test_v1_single_machine_acceptance_runs_device_aware_closed_loop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "demo", "--name", "Demo", "--owner", "meimei"]), 0)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assert_cli_ok(
                    ["--root", str(root), "v1", "acceptance", "run", "--project", "demo"],
                    "v1 acceptance run should complete the single-machine closed loop.",
                )
            summary = json.loads(output.getvalue())
            self.assertEqual(summary["status"], "accepted")
            self.assertIn("local_device_registered", summary["testsOrChecks"])
            self.assertIn("device_aware_route_recorded", summary["testsOrChecks"])
            run = load_object(root / summary["runRef"])
            self.assertEqual(run["type"], "V1AcceptanceRun")
            self.assertEqual(len(run["sessionRefs"]), 4)
            confirm_message = load_object(root / run["confirmMessageRef"])
            self.assertEqual(confirm_message["messageType"], "confirm_request")
            self.assertEqual(confirm_message["routing"]["targetDeviceId"], "device.local")
            self.assertTrue(run["devExecution"]["worktreeRef"])
            self.assertTrue((root / run["devExecution"]["resultRef"]).exists())
            self.assertTrue((root / run["testExecution"]["resultRef"]).exists())
            product_task_path = create_project_task(
                Bundle(root),
                "V1 product final acceptance",
                "demo",
                "agent.company.project-manager",
                "agent.company.product-manager",
                task_type="product_review",
                task_id="KT-V1-PRODUCT-FINAL",
                priority="high",
                source_material_refs=[summary["runRef"], run["testExecution"]["resultRef"]],
                expected_output=["Product final acceptance verdict."],
            )
            update_frontmatter_file(
                product_task_path,
                {
                    "currentStage": "solution_review",
                    "technicalSolutionRequired": False,
                    "requiredCapabilities": ["product_review"],
                },
            )
            package_output = io.StringIO()
            with contextlib.redirect_stdout(package_output):
                self.assert_cli_ok(
                    [
                        "--root",
                        str(root),
                        "v1",
                        "package",
                        "compile",
                        "--task-id",
                        "KT-V1-PRODUCT-FINAL",
                        "--from-agent",
                        "agent.company.project-manager",
                        "--to-agent",
                        "agent.company.product-manager",
                        "--project",
                        "demo",
                    ],
                    "PM should package final product acceptance for Product Agent.",
                )
            package = load_object(Path(package_output.getvalue().strip()))
            runtime_output = io.StringIO()
            with contextlib.redirect_stdout(runtime_output):
                self.assert_cli_ok(
                    [
                        "--root",
                        str(root),
                        "v1",
                        "runtime",
                        "execute",
                        "--package-id",
                        package["packageId"],
                        "--runner",
                        "runner.v1.local.product",
                        "--agent",
                        "agent.company.product-manager",
                    ],
                    "Product Agent should execute final acceptance through V1 runtime.",
                )
            product_execution = json.loads(runtime_output.getvalue())
            product_result = load_object(root / product_execution["resultRef"])
            self.assertIn("Product Agent final verdict: accepted", product_result["summary"])
            self.assertIn("product_final_acceptance_verdict_recorded", product_result["testsOrChecks"])
            self.assertIn("device_aware_route_verified", product_result["testsOrChecks"])
            live_model_path = root / "workbench-live-read-model.js"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assert_cli_ok(
                    [
                        "--root",
                        str(root),
                        "v1",
                        "workbench",
                        "export",
                        "--project",
                        "demo",
                        "--format",
                        "js",
                        "--out",
                        str(live_model_path),
                    ],
                    "V1 workbench export should write a live runtime read model.",
                )
            prefix = "window.ZHENZHI_DESKTOP_WORKBENCH_READ_MODEL = "
            live_source = live_model_path.read_text(encoding="utf-8").strip()
            self.assertTrue(live_source.startswith(prefix))
            live_model = json.loads(live_source[len(prefix) : -1])
            self.assertEqual("real-v1-runtime-read-model", live_model["runtimeReadModelKind"])
            self.assertFalse(live_model["fixture"])
            self.assertTrue(any(item["deviceId"] == "device.local" for item in live_model["devices"]))
            self.assertTrue(any(item["routing"]["targetDeviceId"] == "device.local" for item in live_model["agentMessages"]))
            self.assertTrue(live_model["runtimeMetrics"]["productFinalAccepted"])
            self.assertEqual(main(["--root", str(root), "validate"]), 0)

    def test_auto_execution_loop_task_metadata_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "demo", "--name", "Demo", "--owner", "meimei"]), 0)
            self.register_runner_fixture(root, "runner.dev", "agent.company.development", "development", "demo")
            task_path = create_project_task(
                bundle,
                "Valid technical solution task metadata",
                "demo",
                "agent.company.project-manager",
                "agent.company.development",
                task_type="development",
                task_id="DEV-VALIDATE-001",
                priority="high",
                expected_output=["Technical solution before implementation."],
            )
            update_frontmatter_file(
                task_path,
                {
                    "currentStage": "technical_solution",
                    "technicalSolutionRequired": True,
                    "requirementRefs": ["ANOS-REQ-010"],
                    "nextRequiredAction": "worker_run",
                },
            )

            self.assertEqual(main(["--root", str(root), "validate"]), 0)

    def test_scheduler_tick_releases_ready_product_handoff_to_project_manager(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "demo", "--name", "Demo", "--owner", "meimei"]), 0)
            task_path = create_project_task(
                bundle,
                "Complete product package",
                "demo",
                "meimei",
                "agent.company.product-manager",
                task_type="product_requirement",
                task_id="PRODUCT-PACKAGE-001",
                expected_output=["Complete product package."],
            )
            update_frontmatter_file(task_path, {"status": "done", "resultRef": "task-results/tr-product-package-001.md"})
            result_path = root / "task-results/tr-product-package-001.md"
            result_path.write_text(
                """---
type: TaskResult
title: Product package result
description: Product Manager Agent completed package.
timestamp: "2026-06-21T00:00:00Z"
resultId: tr-product-package-001
taskId: PRODUCT-PACKAGE-001
projectId: demo
assignee: agent.company.product-manager
executorAgent: agent.company.product-manager
status: done
summary: Product package complete.
outputRefs:
  - docs/product/demo/index.md
followupTaskRefs: []
qualityEvaluation:
  passed: true
  decision: handoff_ready
acceptancePolicy:
  acceptanceStatus: accepted
  humanAcceptanceRequired: true
handoffContract:
  fromAgent: agent.company.product-manager
  handoffTo: agent.company.project-manager
  handoffSummary: Product package complete; project manager should coordinate execution.
  nextSuggestedTask: Coordinate complete product package execution
---
## Summary

Product package complete.
""",
                encoding="utf-8",
            )

            result = schedule_project_tasks(bundle, "demo")

            self.assertEqual(len(result["releasedFollowups"]), 1)
            followup = load_object(root / result["releasedFollowups"][0]["followupTaskRef"])
            self.assertEqual(followup["assignee"], "agent.company.project-manager")
            self.assertEqual(followup["status"], "waiting_runner")
            updated_result = load_object(result_path)
            self.assertEqual(updated_result["followupTaskRefs"], [result["releasedFollowups"][0]["followupTaskRef"]])

    def test_quality_retry_and_escalation_for_role_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            create_project_task(bundle, "Implement feature", "qa", "meimei", "agent.company.development", task_type="development", task_id="DEV-001")
            result_path = finish_project_task(bundle, "DEV-001", "done", "实现完成。")
            result = load_object(result_path)
            self.assertFalse(result["qualityEvaluation"]["passed"])
            self.assertEqual(result["qualityEvaluation"]["decision"], "retry_required")
            retry_task = load_object(root / result["followupTaskRefs"][0])
            self.assertEqual(retry_task["retryOf"], "DEV-001")
            create_project_task(bundle, "Blocked task", "qa", "meimei", "agent.company.development", task_type="development", task_id="DEV-002")
            blocked_result_path = finish_project_task(bundle, "DEV-002", "blocked", "缺少仓库权限。")
            blocked_result = load_object(blocked_result_path)
            self.assertEqual(blocked_result["qualityEvaluation"]["decision"], "escalate_to_project_manager")
            blocker_task = load_object(root / blocked_result["followupTaskRefs"][0])
            self.assertEqual(blocker_task["assignee"], "agent.company.project-manager")

    def test_project_task_finish_non_knowledge_role_tasks_skip_knowledge_draft_permission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            cases = [
                ("DEV-PERM-001", "development", "agent.company.development"),
                ("TEST-PERM-001", "testing", "agent.company.test"),
                ("DESIGN-PERM-001", "design", "agent.company.design"),
                ("PRODUCT-PERM-001", "product_requirement", "agent.company.product-manager"),
            ]
            for task_id, task_type, executor_agent in cases:
                create_project_task(
                    bundle,
                    f"Close {task_type}",
                    "qa",
                    "meimei",
                    executor_agent,
                    task_type=task_type,
                    task_id=task_id,
                    expected_output=["Evidence-backed closeout."],
                )
                result_path = finish_project_task(
                    bundle,
                    task_id,
                    "done",
                    f"{task_type} work completed without reusable knowledge.",
                    output_refs=[f"projects/qa/outputs/{task_id.lower()}.md"],
                    evidence_refs=[f"projects/qa/evidence/{task_id.lower()}.md"],
                    tests_or_checks=["permission boundary regression passed"],
                    executor_agent=executor_agent,
                )
                result = load_object(result_path)
                self.assertEqual(result["knowledgeRefs"], [])
                self.assertEqual(result["executorAgent"], executor_agent)

    def test_project_task_finish_knowledge_draft_requires_executor_permission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            self.assertEqual(main(["--root", str(root), "agent", "register", "--agent-id", "agent.no.knowledge", "--name", "No Knowledge", "--owner", "meimei", "--purpose", "permission negative"]), 0)
            create_project_task(
                bundle,
                "Draft reusable lesson",
                "qa",
                "meimei",
                "agent.no.knowledge",
                task_type="development",
                task_id="DEV-KNOWLEDGE-PERM-001",
                expected_output=["Knowledge draft permission negative path."],
            )

            with self.assertRaisesRegex(KnowledgeError, "lacks write permission: knowledge:draft"):
                finish_project_task(
                    bundle,
                    "DEV-KNOWLEDGE-PERM-001",
                    "done",
                    "Attempted reusable knowledge write.",
                    evidence_refs=["projects/qa/evidence/dev-knowledge-perm-001.md"],
                    tests_or_checks=["permission negative path"],
                    executor_agent="agent.no.knowledge",
                    knowledge_draft={
                        "title": "Reusable lesson must be permissioned",
                        "summary": "Reusable knowledge writes require knowledge:draft.",
                        "structured": "Only Agents with knowledge:draft may create KnowledgeItem drafts from task finish.",
                        "sourceRefs": ["projects/qa/evidence/dev-knowledge-perm-001.md"],
                        "confidence": "medium",
                        "scope": "engineering",
                    },
                )
            self.assertFalse((root / "knowledge" / "engineering").exists())
            self.assertFalse((root / "task-results" / "tr-dev-knowledge-perm-001.md").exists())

    def test_failed_test_check_blocks_project_task_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            create_project_task(
                bundle,
                "Fix Feishu callback",
                "qa",
                "meimei",
                "agent.company.development",
                task_type="development",
                task_id="DEV-FAILED-CHECK-001",
                expected_output=["callback handles card submit"],
            )
            result_path = finish_project_task(
                bundle,
                "DEV-FAILED-CHECK-001",
                "done",
                "Callback handles card submit.",
                evidence_refs=["projects/qa/evidence/feishu-callback.md"],
                tests_or_checks=["pytest failed: callback action returned 500"],
            )
            result = load_object(result_path)
            self.assertFalse(result["qualityEvaluation"]["passed"])
            self.assertEqual(result["qualityEvaluation"]["decision"], "retry_required")
            self.assertTrue(any("tests/checks reported failure" in item for item in result["qualityEvaluation"]["reasons"]))
            self.assertEqual(load_object(root / "projects" / "qa" / "tasks" / "dev-failed-check-001.md")["status"], "changes_requested")
            self.assertTrue(result["followupTaskRefs"])

    def test_approval_relay_blocks_closure_and_notifies_pm(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            task_path = create_project_task(
                bundle,
                "Run approval-gated migration",
                "qa",
                "meimei",
                "agent.company.development",
                task_type="engineering_action",
                task_id="DEV-APPROVAL-001",
            )
            task = load_object(task_path)
            runtime = dict(task["taskRuntime"])
            runtime["approvalRelayRequired"] = True
            update_frontmatter_file(task_path, {"taskRuntime": runtime})

            result_path = finish_project_task(
                bundle,
                "DEV-APPROVAL-001",
                "done",
                "Migration is ready but requires owner approval in a child approval surface.",
                evidence_refs=["projects/qa/evidence/migration-plan.md"],
                tests_or_checks=["dry-run passed"],
                approval_request={
                    "summary": "Approve migration execution",
                    "reason": "External approval prompt cannot be handled inside runner window.",
                    "requiredDecisionOwner": "agent.company.project-manager",
                    "externalRef": "approval://migration/001",
                },
            )
            result = load_object(result_path)
            task = load_object(task_path)
            self.assertEqual(result["status"], "blocked")
            self.assertEqual(task["status"], "blocked")
            self.assertEqual(result["approvalRequest"]["status"], "requested")
            self.assertEqual(result["approvalRequest"]["externalRef"], "approval://migration/001")
            notifications = [load_object(path) for path in (root / "notifications").glob("*.md") if path.name != "index.md"]
            self.assertIn("task_approval_relay_requested", [item["messageType"] for item in notifications])

    def test_scheduler_repairs_stale_critical_lease_and_records_runner_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            self.register_runner_fixture(root, "runner.dev", "agent.company.development", "engineering_action", "qa")
            task_path = create_project_task(
                bundle,
                "Repair stale lease",
                "qa",
                "meimei",
                "agent.company.development",
                task_type="engineering_action",
                task_id="DEV-STALE-001",
                priority="critical",
            )
            claim = claim_project_task(bundle, "DEV-STALE-001", "runner.dev", lease_seconds=600)
            self.assertTrue(claim["leaseToken"])
            update_frontmatter_file(
                task_path,
                {
                    "leaseExpiresAt": "2000-01-01T00:00:00Z",
                    "leaseHeartbeatAt": "2000-01-01T00:00:00Z",
                    "heartbeatAt": "2000-01-01T00:00:00Z",
                },
            )

            result = schedule_project_tasks(bundle, "qa")

            self.assertEqual(len(result["repairedLeases"]), 1)
            repaired_task = load_object(task_path)
            self.assertEqual(repaired_task["status"], "waiting_runner")
            self.assertEqual(repaired_task["leaseOwner"], "")
            self.assertEqual(repaired_task["staleLeaseOwner"], "runner.dev")
            runner = load_object(root / "runners" / "runner.dev.md")
            self.assertFalse(runner["currentLeases"])
            self.assertEqual(runner["staleLeases"][0]["taskId"], "DEV-STALE-001")
            notifications = [load_object(path) for path in (root / "notifications").glob("*.md") if path.name != "index.md"]
            self.assertIn("critical_stale_lease_alert", [item["messageType"] for item in notifications])

    def test_runner_heartbeat_merges_capabilities_and_projects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "ops", "--name", "Ops", "--owner", "meimei"]), 0)
            self.register_runner_fixture(root, "runner.dev", "agent.company.development", "engineering_action", "qa")

            heartbeat_agent_runner(bundle, "runner.dev", capabilities=["knowledge_capture"], available_projects=["ops"])

            runner = load_object(root / "runners" / "runner.dev.md")
            self.assertEqual(runner["capabilities"], ["engineering_action", "knowledge_capture"])
            self.assertEqual(runner["availableProjects"], ["ops", "qa"])

    def test_claim_returns_execution_context_and_safe_ref_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            self.register_runner_fixture(root, "runner.dev", "agent.company.development", "engineering_action", "qa")
            create_project_task(
                bundle,
                "Execution context transfer",
                "qa",
                "meimei",
                "agent.company.development",
                task_type="engineering_action",
                task_id="DEV-CTX-001",
            )

            claim = claim_project_task(bundle, "DEV-CTX-001", "runner.dev", lease_seconds=600)

            self.assertEqual(claim["executionContext"]["runnerId"], "runner.dev")
            self.assertEqual(claim["executionContext"]["leaseToken"], claim["leaseToken"])
            self.assertIn("--root", claim["executionContext"]["writebackCommand"])
            self.assertIn("--runner-id runner.dev", claim["executionContext"]["writebackCommand"])
            self.assertIn(f"--lease-token {claim['leaseToken']}", claim["executionContext"]["writebackCommand"])
            self.assertIn('--summary "<summary>"', claim["executionContext"]["writebackCommand"])
            self.assertTrue(claim["contextRef"])
            ref_path = root / claim["executionContextRef"]
            self.assertTrue(ref_path.exists())
            ref_text = ref_path.read_text(encoding="utf-8")
            self.assertNotIn(claim["leaseToken"], ref_text)
            self.assertIn(claim["leaseProof"], ref_text)

    def test_project_task_context_payload_includes_execution_context_for_valid_lease(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            self.register_runner_fixture(root, "runner.dev", "agent.company.development", "engineering_action", "qa")
            create_project_task(
                bundle,
                "Context payload private writeback",
                "qa",
                "meimei",
                "agent.company.development",
                task_type="engineering_action",
                task_id="DEV-CTX-002",
            )
            claim = claim_project_task(bundle, "DEV-CTX-002", "runner.dev", lease_seconds=600)

            payload = core_module.project_task_context_payload(bundle, "DEV-CTX-002", "runner.dev", claim["leaseToken"])

            self.assertEqual(payload["executionContext"]["runnerId"], "runner.dev")
            self.assertEqual(payload["executionContext"]["leaseToken"], claim["leaseToken"])
            self.assertEqual(payload["executionContext"]["contextRef"], payload["contextRef"])
            self.assertIn("task finish DEV-CTX-002", payload["executionContext"]["writebackCommand"])

    def test_workbench_exposes_environment_readiness_and_missing_env_blocks_claim(self) -> None:
        missing_env = "ZZ_TEST_REQUIRED_ENV_FOR_CLAIM"
        previous = os.environ.pop(missing_env, None)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_minimal_bundle(root)
                bundle = Bundle(root)
                self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
                self.register_runner_fixture(root, "runner.dev", "agent.company.development", "engineering_action", "qa")
                task_path = create_project_task(
                    bundle,
                    "Environment readiness",
                    "qa",
                    "meimei",
                    "agent.company.development",
                    task_type="engineering_action",
                    task_id="DEV-ENV-001",
                )
                task = load_object(task_path)
                runtime = dict(task["taskRuntime"])
                runtime["requiredEnvVars"] = [missing_env]
                update_frontmatter_file(task_path, {"taskRuntime": runtime, "requiredEnvVars": [missing_env]})

                with self.assertRaises(KnowledgeError) as ctx:
                    claim_project_task(bundle, "DEV-ENV-001", "runner.dev", lease_seconds=600)

                self.assertIn(f"env:{missing_env}", str(ctx.exception))
                blocked = load_object(task_path)
                self.assertEqual(blocked["status"], "blocked")
                model = core_module.scheduler_workbench_read_model(bundle, "qa", "DEV-ENV-001")
                self.assertEqual(model["environmentReadiness"]["status"], "blocked")
                self.assertEqual(model["environmentReadiness"]["missingEnvVars"], [missing_env])
                self.assertIn(f"env:{missing_env}", model["runnerCandidates"][0]["reasons"])
        finally:
            if previous is not None:
                os.environ[missing_env] = previous

    def test_scheduler_workbench_read_model_exposes_queue_runner_lease_and_evidence_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            self.register_runner_fixture(root, "runner.dev", "agent.company.development", "engineering_action", "qa")
            task_path = create_project_task(
                bundle,
                "Workbench scheduler surface",
                "qa",
                "meimei",
                "agent.company.development",
                task_type="engineering_action",
                task_id="DEV-WORKBENCH-001",
                priority="high",
            )
            claim = claim_project_task(bundle, "DEV-WORKBENCH-001", "runner.dev", lease_seconds=600)
            model = core_module.scheduler_workbench_read_model(bundle, "qa", "DEV-WORKBENCH-001")

            self.assertEqual(model["kind"], "SchedulerWorkbenchReadModel")
            self.assertEqual(model["selectedTaskId"], "DEV-WORKBENCH-001")
            self.assertTrue(any(item["taskId"] == "DEV-WORKBENCH-001" for item in model["activeQueue"]))
            self.assertEqual(model["leaseStatus"]["leaseOwner"], "runner.dev")
            self.assertEqual(model["leaseStatus"]["leaseAttempt"], 1)
            self.assertEqual(model["executionContextStatus"]["status"], "ready")
            self.assertEqual(model["environmentReadiness"]["status"], "ready")
            self.assertTrue(model["runnerCandidates"][0]["eligible"])
            self.assertEqual(model["runnerCandidates"][0]["runnerId"], "runner.dev")
            self.assertTrue(model["evidenceRequirements"]["testEvidenceRequired"])
            self.assertEqual(model["retryRepairPath"]["action"], "continue_execution")
            self.assertTrue(claim["leaseToken"])

    def test_agent_ring_console_lifecycle_cli_and_workbench_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            self.register_runner_fixture(root, "runner.dev", "agent.company.development", "engineering_action", "qa")
            self.register_runner_fixture(root, "runner.qa", "agent.company.development", "engineering_action", "qa")
            task_path = create_project_task(
                bundle,
                "Live handoff execution",
                "qa",
                "meimei",
                "agent.company.development",
                task_type="engineering_action",
                task_id="DEV-LIVE-001",
                priority="high",
                source_material_refs=["projects/qa/sources/live-evidence.md"],
            )
            claim = claim_project_task(bundle, "DEV-LIVE-001", "runner.dev", lease_seconds=600)

            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "task",
                            "handoff",
                            "DEV-LIVE-001",
                            "--actor",
                            "runner.dev",
                            "--to",
                            "runner.qa",
                            "--summary",
                            "Runner dev hands off with source review complete.",
                            "--runner-id",
                            "runner.dev",
                            "--lease-token",
                            claim["leaseToken"],
                            "--evidence-ref",
                            "projects/qa/sources/live-evidence.md",
                            "--preferred-runner",
                            "runner.qa",
                        ]
                    ),
                    0,
                )
            handoff_result = json.loads(out.getvalue())
            self.assertEqual(handoff_result["kind"], "TaskManualHandoffResult")
            self.assertTrue((root / handoff_result["handoffRef"]).exists())
            handoff_task = load_object(task_path)
            self.assertEqual(handoff_task["status"], "manual_handoff")
            self.assertEqual(handoff_task["manualHandoff"]["handoffTo"], "runner.qa")
            runner_dev = load_object(root / "runners" / "runner.dev.md")
            self.assertFalse(runner_dev["currentLeases"])
            self.assertEqual(runner_dev["taskHistory"][-1]["event"], "manual_handoff")

            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "task",
                            "retry",
                            "DEV-LIVE-001",
                            "--actor",
                            "agent.company.project-manager",
                            "--reason",
                            "Manual handoff accepted; resume on runner.qa.",
                            "--preferred-runner",
                            "runner.qa",
                        ]
                    ),
                    0,
                )
            retry_task = load_object(task_path)
            self.assertEqual(retry_task["status"], "waiting_runner")
            self.assertEqual(retry_task["preferredRunner"], "runner.qa")
            second_claim = claim_project_task(bundle, "DEV-LIVE-001", "runner.qa", lease_seconds=600)
            result_path = finish_project_task(
                bundle,
                "DEV-LIVE-001",
                "done",
                "Runner qa completed live execution writeback with evidence.",
                output_refs=["projects/qa/tasks/dev-live-001.md"],
                evidence_refs=["projects/qa/sources/live-evidence.md", handoff_result["handoffRef"]],
                tests_or_checks=["two runner local equivalent lifecycle evidence: pass"],
                runner_id="runner.qa",
                lease_token=second_claim["leaseToken"],
                executor_agent="agent.company.development",
            )
            self.assertEqual(result_path.relative_to(root).as_posix(), "task-results/tr-dev-live-001.md")

            cancel_task_path = create_project_task(
                bundle,
                "Cancel and retry execution",
                "qa",
                "meimei",
                "agent.company.development",
                task_type="engineering_action",
                task_id="DEV-LIVE-002",
            )
            cancel_claim = claim_project_task(bundle, "DEV-LIVE-002", "runner.dev", lease_seconds=600)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "task",
                            "cancel",
                            "DEV-LIVE-002",
                            "--actor",
                            "agent.company.project-manager",
                            "--reason",
                            "Operator cancelled stale local run.",
                            "--runner-id",
                            "runner.dev",
                            "--lease-token",
                            cancel_claim["leaseToken"],
                        ]
                    ),
                    0,
                )
            self.assertEqual(load_object(cancel_task_path)["status"], "cancelled")
            self.assertFalse(validate_bundle(bundle))
            with self.assertRaises(KnowledgeError):
                claim_project_task(bundle, "DEV-LIVE-002", "runner.qa", lease_seconds=600)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "task",
                            "retry",
                            "DEV-LIVE-002",
                            "--actor",
                            "agent.company.project-manager",
                            "--reason",
                            "Restart cancelled task on backup runner.",
                            "--preferred-runner",
                            "runner.qa",
                        ]
                    ),
                    0,
                )
            self.assertEqual(load_object(cancel_task_path)["status"], "waiting_runner")
            retry_claim = claim_project_task(bundle, "DEV-LIVE-002", "runner.qa", lease_seconds=600)
            self.assertEqual(retry_claim["task"]["leaseOwner"], "runner.qa")

            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "runner",
                        "register",
                        "--runner-id",
                        "runner.limited",
                        "--name",
                        "runner.limited",
                        "--agent",
                        "agent.company.development",
                        "--capability",
                        "engineering_action",
                        "--project",
                        "qa",
                        "--data-scope",
                        "public",
                    ]
                ),
                0,
            )
            scoped_task_path = create_project_task(
                bundle,
                "Restricted data scope",
                "qa",
                "meimei",
                "agent.company.development",
                task_type="engineering_action",
                task_id="DEV-SCOPE-001",
            )
            scoped_task = load_object(scoped_task_path)
            scoped_runtime = dict(scoped_task["taskRuntime"])
            scoped_runtime["dataScopes"] = ["restricted"]
            update_frontmatter_file(scoped_task_path, {"taskRuntime": scoped_runtime, "dataScopes": ["restricted"]})
            with self.assertRaises(KnowledgeError) as denied:
                claim_project_task(bundle, "DEV-SCOPE-001", "runner.limited", lease_seconds=600)
            self.assertIn("dataScope:restricted", str(denied.exception))
            self.assertEqual(load_object(scoped_task_path)["status"], "blocked")

            model = core_module.scheduler_workbench_read_model(bundle, "qa", "DEV-LIVE-002")
            self.assertEqual(model["kind"], "SchedulerWorkbenchReadModel")
            self.assertEqual(len(model["runnerRegistry"]), 3)
            self.assertEqual(model["metrics"]["runnerCount"], 3)
            self.assertTrue(any(item["runnerId"] == "runner.qa" for item in model["currentWork"]))
            self.assertTrue(any(item["event"] == "retry_requested" for item in model["leaseHistory"]))
            self.assertTrue(any(item["action"] == "task.retry" for item in model["auditTrail"]))

            handoff_model = core_module.scheduler_workbench_read_model(bundle, "qa", "DEV-LIVE-001")
            self.assertTrue(any(item["event"] == "manual_handoff" for item in handoff_model["leaseHistory"]))
            self.assertTrue(any(item["action"] == "task.manual_handoff" for item in handoff_model["auditTrail"]))

            scope_model = core_module.scheduler_workbench_read_model(bundle, "qa", "DEV-SCOPE-001")
            self.assertEqual(scope_model["scopeAudit"]["deniedRunnerCount"], 1)
            self.assertIn("dataScope:restricted", scope_model["scopeAudit"]["deniedRunners"][0]["reasons"])
            self.assertIn("task.claim.blocked", audit_actions(root))
            self.assertIn("task.cancel", audit_actions(root))
            self.assertIn("task.retry", audit_actions(root))
            self.assertIn("task.manual_handoff", audit_actions(root))

    def test_low_risk_project_task_auto_accepts_without_human_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "ops", "--name", "Ops", "--owner", "meimei"]), 0)
            task_path = create_project_task(
                bundle,
                "Update internal runbook",
                "ops",
                "meimei",
                "agent.company.operations",
                task_type="documentation_note",
                task_id="LOW-RISK-001",
                expected_output=["Update runbook"],
            )
            result_path = finish_project_task(
                bundle,
                "LOW-RISK-001",
                "done",
                "Update runbook with the latest internal operating note.",
                evidence_refs=["projects/ops/runbook.md"],
                tests_or_checks=["valid"],
            )
            result = load_object(result_path)
            self.assertTrue(result["qualityEvaluation"]["passed"])
            self.assertEqual(result["qualityEvaluation"]["decision"], "close")
            self.assertEqual(result["acceptancePolicy"]["acceptanceStatus"], "auto_accepted")
            self.assertFalse(result["acceptancePolicy"]["humanAcceptanceRequired"])
            self.assertEqual(load_object(task_path)["status"], "done")
            self.assertFalse(result["followupTaskRefs"])

    def test_failed_agent_result_creates_improvement_proposal_eval_and_notification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            create_project_task(bundle, "Implement feature", "qa", "meimei", "agent.company.development", task_type="development", task_id="DEV-IMPROVE-001")
            result_path = finish_project_task(bundle, "DEV-IMPROVE-001", "done", "实现完成。")
            result = load_object(result_path)
            self.assertFalse(result["qualityEvaluation"]["passed"])
            self.assertTrue(result["improvementRefs"])
            self.assertTrue(result["evalCaseRefs"])
            proposal = load_object(root / result["improvementRefs"][0])
            self.assertEqual(proposal["type"], "AgentImprovementProposal")
            self.assertEqual(proposal["agentId"], "agent.company.development")
            self.assertEqual(proposal["reuseScope"], "company")
            eval_case = load_object(root / result["evalCaseRefs"][0])
            self.assertEqual(eval_case["type"], "EvalCase")
            self.assertEqual(eval_case["status"], "draft")
            notifications = [load_object(path) for path in (root / "notifications").glob("*.md") if path.name != "index.md"]
            message_types = [item["messageType"] for item in notifications]
            self.assertIn("agent_improvement_proposal_created", message_types)
            self.assertIn("agent_improvement_action_required", message_types)
            self.assertFalse(validate_bundle(bundle))

    def test_human_rejection_creates_agent_improvement_feedback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "prd", "--name", "PRD", "--owner", "meimei"]), 0)
            create_project_task(bundle, "Write PRD", "prd", "meimei", "agent.company.product-manager", task_type="product_requirement", task_id="PM-IMPROVE-001")
            result_path = finish_project_task(
                bundle,
                "PM-IMPROVE-001",
                "done",
                "需求已澄清，包含范围、用户场景、边界和验收标准。",
                evidence_refs=["projects/prd/evidence.md"],
                handoff_to="agent.company.design",
                executor_agent="agent.company.product-manager",
            )
            result = load_object(result_path)
            self.assertTrue(result["qualityEvaluation"]["passed"])
            self.assertFalse(result["improvementRefs"])
            acceptance = accept_project_task_result(bundle, "PM-IMPROVE-001", "changes_requested", "meimei", reason="缺少关键边界条件", human=True)
            self.assertEqual(acceptance["taskStatus"], "changes_requested")
            result = load_object(result_path)
            self.assertTrue(result["improvementRefs"])
            proposal = load_object(root / result["improvementRefs"][0])
            self.assertEqual(proposal["trigger"], "humanAcceptance")
            self.assertIn("缺少关键边界条件", proposal["failureReasons"])
            self.assertFalse(validate_bundle(bundle))

    def test_agent_capability_report_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "qa", "--name", "QA", "--owner", "meimei"]), 0)
            create_project_task(bundle, "Implement feature", "qa", "meimei", "agent.company.development", task_type="development", task_id="DEV-REPORT-001")
            finish_project_task(bundle, "DEV-REPORT-001", "done", "实现完成。")
            self.assertEqual(main(["--root", str(root), "agent", "report", "--agent-id", "agent.company.development", "--project", "qa"]), 0)
            reports = [load_object(path) for path in (root / "knowledge" / "metrics").glob("agent-capability-*.md")]
            self.assertEqual(len(reports), 1)
            self.assertEqual(reports[0]["type"], "AgentCapabilityReport")
            self.assertEqual(reports[0]["failedCount"], 1)
            self.assertTrue(reports[0]["improvementRefs"])

    def test_actor_context_is_loaded_into_task_context_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "actor",
                        "context",
                        "--actor-id",
                        "agent.company.development",
                        "--type",
                        "agent",
                        "--name",
                        "研发 Agent",
                        "--default-project",
                        "agent-hub",
                        "--allow-project",
                        "agent-hub",
                        "--scope",
                        "engineering",
                        "--notify",
                        "feishu",
                        "--output-preference",
                        "中文、先结论后证据",
                    ]
                ),
                0,
            )
            create_project_task(bundle, "Implement feature", "agent-hub", "meimei", "agent.company.development", task_type="development", task_id="ACTOR-CTX-001")
            context_path = pull_project_task(bundle, "ACTOR-CTX-001")
            context_text = context_path.read_text(encoding="utf-8")
            payload = project_task_context_payload(bundle, "ACTOR-CTX-001")
            self.assertIn("## Actor Context", context_text)
            self.assertIn("agent.company.development", context_text)
            self.assertIn("中文、先结论后证据", context_text)
            self.assertIn("## Memory Policy", context_text)
            self.assertEqual(payload["projectContextBundle"]["actorContext"]["actorId"], "agent.company.development")
            self.assertEqual(payload["projectContextBundle"]["actorContext"]["currentProject"], "agent-hub")

    def test_actor_context_supports_non_ascii_actor_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            create_project_task(bundle, "Process material", "agent-hub", "meimei", "梅晓华", task_type="knowledge_capture", task_id="ACTOR-CN-001")
            context_path = pull_project_task(bundle, "ACTOR-CN-001")
            context_text = context_path.read_text(encoding="utf-8")
            payload = project_task_context_payload(bundle, "ACTOR-CN-001")
            actor_context = payload["projectContextBundle"]["actorContext"]
            self.assertIn("## Actor Context", context_text)
            self.assertIn("梅晓华", context_text)
            self.assertEqual(actor_context["actorId"], "梅晓华")
            self.assertTrue(actor_context["actorKey"].startswith("actor-"))
            self.assertEqual(actor_context["currentProject"], "agent-hub")
            self.assertFalse(validate_bundle(bundle))

    def test_actor_feedback_can_trigger_improvement_after_passed_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "prd", "--name", "PRD", "--owner", "meimei"]), 0)
            create_project_task(bundle, "Write PRD", "prd", "meimei", "agent.company.product-manager", task_type="product_requirement", task_id="PM-FEEDBACK-001")
            result_path = finish_project_task(
                bundle,
                "PM-FEEDBACK-001",
                "done",
                "需求已澄清，包含范围、用户场景、边界和验收标准。",
                evidence_refs=["projects/prd/evidence.md"],
                handoff_to="agent.company.design",
            )
            result = load_object(result_path)
            self.assertTrue(result["qualityEvaluation"]["passed"])
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "actor",
                            "feedback",
                            "--actor-id",
                            "meimei",
                            "--project",
                            "prd",
                            "--task",
                            "PM-FEEDBACK-001",
                            "--result-ref",
                            str(result_path),
                            "--target-agent",
                            "agent.company.product-manager",
                            "--rating",
                            "2",
                            "--type",
                            "negative",
                            "--content",
                            "这个 PRD 缺少关键边界条件，不能直接交给设计。",
                        ]
                    ),
                    0,
                )
            feedback_result = json.loads(stdout.getvalue())
            self.assertTrue(feedback_result["negative"])
            self.assertTrue(feedback_result["improvementRefs"])
            feedback = load_object(root / feedback_result["feedbackRef"])
            self.assertEqual(feedback["type"], "ActorFeedback")
            self.assertEqual(feedback["actorId"], "meimei")
            self.assertEqual(feedback["status"], "feedback_loop")
            result = load_object(result_path)
            self.assertTrue(result["improvementRefs"])
            proposal = load_object(root / result["improvementRefs"][0])
            self.assertEqual(proposal["trigger"], "actorFeedback")
            self.assertIn("这个 PRD 缺少关键边界条件，不能直接交给设计。", proposal["failureReasons"])
            actor_context = load_object(root / feedback["actorContextRef"])
            self.assertEqual(actor_context["type"], "ActorContext")

    def test_cli_acceptance_creates_next_role_task_after_human_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "cli-demo", "--name", "CLI Demo", "--owner", "meimei"]), 0)
            create_project_task(
                bundle,
                "Write PRD",
                "cli-demo",
                "meimei",
                "agent.company.product-manager",
                task_type="product_requirement",
                task_id="CLI-ACCEPT-001",
                expected_output=["Requirement brief and acceptance criteria."],
            )
            finish_project_task(
                bundle,
                "CLI-ACCEPT-001",
                "done",
                "需求已澄清，包含范围、用户场景、边界和验收标准。",
                output_refs=["projects/cli-demo/prd.md"],
                evidence_refs=["projects/cli-demo/evidence.md"],
                handoff_to="agent.company.design",
                next_suggested_task="Create design spec",
            )
            self.assertEqual(load_object(root / "projects/cli-demo/tasks/cli-accept-001.md")["status"], "waiting_acceptance")
            self.assertEqual(
                main([
                    "--root",
                    str(root),
                    "task",
                    "accept",
                    "CLI-ACCEPT-001",
                    "--decision",
                    "accepted",
                    "--reviewer",
                    "meimei",
                    "--reason",
                    "通过，进入设计",
                    "--human",
                ]),
                0,
            )
            result = load_object(root / "task-results/tr-cli-accept-001.md")
            self.assertEqual(result["acceptancePolicy"]["acceptanceStatus"], "accepted")
            self.assertTrue(result["followupTaskRefs"])
            followup = load_object(root / result["followupTaskRefs"][0])
            self.assertEqual(followup["assignee"], "agent.company.design")

    def test_rejected_acceptance_creates_retry_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "reject-demo", "--name", "Reject Demo", "--owner", "meimei"]), 0)
            create_project_task(
                bundle,
                "Write PRD",
                "reject-demo",
                "meimei",
                "agent.company.product-manager",
                task_type="product_requirement",
                task_id="CLI-REJECT-001",
                expected_output=["Requirement brief and acceptance criteria."],
            )
            finish_project_task(
                bundle,
                "CLI-REJECT-001",
                "done",
                "需求已澄清，包含范围、用户场景、边界和验收标准。",
                output_refs=["projects/reject-demo/prd.md"],
                evidence_refs=["projects/reject-demo/evidence.md"],
                handoff_to="agent.company.design",
            )
            outcome = accept_project_task_result(bundle, "CLI-REJECT-001", "changes_requested", "meimei", reason="验收标准不够可测", human=True)
            self.assertEqual(outcome["taskStatus"], "changes_requested")
            self.assertTrue(outcome["followupTaskRefs"])
            retry_task = load_object(root / outcome["followupTaskRefs"][0])
            self.assertEqual(retry_task["retryOf"], "CLI-REJECT-001")

    def test_feishu_acceptance_card_action_updates_task_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="cli_test",
                app_secret="secret",
                verification_token="",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=False,
                approval_code_project="",
                approval_code_common="",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "feishu-demo", "--name", "Feishu Demo", "--owner", "meimei"]), 0)
            create_project_task(
                bundle,
                "Write PRD",
                "feishu-demo",
                "meimei",
                "agent.company.product-manager",
                task_type="product_requirement",
                task_id="FS-ACCEPT-001",
                expected_output=["Requirement brief and acceptance criteria."],
            )
            finish_project_task(
                bundle,
                "FS-ACCEPT-001",
                "done",
                "需求已澄清，包含范围、用户场景、边界和验收标准。",
                output_refs=["projects/feishu-demo/prd.md"],
                evidence_refs=["projects/feishu-demo/evidence.md"],
                handoff_to="agent.company.design",
            )
            payload = {
                "event": {
                    "action": {
                        "value": {"action": "task_acceptance_accept", "taskId": "FS-ACCEPT-001", "human": "true"},
                        "form_value": {"reason": "通过"},
                    },
                    "operator": {"operator_id": {"open_id": "ou_reviewer"}},
                    "open_message_id": "om_test",
                }
            }
            response = feishu_module.handle_card_action_event(bundle, payload, settings)
            self.assertEqual(response["toast"]["type"], "success")
            result = load_object(root / "task-results/tr-fs-accept-001.md")
            self.assertEqual(result["acceptancePolicy"]["acceptanceStatus"], "accepted")
            self.assertTrue(result["followupTaskRefs"])

    def test_agent_discussion_session_creates_turns_decision_task_and_notifications(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "disc-demo", "--name", "Discussion Demo", "--owner", "meimei"]), 0)
            session = create_discussion_session(
                bundle,
                "需求实现方案讨论",
                "disc-demo",
                "meimei",
                "这个需求如何实现、如何验收、是否有风险。",
                ["agent.company.product-manager", "agent.company.development", "agent.company.test"],
                related_task_id="REQ-001",
            )
            session_path = root / session["discussionRef"]
            session_fm = load_object(session_path)
            self.assertEqual(session_fm["status"], "waiting_agent_turns")
            self.assertGreaterEqual(len(session_fm["notificationRefs"]), 4)
            pending_for_dev = list_notifications(bundle, status="pending", recipient="agent.company.development", message_type="discussion_turn_requested")
            self.assertEqual(len(pending_for_dev), 1)
            self.assertIn("请提交讨论观点", pending_for_dev[0]["messageSummary"])
            delivered = mark_notification_delivery(bundle, pending_for_dev[0]["notificationId"], "sent", "feishu-bot", delivery_ref="om_discussion_turn")
            self.assertEqual(delivered["status"], "sent")
            self.assertEqual(delivered["deliveryRef"], "om_discussion_turn")

            submit_discussion_turn(bundle, session["discussionId"], "agent.company.product-manager", "产品经理", "用户目标清楚，MVP 先做最短路径。", recommendations=["先做已有仓库接入"])
            submit_discussion_turn(bundle, session["discussionId"], "agent.company.development", "研发", "技术上可行，但需要验收门和通知链路。", concerns=["不能跳过人工验收"])
            turn = submit_discussion_turn(bundle, session["discussionId"], "agent.company.test", "测试", "需要覆盖讨论、决策、后续任务和通知。", recommendations=["加 API 和 CLI 测试"])
            self.assertEqual(turn["sessionStatus"], "pm_reviewing")

            result = finalize_discussion_session(
                bundle,
                session["discussionId"],
                "agent.company.project-manager",
                "三方同意先做回合制讨论，输出决策和后续任务。",
                "第一阶段做异步回合制，不做实时聊天室。",
                "先落地 DiscussionSession、DiscussionTurn、DiscussionSummary、Decision 和 follow-up task。",
                followup_task_title="实现 Agent 讨论第一阶段闭环",
                followup_assignee="agent.company.development",
            )
            self.assertEqual(result["status"], "next_task_created")
            self.assertTrue(result["decisionRefs"])
            self.assertTrue(result["followupTaskRefs"])
            final_session = load_object(session_path)
            notification_types = [load_object(root / ref)["messageType"] for ref in final_session["notificationRefs"]]
            self.assertIn("discussion_created", notification_types)
            self.assertIn("discussion_turn_requested", notification_types)
            self.assertIn("discussion_turn_submitted", notification_types)
            self.assertIn("discussion_ready_for_summary", notification_types)
            self.assertIn("discussion_summary_ready", notification_types)
            self.assertIn("discussion_completed", notification_types)
            completed = list_notifications(bundle, status="pending", message_type="discussion_completed", discussion_id=session["discussionId"])
            self.assertEqual(len(completed), 1)
            failed = mark_notification_delivery(bundle, completed[0]["notificationId"], "failed", "feishu-bot", failure_reason="test delivery failure")
            self.assertEqual(failed["failureReason"], "test delivery failure")
            self.assertIn("notification.delivered", audit_actions(root))
            self.assertIn("notification.failed", audit_actions(root))
            self.assertFalse(validate_bundle(bundle))

    def test_discussion_cli_and_feishu_entry_create_real_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "disc-cli", "--name", "Discussion CLI", "--owner", "meimei"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "discussion",
                        "create",
                        "--title",
                        "研发测试讨论",
                        "--project",
                        "disc-cli",
                        "--requester",
                        "meimei",
                        "--topic",
                        "研发和测试如何围绕验收标准达成一致。",
                        "--participant-agent",
                        "agent.company.development",
                        "--participant-agent",
                        "agent.company.test",
                    ]
                ),
                0,
            )
            sessions = [path for path in (root / "projects" / "disc-cli" / "discussions").glob("*.md") if load_object(path).get("type") == "DiscussionSession"]
            self.assertEqual(len(sessions), 1)
            self.assertEqual(load_object(sessions[0])["participantAgents"], ["agent.company.development", "agent.company.test"])
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                self.assertEqual(main(["--root", str(root), "notification", "list", "--status", "pending", "--recipient", "agent.company.development"]), 0)
            cli_notifications = json.loads(stdout.getvalue())["notifications"]
            self.assertEqual(len(cli_notifications), 1)
            self.assertEqual(cli_notifications[0]["messageType"], "discussion_turn_requested")
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "notification",
                        "mark",
                        "--notification-id",
                        cli_notifications[0]["notificationId"],
                        "--status",
                        "sent",
                        "--actor",
                        "cli-notifier",
                        "--delivery-ref",
                        "cli://notification",
                    ]
                ),
                0,
            )
            self.assertEqual(load_object(root / cli_notifications[0]["notificationRef"])["status"], "sent")

            settings = minimal_feishu_settings()
            payload = {
                "event": {
                    "action": {
                        "value": {"action": "discussion_create_submit"},
                        "form_value": {
                            "projectName": "disc-cli",
                            "title": "飞书讨论入口",
                            "topic": "从飞书发起 Agent 讨论会。",
                            "participants": "agent.company.product-manager, agent.company.development",
                        },
                    },
                    "operator": {"operator_id": {"open_id": "ou_requester"}},
                    "open_message_id": "om_discussion",
                }
            }
            response = feishu_module.handle_card_action_event(Bundle(root), payload, settings)
            self.assertEqual(response["toast"]["type"], "success")
            self.assertEqual(set(response.keys()), {"toast", "card"})
            response_card_json = json.dumps(response["card"]["data"], ensure_ascii=False)
            self.assertIn("这张卡片已锁定", response_card_json)
            self.assertNotIn('"tag": "form"', response_card_json)
            sessions_after = [path for path in (root / "projects" / "disc-cli" / "discussions").glob("*.md") if load_object(path).get("type") == "DiscussionSession"]
            self.assertEqual(len(sessions_after), 2)
            feishu_session = sorted(sessions_after)[-1]
            self.assertIn("ou_requester", str(load_object(feishu_session)["requester"]))

    def test_operations_feedback_routes_to_followup_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "ops", "--name", "Ops", "--owner", "meimei"]), 0)
            result = create_operations_feedback(
                bundle,
                "ops",
                "ou_ops",
                "用户反馈发布流程容易出错，需要沉淀运营经验。",
                feedback_type="知识经验",
                evidence_refs=["projects/ops/sources/feedback.md"],
                impact="high",
            )
            self.assertEqual(result["feedbackType"], "knowledge")
            feedback = load_object(root / result["feedbackRef"])
            self.assertEqual(feedback["status"], "feedback_loop")
            task = load_object(root / result["taskRef"])
            self.assertEqual(task["assignee"], "agent.company-knowledge-core.knowledge-engineering")
            self.assertIn(result["feedbackRef"], task["sourceMaterialRefs"])

    def test_task_state_machine_rejects_illegal_backward_transition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            create_project_task(bundle, "One shot", "", "meimei", "agent.company.project-manager", task_type="project_management", task_id="STATE-001")
            finish_project_task(bundle, "STATE-001", "done", "已完成并关闭。", evidence_refs=["tasks/state.md"])
            with self.assertRaisesRegex(KnowledgeError, "illegal task status transition"):
                set_project_task_status(bundle, "STATE-001", "processing", "meimei")

    def test_task_status_rejects_old_gate_and_result_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            create_project_task(bundle, "Layered status guard", "", "meimei", "agent.company.project-manager", task_type="project_management", task_id="STATE-OLD-001")
            for old_status in [
                "manual-runner-required",
                "assigned",
                "result_submitted",
                "waiting_human_acceptance",
                "retry_required",
                "approval_required",
                "clarification_required",
                "handoff_ready",
                "next_task_created",
            ]:
                with self.subTest(old_status=old_status):
                    with self.assertRaisesRegex(KnowledgeError, "unknown task routing status"):
                        set_project_task_status(bundle, "STATE-OLD-001", old_status, "meimei")

    def test_validate_allows_legacy_task_status_without_allowing_new_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            create_project_task(bundle, "Legacy status", "", "meimei", "agent.company.project-manager", task_type="project_management", task_id="STATE-LEGACY-001")
            task_path = root / "tasks" / "state-legacy-001.md"
            update_frontmatter_file(task_path, {"status": "manual-runner-required"})

            self.assertFalse(any("unknown task routing status" in problem for problem in validate_bundle(bundle)))
            with self.assertRaisesRegex(KnowledgeError, "unknown task routing status"):
                set_project_task_status(bundle, "STATE-LEGACY-001", "manual-runner-required", "meimei")

    def test_frontmatter_list_scalars_preserve_colon_and_uri_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "policy.md"
            path.write_text(
                core_module.render_doc(
                    {
                        "type": "Policy",
                        "title": "Policy",
                        "writePermissions": ["knowledge:draft", "toolAsset:draft"],
                        "requiredSecretRefs": ["secretref://stub/deepseek"],
                    },
                    "## Notes\n\nList scalar parsing should preserve colon-bearing values.\n",
                ),
                encoding="utf-8",
            )

            parsed = load_object(path)

            self.assertEqual(parsed["writePermissions"], ["knowledge:draft", "toolAsset:draft"])
            self.assertEqual(parsed["requiredSecretRefs"], ["secretref://stub/deepseek"])
            self.assertNotIn('{"secretref"', path.read_text(encoding="utf-8"))

    def test_permission_merge_accepts_legacy_single_key_permission_dicts(self) -> None:
        permissions = core_module.merged_agent_permissions(
            {"writePermissions": []},
            [{"writePermissions": [{"knowledge": "draft"}, {"toolAsset": "draft"}]}],
        )

        self.assertEqual(permissions["writePermissions"], ["knowledge:draft", "toolAsset:draft"])

    def test_task_diagnose_explains_bottleneck_and_next_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            create_project_task(
                bundle,
                "Diagnose pending work",
                "agent-hub",
                "meimei",
                "agent.company.development",
                task_type="engineering_action",
                task_id="DIAG-001",
                priority="high",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(main(["--root", str(root), "task", "diagnose", "DIAG-001"]), 0)
            pending = json.loads(stdout.getvalue())
            self.assertEqual(pending["bottleneck"], "waiting_for_execution")
            self.assertTrue(any("task pull DIAG-001" in item for item in pending["suggestedCommands"]))

            finish_project_task(
                bundle,
                "DIAG-001",
                "done",
                "已完成诊断测试。",
                evidence_refs=["projects/agent-hub/project.md"],
                tests_or_checks=["diagnose self-test"],
                handoff_summary="等待验收。",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(main(["--root", str(root), "task", "diagnose", "DIAG-001"]), 0)
            submitted = json.loads(stdout.getvalue())
            self.assertEqual(submitted["bottleneck"], "waiting_for_acceptance")
            self.assertTrue(any("task accept DIAG-001" in item for item in submitted["suggestedCommands"]))

    def test_unified_task_runtime_triages_engineering_without_knowledge_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            task_path = create_project_task(
                bundle,
                "修复飞书审批通知",
                "agent-hub",
                "meimei",
                "",
                task_type="engineering_action",
                task_id="RUNTIME-ENG-001",
            )
            task = load_object(task_path)
            self.assertEqual(task["type"], "ProjectTask")
            self.assertEqual(task["assignee"], "agent.company.development")
            self.assertEqual(task["taskRuntime"]["category"], "engineering")
            self.assertFalse(task["taskRuntime"]["requiresKnowledgeDraft"])
            result_path = finish_project_task(
                bundle,
                "RUNTIME-ENG-001",
                "done",
                "已修复审批通过后的通知闭环。",
                evidence_refs=["zhenzhi_knowledge/feishu.py"],
                tests_or_checks=["python3 -m unittest tests.test_cli.CliTests.test_unified_task_runtime_triages_engineering_without_knowledge_gate"],
            )
            result = load_object(result_path)
            self.assertTrue(result["qualityEvaluation"]["passed"])
            self.assertNotIn("missing KnowledgeItem draft", result["qualityEvaluation"]["reasons"])

    def test_unified_task_runtime_keeps_knowledge_capture_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            task_path = create_project_task(
                bundle,
                "沉淀飞书卡片经验",
                "company-knowledge-core",
                "meimei",
                "",
                task_type="knowledge_capture",
                task_id="RUNTIME-KNOW-001",
                source_material_refs=["sources/feishu-card.md"],
            )
            task = load_object(task_path)
            self.assertEqual(task["type"], "KnowledgeTask")
            self.assertEqual(task["assignee"], "agent.company-knowledge-core.knowledge-engineering")
            self.assertEqual(task["taskRuntime"]["category"], "knowledge")
            self.assertTrue(task["taskRuntime"]["requiresKnowledgeDraft"])
            result_path = finish_project_task(
                bundle,
                "RUNTIME-KNOW-001",
                "done",
                "已读取资料，但尚未生成结构化知识草稿。",
                evidence_refs=["sources/feishu-card.md"],
            )
            result = load_object(result_path)
            self.assertFalse(result["qualityEvaluation"]["passed"])
            self.assertIn("missing KnowledgeItem draft", result["qualityEvaluation"]["reasons"])

    def test_unified_task_runtime_triages_project_initialization_to_pm(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            task_path = create_project_task(
                bundle,
                "初始化灰度项目",
                "agent-hub",
                "meimei",
                "",
                task_type="project_initialization",
                task_id="RUNTIME-PROJ-001",
            )
            task = load_object(task_path)
            self.assertEqual(task["type"], "ProjectTask")
            self.assertEqual(task["assignee"], "agent.company.project-manager")
            self.assertEqual(task["taskRuntime"]["category"], "project")
            self.assertEqual(task["taskRuntime"]["acceptancePath"], "pm_review")
            result_path = finish_project_task(
                bundle,
                "RUNTIME-PROJ-001",
                "done",
                "项目初始化任务已完成，Runner 接管路径和首批任务已确认。",
                evidence_refs=["projects/agent-hub/launch.md"],
            )
            result = load_object(result_path)
            self.assertTrue(result["qualityEvaluation"]["passed"])
            self.assertEqual(result["acceptancePolicy"]["projectManager"], "agent.company.project-manager")

    def test_database_url_is_required_for_runtime_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            os.environ.pop("DATABASE_URL", None)
            self.assertEqual(main(["--root", str(root), "index", "rebuild"]), 2)

    def test_database_url_must_be_postgresql(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            os.environ["DATABASE_URL"] = "sqlite:///tmp/local.db"
            self.assertEqual(main(["--root", str(root), "index", "rebuild"]), 2)

    def test_operational_store_migration_status_and_rollback_guard(self) -> None:
        result = ensure_operational_schema("unit-test")
        self.assertTrue(result["ok"])
        storage = _FAKE_POSTGRES_DATABASES[self._test_database_url]
        for table in ["operational_events", "api_command_envelopes", "feishu_delivery_attempts", "migration_versions"]:
            self.assertIn(table, storage)
        status = operational_store_status()
        self.assertTrue(status["ok"])
        self.assertEqual(status["tables"]["migration_versions"], 1)
        with self.assertRaises(KnowledgeError):
            rollback_operational_schema("base")
        rolled_back = rollback_operational_schema("base", allow_destructive=True)
        self.assertTrue(rolled_back["ok"])
        self.assertNotIn("operational_events", storage)

    def test_live_readiness_reports_explicit_blockers_without_secret_leakage(self) -> None:
        previous = {
            name: os.environ.get(name)
            for name in [
                "FEISHU_APP_ID",
                "FEISHU_APP_SECRET",
                "FEISHU_VERIFICATION_TOKEN",
                "ZHENZHI_KNOWLEDGE_API_TOKEN",
                "FEISHU_CALLBACK_URL",
                "ZHENZHI_KNOWLEDGE_API_PORT",
                "ZHENZHI_KNOWLEDGE_BACKUP_REF",
                "ZHENZHI_KNOWLEDGE_PG_DUMP_REF",
                "FEISHU_REPLY_ENABLED",
            ]
        }
        try:
            for name in previous:
                os.environ.pop(name, None)
            os.environ["FEISHU_APP_SECRET"] = "app-secret-live"
            os.environ["FEISHU_VERIFICATION_TOKEN"] = "verification-token-live"
            os.environ["ZHENZHI_KNOWLEDGE_API_TOKEN"] = "api-token-live"
            os.environ["FEISHU_CALLBACK_URL"] = "https://gateway.example.com/integrations/feishu/events?token=callback-secret"
            report = live_readiness_report(check_feishu_api=False)
            text = json.dumps(report, ensure_ascii=False)
            self.assertEqual(report["status"], "blocked")
            labels = {item["name"]: item for item in report["readableLabels"]}
            for name in [
                "feishu_credentials",
                "feishu_callback_route",
                "feishu_message_delivery",
                "feishu_card_delivery",
                "api_gateway_routes",
                "postgres_operational_store",
                "migration",
                "rollback",
                "health",
                "metrics",
                "backup",
            ]:
                self.assertIn(name, labels)
            self.assertIn("missing FEISHU_APP_ID", report["blockers"])
            self.assertIn("Feishu tenant token API reachability", text)
            self.assertNotIn("app-secret-live", text)
            self.assertNotIn("verification-token-live", text)
            self.assertNotIn("api-token-live", text)
            self.assertNotIn("callback-secret", text)
            self.assertIn("https://gateway.example.com/integrations/feishu/events", text)
            self.assertFalse(backup_readiness()["ready"])
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    def test_readiness_redacts_secret_values_and_url_userinfo(self) -> None:
        previous = {name: os.environ.get(name) for name in ["FEISHU_APP_SECRET", "DATABASE_URL"]}
        try:
            os.environ["FEISHU_APP_SECRET"] = "raw-secret-value"
            os.environ["DATABASE_URL"] = "postgresql://user:db-password@db.example.com:5432/core?sslmode=require"
            self.assertEqual(redact_url(os.environ["DATABASE_URL"]), "postgresql://db.example.com:5432/core")
            error = compact_error(KnowledgeError(f"connect failed with raw-secret-value at {os.environ['DATABASE_URL']}"))
            self.assertNotIn("raw-secret-value", error)
            self.assertNotIn("db-password", error)
            self.assertIn("postgresql://db.example.com:5432/core", error)
            fragment_error = compact_error(KnowledgeError("password db-password rejected"))
            self.assertNotIn("db-password", fragment_error)
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    def test_feishu_wrong_token_writes_audit_and_operational_reject(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            payload = {
                "schema": "2.0",
                "header": {"event_type": "im.message.receive_v1", "token": "wrong-token"},
                "event": {
                    "message": {"message_id": "om_bad_token", "chat_id": "oc_test", "chat_type": "group", "content": json.dumps({"text": "hello"})},
                    "sender": {"sender_id": {"open_id": "ou_sender", "user_id": "u_sender"}},
                },
            }
            with self.assertRaises(KnowledgeError):
                feishu_module.handle_feishu_event(Bundle(root), payload, minimal_feishu_settings())
            self.assertIn("feishu.event.rejected", audit_actions(root))
            events = _FAKE_POSTGRES_DATABASES[self._test_database_url]["operational_events"]
            rejected = [row for row in events if row["status"] == "rejected" and row["targetRef"] == "om_bad_token"]
            self.assertEqual(len(rejected), 1)

    def test_feishu_permission_failure_writes_notification_and_delivery_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            payload = {
                "schema": "2.0",
                "header": {"event_type": "im.message.receive_v1", "token": "expected-token"},
                "event": {
                    "message": {"message_id": "om_scope_fail", "chat_id": "oc_test", "chat_type": "group", "content": json.dumps({"text": "查询 项目状态"})},
                    "sender": {"sender_id": {"open_id": "ou_sender", "user_id": "u_sender"}},
                },
            }
            original_build = feishu_module.build_feishu_response
            original_send = feishu_module.send_feishu_incoming_response

            def fake_build(_bundle, _incoming, _settings):
                return {"msg_type": "text", "reply": "readable reply"}

            def fake_send(_settings, _incoming, _response):
                raise urllib.error.HTTPError(
                    "https://open.feishu.cn/open-apis/im/v1/messages",
                    403,
                    "Forbidden",
                    {},
                    io.BytesIO(b'{"code":99991663,"msg":"permission denied: missing send message scope"}'),
                )

            feishu_module.build_feishu_response = fake_build
            feishu_module.send_feishu_incoming_response = fake_send
            try:
                result = feishu_module.handle_feishu_event(
                    Bundle(root),
                    payload,
                    minimal_feishu_settings(app_id="cli_a123456", app_secret="secret-ref", reply_enabled=True),
                )
            finally:
                feishu_module.build_feishu_response = original_build
                feishu_module.send_feishu_incoming_response = original_send
            self.assertTrue(result["replyError"])
            self.assertIn("feishu.permission.notification", audit_actions(root))
            notifications = list((root / "notifications").glob("notification*.md"))
            self.assertEqual(len(notifications), 1)
            text = notifications[0].read_text(encoding="utf-8")
            self.assertIn("飞书应用缺少发消息/发卡片权限", text)
            attempts = _FAKE_POSTGRES_DATABASES[self._test_database_url]["feishu_delivery_attempts"]
            self.assertTrue(any(row["messageId"] == "om_scope_fail" and row["finalStatus"] == "failed" and row["errorClass"] == "missing_send_scope" for row in attempts))

    def test_start_degrades_when_runtime_retrieval_database_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            os.environ.pop("DATABASE_URL", None)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "agent", "register", "--agent-id", "agent.alice.builder", "--name", "Alice", "--owner", "alice", "--purpose", "local work"]), 0)
            self.assertEqual(
                main(["--root", str(root), "start", "--project", "core", "--agent", "agent.alice.builder", "--task", "knowledge work", "--retrieval-limit", "1"]),
                0,
            )
            context = (root / ".zhenzhi" / "context" / "current.md").read_text(encoding="utf-8")
            self.assertIn("Retrieval skipped: DATABASE_URL is required and must point to PostgreSQL.", context)

    def test_runner_register_cli_creates_temporary_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "ou_owner"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "runner",
                        "register",
                        "--runner-id",
                        "runner.this-mac",
                        "--name",
                        "This Mac Local Codex",
                        "--host-type",
                        "mac",
                        "--mode",
                        "manual",
                        "--agent",
                        "agent.agent-hub.executor",
                        "--capability",
                        "codex",
                        "--capability",
                        "git",
                        "--capability",
                        "knowledge_sync",
                        "--project",
                        "agent-hub",
                        "--repo",
                        "https://github.com/meimei7959/company_knowledge_core.git",
                        "--data-scope",
                        "company",
                    ]
                ),
                0,
            )
            runner = (root / "runners" / "runner.this-mac.md").read_text(encoding="utf-8")
            self.assertIn("This Mac Local Codex", runner)
            self.assertIn("codex", runner)
            self.assertIn("agent-hub", runner)
            original_runner = load_object(root / "runners" / "runner.this-mac.md")
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "runner",
                        "register",
                        "--runner-id",
                        "runner.this-mac",
                        "--name",
                        "This Mac Local Codex Updated",
                        "--host-type",
                        "mac",
                        "--mode",
                        "manual",
                        "--agent",
                        "agent.agent-hub.executor",
                        "--capability",
                        "codex",
                        "--capability",
                        "claude",
                        "--project",
                        "agent-hub",
                        "--repo",
                        "https://github.com/meimei7959/company_knowledge_core.git",
                        "--data-scope",
                        "company",
                    ]
                ),
                0,
            )
            updated_runner = load_object(root / "runners" / "runner.this-mac.md")
            self.assertEqual(updated_runner["runnerId"], "runner.this-mac")
            self.assertEqual(updated_runner["timestamp"], original_runner["timestamp"])
            self.assertEqual(updated_runner["title"], "This Mac Local Codex Updated")
            self.assertIn("claude", updated_runner["capabilities"])
            self.assertEqual(
                main(["--root", str(root), "runner", "heartbeat", "--runner-id", "runner.this-mac", "--status", "busy", "--load", "1"]),
                0,
            )
            self.assertIn("status: busy", (root / "runners" / "runner.this-mac.md").read_text(encoding="utf-8"))
            actions = audit_actions(root)
            self.assertIn("runner.register", actions)
            self.assertIn("runner.upsert", actions)
            self.assertIn("runner.heartbeat", actions)

    def test_project_agent_register_preserves_projects_and_prevents_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "knowledge-core", "--name", "Knowledge Core", "--owner", "meimei"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "agent",
                        "register",
                        "--agent-id",
                        "agent.shared.project-manager",
                        "--name",
                        "Shared Project Manager Agent",
                        "--owner",
                        "meimei",
                        "--purpose",
                        "coordinate project state",
                        "--allow-project",
                        "agent-hub",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "agent",
                        "register",
                        "--agent-id",
                        "agent.shared.project-manager",
                        "--name",
                        "Shared Project Manager Agent Updated",
                        "--owner",
                        "meimei",
                        "--purpose",
                        "coordinate multiple projects",
                        "--allow-project",
                        "agent-hub",
                        "--allow-project",
                        "knowledge-core",
                    ]
                ),
                0,
            )
            agent = load_object(root / "agents" / "agent.shared.project-manager.md")
            self.assertEqual(agent["title"], "Shared Project Manager Agent Updated")
            self.assertEqual(agent["allowedProjects"].count("agent-hub"), 1)
            self.assertEqual(agent["allowedProjects"].count("knowledge-core"), 1)
            agent_hub = load_object(root / "projects" / "agent-hub" / "project.md")
            knowledge_core = load_object(root / "projects" / "knowledge-core" / "project.md")
            self.assertEqual(agent_hub["relatedAgents"].count("agent.shared.project-manager"), 1)
            self.assertEqual(knowledge_core["relatedAgents"].count("agent.shared.project-manager"), 1)
            self.assertEqual((root / "projects" / "agent-hub" / "agents.md").read_text(encoding="utf-8").count("../../agents/agent.shared.project-manager.md"), 1)
            self.assertIn("agent.attachProject", audit_actions(root))

    def test_task_lifecycle_writes_notification_records_and_failure_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "runner",
                        "register",
                        "--runner-id",
                        "runner.this-mac",
                        "--name",
                        "This Mac Local Codex",
                        "--capability",
                        "knowledge_capture",
                        "--project",
                        "agent-hub",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "create",
                        "--task-id",
                        "KT-NOTIFY-001",
                        "--title",
                        "沉淀会议纪要",
                        "--project",
                        "agent-hub",
                        "--requester",
                        "ou_requester",
                        "--assignee",
                        "runner.this-mac",
                        "--source",
                        "projects/agent-hub/sources/meeting.md",
                    ]
                ),
                0,
            )
            task_path = root / "projects" / "agent-hub" / "tasks" / "kt-notify-001.md"
            task = load_object(task_path)
            notifications = [load_object(root / ref) for ref in task["notificationRefs"]]
            self.assertEqual([item["messageType"] for item in notifications], ["task_created"])
            self.assertEqual(notifications[0]["recipient"], "ou_requester")
            self.assertEqual(notifications[0]["sourceMessageRef"], "projects/agent-hub/sources/meeting.md")

            set_project_task_status(bundle, "KT-NOTIFY-001", "waiting_runner", "system")
            task = load_object(task_path)
            notifications = [load_object(root / ref) for ref in task["notificationRefs"]]
            self.assertIn("task_waiting_runner", [item["messageType"] for item in notifications])

            claim = claim_project_task(bundle, "KT-NOTIFY-001", "runner.this-mac")
            task = load_object(task_path)
            notifications = [load_object(root / ref) for ref in task["notificationRefs"]]
            self.assertIn("task_claimed", [item["messageType"] for item in notifications])

            finish_project_task(bundle, "KT-NOTIFY-001", "done", "会议纪要已结构化。", runner_id="runner.this-mac", lease_token=claim["leaseToken"])
            task = load_object(task_path)
            notifications = [load_object(root / ref) for ref in task["notificationRefs"]]
            self.assertIn("task_finished", [item["messageType"] for item in notifications])
            self.assertTrue(task["resultRef"].startswith("task-results/"))
            result = load_object(root / task["resultRef"])
            self.assertEqual(result["qualityEvaluation"]["status"], "failed")
            self.assertEqual(result["qualityEvaluation"]["decision"], "retry_required")
            retry_task = load_object(root / "projects" / "agent-hub" / "tasks" / "kt-notify-001-retry.md")
            self.assertEqual(retry_task["taskType"], "knowledge_retry")
            self.assertEqual(retry_task["retryOf"], "KT-NOTIFY-001")
            self.assertEqual(retry_task["attemptNumber"], 2)

            create_task_notification(bundle, task_path, task, "task_finished", delivery_status="failed", failure_reason="feishu unavailable")
            failed_notification = load_object(root / load_object(task_path)["notificationRefs"][-1])
            self.assertEqual(failed_notification["status"], "failed")
            self.assertEqual(failed_notification["failureReason"], "feishu unavailable")
            self.assertEqual(failed_notification["retryCount"], 0)
            retrying = mark_notification_delivery(bundle, failed_notification["notificationId"], "retrying", "feishu-bot", failure_reason="retry scheduled")
            self.assertEqual(retrying["status"], "retrying")
            self.assertEqual(retrying["retryCount"], 1)
            dead_letter = mark_notification_delivery(bundle, failed_notification["notificationId"], "dead_letter", "feishu-bot", failure_reason="max retries exceeded")
            self.assertEqual(dead_letter["status"], "dead_letter")
            self.assertEqual(dead_letter["retryCount"], 1)
            self.assertTrue(dead_letter["deadLetterAt"])
            self.assertIn("task.notification.failed", audit_actions(root))
            self.assertIn("notification.retrying", audit_actions(root))
            self.assertIn("notification.dead_letter", audit_actions(root))

            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "create",
                        "--task-id",
                        "KT-NOTIFY-002",
                        "--title",
                        "处理阻塞任务",
                        "--project",
                        "agent-hub",
                        "--requester",
                        "ou_requester",
                        "--assignee",
                        "runner.this-mac",
                    ]
                ),
                0,
            )
            set_project_task_status(bundle, "KT-NOTIFY-002", "blocked", "runner.this-mac")
            blocked_task = load_object(root / "projects" / "agent-hub" / "tasks" / "kt-notify-002.md")
            blocked_notifications = [load_object(root / ref) for ref in blocked_task["notificationRefs"]]
            self.assertIn("task_blocked", [item["messageType"] for item in blocked_notifications])

    def test_knowledge_capture_pipeline_creates_evidence_backed_reviewable_draft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.grant_agent_write_policy(root, "agent.codex.local")
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            incoming = {
                "messageId": "om_material_unit",
                "chatId": "oc_material_unit",
                "chatType": "group",
                "text": "会议纪要：Agent Hub\n今天确认先做机器人资料入口，原始资料保存为 SourceMaterial。",
                "openId": "ou_alice",
                "userId": "alice",
                "mentionedOpenIds": "",
                "mentionedUserIds": "",
            }
            material = feishu_module.parse_project_material(incoming["text"])
            source_ref, task_ref, task_id, assignee = feishu_module.create_project_material_task(bundle, incoming, feishu_module.load_feishu_settings(), material)
            source = load_object(root / source_ref)
            self.assertEqual(source["type"], "SourceMaterial")
            self.assertEqual(source["sourceRef"], "feishu://message/om_material_unit")
            self.assertEqual(source["materialType"], "meeting")
            self.assertEqual(source["sourceType"], "meeting")
            self.assertEqual(source["extractionTool"], "feishu-bot-intake")
            self.assertEqual(source["extractionStatus"], "task_created")
            self.assertEqual(source["taskRef"], task_ref)
            self.assertTrue(source["contentHash"])
            self.assertIn("Original Text", (root / source_ref).read_text(encoding="utf-8"))
            task = load_object(root / task_ref)
            self.assertEqual(task["type"], "KnowledgeTask")
            self.assertEqual(task["sourceMaterialRefs"], [source_ref])
            self.assertIn("Create structured draft knowledge with source refs.", task["expectedOutput"])
            self.assertEqual(assignee, "梅晓华")

            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "runner",
                        "register",
                        "--runner-id",
                        "runner.material",
                        "--name",
                        "Material Runner",
                        "--capability",
                        "knowledge_capture",
                        "--project",
                        "agent-hub",
                    ]
                ),
                0,
            )
            claim = claim_project_task(bundle, task_id, "runner.material")
            result_path = finish_project_task(
                bundle,
                task_id,
                "done",
                "资料入口链路已结构化。",
                evidence_refs=[source_ref],
                runner_id="runner.material",
                lease_token=claim["leaseToken"],
                executor_agent="agent.codex.local",
                knowledge_draft={
                    "title": "Agent Hub source material handling",
                    "summary": "会议纪要和资料必须先成为 SourceMaterial，再由 Runner 生成草稿。",
                    "structured": "资料沉淀链路：保存原文 -> 创建 KnowledgeTask -> Runner 读取原文 -> 写 KnowledgeItem draft -> Review 后才能复用。",
                    "sourceRefs": [source_ref],
                    "confidence": "high",
                    "scope": "engineering",
                    "limits": ["不代表已验证标准，必须 Review。"],
                },
            )
            result = load_object(result_path)
            self.assertEqual(result["knowledgeRefs"][0].split("/")[0], "knowledge")
            self.assertEqual(result["qualityEvaluation"]["status"], "passed")
            self.assertEqual(result["qualityEvaluation"]["decision"], "review_required")
            review_task_ref = f"projects/agent-hub/tasks/{task_id.lower()}-review.md"
            self.assertEqual(result["followupTaskRefs"], [review_task_ref])
            draft_ref = result["knowledgeRefs"][0]
            draft = load_object(root / draft_ref)
            self.assertEqual(draft["type"], "KnowledgeItem")
            self.assertEqual(draft["status"], "draft")
            self.assertEqual(draft["confidence"], "high")
            self.assertEqual(draft["sourceRef"], source_ref)
            self.assertEqual(draft["originalSourcePath"], source_ref)
            self.assertEqual(draft["taskResultRef"], str(result_path.relative_to(root)))
            self.assertIn("Original Source", (root / draft_ref).read_text(encoding="utf-8"))
            review_paths = [item["path"] for item in list_review_queue(bundle)]
            self.assertIn(draft_ref, review_paths)
            review_task = load_object(root / review_task_ref)
            self.assertEqual(review_task["assignee"], "agent.core.knowledge-review")
            self.assertEqual(review_task["taskType"], "knowledge_review")
            self.assertEqual(review_task["parentTaskId"], task_id)
            self.assertIn("knowledge.draftFromTaskResult", audit_actions(root))

    def test_cli_material_ingest_to_task_finish_writes_knowledge_draft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.grant_agent_write_policy(root, "agent.company-knowledge-core.knowledge-engineering")
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "material",
                            "ingest",
                            "--title",
                            "Agent Hub intake note",
                            "--source-ref",
                            "manual://note/001",
                            "--project",
                            "agent-hub",
                            "--submitter",
                            "meimei",
                            "--material-type",
                            "repo-doc",
                            "--content",
                            "Agent Hub materials must be saved as SourceMaterial before reusable knowledge is drafted.",
                            "--create-task",
                            "--assignee",
                            "agent.company-knowledge-core.knowledge-engineering",
                        ]
                    ),
                    0,
                )
            ingest_result = json.loads(out.getvalue())
            task_ref = ingest_result["taskRef"]
            source_ref = ingest_result["sourceRef"]
            task = load_object(root / task_ref)
            task_id = task["taskId"]
            draft_path = root / "draft.json"
            draft_path.write_text(
                json.dumps(
                    {
                        "title": "Agent Hub source material intake rule",
                        "summary": "原始资料必须先注册为 SourceMaterial。",
                        "structured": "录入内容时，先保存 SourceMaterial，再生成 KnowledgeTask，最后由知识工程 Agent 基于证据写 KnowledgeItem draft。",
                        "sourceRefs": [source_ref],
                        "confidence": "high",
                        "scope": "engineering",
                        "limits": ["仅适用于可读取且无秘密信息的资料。"],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "task",
                            "finish",
                            task_id,
                            "--result",
                            "submitted",
                            "--summary",
                            "已从 SourceMaterial 抽取结构化草稿。",
                            "--evidence-ref",
                            source_ref,
                            "--executor-agent",
                            "agent.company-knowledge-core.knowledge-engineering",
                            "--knowledge-draft-file",
                            str(draft_path),
                        ]
                    ),
                    0,
                )
            result_path = Path(out.getvalue().strip())
            result = load_object(result_path)
            self.assertEqual(result["status"], "submitted")
            self.assertEqual(result["sourceMaterialRefs"], [source_ref])
            self.assertEqual(result["evidenceRefs"], [source_ref])
            self.assertEqual(len(result["knowledgeRefs"]), 1)
            draft = load_object(root / result["knowledgeRefs"][0])
            self.assertEqual(draft["type"], "KnowledgeItem")
            self.assertEqual(draft["status"], "draft")
            self.assertEqual(draft["owner"], "agent.company-knowledge-core.knowledge-engineering")
            self.assertEqual(draft["sourceRef"], source_ref)
            self.assertIn(result["knowledgeRefs"][0], [item["path"] for item in list_review_queue(bundle)])

    def test_blocked_knowledge_task_creates_repair_followup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "runner",
                        "register",
                        "--runner-id",
                        "runner.material",
                        "--name",
                        "Material Runner",
                        "--capability",
                        "knowledge_capture",
                        "--project",
                        "agent-hub",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "create",
                        "--task-id",
                        "KT-BLOCKED-MATERIAL",
                        "--title",
                        "读取不可解析资料",
                        "--project",
                        "agent-hub",
                        "--requester",
                        "ou_requester",
                        "--assignee",
                        "runner.material",
                        "--source",
                        "projects/agent-hub/sources/missing.md",
                    ]
                ),
                0,
            )
            claim = claim_project_task(bundle, "KT-BLOCKED-MATERIAL", "runner.material")
            result_path = finish_project_task(
                bundle,
                "KT-BLOCKED-MATERIAL",
                "blocked",
                "SourceMaterial path cannot be resolved.",
                runner_id="runner.material",
                lease_token=claim["leaseToken"],
                executor_agent="agent.company-knowledge-core.knowledge-engineering",
            )
            result = load_object(result_path)
            self.assertEqual(result["qualityEvaluation"]["status"], "blocked")
            self.assertEqual(result["qualityEvaluation"]["decision"], "repair_required")
            repair_task = load_object(root / "projects" / "agent-hub" / "tasks" / "kt-blocked-material-repair.md")
            self.assertEqual(repair_task["assignee"], "agent.core.knowledge-ops")
            self.assertEqual(repair_task["taskType"], "knowledge_repair")
            self.assertEqual(repair_task["parentTaskId"], "KT-BLOCKED-MATERIAL")
            self.assertIn(str(result_path.relative_to(root)), repair_task["sourceMaterialRefs"])

    def test_knowledge_review_pass_as_observed_publishes_indexes_and_notifies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle, review_task_id, draft_ref = self.create_reviewable_knowledge_fixture(root, "PASS")
            outcome = apply_knowledge_review_result(
                bundle,
                review_task_id,
                "pass_as_observed",
                "agent.core.knowledge-review",
                "低风险经验，证据完整，可以作为 observed 知识检索。",
            )
            self.assertEqual(outcome["outcome"], "pass_as_observed")
            self.assertEqual(outcome["publishedRefs"], [draft_ref])
            draft = load_object(root / draft_ref)
            self.assertEqual(draft["status"], "observed")
            review_task = load_object(root / f"projects/review-pass/tasks/{review_task_id}.md")
            self.assertEqual(review_task["status"], "done")
            self.assertTrue(review_task["reviewRecordRef"].startswith("knowledge/reviews/"))
            review_record = load_object(root / review_task["reviewRecordRef"])
            self.assertEqual(review_record["type"], "ReviewRecord")
            self.assertEqual(review_record["outcome"], "pass_as_observed")
            indexed = search_index(bundle, {"type": "KnowledgeItem", "status": "observed"})
            self.assertIn(draft_ref, [row["path"] for row in indexed])
            retrieved = search_retrieval(bundle, "Structured knowledge PASS")
            self.assertIn(draft_ref, [row["path"] for row in retrieved])
            self.assertIn("knowledge.publish", audit_actions(root))
            notifications = [load_object(root / ref) for ref in review_task["notificationRefs"]]
            self.assertIn("knowledge_indexed", [item["messageType"] for item in notifications])

    def test_knowledge_review_changes_requested_creates_retry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle, review_task_id, draft_ref = self.create_reviewable_knowledge_fixture(root, "CHANGE")
            outcome = apply_knowledge_review_result(
                bundle,
                review_task_id,
                "changes_requested",
                "agent.core.knowledge-review",
                "证据引用不够清晰，需要补充原文段落。",
            )
            self.assertEqual(outcome["outcome"], "changes_requested")
            self.assertEqual(len(outcome["followupTaskRefs"]), 1)
            retry_task = load_object(root / outcome["followupTaskRefs"][0])
            self.assertEqual(retry_task["taskType"], "knowledge_retry")
            self.assertEqual(retry_task["assignee"], "agent.company-knowledge-core.knowledge-engineering")
            self.assertIn(draft_ref, retry_task["sourceMaterialRefs"])
            review_task = load_object(root / f"projects/review-change/tasks/{review_task_id}.md")
            self.assertEqual(review_task["status"], "changes_requested")

    def test_knowledge_review_human_approval_clarification_conflict_and_reject_routes(self) -> None:
        cases = [
            ("APPROVAL", "needs_human_approval", "knowledge_approval", "waiting_acceptance"),
            ("CLARIFY", "needs_clarification", "knowledge_clarification", "changes_requested"),
            ("CONFLICT", "conflict_detected", "knowledge_conflict_resolution", "blocked"),
        ]
        for suffix, outcome_name, expected_task_type, expected_review_status in cases:
            with self.subTest(outcome=outcome_name):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    write_minimal_bundle(root)
                    bundle, review_task_id, _draft_ref = self.create_reviewable_knowledge_fixture(root, suffix)
                    outcome = apply_knowledge_review_result(
                        bundle,
                        review_task_id,
                        outcome_name,
                        "agent.core.knowledge-review",
                        f"Review outcome {outcome_name}.",
                    )
                    self.assertEqual(outcome["outcome"], outcome_name)
                    self.assertEqual(len(outcome["followupTaskRefs"]), 1)
                    followup = load_object(root / outcome["followupTaskRefs"][0])
                    self.assertEqual(followup["taskType"], expected_task_type)
                    review_task = load_object(root / f"projects/review-{suffix.lower()}/tasks/{review_task_id}.md")
                    self.assertEqual(review_task["status"], expected_review_status)
                    self.assertTrue(review_task["reviewRecordRef"].startswith("knowledge/reviews/"))
                    if outcome_name == "conflict_detected":
                        self.assertTrue(outcome["conflictRef"].startswith("knowledge/conflicts/"))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle, review_task_id, draft_ref = self.create_reviewable_knowledge_fixture(root, "REJECT")
            outcome = apply_knowledge_review_result(
                bundle,
                review_task_id,
                "reject",
                "agent.core.knowledge-review",
                "资料不适合沉淀为可复用知识。",
            )
            self.assertEqual(outcome["outcome"], "reject")
            self.assertEqual(load_object(root / draft_ref)["status"], "rejected")
            review_task = load_object(root / f"projects/review-reject/tasks/{review_task_id}.md")
            self.assertEqual(review_task["status"], "rejected")

    def test_knowledge_approval_approved_publishes_indexes_and_closes_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle, review_task_id, draft_ref = self.create_reviewable_knowledge_fixture(root, "APPROVE")
            review_outcome = apply_knowledge_review_result(
                bundle,
                review_task_id,
                "needs_human_approval",
                "agent.core.knowledge-review",
                "高影响知识，需要 human owner 审批后发布为 verified。",
            )
            approval_ref = review_outcome["followupTaskRefs"][0]
            approval_task = load_object(root / approval_ref)
            self.assertEqual(approval_task["taskType"], "knowledge_approval")
            self.assertEqual(approval_task["targetKnowledgeRefs"], [draft_ref])
            approval_outcome = apply_knowledge_approval_result(
                bundle,
                approval_task["taskId"],
                "approved",
                "meimei",
                "确认结论、范围和风险，可以发布。",
            )
            self.assertEqual(approval_outcome["outcome"], "approved")
            self.assertEqual(approval_outcome["publishedRefs"], [draft_ref])
            self.assertEqual(load_object(root / draft_ref)["status"], "verified")
            approval_task_after = load_object(root / approval_ref)
            self.assertEqual(approval_task_after["status"], "done")
            self.assertTrue(approval_task_after["approvalRecordRef"].startswith("knowledge/reviews/"))
            review_task_after = load_object(root / f"projects/review-approve/tasks/{review_task_id}.md")
            self.assertEqual(review_task_after["status"], "done")
            self.assertEqual(review_task_after["publishedRefs"], [draft_ref])
            indexed = search_index(bundle, {"type": "KnowledgeItem", "status": "verified"})
            self.assertIn(draft_ref, [row["path"] for row in indexed])
            retrieved = search_retrieval(bundle, "Structured knowledge APPROVE")
            self.assertIn(draft_ref, [row["path"] for row in retrieved])
            self.assertIn("knowledge.publish", audit_actions(root))
            notifications = [load_object(root / ref) for ref in approval_task_after["notificationRefs"]]
            self.assertIn("knowledge_published", [item["messageType"] for item in notifications])

    def test_publish_rebuild_cli_and_http_publish_indexes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            item_dir = root / "knowledge" / "engineering"
            item_dir.mkdir(parents=True, exist_ok=True)
            (item_dir / "auto-publish.md").write_text(
                """---
type: KnowledgeItem
title: Auto publish searchable knowledge
description: Knowledge publish endpoint should rebuild retrieval automatically.
timestamp: "2026-01-01T00:00:00Z"
owner: agent.core.knowledge-engineering
status: verified
scope: engineering
sourceRef: sources/auto-publish.md
confidence: high
sensitivity: internal
---

## Lesson

自动发布链路会重建对象索引和 RAG 索引，让机器人立刻查到这条知识。
""",
                encoding="utf-8",
            )
            publish_result = publish_knowledge_bundle(bundle, actor="test.publisher", reason="unit test")
            self.assertEqual(publish_result["kind"], "KnowledgePublishResult")
            self.assertGreaterEqual(publish_result["objectCount"], 1)
            self.assertGreaterEqual(publish_result["chunkCount"], 1)
            self.assertIn("knowledge.publish", audit_actions(root))
            self.assertIn("knowledge/engineering/auto-publish.md", [row["path"] for row in search_retrieval(bundle, "自动发布链路 RAG 索引")])

            try:
                server = KnowledgeHTTPServer(("127.0.0.1", 0), bundle, api_token="test-token")
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                request = urllib.request.Request(
                    f"http://127.0.0.1:{server.server_port}/v0/publish/rebuild",
                    data=json.dumps({"actor": "test.http", "reason": "http publish"}).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"},
                    method="POST",
                )
                http_result = json.load(urllib.request.urlopen(request))
                self.assertEqual(http_result["kind"], "KnowledgePublishResult")
                self.assertGreaterEqual(http_result["chunkCount"], 1)
                self.assertIn("knowledge.publish", audit_actions(root))
            finally:
                server.shutdown()
                server.server_close()

    def test_knowledge_approval_rejected_creates_retry_and_notifies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle, review_task_id, draft_ref = self.create_reviewable_knowledge_fixture(root, "APPROVALREJECT")
            review_outcome = apply_knowledge_review_result(
                bundle,
                review_task_id,
                "needs_human_approval",
                "agent.core.knowledge-review",
                "高影响知识，需要 human owner 审批。",
            )
            approval_ref = review_outcome["followupTaskRefs"][0]
            approval_task = load_object(root / approval_ref)
            approval_outcome = apply_knowledge_approval_result(
                bundle,
                approval_task["taskId"],
                "rejected",
                "meimei",
                "审批人认为证据不足，需要补充原文和适用范围。",
            )
            self.assertEqual(approval_outcome["outcome"], "rejected")
            self.assertEqual(load_object(root / draft_ref)["status"], "rejected")
            self.assertEqual(len(approval_outcome["followupTaskRefs"]), 1)
            retry_task = load_object(root / approval_outcome["followupTaskRefs"][0])
            self.assertEqual(retry_task["taskType"], "knowledge_retry")
            self.assertEqual(retry_task["assignee"], "agent.company-knowledge-core.knowledge-engineering")
            approval_task_after = load_object(root / approval_ref)
            self.assertEqual(approval_task_after["status"], "rejected")
            self.assertTrue(approval_task_after["approvalRecordRef"].startswith("knowledge/reviews/"))
            review_task_after = load_object(root / f"projects/review-approvalreject/tasks/{review_task_id}.md")
            self.assertEqual(review_task_after["status"], "changes_requested")
            self.assertIn(approval_outcome["followupTaskRefs"][0], review_task_after["followupTaskRefs"])
            notifications = [load_object(root / ref) for ref in approval_task_after["notificationRefs"]]
            self.assertIn("knowledge_approval_rejected_notice", [item["messageType"] for item in notifications])

    def test_knowledge_ops_repair_completion_creates_retry_or_clarification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "ops-loop", "--name", "Ops Loop", "--owner", "meimei"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "create",
                        "--task-id",
                        "KT-OPS-SOURCE",
                        "--title",
                        "Extract blocked source",
                        "--project",
                        "ops-loop",
                        "--requester",
                        "ou_submitter",
                        "--assignee",
                        "runner.material",
                        "--source",
                        "projects/ops-loop/sources/missing.md",
                    ]
                ),
                0,
            )
            blocked_result = finish_project_task(bundle, "KT-OPS-SOURCE", "blocked", "Source missing.")
            blocked_task = load_object(root / "projects/ops-loop/tasks/kt-ops-source.md")
            repair_ref = blocked_task["followupTaskRefs"][0]
            repair_task = load_object(root / repair_ref)
            self.assertEqual(repair_task["taskType"], "knowledge_repair")
            repair_result = finish_project_task(bundle, repair_task["taskId"], "done", "Recovered source mapping.", evidence_refs=[str(blocked_result.relative_to(root))])
            repair_result_fm = load_object(repair_result)
            retry_task = load_object(root / repair_result_fm["followupTaskRefs"][0])
            self.assertEqual(retry_task["taskType"], "knowledge_retry")
            self.assertEqual(retry_task["parentTaskId"], "KT-OPS-SOURCE")
            self.assertEqual(retry_task["repairTaskId"], repair_task["taskId"])
            self.assertIn(str(repair_result.relative_to(root)), retry_task["sourceMaterialRefs"])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "ops-blocked", "--name", "Ops Blocked", "--owner", "meimei"]), 0)
            repair_path = create_project_task(
                bundle,
                "Repair unresolved handoff",
                "ops-blocked",
                "ou_submitter",
                "agent.core.knowledge-ops",
                "knowledge_repair",
                "KT-OPS-REPAIR",
                source_material_refs=["projects/ops-blocked/sources/missing.md"],
            )
            update_frontmatter_file(repair_path, {"originTaskId": "KT-ORIGIN", "parentTaskId": "KT-ORIGIN"})
            repair_result = finish_project_task(bundle, "KT-OPS-REPAIR", "blocked", "Still missing source permission.")
            clarification = load_object(root / load_object(repair_result)["followupTaskRefs"][0])
            self.assertEqual(clarification["taskType"], "knowledge_clarification")
            self.assertEqual(clarification["assignee"], "ou_submitter")
            self.assertEqual(clarification["repairTaskId"], "KT-OPS-REPAIR")

    def test_knowledge_steward_conflict_completion_resolves_and_returns_to_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle, review_task_id, draft_ref = self.create_reviewable_knowledge_fixture(root, "STEWARD")
            outcome = apply_knowledge_review_result(
                bundle,
                review_task_id,
                "conflict_detected",
                "agent.core.knowledge-review",
                "Candidate overlaps with existing operating rule.",
            )
            conflict_ref = outcome["conflictRef"]
            conflict_task = load_object(root / outcome["followupTaskRefs"][0])
            self.assertEqual(conflict_task["taskType"], "knowledge_conflict_resolution")
            conflict_result = finish_project_task(
                bundle,
                conflict_task["taskId"],
                "done",
                "Steward resolved scope: keep candidate as project-specific observed note.",
                evidence_refs=[draft_ref],
            )
            self.assertEqual(load_object(root / conflict_ref)["status"], "resolved")
            conflict_result_fm = load_object(conflict_result)
            rereview_task = load_object(root / conflict_result_fm["followupTaskRefs"][0])
            self.assertEqual(rereview_task["taskType"], "knowledge_review")
            self.assertEqual(rereview_task["assignee"], "agent.core.knowledge-review")
            self.assertEqual(rereview_task["conflictResolutionTaskId"], conflict_task["taskId"])
            self.assertIn(conflict_ref, rereview_task["resolvedConflictRefs"])
            self.assertIn(draft_ref, rereview_task["sourceMaterialRefs"])

    def test_feishu_project_status_card_resolves_project_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "agent",
                        "register",
                        "--agent-id",
                        "agent.agent-hub.project-manager",
                        "--name",
                        "Agent Hub 项目经理 Agent",
                        "--owner",
                        "meimei",
                        "--purpose",
                        "项目状态协调",
                        "--allow-project",
                        "agent-hub",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "runner",
                        "register",
                        "--runner-id",
                        "runner.this-mac",
                        "--name",
                        "This Mac Local Codex",
                        "--capability",
                        "codex",
                        "--capability",
                        "project_initialization",
                        "--project",
                        "agent-hub",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "create",
                        "--task-id",
                        "project-init-agent-hub",
                        "--title",
                        "Agent Hub 项目初始化",
                        "--project",
                        "agent-hub",
                        "--requester",
                        "meimei",
                        "--assignee",
                        "agent.agent-hub.project-manager",
                        "--type",
                        "project_initialization",
                    ]
                ),
                0,
            )
            summary = feishu_module.project_status_summary(Bundle(root), "Agent Hub")
            self.assertEqual(summary["projectId"], "agent-hub")
            self.assertEqual(summary["title"], "Agent Hub")
            self.assertEqual(summary["agents"][0]["agentId"], "agent.agent-hub.project-manager")
            self.assertEqual(summary["runners"][0]["runnerId"], "runner.this-mac")
            self.assertEqual(summary["tasks"][0]["taskId"], "project-init-agent-hub")
            self.assertEqual(summary["health"], "on_track")
            self.assertEqual(summary["progress"]["total"], 1)
            self.assertEqual(summary["progress"]["active"], 1)

            response = feishu_module.build_feishu_response(
                Bundle(root),
                {
                    "messageId": "om_project_status",
                    "chatId": "oc_project_status",
                    "chatType": "p2p",
                    "text": "查项目状态：Agent Hub",
                    "openId": "ou_meimei",
                    "userId": "meimei",
                    "mentionedOpenIds": "",
                    "mentionedUserIds": "",
                },
                feishu_module.load_feishu_settings(),
            )
            self.assertEqual(response["msg_type"], "interactive")
            self.assertIn("项目状态：Agent Hub", response["card"]["header"]["title"]["content"])
            self.assertIn("Agent Hub 项目初始化", response["reply"])
            self.assertIn("当前状态：草稿；健康度：正常推进", response["reply"])
            self.assertIn("任务进度：共 1 个，已完成 0 个，未完成 1 个，阻塞 0 个", response["reply"])
            self.assertIn("负责人：meimei", response["reply"])

    def test_feishu_project_status_local_router_handles_synonyms(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            variants = [
                "查项目状态：Agent Hub",
                "查看项目状态：Agent Hub",
                "查询项目进度 Agent Hub",
                "Agent Hub 项目情况怎么样？",
                "Agent Hub 的项目详情",
            ]
            for index, text in enumerate(variants):
                with self.subTest(text=text):
                    response = feishu_module.build_feishu_response(
                        Bundle(root),
                        {
                            "messageId": f"om_project_status_variant_{index}",
                            "chatId": "oc_project_status",
                            "chatType": "p2p",
                            "text": text,
                            "openId": "ou_meimei",
                            "userId": "meimei",
                            "mentionedOpenIds": "",
                            "mentionedUserIds": "",
                        },
                        feishu_module.load_feishu_settings(),
                    )
                    self.assertEqual(response["msg_type"], "interactive")
                    self.assertIn("项目状态：Agent Hub", response["card"]["header"]["title"]["content"])
                    self.assertIn("当前状态：草稿", response["reply"])
            audit_text = "\n".join(path.read_text(encoding="utf-8") for path in (root / "knowledge" / "audit").glob("*.md"))
            self.assertIn("feishu.local_router.decision", audit_text)
            self.assertIn("local_project_status_pattern", audit_text)

    def test_feishu_project_status_card_missing_project_is_readable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            response = feishu_module.build_feishu_response(
                Bundle(root),
                {
                    "messageId": "om_missing_project",
                    "chatId": "oc_missing_project",
                    "chatType": "p2p",
                    "text": "查项目：不存在的项目",
                    "openId": "ou_meimei",
                    "userId": "meimei",
                    "mentionedOpenIds": "",
                    "mentionedUserIds": "",
                },
                feishu_module.load_feishu_settings(),
            )
            self.assertEqual(response["msg_type"], "interactive")
            self.assertIn("没找到项目", response["reply"])

    def test_feishu_incoming_response_uses_visible_direct_message_before_reply(self) -> None:
        settings = minimal_feishu_settings()
        calls: list[tuple[str, str, str]] = []
        original_direct = feishu_module.send_feishu_direct_response
        original_reply = feishu_module.send_feishu_response
        try:
            feishu_module.send_feishu_direct_response = lambda _settings, receive_id, _response, receive_id_type="open_id": calls.append(("direct", receive_id_type, receive_id)) is None or True
            feishu_module.send_feishu_response = lambda _settings, message_id, _response: calls.append(("reply", "message_id", message_id)) is None or True
            self.assertTrue(
                feishu_module.send_feishu_incoming_response(
                    settings,
                    {"messageId": "om_visible", "chatType": "p2p", "openId": "ou_meimei", "chatId": "oc_chat"},
                    {"msg_type": "text", "reply": "ok"},
                )
            )
            self.assertEqual(calls, [("direct", "open_id", "ou_meimei")])
            calls.clear()
            self.assertTrue(
                feishu_module.send_feishu_incoming_response(
                    settings,
                    {"messageId": "om_group", "chatType": "group", "openId": "ou_meimei", "chatId": "oc_group"},
                    {"msg_type": "text", "reply": "ok"},
                )
            )
            self.assertEqual(calls, [("direct", "chat_id", "oc_group")])
        finally:
            feishu_module.send_feishu_direct_response = original_direct
            feishu_module.send_feishu_response = original_reply

    def test_feishu_project_status_card_ambiguous_project_asks_for_clarification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "alpha-core", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "beta-core", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            response = feishu_module.build_feishu_response(
                Bundle(root),
                {
                    "messageId": "om_ambiguous_project",
                    "chatId": "oc_ambiguous_project",
                    "chatType": "p2p",
                    "text": "项目状态：Agent Hub",
                    "openId": "ou_meimei",
                    "userId": "meimei",
                    "mentionedOpenIds": "",
                    "mentionedUserIds": "",
                },
                feishu_module.load_feishu_settings(),
            )
            self.assertEqual(response["msg_type"], "interactive")
            self.assertIn("找到多个项目", response["reply"])
            self.assertIn("Agent Hub", response["reply"])

    def test_feishu_project_status_no_runner_has_next_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "create",
                        "--task-id",
                        "project-init-agent-hub",
                        "--title",
                        "Agent Hub 项目初始化",
                        "--project",
                        "agent-hub",
                        "--requester",
                        "meimei",
                        "--assignee",
                        "agent.agent-hub.project-manager",
                        "--type",
                        "project_initialization",
                    ]
                ),
                0,
            )
            set_project_task_status(Bundle(root), "project-init-agent-hub", "waiting_runner", "test")
            summary = feishu_module.project_status_summary(Bundle(root), "Agent Hub")
            self.assertEqual(summary["runners"], [])
            self.assertEqual(summary["health"], "needs_decision")
            self.assertEqual(summary["progress"]["blocked"], 1)
            self.assertIn("项目初始化等待执行电脑接管", summary["risks"][0]["risk"])
            self.assertIn("项目经理 Agent 人工接管", summary["decisionsNeeded"][0])
            self.assertIn("登记或绑定可用 Agent 工作台执行电脑。", summary["nextActions"])
            reply = feishu_module.build_reply(
                Bundle(root),
                {
                    "messageId": "om_project_status_text_fallback",
                    "chatId": "oc_project_status_text_fallback",
                    "chatType": "p2p",
                    "text": "查项目：Agent Hub",
                    "openId": "ou_meimei",
                    "userId": "meimei",
                    "mentionedOpenIds": "",
                    "mentionedUserIds": "",
                },
                feishu_module.load_feishu_settings(),
            )
            self.assertIn("**执行电脑 / Runner**", reply)
            self.assertIn("暂未绑定可用执行电脑", reply)
            self.assertIn("等待人工接管", reply)
            self.assertIn("当前状态：草稿；健康度：需要决策", reply)
            self.assertIn("任务进度：共 1 个，已完成 0 个，未完成 1 个，阻塞 1 个", reply)
            self.assertIn("**风险 / 阻塞**", reply)
            self.assertIn("**待决策**", reply)
            self.assertIn("内部记录位置：projects/agent-hub/project.md", reply)
            self.assertIn("项目经理 Agent 人工接管", reply)
            self.assertIn("Agent 工作台执行电脑", reply)
            self.assertNotIn("状态：draft", reply)
            self.assertNotIn("needs_decision", reply)
            self.assertNotIn("waiting_runner", reply)
            self.assertNotIn("TaskResult", reply)
            self.assertNotIn("AgentRun", reply)
            self.assertNotIn("Owner:", reply)

    def test_feishu_project_status_masks_or_resolves_owner_open_id(self) -> None:
        previous = os.environ.get("FEISHU_USER_OPEN_ID_MAP_JSON")
        os.environ["FEISHU_USER_OPEN_ID_MAP_JSON"] = json.dumps({"梅晓华": "ou_1234567890abcdef"}, ensure_ascii=False)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_minimal_bundle(root)
                self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "ou_1234567890abcdef"]), 0)
                reply = feishu_module.render_project_status_text(feishu_module.project_status_summary(Bundle(root), "Agent Hub"))
                self.assertIn("负责人：梅晓华", reply)
                self.assertNotIn("ou_1234567890abcdef", reply)
        finally:
            if previous is None:
                os.environ.pop("FEISHU_USER_OPEN_ID_MAP_JSON", None)
            else:
                os.environ["FEISHU_USER_OPEN_ID_MAP_JSON"] = previous

    def test_feishu_project_status_reconciles_approval_before_rendering(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "ou_owner"]), 0)
            save_approval_request(
                bundle,
                "approval_project_reconcile",
                {
                    "instanceCode": "approval_project_reconcile",
                    "approvalCode": "approval_project",
                    "approvalType": "project_init",
                    "targetRef": "projects/agent-hub/project.md",
                    "requestedStatus": "verified",
                    "projectId": "agent-hub",
                    "projectName": "Agent Hub",
                    "ownerOpenId": "ou_owner",
                    "ownerName": "梅晓华",
                    "submitterOpenId": "ou_submitter",
                },
            )
            settings = feishu_module.FeishuSettings(
                app_id="cli_app",
                app_secret="cli_secret",
                verification_token="",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            original_detail = feishu_module.feishu_approval_instance_detail
            original_direct = feishu_module.send_feishu_direct_response
            sent_cards: list[tuple[str, dict[str, object]]] = []
            feishu_module.feishu_approval_instance_detail = lambda _settings, _instance_code: {"status": "APPROVED"}
            feishu_module.send_feishu_direct_response = lambda _settings, open_id, response: sent_cards.append((open_id, response)) or True
            try:
                approvals = feishu_module.project_approval_summaries(bundle, "agent-hub", "Agent Hub", settings)
            finally:
                feishu_module.feishu_approval_instance_detail = original_detail
                feishu_module.send_feishu_direct_response = original_direct
            self.assertEqual(approvals[0]["status"], "verified")
            self.assertEqual(sent_cards[0][0], "ou_submitter")
            self.assertEqual(sent_cards[0][1]["msg_type"], "interactive")
            self.assertIn("项目立项审批已通过", json.dumps(sent_cards[0][1]["card"], ensure_ascii=False))
            self.assertEqual(sent_cards[1][0], "ou_owner")
            approval_audits = "\n".join((root / "knowledge" / "audit" / path.name).read_text(encoding="utf-8") for path in (root / "knowledge" / "audit").glob("*.md"))
            self.assertIn("action: feishu.approval.notify_sent", approval_audits)
            self.assertIn("recipientRole: submitter", approval_audits)
            self.assertIn("recipientRole: project_owner", approval_audits)
            reply = feishu_module.render_project_status_text(feishu_module.project_status_summary(bundle, "Agent Hub"))
            self.assertIn("项目立项审批：已通过", reply)
            project = load_object(root / "projects" / "agent-hub" / "project.md")
            self.assertEqual(project["status"], "verified")
            self.assertEqual(project["humanOwner"], "梅晓华")

    def test_project_approval_sends_owner_onboarding_even_when_submitter_is_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "ou_same"]), 0)
            save_approval_request(
                bundle,
                "approval_same_owner",
                {
                    "instanceCode": "approval_same_owner",
                    "approvalCode": "approval_project",
                    "approvalType": "project_init",
                    "targetRef": "projects/agent-hub/project.md",
                    "requestedStatus": "verified",
                    "projectId": "agent-hub",
                    "projectName": "Agent Hub",
                    "ownerOpenId": "ou_same",
                    "ownerName": "梅晓华",
                    "submitterOpenId": "ou_same",
                    "submitterName": "梅晓华",
                },
            )
            settings = minimal_feishu_settings(app_id="cli_app", app_secret="cli_secret", approval_enabled=True)
            original_detail = feishu_module.feishu_approval_instance_detail
            original_direct = feishu_module.send_feishu_direct_response
            sent_cards: list[tuple[str, dict[str, object]]] = []
            feishu_module.feishu_approval_instance_detail = lambda _settings, _instance_code: {"status": "APPROVED"}
            feishu_module.send_feishu_direct_response = lambda _settings, open_id, response: sent_cards.append((open_id, response)) or True
            try:
                feishu_module.project_approval_summaries(bundle, "agent-hub", "Agent Hub", settings)
            finally:
                feishu_module.feishu_approval_instance_detail = original_detail
                feishu_module.send_feishu_direct_response = original_direct
            self.assertEqual([item[0] for item in sent_cards], ["ou_same", "ou_same"])
            sent_text = json.dumps([item[1]["card"] for item in sent_cards], ensure_ascii=False)
            self.assertIn("项目立项审批已通过", sent_text)
            self.assertIn("你负责的项目已立项", sent_text)
            self.assertIn("状态：已立项", sent_text)
            self.assertNotIn("状态：verified", sent_text)

    def test_project_approval_sends_manual_runner_handoff_after_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            create_project_launch(
                bundle,
                "Agent Hub",
                "ou_owner",
                "建设公司 Agent Hub",
                repo_url="https://github.com/company/agent-hub.git",
                requester="ou_submitter",
                ring_enabled=False,
            )
            request = {
                "instanceCode": "approval_agent_hub_12345678",
                "approvalCode": "approval_project",
                "approvalType": "project_init",
                "targetRef": "projects/agent-hub/project.md",
                "requestedStatus": "verified",
                "projectId": "agent-hub",
                "projectName": "Agent Hub",
                "ownerOpenId": "ou_owner",
                "ownerName": "梅晓华",
                "submitterOpenId": "ou_submitter",
                "submitterName": "提交人",
            }
            settings = minimal_feishu_settings(app_id="cli_app", app_secret="cli_secret", approval_enabled=True)
            original_direct = feishu_module.send_feishu_direct_response
            sent_cards: list[tuple[str, dict[str, object]]] = []
            feishu_module.send_feishu_direct_response = lambda _settings, open_id, response: sent_cards.append((open_id, response)) or True
            try:
                feishu_module.notify_approval_result(bundle, settings, request, True, "approval_agent_hub_12345678", "verified")
            finally:
                feishu_module.send_feishu_direct_response = original_direct
            self.assertEqual([item[0] for item in sent_cards], ["ou_submitter", "ou_owner", "ou_owner"])
            sent_text = json.dumps([item[1]["card"] for item in sent_cards], ensure_ascii=False)
            self.assertIn("项目立项审批已通过", sent_text)
            self.assertIn("你负责的项目已立项", sent_text)
            self.assertIn("项目初始化需要本地接管", sent_text)
            self.assertIn("等待本地接管", sent_text)
            self.assertNotIn("状态：verified", sent_text)
            self.assertNotIn("waiting_runner", sent_text)
            self.assertNotIn("任务卡", sent_text)

    def test_project_manager_health_check_creates_review_followup_notifications_and_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "create",
                        "--task-id",
                        "project-init-agent-hub",
                        "--title",
                        "Agent Hub 项目初始化",
                        "--project",
                        "agent-hub",
                        "--requester",
                        "meimei",
                        "--assignee",
                        "agent.agent-hub.project-manager",
                        "--type",
                        "project_initialization",
                    ]
                ),
                0,
            )
            set_project_task_status(Bundle(root), "project-init-agent-hub", "waiting_runner", "test")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "project",
                            "health",
                            "--project",
                            "agent-hub",
                            "--actor",
                            "agent.agent-hub.project-manager",
                            "--create-followup",
                        ]
                    ),
                    0,
                )
            result = json.loads(stdout.getvalue())
            self.assertEqual(result["kind"], "ProjectManagerReview")
            self.assertEqual(result["projectManagerAgent"], "agent.agent-hub.project-manager")
            self.assertIn(result["health"], {"at_risk", "blocked", "needs_decision"})
            self.assertTrue(result["risks"])
            self.assertTrue(result["decisionsNeeded"])
            self.assertTrue(result["followupTaskRefs"])
            self.assertTrue(result["notificationRefs"])
            review = load_object(root / result["reviewRef"])
            self.assertEqual(review["type"], "ProjectManagerReview")
            self.assertEqual(review["status"], result["health"])
            followup = load_object(root / result["followupTaskRefs"][0])
            self.assertEqual(followup["assignee"], "agent.agent-hub.project-manager")
            self.assertEqual(followup["taskType"], "project_management")
            notifications = [load_object(root / ref) for ref in result["notificationRefs"]]
            self.assertIn(f"project_manager_health_{result['health']}", [item["messageType"] for item in notifications])
            self.assertIn("project_manager_human_decision_required", [item["messageType"] for item in notifications])
            project = load_object(root / "projects" / "agent-hub" / "project.md")
            self.assertEqual(project["lastProjectManagerReviewRef"], result["reviewRef"])
            self.assertEqual(project["health"], result["health"])
            self.assertIn("project.pm_health_check", audit_actions(root))

    def test_common_agent_rules_are_injected_and_evaluated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            rules_dir = root / "docs" / "agent-team"
            rules_dir.mkdir(parents=True, exist_ok=True)
            (rules_dir / "common-agent-operating-rules.md").write_text("# Agent 公共运行制度\n", encoding="utf-8")
            (rules_dir / "company-agent-constitution.md").write_text("# 公司 Agent 宪法\n", encoding="utf-8")
            (rules_dir / "agent-task-runtime-contract.md").write_text("# Agent 任务运行契约\n", encoding="utf-8")
            (rules_dir / "human-acceptance-policy.md").write_text("# 人类验收策略\n", encoding="utf-8")
            (rules_dir / "company-agent-team-operating-guide.md").write_text("# 公司 Agent Team 工作指南\n", encoding="utf-8")
            (rules_dir / "role-operating-specs.json").write_text('{"roles": []}\n', encoding="utf-8")
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "create",
                        "--task-id",
                        "COMMON-001",
                        "--title",
                        "验证公共制度注入",
                        "--project",
                        "agent-hub",
                        "--requester",
                        "meimei",
                        "--assignee",
                        "agent.agent-hub.project-manager",
                        "--type",
                        "project_management",
                        "--expected",
                        "输出有证据的执行结果。",
                    ]
                ),
                0,
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(main(["--root", str(root), "task", "pull", "COMMON-001"]), 0)
            context_path = Path(stdout.getvalue().strip())
            context_text = context_path.read_text(encoding="utf-8")
            self.assertIn("Common Agent Operating Rules", context_text)
            self.assertIn("common-agent-operating-rules.md", context_text)
            self.assertIn("Company Constitution", context_text)
            self.assertIn("company-agent-constitution.md", context_text)
            self.assertIn("Task Runtime Contract", context_text)
            self.assertIn("agent-task-runtime-contract.md", context_text)
            self.assertIn("Human Acceptance Policy", context_text)
            self.assertIn("human-acceptance-policy.md", context_text)
            self.assertIn("Role Rules", context_text)
            self.assertIn("role-operating-specs.json", context_text)
            self.assertIn("Project Rules", context_text)
            self.assertIn("projects/agent-hub/project.md", context_text)

            result_path = finish_project_task(
                Bundle(root),
                "COMMON-001",
                "done",
                "完成公共制度注入验证。",
                output_refs=["projects/agent-hub/launch.md"],
                evidence_refs=["projects/agent-hub/project.md"],
                tests_or_checks=["self-check completed"],
                handoff_summary="任务已完成，无需继续交接。",
            )
            result = load_object(result_path)
            self.assertEqual(result["operatingRuleRefs"]["companyConstitution"], "docs/agent-team/company-agent-constitution.md")
            self.assertEqual(result["operatingRuleRefs"]["taskRuntimeContract"], "docs/agent-team/agent-task-runtime-contract.md")
            self.assertEqual(result["operatingRuleRefs"]["humanAcceptancePolicy"], "docs/agent-team/human-acceptance-policy.md")
            self.assertEqual(result["operatingRuleRefs"]["roleRules"], "docs/agent-team/role-operating-specs.json")
            self.assertEqual(result["operatingRuleRefs"]["projectRules"], "projects/agent-hub/project.md")
            self.assertEqual(result["commonRulesEvaluation"]["status"], "passed")
            self.assertIn("operating_rule_refs", result["commonRulesEvaluation"]["checkedRules"])
            self.assertTrue(result["qualityEvaluation"]["passed"])

    def test_operating_rule_refs_do_not_accept_case_insensitive_false_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            project_dir = root / "projects" / "company-knowledge-core"
            project_dir.mkdir(parents=True, exist_ok=True)
            (project_dir / "project.md").write_text("---\ntype: Project\nprojectId: company-knowledge-core\n---\n# Project\n", encoding="utf-8")
            (project_dir / "agents.md").write_text("# lowercase agents file\n", encoding="utf-8")

            refs = core_module.task_operating_rule_refs(
                Bundle(root),
                {"projectId": "company-knowledge-core", "assignee": "agent.company.development"},
            )

            self.assertEqual(refs["projectRules"], "projects/company-knowledge-core/project.md")

    def test_agent_rules_issue_creates_governance_task_and_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "agent-rules",
                            "issue",
                            "--title",
                            "公共制度过重",
                            "--rule-id",
                            "complex-task-plan-first",
                            "--reporter",
                            "agent.company.project-manager",
                            "--reason",
                            "低风险任务也被要求写长方案，影响效率。",
                            "--proposal",
                            "允许低风险单点任务直接执行，但必须写 TaskResult。",
                        ]
                    ),
                    0,
                )
            result = json.loads(stdout.getvalue())
            self.assertEqual(result["kind"], "OperatingRuleIssue")
            issue = load_object(root / result["issueRef"])
            self.assertEqual(issue["type"], "OperatingRuleIssue")
            self.assertEqual(issue["status"], "pending")
            review_task = load_object(root / result["reviewTaskRef"])
            self.assertEqual(review_task["taskType"], "governance_change")
            self.assertEqual(review_task["assignee"], "agent.core.knowledge-steward")
            self.assertIn("agent_rule.issue.create", audit_actions(root))

    def test_agent_role_operating_specs_cover_nine_roles(self) -> None:
        spec = json.loads((REPO_ROOT / "docs" / "agent-team" / "role-operating-specs.json").read_text(encoding="utf-8"))
        roles = {role["roleId"]: role for role in spec["roles"]}
        self.assertEqual(
            set(roles),
            {
                "project-manager",
                "product-manager",
                "design",
                "architecture",
                "development",
                "test",
                "operations",
                "knowledge-engineering",
                "knowledge-query",
            },
        )
        for role in roles.values():
            self.assertTrue((REPO_ROOT / role["roleProfileRef"]).exists(), role["roleProfileRef"])
            self.assertEqual(role["skillRegistryRef"], "docs/agent-team/company-skill-registry.json")
            for skill_id in role["skillRefs"]:
                registry = json.loads((REPO_ROOT / role["skillRegistryRef"]).read_text(encoding="utf-8"))
                skill = next(item for item in registry["skills"] if item["skillId"] == skill_id)
                self.assertTrue((REPO_ROOT / skill["skillDir"] / "SKILL.md").exists(), skill["skillDir"])
            self.assertEqual(role["commonRulesRef"], "docs/agent-team/common-agent-operating-rules.md")
            for field in ["responsibilities", "skillRefs", "capabilityTags", "inputContract", "outputContract", "workflow", "acceptanceChecks", "qualityEvaluationTemplate", "handoffTo", "boundaries", "commandTemplates"]:
                self.assertTrue(role[field], f"{role['roleId']} missing {field}")
            for field in ["artifactTypes", "requiredEvidence", "qualityChecks", "failureRoutes"]:
                self.assertTrue(role["qualityEvaluationTemplate"][field], f"{role['roleId']} missing qualityEvaluationTemplate.{field}")
        self.assertIn("architecture", roles["product-manager"]["handoffTo"])
        self.assertIn("architecture", roles["design"]["handoffTo"])
        self.assertIn("development", roles["architecture"]["handoffTo"])
        self.assertIn("architecture", roles["development"]["handoffTo"])
        self.assertIn("architecture-technical-design", roles["architecture"]["skillRefs"])
        self.assertIn("code-architecture-review", roles["architecture"]["skillRefs"])
        self.assertNotIn("architecture-design", roles["development"]["capabilityTags"])

    def test_agent_role_check_creates_review_followup_notification_and_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            docs_dir = root / "docs" / "agent-team"
            docs_dir.mkdir(parents=True, exist_ok=True)
            (docs_dir / "company-agent-team-operating-guide.md").write_text("# guide\n", encoding="utf-8")
            (docs_dir / "common-agent-operating-rules.md").write_text("# rules\n", encoding="utf-8")
            (docs_dir / "skill-system-architecture.md").write_text("# skill system\n", encoding="utf-8")
            (docs_dir / "product-manager-agent-role-and-skill-pack.md").write_text("# product role\n", encoding="utf-8")
            (docs_dir / "project-manager-agent-skill-pack.md").write_text("# project role\n", encoding="utf-8")
            (root / "skills" / "_shared").mkdir(parents=True, exist_ok=True)
            (root / "skills" / "_shared" / "skill-output-contract.md").write_text("# contract\n", encoding="utf-8")
            valid_skill_body = """
## Purpose

Run a test skill.

## Triggers

- Test trigger.

## Inputs

- Test input.

## Workflow

1. Do the work.

## Outputs

- Test output.

## Quality Gate

- Test output is checkable.

## Failure Routes

- Return to owner.
"""
            for skill_id in ["project-health-orchestration", "requirement-clarification", "prd-scope-definition", "prd-high-quality-generation"]:
                skill_dir = root / "skills" / skill_id
                skill_dir.mkdir(parents=True, exist_ok=True)
                (skill_dir / "references").mkdir(parents=True, exist_ok=True)
                (skill_dir / "templates").mkdir(parents=True, exist_ok=True)
                (skill_dir / "examples").mkdir(parents=True, exist_ok=True)
                (skill_dir / "SKILL.md").write_text(
                    f"---\nname: {skill_id}\ndescription: Use when validating {skill_id} in role-check tests.\n---\n\n# {skill_id}\n{valid_skill_body}",
                    encoding="utf-8",
                )
                (skill_dir / "references" / "delivery-card.md").write_text("# Delivery\n\nThis delivery card describes inputs, outputs, evidence, quality gate, and handoff expectations for role-check validation.\n", encoding="utf-8")
                (skill_dir / "templates" / "output-template.md").write_text("# Template\n\nThis output template includes request, inputs, result, evidence, quality gate, and next step sections for validation.\n", encoding="utf-8")
                (skill_dir / "examples" / "quality-example.md").write_text("# Example\n\nThis quality example shows a complete result with evidence, checkable output, handoff readiness, and no missing fields.\n", encoding="utf-8")
            (docs_dir / "company-skill-registry.json").write_text(
                json.dumps(
                    {
                        "version": "test",
                        "sharedContractRef": "skills/_shared/skill-output-contract.md",
                        "skills": [
                            {
                                "skillId": "project-health-orchestration",
                                "name": "Project Health",
                                "ownerRole": "project-manager",
                                "skillDir": "skills/project-health-orchestration",
                                "status": "active",
                                "allowedRoles": ["project-manager"],
                                "aliases": ["project-health"],
                            },
                            {
                                "skillId": "requirement-clarification",
                                "name": "Requirement Clarification",
                                "ownerRole": "product-manager",
                                "skillDir": "skills/requirement-clarification",
                                "status": "active",
                                "allowedRoles": ["product-manager"],
                                "aliases": ["requirement-clarification"],
                            },
                            {
                                "skillId": "prd-scope-definition",
                                "name": "PRD Scope",
                                "ownerRole": "product-manager",
                                "skillDir": "skills/prd-scope-definition",
                                "status": "active",
                                "allowedRoles": ["product-manager"],
                                "aliases": ["prd-writing"],
                            },
                            {
                                "skillId": "prd-high-quality-generation",
                                "name": "PRD High Quality",
                                "ownerRole": "product-manager",
                                "skillDir": "skills/prd-high-quality-generation",
                                "status": "active",
                                "allowedRoles": ["product-manager"],
                                "aliases": ["prd-high-quality-generation"],
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (docs_dir / "role-operating-specs.json").write_text(
                json.dumps(
                    {
                        "version": "test",
                        "roles": [
                            {
                                "roleId": "project-manager",
                                "name": "项目经理 Agent",
                                "defaultAgentId": "agent.company.project-manager",
                                "primaryOwner": "agent.company.project-manager",
                                "roleProfileRef": "docs/agent-team/project-manager-agent-skill-pack.md",
                                "skillRegistryRef": "docs/agent-team/company-skill-registry.json",
                                "guideRef": "docs/agent-team/company-agent-team-operating-guide.md",
                                "commonRulesRef": "docs/agent-team/common-agent-operating-rules.md",
                                "responsibilities": ["项目健康巡检"],
                                "skillRefs": ["project-health-orchestration"],
                                "capabilityTags": ["project-health"],
                                "inputContract": ["项目状态"],
                                "outputContract": ["健康报告"],
                                "workflow": ["巡检阻塞", "通知负责人"],
                                "acceptanceChecks": ["阻塞已暴露"],
                                "qualityEvaluationTemplate": {
                                    "artifactTypes": ["ProjectHealthReview"],
                                    "requiredEvidence": ["项目任务状态"],
                                    "qualityChecks": ["阻塞可追踪"],
                                    "failureRoutes": ["创建跟进任务"],
                                },
                                "handoffTo": ["development", "test"],
                                "boundaries": ["不直接写生产代码"],
                                "commandTemplates": ["zhenzhi-knowledge project health --project <project-id> --create-followup"],
                            },
                            {
                                "roleId": "product-manager",
                                "name": "产品经理 Agent",
                                "defaultAgentId": "agent.company.product-manager",
                                "primaryOwner": "agent.company.product-manager",
                                "roleProfileRef": "docs/agent-team/product-manager-agent-role-and-skill-pack.md",
                                "skillRegistryRef": "docs/agent-team/company-skill-registry.json",
                                "guideRef": "docs/agent-team/company-agent-team-operating-guide.md",
                                "commonRulesRef": "docs/agent-team/common-agent-operating-rules.md",
                                "responsibilities": ["需求澄清", "PRD 高质量生成协议"],
                                "skillRefs": ["requirement-clarification", "prd-scope-definition", "prd-high-quality-generation"],
                                "capabilityTags": ["requirement-clarification", "prd-writing", "prd-high-quality-generation"],
                                "inputContract": ["项目目标"],
                                "outputContract": ["PRD", "六工序协议证据"],
                                "workflow": ["澄清需求", "执行 PRD 高质量生成协议", "输出验收标准"],
                                "acceptanceChecks": ["验收标准可测试", "六工序协议完成"],
                                "qualityEvaluationTemplate": {
                                    "artifactTypes": ["PRD"],
                                    "requiredEvidence": ["用户输入"],
                                    "qualityChecks": ["验收标准可测试", "PRD 高质量生成协议完成"],
                                    "failureRoutes": ["需求不清 -> 继续澄清"],
                                },
                                "handoffTo": ["design"],
                                "boundaries": ["不写生产代码"],
                                "commandTemplates": ["zhenzhi-knowledge task finish <taskId> --result submitted --summary <summary>"],
                            },
                            {
                                "roleId": "broken-role",
                                "name": "缺口岗位",
                                "defaultAgentId": "agent.company.broken",
                                "primaryOwner": "agent.company.broken",
                                "roleProfileRef": "docs/agent-team/missing.md",
                                "skillRegistryRef": "docs/agent-team/company-skill-registry.json",
                                "guideRef": "docs/agent-team/company-agent-team-operating-guide.md",
                                "commonRulesRef": "docs/agent-team/common-agent-operating-rules.md",
                                "responsibilities": [],
                                "skillRefs": [],
                                "capabilityTags": [],
                                "inputContract": [],
                                "outputContract": [],
                                "workflow": [],
                                "acceptanceChecks": [],
                                "handoffTo": [],
                                "boundaries": [],
                                "commandTemplates": [],
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(main(["--root", str(root), "agent", "role-check", "--role", "product-manager", "--project", "agent-hub"]), 0)
            ready = json.loads(stdout.getvalue())
            self.assertEqual(ready["kind"], "RoleOperatingReview")
            self.assertEqual(ready["status"], "ready")
            self.assertFalse(ready["gaps"])

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(main(["--root", str(root), "agent", "role-check", "--role", "broken-role", "--project", "agent-hub", "--create-followup"]), 0)
            broken = json.loads(stdout.getvalue())
            self.assertEqual(broken["status"], "needs_repair")
            self.assertTrue(broken["followupTaskRefs"])
            self.assertTrue(broken["notificationRefs"])
            review = load_object(root / broken["reviewRef"])
            self.assertEqual(review["type"], "RoleOperatingReview")
            followup = load_object(root / broken["followupTaskRefs"][0])
            self.assertEqual(followup["taskType"], "agent_role_change")
            self.assertEqual(followup["assignee"], "agent.company.broken")
            self.assertIn("agent.role_operating_check", audit_actions(root))

            create_project_task(
                Bundle(root),
                "Unclaimed project work",
                "agent-hub",
                "meimei",
                "agent.company.development",
                task_type="development",
                task_id="PM-SWEEP-001",
            )
            set_project_task_status(Bundle(root), "PM-SWEEP-001", "waiting_runner", "meimei")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(
                    main(["--root", str(root), "agent", "role-check", "--role", "project-manager", "--project", "agent-hub", "--create-followup"]),
                    0,
                )
            pm_review = json.loads(stdout.getvalue())
            self.assertEqual(pm_review["kind"], "RoleOperatingReview")
            self.assertEqual(pm_review["status"], "ready")
            self.assertTrue(pm_review["projectManagerReview"])
            self.assertIn(pm_review["projectManagerReview"]["health"], {"needs_decision", "at_risk", "blocked"})
            self.assertTrue(pm_review["projectManagerReview"]["notificationRefs"])

    def test_feishu_knowledge_search_returns_reviewable_sources_when_no_verified_answer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            item_dir = root / "knowledge" / "engineering"
            item_dir.mkdir(parents=True, exist_ok=True)
            item_path = item_dir / "feishu-card-json-v2-form-pattern.md"
            item_path.write_text(
                """---
type: KnowledgeItem
title: Feishu Card JSON 2.0 Form Pattern
description: Draft lesson from Feishu card debugging.
timestamp: 2026-06-18T00:00:00Z
owner: agent.company-knowledge-core.knowledge-engineering
status: draft
scope: engineering
sourceRef: feishu-card-debug-20260618
confidence: medium
---

## Lesson

飞书卡片报错的正确实现路径是使用 JSON 2.0 form 容器、input 字段和 submit button，卡片回调只返回 toast，后续结果异步发新卡片。
""",
                encoding="utf-8",
            )
            source_dir = root / "projects" / "company-knowledge-core" / "sources"
            source_dir.mkdir(parents=True, exist_ok=True)
            source_path = source_dir / "source.feishu-card.md"
            source_path.write_text(
                """---
type: SourceMaterial
title: Feishu card raw debug note
description: Raw source should not be returned as a knowledge answer.
timestamp: 2026-06-18T00:00:00Z
sourceId: source.feishu-card
projectId: company-knowledge-core
submitter: alice
owner: alice
status: draft
materialType: common_knowledge
sourceType: common_knowledge
sourceRef: feishu://message/raw-card
storageRef: ""
contentHash: raw
sensitivity: internal
---

## Original Text

飞书卡片报错的正确实现路径原始资料，不应该作为查知识答案直接展示。
""",
                encoding="utf-8",
            )
            self.assertEqual(main(["--root", str(root), "rag", "rebuild"]), 0)
            reply = feishu_module.build_reply(
                Bundle(root),
                {
                    "messageId": "om_search_reviewable",
                    "chatId": "ou_alice",
                    "chatType": "p2p",
                    "text": "飞书卡片为什么之前会报错？正确实现路径是什么？",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                    "mentionedUserIds": "",
                },
                feishu_module.load_feishu_settings(),
            )
            self.assertIn("待审核经验", reply)
            self.assertIn("Feishu Card JSON 2.0 Form Pattern [draft]", reply)
            self.assertIn("来源: feishu-card-debug-20260618", reply)
            self.assertIn("知识文件: knowledge/engineering/feishu-card-json-v2-form-pattern.md", reply)
            self.assertEqual(reply.count("Feishu Card JSON 2.0 Form Pattern [draft]"), 1)
            self.assertNotIn("Feishu card raw debug note", reply)
            self.assertNotIn("projects/company-knowledge-core/sources/source.feishu-card.md", reply)

    def test_fast_knowledge_query_logs_trace_and_respects_project_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            item_dir = root / "knowledge" / "engineering"
            item_dir.mkdir(parents=True, exist_ok=True)
            (item_dir / "core-deploy-token.md").write_text(
                """---
type: KnowledgeItem
title: Core Deploy Token Handling
description: Core project deployment token handling.
timestamp: 2026-06-19T00:00:00Z
owner: agent.company-knowledge-core.knowledge-engineering
status: verified
scope: engineering
projectId: core
sourceRef: projects/core/sources/deploy-token.md
confidence: high
---

## Lesson

Core 项目的部署令牌只能登记 secretRef，不能把明文 token 写进知识库或任务结果。
""",
                encoding="utf-8",
            )
            self.assertEqual(main(["--root", str(root), "rag", "rebuild"]), 0)
            general = feishu_module.run_knowledge_query(
                Bundle(root),
                {
                    "messageId": "om_kq_general",
                    "chatId": "ou_alice",
                    "chatType": "p2p",
                    "text": "部署令牌怎么处理？",
                    "openId": "ou_alice",
                    "userId": "alice",
                },
                "部署令牌怎么处理？",
            )
            self.assertEqual(general["answerMode"], "no_reliable_answer")
            general_log = json.loads((root / general["logRef"]).read_text(encoding="utf-8"))
            self.assertEqual(general_log["status"], "no_reliable_answer")
            self.assertEqual(general_log["rejectedCandidates"][0]["reason"], "project_scope_required")
            self.assertIn("knowledge_query.completed", audit_actions(root))

            scoped = feishu_module.run_knowledge_query(
                Bundle(root),
                {
                    "messageId": "om_kq_core",
                    "chatId": "oc_core",
                    "chatType": "group",
                    "text": "查知识：项目 Core，问题 部署令牌怎么处理？",
                    "openId": "ou_alice",
                    "userId": "alice",
                },
                "查知识：项目 Core，问题 部署令牌怎么处理？",
            )
            self.assertEqual(scoped["answerMode"], "verified_answer")
            self.assertEqual(scoped["projectId"], "core")
            self.assertIn("Core Deploy Token Handling [verified]", scoped["reply"])
            scoped_log = json.loads((root / scoped["logRef"]).read_text(encoding="utf-8"))
            self.assertEqual(scoped_log["resolvedProjectId"], "core")
            self.assertEqual(scoped_log["citations"][0]["path"], "knowledge/engineering/core-deploy-token.md")

            bind_reply = feishu_module.bind_project_group(
                Bundle(root),
                {
                    "messageId": "om_bind_core",
                    "chatId": "oc_core_group",
                    "chatType": "group",
                    "text": "绑定项目群：项目 Core",
                    "openId": "ou_alice",
                    "userId": "alice",
                },
                "Core",
                "ou_alice",
            )
            self.assertIn("已绑定项目群", bind_reply)
            bound = feishu_module.run_knowledge_query(
                Bundle(root),
                {
                    "messageId": "om_kq_bound",
                    "chatId": "oc_core_group",
                    "chatType": "group",
                    "text": "部署令牌怎么处理？",
                    "openId": "ou_alice",
                    "userId": "alice",
                },
                "部署令牌怎么处理？",
            )
            self.assertEqual(bound["answerMode"], "verified_answer")
            self.assertEqual(bound["projectId"], "core")
            bound_log = json.loads((root / bound["logRef"]).read_text(encoding="utf-8"))
            self.assertTrue(bound_log["projectBindingRef"].endswith("oc_core_group.json"))

    def test_http_fast_knowledge_query_api_returns_citations_and_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            item_dir = root / "knowledge" / "engineering"
            item_dir.mkdir(parents=True, exist_ok=True)
            (item_dir / "agent-ring-result-writeback.md").write_text(
                """---
type: KnowledgeItem
title: Agent Ring Result Writeback
description: Verified Agent Ring result writeback pattern.
timestamp: 2026-06-19T00:00:00Z
owner: agent.company-knowledge-core.knowledge-engineering
status: verified
scope: engineering
sourceRef: agent-ring-contract
confidence: high
---

## Pattern

Agent Ring 完成任务后必须写 TaskResult 和 AgentRun，并把结果引用回填到任务。
""",
                encoding="utf-8",
            )
            self.assertEqual(main(["--root", str(root), "rag", "rebuild"]), 0)
            try:
                server = KnowledgeHTTPServer(("127.0.0.1", 0), Bundle(root), api_token="test-token")
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"
            try:
                request = urllib.request.Request(
                    base + "/v0/knowledge/query",
                    data=json.dumps({"query": "Agent Ring 怎么回填任务结果？", "actor": "api-test"}).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"},
                    method="POST",
                )
                result = json.load(urllib.request.urlopen(request))
                self.assertEqual(result["kind"], "KnowledgeQueryResult")
                self.assertEqual(result["answerMode"], "verified_answer")
                self.assertIn("TaskResult", result["reply"])
                self.assertEqual(result["citations"][0]["path"], "knowledge/engineering/agent-ring-result-writeback.md")
                self.assertTrue((root / result["logRef"]).exists())
                query_log = json.loads((root / result["logRef"]).read_text(encoding="utf-8"))
                self.assertEqual(query_log["delivery"]["channel"], "http")
                self.assertEqual(query_log["delivery"]["status"], "returned")
            finally:
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()

    def test_fast_knowledge_query_uses_title_and_does_not_mask_reviewable_top_hit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            (root / "knowledge" / "policies").mkdir(parents=True, exist_ok=True)
            (root / "knowledge" / "policies" / "policy.lookup.md").write_text(
                """---
type: Policy
title: General Lookup Policy
description: General lookup rules.
timestamp: 2026-06-19T00:00:00Z
owner: alice
status: active
scope: company
---

## Policy

Lookup results must include citations.
""",
                encoding="utf-8",
            )
            item_dir = root / "knowledge" / "engineering"
            item_dir.mkdir(parents=True, exist_ok=True)
            (item_dir / "exact-draft-lookup-pattern.md").write_text(
                """---
type: KnowledgeItem
title: Exact Draft Lookup Pattern
description: Draft lookup pattern only present in frontmatter.
timestamp: 2026-06-19T00:00:00Z
owner: agent.company-knowledge-core.knowledge-engineering
status: draft
scope: engineering
projectId: core
sourceRef: exact-draft-source
confidence: medium
---

## Lesson

正文只描述回调和引用，不重复标题里的专有名称。
""",
                encoding="utf-8",
            )
            self.assertEqual(main(["--root", str(root), "rag", "rebuild"]), 0)
            result = feishu_module.run_knowledge_query(
                Bundle(root),
                {
                    "messageId": "om_exact_draft_title",
                    "chatId": "oc_core",
                    "chatType": "group",
                    "text": "查知识：项目 Core，问题 Exact Draft Lookup Pattern",
                    "openId": "ou_alice",
                    "userId": "alice",
                },
                "查知识：项目 Core，问题 Exact Draft Lookup Pattern",
            )
            self.assertEqual(result["answerMode"], "reviewable_reference")
            self.assertEqual(result["chunks"][0]["path"], "knowledge/engineering/exact-draft-lookup-pattern.md")

    def test_retrieval_index_auto_rebuilds_when_knowledge_files_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            item_dir = root / "knowledge" / "engineering"
            item_dir.mkdir(parents=True, exist_ok=True)
            (item_dir / "initial-index-item.md").write_text(
                """---
type: KnowledgeItem
title: Initial Index Item
description: Initial indexed item.
timestamp: 2026-06-19T00:00:00Z
owner: agent.company-knowledge-core.knowledge-engineering
status: verified
scope: engineering
sourceRef: initial-source
confidence: high
---

## Lesson

Initial indexed content.
""",
                encoding="utf-8",
            )
            self.assertEqual(main(["--root", str(root), "rag", "rebuild"]), 0)
            self.assertFalse([row for row in search_retrieval(Bundle(root), "Auto Rebuild Fresh Knowledge", limit=10) if row.get("title") == "Auto Rebuild Fresh Knowledge"])
            (item_dir / "auto-rebuild-fresh-knowledge.md").write_text(
                """---
type: KnowledgeItem
title: Auto Rebuild Fresh Knowledge
description: Newly added knowledge after the previous rebuild.
timestamp: 2026-06-19T00:00:00Z
owner: agent.company-knowledge-core.knowledge-engineering
status: verified
scope: engineering
sourceRef: auto-rebuild-source
confidence: high
---

## Lesson

This file was added after the previous retrieval index build.
""",
                encoding="utf-8",
            )
            rows = search_retrieval(Bundle(root), "Auto Rebuild Fresh Knowledge", limit=10)
            self.assertTrue([row for row in rows if row.get("title") == "Auto Rebuild Fresh Knowledge"])

    def test_deepseek_router_clarify_does_not_block_fast_knowledge_query(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            item_dir = root / "knowledge" / "engineering"
            item_dir.mkdir(parents=True, exist_ok=True)
            (item_dir / "meeting-notes-review.md").write_text(
                """---
type: KnowledgeItem
title: Meeting Notes Review Rule
description: Verified meeting notes review rule.
timestamp: 2026-06-19T00:00:00Z
owner: agent.company-knowledge-core.knowledge-engineering
status: verified
scope: engineering
sourceRef: meeting-review-source
confidence: high
---

## Rule

会议纪要不能直接进入可复用知识，必须先登记 SourceMaterial，再生成结构化草稿并通过 Review。
""",
                encoding="utf-8",
            )
            self.assertEqual(main(["--root", str(root), "rag", "rebuild"]), 0)
            original_router = feishu_module.call_deepseek_router

            def clarify_router(_text, _incoming):
                return {
                    "intent": "clarify",
                    "confidence": 0.9,
                    "risk": "L1",
                    "directHandle": False,
                    "taskType": "",
                    "requiredFields": {},
                    "missingFields": ["项目"],
                    "toolSuggestions": [],
                    "reason": "test router should not block knowledge search",
                    "_routerMetrics": {"fallback": False},
                }

            feishu_module.call_deepseek_router = clarify_router
            try:
                reply = feishu_module.build_reply(
                    Bundle(root),
                    {
                        "messageId": "om_router_clarify_kq",
                        "chatId": "oc_test",
                        "chatType": "group",
                        "text": "会议纪要为什么不能直接入知识库？",
                        "openId": "ou_alice",
                        "userId": "alice",
                        "mentionedOpenIds": "",
                        "mentionedUserIds": "",
                    },
                    minimal_feishu_settings(),
                )
                self.assertIn("Meeting Notes Review Rule [verified]", reply)
                self.assertNotIn("我需要补充信息", reply)
            finally:
                feishu_module.call_deepseek_router = original_router

    def test_install_writes_local_agent_entrypoints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "project",
                        "register",
                        "--project-id",
                        "core",
                        "--name",
                        "Core",
                        "--owner",
                        "alice",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "install",
                        "--user-id",
                        "alice",
                        "--ai-tool",
                        "codex",
                        "--agent-id",
                        "agent.alice.codex",
                        "--remote",
                        "https://github.com/meimei7959/company_knowledge_core.git",
                        "--default-project",
                        "core",
                        "--register-agent",
                        "--agent-name",
                        "Alice Codex",
                    ]
                ),
                0,
            )
            config_text = (root / ".zhenzhi" / "config.json").read_text(encoding="utf-8")
            self.assertIn('"defaultProjectId": "core"', config_text)
            self.assertIn("company_knowledge_core.git", config_text)
            entrypoint = (root / ".zhenzhi" / "agent-entrypoint.md").read_text(encoding="utf-8")
            self.assertIn("zhenzhi-knowledge start --project core --agent agent.alice.codex", entrypoint)
            self.assertIn("zhenzhi-knowledge finish --project core --agent agent.alice.codex", entrypoint)
            self.assertTrue((root / ".zhenzhi" / "codex-start.md").exists())
            self.assertTrue((root / ".zhenzhi" / "antigravity-start.md").exists())
            self.assertTrue((root / ".zhenzhi" / "claude-start.md").exists())
            self.assertTrue((root / "agents" / "agent.alice.codex.md").exists())

    def test_validate_blocks_unstructured_knowledge_dump(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            (root / "knowledge" / "random.md").write_text("raw notes without structure\n", encoding="utf-8")
            self.assertEqual(main(["--root", str(root), "validate"]), 1)

    def test_validate_accepts_categorized_knowledge_item(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            item_dir = root / "knowledge" / "engineering"
            item_dir.mkdir(parents=True, exist_ok=True)
            (item_dir / "lesson.md").write_text(
                """---
type: KnowledgeItem
title: Engineering Lesson
description: Structured lesson.
timestamp: 2026-06-17T00:00:00Z
owner: alice
status: draft
scope: engineering
sourceRef: projects/core/project.md
confidence: medium
---

## Knowledge

Structured knowledge only.
""",
                encoding="utf-8",
            )
            self.assertEqual(main(["--root", str(root), "validate"]), 0)

    def test_environment_manifest_rejects_local_absolute_canonical_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            task = root / "projects" / "core" / "tasks" / "env-word-task.md"
            task.parent.mkdir(parents=True, exist_ok=True)
            task.write_text(
                """---
type: ProjectTask
title: Environment readiness task
description: "Normal task that mentions environment and validate command paths."
timestamp: 2026-06-18T00:00:00Z
taskId: ENV-WORD-TASK
taskType: development
projectId: core
requester: alice
assignee: agent.alice.builder
status: pending
priority: normal
---

## Request

Run `python3 -m zhenzhi_knowledge --root /Users/alice/projects/core validate`.
""",
                encoding="utf-8",
            )
            self.assertEqual(main(["--root", str(root), "validate"]), 0)
            manifest = root / "projects" / "core" / "environment.manifest.md"
            manifest.write_text(
                """---
type: Workflow
title: Core Environment Manifest
description: Portable environment manifest.
timestamp: 2026-06-18T00:00:00Z
owner: alice
status: draft
scope: project
projectId: core
---

## Environment

repositories:
  - localPath: /Users/alice/projects/core
secrets:
  - ref: secretref://zhenzhi/model/deepseek
""",
                encoding="utf-8",
            )
            self.assertEqual(main(["--root", str(root), "validate"]), 1)
            manifest.write_text(manifest.read_text(encoding="utf-8").replace("/Users/alice/projects/core", "workspace://core"), encoding="utf-8")
            self.assertEqual(main(["--root", str(root), "validate"]), 0)

    def test_task_flow_creates_pull_context_and_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.grant_agent_write_policy(root, "alice")
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            source = root / "projects" / "core" / "sources" / "sm-meeting.md"
            source.write_text(
                """---
type: SourceMaterial
title: Meeting
description: Meeting note.
timestamp: 2026-06-18T00:00:00Z
sourceId: SM-20260618-001
sourceType: feishu
materialType: meeting_note
sourceRef: feishu://minutes/abc
owner: bob
status: pending
scope: project
projectId: core
---

## Raw

The team decided to create task-based knowledge intake.
""",
                encoding="utf-8",
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "create",
                        "--task-id",
                        "KT-20260618-001",
                        "--title",
                        "整理会议纪要",
                        "--project",
                        "core",
                        "--requester",
                        "bob",
                        "--assignee",
                        "alice",
                        "--source",
                        "projects/core/sources/sm-meeting.md",
                        "--expected",
                        "结构化会议结论并保留证据",
                    ]
                ),
                0,
            )
            task = root / "projects" / "core" / "tasks" / "kt-20260618-001.md"
            self.assertTrue(task.exists())
            self.assertIn("type: KnowledgeTask", task.read_text(encoding="utf-8"))

            self.assertEqual(main(["--root", str(root), "task", "pull", "KT-20260618-001"]), 0)
            context = root / ".zhenzhi" / "context" / "task.kt-20260618-001.md"
            self.assertTrue(context.exists())
            context_text = context.read_text(encoding="utf-8")
            self.assertIn("taskId: KT-20260618-001", context_text)
            self.assertIn("task-based knowledge intake", context_text)

            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "finish",
                        "KT-20260618-001",
                        "--result",
                        "done",
                        "--summary",
                        "已整理会议结论，待 Review。",
                        "--evidence-ref",
                        "projects/core/sources/sm-meeting.md",
                        "--knowledge-draft-json",
                        json.dumps(
                            {
                                "title": "会议纪要结构化经验",
                                "summary": "会议纪要已整理为可 Review 草稿。",
                                "structured": "会议纪要处理需要保留原文证据，并输出结构化结论。",
                                "sourceRefs": ["projects/core/sources/sm-meeting.md"],
                                "confidence": "medium",
                                "scope": "engineering",
                                "limits": ["测试夹具生成的最小草稿。"],
                            },
                            ensure_ascii=False,
                        ),
                    ]
                ),
                0,
            )
            result = root / "task-results" / "tr-kt-20260618-001.md"
            self.assertTrue(result.exists())
            self.assertIn("type: TaskResult", result.read_text(encoding="utf-8"))
            task_text = task.read_text(encoding="utf-8")
            self.assertIn("status: done", task_text)
            self.assertIn("resultRef: task-results/tr-kt-20260618-001.md", task_text)
            self.assertEqual(main(["--root", str(root), "validate"]), 0)

    def test_task_lookup_uses_frontmatter_task_id_when_filename_differs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            task = root / "projects" / "core" / "tasks" / "human-readable-task.md"
            task.write_text(
                """---
type: ProjectTask
title: Filename differs from taskId
description: Regression task.
timestamp: 2026-06-18T00:00:00Z
taskId: KT-FRONTMATTER-ID
projectId: core
requester: bob
assignee: runner.mac-mini
status: pending
humanAcceptanceRequired: false
sourceMaterialRefs: []
expectedOutput:
  - TaskResult
resultRef:
---

## Task

Use the frontmatter taskId as the stable business identifier.
""",
                encoding="utf-8",
            )

            self.assertEqual(main(["--root", str(root), "task", "pull", "KT-FRONTMATTER-ID"]), 0)
            self.assertTrue((root / ".zhenzhi" / "context" / "task.kt-frontmatter-id.md").exists())
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "finish",
                        "KT-FRONTMATTER-ID",
                        "--result",
                        "done",
                        "--summary",
                        "Task lookup by frontmatter taskId works.",
                        "--evidence-ref",
                        "projects/core/tasks/human-readable-task.md",
                    ]
                ),
                0,
            )
            self.assertIn("status: done", task.read_text(encoding="utf-8"))
            self.assertTrue((root / "task-results" / "tr-kt-frontmatter-id.md").exists())

    def test_agent_ring_http_task_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.grant_agent_write_policy(root, "agent.codex.local")
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            source = root / "projects" / "core" / "sources" / "sm-meeting.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(
                """---
type: SourceMaterial
title: Meeting
description: Meeting note.
timestamp: 2026-06-18T00:00:00Z
sourceId: SM-20260618-001
sourceType: feishu
sourceRef: feishu://minutes/abc
owner: bob
status: draft
projectId: core
---

## Original Text

Agent Ring should pull tasks from the central processor and write back evidence.
""",
                encoding="utf-8",
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "create",
                        "--task-id",
                        "KT-20260618-010",
                        "--title",
                        "整理会议纪要",
                        "--project",
                        "core",
                        "--requester",
                        "bob",
                        "--assignee",
                        "runner.mac-mini",
                        "--source",
                        "projects/core/sources/sm-meeting.md",
                    ]
                ),
                0,
            )
            try:
                server = KnowledgeHTTPServer(("127.0.0.1", 0), Bundle(root), api_token="ring-token")
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"

            def post(path: str, payload: dict) -> dict:
                request = urllib.request.Request(
                    base + path,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer ring-token"},
                    method="POST",
                )
                return json.load(urllib.request.urlopen(request))

            def get(path: str) -> dict:
                request = urllib.request.Request(base + path, headers={"Authorization": "Bearer ring-token"})
                return json.load(urllib.request.urlopen(request))

            try:
                runner = post(
                    "/v0/runners/register",
                    {
                        "runnerId": "runner.mac-mini",
                        "name": "Mac mini Runner",
                        "hostType": "macos",
                        "agents": ["codex"],
                        "capabilities": ["knowledge_capture"],
                        "availableProjects": ["core"],
                    },
                )
                self.assertEqual(runner["runnerRef"], "runners/runner.mac-mini.md")
                runner_upsert = post(
                    "/v0/runners/register",
                    {
                        "runnerId": "runner.mac-mini",
                        "name": "Mac mini Runner Updated",
                        "hostType": "macos",
                        "agents": ["codex", "claude"],
                        "capabilities": ["knowledge_capture"],
                        "availableProjects": ["core"],
                    },
                )
                self.assertEqual(runner_upsert["runnerRef"], "runners/runner.mac-mini.md")
                runner_text = (root / "runners" / "runner.mac-mini.md").read_text(encoding="utf-8")
                self.assertIn("Mac mini Runner Updated", runner_text)
                self.assertIn("claude", runner_text)
                heartbeat = post("/v0/runners/heartbeat", {"runnerId": "runner.mac-mini", "status": "busy", "load": "1"})
                self.assertEqual(heartbeat["kind"], "RunnerHeartbeat")

                tasks = get("/v0/tasks?status=pending&assignee=runner.mac-mini")
                self.assertEqual(len(tasks["tasks"]), 1)
                self.assertEqual(tasks["tasks"][0]["taskId"], "KT-20260618-010")

                claim = post(
                    "/v0/tasks/claim",
                    {"taskId": "KT-20260618-010", "runnerId": "runner.mac-mini", "expectedVersion": 1, "leaseSeconds": 600},
                )
                self.assertEqual(claim["kind"], "TaskClaim")
                lease_token = claim["leaseToken"]
                self.assertEqual(claim["task"]["status"], "processing")

                with self.assertRaises(urllib.error.HTTPError) as stale_claim:
                    post(
                        "/v0/tasks/claim",
                        {"taskId": "KT-20260618-010", "runnerId": "runner.mac-mini", "expectedVersion": 1},
                    )
                self.assertEqual(stale_claim.exception.code, 400)

                with self.assertRaises(urllib.error.HTTPError) as bad_finish:
                    post(
                        "/v0/tasks/finish",
                        {
                            "taskId": "KT-20260618-010",
                            "runnerId": "runner.mac-mini",
                            "leaseToken": "wrong",
                            "summary": "should fail",
                        },
                    )
                self.assertEqual(bad_finish.exception.code, 400)

                context = post(
                    "/v0/tasks/pull",
                    {"taskId": "KT-20260618-010", "runnerId": "runner.mac-mini", "leaseToken": lease_token},
                )
                self.assertEqual(context["task"]["status"], "processing")
                self.assertIn("Agent Ring should pull tasks", context["context"])
                self.assertEqual(context["contextRef"], ".zhenzhi/context/task.kt-20260618-010.md")
                self.assertEqual(context["projectContextBundle"]["project"]["projectId"], "core")
                self.assertEqual(context["projectContextBundle"]["task"]["taskId"], "KT-20260618-010")
                self.assertIn("projects/core/sources/sm-meeting.md", context["projectContextBundle"]["task"]["sourceMaterialRefs"])
                self.assertEqual(context["projectContextBundle"]["handoff"]["requiredFields"][0], "done")

                task_heartbeat = post(
                    "/v0/tasks/heartbeat",
                    {"taskId": "KT-20260618-010", "runnerId": "runner.mac-mini", "leaseToken": lease_token},
                )
                self.assertEqual(task_heartbeat["kind"], "TaskHeartbeat")

                result = post(
                    "/v0/tasks/finish",
                    {
                        "taskId": "KT-20260618-010",
                        "runnerId": "runner.mac-mini",
                        "leaseToken": lease_token,
                        "executorAgent": "agent.codex.local",
                        "result": "done",
                        "summary": "已完成结构化整理，证据保留在原始资料中。",
                        "evidenceRefs": ["projects/core/sources/sm-meeting.md"],
                        "testsOrChecks": ["stub runner deterministic writeback"],
                        "nextActions": ["进入知识 Review"],
                        "knowledgeDraft": {
                            "title": "Agent Ring task lifecycle lesson",
                            "summary": "Runner 完成任务后必须写回结构化知识草稿和证据。",
                            "structured": "Agent Ring 写回 KnowledgeTask 时要包含 TaskResult、KnowledgeItem draft、source evidence 和 tests/checks。",
                            "sourceRefs": ["projects/core/sources/sm-meeting.md"],
                            "confidence": "medium",
                            "scope": "engineering",
                            "limits": ["HTTP 集成测试夹具生成。"],
                        },
                    },
                )
                self.assertEqual(result["task"]["status"], "done")
                self.assertEqual(result["resultRef"], "task-results/tr-kt-20260618-010.md")
                before_results = sorted((root / "task-results").glob("tr-kt-20260618-010.md"))
                repeat_result = post(
                    "/v0/tasks/finish",
                    {
                        "taskId": "KT-20260618-010",
                        "runnerId": "runner.mac-mini",
                        "leaseToken": lease_token,
                        "executorAgent": "agent.codex.local",
                        "result": "done",
                        "summary": "已完成结构化整理，证据保留在原始资料中。",
                        "evidenceRefs": ["projects/core/sources/sm-meeting.md"],
                        "testsOrChecks": ["stub runner deterministic writeback"],
                        "knowledgeDraft": {
                            "title": "Agent Ring task lifecycle lesson",
                            "summary": "Runner 完成任务后必须写回结构化知识草稿和证据。",
                            "structured": "Agent Ring 写回 KnowledgeTask 时要包含 TaskResult、KnowledgeItem draft、source evidence 和 tests/checks。",
                            "sourceRefs": ["projects/core/sources/sm-meeting.md"],
                            "confidence": "medium",
                            "scope": "engineering",
                            "limits": ["HTTP 集成测试夹具生成。"],
                        },
                    },
                )
                self.assertEqual(repeat_result["resultRef"], "task-results/tr-kt-20260618-010.md")
                self.assertEqual(before_results, sorted((root / "task-results").glob("tr-kt-20260618-010.md")))
                result_text = (root / "task-results" / "tr-kt-20260618-010.md").read_text(encoding="utf-8")
                self.assertIn("runnerId: runner.mac-mini", result_text)
                self.assertIn("executorAgent: agent.codex.local", result_text)
                self.assertIn("stub runner deterministic writeback", result_text)
                self.assertIn("status: busy", (root / "runners" / "runner.mac-mini.md").read_text(encoding="utf-8"))
                self.assertIn("task.finish", "\n".join(path.read_text(encoding="utf-8") for path in (root / "knowledge" / "audit").glob("*.md")))

                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "task",
                            "create",
                            "--task-id",
                            "KT-20260618-011",
                            "--title",
                            "处理可重分配任务",
                            "--project",
                            "core",
                            "--requester",
                            "bob",
                            "--assignee",
                            "runner.mac-mini",
                            "--source",
                            "projects/core/sources/sm-meeting.md",
                        ]
                    ),
                    0,
                )
                post(
                    "/v0/runners/register",
                    {
                        "runnerId": "runner.macbook",
                        "name": "MacBook Runner",
                        "hostType": "macos",
                        "agents": ["codex"],
                        "capabilities": ["knowledge_capture"],
                        "availableProjects": ["core"],
                    },
                )
                registry = get("/v0/runners?projectId=core")
                self.assertEqual(registry["kind"], "RunnerRegistry")
                self.assertEqual({item["runnerId"] for item in registry["runners"]}, {"runner.mac-mini", "runner.macbook"})
                first_claim = post("/v0/tasks/claim", {"taskId": "KT-20260618-011", "runnerId": "runner.mac-mini"})
                with self.assertRaises(urllib.error.HTTPError) as active_lease:
                    post("/v0/tasks/claim", {"taskId": "KT-20260618-011", "runnerId": "runner.macbook"})
                self.assertEqual(active_lease.exception.code, 400)
                task2 = root / "projects" / "core" / "tasks" / "kt-20260618-011.md"
                handoff_result = post(
                    "/v0/tasks/handoff",
                    {
                        "taskId": "KT-20260618-011",
                        "actor": "runner.mac-mini",
                        "handoffTo": "runner.macbook",
                        "summary": "Runner mac-mini reviewed source material; runner.macbook should continue.",
                        "runnerId": "runner.mac-mini",
                        "leaseToken": first_claim["leaseToken"],
                        "evidenceRefs": ["projects/core/sources/sm-meeting.md"],
                        "preferredRunner": "runner.macbook",
                    },
                )
                self.assertEqual(handoff_result["kind"], "TaskManualHandoffResult")
                self.assertIn("handoff.", handoff_result["handoffRef"])
                self.assertIn("status: manual_handoff", task2.read_text(encoding="utf-8"))
                second_claim = post("/v0/tasks/claim", {"taskId": "KT-20260618-011", "runnerId": "runner.macbook"})
                self.assertEqual(second_claim["task"]["leaseOwner"], "runner.macbook")
                second_context = post(
                    "/v0/tasks/pull",
                    {"taskId": "KT-20260618-011", "runnerId": "runner.macbook", "leaseToken": second_claim["leaseToken"]},
                )
                self.assertIn(handoff_result["handoffRef"], second_context["projectContextBundle"]["executionHistory"]["handoffRefs"])
                self.assertIn("projects/core/sources/sm-meeting.md", second_context["projectContextBundle"]["task"]["sourceMaterialRefs"])
                task2.write_text(task2.read_text(encoding="utf-8").replace(second_claim["leaseExpiresAt"], "2000-01-01T00:00:00Z"), encoding="utf-8")
                with self.assertRaises(urllib.error.HTTPError) as expired_finish:
                    post(
                        "/v0/tasks/finish",
                        {
                            "taskId": "KT-20260618-011",
                            "runnerId": "runner.macbook",
                            "leaseToken": second_claim["leaseToken"],
                            "summary": "should fail because lease expired",
                        },
                    )
                self.assertEqual(expired_finish.exception.code, 400)

                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "task",
                            "create",
                            "--task-id",
                            "KT-20260618-017",
                            "--title",
                            "取消后重试任务",
                            "--project",
                            "core",
                            "--requester",
                            "bob",
                            "--assignee",
                            "runner.macbook",
                            "--source",
                            "projects/core/sources/sm-meeting.md",
                        ]
                    ),
                    0,
                )
                cancel_claim = post("/v0/tasks/claim", {"taskId": "KT-20260618-017", "runnerId": "runner.macbook"})
                cancel_result = post(
                    "/v0/tasks/cancel",
                    {
                        "taskId": "KT-20260618-017",
                        "actor": "agent.company.project-manager",
                        "reason": "Operator stopped the active run.",
                        "runnerId": "runner.macbook",
                        "leaseToken": cancel_claim["leaseToken"],
                    },
                )
                self.assertEqual(cancel_result["kind"], "TaskCancelResult")
                with self.assertRaises(urllib.error.HTTPError) as closed_claim:
                    post("/v0/tasks/claim", {"taskId": "KT-20260618-017", "runnerId": "runner.macbook"})
                self.assertEqual(closed_claim.exception.code, 400)
                retry_result = post(
                    "/v0/tasks/retry",
                    {
                        "taskId": "KT-20260618-017",
                        "actor": "agent.company.project-manager",
                        "reason": "Restart after operator cancellation.",
                        "preferredRunner": "runner.macbook",
                    },
                )
                self.assertEqual(retry_result["kind"], "TaskRetryResult")
                retried_claim = post("/v0/tasks/claim", {"taskId": "KT-20260618-017", "runnerId": "runner.macbook"})
                self.assertEqual(retried_claim["task"]["leaseOwner"], "runner.macbook")

                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "task",
                            "create",
                            "--task-id",
                            "KT-20260618-012",
                            "--title",
                            "处理缺少凭证的任务",
                            "--project",
                            "core",
                            "--requester",
                            "bob",
                            "--assignee",
                            "runner.macbook",
                        ]
                    ),
                    0,
                )
                missing_secret_task = root / "projects" / "core" / "tasks" / "kt-20260618-012.md"
                missing_secret_task.write_text(
                    missing_secret_task.read_text(encoding="utf-8").replace(
                        "resultRef:",
                        "requiredSecretRefs:\n  - secretref://stub/deepseek\nresultRef:",
                    ),
                    encoding="utf-8",
                )
                with self.assertRaises(urllib.error.HTTPError) as missing_secret:
                    post("/v0/tasks/claim", {"taskId": "KT-20260618-012", "runnerId": "runner.macbook"})
                self.assertEqual(missing_secret.exception.code, 400)
                self.assertIn("status: blocked", missing_secret_task.read_text(encoding="utf-8"))

                feishu_module.create_access_credential_request(
                    Bundle(root),
                    requester="ou_alice",
                    purpose="stub deepseek readiness",
                    credential_type="model_api",
                    request_id="credential.stub.deepseek",
                )
                ready = post(
                    "/v0/credentials/ready",
                    {
                        "requestId": "credential.stub.deepseek",
                        "secretRef": "secretref://stub/deepseek",
                        "actor": "runner.macbook",
                    },
                )
                self.assertEqual(ready["kind"], "CredentialReady")
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "task",
                            "create",
                            "--task-id",
                            "KT-20260618-013",
                            "--title",
                            "处理已有凭证的任务",
                            "--project",
                            "core",
                            "--requester",
                            "bob",
                            "--assignee",
                            "runner.macbook",
                        ]
                    ),
                    0,
                )
                ready_secret_task = root / "projects" / "core" / "tasks" / "kt-20260618-013.md"
                ready_secret_task.write_text(
                    ready_secret_task.read_text(encoding="utf-8").replace(
                        "resultRef:",
                        "requiredSecretRefs:\n  - secretref://stub/deepseek\nresultRef:",
                    ),
                    encoding="utf-8",
                )
                ready_claim = post("/v0/tasks/claim", {"taskId": "KT-20260618-013", "runnerId": "runner.macbook"})
                self.assertEqual(ready_claim["task"]["status"], "processing")

                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "task",
                            "create",
                            "--task-id",
                            "KT-20260618-014",
                            "--title",
                            "需要工程能力的任务",
                            "--project",
                            "core",
                            "--requester",
                            "bob",
                            "--assignee",
                            "runner.macbook",
                        ]
                    ),
                    0,
                )
                missing_cap_task = root / "projects" / "core" / "tasks" / "kt-20260618-014.md"
                missing_cap_task.write_text(
                    missing_cap_task.read_text(encoding="utf-8").replace(
                        "resultRef:",
                        "requiredCapabilities:\n  - engineering_action\nresultRef:",
                    ),
                    encoding="utf-8",
                )
                with self.assertRaises(urllib.error.HTTPError) as missing_capability:
                    post("/v0/tasks/claim", {"taskId": "KT-20260618-014", "runnerId": "runner.macbook"})
                self.assertEqual(missing_capability.exception.code, 400)
                self.assertIn("status: blocked", missing_cap_task.read_text(encoding="utf-8"))

                post(
                    "/v0/runners/register",
                    {
                        "runnerId": "runner.engineer",
                        "name": "Engineering Runner",
                        "hostType": "linux",
                        "agents": ["codex"],
                        "capabilities": ["engineering_action"],
                        "availableProjects": ["core"],
                    },
                )
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "task",
                            "create",
                            "--task-id",
                            "KT-20260618-018",
                            "--title",
                            "工程实现任务",
                            "--project",
                            "core",
                            "--requester",
                            "bob",
                            "--assignee",
                            "runner.engineer",
                            "--type",
                            "engineering_action",
                        ]
                    ),
                    0,
                )
                update_frontmatter_file(root / "projects" / "core" / "tasks" / "kt-20260618-018.md", {"humanAcceptanceRequired": False})
                project_claim = post("/v0/tasks/claim", {"taskId": "KT-20260618-018", "runnerId": "runner.engineer"})
                project_context = post(
                    "/v0/tasks/pull",
                    {"taskId": "KT-20260618-018", "runnerId": "runner.engineer", "leaseToken": project_claim["leaseToken"]},
                )
                self.assertIn("engineering_action", project_context["context"])
                project_result = post(
                    "/v0/tasks/finish",
                    {
                        "taskId": "KT-20260618-018",
                        "runnerId": "runner.engineer",
                        "leaseToken": project_claim["leaseToken"],
                        "executorAgent": "agent.codex.local",
                        "result": "done",
                        "summary": "StubRunner completed a ProjectTask without claiming real local side effects.",
                        "outputRefs": ["projects/core/tasks/kt-20260618-018.md"],
                        "testsOrChecks": ["stubbed engineering_action only"],
                    },
                )
                self.assertEqual(project_result["task"]["status"], "done")
            finally:
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()
            self.assertEqual(main(["--root", str(root), "validate"]), 0)

    def test_agent_ring_contract_script_runs_when_socket_allowed(self) -> None:
        module_path = REPO_ROOT / "scripts" / "agent_ring_contract.py"
        spec = importlib.util.spec_from_file_location("agent_ring_contract", module_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module.create_fixture(root)
            try:
                result = module.run_contract(root)
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            self.assertTrue(result["ok"])
            self.assertIn("runner_register", result["checks"])
            self.assertIn("stale_version", result["checks"])
            self.assertIn("invalid_lease", result["checks"])
            self.assertIn("missing_capability", result["checks"])
            self.assertIn("expired_lease", result["checks"])

    def test_feishu_async_card_failure_writes_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = minimal_feishu_settings(app_id="cli_x", app_secret="secret", reply_enabled=True)
            original_send = feishu_module.send_feishu_response

            def failing_send(_settings, _message_id, _response):
                raise feishu_module.KnowledgeError("Feishu reply failed: 200530")

            feishu_module.send_feishu_response = failing_send
            try:
                self.assertTrue(
                    feishu_module.send_feishu_response_later(
                        settings,
                        "om_card_error",
                        {"msg_type": "interactive", "card": {"type": "template"}},
                        Bundle(root),
                        action_name="project_create_submit",
                    )
                )
                audit_dir = root / "knowledge" / "audit"
                for _ in range(50):
                    audit_text = "\n".join(path.read_text(encoding="utf-8") for path in audit_dir.glob("*.md"))
                    if "feishu.async_reply.failed" in audit_text:
                        break
                    time.sleep(0.01)
                self.assertIn("feishu.async_reply.failed", audit_text)
                self.assertIn("project_create_submit", audit_text)
                self.assertIn("200530", audit_text)
            finally:
                feishu_module.send_feishu_response = original_send

    def test_index_includes_task_objects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "task",
                        "create",
                        "--task-id",
                        "KT-20260618-002",
                        "--title",
                        "处理项目资料",
                        "--project",
                        "core",
                        "--requester",
                        "bob",
                        "--assignee",
                        "alice",
                    ]
                ),
                0,
            )
            self.assertEqual(main(["--root", str(root), "index", "rebuild"]), 0)
            rows = search_index(Bundle(root), {"type": "KnowledgeTask", "status": "pending"})
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["path"], "projects/core/tasks/kt-20260618-002.md")

    def test_validate_blocks_approved_tool_without_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            tool = root / "tools" / "tool.parser.md"
            tool.write_text(
                """---
type: ToolAsset
title: Parser
description: Parser tool.
timestamp: 2026-06-17T00:00:00Z
toolId: tool.parser
owner: alice
repoRef: git@example.com:zhenzhi/parser.git
entrypoint: cli://parser
version: 0.1.0
status: approved
scope: company
riskLevel: L1
lastVerifiedAt: ""
---

## Usage

Parse documents.
""",
                encoding="utf-8",
            )
            self.assertEqual(main(["--root", str(root), "validate"]), 1)

    def test_high_risk_tool_dry_run_is_allowed_but_execution_requires_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "init", "--user-id", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "agent", "register", "--agent-id", "agent.alice.builder", "--name", "Alice Builder", "--owner", "alice", "--purpose", "local development"]), 0)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "tool",
                        "register",
                        "--tool-id",
                        "tool.publisher",
                        "--name",
                        "Publisher",
                        "--owner",
                        "alice",
                        "--repo",
                        "git@example.com:zhenzhi/publisher.git",
                        "--entrypoint",
                        "echo://published",
                        "--risk",
                        "L3",
                    ]
                ),
                0,
            )
            tool_path = root / "tools" / "tool.publisher.md"
            tool_text = tool_path.read_text(encoding="utf-8")
            tool_path.write_text(
                tool_text.replace("status: testing", "status: approved").replace('lastVerifiedAt: ""', 'lastVerifiedAt: "2026-06-18T00:00:00Z"'),
                encoding="utf-8",
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "tool",
                        "invoke",
                        "--tool-id",
                        "tool.publisher",
                        "--project",
                        "core",
                        "--agent",
                        "agent.alice.builder",
                        "--input",
                        "prepare publish draft",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "tool",
                        "invoke",
                        "--tool-id",
                        "tool.publisher",
                        "--project",
                        "core",
                        "--agent",
                        "agent.alice.builder",
                        "--input",
                        "publish externally",
                        "--execute",
                    ]
                ),
                2,
            )

    def test_register_start_finish_review_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "init", "--user-id", "alice"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "agent",
                        "register",
                        "--agent-id",
                        "agent.alice.builder",
                        "--name",
                        "Alice Builder",
                        "--owner",
                        "alice",
                        "--purpose",
                        "local development",
                    ]
                ),
                0,
            )
            knowledge_dir = root / "knowledge" / "engineering"
            knowledge_dir.mkdir(parents=True, exist_ok=True)
            (knowledge_dir / "parser-context.md").write_text(
                """---
type: KnowledgeItem
title: Parser Context
description: Parser context for retrieval.
timestamp: 2026-06-17T00:00:00Z
owner: alice
status: verified
scope: engineering
sourceRef: tools/tool.parser.md
confidence: high
---

## Knowledge

Parser work should preserve source references in Agent output.
""",
                encoding="utf-8",
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "project",
                        "register",
                        "--project-id",
                        "core",
                        "--name",
                        "Core",
                        "--owner",
                        "alice",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "tool",
                        "register",
                        "--tool-id",
                        "tool.parser",
                        "--name",
                        "Parser",
                        "--owner",
                        "alice",
                        "--repo",
                        "git@example.com:zhenzhi/parser.git",
                        "--entrypoint",
                        "cli://parser",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "policy",
                        "register",
                        "--policy-id",
                        "policy.alice",
                        "--title",
                        "Alice Policy",
                        "--agent-id",
                        "agent.alice.builder",
                        "--owner",
                        "alice",
                        "--allow-project",
                        "core",
                        "--allow-scope",
                        "engineering",
                        "--allow-risk",
                        "L1",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "review",
                        "update",
                        "--target",
                        "knowledge/policies/policy.alice.md",
                        "--status",
                        "active",
                        "--reviewer",
                        "alice",
                    ]
                ),
                0,
            )
            self.assertEqual(main(["--root", str(root), "rag", "rebuild"]), 0)
            self.assertEqual(main(["--root", str(root), "rag", "search", "--query", "parser source references", "--scope", "engineering"]), 0)
            self.assertEqual(main(["--root", str(root), "start", "--project", "core", "--agent", "agent.alice.builder", "--task", "parser source references work"]), 0)
            self.assertTrue((root / ".zhenzhi" / "context" / "current.md").exists())
            context_text = (root / ".zhenzhi" / "context" / "current.md").read_text(encoding="utf-8")
            self.assertIn("## Retrieved Context", context_text)
            self.assertIn("knowledge/engineering/parser-context.md", context_text)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "finish",
                        "--project",
                        "core",
                        "--agent",
                        "agent.alice.builder",
                        "--summary",
                        "completed work",
                        "--no-reusable-lesson",
                    ]
                ),
                0,
            )
            runs = list((root / "runs" / "core").glob("*.md"))
            self.assertEqual(len(runs), 1)
            run_text = runs[0].read_text(encoding="utf-8")
            self.assertIn("knowledge/engineering/parser-context.md", run_text)
            self.assertIn(".zhenzhi/context/context.", run_text)
            self.assertNotIn("TBD", run_text)
            self.assertEqual(main(["--root", str(root), "review", "update", "--target", str(runs[0]), "--status", "verified", "--reviewer", "alice"]), 0)
            self.assertTrue(list((root / "knowledge" / "audit").glob("*.md")))
            self.assertTrue((root / "knowledge" / "policies" / "policy.alice.md").exists())
            self.assertEqual(main(["--root", str(root), "review", "list"]), 0)
            self.assertEqual(main(["--root", str(root), "review", "bulk", "--type", "ToolAsset", "--from-status", "testing", "--to-status", "approved", "--reviewer", "alice", "--limit", "1"]), 0)
            self.assertIn("lastVerifiedAt:", (root / "tools" / "tool.parser.md").read_text(encoding="utf-8"))
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "tool",
                        "invoke",
                        "--tool-id",
                        "tool.parser",
                        "--project",
                        "core",
                        "--agent",
                        "agent.alice.builder",
                        "--input",
                        "parse source references",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "tool",
                        "invoke",
                        "--tool-id",
                        "tool.unknown",
                        "--project",
                        "core",
                        "--agent",
                        "agent.alice.builder",
                        "--input",
                        "blocked",
                    ]
                ),
                2,
            )
            self.assertEqual(main(["--root", str(root), "index", "rebuild"]), 0)
            self.assertFalse((root / ".zhenzhi" / "index.sqlite3").exists())
            self.assertEqual(main(["--root", str(root), "index", "search", "--type", "ToolAsset"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "conflict",
                        "create",
                        "--type",
                        "fact",
                        "--owner",
                        "alice",
                        "--summary",
                        "conflicting project note",
                        "--affected",
                        "projects/core/project.md",
                    ]
                ),
                0,
            )
            self.assertTrue(list((root / "knowledge" / "conflicts").glob("*.md")))
            conflict_path = list((root / "knowledge" / "conflicts").glob("*.md"))[0]
            self.assertEqual(main(["--root", str(root), "conflict", "resolve", "--target", str(conflict_path), "--owner", "alice", "--resolution", "kept project note"]), 0)
            self.assertIn("status: resolved", conflict_path.read_text(encoding="utf-8"))
            self.assertEqual(main(["--root", str(root), "audit", "search", "--target", "knowledge/conflicts"]), 0)
            self.assertEqual(main(["--root", str(root), "metrics", "report", "--owner", "alice"]), 0)
            metrics_path = list((root / "knowledge" / "metrics").glob("*.md"))[0]
            metrics_text = metrics_path.read_text(encoding="utf-8")
            self.assertIn("startCount:", metrics_text)
            self.assertIn("approvedToolInvocations:", metrics_text)
            self.assertIn("agentRunSuccessCount:", metrics_text)
            self.assertEqual(main(["--root", str(root), "stale", "scan", "--owner", "alice"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "eval",
                        "case",
                        "create",
                        "--eval-id",
                        "eval.parser.basic",
                        "--title",
                        "Parser Basic Eval",
                        "--owner",
                        "alice",
                        "--target-ref",
                        "tools/tool.parser.md",
                        "--input",
                        "parse document",
                        "--expected",
                        "parsed",
                    ]
                ),
                0,
            )
            self.assertEqual(main(["--root", str(root), "eval", "run", "--eval-id", "eval.parser.basic", "--actual", "parsed document", "--runner", "alice"]), 0)
            self.assertTrue(list((root / "knowledge" / "eval-runs").glob("*.md")))
            self.assertEqual(main(["--root", str(root), "eval", "run", "--eval-id", "eval.parser.basic", "--actual", "failed output", "--runner", "alice"]), 0)
            self.assertTrue(list((root / "knowledge" / "engineering").glob("eval-failure-*.md")))
            self.assertEqual(main(["--root", str(root), "review", "update", "--target", "tools/tool.parser.md", "--status", "approved", "--reviewer", "alice"]), 2)
            self.assertEqual(main(["--root", str(root), "backup", "create"]), 0)
            backups = list((root / "backups").glob("*.zip"))
            self.assertTrue(backups)
            self.assertEqual(main(["--root", str(root), "backup", "restore", "--archive", str(backups[0]), "--overwrite"]), 0)
            self.assertEqual(main(["--root", str(root), "api", "export"]), 0)
            self.assertEqual(main(["--root", str(root), "gateway", "context", "--project", "core", "--agent", "agent.alice.builder", "--task", "gateway test"]), 0)
            self.assertEqual(main(["--root", str(root), "validate"]), 0)

    def test_finish_requires_current_context_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "init", "--user-id", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "agent", "register", "--agent-id", "agent.alice.builder", "--name", "Alice Builder", "--owner", "alice", "--purpose", "local development"]), 0)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "policy", "register", "--policy-id", "policy.alice", "--title", "Alice Policy", "--agent-id", "agent.alice.builder", "--owner", "alice", "--allow-project", "core", "--allow-scope", "engineering", "--allow-risk", "L1"]), 0)
            self.assertEqual(main(["--root", str(root), "review", "update", "--target", "knowledge/policies/policy.alice.md", "--status", "active", "--reviewer", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "finish", "--project", "core", "--agent", "agent.alice.builder", "--summary", "should fail"]), 2)

    def test_finish_no_reusable_lesson_skips_knowledge_draft_permission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "init", "--user-id", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "agent", "register", "--agent-id", "agent.alice.tester", "--name", "Alice Tester", "--owner", "alice", "--purpose", "test closeout"]), 0)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "start", "--project", "core", "--agent", "agent.alice.tester", "--task", "regression evidence"]), 0)

            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "finish",
                        "--project",
                        "core",
                        "--agent",
                        "agent.alice.tester",
                        "--summary",
                        "regression passed",
                        "--no-reusable-lesson",
                        "--no-tool-update",
                    ]
                ),
                0,
            )

            runs = list((root / "runs" / "core").glob("*.md"))
            self.assertEqual(len(runs), 1)
            self.assertIn("no reusable lesson", runs[0].read_text(encoding="utf-8"))
            self.assertFalse((root / "projects" / "core" / "lessons.draft.md").exists())
            self.assertTrue((root / "projects" / "core" / "project.update.draft.md").exists())

    def test_finish_reusable_lesson_requires_knowledge_draft_permission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "init", "--user-id", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "agent", "register", "--agent-id", "agent.alice.tester", "--name", "Alice Tester", "--owner", "alice", "--purpose", "test closeout"]), 0)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "start", "--project", "core", "--agent", "agent.alice.tester", "--task", "regression evidence"]), 0)

            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "finish",
                        "--project",
                        "core",
                        "--agent",
                        "agent.alice.tester",
                        "--summary",
                        "write reusable lesson",
                        "--no-tool-update",
                    ]
                ),
                2,
            )
            self.assertFalse(list((root / "runs" / "core").glob("*.md")))

    def test_eval_requires_all_declared_terms(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "agent", "register", "--agent-id", "agent.alice.builder", "--name", "Alice Builder", "--owner", "alice", "--purpose", "local development"]), 0)
            eval_dir = root / "knowledge" / "evals"
            eval_dir.mkdir(parents=True, exist_ok=True)
            (eval_dir / "eval.agent.workflow.md").write_text(
                """---
type: EvalCase
title: Agent workflow eval
description: Agent workflow must write traceable memory.
timestamp: 2026-06-17T00:00:00Z
evalId: eval.agent.workflow
owner: alice
status: verified
targetRef: agents/agent.alice.builder.md
expected: AgentRun
requires:
  - contextRefs
  - knowledgeUsed
  - sourceRef
---

## Input

Run start and finish.

## Expected

AgentRun with contextRefs, knowledgeUsed, and sourceRef.
""",
                encoding="utf-8",
            )
            self.assertEqual(main(["--root", str(root), "eval", "run", "--eval-id", "eval.agent.workflow", "--actual", "AgentRun contextRefs", "--runner", "alice"]), 0)
            eval_runs = sorted((root / "knowledge" / "eval-runs").glob("*.md"))
            self.assertIn("result: fail", eval_runs[-1].read_text(encoding="utf-8"))
            self.assertTrue(list((root / "knowledge" / "engineering").glob("eval-failure-*.md")))

    def test_stale_scan_marks_verified_tool_linked_knowledge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "init", "--user-id", "alice"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "tool",
                        "register",
                        "--tool-id",
                        "tool.parser",
                        "--name",
                        "Parser",
                        "--owner",
                        "alice",
                        "--repo",
                        "git@example.com:zhenzhi/parser.git",
                        "--entrypoint",
                        "cli://parser",
                    ]
                ),
                0,
            )
            knowledge_dir = root / "knowledge" / "engineering"
            knowledge_dir.mkdir(parents=True, exist_ok=True)
            item = knowledge_dir / "parser-lesson.md"
            item.write_text(
                """---
type: KnowledgeItem
title: Parser Lesson
description: Tool-linked lesson.
timestamp: 2026-06-16T00:00:00Z
owner: alice
status: verified
scope: engineering
sourceRef: tools/tool.parser.md
confidence: high
toolId: tool.parser
toolVersion: 0.0.1
---

## Knowledge

Use parser.
""",
                encoding="utf-8",
            )
            self.assertEqual(main(["--root", str(root), "stale", "scan", "--owner", "alice"]), 0)
            self.assertIn("status: stale_candidate", item.read_text(encoding="utf-8"))
            self.assertEqual(main(["--root", str(root), "review", "update", "--target", str(item), "--status", "stale", "--reviewer", "alice"]), 0)
            self.assertIn("status: stale", item.read_text(encoding="utf-8"))
            self.assertTrue(list((root / "knowledge" / "audit").glob("*.md")))

    def test_sync_failure_creates_conflict_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "init", "--user-id", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "sync", "pull"]), 2)
            self.assertTrue(list((root / "knowledge" / "conflicts").glob("*.md")))

    def test_http_api_and_gateway(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "init", "--user-id", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "agent", "register", "--agent-id", "agent.alice.builder", "--name", "Alice Builder", "--owner", "alice", "--purpose", "local development"]), 0)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "policy", "register", "--policy-id", "policy.alice", "--title", "Alice Policy", "--agent-id", "agent.alice.builder", "--owner", "alice", "--allow-project", "core", "--allow-scope", "engineering", "--allow-risk", "L1"]), 0)
            self.assertEqual(main(["--root", str(root), "review", "update", "--target", "knowledge/policies/policy.alice.md", "--status", "active", "--reviewer", "alice"]), 0)
            self.grant_agent_write_policy(root, "agent.codex.local")

            try:
                server = KnowledgeHTTPServer(("127.0.0.1", 0), Bundle(root), api_token="test-token")
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"
            previous_api = os.environ.get("ZHENZHI_KNOWLEDGE_API_STAGING")
            previous_token = os.environ.get("ZHENZHI_KNOWLEDGE_API_TOKEN_STAGING")
            previous_unsigned = os.environ.get("FEISHU_ALLOW_UNSIGNED_EVENTS")
            sent_messages: list[tuple[str, str]] = []
            original_send_message = feishu_module.send_feishu_message
            feishu_module.send_feishu_message = lambda _settings, open_id, text: sent_messages.append((open_id, text)) is None or True
            os.environ["ZHENZHI_KNOWLEDGE_API_STAGING"] = base
            os.environ["FEISHU_ALLOW_UNSIGNED_EVENTS"] = "true"
            try:
                def api_post(path: str, payload: dict) -> dict:
                    request = urllib.request.Request(
                        base + path,
                        data=json.dumps(payload).encode("utf-8"),
                        headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"},
                        method="POST",
                    )
                    return json.load(urllib.request.urlopen(request))

                health = json.load(urllib.request.urlopen(base + "/health"))
                self.assertTrue(health["ok"])
                feishu_verify = urllib.request.Request(
                    base + "/integrations/feishu/events",
                    data=json.dumps({"type": "url_verification", "challenge": "ok"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                self.assertEqual(json.load(urllib.request.urlopen(feishu_verify))["challenge"], "ok")
                feishu_message = urllib.request.Request(
                    base + "/integrations/feishu/events",
                    data=json.dumps(
                        {
                            "schema": "2.0",
                            "header": {"event_type": "im.message.receive_v1"},
                            "event": {
                                "sender": {"sender_id": {"open_id": "ou_alice", "user_id": "alice"}},
                                "message": {
                                    "message_id": "om_test",
                                    "chat_id": "oc_test",
                                    "chat_type": "group",
                                    "message_type": "text",
                                    "content": json.dumps({"text": "申请知识工程 token"}),
                                },
                            },
                        }
                    ).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                feishu_result = json.load(urllib.request.urlopen(feishu_message))
                self.assertTrue(feishu_result["ok"])
                self.assertFalse(feishu_result["sent"])
                self.assertIn("私聊", feishu_result["reply"])
                feishu_intake = urllib.request.Request(
                    base + "/integrations/feishu/events",
                    data=json.dumps(
                        {
                            "schema": "2.0",
                            "header": {"event_type": "im.message.receive_v1"},
                            "event": {
                                "sender": {"sender_id": {"open_id": "ou_alice", "user_id": "alice"}},
                                "message": {
                                    "message_id": "om_intake",
                                    "chat_id": "oc_test",
                                    "chat_type": "group",
                                    "message_type": "text",
                                    "content": json.dumps({"text": "沉淀：机器人应先生成 draft，再等待人工审核。"}),
                                },
                            },
                        }
                    ).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                intake_result = json.load(urllib.request.urlopen(feishu_intake))
                self.assertIn("KnowledgeItem", (root / "knowledge" / "engineering" / Path(intake_result["reply"].split("：", 1)[1].splitlines()[0]).name).read_text(encoding="utf-8"))
                feishu_material = urllib.request.Request(
                    base + "/integrations/feishu/events",
                    data=json.dumps(
                        {
                            "schema": "2.0",
                            "header": {"event_type": "im.message.receive_v1"},
                            "event": {
                                "sender": {"sender_id": {"open_id": "ou_alice", "user_id": "alice"}},
                                "message": {
                                    "message_id": "om_material",
                                    "chat_id": "oc_test",
                                    "chat_type": "group",
                                    "message_type": "text",
                                    "content": json.dumps({"text": "会议纪要：A项目\n今天确认先做机器人资料入口，原始资料保存为 SourceMaterial。"}),
                                },
                            },
                        }
                    ).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                material_result = json.load(urllib.request.urlopen(feishu_material))
                self.assertIn("原始资料", material_result["reply"])
                self.assertIn("任务编号", material_result["reply"])
                self.assertTrue(list((root / "projects" / "a" / "sources").glob("source.*.md")))
                material_tasks = list((root / "tasks").glob("kt-*.md")) + list((root / "projects" / "a" / "tasks").glob("kt-*.md"))
                self.assertTrue(material_tasks)
                material_task_text = material_tasks[0].read_text(encoding="utf-8")
                self.assertIn("type: KnowledgeTask", material_task_text)
                material_task_id = material_task_text.split("taskId:", 1)[1].splitlines()[0].strip()
                api_post(
                    "/v0/runners/register",
                    {
                        "runnerId": "runner.material",
                        "name": "Material StubRunner",
                        "hostType": "stub",
                        "agents": ["codex"],
                        "capabilities": ["knowledge_capture"],
                        "availableProjects": ["a"],
                    },
                )
                material_claim = api_post("/v0/tasks/claim", {"taskId": material_task_id, "runnerId": "runner.material"})
                material_context = api_post(
                    "/v0/tasks/pull",
                    {"taskId": material_task_id, "runnerId": "runner.material", "leaseToken": material_claim["leaseToken"]},
                )
                self.assertIn("SourceMaterial", material_context["context"])
                material_finish = api_post(
                    "/v0/tasks/finish",
                    {
                        "taskId": material_task_id,
                        "runnerId": "runner.material",
                        "leaseToken": material_claim["leaseToken"],
                        "executorAgent": "agent.codex.local",
                        "summary": "StubRunner completed Feishu SourceMaterial to KnowledgeTask flow.",
                        "evidenceRefs": [material_claim["task"]["sourceMaterialRefs"][0]],
                        "testsOrChecks": ["feishu material intake stub writeback"],
                        "knowledgeDraft": {
                            "title": "Agent Hub material intake lesson",
                            "summary": "机器人资料入口要先保存原文，再生成结构化草稿。",
                            "structured": "飞书资料入口必须先创建 SourceMaterial，保留原始文本；Runner 解析后才能提交 KnowledgeItem draft。",
                            "sourceRefs": [material_claim["task"]["sourceMaterialRefs"][0]],
                            "confidence": "high",
                            "scope": "engineering",
                            "limits": ["只适用于资料沉淀链路，不代表 verified 知识。"],
                        },
                    },
                )
                self.assertEqual(material_finish["task"]["status"], "done")
                draft_refs = material_finish["task"].get("resultRef", "")
                result_fm = load_object(root / draft_refs)
                self.assertTrue(result_fm["knowledgeRefs"])
                create_project_task(
                    Bundle(root),
                    "HTTP PRD handoff",
                    "core",
                    "alice",
                    "agent.company.product-manager",
                    task_type="product_requirement",
                    task_id="HTTP-ACCEPT-001",
                    expected_output=["Requirement brief and acceptance criteria."],
                )
                http_finish = api_post(
                    "/v0/tasks/finish",
                    {
                        "taskId": "HTTP-ACCEPT-001",
                        "summary": "需求已澄清，包含范围、用户场景、边界和验收标准。",
                        "outputRefs": ["projects/core/prd.md"],
                        "executorAgent": "agent.company.product-manager",
                        "evidenceRefs": ["projects/core/evidence.md"],
                        "handoffTo": "agent.company.design",
                        "nextSuggestedTask": "Create UX spec",
                    },
                )
                self.assertEqual(http_finish["task"]["status"], "waiting_acceptance")
                http_accept = api_post(
                    "/v0/task/accept",
                    {
                        "taskId": "HTTP-ACCEPT-001",
                        "decision": "accepted",
                        "reviewer": "alice",
                        "reason": "API 验收通过",
                        "human": True,
                    },
                )
                self.assertEqual(http_accept["taskStatus"], "done")
                self.assertTrue(http_accept["followupTaskRefs"])
                draft_path = root / result_fm["knowledgeRefs"][0]
                draft = load_object(draft_path)
                self.assertEqual(draft["type"], "KnowledgeItem")
                self.assertEqual(draft["status"], "draft")
                self.assertEqual(draft["sourceRef"], material_claim["task"]["sourceMaterialRefs"][0])
                self.assertEqual(draft["originalSourcePath"], material_claim["task"]["sourceMaterialRefs"][0])
                self.assertEqual(draft["taskResultRef"], material_finish["resultRef"])
                self.assertIn(str(draft_path.relative_to(root)), [item["path"] for item in list_review_queue(Bundle(root))])
                source_count = len(list((root / "projects" / "a" / "sources").glob("source.*.md")))
                task_paths = list((root / "tasks").glob("kt-*.md")) + list((root / "projects" / "a" / "tasks").glob("kt-*.md"))
                intake_task_count = len([path for path in task_paths if load_object(path).get("taskType") == "knowledge_capture"])
                duplicate_material = urllib.request.Request(
                    base + "/integrations/feishu/events",
                    data=json.dumps(
                        {
                            "schema": "2.0",
                            "header": {"event_type": "im.message.receive_v1"},
                            "event": {
                                "sender": {"sender_id": {"open_id": "ou_alice", "user_id": "alice"}},
                                "message": {
                                    "message_id": "om_material",
                                    "chat_id": "oc_test",
                                    "chat_type": "group",
                                    "message_type": "text",
                                    "content": json.dumps({"text": "会议纪要：A项目\n今天确认先做机器人资料入口，原始资料保存为 SourceMaterial。"}),
                                },
                            },
                        }
                    ).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                duplicate_material_result = json.load(urllib.request.urlopen(duplicate_material))
                self.assertTrue(duplicate_material_result["duplicate"])
                self.assertEqual(len(list((root / "projects" / "a" / "sources").glob("source.*.md"))), source_count)
                task_paths_after_duplicate = list((root / "tasks").glob("kt-*.md")) + list((root / "projects" / "a" / "tasks").glob("kt-*.md"))
                self.assertEqual(len([path for path in task_paths_after_duplicate if load_object(path).get("taskType") == "knowledge_capture"]), intake_task_count)
                review_list = urllib.request.Request(
                    base + "/integrations/feishu/events",
                    data=json.dumps(
                        {
                            "schema": "2.0",
                            "header": {"event_type": "im.message.receive_v1"},
                            "event": {
                                "sender": {"sender_id": {"open_id": "ou_reviewer", "user_id": "reviewer"}},
                                "message": {
                                    "message_id": "om_review_list",
                                    "chat_id": "oc_test",
                                    "chat_type": "group",
                                    "message_type": "text",
                                    "content": json.dumps({"text": "待审核"}),
                                },
                            },
                        }
                    ).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                self.assertIn("待审核队列", json.load(urllib.request.urlopen(review_list))["reply"])
                target = str(list((root / "knowledge" / "engineering").glob("feishu-intake.*.md"))[0].relative_to(root))
                review_approve = urllib.request.Request(
                    base + "/integrations/feishu/events",
                    data=json.dumps(
                        {
                            "schema": "2.0",
                            "header": {"event_type": "im.message.receive_v1"},
                            "event": {
                                "sender": {"sender_id": {"open_id": "ou_reviewer", "user_id": "reviewer"}},
                                "message": {
                                    "message_id": "om_review_approve",
                                    "chat_id": "oc_test",
                                    "chat_type": "group",
                                    "message_type": "text",
                                    "content": json.dumps({"text": f"通过 {target}"}),
                                },
                            },
                        }
                    ).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                approve_result = json.load(urllib.request.urlopen(review_approve))
                self.assertIn("状态: verified", approve_result["reply"])
                self.assertIn("status: verified", (root / target).read_text(encoding="utf-8"))
                callback_target = list((root / "knowledge" / "engineering").glob("feishu-intake.*.md"))[0]
                save_approval_request(
                    Bundle(root),
                    "approval_test",
                    {
                        "instanceCode": "approval_test",
                        "approvalCode": "approval_common",
                        "approvalType": "common",
                        "targetRef": str(callback_target.relative_to(root)),
                        "requestedStatus": "verified",
                        "projectId": "",
                        "submitterOpenId": "ou_alice",
                        "chatId": "oc_test",
                        "messageId": "om_intake",
                    },
                )
                approval_callback = urllib.request.Request(
                    base + "/integrations/feishu/events",
                    data=json.dumps(
                        {
                            "schema": "2.0",
                            "header": {"event_type": "approval.instance.updated_v4"},
                            "event": {"instance_code": "approval_test", "approval_code": "approval_common", "status": "APPROVED", "operator_id": {"open_id": "ou_reviewer"}},
                        }
                    ).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                callback_result = json.load(urllib.request.urlopen(approval_callback))
                self.assertEqual(callback_result["status"], "verified")
                self.assertIn("status: verified", callback_target.read_text(encoding="utf-8"))
                self.assertEqual(sent_messages[-1][0], "ou_alice")
                self.assertIn("已通过", sent_messages[-1][1])
                repeat_callback = json.load(urllib.request.urlopen(approval_callback))
                self.assertTrue(repeat_callback["idempotent"])
                save_approval_request(
                    Bundle(root),
                    "approval_bad",
                    {
                        "instanceCode": "approval_bad",
                        "approvalCode": "approval_common",
                        "approvalType": "common",
                        "targetRef": str(callback_target.relative_to(root)),
                        "requestedStatus": "verified",
                    },
                )
                bad_callback = urllib.request.Request(
                    base + "/integrations/feishu/events",
                    data=json.dumps(
                        {
                            "schema": "2.0",
                            "header": {"event_type": "approval.instance.updated_v4"},
                            "event": {"instance_code": "approval_bad", "approval_code": "wrong", "status": "APPROVED"},
                        }
                    ).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(urllib.error.HTTPError) as bad_approval:
                    urllib.request.urlopen(bad_callback)
                self.assertEqual(bad_approval.exception.code, 400)
                with self.assertRaises(urllib.error.HTTPError) as unauthorized:
                    urllib.request.urlopen(base + "/v0/snapshot")
                self.assertEqual(unauthorized.exception.code, 401)
                authorized_req = urllib.request.Request(base + "/v0/snapshot", headers={"Authorization": "Bearer test-token"})
                snapshot = json.load(urllib.request.urlopen(authorized_req))
                self.assertEqual(snapshot["kind"], "KnowledgeSnapshot")
                objects_req = urllib.request.Request(base + "/v0/objects?type=Project", headers={"Authorization": "Bearer test-token"})
                objects = json.load(urllib.request.urlopen(objects_req))
                self.assertEqual(objects["kind"], "ObjectList")
                req = urllib.request.Request(
                    base + "/v0/gateway/context",
                    data=json.dumps({"projectId": "core", "agentId": "agent.alice.builder", "task": "http test"}).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"},
                    method="POST",
                )
                context = json.load(urllib.request.urlopen(req))
                self.assertEqual(context["kind"], "GatewayContext")
                self.assertEqual(context["policyResult"]["policyCount"], 1)
                os.environ["ZHENZHI_KNOWLEDGE_API_TOKEN_STAGING"] = "test-token"
                self.assertEqual(main(["--root", str(root), "profile", "use", "staging"]), 0)
                self.assertEqual(main(["--root", str(root), "api", "export"]), 0)
                self.assertEqual(main(["--root", str(root), "index", "search", "--type", "Project"]), 0)
                self.assertEqual(main(["--root", str(root), "gateway", "context", "--project", "core", "--agent", "agent.alice.builder", "--task", "remote cli test"]), 0)
            finally:
                if previous_api is None:
                    os.environ.pop("ZHENZHI_KNOWLEDGE_API_STAGING", None)
                else:
                    os.environ["ZHENZHI_KNOWLEDGE_API_STAGING"] = previous_api
                if previous_token is None:
                    os.environ.pop("ZHENZHI_KNOWLEDGE_API_TOKEN_STAGING", None)
                else:
                    os.environ["ZHENZHI_KNOWLEDGE_API_TOKEN_STAGING"] = previous_token
                if previous_unsigned is None:
                    os.environ.pop("FEISHU_ALLOW_UNSIGNED_EVENTS", None)
                else:
                    os.environ["FEISHU_ALLOW_UNSIGNED_EVENTS"] = previous_unsigned
                feishu_module.send_feishu_message = original_send_message
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()

    def test_feishu_webhook_requires_verification_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            try:
                server = KnowledgeHTTPServer(("127.0.0.1", 0), Bundle(root), api_token="test-token")
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"
            previous_token = os.environ.get("FEISHU_VERIFICATION_TOKEN")
            previous_unsigned = os.environ.get("FEISHU_ALLOW_UNSIGNED_EVENTS")
            try:
                os.environ.pop("FEISHU_VERIFICATION_TOKEN", None)
                os.environ.pop("FEISHU_ALLOW_UNSIGNED_EVENTS", None)
                request = urllib.request.Request(
                    base + "/integrations/feishu/events",
                    data=json.dumps({"type": "url_verification", "challenge": "ok"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(urllib.error.HTTPError) as missing_token:
                    urllib.request.urlopen(request)
                self.assertEqual(missing_token.exception.code, 400)

                os.environ["FEISHU_VERIFICATION_TOKEN"] = "expected-token"
                bad_request = urllib.request.Request(
                    base + "/integrations/feishu/events",
                    data=json.dumps({"type": "url_verification", "challenge": "ok", "token": "wrong"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(urllib.error.HTTPError) as bad_token:
                    urllib.request.urlopen(bad_request)
                self.assertEqual(bad_token.exception.code, 400)

                good_request = urllib.request.Request(
                    base + "/integrations/feishu/events",
                    data=json.dumps({"type": "url_verification", "challenge": "ok", "token": "expected-token"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                self.assertEqual(json.load(urllib.request.urlopen(good_request))["challenge"], "ok")
            finally:
                if previous_token is None:
                    os.environ.pop("FEISHU_VERIFICATION_TOKEN", None)
                else:
                    os.environ["FEISHU_VERIFICATION_TOKEN"] = previous_token
                if previous_unsigned is None:
                    os.environ.pop("FEISHU_ALLOW_UNSIGNED_EVENTS", None)
                else:
                    os.environ["FEISHU_ALLOW_UNSIGNED_EVENTS"] = previous_unsigned
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()

    def test_token_approval_sends_secret_ref_only_to_submitter_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "knowledge-core", "--name", "知识工程中枢", "--owner", "meimei"]), 0)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=False,
                approval_code_project="",
                approval_code_common="",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=True,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="https://xcn68awb7dsi.feishu.cn",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            sent: list[tuple[str, str]] = []
            original_send = feishu_module.send_feishu_message
            previous_token = os.environ.get("ZHENZHI_KNOWLEDGE_API_TOKEN")
            os.environ["ZHENZHI_KNOWLEDGE_API_TOKEN"] = "prod-token"
            feishu_module.send_feishu_message = lambda _settings, open_id, text: sent.append((open_id, text)) is None or True
            try:
                result = feishu_module.handle_token_approval_result(
                    Bundle(root),
                    settings,
                    {"targetRef": "token-request:om_test", "submitterOpenId": "ou_alice"},
                    "ou_reviewer",
                    True,
                    "approval_token",
                )
                self.assertEqual(result["status"], "approved")
                self.assertEqual(sent[0][0], "ou_alice")
                self.assertIn("secretRef：secretref://zhenzhi/central_api/ou_alice", sent[0][1])
                self.assertNotIn("prod-token", sent[0][1])
                self.assertNotIn("export ZHENZHI_KNOWLEDGE_API_TOKEN_PROD", sent[0][1])
            finally:
                feishu_module.send_feishu_message = original_send
                if previous_token is None:
                    os.environ.pop("ZHENZHI_KNOWLEDGE_API_TOKEN", None)
                else:
                    os.environ["ZHENZHI_KNOWLEDGE_API_TOKEN"] = previous_token

    def test_feishu_private_credential_request_creates_secret_ref_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "knowledge-core", "--name", "知识工程中枢", "--owner", "meimei"]), 0)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=False,
                approval_code_project="",
                approval_code_common="",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            reply = feishu_module.build_reply(
                Bundle(root),
                {
                    "messageId": "om_credential",
                    "chatId": "ou_alice",
                    "chatType": "p2p",
                    "text": "申请知识工程 token：使用人 Alice，用途 本地开发，默认项目 Core，使用工具 Codex，凭证类型 DeepSeek模型",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                },
                settings,
            )
            self.assertIn("访问凭证申请", reply)
            request_files = [path for path in (root / "credential-requests").glob("*.md") if path.name != "index.md"]
            self.assertEqual(len(request_files), 1)
            request_text = request_files[0].read_text(encoding="utf-8")
            self.assertIn("type: AccessCredentialRequest", request_text)
            self.assertIn("credentialType: model_api", request_text)
            self.assertIn("purpose: 本地开发", request_text)
            self.assertNotIn("prod-token", request_text)
            self.assertNotIn("sk-", request_text)
            self.assertEqual(main(["--root", str(root), "validate"]), 0)

    def test_deepseek_router_payload_and_json_validation(self) -> None:
        payload = feishu_module.deepseek_router_payload(
            "我想申请 DeepSeek 凭证",
            {"chatType": "p2p"},
        )
        self.assertEqual(payload["model"], os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"))
        self.assertEqual(payload["temperature"], 0)
        valid = feishu_module.parse_router_decision(
            json.dumps(
                {
                    "intent": "credential_request",
                    "confidence": 0.91,
                    "risk": "L2",
                    "directHandle": True,
                    "taskType": "credential_request",
                    "requiredFields": {"credentialType": "model_api"},
                    "missingFields": [],
                    "toolSuggestions": ["credential_request"],
                }
            )
        )
        self.assertEqual(valid["intent"], "credential_request")
        with self.assertRaises(feishu_module.KnowledgeError):
            feishu_module.parse_router_decision("{bad json")
        with self.assertRaises(feishu_module.KnowledgeError):
            feishu_module.parse_router_decision(json.dumps({"intent": "delete_everything", "confidence": 1, "risk": "L3"}))

    def test_deepseek_router_eval_fixtures_cover_supported_intents(self) -> None:
        fixtures = [
            ("create_project", "L1", False, "project_init", {"projectName": "Agent Hub"}, []),
            ("knowledge_query", "L0", True, "none", {"question": "Agent Ring 是什么"}, []),
            ("capture_material", "L1", False, "knowledge_capture", {"projectName": "Agent Hub"}, []),
            ("credential_request", "L2", True, "credential_request", {"credentialType": "model_api"}, []),
            ("tool_or_skill_request", "L2", False, "tool_request", {"toolName": "Feishu Doc"}, []),
            ("summon_agent", "L1", True, "none", {"agentRole": "product-agent"}, []),
            ("status_query", "L0", True, "none", {"projectName": "Agent Hub"}, []),
            ("dangerous_request", "L3", False, "approval_task", {}, []),
            ("clarify", "L1", False, "", {}, ["项目名称"]),
        ]
        for intent, risk, direct, task_type, fields, missing in fixtures:
            with self.subTest(intent=intent):
                decision = feishu_module.parse_router_decision(
                    json.dumps(
                        {
                            "intent": intent,
                            "confidence": 0.9,
                            "risk": risk,
                            "directHandle": direct,
                            "taskType": task_type,
                            "requiredFields": fields,
                            "missingFields": missing,
                            "toolSuggestions": ["knowledge_search"] if intent == "knowledge_query" else [],
                        }
                    )
                )
                self.assertEqual(decision["intent"], intent)
                self.assertEqual(decision["risk"], risk)
                self.assertEqual(decision["directHandle"], direct)

    def test_skill_asset_registration_cli_and_feishu_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "skill",
                        "register",
                        "--skill-id",
                        "skill.reader.pdf",
                        "--name",
                        "PDF Reader Skill",
                        "--owner",
                        "agent.company.knowledge",
                        "--purpose",
                        "Extract structured evidence from PDF files.",
                        "--scope",
                        "company",
                        "--risk",
                        "L2",
                    ]
                ),
                0,
            )
            cli_skill = load_object(root / "skills" / "skill.reader.pdf.md")
            self.assertEqual(cli_skill["type"], "SkillAsset")
            self.assertEqual(cli_skill["version"], "0.1.0")
            self.assertEqual(cli_skill["rolloutState"], "draft")
            self.assertEqual(cli_skill["reusePolicy"], "review_required_before_company_reuse")

            reply = feishu_module.submit_tool_skill_card(
                Bundle(root),
                {"messageId": "om_skill_card", "openId": "ou_alice"},
                {
                    "assetType": "skill",
                    "name": "Feishu Doc Reader",
                    "owner": "agent.company.knowledge",
                    "scope": "project",
                    "projectName": "Agent Hub",
                    "risk": "L2",
                    "purpose": "Read Feishu docs and preserve citations.",
                    "io": "doc URL -> evidence packet",
                },
            )
            self.assertIn("技能资产申请草稿", reply)
            card_skill = load_object(root / "skills" / "skill.feishu-doc-reader.md")
            self.assertEqual(card_skill["type"], "SkillAsset")
            self.assertEqual(card_skill["scope"], "project")
            self.assertEqual(card_skill["projectId"], "agent-hub")
            self.assertEqual(card_skill["sourceRef"], "feishu://card/om_skill_card")
            self.assertIn("skill.register", audit_actions(root))

    def test_deepseek_router_mocked_credential_and_tool_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=False,
                approval_code_project="",
                approval_code_common="",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            original_router = feishu_module.call_deepseek_router
            try:
                feishu_module.call_deepseek_router = lambda _text, _incoming: {
                    "intent": "credential_request",
                    "confidence": 0.88,
                    "risk": "L2",
                    "directHandle": True,
                    "taskType": "credential_request",
                    "requiredFields": {"credentialType": "model_api"},
                    "missingFields": [],
                    "toolSuggestions": ["credential_request"],
                    "reason": "needs model key",
                }
                reply = feishu_module.build_reply(
                    Bundle(root),
                    {
                        "messageId": "om_router_credential",
                        "chatId": "ou_alice",
                        "chatType": "p2p",
                        "text": "我需要 DeepSeek 模型访问凭证",
                        "openId": "ou_alice",
                        "userId": "alice",
                        "mentionedOpenIds": "",
                    },
                    settings,
                )
                self.assertIn("访问凭证申请", reply)
                self.assertTrue([path for path in (root / "credential-requests").glob("*.md") if path.name != "index.md"])
                metric_logs = [
                    path.read_text(encoding="utf-8")
                    for path in (root / "knowledge" / "audit").glob("*.md")
                    if "feishu.router.metric" in path.read_text(encoding="utf-8")
                ]
                self.assertTrue(metric_logs)
                self.assertIn("model_router_observability", metric_logs[-1])
                self.assertIn('"fallback": false', metric_logs[-1])
                self.assertNotIn("我需要 DeepSeek 模型访问凭证", metric_logs[-1])

                feishu_module.call_deepseek_router = lambda _text, _incoming: {
                    "intent": "tool_or_skill_request",
                    "confidence": 0.92,
                    "risk": "L3",
                    "directHandle": True,
                    "taskType": "tool_call",
                    "requiredFields": {},
                    "missingFields": [],
                    "toolSuggestions": ["delete_all_data"],
                    "reason": "unsafe tool",
                }
                unsafe_reply = feishu_module.build_reply(
                    Bundle(root),
                    {
                        "messageId": "om_router_unsafe",
                        "chatId": "ou_alice",
                        "chatType": "p2p",
                        "text": "帮我调用一个内部超级工具处理一下",
                        "openId": "ou_alice",
                        "userId": "alice",
                        "mentionedOpenIds": "",
                    },
                    settings,
                )
                self.assertIn("未注册或高风险工具", unsafe_reply)
            finally:
                feishu_module.call_deepseek_router = original_router

    def test_deepseek_router_low_confidence_falls_back_to_local_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            reply = feishu_module.router_decision_reply(
                Bundle(root),
                {"messageId": "om_low", "text": "搞一下", "openId": "ou_alice"},
                feishu_module.load_feishu_settings(),
                {
                    "intent": "create_project",
                    "confidence": 0.2,
                    "risk": "L1",
                    "directHandle": False,
                    "taskType": "",
                    "requiredFields": {},
                    "missingFields": ["项目名称", "负责人"],
                    "toolSuggestions": [],
                    "reason": "too short",
                },
            )
            self.assertEqual(reply, "")
            self.assertFalse(list((root / "projects").glob("*/project.md")))

    def test_deepseek_router_status_query_uses_project_status_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "agent-hub", "--name", "Agent Hub", "--owner", "meimei"]), 0)
            reply = feishu_module.router_decision_reply(
                Bundle(root),
                {"messageId": "om_model_status", "text": "这个项目现在怎么样", "openId": "ou_alice"},
                feishu_module.load_feishu_settings(),
                {
                    "intent": "status_query",
                    "confidence": 0.91,
                    "risk": "L0",
                    "directHandle": True,
                    "taskType": "none",
                    "requiredFields": {"projectName": "Agent Hub"},
                    "missingFields": [],
                    "toolSuggestions": [],
                    "reason": "project status query",
                },
            )
            self.assertIn("项目：Agent Hub", reply)
            self.assertIn("当前状态：草稿", reply)

    def test_deepseek_router_failure_records_metric_and_falls_back(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            original_router = feishu_module.call_deepseek_router
            try:
                feishu_module.call_deepseek_router = lambda _text, _incoming: (_ for _ in ()).throw(feishu_module.KnowledgeError("invalid router JSON"))
                reply = feishu_module.deepseek_router_reply(
                    Bundle(root),
                    {"messageId": "om_router_fail", "chatType": "p2p", "text": "删掉所有知识库", "openId": "ou_alice"},
                    feishu_module.load_feishu_settings(),
                )
                self.assertEqual(reply, "")
                audit_text = "\n".join(path.read_text(encoding="utf-8") for path in (root / "knowledge" / "audit").glob("*.md"))
                self.assertIn("feishu.router.metric", audit_text)
                self.assertIn('"fallback": true', audit_text)
                self.assertIn('"errorClass": "KnowledgeError"', audit_text)
                self.assertNotIn("删掉所有知识库", audit_text)
            finally:
                feishu_module.call_deepseek_router = original_router

    def test_project_owner_onboarding_uses_project_name_not_required_project_id(self) -> None:
        message = feishu_module.project_owner_onboarding_message(
            {"projectName": "桢知 Agent Hub", "projectId": "zhenzhi-agent-hub"},
            "approval_1",
            "verified",
        )
        self.assertIn("会议纪要：项目 桢知 Agent Hub", message)
        self.assertIn("资料：项目 桢知 Agent Hub", message)
        self.assertIn("状态：已立项", message)
        self.assertIn("后续如何给这个项目补充资料", message)
        self.assertNotIn("状态：verified", message)
        self.assertNotIn("\\n<内容>", message)
        self.assertNotIn("会议纪要：zhenzhi-agent-hub", message)
        self.assertNotIn("资料：zhenzhi-agent-hub", message)

    def test_feishu_menu_shortcuts_have_actionable_project_name_flows(self) -> None:
        incoming = {"chatType": "p2p"}
        shortcuts = {
            "创建项目": "项目启动卡",
            "已有仓库": "已有仓库接入",
            "新建仓库": "从头创建新项目",
            "召唤 Agent": "Agent team 编组卡",
            "查知识": "知识检索卡",
            "记录知识": "知识沉淀卡",
            "会议纪要": "会议纪要沉淀卡",
            "申请工具/技能": "工具/技能申请卡",
            "绑定项目群": "项目群",
            "项目交接": "项目交接卡",
        }
        for text, expected in shortcuts.items():
            with self.subTest(text=text):
                reply = feishu_module.handle_menu_shortcut(incoming, text)
                self.assertIn(expected, reply)
                self.assertTrue("请" in reply or "后续" in reply or "安全边界" in reply)
        self.assertIn("项目 <项目名称>", feishu_module.knowledge_search_entry_text())
        self.assertIn("项目 <项目名称>", feishu_module.knowledge_capture_entry_text())
        self.assertIn("项目 <项目名称>", feishu_module.meeting_notes_entry_text())
        self.assertNotIn("<项目ID>", feishu_module.knowledge_search_entry_text())

    def test_legacy_token_shortcut_is_deemphasized_not_menu_first(self) -> None:
        reply = feishu_module.handle_menu_shortcut({"chatType": "p2p"}, "申请 token")
        self.assertIn("已升级为访问凭证 / Agent Ring 接入申请", reply)
        self.assertIn("不建议放在一级菜单", reply)
        self.assertIn("默认项目 <项目名称>", reply)
        self.assertNotIn("<项目ID>", reply)

    def test_feishu_approval_form_uses_knowledge_template_widgets(self) -> None:
        form = feishu_module.approval_form(
            {
                "approval_type": "knowledge_ingest",
                "object_path": "knowledge/engineering/example.md",
                "project_id": "core",
                "project_name": "Core",
                "owner_open_id": "ou_owner",
                "requested_status": "verified",
                "submitter": "ou_submitter",
                "summary": "knowledge draft",
            }
        )
        by_id = {item["id"]: item for item in form}
        self.assertEqual(by_id["widget17816810502430001"]["type"], "radioV2")
        self.assertEqual(by_id["widget17816810502430001"]["value"], "mqhqw8sk-kybdohz4afi-0")
        self.assertEqual(by_id["widget17816812084890001"]["value"], "Core")
        self.assertEqual(by_id["widget17816816166430001"]["value"], ["ou_owner"])
        self.assertEqual(by_id["widget17816813081730001"]["value"], ["ou_submitter"])
        self.assertEqual(by_id["widget17816813651240001"]["type"], "document")

    def test_feishu_approval_doc_uses_human_readable_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            project = root / "projects" / "industrial-dispenser" / "project.md"
            project.parent.mkdir(parents=True, exist_ok=True)
            project.write_text("---\ntype: Project\nstatus: draft\n---\n\nproject draft\n", encoding="utf-8")
            markdown = feishu_module.build_approval_change_markdown(
                Bundle(root),
                {
                    "approval_type": "project_init",
                    "approval_type_label": "项目立项",
                    "object_path": str(project.relative_to(root)),
                    "project_id": "industrial-dispenser",
                    "project_name": "工业软件点胶机",
                    "submitter": "e5dg86b5",
                    "submitter_name": "梅晓华",
                    "owner_open_id": "f4e3ge64",
                    "owner_name": "沈英俊",
                    "requested_status": "verified",
                    "requested_status_label": "审核通过，进入可复用状态",
                    "summary": "项目立项申请：工业软件点胶机",
                },
                "项目立项审批说明-工业软件点胶机-doc.test",
            )
            self.assertIn("提交人：梅晓华", markdown)
            self.assertIn("项目负责人：沈英俊", markdown)
            self.assertIn("审批事项：项目立项", markdown)
            self.assertNotIn("提交人：e5dg86b5", markdown)

    def test_feishu_project_init_creates_project_and_approval_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=["ou_common"],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="https://xcn68awb7dsi.feishu.cn",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            created: dict[str, object] = {}
            original_create = feishu_module.create_feishu_approval_instance
            def fake_create_approval(_settings, requester_user_id, approval_code, approver_user_ids, form_values):
                created.update(
                    {
                        "requester": requester_user_id,
                        "approval_code": approval_code,
                        "approvers": approver_user_ids,
                        "form_values": form_values,
                    }
                )
                return "approval_project_instance"

            feishu_module.create_feishu_approval_instance = fake_create_approval
            try:
                reply = feishu_module.build_reply(
                    Bundle(root),
                    {
                        "messageId": "om_project",
                        "chatId": "oc_test",
                        "chatType": "group",
                        "text": "立项申请：项目名称 A项目，项目负责人 @Alice",
                        "openId": "ou_submitter",
                        "userId": "submitter",
                        "mentionedOpenIds": "ou_owner",
                    },
                    settings,
                )
                self.assertIn("项目草稿已创建", reply)
                self.assertTrue((root / "projects" / "a" / "project.md").exists())
                self.assertEqual(created["approval_code"], "approval_project")
                self.assertEqual(created["approvers"], ["ou_common"])
                self.assertEqual(created["form_values"]["approval_type"], "project_init")
                self.assertEqual(created["form_values"]["owner_open_id"], "ou_owner")
            finally:
                feishu_module.create_feishu_approval_instance = original_create

    def test_feishu_project_init_ensures_approval_event_subscription(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="cli_app",
                app_secret="cli_secret",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=["ou_common"],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="https://xcn68awb7dsi.feishu.cn",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            subscribed: list[str] = []
            original_create = feishu_module.create_feishu_approval_instance
            original_subscribe = feishu_module.subscribe_feishu_approval_events
            feishu_module.create_feishu_approval_instance = lambda *_args, **_kwargs: "approval_project_instance"
            feishu_module.subscribe_feishu_approval_events = lambda _settings, approval_code: subscribed.append(approval_code)
            try:
                reply = feishu_module.build_reply(
                    Bundle(root),
                    {
                        "messageId": "om_project",
                        "chatId": "oc_test",
                        "chatType": "group",
                        "text": "立项申请：项目名称 A项目，项目负责人 @Alice",
                        "openId": "ou_submitter",
                        "userId": "submitter",
                        "mentionedOpenIds": "ou_owner",
                    },
                    settings,
                )
            finally:
                feishu_module.create_feishu_approval_instance = original_create
                feishu_module.subscribe_feishu_approval_events = original_subscribe
            self.assertIn("已发起飞书审批", reply)
            self.assertEqual(subscribed, ["approval_project"])
            request_files = list((root / ".zhenzhi" / "approval-requests").glob("*.json"))
            self.assertEqual(len(request_files), 1)
            request = json.loads(request_files[0].read_text(encoding="utf-8"))
            self.assertEqual(request["eventSubscriptionStatus"], "subscribed")

    def test_feishu_approval_instance_detail_uses_official_instance_endpoint(self) -> None:
        settings = feishu_module.FeishuSettings(
            app_id="cli_app",
            app_secret="cli_secret",
            verification_token="",
            reply_enabled=False,
            token_auto_approve=False,
            approval_enabled=True,
            approval_code_project="",
            approval_code_common="",
            approval_code_security="",
            approval_node_approver_key="",
            common_reviewer_open_ids=[],
            security_reviewer_open_ids=[],
            project_reviewer_open_ids={},
            token_send_on_approval=False,
            approval_doc_folder_token="",
            approval_doc_folder_tokens={},
            approval_doc_domain="",
            approval_doc_share_names=[],
            user_open_id_map={},
        )
        calls: list[tuple[str, str]] = []
        original_token = feishu_module.get_tenant_access_token
        original_request = feishu_module.feishu_json_request
        feishu_module.get_tenant_access_token = lambda _settings: "tenant_token"
        feishu_module.feishu_json_request = lambda method, url, token, body=None: calls.append((method, url)) or {"data": {"status": "APPROVED"}}
        try:
            detail = feishu_module.feishu_approval_instance_detail(settings, "A7F76814-0A5A")
        finally:
            feishu_module.get_tenant_access_token = original_token
            feishu_module.feishu_json_request = original_request
        self.assertEqual(detail["status"], "APPROVED")
        self.assertEqual(calls[0][0], "GET")
        self.assertIn("/approval/v4/instances/A7F76814-0A5A?", calls[0][1])
        self.assertNotIn("/instances/detail", calls[0][1])

    def test_feishu_project_init_reuses_pending_project_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=["ou_common"],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            created: list[str] = []
            original_create = feishu_module.create_feishu_approval_instance
            feishu_module.create_feishu_approval_instance = lambda *_args, **_kwargs: created.append("approval_once") or "approval_once"
            incoming = {
                "messageId": "om_project",
                "chatId": "oc_test",
                "chatType": "group",
                "text": "立项申请：项目名称 A项目，项目负责人 @Alice",
                "openId": "ou_submitter",
                "userId": "submitter",
                "mentionedOpenIds": "ou_owner",
            }
            try:
                first = feishu_module.build_reply(Bundle(root), incoming, settings)
                second = feishu_module.build_reply(Bundle(root), {**incoming, "messageId": "om_project_retry"}, settings)
            finally:
                feishu_module.create_feishu_approval_instance = original_create
            self.assertIn("已发起飞书审批：approval_once", first)
            self.assertIn("项目草稿已存在", second)
            self.assertEqual(created, ["approval_once"])

    def test_feishu_project_init_creates_launch_plan_for_existing_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=["ou_common"],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={"梅晓华": "ou_owner"},
            )
            original_create = feishu_module.create_feishu_approval_instance
            feishu_module.create_feishu_approval_instance = lambda *_args, **_kwargs: "approval_existing_repo"
            try:
                reply = feishu_module.build_reply(
                    Bundle(root),
                    {
                        "messageId": "om_project_existing_repo",
                        "chatId": "ou_submitter",
                        "chatType": "p2p",
                        "text": "创建项目：项目名称 GEO增长，项目负责人 梅晓华，已有仓库 https://github.com/company/geo.git，项目目标 提升GEO效率，需要Agent 产品/后端/知识工程，创建项目群 是",
                        "openId": "ou_submitter",
                        "userId": "submitter",
                        "mentionedOpenIds": "",
                    },
                    settings,
                )
            finally:
                feishu_module.create_feishu_approval_instance = original_create
            launch_path = root / "projects" / "geo" / "launch.md"
            self.assertTrue(launch_path.exists())
            launch = launch_path.read_text(encoding="utf-8")
            self.assertIn("type: Workflow", launch)
            self.assertIn("status: draft", launch)
            self.assertIn("repoMode: existing", launch)
            self.assertIn("https://github.com/company/geo.git", launch)
            self.assertIn("项目启动卡摘要", reply)
            self.assertIn("审批通过后的执行顺序", reply)

    def test_feishu_project_create_card_submit_creates_project_launch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=["ou_common"],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={"梅晓华": "ou_owner"},
            )
            original_create = feishu_module.create_feishu_approval_instance
            feishu_module.create_feishu_approval_instance = lambda *_args, **_kwargs: "approval_card_project"
            try:
                result = feishu_module.handle_feishu_event(
                    Bundle(root),
                    {
                        "schema": "2.0",
                        "header": {"event_type": "card.action.trigger", "token": "expected-token"},
                        "event": {
                            "operator": {"operator_id": {"open_id": "ou_submitter", "user_id": "submitter"}},
                            "context": {"open_message_id": "om_card_project", "open_chat_id": "oc_card"},
                            "action": {
                                "value": {"action": "project_create_submit"},
                                "form_value": {
                                    "projectName": "桢知 Agent Hub 与知识工程中枢",
                                    "projectOwner": "梅晓华",
                                    "leadAgent": "知识工程项目经理 Agent",
                                    "defaultRunner": "runner.mac-mini",
                                    "repoMode": "existing",
                                    "repoUrl": "https://github.com/company/company_knowledge_core.git",
                                    "goal": "建设公司 Agent 团队入口、中央调度器和知识工程底座",
                                    "agents": "产品/后端/知识工程/测试/运维",
                                    "createGroup": "是",
                                },
                            },
                        },
                    },
                    settings,
                )
            finally:
                feishu_module.create_feishu_approval_instance = original_create
            self.assertEqual(set(result.keys()), {"toast", "card"})
            self.assertIn("这张卡片已锁定", json.dumps(result["card"]["data"], ensure_ascii=False))
            self.assertIn("项目草稿已创建", result["toast"]["content"])
            launch = (root / "projects" / "agent-hub" / "launch.md").read_text(encoding="utf-8")
            self.assertIn("leadAgent: 知识工程项目经理 Agent", launch)
            self.assertIn("defaultRunner: runner.mac-mini", launch)
            self.assertIn("https://github.com/company/company_knowledge_core.git", launch)
            self.assertIn("Startup Milestones", launch)
            self.assertIn("M0 Intake Complete", launch)
            self.assertIn("M3 First Work Queue", launch)
            self.assertIn("Business or product milestones are not guessed", launch)
            self.assertIn("Default Agent Team", launch)
            self.assertIn("Requested frontend, backend, test, ops, or domain roles become candidate Agents", launch)
            self.assertIn("Product Manager Agent: agent.agent-hub.product-manager", launch)
            self.assertIn("Product Manager decision:", launch)
            self.assertIn("included:", launch)
            self.assertIn("Product requirement clarification becomes a first ProjectTask", launch)
            self.assertIn("Flow Entry", launch)
            task = (root / "projects" / "agent-hub" / "tasks" / "project-init-agent-hub.md").read_text(encoding="utf-8")
            self.assertIn("taskType: project_initialization", task)
            self.assertIn("status: waiting_runner", task)
            self.assertIn("assignee: agent.agent-hub.project-manager", task)
            self.assertIn("assignedRunner: runner.mac-mini", task)
            self.assertIn("knowledge_sync", task)
            self.assertIn("启动闭环验收", task)
            self.assertIn("业务/产品里程碑", task)
            self.assertIn("Product Manager Agent", task)
            self.assertIn("记录跳过原因", task)
            self.assertIn("tool.zhenzhi-knowledge", task)
            self.assertIn("Agent Ring runner registry", task)
            self.assertIn("Git 只读检查", task)
            self.assertIn("pass、blocked、needs_human_approval 或 needs_repair", task)
            self.assertIn("TaskResult", task)
            self.assertIn("AgentRun", task)
            project = (root / "projects" / "agent-hub" / "project.md").read_text(encoding="utf-8")
            self.assertIn("agent.agent-hub.project-manager", project)
            self.assertIn("agent.agent-hub.product-manager", project)
            self.assertTrue((root / "agents" / "agent.agent-hub.knowledge-engineering.md").exists())
            self.assertTrue((root / "agents" / "agent.agent-hub.product-manager.md").exists())
            project_agent = (root / "agents" / "agent.agent-hub.project-manager.md").read_text(encoding="utf-8")
            project_agent_fm = load_object(root / "agents" / "agent.agent-hub.project-manager.md")
            self.assertIn("tool.zhenzhi-knowledge", project_agent_fm["allowedTools"])
            self.assertIn("allowedProjects:", project_agent)
            self.assertIn("- agent-hub", project_agent)
            self.assertIn("project_initialization", project_agent)
            self.assertIn("项目初始化闭环负责人", project_agent)
            self.assertIn("Required Tools", project_agent)
            self.assertIn("Initialization Workflow", project_agent)
            self.assertIn("Completion Criteria", project_agent)
            self.assertIn("Evaluation", project_agent)
            self.assertIn("Agent Ring runner registry", project_agent)
            self.assertIn("Git/repository inspection", project_agent)
            self.assertIn("Feishu project group", project_agent)
            self.assertIn("needs_human_approval", project_agent)
            self.assertIn("After Initialization Handoff", project_agent)
            self.assertIn("Operating Cadence", project_agent)
            self.assertIn("Progress Control", project_agent)
            self.assertIn("Risk Radar", project_agent)
            self.assertIn("Alert And Escalation", project_agent)
            self.assertIn("Status Report Format", project_agent)
            self.assertIn("on_track, at_risk, blocked, or needs_decision", project_agent)
            self.assertIn("Runner lease/heartbeat", project_agent)
            product_agent = (root / "agents" / "agent.agent-hub.product-manager.md").read_text(encoding="utf-8")
            self.assertIn("product_discovery", product_agent)
            self.assertIn("requirement_clarification", product_agent)
            self.assertIn("Closed Loop Acceptance", launch)

    def test_feishu_project_create_skips_product_agent_when_requirements_clear(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=["ou_common"],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={"梅晓华": "ou_owner"},
            )
            original_create = feishu_module.create_feishu_approval_instance
            feishu_module.create_feishu_approval_instance = lambda *_args, **_kwargs: "approval_tech_migration"
            try:
                result = feishu_module.handle_feishu_event(
                    Bundle(root),
                    {
                        "schema": "2.0",
                        "header": {"event_type": "card.action.trigger", "token": "expected-token"},
                        "event": {
                            "operator": {"operator_id": {"open_id": "ou_submitter", "user_id": "submitter"}},
                            "context": {"open_message_id": "om_card_project_tech", "open_chat_id": "oc_card"},
                            "action": {
                                "value": {"action": "project_create_submit"},
                                "form_value": {
                                    "projectName": "Tech Migration",
                                    "projectOwner": "梅晓华",
                                    "repoMode": "existing",
                                    "repoUrl": "https://github.com/company/tech-migration.git",
                                    "goal": "需求已明确，仅技术迁移和仓库初始化",
                                    "agents": "后端/运维",
                                    "createGroup": "否",
                                },
                            },
                        },
                    },
                    settings,
                )
            finally:
                feishu_module.create_feishu_approval_instance = original_create
            self.assertEqual(set(result.keys()), {"toast", "card"})
            self.assertIn("这张卡片已锁定", json.dumps(result["card"]["data"], ensure_ascii=False))
            launch = (root / "projects" / "tech-migration" / "launch.md").read_text(encoding="utf-8")
            self.assertIn("Product Manager decision:", launch)
            self.assertIn("skipped: intake says product work is already clear or not needed", launch)
            self.assertFalse((root / "agents" / "agent.tech-migration.product-manager.md").exists())

    def test_feishu_project_create_submit_returns_immediately_when_replies_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="expected-token",
                reply_enabled=True,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=["ou_common"],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={"梅晓华": "ou_owner"},
            )
            queued_jobs = []
            original_start = feishu_module.start_card_submit_job
            feishu_module.start_card_submit_job = lambda _bundle, incoming, _settings, form, action_name, actor, job_path: queued_jobs.append(
                {
                    "messageId": incoming["messageId"],
                    "form": form,
                    "actionName": action_name,
                    "actor": actor,
                    "jobPath": job_path,
                }
            )
            try:
                payload = {
                    "schema": "2.0",
                    "header": {"event_type": "card.action.trigger", "token": "expected-token"},
                    "event": {
                        "operator": {"operator_id": {"open_id": "ou_submitter", "user_id": "submitter"}},
                        "context": {"open_message_id": "om_async_project", "open_chat_id": "oc_card"},
                        "action": {
                            "name": "project_create_submit|repoMode=existing",
                            "value": {},
                            "form_value": {
                                "projectName": "桢知 Agent Hub 与知识工程中枢",
                                "projectOwner": "梅晓华",
                                "repoUrl": "https://github.com/company/company_knowledge_core.git",
                            },
                        },
                    },
                }
                result = feishu_module.handle_feishu_event(
                    Bundle(root),
                    payload,
                    settings,
                )
                duplicate_result = feishu_module.handle_feishu_event(Bundle(root), payload, settings)
            finally:
                feishu_module.start_card_submit_job = original_start
            self.assertEqual(set(result.keys()), {"toast", "card"})
            self.assertIn("后台处理", result["toast"]["content"])
            card_json = json.dumps(result["card"]["data"], ensure_ascii=False)
            self.assertIn("已提交，处理中", card_json)
            self.assertIn("这张卡片已锁定", card_json)
            self.assertNotIn('"tag": "form"', card_json)
            self.assertNotIn('"tag": "input"', card_json)
            self.assertNotIn('"tag": "select_static"', card_json)
            self.assertEqual(set(duplicate_result.keys()), {"toast", "card"})
            duplicate_card_json = json.dumps(duplicate_result["card"]["data"], ensure_ascii=False)
            self.assertIn("已提交，请勿重复操作", duplicate_card_json)
            self.assertNotIn('"tag": "form"', duplicate_card_json)
            self.assertEqual(len(queued_jobs), 1)
            self.assertEqual(queued_jobs[0]["actionName"], "project_create_submit")
            self.assertEqual(queued_jobs[0]["form"]["repoMode"], "existing")
            self.assertFalse((root / "projects" / "agent-hub" / "launch.md").exists())
            job_records = list((root / ".zhenzhi" / "feishu-card-jobs").glob("*.json"))
            self.assertEqual(len(job_records), 1)

    def test_feishu_help_uses_agent_hub_in_private_chat(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=False,
                approval_code_project="",
                approval_code_common="",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            reply = feishu_module.build_reply(
                Bundle(root),
                {
                    "messageId": "om_agent_hub_help",
                    "chatId": "ou_alice",
                    "chatType": "p2p",
                    "text": "帮助",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                },
                settings,
            )
            self.assertIn("桢知 Agent Hub", reply)
            self.assertIn("创建项目", reply)
            self.assertIn("组建 Agent 团队", reply)
            self.assertIn("完整说明", reply)

    def test_feishu_help_uses_project_assistant_in_group_chat(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=False,
                approval_code_project="",
                approval_code_common="",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            reply = feishu_module.build_reply(
                Bundle(root),
                {
                    "messageId": "om_project_assistant_help",
                    "chatId": "oc_project",
                    "chatType": "group",
                    "text": "帮助",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                },
                settings,
            )
            self.assertIn("项目助手", reply)
            self.assertIn("绑定项目群", reply)
            self.assertIn("请产品 Agent", reply)
            self.assertIn("完整说明", reply)
            self.assertIn("安全边界", reply)

    def test_agent_hub_user_guide_documents_unified_menu_and_safety(self) -> None:
        guide = (REPO_ROOT / "docs/guides/agent-hub-user-guide.md").read_text(encoding="utf-8")
        workflow = (REPO_ROOT / "docs/agent-team/agent-hub-product-workflows.md").read_text(encoding="utf-8")
        protocol = (REPO_ROOT / "docs/protocols/agent-ring-communication-protocol.md").read_text(encoding="utf-8")
        self.assertIn("桢知 Agent Hub 是公司项目入口、中央调度器入口和知识沉淀入口", guide)
        self.assertIn("飞书自定义菜单不能按私聊和群聊分别配置", guide)
        self.assertIn("中央调度器会把任务分配给具备能力和权限的 Agent Ring Runner", guide)
        self.assertIn("已有仓库接入", guide)
        self.assertIn("从头创建新项目", guide)
        self.assertIn("菜单地图", guide)
        self.assertIn("安全边界", guide)
        self.assertIn("Agent Ring 是外部 Agent 工作台", guide)
        self.assertIn("This repository does not implement Agent Ring", protocol)
        self.assertIn("flowchart", guide)
        self.assertIn("Creating a project means starting a real project", workflow)
        self.assertIn("repoMode", workflow)

    def test_feishu_menu_shortcuts_return_guided_next_steps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=False,
                approval_code_project="",
                approval_code_common="",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            reply = feishu_module.build_reply(
                Bundle(root),
                {
                    "messageId": "om_menu_create_project",
                    "chatId": "ou_alice",
                    "chatType": "p2p",
                    "text": "创建项目",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                },
                settings,
            )
            self.assertIn("创建项目草稿", reply)
            self.assertIn("项目 Owner", reply)
            group_reply = feishu_module.build_reply(
                Bundle(root),
                {
                    "messageId": "om_menu_bind_group",
                    "chatId": "oc_project",
                    "chatType": "group",
                    "text": "绑定项目群",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                },
                settings,
            )
            self.assertIn("绑定项目群", group_reply)
            self.assertIn("项目助手", group_reply)

    def test_feishu_project_menu_uses_interactive_card_in_real_response(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            response = feishu_module.build_feishu_response(
                Bundle(root),
                {
                    "messageId": "om_menu_create_project_card",
                    "chatId": "ou_alice",
                    "chatType": "p2p",
                    "text": "创建项目",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                },
                feishu_module.load_feishu_settings(),
            )
            self.assertEqual(response["msg_type"], "interactive")
            card_text = json.dumps(response["card"], ensure_ascii=False)
            self.assertIn("已有仓库接入/老项目迁移", card_text)
            self.assertIn("从头创建新项目", card_text)
            self.assertIn("project_create_mode", card_text)
            self.assertNotIn("默认 Runner", card_text)

            direct = feishu_module.build_feishu_response(
                Bundle(root),
                {
                    "messageId": "om_danger_text",
                    "chatId": "ou_alice",
                    "chatType": "p2p",
                    "text": "删除知识库",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                },
                feishu_module.load_feishu_settings(),
            )
            self.assertEqual(direct["msg_type"], "text")
            self.assertIn("高风险操作", direct["reply"])

            agent_team = feishu_module.build_feishu_response(
                Bundle(root),
                {
                    "messageId": "om_agent_team_card",
                    "chatId": "ou_alice",
                    "chatType": "p2p",
                    "text": "组建 Agent 团队",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                },
                feishu_module.load_feishu_settings(),
            )
            self.assertEqual(agent_team["msg_type"], "interactive")
            self.assertIn("agent_team_submit", json.dumps(agent_team["card"], ensure_ascii=False))

            group_bind = feishu_module.build_feishu_response(
                Bundle(root),
                {
                    "messageId": "om_bind_group_card",
                    "chatId": "oc_project",
                    "chatType": "group",
                    "text": "绑定项目群",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                },
                feishu_module.load_feishu_settings(),
            )
            self.assertEqual(group_bind["msg_type"], "interactive")
            self.assertIn("bind_project_group_submit", json.dumps(group_bind["card"], ensure_ascii=False))

            private_bind = feishu_module.build_feishu_response(
                Bundle(root),
                {
                    "messageId": "om_bind_group_private",
                    "chatId": "ou_alice",
                    "chatType": "p2p",
                    "text": "绑定项目群",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                },
                feishu_module.load_feishu_settings(),
            )
            self.assertEqual(private_bind["msg_type"], "text")
            self.assertIn("目标项目群里操作", private_bind["reply"])

    def test_feishu_structured_cards_submit_to_matching_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "knowledge-core", "--name", "知识工程中枢", "--owner", "meimei"]), 0)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=False,
                approval_code_project="",
                approval_code_common="",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            result = feishu_module.handle_feishu_event(
                Bundle(root),
                {
                    "schema": "2.0",
                    "header": {"event_type": "card.action.trigger", "token": "expected-token"},
                    "event": {
                        "operator": {"operator_id": {"open_id": "ou_submitter", "user_id": "submitter"}},
                        "context": {"open_message_id": "om_agent_team", "open_chat_id": "oc_project"},
                        "action": {
                            "value": {"action": "agent_team_submit"},
                            "form_value": {
                                "projectName": "知识工程中枢",
                                "stage": "需求",
                                "goal": "梳理中央调度器和 Agent Ring 协议",
                                "expectedOutput": "方案和任务清单",
                            },
                        },
                    },
                },
                settings,
            )
            self.assertEqual(set(result.keys()), {"toast", "card"})
            self.assertIn("已收到 Agent 编组需求", result["toast"]["content"])
            card_json = json.dumps(result["card"]["data"], ensure_ascii=False)
            self.assertIn("已提交", card_json)
            self.assertIn("这张卡片已锁定", card_json)
            self.assertNotIn('"tag": "form"', card_json)

            bind_result = feishu_module.handle_feishu_event(
                Bundle(root),
                {
                    "schema": "2.0",
                    "header": {"event_type": "card.action.trigger", "token": "expected-token"},
                    "event": {
                        "operator": {"operator_id": {"open_id": "ou_submitter", "user_id": "submitter"}},
                        "context": {"open_message_id": "om_bind_project", "open_chat_id": "oc_project"},
                        "action": {
                            "value": {"action": "bind_project_group_submit"},
                            "form_value": {"projectName": "知识工程中枢", "ownerConfirmed": "是"},
                        },
                    },
                },
                settings,
            )
            self.assertEqual(set(bind_result.keys()), {"toast", "card"})
            self.assertIn("已绑定项目群", bind_result["toast"]["content"])
            bind_card_json = json.dumps(bind_result["card"]["data"], ensure_ascii=False)
            self.assertIn("已提交", bind_card_json)
            self.assertIn("这张卡片已锁定", bind_card_json)
            self.assertNotIn('"tag": "form"', bind_card_json)
            binding = json.loads((root / ".zhenzhi" / "project-group-bindings" / "oc_project.json").read_text(encoding="utf-8"))
            self.assertEqual(binding["projectId"], "knowledge-core")

    def test_feishu_project_create_mode_progressively_reduces_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=False,
                approval_code_project="",
                approval_code_common="",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            settings = replace(settings, reply_enabled=True)
            sent_followups = []
            original_send_response_later = feishu_module.send_feishu_response_later
            feishu_module.send_feishu_response_later = lambda _settings, message_id, response, **_kwargs: sent_followups.append((message_id, response)) or True
            try:
                result = feishu_module.handle_feishu_event(
                    Bundle(root),
                    {
                        "schema": "2.0",
                        "header": {"event_type": "card.action.trigger", "token": "expected-token"},
                        "event": {
                            "operator": {"operator_id": {"open_id": "ou_submitter", "user_id": "submitter"}},
                            "context": {"open_message_id": "om_project_mode", "open_chat_id": "oc_project"},
                            "action": {"value": {"action": "project_create_mode", "repoMode": "existing"}},
                        },
                    },
                    settings,
                )
            finally:
                feishu_module.send_feishu_response_later = original_send_response_later
            self.assertEqual(set(result.keys()), {"toast"})
            self.assertIn("正在发送新的项目启动卡", result["toast"]["content"])
            self.assertEqual(sent_followups[0][0], "om_project_mode")
            self.assertEqual(sent_followups[0][1]["msg_type"], "interactive")
            card_text = json.dumps(sent_followups[0][1]["card"], ensure_ascii=False)
            self.assertIn("Git 地址", card_text)
            self.assertIn("项目名称，可选", card_text)
            self.assertIn("是否创建或绑定项目群", card_text)
            self.assertIn("请选择", card_text)
            self.assertIn("暂不需要项目群", card_text)
            self.assertIn("select_static", card_text)
            self.assertIn("create_or_bind", card_text)
            self.assertIn("form_action_type", card_text)
            self.assertIn("project_create_submit|repoMode=existing", card_text)
            self.assertNotIn("behaviors", card_text)
            self.assertNotIn("\"content\": \"是\"", card_text)
            self.assertNotIn("\"content\": \"否\"", card_text)
            self.assertNotIn("默认 Runner", card_text)
            card_event_records = list((root / ".zhenzhi" / "feishu-card-events").glob("*.json"))
            self.assertTrue(card_event_records)
            card_event = next(json.loads(path.read_text(encoding="utf-8")) for path in card_event_records if "responseKeys" in path.read_text(encoding="utf-8"))
            self.assertEqual(card_event["responseKeys"], ["toast"])
            self.assertEqual(card_event["responseCardType"], "")

            sent_followups.clear()
            feishu_module.send_feishu_response_later = lambda _settings, message_id, response, **_kwargs: sent_followups.append((message_id, response)) or True
            try:
                material_scope_result = feishu_module.handle_feishu_event(
                    Bundle(root),
                    {
                        "schema": "2.0",
                        "header": {"event_type": "card.action.trigger", "token": "expected-token"},
                        "event": {
                            "operator": {"operator_id": {"open_id": "ou_submitter", "user_id": "submitter"}},
                            "context": {"open_message_id": "om_material_scope", "open_chat_id": "oc_project"},
                            "action": {"value": {"action": "material_capture_scope", "scope": "common"}},
                        },
                    },
                    settings,
                )
            finally:
                feishu_module.send_feishu_response_later = original_send_response_later
            self.assertEqual(set(material_scope_result.keys()), {"toast"})
            self.assertIn("知识记录卡", material_scope_result["toast"]["content"])
            self.assertEqual(sent_followups[0][0], "om_material_scope")
            self.assertEqual(sent_followups[0][1]["msg_type"], "interactive")
            material_followup_text = json.dumps(sent_followups[0][1]["card"], ensure_ascii=False)
            self.assertIn("记录公共知识", material_followup_text)
            self.assertNotIn("项目名称", material_followup_text)

            settings = replace(settings, reply_enabled=False)
            new_result = feishu_module.handle_feishu_event(
                Bundle(root),
                {
                    "schema": "2.0",
                    "header": {"event_type": "card.action.trigger", "token": "expected-token"},
                    "event": {
                        "operator": {"operator_id": {"open_id": "ou_submitter", "user_id": "submitter"}},
                        "context": {"open_message_id": "om_project_mode_new", "open_chat_id": "oc_project"},
                        "action": {"value": {"action": "project_create_mode", "repoMode": "new"}},
                    },
                },
                settings,
            )
            self.assertEqual(set(new_result.keys()), {"toast"})
            new_card_text = json.dumps(feishu_module.project_create_details_card("new"), ensure_ascii=False)
            self.assertIn("项目名称", new_card_text)
            self.assertIn("项目目标", new_card_text)
            self.assertIn("按项目名称生成仓库名", new_card_text)
            self.assertIn("需要创建或绑定项目群", new_card_text)
            self.assertIn("主责 Agent，可选", new_card_text)
            self.assertIn("select_static", new_card_text)
            self.assertIn("form_action_type", new_card_text)
            self.assertIn("project_create_submit|repoMode=new", new_card_text)
            self.assertNotIn("behaviors", new_card_text)
            self.assertNotIn("新建仓库名", new_card_text)

            material_card_text = json.dumps(feishu_module.material_capture_card(), ensure_ascii=False)
            self.assertIn("公共知识/通用经验", material_card_text)
            self.assertIn("项目资料/项目知识", material_card_text)
            common_material_card_text = json.dumps(feishu_module.material_capture_card("common"), ensure_ascii=False)
            self.assertIn("记录公共知识", common_material_card_text)
            self.assertIn("来源，可选", common_material_card_text)
            self.assertNotIn("项目名称", common_material_card_text)
            project_material_card_text = json.dumps(feishu_module.material_capture_card("project"), ensure_ascii=False)
            self.assertIn("记录项目资料", project_material_card_text)
            self.assertIn("项目名称", project_material_card_text)
            self.assertIn("资料原文", project_material_card_text)
            self.assertIn("可分行填写", project_material_card_text)
            search_card_text = json.dumps(feishu_module.knowledge_search_card(), ensure_ascii=False)
            self.assertIn("项目名称，可选", search_card_text)
            self.assertIn("可分行填写", search_card_text)

    def test_feishu_common_knowledge_capture_card_creates_task_without_project_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "company-knowledge-core", "--name", "Company Knowledge Core", "--owner", "meimei"]), 0)
            incoming = {
                "messageId": "om_common_material",
                "chatId": "oc_common_material",
                "chatType": "p2p",
                "text": "",
                "openId": "ou_submitter",
                "userId": "submitter",
                "mentionedOpenIds": "",
                "mentionedUserIds": "",
            }
            settings = minimal_feishu_settings(
                app_id="cli_app",
                app_secret="cli_secret",
                common_reviewer_open_ids=["ou_meimei"],
            )
            sent_cards: list[tuple[str, dict[str, object]]] = []
            original_direct = feishu_module.send_feishu_direct_response
            feishu_module.send_feishu_direct_response = lambda _settings, open_id, response: sent_cards.append((open_id, response)) or True
            try:
                reply = feishu_module.submit_material_capture_card(
                    bundle,
                    incoming,
                    settings,
                    {
                        "scope": "common",
                        "title": "飞书卡片正确实现路径",
                        "content": "飞书卡片 callback 只做短确认，复杂结果用异步消息发送。",
                        "sourceRef": "feishu://docx/card-runbook",
                        "scopeNote": "飞书卡片实现",
                    },
                )
            finally:
                feishu_module.send_feishu_direct_response = original_direct
            self.assertIn("公共知识资料", reply)
            self.assertIn("任务编号", reply)
            self.assertIn("原始资料", reply)
            self.assertIn("等待执行电脑接管", reply)
            self.assertNotIn("状态: waiting_runner", reply)
            sources = [path for path in (root / "projects" / "company-knowledge-core" / "sources").glob("*.md") if path.name != "index.md"]
            self.assertEqual(len(sources), 1)
            source = load_object(sources[0])
            self.assertEqual(source["type"], "SourceMaterial")
            self.assertEqual(source["sourceRef"], "feishu://docx/card-runbook")
            self.assertEqual(source["materialType"], "common_knowledge")
            self.assertEqual(source["projectId"], "company-knowledge-core")
            self.assertIn("适用范围：飞书卡片实现", sources[0].read_text(encoding="utf-8"))
            tasks = [path for path in (root / "projects" / "company-knowledge-core" / "tasks").glob("*.md") if path.name != "index.md"]
            self.assertEqual(len(tasks), 1)
            task = load_object(tasks[0])
            self.assertEqual(task["type"], "KnowledgeTask")
            self.assertEqual(task["sourceMaterialRefs"], [str(sources[0].relative_to(root))])
            self.assertEqual(task["assignee"], "agent.company-knowledge-core.knowledge-engineering")
            self.assertEqual(task["status"], "waiting_runner")
            self.assertEqual(sent_cards[0][0], "ou_meimei")
            sent_card_text = json.dumps(sent_cards[0][1], ensure_ascii=False)
            self.assertIn(str(task["taskId"]), sent_card_text)
            self.assertIn("需要手动接管任务", sent_card_text)
            self.assertIn("本地 Codex", sent_card_text)
            notifications = [
                load_object(path)
                for path in (root / "notifications").glob("*.md")
                if path.name != "index.md"
            ]
            self.assertIn("sent", [item["status"] for item in notifications])
            self.assertIn("task_waiting_runner", [item["messageType"] for item in notifications])

    def test_manual_runner_card_uses_project_initialization_instructions(self) -> None:
        project_card = feishu_module.manual_runner_required_card(
            {
                "taskId": "project-init-agent-hub",
                "title": "Agent Hub 项目初始化",
                "projectId": "agent-hub",
                "taskType": "project_initialization",
                "sourceMaterialRefs": ["projects/agent-hub/launch.md"],
            },
            "projects/agent-hub/tasks/project-init-agent-hub.md",
            "agent.agent-hub.project-manager",
            "projects/agent-hub/launch.md",
        )
        project_text = json.dumps(project_card, ensure_ascii=False)
        self.assertIn("接管项目初始化任务 project-init-agent-hub", project_text)
        self.assertIn("首批 ProjectTask", project_text)
        self.assertIn("项目初始化需要本地接管", project_text)
        self.assertIn("等待本地接管", project_text)
        self.assertNotIn("waiting_runner", project_text)
        self.assertNotIn("任务卡", project_text)
        self.assertNotIn("接管知识工程任务", project_text)
        self.assertNotIn("KnowledgeItem draft", project_text)

        knowledge_card = feishu_module.manual_runner_required_card(
            {
                "taskId": "KT-001",
                "title": "知识沉淀",
                "projectId": "company-knowledge-core",
                "taskType": "knowledge_capture",
                "sourceMaterialRefs": ["projects/company-knowledge-core/sources/source.md"],
            },
            "projects/company-knowledge-core/tasks/kt-001.md",
            "agent.company-knowledge-core.knowledge-engineering",
            "projects/company-knowledge-core/sources/source.md",
        )
        knowledge_text = json.dumps(knowledge_card, ensure_ascii=False)
        self.assertIn("接管知识工程任务 KT-001", knowledge_text)
        self.assertIn("KnowledgeItem draft", knowledge_text)

    def test_feishu_new_project_card_generates_repo_name_from_project_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=["ou_common"],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            original_create = feishu_module.create_feishu_approval_instance
            feishu_module.create_feishu_approval_instance = lambda *_args, **_kwargs: "approval_new_project"
            try:
                result = feishu_module.handle_feishu_event(
                    Bundle(root),
                    {
                        "schema": "2.0",
                        "header": {"event_type": "card.action.trigger", "token": "expected-token"},
                        "event": {
                            "operator": {"operator_id": {"open_id": "ou_submitter", "user_id": "submitter"}},
                            "context": {"open_message_id": "om_new_project_repo_infer", "open_chat_id": "oc_project"},
                            "action": {
                                "value": {"action": "project_create_submit", "repoMode": "new"},
                                "form_value": {
                                    "projectName": "桢知 Agent Hub",
                                    "goal": "建设公司 Agent 团队入口",
                                },
                            },
                        },
                    },
                    settings,
                )
            finally:
                feishu_module.create_feishu_approval_instance = original_create
            self.assertEqual(set(result.keys()), {"toast", "card"})
            self.assertIn("这张卡片已锁定", json.dumps(result["card"]["data"], ensure_ascii=False))
            launch = (root / "projects" / "agent-hub" / "launch.md").read_text(encoding="utf-8")
            self.assertIn("repoMode: new", launch)
            self.assertIn("repoName: agent-hub", launch)

    def test_feishu_existing_repo_card_infers_project_name_from_git_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=["ou_common"],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            original_create = feishu_module.create_feishu_approval_instance
            feishu_module.create_feishu_approval_instance = lambda *_args, **_kwargs: "approval_inferred_project"
            try:
                result = feishu_module.handle_feishu_event(
                    Bundle(root),
                    {
                        "schema": "2.0",
                        "header": {"event_type": "card.action.trigger", "token": "expected-token"},
                        "event": {
                            "operator": {"operator_id": {"open_id": "ou_submitter", "user_id": "submitter"}},
                            "context": {"open_message_id": "om_existing_repo_infer", "open_chat_id": "oc_project"},
                            "action": {
                                "name": "project_create_submit|repoMode=existing",
                                "value": {},
                                "form_value": {"repoUrl": "https://github.com/company/company_knowledge_core.git"},
                            },
                        },
                    },
                    settings,
                )
            finally:
                feishu_module.create_feishu_approval_instance = original_create
            self.assertEqual(set(result.keys()), {"toast", "card"})
            self.assertIn("这张卡片已锁定", json.dumps(result["card"]["data"], ensure_ascii=False))
            launch = (root / "projects" / "company-knowledge-core" / "launch.md").read_text(encoding="utf-8")
            self.assertIn("repoUrl: https://github.com/company/company_knowledge_core.git", launch)
            self.assertIn("repoName: company_knowledge_core", launch)

    def test_feishu_project_creation_a_b_selection_does_not_search_knowledge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=False,
                approval_code_project="",
                approval_code_common="",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            reply_a = feishu_module.build_reply(
                Bundle(root),
                {
                    "messageId": "om_menu_select_a",
                    "chatId": "ou_alice",
                    "chatType": "p2p",
                    "text": "A",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                },
                settings,
            )
            self.assertIn("已选择：已有仓库接入", reply_a)
            self.assertIn("已有仓库 <Git URL>", reply_a)
            self.assertNotIn("基于已审核知识", reply_a)
            reply_b = feishu_module.build_reply(
                Bundle(root),
                {
                    "messageId": "om_menu_select_b",
                    "chatId": "ou_alice",
                    "chatType": "p2p",
                    "text": "B",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                },
                settings,
            )
            self.assertIn("已选择：从头创建新项目", reply_b)
            self.assertIn("按项目名称生成仓库名", reply_b)
            self.assertNotIn("新建仓库 <仓库名>", reply_b)
            self.assertNotIn("基于已审核知识", reply_b)

    def test_feishu_dangerous_intent_is_blocked_with_approval_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=False,
                approval_code_project="",
                approval_code_common="",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            reply = feishu_module.build_reply(
                Bundle(root),
                {
                    "messageId": "om_delete_core",
                    "chatId": "ou_alice",
                    "chatType": "p2p",
                    "text": "把知识工程体系删掉",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                },
                settings,
            )
            self.assertIn("高风险操作", reply)
            self.assertIn("不能直接执行", reply)
            self.assertIn("owner 审批", reply)

    def test_feishu_unknown_query_reply_matches_chat_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=False,
                approval_code_project="",
                approval_code_common="",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            private_reply = feishu_module.build_reply(
                Bundle(root),
                {
                    "messageId": "om_agent_hub_unknown",
                    "chatId": "ou_alice",
                    "chatType": "p2p",
                    "text": "查一个不存在的问题",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                },
                settings,
            )
            group_reply = feishu_module.build_reply(
                Bundle(root),
                {
                    "messageId": "om_project_assistant_unknown",
                    "chatId": "oc_project",
                    "chatType": "group",
                    "text": "查一个不存在的问题",
                    "openId": "ou_alice",
                    "userId": "alice",
                    "mentionedOpenIds": "",
                },
                settings,
            )
            self.assertIn("创建项目", private_reply)
            self.assertIn("Agent Hub", private_reply)
            self.assertIn("项目内可以发送", group_reply)
            self.assertIn("项目助手", group_reply)

    def test_approval_callback_recreates_missing_project_target_and_notifies_submitter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            save_approval_request(
                bundle,
                "approval_project_missing",
                {
                    "instanceCode": "approval_project_missing",
                    "approvalCode": "approval_common",
                    "approvalType": "project_init",
                    "targetRef": "projects/project-missing/project.md",
                    "requestedStatus": "verified",
                    "projectId": "project-missing",
                    "projectName": "缺失项目",
                    "ownerOpenId": "ou_owner",
                    "submitterOpenId": "ou_submitter",
                    "approvalDocUrl": "https://example.com/doc",
                },
            )
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            sent_messages: list[tuple[str, str]] = []
            original_send = feishu_module.send_feishu_message
            feishu_module.send_feishu_message = lambda _settings, open_id, text: sent_messages.append((open_id, text)) or True
            try:
                result = feishu_module.handle_approval_event(
                    bundle,
                    {
                        "schema": "2.0",
                        "header": {"event_type": "approval.instance.updated_v4"},
                        "event": {
                            "instance_code": "approval_project_missing",
                            "approval_code": "approval_common",
                            "status": "APPROVED",
                            "operator_id": {"open_id": "ou_reviewer"},
                        },
                    },
                    settings,
                )
            finally:
                feishu_module.send_feishu_message = original_send
            project_path = root / "projects" / "project-missing" / "project.md"
            self.assertEqual(result["status"], "verified")
            self.assertIn("status: verified", project_path.read_text(encoding="utf-8"))
            self.assertEqual(sent_messages[0][0], "ou_submitter")
            self.assertIn("项目立项已通过：缺失项目", sent_messages[0][1])
            self.assertEqual(sent_messages[1][0], "ou_owner")
            self.assertIn("你负责的项目已立项：缺失项目", sent_messages[1][1])
            self.assertIn("会议纪要：项目 缺失项目", sent_messages[1][1])
            self.assertNotIn("会议纪要：project-missing", sent_messages[1][1])
            self.assertEqual(len(sent_messages), 2)
            audits = "\n".join(path.read_text(encoding="utf-8") for path in (root / "knowledge" / "audit").glob("*.md"))
            self.assertIn("feishu.approval.target_recreated", audits)

    def test_project_owner_notification_failure_notifies_submitter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            save_approval_request(
                bundle,
                "approval_owner_unreachable",
                {
                    "instanceCode": "approval_owner_unreachable",
                    "approvalCode": "approval_common",
                    "approvalType": "project_init",
                    "targetRef": "projects/project-owner/project.md",
                    "requestedStatus": "verified",
                    "projectId": "project-owner",
                    "projectName": "负责人不可达项目",
                    "ownerOpenId": "ou_owner",
                    "ownerName": "Owner",
                    "submitterOpenId": "ou_submitter",
                },
            )
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            sent_messages: list[tuple[str, str]] = []
            original_send = feishu_module.send_feishu_message
            def fake_send(_settings, open_id, text):
                if open_id == "ou_owner":
                    raise feishu_module.KnowledgeError("Bot has NO availability to this user.")
                sent_messages.append((open_id, text))
                return True
            feishu_module.send_feishu_message = fake_send
            try:
                feishu_module.handle_approval_event(
                    bundle,
                    {
                        "schema": "2.0",
                        "header": {"event_type": "approval.instance.updated_v4"},
                        "event": {"instance_code": "approval_owner_unreachable", "approval_code": "approval_common", "status": "APPROVED"},
                    },
                    settings,
                )
            finally:
                feishu_module.send_feishu_message = original_send
            self.assertEqual(sent_messages[0][0], "ou_submitter")
            self.assertIn("项目立项已通过", sent_messages[0][1])
            self.assertEqual(sent_messages[1][0], "ou_submitter")
            self.assertIn("负责人通知未送达", sent_messages[1][1])
            audits = "\n".join(path.read_text(encoding="utf-8") for path in (root / "knowledge" / "audit").glob("*.md"))
            self.assertIn("recipientRole: project_owner", audits)

    def test_project_approval_sends_interactive_result_cards(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            bundle = Bundle(root)
            save_approval_request(
                bundle,
                "approval_project_card_notice",
                {
                    "instanceCode": "approval_project_card_notice",
                    "approvalCode": "approval_project",
                    "approvalType": "project_init",
                    "targetRef": "projects/agent-hub/project.md",
                    "requestedStatus": "verified",
                    "projectId": "agent-hub",
                    "projectName": "桢知 Agent Hub 与知识工程中枢",
                    "ownerOpenId": "ou_owner",
                    "ownerName": "梅晓华",
                    "submitterOpenId": "ou_submitter",
                    "approvalDocUrl": "https://xcn68awb7dsi.feishu.cn/docx/example",
                },
            )
            settings = feishu_module.FeishuSettings(
                app_id="cli_app",
                app_secret="cli_secret",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            sent_cards: list[tuple[str, dict[str, object]]] = []
            original_direct = feishu_module.send_feishu_direct_response
            feishu_module.send_feishu_direct_response = lambda _settings, open_id, response: sent_cards.append((open_id, response)) or True
            try:
                result = feishu_module.handle_approval_event(
                    bundle,
                    {
                        "schema": "2.0",
                        "header": {"event_type": "approval.instance.updated_v4"},
                        "event": {
                            "instance_code": "approval_project_card_notice",
                            "approval_code": "approval_project",
                            "status": "APPROVED",
                            "operator_id": {"open_id": "ou_reviewer"},
                        },
                    },
                    settings,
                )
            finally:
                feishu_module.send_feishu_direct_response = original_direct
            self.assertEqual(result["status"], "verified")
            self.assertEqual(sent_cards[0][0], "ou_submitter")
            self.assertEqual(sent_cards[0][1]["msg_type"], "interactive")
            submitter_card = json.dumps(sent_cards[0][1]["card"], ensure_ascii=False)
            self.assertIn("项目立项审批已通过", submitter_card)
            self.assertIn("桢知 Agent Hub 与知识工程中枢", submitter_card)
            self.assertIn("审批说明", submitter_card)
            self.assertEqual(sent_cards[1][0], "ou_owner")
            owner_card = json.dumps(sent_cards[1][1]["card"], ensure_ascii=False)
            self.assertIn("你负责的项目已立项", owner_card)
            self.assertIn("会议纪要：项目 桢知 Agent Hub 与知识工程中枢", owner_card)
            project = load_object(root / "projects" / "agent-hub" / "project.md")
            self.assertEqual(project["status"], "verified")
            self.assertEqual(project["humanOwner"], "梅晓华")

    def test_feishu_project_init_understands_natural_language_and_asks_for_mention(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=["ou_common"],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="https://xcn68awb7dsi.feishu.cn",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            reply = feishu_module.build_reply(
                Bundle(root),
                {
                    "messageId": "om_project_natural",
                    "chatId": "oc_test",
                    "chatType": "group",
                    "text": "创建一个项目，名字叫做工业软件点胶机。项目负责人是hanson",
                    "openId": "ou_submitter",
                    "userId": "submitter",
                    "mentionedOpenIds": "",
                },
                settings,
            )
            self.assertIn("hanson", reply)
            self.assertIn("项目 Owner 请 @ 对方", reply)
            self.assertIn("姓名/手机号", reply)
            self.assertFalse((root / "projects" / "gong-ye-ruan-jian-dian-jiao-ji").exists())

    def test_feishu_project_init_resolves_owner_name_from_map(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=["ou_common"],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="https://xcn68awb7dsi.feishu.cn",
                approval_doc_share_names=[],
                user_open_id_map={"hanson": "ou_hanson"},
            )
            original_create = feishu_module.create_feishu_approval_instance
            feishu_module.create_feishu_approval_instance = lambda *_args, **_kwargs: "approval_project_natural"
            try:
                reply = feishu_module.build_reply(
                    Bundle(root),
                    {
                        "messageId": "om_project_natural",
                        "chatId": "oc_test",
                        "chatType": "group",
                        "text": "创建一个项目，名字叫做工业软件点胶机。项目负责人是hanson",
                        "openId": "ou_submitter",
                        "userId": "submitter",
                        "mentionedOpenIds": "",
                    },
                    settings,
                )
                self.assertIn("项目草稿已创建", reply)
                self.assertIn("已发起飞书审批", reply)
            finally:
                feishu_module.create_feishu_approval_instance = original_create

    def test_feishu_message_event_retry_is_idempotent_for_project_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=["reviewer"],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="https://xcn68awb7dsi.feishu.cn",
                approval_doc_share_names=[],
                user_open_id_map={"hanson": "owner"},
            )
            created: list[dict[str, str]] = []
            original_create = feishu_module.create_feishu_approval_instance
            def fake_create_approval(*_args, **kwargs):
                created.append(dict(kwargs.get("form_values", {})))
                return "approval_once"

            feishu_module.create_feishu_approval_instance = fake_create_approval
            payload = {
                "schema": "2.0",
                "header": {"event_type": "im.message.receive_v1", "token": "expected-token"},
                "event": {
                    "sender": {"sender_id": {"open_id": "ou_submitter", "user_id": "submitter"}},
                    "message": {
                        "message_id": "om_project_retry",
                        "chat_id": "oc_test",
                        "chat_type": "group",
                        "message_type": "text",
                        "content": json.dumps({"text": "创建一个项目，名字叫做工业软件点胶机。项目负责人是hanson"}),
                    },
                },
            }
            try:
                first = feishu_module.handle_feishu_event(Bundle(root), payload, settings)
                second = feishu_module.handle_feishu_event(Bundle(root), payload, settings)
                self.assertTrue(first["ok"])
                self.assertTrue(second["duplicate"])
                self.assertEqual(len(created), 1)
                self.assertEqual(len(list((root / "projects").glob("*/project.md"))), 1)
            finally:
                feishu_module.create_feishu_approval_instance = original_create

    def test_feishu_message_retry_respects_legacy_audit_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            feishu_module.create_audit_log(Bundle(root), "ou_submitter", "feishu.message.receive", "om_legacy_retry", after="replied", policy_result="bot_gateway")
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="expected-token",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=["reviewer"],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="https://xcn68awb7dsi.feishu.cn",
                approval_doc_share_names=[],
                user_open_id_map={"hanson": "owner"},
            )
            result = feishu_module.handle_feishu_event(
                Bundle(root),
                {
                    "schema": "2.0",
                    "header": {"event_type": "im.message.receive_v1", "token": "expected-token"},
                    "event": {
                        "sender": {"sender_id": {"open_id": "ou_submitter", "user_id": "submitter"}},
                        "message": {
                            "message_id": "om_legacy_retry",
                            "chat_id": "oc_test",
                            "chat_type": "group",
                            "message_type": "text",
                            "content": json.dumps({"text": "创建一个项目，名字叫做工业软件点胶机。项目负责人是hanson"}),
                        },
                    },
                },
                settings,
            )
            self.assertTrue(result["duplicate"])
            self.assertEqual(len(list((root / "projects").glob("*/project.md"))), 0)

    def test_feishu_message_reply_failure_does_not_fail_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            settings = feishu_module.FeishuSettings(
                app_id="app",
                app_secret="secret",
                verification_token="expected-token",
                reply_enabled=True,
                token_auto_approve=False,
                approval_enabled=False,
                approval_code_project="",
                approval_code_common="",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=[],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="https://xcn68awb7dsi.feishu.cn",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            original_send = feishu_module.send_feishu_incoming_response
            feishu_module.send_feishu_incoming_response = lambda *_args, **_kwargs: (_ for _ in ()).throw(feishu_module.KnowledgeError("reply failed"))
            try:
                result = feishu_module.handle_feishu_event(
                    Bundle(root),
                    {
                        "schema": "2.0",
                        "header": {"event_type": "im.message.receive_v1", "token": "expected-token"},
                        "event": {
                            "sender": {"sender_id": {"open_id": "ou_alice", "user_id": "alice"}},
                            "message": {
                                "message_id": "om_bad_reply",
                                "chat_id": "oc_test",
                                "chat_type": "group",
                                "message_type": "text",
                                "content": json.dumps({"text": "创建一个项目，名字叫做工业软件点胶机。项目负责人是hanson"}),
                            },
                        },
                    },
                    settings,
                )
                self.assertTrue(result["ok"])
                self.assertFalse(result["sent"])
                self.assertIn("reply failed", result["replyError"])
            finally:
                feishu_module.send_feishu_incoming_response = original_send

    def test_feishu_fast_knowledge_query_records_delivery_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            item_dir = root / "knowledge" / "engineering"
            item_dir.mkdir(parents=True, exist_ok=True)
            (item_dir / "feishu-card-json-v2.md").write_text(
                """---
type: KnowledgeItem
title: Feishu Card JSON 2.0
description: Verified Feishu card pattern.
timestamp: 2026-06-19T00:00:00Z
owner: agent.company-knowledge-core.knowledge-engineering
status: verified
scope: engineering
sourceRef: feishu-card-json-v2-source
confidence: high
---

## Pattern

飞书卡片 JSON 2.0 使用 form 容器、input 字段和 submit button。
""",
                encoding="utf-8",
            )
            self.assertEqual(main(["--root", str(root), "rag", "rebuild"]), 0)
            settings = minimal_feishu_settings(app_id="app", app_secret="secret", reply_enabled=True)
            original_send = feishu_module.send_feishu_incoming_response
            feishu_module.send_feishu_incoming_response = lambda *_args, **_kwargs: (_ for _ in ()).throw(feishu_module.KnowledgeError("reply failed"))
            try:
                result = feishu_module.handle_feishu_event(
                    Bundle(root),
                    {
                        "schema": "2.0",
                        "header": {"event_type": "im.message.receive_v1", "token": "expected-token"},
                        "event": {
                            "sender": {"sender_id": {"open_id": "ou_alice", "user_id": "alice"}},
                            "message": {
                                "message_id": "om_kq_bad_reply",
                                "chat_id": "oc_test",
                                "chat_type": "group",
                                "message_type": "text",
                                "content": json.dumps({"text": "飞书卡片 JSON 2.0 怎么写？"}),
                            },
                        },
                    },
                    settings,
                )
                self.assertTrue(result["ok"])
                self.assertFalse(result["sent"])
                self.assertIn("reply failed", result["replyError"])
                logs = list((root / ".zhenzhi" / "knowledge-query-logs").glob("*.json"))
                self.assertEqual(len(logs), 1)
                query_log = json.loads(logs[0].read_text(encoding="utf-8"))
                self.assertEqual(query_log["answerMode"], "verified_answer")
                self.assertEqual(query_log["delivery"]["status"], "failed")
                self.assertIn("knowledge_query.completed", audit_actions(root))
                self.assertIn("feishu.reply.failed", audit_actions(root))
            finally:
                feishu_module.send_feishu_incoming_response = original_send

    def test_feishu_approval_creates_change_doc_before_instance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            draft = root / "knowledge" / "engineering" / "example.md"
            draft.parent.mkdir(parents=True, exist_ok=True)
            draft.write_text("---\ntype: KnowledgeItem\nstatus: draft\nsourceRef: \"\"\n---\n\nnew policy draft\n", encoding="utf-8")
            settings = feishu_module.FeishuSettings(
                app_id="",
                app_secret="",
                verification_token="",
                reply_enabled=False,
                token_auto_approve=False,
                approval_enabled=True,
                approval_code_project="approval_project",
                approval_code_common="approval_common",
                approval_code_security="",
                approval_node_approver_key="",
                common_reviewer_open_ids=["ou_common"],
                security_reviewer_open_ids=[],
                project_reviewer_open_ids={},
                token_send_on_approval=False,
                approval_doc_folder_token="",
                approval_doc_folder_tokens={},
                approval_doc_domain="https://xcn68awb7dsi.feishu.cn",
                approval_doc_share_names=[],
                user_open_id_map={},
            )
            created: dict[str, object] = {}
            original_doc = feishu_module.create_approval_change_doc
            original_instance = feishu_module.create_feishu_approval_instance

            def fake_doc(_bundle, _settings, values):
                created["doc_values"] = dict(values)
                return {"url": "https://xcn68awb7dsi.feishu.cn/wiki/doc_node", "nodeToken": "doc_node", "objToken": "doc_obj"}

            def fake_instance(_settings, requester_user_id, approval_code, approver_user_ids, form_values):
                created["instance_values"] = dict(form_values)
                return "approval_with_doc"

            feishu_module.create_approval_change_doc = fake_doc
            feishu_module.create_feishu_approval_instance = fake_instance
            try:
                reply = feishu_module.trigger_approval_for_target(
                    Bundle(root),
                    settings,
                    {"openId": "ou_submitter", "messageId": "om1", "chatId": "oc1"},
                    approval_type="knowledge_ingest",
                    target_ref="knowledge/engineering/example.md",
                    requested_status="verified",
                    project_id="core",
                    project_name="Core",
                    owner_open_id="ou_owner",
                    summary="change summary",
                )
                self.assertIn("审批说明", reply)
                self.assertEqual(created["doc_values"]["object_path"], "knowledge/engineering/example.md")
                self.assertEqual(created["instance_values"]["approval_doc_url"], "https://xcn68awb7dsi.feishu.cn/wiki/doc_node")
                saved = json.loads((root / ".zhenzhi" / "approval-requests" / "approval_with_doc.json").read_text(encoding="utf-8"))
                self.assertEqual(saved["approvalDocUrl"], "https://xcn68awb7dsi.feishu.cn/wiki/doc_node")
            finally:
                feishu_module.create_approval_change_doc = original_doc
                feishu_module.create_feishu_approval_instance = original_instance

    def test_finish_requires_write_permission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "init", "--user-id", "alice"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "agent",
                        "register",
                        "--agent-id",
                        "agent.alice.builder",
                        "--name",
                        "Alice Builder",
                        "--owner",
                        "alice",
                        "--purpose",
                        "local development",
                    ]
                ),
                0,
            )
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "finish",
                        "--project",
                        "core",
                        "--agent",
                        "agent.alice.builder",
                        "--summary",
                        "should fail",
                    ]
                ),
                2,
            )

    def test_material_ingest_creates_source_material_and_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "meimei"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "material",
                        "ingest",
                        "--title",
                        "Agent meeting notes",
                        "--project",
                        "core",
                        "--submitter",
                        "meimei",
                        "--source-ref",
                        "https://xcn68awb7dsi.feishu.cn/minutes/example",
                        "--content",
                        "meeting conclusion: create Agent Hub project.",
                        "--create-task",
                    ]
                ),
                0,
            )
            source_files = list((root / "projects" / "core" / "sources").glob("source.*.md"))
            self.assertEqual(len(source_files), 1)
            source = load_object(source_files[0])
            self.assertEqual(source["type"], "SourceMaterial")
            self.assertEqual(source["materialType"], "meeting")
            self.assertEqual(source["extractionStatus"], "task_created")
            self.assertTrue(source["contentHash"])
            self.assertIn("meeting conclusion", source_files[0].read_text(encoding="utf-8"))
            task_files = [path for path in (root / "projects" / "core" / "tasks").glob("*.md") if path.name != "index.md"]
            self.assertEqual(len(task_files), 1)
            task = load_object(task_files[0])
            self.assertEqual(task["type"], "KnowledgeTask")
            self.assertEqual(task["sourceMaterialRefs"], [f"projects/core/sources/{source_files[0].name}"])
            self.assertIn("material.ingest", audit_actions(root))
            self.assertIn("task.create", audit_actions(root))

    def test_material_ingest_binary_keeps_metadata_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "material",
                        "ingest",
                        "--title",
                        "Local model package",
                        "--submitter",
                        "meimei",
                        "--source-ref",
                        "s3://models/local-model.dmg",
                        "--material-type",
                        "package",
                        "--content",
                        "this raw package body should not be reusable text",
                    ]
                ),
                0,
            )
            source_files = list((root / "sources").glob("source.*.md"))
            self.assertEqual(len(source_files), 1)
            text = source_files[0].read_text(encoding="utf-8")
            self.assertIn("Raw binary or bulky content is not stored", text)
            self.assertNotIn("this raw package body should not be reusable text", text)

    def test_material_ingest_rejects_secret_like_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "material",
                        "ingest",
                        "--title",
                        "Bad material",
                        "--submitter",
                        "meimei",
                        "--source-ref",
                        "feishu://message/bad",
                        "--content",
                        "temporary api_key sk-localtest1234567890 should never be stored",
                    ]
                ),
                2,
            )
            self.assertFalse(list((root / "sources").glob("source.*.md")))

    def test_graph_export_impact_and_context_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "meimei"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "agent",
                        "register",
                        "--agent-id",
                        "agent.core.knowledge",
                        "--name",
                        "Knowledge Agent",
                        "--owner",
                        "meimei",
                        "--purpose",
                        "knowledge work",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "material",
                        "ingest",
                        "--title",
                        "Feishu card experience",
                        "--project",
                        "core",
                        "--submitter",
                        "meimei",
                        "--source-ref",
                        "docs/feishu-card.md",
                        "--content",
                        "Feishu card callback must respond immediately and update card asynchronously.",
                        "--create-task",
                    ]
                ),
                0,
            )
            self.assertEqual(main(["--root", str(root), "graph", "export", "--actor", "tester"]), 0)
            self.assertTrue(list((root / "graph" / "edges").glob("edge.*.md")))
            self.assertTrue(list((root / "graph" / "snapshots").glob("graph-snapshot.*.md")))
            snapshot = load_object(next((root / "graph" / "snapshots").glob("graph-snapshot.*.md")))
            self.assertEqual(snapshot["status"], "observed")
            source_ref = "projects/core/sources/" + next((root / "projects" / "core" / "sources").glob("source.*.md")).name
            rebuild_count = audit_actions(root).count("graph.edges.rebuild")
            edge_text_before = {path.name: path.read_text(encoding="utf-8") for path in (root / "graph" / "edges").glob("edge.*.md")}
            self.assertEqual(main(["--root", str(root), "graph", "impact", source_ref, "--actor", "tester"]), 0)
            self.assertEqual(rebuild_count, audit_actions(root).count("graph.edges.rebuild"))
            edge_text_after = {path.name: path.read_text(encoding="utf-8") for path in (root / "graph" / "edges").glob("edge.*.md")}
            self.assertEqual(edge_text_before, edge_text_after)
            edge_text = "\n".join(path.read_text(encoding="utf-8") for path in (root / "graph" / "edges").glob("edge.*.md"))
            self.assertIn("usesSource", edge_text)
            self.assertIn(source_ref, edge_text)
            self.assertEqual(main(["--root", str(root), "rag", "rebuild"]), 0)
            self.assertEqual(main(["--root", str(root), "start", "--project", "core", "--agent", "agent.core.knowledge", "--task", "Feishu callback card"]), 0)
            context_text = (root / ".zhenzhi" / "context" / "current.md").read_text(encoding="utf-8")
            self.assertIn("inclusionReason:", context_text)
            self.assertIn("graph:", context_text)
            self.assertIn("graph.edges.rebuild", audit_actions(root))
            self.assertIn("graph.snapshot.export", audit_actions(root))
            self.assertIn("graph.impact", audit_actions(root))

    def test_http_material_and_graph_api(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "meimei"]), 0)
            try:
                server = KnowledgeHTTPServer(("127.0.0.1", 0), Bundle(root), api_token="test-token")
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"

            def post(path: str, payload: dict) -> dict:
                request = urllib.request.Request(
                    base + path,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"},
                    method="POST",
                )
                with urllib.request.urlopen(request) as response:
                    body = response.read()
                return json.loads(body.decode("utf-8"))

            try:
                material = post(
                    "/v0/materials/ingest",
                    {
                        "title": "HTTP meeting note",
                        "projectId": "core",
                        "submitter": "ou_http",
                        "sourceRef": "feishu://message/http-material",
                        "materialType": "meeting",
                        "content": "HTTP material intake creates source material and task.",
                        "createTask": True,
                    },
                )
                self.assertEqual(material["kind"], "SourceMaterialIngest")
                source = load_object(root / material["sourceRef"])
                self.assertEqual(source["materialType"], "meeting")
                self.assertEqual(source["taskRef"], material["taskRef"])
                graph = post("/v0/graph/export", {"actor": "http-test"})
                self.assertEqual(graph["kind"], "GraphSnapshot")
                self.assertEqual(load_object(root / graph["snapshotRef"])["status"], "observed")
                impact = post("/v0/graph/impact", {"actor": "http-test", "ref": material["sourceRef"]})
                self.assertEqual(impact["kind"], "GraphImpact")
                self.assertIn("projects/core/project.md", impact["affectedRefs"])

                _review_bundle, review_task_id, draft_ref = self.create_reviewable_knowledge_fixture(root, "HTTP")
                review = post(
                    "/v0/review/finish",
                    {
                        "reviewTaskId": review_task_id,
                        "outcome": "pass_as_observed",
                        "reviewer": "agent.core.knowledge-review",
                        "summary": "HTTP review pass.",
                        "targetRefs": [draft_ref],
                    },
                )
                self.assertEqual(review["kind"], "KnowledgeReviewOutcome")
                self.assertEqual(review["outcome"], "pass_as_observed")
                self.assertEqual(load_object(root / draft_ref)["status"], "observed")
                self.assertTrue(review["notificationRefs"])
                indexed = search_index(Bundle(root), {"type": "KnowledgeItem", "status": "observed"})
                self.assertIn(draft_ref, [row["path"] for row in indexed])
            finally:
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()

    def test_http_discussion_api_closed_loop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "api-disc", "--name", "API Discussion", "--owner", "meimei"]), 0)
            try:
                server = KnowledgeHTTPServer(("127.0.0.1", 0), Bundle(root), api_token="test-token")
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"

            def post(path: str, payload: dict) -> dict:
                request = urllib.request.Request(
                    base + path,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"},
                    method="POST",
                )
                with urllib.request.urlopen(request) as response:
                    body = response.read()
                return json.loads(body.decode("utf-8"))

            def get(path: str) -> dict:
                request = urllib.request.Request(base + path, headers={"Authorization": "Bearer test-token"})
                with urllib.request.urlopen(request) as response:
                    body = response.read()
                return json.loads(body.decode("utf-8"))

            try:
                session = post(
                    "/v0/discussions/create",
                    {
                        "title": "API 讨论",
                        "projectId": "api-disc",
                        "requester": "agent.company.project-manager",
                        "topic": "Agent 工作台如何接入讨论会。",
                        "participantAgents": ["agent.company.development", "agent.company.test"],
                    },
                )
                self.assertEqual(session["kind"], "DiscussionSession")
                notifications = get(f"/v0/notifications?status=pending&recipient=agent.company.development&discussionId={session['discussionId']}")
                self.assertEqual(notifications["kind"], "NotificationList")
                self.assertEqual(len(notifications["notifications"]), 1)
                delivered = post(
                    "/v0/notifications/delivery",
                    {
                        "notificationId": notifications["notifications"][0]["notificationId"],
                        "status": "sent",
                        "actor": "http-notifier",
                        "deliveryRef": "om_http_discussion",
                    },
                )
                self.assertEqual(delivered["notification"]["status"], "sent")
                post("/v0/discussions/turn", {"discussionId": session["discussionId"], "agentId": "agent.company.development", "content": "开发建议用 HTTP 写回。"})
                turn = post("/v0/discussions/turn", {"discussionId": session["discussionId"], "agentId": "agent.company.test", "content": "测试要求验通知和后续任务。"})
                self.assertEqual(turn["sessionStatus"], "pm_reviewing")
                summary = post(
                    "/v0/discussions/finalize",
                    {
                        "discussionId": session["discussionId"],
                        "facilitator": "agent.company.project-manager",
                        "summary": "API 讨论闭环完成。",
                        "consensus": "工作台使用 HTTP API 写回讨论观点和汇总。",
                        "decision": "采用 /v0/discussions/* 作为第一阶段协议。",
                        "followupTaskTitle": "实现 Agent 工作台讨论 API 对接",
                        "followupAssignee": "agent.company.development",
                    },
                )
                self.assertEqual(summary["status"], "next_task_created")
                self.assertTrue(summary["decisionRefs"])
                self.assertTrue(summary["followupTaskRefs"])
            finally:
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()

    def test_governance_review_boundaries_comments_and_notification_repair(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "init", "--user-id", "alice"]), 0)
            bundle, review_task_id, draft_ref = self.create_reviewable_knowledge_fixture(root, "GOV")

            self.assertEqual(
                main(["--root", str(root), "review", "update", "--target", draft_ref, "--status", "verified", "--reviewer", "agent.core.knowledge-review"]),
                2,
            )
            self.assertEqual(main(["--root", str(root), "review", "update", "--target", draft_ref, "--status", "verified", "--reviewer", "meimei"]), 0)
            audit_rows = [load_object(path) for path in (root / "knowledge" / "audit").glob("*.md")]
            self.assertTrue(any(row.get("reviewRoute") == "knowledge_review_agent_then_human" for row in audit_rows))
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "review",
                        "apply",
                        "--task-id",
                        review_task_id,
                        "--outcome",
                        "changes_requested",
                        "--reviewer",
                        "agent.core.knowledge-review",
                        "--summary",
                        "needs improvement",
                        "--target-ref",
                        draft_ref,
                    ]
                ),
                2,
            )

            task_path = create_project_task(
                bundle,
                "Notify requester",
                "review-gov",
                "alice",
                "agent.company.project-manager",
                task_type="notification",
                task_id="NT-REPAIR-001",
            )
            notification_path = create_task_notification(
                bundle,
                task_path,
                load_object(task_path),
                "knowledge_published",
                recipient="alice",
                summary="知识审核结果：已发布。下一步查看知识对象。",
            )
            failed = mark_notification_delivery(bundle, load_object(notification_path)["notificationId"], "failed", "feishu-bot", failure_reason="review card send failed")
            self.assertTrue(failed["repairTaskRef"])
            repair_task = load_object(root / failed["repairTaskRef"])
            self.assertEqual(repair_task["assignee"], "agent.company.operations")
            self.assertIn("notification.repairTask.create", audit_actions(root))

    def test_admin_disable_blocks_usage_and_pauses_active_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "init", "--user-id", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "agent", "register", "--agent-id", "agent.alice.builder", "--name", "Alice Builder", "--owner", "alice", "--purpose", "local development"]), 0)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "tool", "register", "--tool-id", "tool.publisher", "--name", "Publisher", "--owner", "tool-owner", "--repo", "git@example.com:tool.git", "--entrypoint", "echo://ok", "--risk", "L1"]), 0)
            tool_path = root / "tools" / "tool.publisher.md"
            update_frontmatter_file(tool_path, {"status": "approved", "lastVerifiedAt": "2026-06-21T00:00:00Z"})
            task_path = create_project_task(Bundle(root), "Use publisher", "core", "alice", "agent.alice.builder", task_type="development", task_id="DISABLE-001")
            update_frontmatter_file(task_path, {"requiredTools": ["tool.publisher"], "status": "processing"})

            self.assertEqual(main(["--root", str(root), "admin", "disable", "--type", "tool", "--id", "tool.publisher", "--actor", "admin.alice", "--reason", "security review failed"]), 0)
            self.assertEqual(load_object(tool_path)["status"], "disabled")
            self.assertEqual(load_object(task_path)["status"], "blocked")
            self.assertEqual(
                main(["--root", str(root), "tool", "invoke", "--tool-id", "tool.publisher", "--project", "core", "--agent", "agent.alice.builder", "--input", "dry run"]),
                2,
            )
            self.assertIn("admin.disableAsset", audit_actions(root))
            self.assertIn("tool.invoke.denied", audit_actions(root))

    def test_ops_feedback_metrics_eval_and_experiment_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "feedback",
                        "--project",
                        "core",
                        "--submitter",
                        "ou_alice",
                        "--content",
                        "用户反馈：审核通知失败后需要可见修复路径。",
                        "--requirement-ref",
                        "ANOS-REQ-140",
                        "--agent-ref",
                        "agent.company.operations",
                        "--result-ref",
                        "task-results/example.md",
                        "--score",
                        "4",
                    ]
                ),
                0,
            )
            feedback = load_object(next((root / "projects" / "core" / "feedback").glob("feedback*.md")))
            self.assertEqual(feedback["type"], "FeedbackRecord")
            self.assertEqual(feedback["requirementRef"], "ANOS-REQ-140")
            self.assertTrue(feedback["improvementTaskRef"])

            self.assertEqual(main(["--root", str(root), "ops", "experiment", "--project", "core", "--title", "No metric", "--owner", "alice", "--hypothesis", "x", "--audience", "users", "--metric", ""]), 2)
            self.assertEqual(main(["--root", str(root), "eval", "case", "create", "--eval-id", "eval.release", "--title", "Release Gate", "--owner", "alice", "--target-ref", "projects/core/project.md", "--input", "x", "--expected", "must-pass"]), 0)
            self.assertEqual(main(["--root", str(root), "eval", "run", "--eval-id", "eval.release", "--actual", "failed", "--runner", "tester", "--severity", "critical"]), 0)
            self.assertEqual(main(["--root", str(root), "metrics", "report", "--owner", "alice"]), 0)
            metrics = load_object(next((root / "knowledge" / "metrics").glob("metrics*.md")))
            self.assertIn("taskThroughput", metrics)
            self.assertEqual(metrics["releaseBlockingEvalRunCount"], 1)
            self.assertIn("notificationFailureCount", metrics)

    def test_http_shared_api_envelope_admin_disable_and_safe_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            self.assertEqual(main(["--root", str(root), "init", "--user-id", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "project", "register", "--project-id", "core", "--name", "Core", "--owner", "alice"]), 0)
            self.assertEqual(main(["--root", str(root), "tool", "register", "--tool-id", "tool.http", "--name", "HTTP Tool", "--owner", "alice", "--repo", "git@example.com:http.git", "--entrypoint", "echo://ok"]), 0)
            try:
                server = KnowledgeHTTPServer(("127.0.0.1", 0), Bundle(root), api_token="test-token")
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"

            def post(path: str, payload: dict) -> dict:
                request = urllib.request.Request(
                    base + path,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"},
                    method="POST",
                )
                with urllib.request.urlopen(request) as response:
                    return json.loads(response.read().decode("utf-8"))

            try:
                with self.assertRaises(urllib.error.HTTPError) as unauthorized:
                    urllib.request.urlopen(base + "/v0/snapshot")
                self.assertEqual(unauthorized.exception.code, 401)
                error_payload = json.loads(unauthorized.exception.read().decode("utf-8"))
                self.assertEqual(error_payload["kind"], "Error")
                self.assertEqual(error_payload["errorCode"], "UNAUTHORIZED")

                with self.assertRaises(urllib.error.HTTPError) as invalid:
                    post("/v0/command/validate", {"actorRef": "agent.company.development", "sourceChannel": "api", "commandType": "update"})
                invalid_payload = json.loads(invalid.exception.read().decode("utf-8"))
                self.assertEqual(invalid_payload["kind"], "Error")
                self.assertEqual(invalid_payload["errorCode"], "INVALID_ENVELOPE")

                disabled = post(
                    "/v0/admin/disable",
                    {
                        "objectType": "tool",
                        "objectId": "tool.http",
                        "reason": "owner requested rollback",
                        "commandEnvelope": {
                            "actorRef": "human.admin",
                            "actorRole": "System Admin",
                            "sourceChannel": "api",
                            "commandType": "admin.disable",
                            "objectRef": "tool:tool.http",
                            "projectRef": "core",
                            "idempotencyKey": "disable-tool-http-1",
                            "reason": "owner requested rollback",
                            "evidenceRefs": ["projects/core/project.md"],
                        },
                    },
                )
                self.assertEqual(disabled["kind"], "AdminDisableResult")
                self.assertEqual(disabled["commandEnvelope"]["sourceChannel"], "api")
                self.assertEqual(load_object(root / "tools" / "tool.http.md")["status"], "disabled")
            finally:
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()


if __name__ == "__main__":
    unittest.main()
