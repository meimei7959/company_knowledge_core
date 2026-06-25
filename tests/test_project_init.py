from __future__ import annotations

import contextlib
import importlib.util
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.test_cli import REPO_ROOT, write_minimal_bundle
from zhenzhi_knowledge.core import Bundle, load_object, validate_bundle


def load_script_module():
    spec = importlib.util.spec_from_file_location("init_project_script", REPO_ROOT / "scripts" / "init_project.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_pm_script_module():
    spec = importlib.util.spec_from_file_location("pm_init_project_script", REPO_ROOT / "scripts" / "pm_init_project.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def external_workspace(root: Path, suffix: str) -> Path:
    return root.parent / f"{root.name}-{suffix}"


def assert_feedback_governance_text(testcase: unittest.TestCase, agents: str, start_here: str) -> None:
    testcase.assertIn("Do not write skill-gap feedback directly on `main`.", agents)
    testcase.assertIn("Push the feedback branch", agents)
    testcase.assertIn("Knowledge Engineering / PM to review it", agents)
    testcase.assertIn("不要直接写 `main`", start_here)
    testcase.assertIn("推送这个分支", start_here)
    testcase.assertIn("知识工程/PM 评审", start_here)


def assert_delivery_thinking_text(testcase: unittest.TestCase, agents: str, start_here: str) -> None:
    testcase.assertIn("Agent Delivery Thinking Framework", agents)
    testcase.assertIn("docs/agent-team/agent-delivery-thinking-framework.md", agents)
    testcase.assertIn("Do not just fill templates", agents)
    testcase.assertIn("ReceiverReview checks whether the upstream output can be used", agents)
    testcase.assertIn("不要只填模板", start_here)
    testcase.assertIn("目标、对象、状态、路径、异常、依赖、证据、门禁和下一步", start_here)
    testcase.assertIn("下游接收 Agent 必须做 ReceiverReview", start_here)


class ProjectInitBoundaryTests(unittest.TestCase):
    def test_workspace_inside_central_root_is_rejected(self) -> None:
        module = load_script_module()
        workspace = REPO_ROOT / "projects" / "__bad_workspace_for_test__"
        old_argv = sys.argv
        try:
            sys.argv = [
                "init_project.py",
                "--root",
                str(REPO_ROOT),
                "--project-id",
                "bad",
                "--name",
                "Bad",
                "--owner",
                "meimei",
                "--workspace-ref",
                str(workspace),
            ]
            with contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(module.main(), 1)
            self.assertIn("project workspace must not be inside company_knowledge_core", err.getvalue())
            self.assertFalse(workspace.exists())
        finally:
            sys.argv = old_argv


class ProjectInitRuntimeTests(unittest.TestCase):
    def test_pm_action_is_created_for_project_initialization(self) -> None:
        module = load_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = external_workspace(root, "demo-workspace")
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
                    "--workspace-ref",
                    str(workspace),
                    "--goal",
                    "Initialize Demo",
                ]
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(module.main(), 0)
                pm_actions = sorted((root / "projects" / "demo" / "pm-actions").glob("pm-action.*.md"))
                self.assertEqual(len(pm_actions), 1)
                pm_action = load_object(pm_actions[0])
                self.assertEqual(pm_action["actor"], "agent.company.project-manager")
                self.assertEqual(pm_action["exitState"], "dispatched")
                task_refs = pm_action.get("recordsWritten", [])
                self.assertTrue(any(ref.endswith("project-init-demo-product-scope.md") for ref in task_refs))
                self.assertTrue((root / "projects" / "demo" / "tasks" / "project-init-demo-product-scope.md").is_file())
                init_task = load_object(root / "projects" / "demo" / "tasks" / "project-init-demo.md")
                self.assertEqual(init_task["title"], "Demo 项目初始化")
                task_index = (root / "projects" / "demo" / "tasks" / "index.md").read_text(encoding="utf-8")
                self.assertIn("[Demo 项目初始化](project-init-demo.md)", task_index)
                self.assertNotIn("Initialize project: Demo", task_index)
                project_log = (root / "projects" / "demo" / "log.md").read_text(encoding="utf-8")
                self.assertIn("registered project Demo (demo)", project_log)
                launch = (root / "projects" / "demo" / "launch.md").read_text(encoding="utf-8")
                self.assertIn("## 项目接入信息", launch)
                self.assertIn("## 初始化检查清单", launch)
                self.assertFalse(validate_bundle(Bundle(root)))
            finally:
                sys.argv = old_argv
                if workspace.exists():
                    shutil.rmtree(workspace)

    def test_pm_intake_missing_fields_does_not_create_project(self) -> None:
        module = load_pm_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            old_argv = sys.argv
            try:
                sys.argv = [
                    "pm_init_project.py",
                    "--root",
                    str(root),
                    "--request",
                    "帮我初始化一个软著项目",
                ]
                with contextlib.redirect_stderr(io.StringIO()) as err:
                    self.assertEqual(module.main(), 2)
                self.assertIn("--name", err.getvalue())
                self.assertIn("--owner", err.getvalue())
                self.assertIn("--workspace-ref", err.getvalue())
                self.assertFalse((root / "projects" / "project" / "project.md").exists())
            finally:
                sys.argv = old_argv

    def test_pm_intake_infers_copyright_profile_and_creates_project(self) -> None:
        module = load_pm_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = external_workspace(root, "pm-copyright-workspace")
            write_minimal_bundle(root)
            old_argv = sys.argv
            try:
                sys.argv = [
                    "pm_init_project.py",
                    "--root",
                    str(root),
                    "--request",
                    "帮我初始化一个软著项目，源码只是参考",
                    "--name",
                    "PicPeek",
                    "--owner",
                    "meimei",
                    "--workspace-ref",
                    str(workspace),
                    "--source-repo-url",
                    "https://github.com/shenyingjun5/picpeek",
                ]
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(module.main(), 0)
                project = load_object(root / "projects" / "picpeek" / "project.md")
                self.assertEqual(project["workspaceProfile"], "copyright")
                self.assertTrue((workspace / "01_源码镜像").is_dir())
                self.assertTrue((workspace / "02_软著材料" / "01_产品说明").is_dir())
                self.assertTrue((root / "projects" / "picpeek" / "tasks" / "project-init-picpeek-copyright-scope.md").is_file())
                self.assertFalse(validate_bundle(Bundle(root)))
            finally:
                sys.argv = old_argv
                if workspace.exists():
                    shutil.rmtree(workspace)


class ProjectInitProfileTests(unittest.TestCase):
    def test_development_workspace_creates_engineering_dirs(self) -> None:
        module = load_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = external_workspace(root, "development-workspace")
            write_minimal_bundle(root)
            old_argv = sys.argv
            try:
                sys.argv = [
                    "init_project.py",
                    "--root",
                    str(root),
                    "--project-id",
                    "dev-demo",
                    "--name",
                    "Dev Demo",
                    "--owner",
                    "meimei",
                    "--workspace-profile",
                    "development",
                    "--workspace-ref",
                    str(workspace),
                    "--goal",
                    "初始化开发型项目",
                ]
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(module.main(), 0)
                self.assertTrue((workspace / "04_研发工程" / "services").is_dir())
                self.assertTrue((workspace / "04_研发工程" / "skills").is_dir())
                self.assertTrue((workspace / "05_测试验收").is_dir())
                project = load_object(root / "projects" / "dev-demo" / "project.md")
                self.assertEqual(project["workspaceProfile"], "development")
                self.assertFalse(validate_bundle(Bundle(root)))
            finally:
                sys.argv = old_argv
                if workspace.exists():
                    shutil.rmtree(workspace)

    def test_copyright_workspace_keeps_materials_separate_from_source_mirror(self) -> None:
        module = load_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = external_workspace(root, "picpeek-workspace")
            source_repo = workspace / "01_源码镜像" / "picpeek"
            source_repo.mkdir(parents=True)
            (source_repo / "README.zh-CN.md").write_text("# PicPeek\n", encoding="utf-8")
            prd = root / "picpeek-prd.md"
            prd.write_text("# PicPeek 软著说明\n", encoding="utf-8")
            write_minimal_bundle(root)
            old_argv = sys.argv
            try:
                sys.argv = [
                    "init_project.py",
                    "--root",
                    str(root),
                    "--project-id",
                    "picpeek",
                    "--name",
                    "PicPeek",
                    "--owner",
                    "meimei",
                    "--workspace-ref",
                    str(workspace),
                    "--workspace-profile",
                    "copyright",
                    "--source-repo-url",
                    "https://github.com/shenyingjun5/picpeek",
                    "--source-repo-path",
                    str(source_repo),
                    "--source-file",
                    str(prd),
                    "--goal",
                    "准备软著和运营材料",
                ]
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(module.main(), 0)
                project = load_object(root / "projects" / "picpeek" / "project.md")
                self.assertEqual(project["workspaceRef"], str(workspace))
                self.assertEqual(project["workspaceProfile"], "copyright")
                self.assertEqual(project["sourceRepoRef"], str(source_repo))
                self.assertEqual(project["workspaceMaterialPolicy"], "workspace_keeps_materials_source_repo_is_reference_only")
                self.assertTrue((workspace / "02_软著材料" / "01_产品说明" / "picpeek-prd.md").is_file())
                self.assertFalse((source_repo / "AGENTS.md").exists())
                self.assertTrue((workspace / "AGENTS.md").is_file())
                agents = (workspace / "AGENTS.md").read_text(encoding="utf-8")
                start_here = (workspace / "START_HERE.md").read_text(encoding="utf-8")
                self.assertIn("git switch -c feedback/", agents)
                self.assertIn("git switch -c feedback/", start_here)
                self.assertIn("scripts/agent_feedback.py skill-gap", agents)
                self.assertIn("scripts/agent_feedback.py skill-gap", start_here)
                self.assertIn("scripts/agent_feedback.py system-issue", start_here)
                assert_feedback_governance_text(self, agents, start_here)
                assert_delivery_thinking_text(self, agents, start_here)
                self.assertNotIn("scripts/report_skill_gap.py", agents)
                self.assertNotIn("scripts/report_skill_gap.py", start_here)
                self.assertNotIn("scripts/report_system_issue.py", agents)
                self.assertNotIn("scripts/report_system_issue.py", start_here)
                self.assertTrue((root / "projects" / "picpeek" / "tasks" / "project-init-picpeek-copyright-scope.md").is_file())
                self.assertTrue((root / "projects" / "picpeek" / "tasks" / "project-init-picpeek-code-structure-review.md").is_file())
                self.assertTrue((root / "projects" / "picpeek" / "tasks" / "project-init-picpeek-screenshot-evidence-plan.md").is_file())
                self.assertGreaterEqual(len(project.get("sourceMaterialRefs", [])), 2)
                self.assertFalse(validate_bundle(Bundle(root)))
            finally:
                sys.argv = old_argv
                if workspace.exists():
                    shutil.rmtree(workspace)


class ProjectInitExistingRepoTests(unittest.TestCase):
    def test_existing_source_repo_workspace_gets_active_source_boundary_rule(self) -> None:
        module = load_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "central"
            workspace = Path(tmp) / "official-website"
            workspace.mkdir()
            write_minimal_bundle(root)
            old_argv = sys.argv
            try:
                sys.argv = [
                    "init_project.py",
                    "--root",
                    str(root),
                    "--project-id",
                    "official-website",
                    "--name",
                    "官网",
                    "--owner",
                    "meimei",
                    "--workspace-profile",
                    "development",
                    "--workspace-ref",
                    str(workspace),
                    "--source-repo-url",
                    "https://github.com/example/official-website.git",
                    "--source-repo-path",
                    str(workspace),
                    "--no-create-workspace",
                    "--goal",
                    "接管已有官网项目",
                ]
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(module.main(), 0)
                agents = (workspace / "AGENTS.md").read_text(encoding="utf-8")
                self.assertIn("This workspace is the active source repository", agents)
                self.assertNotIn("Source code is a reference mirror", agents)
                self.assertFalse(validate_bundle(Bundle(root)))
            finally:
                sys.argv = old_argv
                if workspace.exists():
                    shutil.rmtree(workspace)


class ProjectInitCloneTests(unittest.TestCase):
    def test_clone_source_repo_uses_profile_source_mirror(self) -> None:
        module = load_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "central"
            upstream = Path(tmp) / "upstream"
            workspace = Path(tmp) / "copyright-workspace"
            write_minimal_bundle(root)
            upstream.mkdir()
            subprocess.run(["git", "init"], cwd=upstream, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=upstream, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=upstream, check=True)
            (upstream / "README.md").write_text("# Upstream\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=upstream, check=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=upstream, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            old_argv = sys.argv
            try:
                sys.argv = [
                    "init_project.py",
                    "--root",
                    str(root),
                    "--project-id",
                    "clone-demo",
                    "--name",
                    "Clone Demo",
                    "--owner",
                    "meimei",
                    "--workspace-ref",
                    str(workspace),
                    "--workspace-profile",
                    "copyright",
                    "--source-repo-url",
                    str(upstream),
                    "--clone-source-repo",
                ]
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(module.main(), 0)
                source_mirror = workspace / "01_源码镜像" / "upstream"
                self.assertTrue((source_mirror / ".git").is_dir())
                self.assertFalse((source_mirror / "AGENTS.md").exists())
                project = load_object(root / "projects" / "clone-demo" / "project.md")
                self.assertEqual(project["sourceRepoRef"], str(source_mirror.resolve()))
                self.assertFalse(validate_bundle(Bundle(root)))
            finally:
                sys.argv = old_argv
                if workspace.exists():
                    shutil.rmtree(workspace)


if __name__ == "__main__":
    unittest.main()
