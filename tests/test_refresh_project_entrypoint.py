from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

from tests.test_cli import REPO_ROOT, write_minimal_bundle
from zhenzhi_knowledge.core import Bundle, load_object, make_project, validate_bundle


def load_refresh_script_module():
    spec = importlib.util.spec_from_file_location("refresh_project_entrypoint_script", REPO_ROOT / "scripts" / "refresh_project_entrypoint.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RefreshProjectEntrypointTests(unittest.TestCase):
    def test_existing_project_entrypoint_gets_skill_gap_rules(self) -> None:
        module = load_refresh_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "central"
            workspace = Path(tmp) / "picpeek"
            workspace.mkdir()
            write_minimal_bundle(root)
            make_project(Bundle(root), "picpeek", "PicPeek", "meimei", workspace_ref=str(workspace))
            old_argv = sys.argv
            try:
                sys.argv = [
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
                ]
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(module.main(), 0)
                agents = (workspace / "AGENTS.md").read_text(encoding="utf-8")
                start_here = (workspace / "START_HERE.md").read_text(encoding="utf-8")
                project = load_object(root / "projects" / "picpeek" / "project.md")
                self.assertIn("scripts/report_skill_gap.py", agents)
                self.assertIn("scripts/report_system_issue.py", start_here)
                self.assertEqual(project["workspaceProfile"], "copyright")
                self.assertEqual(project["sourceRepoUrl"], "https://github.com/shenyingjun5/picpeek")
                self.assertFalse(validate_bundle(Bundle(root)))
            finally:
                sys.argv = old_argv


if __name__ == "__main__":
    unittest.main()
