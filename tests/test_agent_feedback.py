from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

from tests.test_cli import REPO_ROOT, write_minimal_bundle
from zhenzhi_knowledge.core import Bundle, load_object, make_project, validate_bundle


def load_agent_feedback_module():
    spec = importlib.util.spec_from_file_location("agent_feedback_script", REPO_ROOT / "scripts" / "agent_feedback.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AgentFeedbackTests(unittest.TestCase):
    def test_system_issue_subcommand_creates_defect_and_pm_fix_task(self) -> None:
        module = load_agent_feedback_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            argv = [
                "system-issue",
                "--central-root",
                str(root),
                "--source-project",
                "billing-lite",
                "--title",
                "项目经理不理解同步到中枢",
                "--actual",
                "业务项目项目经理不知道如何把体系问题写回中枢。",
                "--expected",
                "业务项目项目经理应创建中枢 Defect 和 PM 分诊任务。",
                "--evidence-ref",
                "screenshot://billing-lite-sync-question",
            ]
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(module.main(argv), 0)
            lines = [line.strip() for line in out.getvalue().splitlines() if line.strip()]
            self.assertEqual(len(lines), 2)
            defect = load_object(root / lines[0])
            task = load_object(root / lines[1])
            self.assertEqual(defect["type"], "Defect")
            self.assertEqual(defect["projectId"], "company-knowledge-core")
            self.assertIn("sourceProject:billing-lite", defect["evidenceRefs"])
            self.assertEqual(task["workSourceType"], "bugfix")
            self.assertEqual(task["assignee"], "agent.company.project-manager")
            self.assertFalse(validate_bundle(Bundle(root)))

    def test_skill_gap_subcommand_creates_draft_skill_and_review_task(self) -> None:
        module = load_agent_feedback_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            argv = [
                "skill-gap",
                "--central-root",
                str(root),
                "--source-project",
                "billing-lite",
                "--skill-id",
                "softcopyright-submission-pack",
                "--name",
                "软著材料整理 Skill",
                "--purpose",
                "沉淀软著材料整理、源码清单、截图证据和提交包检查能力。",
                "--gap",
                "知识工程 Agent 当前缺少软著场景专用检查清单。",
                "--proposed-use",
                "后续软著、运营材料、交付归档项目可复用。",
                "--source-ref",
                "sourceProject:billing-lite",
            ]
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(module.main(argv), 0)
            lines = [line.strip() for line in out.getvalue().splitlines() if line.strip()]
            self.assertEqual(len(lines), 2)
            skill = load_object(root / lines[0])
            task = load_object(root / lines[1])
            self.assertEqual(skill["type"], "SkillAsset")
            self.assertEqual(skill["scope"], "company")
            self.assertEqual(skill["status"], "draft")
            self.assertEqual(skill["reusePolicy"], "review_required_before_company_reuse")
            self.assertEqual(task["assignee"], "agent.company.knowledge-engineering")
            self.assertEqual(task["workSourceType"], "maintenance")
            self.assertFalse(validate_bundle(Bundle(root)))

class AgentFeedbackSafetyTests(unittest.TestCase):
    def test_duplicate_skill_id_fails_without_overwriting_or_creating_review_task(self) -> None:
        module = load_agent_feedback_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            base_argv = [
                "skill-gap",
                "--central-root",
                str(root),
                "--source-project",
                "billing-lite",
                "--skill-id",
                "softcopyright-submission-pack",
                "--name",
                "软著材料整理 Skill",
                "--purpose",
                "沉淀软著材料整理能力。",
                "--gap",
                "缺少场景清单。",
            ]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(module.main(base_argv), 0)
            skill_path = root / "skills" / "softcopyright-submission-pack.md"
            original_skill = skill_path.read_text(encoding="utf-8")
            tasks_dir = root / "projects" / "company-knowledge-core" / "tasks"
            task_count = len(list(tasks_dir.glob("*.md")))

            duplicate_argv = [
                *base_argv[:-4],
                "--name",
                "覆盖后的名字",
                "--purpose",
                "这次不应该写入。",
                "--gap",
                "重复 ID。",
            ]
            with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(module.main(duplicate_argv), 1)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("SkillAsset already exists", err.getvalue())
            self.assertEqual(skill_path.read_text(encoding="utf-8"), original_skill)
            self.assertEqual(len(list(tasks_dir.glob("*.md"))), task_count)

class AgentFeedbackCliErrorTests(unittest.TestCase):
    def test_missing_subcommand_error_points_to_supported_commands(self) -> None:
        module = load_agent_feedback_module()
        with contextlib.redirect_stderr(io.StringIO()) as err:
            with self.assertRaises(SystemExit) as raised:
                module.main([])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("Use one feedback subcommand", err.getvalue())
        self.assertIn("system-issue", err.getvalue())
        self.assertIn("skill-gap", err.getvalue())


if __name__ == "__main__":
    unittest.main()
