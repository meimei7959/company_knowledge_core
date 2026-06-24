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


def load_report_script_module():
    spec = importlib.util.spec_from_file_location("report_system_issue_script", REPO_ROOT / "scripts" / "report_system_issue.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReportSystemIssueTests(unittest.TestCase):
    def test_business_project_can_report_system_issue_to_central(self) -> None:
        module = load_report_script_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_bundle(root)
            make_project(Bundle(root), "company-knowledge-core", "Company Knowledge Core", "meimei")
            old_argv = sys.argv
            try:
                sys.argv = [
                    "report_system_issue.py",
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
                    self.assertEqual(module.main(), 0)
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
            finally:
                sys.argv = old_argv


if __name__ == "__main__":
    unittest.main()
