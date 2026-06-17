import tempfile
import threading
import unittest
import urllib.request
import urllib.error
import json
import os
from pathlib import Path

from zhenzhi_knowledge.cli import main
from zhenzhi_knowledge.core import Bundle
from zhenzhi_knowledge.server import KnowledgeHTTPServer


def write_minimal_bundle(root: Path) -> None:
    for directory in ["projects", "agents", "tools", "knowledge", "runs"]:
        (root / directory).mkdir(parents=True, exist_ok=True)
        (root / directory / "index.md").write_text(f"# {directory}\n", encoding="utf-8")
    (root / "index.md").write_text("# Index\n", encoding="utf-8")
    (root / "log.md").write_text("# Log\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")


class CliTests(unittest.TestCase):
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
            self.assertIn("knowledge/engineering/parser-context.md", runs[0].read_text(encoding="utf-8"))
            self.assertEqual(main(["--root", str(root), "review", "update", "--target", str(runs[0]), "--status", "verified", "--reviewer", "alice"]), 0)
            self.assertTrue(list((root / "knowledge" / "audit").glob("*.md")))
            self.assertTrue((root / "knowledge" / "policies" / "policy.alice.md").exists())
            self.assertEqual(main(["--root", str(root), "review", "list"]), 0)
            self.assertEqual(main(["--root", str(root), "review", "bulk", "--type", "ToolAsset", "--from-status", "testing", "--to-status", "approved", "--reviewer", "alice", "--limit", "1"]), 0)
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
            self.assertTrue((root / ".zhenzhi" / "index.sqlite3").exists())
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

            try:
                server = KnowledgeHTTPServer(("127.0.0.1", 0), Bundle(root), api_token="test-token")
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"
            previous_api = os.environ.get("ZHENZHI_KNOWLEDGE_API_STAGING")
            previous_token = os.environ.get("ZHENZHI_KNOWLEDGE_API_TOKEN_STAGING")
            os.environ["ZHENZHI_KNOWLEDGE_API_STAGING"] = base
            try:
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
                self.assertTrue(list((root / "projects" / "a" / "sources").glob("source.*.md")))
                material_drafts = list((root / "knowledge" / "engineering").glob("feishu-material.*.md"))
                self.assertTrue(material_drafts)
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
                target = str(material_drafts[0].relative_to(root))
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
                self.assertIn("status: verified", material_drafts[0].read_text(encoding="utf-8"))
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
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()

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


if __name__ == "__main__":
    unittest.main()
