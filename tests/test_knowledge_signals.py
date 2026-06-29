import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from zhenzhi_knowledge.cli import main
from zhenzhi_knowledge.core import Bundle, load_object, validate_bundle


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


VALID_SIGNAL = """---
signalId: ks-zknow-agent-20260628-001
sourceProjectId: zknow-agent
sourceTaskId: task-feishu-workbench-link-debug-001
title: 飞书工作台 Web App 外链跳转需检查企业管理后台 Link Security
knowledgeDomain: engineering
knowledgeType: troubleshooting
candidateConclusion: >
  遇到飞书工作台 Web App 外链跳转或 lk_jump_to_browser 问题时，
  不应只检查开放平台域名配置，还要检查企业管理后台 Link Security
  白名单功能是否开启并生效。
appliesWhen:
  - 飞书工作台 Web App 打开内部域名时被判定为外链
  - 飞书出现 lk_jump_to_browser 跳转
  - 开放平台域名配置看起来已经正确，但仍然异常
doesNotApplyWhen:
  - 域名本身没有完成备案或 HTTPS 配置
  - Web App URL 配置错误
  - 飞书应用没有正确发布到工作台
sourceRefs:
  - projects/zknow-agent/lessons.md
  - projects/zknow-agent/log.md
evidenceRefs:
  - "现象：开放平台配置有效，但 team.zknowai.com 仍被判定为外链"
  - "根因：企业管理后台 Link Security 白名单功能未开启"
keywords:
  - 飞书工作台
  - Web App
  - Link Security
  - lk_jump_to_browser
  - 外链白名单
confidence: high
riskLevel: low
skillImpact:
  hasImpact: true
  suggestedImpact: "可加入飞书集成排障 Skill 的检查清单"
  autoApplyAllowed: false
toolImpact:
  hasImpact: false
  suggestedImpact: ""
humanOwnerConfirmationRequired: false
---

# 补充说明

这是一条从 zknow-agent 项目排障中提炼出的可复用经验。
"""


def write_signal(root: Path, project: str = "zknow-agent", name: str = "feishu.md", text: str = VALID_SIGNAL) -> Path:
    path = root / "projects" / project / ".zhenzhi" / "knowledge-signals" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def run_cli(root: Path, *args: str) -> str:
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        code = main(["--root", str(root), *args])
    if code not in (None, 0):
        raise AssertionError(f"CLI failed with code {code}: {stream.getvalue()}")
    return stream.getvalue()


class KnowledgeSignalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.previous_database_url = os.environ.pop("DATABASE_URL", None)

    def tearDown(self) -> None:
        if self.previous_database_url is not None:
            os.environ["DATABASE_URL"] = self.previous_database_url

    def test_lessons_and_log_are_not_scanned_without_signal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            project = root / "projects" / "demo"
            project.mkdir(parents=True, exist_ok=True)
            (project / "lessons.md").write_text("# Lessons\n\n- Reusable but not submitted.\n", encoding="utf-8")
            (project / "log.md").write_text("# Log\n\n- Reusable but not submitted.\n", encoding="utf-8")

            output = run_cli(root, "knowledge", "distill-signals")

            self.assertIn("Scanned 0 knowledge signals.", output)
            self.assertFalse((root / "knowledge" / "index.jsonl").exists())
            self.assertFalse(list((root / "knowledge").glob("engineering/*.md")))

    def test_valid_signal_generates_draft_indexes_gap_and_is_searchable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            write_signal(root)

            output = run_cli(root, "knowledge", "distill-signals")

            self.assertIn("Distilled: 1", output)
            knowledge_files = list((root / "knowledge" / "engineering").glob("*.md"))
            self.assertEqual(1, len(knowledge_files))
            item = load_object(knowledge_files[0])
            self.assertEqual("KnowledgeItem", item["type"])
            self.assertEqual("draft", item["status"])
            self.assertEqual("high", item["confidence"])
            self.assertEqual("zknow-agent", item["sourceProjectId"])
            self.assertTrue(item["sourceRefs"])
            self.assertTrue(item["evidenceRefs"])
            self.assertTrue(item["appliesWhen"])
            self.assertTrue(item["fingerprint"])
            self.assertTrue((root / "knowledge" / "index.md").read_text(encoding="utf-8").count(str(item["knowledgeId"])) == 1)
            index_rows = [json.loads(line) for line in (root / "knowledge" / "index.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(1, len(index_rows))
            self.assertEqual(item["knowledgeId"], index_rows[0]["knowledgeId"])
            gaps = list((root / "knowledge" / "gaps" / "agent-capability").glob("*.md"))
            self.assertEqual(1, len(gaps))
            self.assertFalse((root / "capabilities").exists())
            search_output = run_cli(root, "knowledge", "search", "lk_jump_to_browser")
            self.assertIn(str(item["knowledgeId"]), search_output)
            self.assertFalse([problem for problem in validate_bundle(Bundle(root)) if "KnowledgeItem" in problem])

    def test_missing_evidence_refs_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            write_signal(root, text=VALID_SIGNAL.replace("evidenceRefs:\n  - \"现象：开放平台配置有效，但 team.zknowai.com 仍被判定为外链\"\n  - \"根因：企业管理后台 Link Security 白名单功能未开启\"\n", ""))

            output = run_cli(root, "knowledge", "distill-signals")

            self.assertIn("Invalid: 1", output)
            self.assertFalse(list((root / "knowledge").glob("engineering/*.md")))
            states = list((root / "knowledge" / ".state" / "distilled-signals").glob("*.json"))
            self.assertEqual(1, len(states))
            state = json.loads(states[0].read_text(encoding="utf-8"))
            self.assertEqual("invalid", state["status"])
            self.assertIn("missing evidenceRefs", state["errors"])

    def test_repeated_run_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            write_signal(root)

            run_cli(root, "knowledge", "distill-signals")
            output = run_cli(root, "knowledge", "distill-signals")

            self.assertIn("Already processed: 1", output)
            self.assertEqual(1, len(list((root / "knowledge" / "engineering").glob("*.md"))))
            index_text = (root / "knowledge" / "index.md").read_text(encoding="utf-8")
            self.assertEqual(1, index_text.count("knowledgeId:"))
            self.assertEqual(1, len((root / "knowledge" / "index.jsonl").read_text(encoding="utf-8").splitlines()))

    def test_same_fingerprint_different_file_is_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            write_signal(root, name="one.md")
            write_signal(root, name="two.md", text=VALID_SIGNAL.replace("ks-zknow-agent-20260628-001", "ks-zknow-agent-20260628-002"))

            output = run_cli(root, "knowledge", "distill-signals")

            self.assertIn("Distilled: 1", output)
            self.assertIn("Duplicate: 1", output)
            self.assertEqual(1, len(list((root / "knowledge" / "engineering").glob("*.md"))))

    def test_tool_impact_creates_only_tool_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            signal = VALID_SIGNAL.replace("hasImpact: false\n  suggestedImpact: \"\"\nhumanOwnerConfirmationRequired", "hasImpact: true\n  suggestedImpact: \"需要工具检查 Link Security 配置\"\nhumanOwnerConfirmationRequired")
            write_signal(root, text=signal)

            run_cli(root, "knowledge", "distill-signals")

            self.assertEqual(1, len(list((root / "knowledge" / "gaps" / "tool-capability").glob("*.md"))))
            self.assertFalse((root / "tools" / "tool.link-security.md").exists())

    def test_high_risk_is_restricted_and_hidden_from_default_search(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            signal = VALID_SIGNAL.replace("riskLevel: low", "riskLevel: high").replace("lk_jump_to_browser", "access_token")
            write_signal(root, text=signal)

            run_cli(root, "knowledge", "distill-signals")

            item = load_object(next((root / "knowledge" / "engineering").glob("*.md")))
            self.assertTrue(item["reviewRequired"])
            self.assertTrue(item["restricted"])
            self.assertTrue(list((root / "knowledge" / "review").glob("*.md")))
            self.assertNotIn(str(item["knowledgeId"]), run_cli(root, "knowledge", "search", "access_token"))
            self.assertIn(str(item["knowledgeId"]), run_cli(root, "knowledge", "search", "access_token", "--include-restricted"))


if __name__ == "__main__":
    unittest.main()
