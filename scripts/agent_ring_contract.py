#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from zhenzhi_knowledge.cli import main as cli_main
from zhenzhi_knowledge.core import Bundle, KnowledgeError, update_frontmatter_file
from zhenzhi_knowledge.server import KnowledgeHTTPServer


TOKEN = "agent-ring-contract-token"


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
    ]:
        (root / directory).mkdir(parents=True, exist_ok=True)
        (root / directory / "index.md").write_text(f"# {directory}\n", encoding="utf-8")
    (root / "index.md").write_text("# Index\n", encoding="utf-8")
    (root / "log.md").write_text("# Log\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")


def create_fixture(root: Path) -> None:
    write_minimal_bundle(root)
    run_cli(["--root", str(root), "project", "register", "--project-id", "contract-core", "--name", "Contract Core", "--owner", "agent-ring"])
    run_cli(["--root", str(root), "agent", "register", "--agent-id", "agent.contract.codex", "--name", "Contract Codex", "--owner", "agent-ring", "--purpose", "contract fixture executor"])
    run_cli(
        [
            "--root",
            str(root),
            "policy",
            "register",
            "--policy-id",
            "policy.agent-contract-codex",
            "--title",
            "Contract Codex Write Policy",
            "--agent-id",
            "agent.contract.codex",
            "--owner",
            "agent-ring",
            "--allow-project",
            "contract-core",
            "--allow-scope",
            "engineering",
            "--allow-risk",
            "L1",
        ]
    )
    update_frontmatter_file(root / "knowledge" / "policies" / "policy.agent-contract-codex.md", {"status": "active"})
    source = root / "projects" / "contract-core" / "sources" / "sm-contract-note.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        """---
type: SourceMaterial
title: Contract Note
description: Agent Ring contract fixture source.
timestamp: 2026-06-19T00:00:00Z
sourceId: SM-CONTRACT-NOTE
sourceType: test
sourceRef: contract://source/note
owner: agent-ring
status: draft
projectId: contract-core
---

## Original Text

