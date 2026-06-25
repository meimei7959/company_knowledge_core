from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

from tests.test_cli import REPO_ROOT, write_minimal_bundle
from zhenzhi_knowledge.core import Bundle, load_object, make_project, update_frontmatter_file, validate_bundle


def load_refresh_script_module():
    spec = importlib.util.spec_from_file_location("refresh_project_entrypoint_script", REPO_ROOT / "scripts" / "refresh_project_entrypoint.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    testcase.assertIn("Do not wait for the user to ask for it", agents)
    testcase.assertIn("Project Manager Agent owns cost control", agents)
    testcase.assertIn("One stage has one primary Agent", agents)
    testcase.assertIn("downstreamAgent means one next receiver only", agents)
    testcase.assertIn("do not write one arrow string", agents)
    testcase.assertIn("must use canonical Agent ids", agents)
    testcase.assertIn("validate_workspace_outcome_slices.py", agents)
    testcase.assertIn("不要只填模板", start_here)
    testcase.assertIn("目标、对象、状态、路径、异常、依赖、证据、门禁和下一步", start_here)
    testcase.assertIn("不能等用户追问", start_here)
    testcase.assertIn("项目经理 Agent 负责成本控制", start_here)
    testcase.assertIn("必须停损", start_here)
    testcase.assertIn("一个阶段只有一个主责 Agent", start_here)
    testcase.assertIn("downstreamAgent 只表示一个下一棒主要接收方", start_here)
    testcase.assertIn("不要写成 agent.company.architecture -> agent.company.development", start_here)
    testcase.assertIn("必须写规范 Agent ID", start_here)
    testcase.assertIn("validate_workspace_outcome_slices.py", start_here)
    testcase.assertIn("下游接收 Agent 必须做 ReceiverReview", start_here)


def run_refresh_main(module, argv: list[str]) -> tuple[int, str, str]:
    old_argv = sys.argv
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        sys.argv = argv
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = module.main()
    finally:
        sys.argv = old_argv
    return status, stdout.getvalue(), stderr.getvalue()


class RefreshProjectEntrypointTests(unittest.TestCase):
    def test_existing_project_entrypoint_gets_skill_gap_rules(self) -> None:
        module = load_refresh_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "central"
            workspace = Path(tmp) / "picpeek"
            workspace.mkdir()
            write_minimal_bundle(root)
            make_project(Bundle(root), "picpeek", "PicPeek", "meimei", workspace_ref=str(workspace))
            status, _, stderr = run_refresh_main(
                module,
                [
                    "refresh_project_entrypoint.py",
                    "--root",
                    str(root),
                    "--project-id",
                    "picpeek",
                    "--workspace-profile",
                    "copyright",
                    "--source-repo-url",
                    "https://github.com/shenyingjun5/picpeek",
                    "--source-repo-path",
                    str(workspace / "01_源码镜像" / "picpeek"),
                ],
            )
            self.assertEqual(status, 0, stderr)
            agents = (workspace / "AGENTS.md").read_text(encoding="utf-8")
            start_here = (workspace / "START_HERE.md").read_text(encoding="utf-8")
            project = load_object(root / "projects" / "picpeek" / "project.md")
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
            self.assertEqual(project["workspaceProfile"], "copyright")
            self.assertEqual(project["sourceRepoUrl"], "https://github.com/shenyingjun5/picpeek")
            self.assertFalse(validate_bundle(Bundle(root)))


class BatchRefreshCentralWorkspaceSkipTests(unittest.TestCase):
    def test_all_skips_central_repository_workspaces_without_writing(self) -> None:
        module = load_refresh_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "central"
            central_child = root / "central-child"
            write_minimal_bundle(root)
            central_child.mkdir()
            bundle = Bundle(root)
            make_project(bundle, "central-root", "Central Root", "meimei", workspace_ref=str(root))
            make_project(bundle, "central-child", "Central Child", "meimei", workspace_ref=str(central_child))
            root_agents_before = (root / "AGENTS.md").read_text(encoding="utf-8")

            status, stdout, stderr = run_refresh_main(
                module,
                [
                    "refresh_project_entrypoint.py",
                    "--root",
                    str(root),
                    "--all",
                ],
            )

            self.assertEqual(status, 0, stderr)
            self.assertIn("summary: refreshed=0 would_refresh=0 skipped=2 failed=0", stdout)
            self.assertEqual(stdout.count("workspaceRef points inside central repository"), 2)
            self.assertEqual((root / "AGENTS.md").read_text(encoding="utf-8"), root_agents_before)
            self.assertFalse((root / "START_HERE.md").exists())
            self.assertFalse((central_child / "AGENTS.md").exists())
            self.assertFalse((central_child / "START_HERE.md").exists())

    def test_all_dry_run_skips_central_repository_workspaces_without_writing(self) -> None:
        module = load_refresh_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "central"
            central_child = root / "central-child"
            write_minimal_bundle(root)
            central_child.mkdir()
            bundle = Bundle(root)
            make_project(bundle, "central-root", "Central Root", "meimei", workspace_ref=str(root))
            make_project(bundle, "central-child", "Central Child", "meimei", workspace_ref=str(central_child))
            root_agents_before = (root / "AGENTS.md").read_text(encoding="utf-8")

            status, stdout, stderr = run_refresh_main(
                module,
                [
                    "refresh_project_entrypoint.py",
                    "--root",
                    str(root),
                    "--all",
                    "--dry-run",
                ],
            )

            self.assertEqual(status, 0, stderr)
            self.assertIn("dry-run: no files written", stdout)
            self.assertIn("summary: refreshed=0 would_refresh=0 skipped=2 failed=0", stdout)
            self.assertEqual(stdout.count("workspaceRef points inside central repository"), 2)
            self.assertEqual((root / "AGENTS.md").read_text(encoding="utf-8"), root_agents_before)
            self.assertFalse((root / "START_HERE.md").exists())
            self.assertFalse((central_child / "AGENTS.md").exists())
            self.assertFalse((central_child / "START_HERE.md").exists())


class BatchRefreshDryRunTests(unittest.TestCase):
    def test_all_dry_run_reports_without_writing(self) -> None:
        module = load_refresh_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "central"
            workspace = Path(tmp) / "active"
            workspace.mkdir()
            write_minimal_bundle(root)
            make_project(Bundle(root), "active", "Active", "meimei", workspace_ref=str(workspace))
            status, stdout, stderr = run_refresh_main(
                module,
                [
                    "refresh_project_entrypoint.py",
                    "--root",
                    str(root),
                    "--all",
                    "--dry-run",
                ],
            )
            self.assertEqual(status, 0, stderr)
            self.assertIn("dry-run: no files written", stdout)
            self.assertIn("would_refresh=1", stdout)
            self.assertFalse((workspace / "AGENTS.md").exists())
            self.assertFalse((workspace / "START_HERE.md").exists())


class BatchRefreshMixedWorkspaceTests(unittest.TestCase):
    def test_all_refreshes_confirmed_workspaces_and_skips_unrefreshable_projects(self) -> None:
        module = load_refresh_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "central"
            alpha_workspace = Path(tmp) / "alpha"
            beta_workspace = Path(tmp) / "beta"
            missing_workspace = Path(tmp) / "missing"
            alpha_workspace.mkdir()
            beta_workspace.mkdir()
            write_minimal_bundle(root)
            bundle = Bundle(root)
            alpha_project = make_project(bundle, "alpha", "Alpha", "meimei", workspace_ref=str(alpha_workspace))
            beta_project = make_project(bundle, "beta", "Beta", "meimei", workspace_ref=str(beta_workspace))
            make_project(bundle, "pending", "Pending", "meimei")
            make_project(bundle, "missing", "Missing", "meimei", workspace_ref=str(missing_workspace))
            update_frontmatter_file(
                alpha_project,
                {
                    "workspaceProfile": "copyright",
                    "sourceRepoUrl": "https://github.com/example/alpha",
                    "sourceRepoRef": str(alpha_workspace / "01_source" / "alpha"),
                },
            )
            update_frontmatter_file(
                beta_project,
                {
                    "workspaceProfile": "development",
                    "sourceRepoPath": str(beta_workspace / "source" / "beta"),
                },
            )

            status, stdout, stderr = run_refresh_main(
                module,
                [
                    "refresh_project_entrypoint.py",
                    "--root",
                    str(root),
                    "--all",
                ],
            )

            self.assertEqual(status, 0, stderr)
            self.assertIn("summary: refreshed=2", stdout)
            self.assertIn("skipped=2", stdout)
            self.assertIn("workspaceRef pending_confirmation", stdout)
            self.assertIn("workspace path does not exist", stdout)
            for workspace in [alpha_workspace, beta_workspace]:
                agents = (workspace / "AGENTS.md").read_text(encoding="utf-8")
                start_here = (workspace / "START_HERE.md").read_text(encoding="utf-8")
                self.assertIn("git switch -c feedback/", agents)
                self.assertIn("git switch -c feedback/", start_here)
                assert_feedback_governance_text(self, agents, start_here)
                assert_delivery_thinking_text(self, agents, start_here)
            alpha = load_object(alpha_project)
            beta = load_object(beta_project)
            self.assertEqual(alpha["workspaceProfile"], "copyright")
            self.assertEqual(alpha["sourceRepoUrl"], "https://github.com/example/alpha")
            self.assertEqual(beta["workspaceProfile"], "development")
            self.assertEqual(beta["sourceRepoRef"], str(beta_workspace / "source" / "beta"))
            self.assertFalse((missing_workspace / "AGENTS.md").exists())
            self.assertFalse(validate_bundle(Bundle(root)))


if __name__ == "__main__":
    unittest.main()
