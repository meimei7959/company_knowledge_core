import tempfile
import threading
import unittest
import urllib.request
import urllib.error
import json
import os
from pathlib import Path

import zhenzhi_knowledge.feishu as feishu_module
from zhenzhi_knowledge.cli import main
from zhenzhi_knowledge.core import Bundle
from zhenzhi_knowledge.feishu import save_approval_request
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
            os.environ["ZHENZHI_KNOWLEDGE_API_STAGING"] = base
            os.environ["FEISHU_ALLOW_UNSIGNED_EVENTS"] = "true"
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

    def test_token_approval_sends_only_to_submitter_when_enabled(self) -> None:
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
                token_send_on_approval=True,
                approval_doc_wiki_node="",
                approval_doc_domain="https://xcn68awb7dsi.feishu.cn",
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
                self.assertIn("prod-token", sent[0][1])
            finally:
                feishu_module.send_feishu_message = original_send
                if previous_token is None:
                    os.environ.pop("ZHENZHI_KNOWLEDGE_API_TOKEN", None)
                else:
                    os.environ["ZHENZHI_KNOWLEDGE_API_TOKEN"] = previous_token

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
                approval_doc_wiki_node="",
                approval_doc_domain="https://xcn68awb7dsi.feishu.cn",
                user_open_id_map={},
            )
            created: dict[str, object] = {}
            original_create = feishu_module.create_feishu_approval_instance
            def fake_create_approval(_settings, requester_open_id, approval_code, approver_open_ids, form_values):
                created.update(
                    {
                        "requester": requester_open_id,
                        "approval_code": approval_code,
                        "approvers": approver_open_ids,
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
                self.assertIn("已生成项目立项草稿", reply)
                self.assertTrue((root / "projects" / "a" / "project.md").exists())
                self.assertEqual(created["approval_code"], "approval_project")
                self.assertEqual(created["approvers"], ["ou_common"])
                self.assertEqual(created["form_values"]["approval_type"], "project_init")
                self.assertEqual(created["form_values"]["owner_open_id"], "ou_owner")
            finally:
                feishu_module.create_feishu_approval_instance = original_create

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
                approval_doc_wiki_node="",
                approval_doc_domain="https://xcn68awb7dsi.feishu.cn",
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
            self.assertIn("我识别到这是项目立项", reply)
            self.assertIn("工业软件点胶机", reply)
            self.assertIn("hanson", reply)
            self.assertIn("通讯录读取权限", reply)
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
                approval_doc_wiki_node="",
                approval_doc_domain="https://xcn68awb7dsi.feishu.cn",
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
                self.assertIn("已生成项目立项草稿", reply)
                self.assertIn("ou_hanson", reply)
            finally:
                feishu_module.create_feishu_approval_instance = original_create

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
                approval_doc_wiki_node="",
                approval_doc_domain="https://xcn68awb7dsi.feishu.cn",
                user_open_id_map={},
            )
            original_send = feishu_module.send_feishu_reply
            feishu_module.send_feishu_reply = lambda *_args, **_kwargs: (_ for _ in ()).throw(feishu_module.KnowledgeError("reply failed"))
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
                feishu_module.send_feishu_reply = original_send

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
                approval_doc_wiki_node="GZ59w7hsNijjXYk9BNocCQjFnpc",
                approval_doc_domain="https://xcn68awb7dsi.feishu.cn",
                user_open_id_map={},
            )
            created: dict[str, object] = {}
            original_doc = feishu_module.create_approval_change_doc
            original_instance = feishu_module.create_feishu_approval_instance

            def fake_doc(_bundle, _settings, values):
                created["doc_values"] = dict(values)
                return {"url": "https://xcn68awb7dsi.feishu.cn/wiki/doc_node", "nodeToken": "doc_node", "objToken": "doc_obj"}

            def fake_instance(_settings, requester_open_id, approval_code, approver_open_ids, form_values):
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


if __name__ == "__main__":
    unittest.main()
