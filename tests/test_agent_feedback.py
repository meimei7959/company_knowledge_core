from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import subprocess
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


def run_git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=True)


def init_git_repo(root: Path, branch: str = "main", *, detached: bool = False) -> None:
    run_git(root, "init")
    run_git(root, "checkout", "-B", branch)
    if detached:
        run_git(root, "add", ".")
        subprocess.run(
            ["git", "-c", "user.name=Test Agent", "-c", "user.email=test@example.com", "commit", "-m", "test bundle"],
            cwd=root,
            text=True,
            capture_output=True,
            check=True,
        )
        run_git(root, "checkout", "--detach", "HEAD")


def skill_gap_argv(root: Path, skill_id: str = "softcopyright-submission-pack") -> list[str]:
    return [
        "skill-gap",
        "--central-root",
        str(root),
        "--source-project",
        "billing-lite",
        "--skill-id",
        skill_id,
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


def count_task_files(root: Path) -> int:
    return len(list((root / "projects" / "company-knowledge-core" / "tasks").glob("*.md")))


class AgentFeedbackTests(unittest.TestCase):
    def test_system_issue_subcommand_creates_defect_and_pm_fix_task(self) -> None:
        module = load_agent_feedback_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            init_git_repo(root, "main")
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
            init_git_repo(root, "feedback/softcopyright-skill-gap")
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            argv = skill_gap_argv(root)
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


class AgentFeedbackBranchGuardTests(unittest.TestCase):
    def test_skill_gap_allows_codex_branch(self) -> None:
        module = load_agent_feedback_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            init_git_repo(root, "codex/skill-gap-intake")
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(module.main(skill_gap_argv(root, "codex-gap")), 0)
            self.assertEqual(len([line for line in out.getvalue().splitlines() if line.strip()]), 2)

    def test_skill_gap_blocks_main_before_writing_files(self) -> None:
        module = load_agent_feedback_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            init_git_repo(root, "main")
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            tasks_before = count_task_files(root)
            with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(module.main(skill_gap_argv(root, "main-gap")), 1)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("branch 'main' is not allowed", err.getvalue())
            self.assertFalse((root / "skills" / "main-gap.md").exists())
            self.assertEqual(count_task_files(root), tasks_before)

    def test_skill_gap_blocks_feature_branch_before_writing_files(self) -> None:
        module = load_agent_feedback_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            init_git_repo(root, "feature/skill-gap")
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            with contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(module.main(skill_gap_argv(root, "feature-gap")), 1)
            self.assertIn("feature/skill-gap", err.getvalue())
            self.assertFalse((root / "skills" / "feature-gap.md").exists())

    def test_skill_gap_blocks_detached_head_before_writing_files(self) -> None:
        module = load_agent_feedback_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            init_git_repo(root, "feedback/skill-gap", detached=True)
            with contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(module.main(skill_gap_argv(root, "detached-gap")), 1)
            self.assertIn("detached HEAD", err.getvalue())
            self.assertFalse((root / "skills" / "detached-gap.md").exists())

    def test_skill_gap_blocks_non_git_central_root_before_writing_files(self) -> None:
        module = load_agent_feedback_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            with contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(module.main(skill_gap_argv(root, "non-git-gap")), 1)
            self.assertIn("not inside a Git repository", err.getvalue())
            self.assertFalse((root / "skills" / "non-git-gap.md").exists())

    def test_skill_gap_no_review_task_still_blocks_main_before_writing_files(self) -> None:
        module = load_agent_feedback_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            init_git_repo(root, "main")
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            argv = [*skill_gap_argv(root, "main-no-review-gap"), "--no-review-task"]
            tasks_before = count_task_files(root)
            with contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(module.main(argv), 1)
            self.assertIn("branch 'main' is not allowed", err.getvalue())
            self.assertFalse((root / "skills" / "main-no-review-gap.md").exists())
            self.assertEqual(count_task_files(root), tasks_before)

    def test_skill_gap_uses_central_root_git_branch_not_shell_cwd(self) -> None:
        module = load_agent_feedback_module()
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as cwd:
            root = Path(tmp)
            write_minimal_bundle(root)
            init_git_repo(root, "feedback/central-root-branch")
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            old_cwd = os.getcwd()
            try:
                os.chdir(cwd)
                with contextlib.redirect_stdout(io.StringIO()) as out:
                    self.assertEqual(module.main(skill_gap_argv(root, "central-root-gap")), 0)
            finally:
                os.chdir(old_cwd)
            self.assertEqual(len([line for line in out.getvalue().splitlines() if line.strip()]), 2)


class AgentFeedbackSafetyTests(unittest.TestCase):
    def test_duplicate_skill_id_fails_without_overwriting_or_creating_review_task(self) -> None:
        module = load_agent_feedback_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            init_git_repo(root, "feedback/duplicate-skill")
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            base_argv = skill_gap_argv(root)
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
