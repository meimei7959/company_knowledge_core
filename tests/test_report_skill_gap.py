from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

from tests.test_agent_feedback import init_git_repo
from tests.test_cli import REPO_ROOT, write_minimal_bundle
from zhenzhi_knowledge.core import Bundle, load_object, make_project, validate_bundle


def load_skill_gap_script_module():
    spec = importlib.util.spec_from_file_location("report_skill_gap_script", REPO_ROOT / "scripts" / "report_skill_gap.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReportSkillGapTests(unittest.TestCase):
    def test_business_project_can_report_reusable_skill_gap_to_central(self) -> None:
        module = load_skill_gap_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            init_git_repo(root, "feedback/report-skill-gap")
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            old_argv = sys.argv
            try:
                sys.argv = [
                    "report_skill_gap.py",
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
                    self.assertEqual(module.main(), 0)
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
            finally:
                sys.argv = old_argv

    def test_legacy_wrapper_preserves_no_review_task(self) -> None:
        module = load_skill_gap_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            init_git_repo(root, "feedback/report-skill-gap-no-review")
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            old_argv = sys.argv
            try:
                sys.argv = [
                    "report_skill_gap.py",
                    "--central-root",
                    str(root),
                    "--source-project",
                    "billing-lite",
                    "--skill-id",
                    "local-gap-only",
                    "--name",
                    "本地缺口 Skill",
                    "--purpose",
                    "验证旧脚本 no-review-task 兼容。",
                    "--gap",
                    "旧脚本需要继续只输出 SkillAsset。",
                    "--no-review-task",
                ]
                with contextlib.redirect_stdout(io.StringIO()) as out:
                    self.assertEqual(module.main(), 0)
                lines = [line.strip() for line in out.getvalue().splitlines() if line.strip()]
                self.assertEqual(len(lines), 1)
                skill = load_object(root / lines[0])
                self.assertEqual(skill["type"], "SkillAsset")
                self.assertFalse(validate_bundle(Bundle(root)))
            finally:
                sys.argv = old_argv

    def test_legacy_wrapper_blocks_no_review_task_on_main_before_writing(self) -> None:
        module = load_skill_gap_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            init_git_repo(root, "main")
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            old_argv = sys.argv
            try:
                sys.argv = [
                    "report_skill_gap.py",
                    "--central-root",
                    str(root),
                    "--source-project",
                    "billing-lite",
                    "--skill-id",
                    "main-wrapper-gap",
                    "--name",
                    "本地缺口 Skill",
                    "--purpose",
                    "验证旧脚本 main 分支阻断。",
                    "--gap",
                    "旧脚本也必须先过分支治理。",
                    "--no-review-task",
                ]
                with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
                    self.assertEqual(module.main(), 1)
                self.assertEqual(out.getvalue(), "")
                self.assertIn("branch 'main' is not allowed", err.getvalue())
                self.assertFalse((root / "skills" / "main-wrapper-gap.md").exists())
            finally:
                sys.argv = old_argv


if __name__ == "__main__":
    unittest.main()
