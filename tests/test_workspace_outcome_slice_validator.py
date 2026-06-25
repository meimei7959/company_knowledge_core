from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

from tests.test_cli import REPO_ROOT


def load_validator_module():
    spec = importlib.util.spec_from_file_location(
        "validate_workspace_outcome_slices",
        REPO_ROOT / "scripts" / "validate_workspace_outcome_slices.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WorkspaceOutcomeSliceValidatorTests(unittest.TestCase):
    def test_rejects_arrow_handoff_chain_and_display_names(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "OS-20260625-LOCAL.md").write_text(
                "\n".join(
                    [
                        "# OutcomeSlice",
                        "",
                        "- primaryAgent: agent.company.development",
                        "- upstreamAgent: PM Agent",
                        "- downstreamAgent: agent.company.test",
                        "- handoffChain: development -> test -> project-manager",
                    ]
                ),
                encoding="utf-8",
            )
            self.assertEqual(module.main(["--workspace", str(workspace)]), 1)

    def test_accepts_structured_canonical_agent_fields(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "OS-20260625-LOCAL.md").write_text(
                "\n".join(
                    [
                        "# OutcomeSlice",
                        "",
                        "- primaryAgent: agent.company.development",
                        "- upstreamAgent: agent.company.project-manager",
                        "- downstreamAgent: agent.company.test",
                        "- handoffChain:",
                        "  - agent.company.project-manager",
                        "- escalationAgents:",
                        "  - agent.company.architecture",
                    ]
                ),
                encoding="utf-8",
            )
            self.assertEqual(module.main(["--workspace", str(workspace)]), 0)