Agent Ring must claim tasks, pull portable context, execute locally, and write back TaskResult evidence.
""",
        encoding="utf-8",
    )
    create_task(root, "KT-CONTRACT-HAPPY", "Happy path", "runner.contract", source)
    create_task(root, "KT-CONTRACT-IMPROVE", "Improvement path", "runner.contract", source)
    create_task(root, "KT-CONTRACT-EXPIRED", "Expired lease", "runner.contract", source)
    create_task(root, "KT-CONTRACT-MISSING-CAP", "Missing capability", "runner.limited", source)
    task = root / "projects" / "contract-core" / "tasks" / "kt-contract-missing-cap.md"
    task.write_text(
        task.read_text(encoding="utf-8").replace(
            "resultRef:",
            "requiredCapabilities:\n  - engineering_action\nresultRef:",
        ),
        encoding="utf-8",
    )


def create_task(root: Path, task_id: str, title: str, assignee: str, source: Path) -> None:
    run_cli(
        [
            "--root",
            str(root),
            "task",
            "create",
            "--task-id",
            task_id,
            "--title",
            title,
            "--project",
            "contract-core",
            "--requester",
            "agent-ring-contract",
            "--assignee",
            assignee,
            "--source",
            str(source.relative_to(root)),
        ]
    )


def run_contract(root: Path, token: str = TOKEN) -> dict[str, Any]:
    server = KnowledgeHTTPServer(("127.0.0.1", 0), Bundle(root), api_token=token)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    checks: list[str] = []

    try:
        health = get(base, "/health", token="")
        assert_equal(health["ok"], True, "health ok")
        checks.append("health")

        expect_http_error(lambda: get(base, "/v0/tasks", token=""), 401, "unauthorized task query")
        checks.append("unauthorized")

        runner = post(
            base,
            "/v0/runners/register",
            {
                "runnerId": "runner.contract",
                "name": "Contract Runner",
                "hostType": "test",
                "mode": "unattended",
                "agents": ["codex", "claude"],
                "capabilities": ["knowledge_capture", "contract_tests"],
                "availableProjects": ["contract-core"],
                "ringVersion": "contract-0.1",
            },
            token,
        )
        assert_equal(runner["kind"], "Runner", "runner register")
        checks.append("runner_register")

        heartbeat = post(base, "/v0/runners/heartbeat", {"runnerId": "runner.contract", "status": "online", "load": "0"}, token)
        assert_equal(heartbeat["kind"], "RunnerHeartbeat", "runner heartbeat")
        checks.append("runner_heartbeat")

        tasks = get(base, "/v0/tasks?status=pending&assignee=runner.contract", token)
        assert_true(any(task["taskId"] == "KT-CONTRACT-HAPPY" for task in tasks["tasks"]), "task query returns happy task")
        checks.append("task_query")

        claim = post(base, "/v0/tasks/claim", {"taskId": "KT-CONTRACT-HAPPY", "runnerId": "runner.contract", "expectedVersion": 1}, token)
        assert_equal(claim["kind"], "TaskClaim", "task claim")
        lease_token = claim["leaseToken"]
        checks.append("task_claim")

        expect_http_error(
            lambda: post(base, "/v0/tasks/claim", {"taskId": "KT-CONTRACT-HAPPY", "runnerId": "runner.contract", "expectedVersion": 1}, token),
            400,
            "stale expectedVersion",
        )
        checks.append("stale_version")

        expect_http_error(
            lambda: post(
                base,
                "/v0/tasks/finish",
                {"taskId": "KT-CONTRACT-HAPPY", "runnerId": "runner.contract", "leaseToken": "wrong", "summary": "wrong lease"},
                token,
            ),
            400,
            "invalid lease",
        )
        checks.append("invalid_lease")

        context = post(base, "/v0/tasks/pull", {"taskId": "KT-CONTRACT-HAPPY", "runnerId": "runner.contract", "leaseToken": lease_token}, token)
        assert_equal(context["kind"], "TaskContext", "task pull")
        assert_true("portable context" in context["context"], "context contains source material")
        checks.append("task_pull")

        task_heartbeat = post(
            base,
            "/v0/tasks/heartbeat",
            {"taskId": "KT-CONTRACT-HAPPY", "runnerId": "runner.contract", "leaseToken": lease_token},
            token,
        )
        assert_equal(task_heartbeat["kind"], "TaskHeartbeat", "task heartbeat")
        checks.append("task_heartbeat")

        finish = post(
            base,
            "/v0/tasks/finish",
            {
                "taskId": "KT-CONTRACT-HAPPY",
                "runnerId": "runner.contract",
                "leaseToken": lease_token,
                "executorAgent": "agent.contract.codex",
                "result": "done",
                "summary": "Contract runner wrote back deterministic TaskResult.",
                "evidenceRefs": ["projects/contract-core/sources/sm-contract-note.md"],
                "testsOrChecks": ["agent_ring_contract.py"],
                "knowledgeDraft": {
                    "title": "Agent Ring contract task lifecycle",
                    "summary": "Contract runner writes back TaskResult, KnowledgeItem draft, and source evidence.",
                    "structured": "Agent Ring runner must return structured knowledge draft with source evidence when completing KnowledgeTask.",
                    "sourceRefs": ["projects/contract-core/sources/sm-contract-note.md"],
                    "confidence": "medium",
                    "scope": "engineering",
                    "limits": ["Contract harness fixture."],
                },
            },
            token,
        )
        assert_equal(finish["kind"], "TaskResult", "task finish")
        assert_equal(finish["task"]["status"], "done", "task finish status")
        checks.append("task_finish")

        improve_claim = post(base, "/v0/tasks/claim", {"taskId": "KT-CONTRACT-IMPROVE", "runnerId": "runner.contract"}, token)
        improve_finish = post(
            base,
            "/v0/tasks/finish",
            {
                "taskId": "KT-CONTRACT-IMPROVE",
                "runnerId": "runner.contract",
                "leaseToken": improve_claim["leaseToken"],
                "executorAgent": "agent.contract.codex",
                "result": "done",
                "summary": "Contract runner intentionally omitted knowledge draft to trigger improvement.",
            },
            token,
        )
        assert_equal(improve_finish["kind"], "TaskResult", "improvement task finish")
        assert_equal(improve_finish["task"]["status"], "changes_requested", "improvement task status")
        assert_equal(improve_finish["taskResult"]["qualityEvaluation"]["decision"], "retry_required", "improvement quality decision")
        improvement_notifications = get(
            base,
            "/v0/notifications?status=pending&recipient=agent.contract.codex&messageType=agent_improvement_action_required",
            token,
        )
        assert_true(bool(improvement_notifications["notifications"]), "agent improvement notification exists")
        report = post(
            base,
            "/v0/agents/report",
            {"agentId": "agent.contract.codex", "projectId": "contract-core", "owner": "agent-ring-contract"},
            token,
        )
        assert_equal(report["kind"], "AgentCapabilityReport", "agent capability report")
        assert_true(report["reportRef"].startswith("knowledge/metrics/agent-capability-"), "agent capability report ref")
        checks.append("agent_improvement")
        checks.append("agent_capability_report")

        discussion = post(
            base,
            "/v0/discussions/create",
            {
                "title": "Contract discussion",
                "projectId": "contract-core",
                "requester": "agent.company.project-manager",
                "topic": "Validate Agent Ring discussion writeback.",
                "participantAgents": ["agent.company.development", "agent.company.test"],
            },
            token,
        )
        assert_equal(discussion["kind"], "DiscussionSession", "discussion create")
        checks.append("discussion_create")

        notifications = get(
            base,
            f"/v0/notifications?status=pending&recipient=agent.company.development&discussionId={discussion['discussionId']}",
            token,
        )
        assert_equal(notifications["kind"], "NotificationList", "notification list")
        assert_true(bool(notifications["notifications"]), "discussion turn notification exists")
        delivered = post(
            base,
            "/v0/notifications/delivery",
            {
                "notificationId": notifications["notifications"][0]["notificationId"],
                "status": "sent",
                "actor": "agent-ring-contract",
                "deliveryRef": "contract://notification/discussion-turn",
            },
            token,
        )
        assert_equal(delivered["notification"]["status"], "sent", "notification delivery ack")
        checks.append("notification_delivery")

        dev_turn = post(
            base,
            "/v0/discussions/turn",
            {
                "discussionId": discussion["discussionId"],
                "agentId": "agent.company.development",
                "content": "Development Agent can write back a role turn through Agent Ring.",
            },
            token,
        )
        assert_equal(dev_turn["kind"], "DiscussionTurn", "discussion turn")
        test_turn = post(
            base,
            "/v0/discussions/turn",
            {
                "discussionId": discussion["discussionId"],
                "agentId": "agent.company.test",
                "content": "Test Agent requires notification and follow-up task evidence.",
            },
            token,
        )
        assert_equal(test_turn["sessionStatus"], "pm_reviewing", "discussion ready for summary")
        checks.append("discussion_turns")

        discussion_summary = post(
            base,
            "/v0/discussions/finalize",
            {
                "discussionId": discussion["discussionId"],
                "facilitator": "agent.company.project-manager",
                "summary": "Contract discussion finalized.",
                "consensus": "Agent Ring can write discussion turns and summaries.",
                "decision": "Use /v0/discussions/* for phase-1 discussion protocol.",
                "followupTaskTitle": "Implement workbench discussion integration",
                "followupAssignee": "agent.company.development",
            },
            token,
        )
        assert_equal(discussion_summary["status"], "next_task_created", "discussion finalize")
        assert_true(bool(discussion_summary["decisionRefs"]), "discussion creates decision")
        assert_true(bool(discussion_summary["followupTaskRefs"]), "discussion creates followup task")
        checks.append("discussion_finalize")

        post(
            base,
            "/v0/runners/register",
            {
                "runnerId": "runner.limited",
                "name": "Limited Runner",
                "hostType": "test",
                "agents": ["codex"],
                "capabilities": ["knowledge_capture"],
                "availableProjects": ["contract-core"],
            },
            token,
        )
        expect_http_error(lambda: post(base, "/v0/tasks/claim", {"taskId": "KT-CONTRACT-MISSING-CAP", "runnerId": "runner.limited"}, token), 400, "missing capability")
        checks.append("missing_capability")

        expired_claim = post(base, "/v0/tasks/claim", {"taskId": "KT-CONTRACT-EXPIRED", "runnerId": "runner.contract"}, token)
        expired_task = root / "projects" / "contract-core" / "tasks" / "kt-contract-expired.md"
        expired_task.write_text(
            expired_task.read_text(encoding="utf-8").replace(expired_claim["leaseExpiresAt"], "2000-01-01T00:00:00Z"),
            encoding="utf-8",
        )
        expect_http_error(
            lambda: post(
                base,
                "/v0/tasks/finish",
                {"taskId": "KT-CONTRACT-EXPIRED", "runnerId": "runner.contract", "leaseToken": expired_claim["leaseToken"], "summary": "expired"},
                token,
            ),
            400,
            "expired lease",
        )
        checks.append("expired_lease")

        run_cli(["--root", str(root), "validate"])
        checks.append("bundle_validate")
        return {"ok": True, "base": base, "root": str(root), "checks": checks}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def get(base: str, path: str, token: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    request = urllib.request.Request(base + path, headers=headers)
    return json.load(urllib.request.urlopen(request))


def post(base: str, path: str, payload: dict[str, Any], token: str) -> dict[str, Any]:
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    request = urllib.request.Request(base + path, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    return json.load(urllib.request.urlopen(request))


def expect_http_error(callable_obj, status: int, label: str) -> None:
    try:
        callable_obj()
    except urllib.error.HTTPError as exc:
        if exc.code == status:
            return
        raise AssertionError(f"{label}: expected HTTP {status}, got HTTP {exc.code}") from exc
    raise AssertionError(f"{label}: expected HTTP {status}, got success")


def assert_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def assert_true(value: bool, label: str) -> None:
    if not value:
        raise AssertionError(label)


def require_ok(exit_code: int) -> None:
    if exit_code != 0:
        raise SystemExit(exit_code)


def run_cli(args: list[str]) -> None:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        require_ok(cli_main(args))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Agent Ring contract checks against the central processor HTTP API.")
    parser.add_argument("--root", help="Existing or new local bundle root. If omitted, a temporary fixture is used.")
    parser.add_argument("--token", default=TOKEN, help="API token for the local contract server.")
    parser.add_argument("--keep", action="store_true", help="Keep the generated temporary bundle for inspection.")
    args = parser.parse_args()

    if not os.environ.get("DATABASE_URL") and not os.environ.get("ZHENZHI_KNOWLEDGE_DATABASE_URL"):
        print(
            "DATABASE_URL is required and must point to PostgreSQL before running this contract script.\n"
            "Example:\n"
            "  export DATABASE_URL='postgresql://user:password@host:5432/company_knowledge_core'\n"
            "SQLite is intentionally not supported for central-processor contract checks.",
            file=sys.stderr,
        )
        return 2

    if args.root:
        root = Path(args.root).resolve()
        root.mkdir(parents=True, exist_ok=True)
        create_fixture(root)
        try:
            result = run_contract(root, args.token)
        except KnowledgeError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    tmp = tempfile.mkdtemp(prefix="agent-ring-contract-")
    root = Path(tmp)
    try:
        create_fixture(root)
        try:
            result = run_contract(root, args.token)
        except KnowledgeError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.keep:
            print(f"kept fixture: {root}")
        return 0
    finally:
        if not args.keep:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
