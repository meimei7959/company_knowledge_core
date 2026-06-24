from __future__ import annotations

import contextlib
import importlib.util
import io
import shutil
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


def external_workspace(root: Path, suffix: str) -> Path:
    return root.parent / f"{root.name}-{suffix}"


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
                self.assertGreaterEqual(len(project.get("sourceMaterialRefs", [])), 2)
                self.assertFalse(validate_bundle(Bundle(root)))
            finally:
                sys.argv = old_argv
                if workspace.exists():
                    shutil.rmtree(workspace)


if __name__ == "__main__":
    unittest.main()
