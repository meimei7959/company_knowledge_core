import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HARNESS_PATH = REPO_ROOT / "scripts" / "distributed_runner_proof_harness.py"


def load_harness():
    spec = importlib.util.spec_from_file_location("distributed_runner_proof_harness", HARNESS_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class DistributedRunnerProofHarnessTests(unittest.TestCase):
    def test_simulated_phase2_evidence_verifies_as_dev_self_check(self) -> None:
        harness = load_harness()
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "phase2-simulated.jsonl"
            self.assertEqual(0, harness.main(["--evidence-file", str(evidence), "simulate-phase2"]))
            self.assertTrue(evidence.exists())
            self.assertEqual(0, harness.main(["verify", "--evidence", str(evidence)]))


if __name__ == "__main__":
    unittest.main()
