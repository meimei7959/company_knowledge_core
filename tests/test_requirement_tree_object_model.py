import contextlib
import io
import json
import threading
import tempfile
import unittest
import urllib.request
from pathlib import Path

from zhenzhi_knowledge.cli import main, make_parser
from zhenzhi_knowledge.core import Bundle, KnowledgeError, create_project_task, load_object, render_doc, requirement_tree_workbench_read_model, validate_bundle, validate_requirement_tree_records
from zhenzhi_knowledge.server import KnowledgeHTTPServer


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_minimal_bundle(root: Path) -> None:
    for directory in ["projects", "agents", "tools", "knowledge", "runs", "tasks", "sources", "task-results", "runners", "credential-requests", "notifications"]:
        (root / directory).mkdir(parents=True, exist_ok=True)
        (root / directory / "index.md").write_text(f"# {directory}\n", encoding="utf-8")
    (root / "index.md").write_text("# Index\n", encoding="utf-8")
    (root / "log.md").write_text("# Log\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")


def write_import_sources(root: Path) -> tuple[Path, Path]:
    product_path = root / "docs/product/ai-native-os/requirement-tree.md"
    matrix_path = root / "projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-coverage-matrix.md"
    product_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    product_path.write_text((REPO_ROOT / "docs/product/ai-native-os/requirement-tree.md").read_text(encoding="utf-8"), encoding="utf-8")
    matrix_path.write_text((REPO_ROOT / "projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-coverage-matrix.md").read_text(encoding="utf-8"), encoding="utf-8")
    return product_path, matrix_path


EXISTING_WORK_TASK_IDS = [
    "kt-ai-native-os-impl-requirement-prd-domain",
    "kt-ai-native-os-test-requirement-prd-domain",
    "kt-ai-native-os-impl-desktop-workbench-slice0",
    "kt-ai-native-os-test-desktop-workbench-slice0",
    "kt-ai-native-os-impl-scheduler-runner-result",
    "kt-ai-native-os-test-scheduler-runner-result",
    "kt-ai-native-os-impl-governance-quality-ops-api",
    "kt-ai-native-os-test-governance-quality-ops-api",
    "kt-agent-ring-stub-runner-tests",
]

EXISTING_WORK_RESULT_REFS = [
    ("task-results/tr-kt-ai-native-os-impl-requirement-prd-domain.md", "kt-ai-native-os-impl-requirement-prd-domain"),
    ("task-results/tr-kt-ai-native-os-test-requirement-prd-domain.md", "kt-ai-native-os-test-requirement-prd-domain"),
    ("task-results/tr-kt-ai-native-os-impl-desktop-workbench-slice0.md", "kt-ai-native-os-impl-desktop-workbench-slice0"),
    ("task-results/tr-kt-ai-native-os-test-desktop-workbench-slice0.md", "kt-ai-native-os-test-desktop-workbench-slice0"),
    ("task-results/tr-kt-ai-native-os-impl-scheduler-runner-result.md", "kt-ai-native-os-impl-scheduler-runner-result"),
    ("task-results/tr-kt-ai-native-os-test-scheduler-runner-result.md", "kt-ai-native-os-test-scheduler-runner-result"),
    ("task-results/tr-kt-ai-native-os-impl-governance-quality-ops-api.md", "kt-ai-native-os-impl-governance-quality-ops-api"),
    ("task-results/tr-kt-ai-native-os-test-governance-quality-ops-api.md", "kt-ai-native-os-test-governance-quality-ops-api"),
    ("task-results/tr-kt-ai-native-os-product-review-technical-solutions.md", "kt-ai-native-os-product-review-technical-solutions"),
    ("task-results/tr-kt-agent-ring-protocol.md", "KT-AGENT-RING-PROTOCOL"),
    ("task-results/tr-kt-agent-ring-stub-runner-tests.md", "KT-AGENT-RING-STUB-RUNNER-TESTS"),
    ("task-results/tr-kt-ai-native-os-repair-taskresult-metadata-migration.md", "kt-ai-native-os-repair-taskresult-metadata-migration"),
    ("task-results/tr-task-task-notification-loop.md", "TASK-TASK-NOTIFICATION-LOOP"),
    ("task-results/tr-kt-os-digital-worker-capability-registry.md", "kt-os-digital-worker-capability-registry"),
    ("task-results/tr-kt-ai-native-os-dev-automation-hub-hard-capabilities.md", "kt-ai-native-os-dev-automation-hub-hard-capabilities"),
    ("task-results/tr-kt-ai-native-os-test-automation-hub-hard-capabilities.md", "kt-ai-native-os-test-automation-hub-hard-capabilities"),
    ("task-results/tr-kt-os-policy-quality-gates.md", "kt-os-policy-quality-gates"),
]


def write_existing_work_evidence(root: Path) -> None:
    bundle = Bundle(root)
    for task_id in EXISTING_WORK_TASK_IDS:
        create_project_task(
            bundle,
            task_id,
            "company-knowledge-core",
            "meimei",
            "agent.company.development",
            task_type="development",
            task_id=task_id,
            source_material_refs=["projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-coverage-matrix.md"],
            expected_output=["Existing work evidence package."],
        )
    for result_ref, task_id in EXISTING_WORK_RESULT_REFS:
        result_path = root / result_ref
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(
            render_doc(
                {
                    "type": "TaskResult",
                    "title": f"Result for {task_id}",
                    "taskId": task_id,
                    "resultId": Path(result_ref).stem,
                    "projectId": "company-knowledge-core",
                    "status": "done",
                    "summary": "Existing work package evidence for Requirement Tree backfill.",
                    "outputRefs": [result_ref],
                    "executorAgent": "agent.company.development",
                    "runner": "runner.test",
                    "leaseProof": "",
                    "risks": [],
                    "blockers": [],
                    "nextAction": "none",
                    "checks": ["evidence fixture"],
                    "approvalRequest": "",
                    "qualityEvaluation": {"decision": "handoff_ready", "notes": "fixture"},
                    "createdAt": "2026-06-21T11:00:00Z",
                    "evidenceRefs": ["projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-coverage-matrix.md"],
                },
                "## Summary\n\nExisting work package evidence for Requirement Tree backfill.",
            ),
            encoding="utf-8",
        )


def valid_records() -> dict[str, dict]:
    tree_id = "rt.company-knowledge-core.ai-native-os.v20260621095500"
    snapshot_id = "requirements/snapshots/coverage-snapshot.20260621095500.json"
    base_node = {
        "type": "RequirementNode",
        "treeRef": tree_id,
        "statement": "Requirement statement.",
        "whyItMatters": "Traceability matters.",
        "successSignal": "Observable signal exists.",
        "ownerRole": "agent.company.product-manager",
        "sourceRefs": ["docs/product/ai-native-os/requirement-tree.md"],
        "sourceLocation": "docs/product/ai-native-os/requirement-tree.md#test",
        "status": "draft",
        "sensitivity": "internal",
        "acceptanceGateRefs": [],
        "testCaseRefs": [],
        "taskRefs": [],
        "resultRefs": [],
        "decisionRefs": [],
        "auditRefs": [],
    }
    br = {**base_node, "nodeId": "BR-001", "nodeKind": "business", "title": "Business loop", "parentRefs": [], "childRefs": ["UREQ-001"]}
    ureq = {**base_node, "nodeId": "UREQ-001", "nodeKind": "user", "title": "User loop", "parentRefs": ["BR-001"], "childRefs": ["PREQ-001"]}
    preq = {**base_node, "nodeId": "PREQ-001", "nodeKind": "product", "title": "Product bridge", "parentRefs": ["UREQ-001"], "childRefs": ["ANOS-REQ-010"]}
    functional = {
        **base_node,
        "nodeId": "ANOS-REQ-010",
        "nodeKind": "functional",
        "title": "Functional implementation",
        "parentRefs": ["PREQ-001"],
        "childRefs": [],
        "acceptanceGateRefs": ["GATE-RT-001"],
        "testCaseRefs": ["TEST-RT-001"],
    }
    mapping_base = {
        "type": "RequirementMapping",
        "treeRef": tree_id,
        "confidence": "source_exact",
        "rationale": "Source tree preserves this edge.",
        "sourceRefs": ["docs/product/ai-native-os/requirement-tree.md"],
        "createdByAgentRef": "agent.company.development",
        "reviewState": "draft",
        "auditRefs": [],
    }
    return {
        "tree": {
            "type": "RequirementTree",
            "treeId": tree_id,
            "projectRef": "projects/company-knowledge-core/project.md",
            "title": "AI Native OS Requirement Tree",
            "version": "v20260621095500",
            "status": "draft",
            "sourceRefs": ["docs/product/ai-native-os/requirement-tree.md"],
            "businessRequirementRefs": ["BR-001"],
            "userRequirementRefs": ["UREQ-001"],
            "productRequirementRefs": ["PREQ-001"],
            "functionalRequirementRefs": ["ANOS-REQ-010"],
            "acceptanceGateRefs": ["GATE-RT-001"],
            "testCaseRefs": ["TEST-RT-001"],
            "taskRefs": ["projects/company-knowledge-core/tasks/kt-example.md"],
            "resultRefs": ["task-results/tr-example.md"],
            "coverageSnapshotRef": snapshot_id,
            "reviewRefs": [],
            "auditRefs": [],
        },
        "br": br,
        "ureq": ureq,
        "preq": preq,
        "functional": functional,
        "mappings": [
            {**mapping_base, "mappingId": "map.br.ureq", "fromRef": "BR-001", "toRef": "UREQ-001", "mappingKind": "decomposes_to"},
            {**mapping_base, "mappingId": "map.ureq.preq", "fromRef": "UREQ-001", "toRef": "PREQ-001", "mappingKind": "decomposes_to"},
            {**mapping_base, "mappingId": "map.preq.anos", "fromRef": "PREQ-001", "toRef": "ANOS-REQ-010", "mappingKind": "satisfies"},
            {**mapping_base, "mappingId": "map.anos.test", "fromRef": "ANOS-REQ-010", "toRef": "TEST-RT-001", "mappingKind": "verified_by"},
            {**mapping_base, "mappingId": "map.anos.gate", "fromRef": "ANOS-REQ-010", "toRef": "GATE-RT-001", "mappingKind": "accepted_by"},
        ],
        "gate": {
            "type": "AcceptanceGate",
            "gateId": "GATE-RT-001",
            "treeRef": tree_id,
            "requirementRefs": ["ANOS-REQ-010"],
            "ownerRole": "agent.company.test",
            "verificationMethod": "automated_test",
            "observableSignal": "Test case passes and evidence is attached.",
            "requiredEvidenceRefs": ["tests/test_requirement_tree_object_model.py"],
            "status": "draft",
            "waiverDecisionRef": "",
            "sourceRefs": ["docs/product/ai-native-os/requirement-tree.md"],
            "auditRefs": [],
        },
        "snapshot": {
            "type": "RequirementCoverageSnapshot",
            "snapshotId": snapshot_id,
            "treeRef": tree_id,
            "treeVersion": "v20260621095500",
            "counts": {"BR": 1, "UREQ": 1, "product": 1, "functional": 1, "acceptance": 1, "tests": 1, "tasks": 1, "results": 1, "blockers": 0},
            "coverageRows": [
                {
                    "businessRequirementRef": "BR-001",
                    "userRequirementRef": "UREQ-001",
                    "productRequirementRef": "PREQ-001",
                    "functionalRequirementRef": "ANOS-REQ-010",
                    "taskRef": "projects/company-knowledge-core/tasks/kt-example.md",
                    "resultRef": "task-results/tr-example.md",
                    "testCaseRef": "TEST-RT-001",
                    "acceptanceGateRef": "GATE-RT-001",
                }
            ],
            "blockers": [],
            "generatedAt": "2026-06-21T09:55:00Z",
            "generatedByAgentRef": "agent.company.development",
            "sourceRefs": ["docs/product/ai-native-os/requirement-tree.md"],
            "auditRefs": [],
        },
    }


def write_valid_records(root: Path) -> None:
    base = root / "projects" / "company-knowledge-core" / "requirements"
    records = valid_records()
    write_json(base / "requirement-trees" / "rt.company-knowledge-core.ai-native-os.v20260621095500.json", records["tree"])
    for key in ["br", "ureq", "preq", "functional"]:
        write_json(base / "nodes" / f"{records[key]['nodeId']}.json", records[key])
    for mapping in records["mappings"]:
        write_json(base / "mappings" / f"{mapping['mappingId']}.json", mapping)
    write_json(base / "gates" / "acceptance-gates.json", records["gate"])
    write_json(base / "snapshots" / "coverage-snapshot.20260621095500.json", records["snapshot"])


def register_project_and_requirement_tree_agents(root: Path) -> None:
    commands = [
        ["--root", str(root), "project", "register", "--project-id", "company-knowledge-core", "--name", "Company Knowledge Core", "--owner", "meimei"],
        ["--root", str(root), "agent", "register", "--agent-id", "agent.company.development", "--name", "Development", "--owner", "meimei", "--purpose", "development"],
        ["--root", str(root), "agent", "register", "--agent-id", "agent.company.test", "--name", "Test", "--owner", "meimei", "--purpose", "testing"],
        ["--root", str(root), "agent", "register", "--agent-id", "agent.company.design", "--name", "Design", "--owner", "meimei", "--purpose", "design"],
        ["--root", str(root), "agent", "register", "--agent-id", "agent.company.operations", "--name", "Operations", "--owner", "meimei", "--purpose", "operations"],
        ["--root", str(root), "agent", "register", "--agent-id", "agent.core.knowledge-review", "--name", "Review", "--owner", "meimei", "--purpose", "review"],
        ["--root", str(root), "agent", "register", "--agent-id", "agent.core.knowledge-steward", "--name", "Governance", "--owner", "meimei", "--purpose", "governance"],
    ]
    with contextlib.redirect_stdout(io.StringIO()):
        for command in commands:
            assert main(command) == 0


def write_requirement_tree_workbench_fixture(root: Path) -> None:
    register_project_and_requirement_tree_agents(root)
    write_valid_records(root)
    bundle = Bundle(root)
    create_project_task(
        bundle,
        "Example implementation task",
        "company-knowledge-core",
        "meimei",
        "agent.company.development",
        task_type="development",
        task_id="kt-example",
        source_material_refs=["docs/product/ai-native-os/requirement-tree.md"],
        expected_output=["Implement traced requirement."],
    )
    result_path = root / "task-results" / "tr-example.md"
    result_path.write_text(
        render_doc(
            {
                "type": "TaskResult",
                "title": "Example result",
                "taskId": "kt-example",
                "resultId": "tr-example",
                "projectId": "company-knowledge-core",
                "status": "done",
                "summary": "Requirement implemented with evidence.",
                "executorAgent": "agent.company.development",
                "evidenceRefs": ["tests/test_requirement_tree_object_model.py"],
            },
            "## Summary\n\nRequirement implemented with evidence.",
        ),
        encoding="utf-8",
    )
    base = root / "projects" / "company-knowledge-core" / "requirements"
    functional_path = base / "nodes" / "ANOS-REQ-010.json"
    functional = json.loads(functional_path.read_text(encoding="utf-8"))
    functional["taskRefs"] = ["projects/company-knowledge-core/tasks/kt-example.md"]
    functional["resultRefs"] = ["task-results/tr-example.md"]
    functional["assumptions"] = ["Assumption one", "Assumption two", "Assumption three"]
    write_json(functional_path, functional)
    extra = {**functional, "nodeId": "ANOS-REQ-011", "title": "Untested functional item", "testCaseRefs": [], "acceptanceGateRefs": [], "taskRefs": [], "resultRefs": [], "assumptions": []}
    write_json(base / "nodes" / "ANOS-REQ-011.json", extra)
    tree_path = base / "requirement-trees" / "rt.company-knowledge-core.ai-native-os.v20260621095500.json"
    tree = json.loads(tree_path.read_text(encoding="utf-8"))
    tree["functionalRequirementRefs"] = ["ANOS-REQ-010", "ANOS-REQ-011"]
    write_json(tree_path, tree)
    snapshot_path = base / "snapshots" / "coverage-snapshot.20260621095500.json"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    snapshot["blockers"] = [
        {
            "severity": "medium",
            "ownerRole": "agent.company.development",
            "nodeRef": "ANOS-REQ-011",
            "reason": "Needs test mapping.",
            "suggestedFix": "Add test and acceptance gate.",
        }
    ]
    write_json(snapshot_path, snapshot)


def write_traceability_promotion_candidate(root: Path, overrides=None) -> Path:
    base = root / "projects" / "company-knowledge-core" / "requirements"
    gate_path = base / "gates" / "acceptance-gates.json"
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    gate["status"] = "passed"
    write_json(gate_path, gate)
    execution_ref = "projects/company-knowledge-core/requirements/evidence/ANOS-REQ-010-execution.md"
    test_ref = "tests/requirement-tree/TC-RT-001.md"
    review_ref = "reviews/product-manager-review.md"
    acceptance_ref = "projects/company-knowledge-core/requirements/gates/acceptance-gates.json"
    for ref, text in [
        (execution_ref, "# Execution Evidence\n\nANOS-REQ-010 behavior executed."),
        (test_ref, "# Test Evidence\n\nTC-RT-001 passed."),
        (review_ref, "# PM Review\n\nProduct Manager confirms observable completion boundary."),
    ]:
        path = root / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
    candidate = {
        "projectId": "company-knowledge-core",
        "treeRef": "rt.company-knowledge-core.ai-native-os.v20260621095500",
        "candidates": [
            {
                "requirementRef": "ANOS-REQ-010",
                "targetCoverageStatus": "complete",
                "confidence": "direct_verified",
                "executionUnlocking": True,
                "implementationEvidenceRefs": ["task-results/tr-example.md"],
                "executionEvidenceRefs": [execution_ref],
                "testEvidenceRefs": [test_ref],
                "testStatus": "passed",
                "acceptanceGateRefs": ["GATE-RT-001"],
                "acceptanceEvidenceRefs": [acceptance_ref],
                "reviewEvidenceRefs": [review_ref],
                "reviewConclusion": "Product Manager confirms ANOS-REQ-010 is complete for the reviewed launch boundary.",
            }
        ],
    }
    if overrides:
        candidate.update(overrides)
    candidate_path = base / "promotions" / "candidate.json"
    write_json(candidate_path, candidate)
    return candidate_path


class RequirementTreeObjectModelTests(unittest.TestCase):
    def test_valid_requirement_tree_records_pass_bundle_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            write_valid_records(root)
            self.assertEqual([], validate_requirement_tree_records(Bundle(root)))
            self.assertEqual([], validate_bundle(Bundle(root)))

    def test_requirement_tree_validation_rejects_shape_refs_and_secret_like_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            write_valid_records(root)
            tree_path = root / "projects" / "company-knowledge-core" / "requirements" / "requirement-trees" / "rt.company-knowledge-core.ai-native-os.v20260621095500.json"
            tree = json.loads(tree_path.read_text(encoding="utf-8"))
            tree.pop("sourceRefs")
            write_json(tree_path, tree)
            ureq_path = root / "projects" / "company-knowledge-core" / "requirements" / "nodes" / "UREQ-001.json"
            ureq = json.loads(ureq_path.read_text(encoding="utf-8"))
            ureq["parentRefs"] = []
            ureq["statement"] = "Do not store token=abc123456789 in requirement text."
            write_json(ureq_path, ureq)
            problems = validate_requirement_tree_records(Bundle(root))
            joined = "\n".join(problems)
            self.assertIn("RequirementTree missing required field sourceRefs", joined)
            self.assertIn("missing reciprocal parentRef BR-001", joined)
            self.assertIn("possible secret-like text", joined)

    def test_requirement_tree_validate_cli_returns_nonzero_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            write_valid_records(root)
            self.assertEqual(main(["--root", str(root), "requirement", "tree", "validate"]), 0)
            gate_path = root / "projects" / "company-knowledge-core" / "requirements" / "gates" / "acceptance-gates.json"
            gate = json.loads(gate_path.read_text(encoding="utf-8"))
            gate["verificationMethod"] = "maybe"
            write_json(gate_path, gate)
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.assertEqual(main(["--root", str(root), "requirement", "tree", "validate"]), 2)
            self.assertIn("unknown verificationMethod maybe", buffer.getvalue())

    def test_accepted_tree_requires_pm_project_reviews_and_no_high_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            write_valid_records(root)
            tree_path = root / "projects" / "company-knowledge-core" / "requirements" / "requirement-trees" / "rt.company-knowledge-core.ai-native-os.v20260621095500.json"
            tree = json.loads(tree_path.read_text(encoding="utf-8"))
            tree["status"] = "accepted"
            write_json(tree_path, tree)
            snapshot_path = root / "projects" / "company-knowledge-core" / "requirements" / "snapshots" / "coverage-snapshot.20260621095500.json"
            snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
            snapshot["blockers"] = [
                {
                    "severity": "high",
                    "ownerRole": "agent.company.product-manager",
                    "nodeRef": "UREQ-001",
                    "reason": "Missing accepted evidence.",
                    "suggestedFix": "Attach PM review evidence before accepting the tree.",
                }
            ]
            write_json(snapshot_path, snapshot)
            joined = "\n".join(validate_requirement_tree_records(Bundle(root)))
            self.assertIn("accepted RequirementTree requires Product Manager review ref", joined)
            self.assertIn("accepted RequirementTree requires Project Manager review ref", joined)
            self.assertIn("accepted RequirementTree requires zero high-severity coverage blockers", joined)

    def test_mapping_endpoints_must_resolve_to_local_records_or_allowed_evidence_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            write_valid_records(root)
            mapping_path = root / "projects" / "company-knowledge-core" / "requirements" / "mappings" / "map.ureq.preq.json"
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            mapping["toRef"] = "PREQ-999"
            write_json(mapping_path, mapping)
            joined = "\n".join(validate_requirement_tree_records(Bundle(root)))
            self.assertIn("toRef does not resolve to RequirementNode: PREQ-999", joined)

    def test_requirement_tree_import_reads_product_tree_and_coverage_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            product_path, matrix_path = write_import_sources(root)
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "requirement",
                            "tree",
                            "import",
                            "--project",
                            "company-knowledge-core",
                            "--source",
                            str(product_path.relative_to(root)),
                            "--coverage-matrix",
                            str(matrix_path.relative_to(root)),
                            "--version",
                            "20260621102000",
                        ]
                    ),
                    0,
                )
            result = json.loads(buffer.getvalue())
            self.assertEqual(result["counts"]["BR"], 5)
            self.assertEqual(result["counts"]["UREQ"], 15)
            self.assertEqual(result["counts"]["product"], 15)
            self.assertEqual(result["counts"]["functional"], 74)
            self.assertGreaterEqual(result["counts"]["tests"], 84)
            self.assertGreaterEqual(result["counts"]["acceptance"], 20)
            self.assertEqual([], validate_requirement_tree_records(Bundle(root)))
            self.assertEqual([], validate_bundle(Bundle(root)))

    def test_traceability_promotion_dry_run_reports_audit_preview_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            write_requirement_tree_workbench_fixture(root)
            candidate_path = write_traceability_promotion_candidate(root)
            node_path = root / "projects/company-knowledge-core/requirements/nodes/ANOS-REQ-010.json"
            before = json.loads(node_path.read_text(encoding="utf-8"))
            audit_count_before = len(list((root / "knowledge" / "audit").glob("*.md")))
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "requirement",
                            "tree",
                            "promote",
                            "--candidate",
                            str(candidate_path.relative_to(root)),
                        ]
                    ),
                    0,
                )
            result = json.loads(buffer.getvalue())
            self.assertEqual(result["status"], "dry_run")
            self.assertTrue(result["dryRun"])
            self.assertEqual(result["validCandidateCount"], 1)
            self.assertEqual(result["auditPreview"][0]["after"], "complete")
            after = json.loads(node_path.read_text(encoding="utf-8"))
            self.assertEqual(after, before)
            self.assertEqual(len(list((root / "knowledge" / "audit").glob("*.md"))), audit_count_before)

    def test_traceability_promotion_write_updates_node_and_audit_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            write_requirement_tree_workbench_fixture(root)
            candidate_path = write_traceability_promotion_candidate(root)
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "requirement",
                            "tree",
                            "promote",
                            "--candidate",
                            str(candidate_path.relative_to(root)),
                            "--write",
                        ]
                    ),
                    0,
                )
            result = json.loads(buffer.getvalue())
            self.assertEqual(result["status"], "written")
            self.assertFalse(result["dryRun"])
            self.assertEqual(result["changedRequirementRefs"], ["ANOS-REQ-010"])
            self.assertTrue(result["auditRefs"])
            self.assertTrue((root / result["promotionReportRef"]).exists())
            node = json.loads((root / "projects/company-knowledge-core/requirements/nodes/ANOS-REQ-010.json").read_text(encoding="utf-8"))
            self.assertEqual(node["coverageStatus"], "complete")
            self.assertEqual(node["promotionConfidence"], "direct_verified")
            self.assertTrue(node["executionUnlocking"])
            self.assertIn(result["auditRefs"][0], node["auditRefs"])
            audit_text = (root / result["auditRefs"][0]).read_text(encoding="utf-8")
            self.assertIn("requirement_tree.traceability_promotion", audit_text)
            snapshot = json.loads((root / "projects/company-knowledge-core/requirements/snapshots/coverage-snapshot.20260621095500.json").read_text(encoding="utf-8"))
            self.assertEqual(snapshot["counts"]["completePromotions"], 1)
            self.assertEqual(snapshot["counts"]["executionUnlockingMappings"], 1)

    def test_traceability_promotion_rejects_backfill_inferred_execution_unlocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            write_requirement_tree_workbench_fixture(root)
            backfill_ref = "projects/company-knowledge-core/requirements/backfills/requirement-tree-existing-work-backfill.20260621112327.json"
            backfill_path = root / backfill_ref
            backfill_path.parent.mkdir(parents=True, exist_ok=True)
            backfill_path.write_text("{}\n", encoding="utf-8")
            candidate_path = write_traceability_promotion_candidate(
                root,
                {
                    "candidates": [
                        {
                            "requirementRef": "ANOS-REQ-010",
                            "targetCoverageStatus": "complete",
                            "confidence": "backfill_inferred",
                            "executionUnlocking": True,
                            "implementationEvidenceRefs": [backfill_ref],
                            "executionEvidenceRefs": [backfill_ref],
                            "testEvidenceRefs": [backfill_ref],
                            "testStatus": "passed",
                            "acceptanceGateRefs": ["GATE-RT-001"],
                            "acceptanceEvidenceRefs": [backfill_ref],
                            "reviewEvidenceRefs": [backfill_ref],
                            "reviewConclusion": "Backfill-only historical mapping should not unlock execution.",
                        }
                    ]
                },
            )
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.assertEqual(
                    main(["--root", str(root), "requirement", "tree", "promote", "--candidate", str(candidate_path.relative_to(root))]),
                    2,
                )
            result = json.loads(buffer.getvalue())
            joined = "\n".join(result["errors"])
            self.assertIn("backfill_inferred cannot be execution-unlocking", joined)
            self.assertIn("backfill-only evidence cannot promote traceability status", joined)

    def test_traceability_promotion_rejects_all_74_batch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            product_path, matrix_path = write_import_sources(root)
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "requirement",
                            "tree",
                            "import",
                            "--project",
                            "company-knowledge-core",
                            "--source",
                            str(product_path.relative_to(root)),
                            "--coverage-matrix",
                            str(matrix_path.relative_to(root)),
                            "--version",
                            "20260621103000",
                        ]
                    ),
                    0,
                )
            imported = json.loads(buffer.getvalue())
            candidates = [
                {"requirementRef": f"ANOS-REQ-{number:03d}", "targetCoverageStatus": "partial", "confidence": "direct_verified", "executionUnlocking": False}
                for number in list(range(1, 7)) + list(range(10, 17)) + list(range(20, 25)) + list(range(30, 35)) + list(range(40, 46)) + list(range(50, 57)) + list(range(60, 64)) + list(range(70, 74)) + list(range(80, 85)) + list(range(90, 94)) + list(range(100, 103)) + list(range(110, 115)) + list(range(120, 123)) + list(range(130, 134)) + list(range(140, 143)) + list(range(150, 153))
            ]
            self.assertEqual(len(candidates), 74)
            candidate_path = root / "projects/company-knowledge-core/requirements/promotions/all-74.json"
            write_json(candidate_path, {"projectId": "company-knowledge-core", "treeRef": imported["treeId"], "candidates": candidates})
            promote_buffer = io.StringIO()
            with contextlib.redirect_stdout(promote_buffer):
                self.assertEqual(
                    main(["--root", str(root), "requirement", "tree", "promote", "--candidate", str(candidate_path.relative_to(root))]),
                    2,
                )
            result = json.loads(promote_buffer.getvalue())
            self.assertEqual(result["status"], "rejected")
            self.assertIn("refusing all-74 functional requirement promotion", "\n".join(result["errors"]))

    def test_requirement_tree_existing_work_backfill_preserves_partial_and_blocked_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            register_project_and_requirement_tree_agents(root)
            product_path, matrix_path = write_import_sources(root)
            write_existing_work_evidence(root)
            import_buffer = io.StringIO()
            with contextlib.redirect_stdout(import_buffer):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "requirement",
                            "tree",
                            "import",
                            "--project",
                            "company-knowledge-core",
                            "--source",
                            str(product_path.relative_to(root)),
                            "--coverage-matrix",
                            str(matrix_path.relative_to(root)),
                            "--version",
                            "20260621102500",
                        ]
                    ),
                    0,
                )
            imported = json.loads(import_buffer.getvalue())
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "requirement",
                            "tree",
                            "backfill-existing-work",
                            "--project",
                            "company-knowledge-core",
                            "--tree",
                            imported["treeId"],
                            "--coverage-matrix",
                            str(matrix_path.relative_to(root)),
                            "--actor",
                            "agent.company.development",
                        ]
                    ),
                    0,
                )
            result = json.loads(buffer.getvalue())
            self.assertEqual(result["counts"]["functionalRequirements"], 74)
            self.assertEqual(result["counts"]["partial"], 70)
            self.assertEqual(result["counts"]["blocked"], 4)
            self.assertEqual(result["counts"]["completePromotions"], 0)
            self.assertEqual(result["counts"]["executionUnlockingMappings"], 0)
            manifest = json.loads((root / result["backfillRef"]).read_text(encoding="utf-8"))
            self.assertEqual(manifest["policy"]["promotePartialToComplete"], False)
            self.assertEqual(manifest["policy"]["inferredMappingsExecutionUnlocking"], False)
            statuses = {record["coverageStatus"] for record in manifest["records"]}
            self.assertEqual(statuses, {"partial", "blocked"})
            blocked = [record for record in manifest["records"] if record["functionalRequirementRef"] == "ANOS-REQ-060"][0]
            self.assertEqual(blocked["coverageStatus"], "blocked")
            self.assertFalse(blocked["executionUnlocking"])
            self.assertIn("UREQ-008", blocked["userRequirementRefs"])
            self.assertIn("task-results/tr-kt-ai-native-os-test-scheduler-runner-result.md", blocked["resultRefs"])

            base = root / "projects" / "company-knowledge-core" / "requirements"
            node = json.loads((base / "nodes" / "ANOS-REQ-060.json").read_text(encoding="utf-8"))
            self.assertEqual(node["coverageStatus"], "blocked")
            self.assertFalse(node["executionUnlocking"])
            self.assertIn(result["backfillRef"], node["backfillRefs"])
            self.assertIn("task-results/tr-kt-agent-ring-stub-runner-tests.md", node["resultRefs"])
            mapping_files = list((base / "mappings").glob("map.*existing-work*.json"))
            self.assertGreater(len(mapping_files), 74)
            sample_mapping = json.loads(mapping_files[0].read_text(encoding="utf-8"))
            self.assertEqual(sample_mapping["mappingKind"], "implemented_by")
            self.assertEqual(sample_mapping["confidence"], "backfill_inferred")
            self.assertEqual(sample_mapping["reviewState"], "needs_review")
            self.assertFalse(sample_mapping["executionUnlocking"])
            snapshot = json.loads((base / "snapshots" / "coverage-snapshot.20260621102500.json").read_text(encoding="utf-8"))
            self.assertEqual(snapshot["counts"]["blockers"], 4)
            self.assertTrue(all(blocker["severity"] == "high" for blocker in snapshot["blockers"]))
            self.assertEqual([], validate_requirement_tree_records(Bundle(root)))
            self.assertEqual([], validate_bundle(Bundle(root)))

    def test_traceability_validator_reports_import_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            product_path, matrix_path = write_import_sources(root)
            self.assertEqual(
                main(
                    [
                        "--root",
                        str(root),
                        "requirement",
                        "tree",
                        "import",
                        "--project",
                        "company-knowledge-core",
                        "--source",
                        str(product_path.relative_to(root)),
                        "--coverage-matrix",
                        str(matrix_path.relative_to(root)),
                        "--version",
                        "20260621102001",
                    ]
                ),
                0,
            )
            base = root / "projects/company-knowledge-core/requirements"
            functional_path = base / "nodes" / "ANOS-REQ-001.json"
            functional = json.loads(functional_path.read_text(encoding="utf-8"))
            functional["parentRefs"] = []
            functional["ownerRole"] = ""
            functional["testCaseRefs"] = []
            functional["acceptanceGateRefs"] = []
            write_json(functional_path, functional)
            gate_path = next((base / "gates").glob("*.json"))
            gate = json.loads(gate_path.read_text(encoding="utf-8"))
            gate["observableSignal"] = ""
            write_json(gate_path, gate)
            joined = "\n".join(validate_requirement_tree_records(Bundle(root)))
            self.assertIn("orphan functional requirement has no ProductRequirement parent: ANOS-REQ-001", joined)
            self.assertIn("ANOS-REQ-001 missing ownerRole", joined)
            self.assertIn("functional requirement missing test expectation: ANOS-REQ-001", joined)
            self.assertIn("functional requirement missing acceptance gate: ANOS-REQ-001", joined)
            self.assertIn("acceptance gate missing observable criteria", joined)

    def test_requirement_tree_task_queue_compiler_generates_role_specific_drafts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            product_path, matrix_path = write_import_sources(root)
            import_buffer = io.StringIO()
            with contextlib.redirect_stdout(import_buffer):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "requirement",
                            "tree",
                            "import",
                            "--project",
                            "company-knowledge-core",
                            "--source",
                            str(product_path.relative_to(root)),
                            "--coverage-matrix",
                            str(matrix_path.relative_to(root)),
                            "--version",
                            "20260621103000",
                        ]
                    ),
                    0,
                )
            imported = json.loads(import_buffer.getvalue())
            tree_path = root / imported["treeRef"]
            tree = json.loads(tree_path.read_text(encoding="utf-8"))
            tree["status"] = "accepted"
            tree["reviewRefs"] = ["reviews/product-manager-review.md", "reviews/project-manager-review.md"]
            write_json(tree_path, tree)

            compile_buffer = io.StringIO()
            with contextlib.redirect_stdout(compile_buffer):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "requirement",
                            "tree",
                            "compile",
                            "--project",
                            "company-knowledge-core",
                            "--tree",
                            imported["treeId"],
                            "--actor",
                            "agent.company.development",
                        ]
                    ),
                    0,
                )
            result = json.loads(compile_buffer.getvalue())
            self.assertEqual(result["status"], "drafted")
            self.assertEqual(result["routes"], ["development", "test", "design", "ops", "review", "governance"])
            self.assertEqual(result["counts"]["BR"], 5)
            self.assertEqual(result["counts"]["UREQ"], 15)
            self.assertEqual(result["counts"]["product"], 15)
            self.assertEqual(result["counts"]["functional"], 74)
            self.assertEqual(len(result["taskDraftRefs"]), 6)
            for draft_ref in result["taskDraftRefs"]:
                self.assertTrue(draft_ref.endswith(".draft.md"))
                draft = load_object(root / draft_ref)
                self.assertEqual(draft["type"], "ProjectTask")
                self.assertEqual(draft["status"], "draft")
                self.assertEqual(draft["requirementTreeId"], imported["treeId"])
                self.assertEqual(len(draft["businessRequirementRefs"]), 5)
                self.assertEqual(len(draft["userRequirementRefs"]), 15)
                self.assertEqual(len(draft["productRequirementRefs"]), 15)
                self.assertEqual(len(draft["functionalRequirementRefs"]), 74)
                self.assertGreaterEqual(len(draft["testCaseRefs"]), 84)
                self.assertGreaterEqual(len(draft["acceptanceGateRefs"]), 20)
            self.assertEqual([], validate_requirement_tree_records(Bundle(root)))
            self.assertEqual([], validate_bundle(Bundle(root)))

    def test_requirement_tree_task_queue_compiler_blocks_incomplete_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            write_valid_records(root)
            base = root / "projects" / "company-knowledge-core" / "requirements"
            tree_path = base / "requirement-trees" / "rt.company-knowledge-core.ai-native-os.v20260621095500.json"
            tree = json.loads(tree_path.read_text(encoding="utf-8"))
            tree["status"] = "accepted"
            tree["reviewRefs"] = ["reviews/product-manager-review.md", "reviews/project-manager-review.md"]
            write_json(tree_path, tree)
            functional_path = base / "nodes" / "ANOS-REQ-010.json"
            functional = json.loads(functional_path.read_text(encoding="utf-8"))
            functional["ownerRole"] = ""
            functional["testCaseRefs"] = []
            functional["acceptanceGateRefs"] = []
            write_json(functional_path, functional)
            gate_path = base / "gates" / "acceptance-gates.json"
            gate = json.loads(gate_path.read_text(encoding="utf-8"))
            gate["observableSignal"] = ""
            gate["requiredEvidenceRefs"] = []
            write_json(gate_path, gate)
            snapshot_path = base / "snapshots" / "coverage-snapshot.20260621095500.json"
            snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
            snapshot["blockers"] = [
                {
                    "severity": "critical",
                    "ownerRole": "agent.company.test",
                    "nodeRef": "ANOS-REQ-010",
                    "reason": "Acceptance evidence missing.",
                    "suggestedFix": "Restore gate evidence before compiling.",
                }
            ]
            snapshot["coverageRows"][0]["testCaseRef"] = ""
            snapshot["coverageRows"][0]["acceptanceGateRef"] = ""
            write_json(snapshot_path, snapshot)

            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "requirement",
                            "tree",
                            "compile",
                            "--project",
                            "company-knowledge-core",
                            "--tree",
                            "rt.company-knowledge-core.ai-native-os.v20260621095500",
                        ]
                    ),
                    0,
                )
            result = json.loads(buffer.getvalue())
            self.assertEqual(result["status"], "blocked")
            self.assertEqual(result["taskDraftRefs"], [])
            self.assertTrue((root / result["blockerDiagnosticRef"]).exists())
            blocker_codes = {blocker["code"] for blocker in result["blockers"]}
            self.assertIn("missing_owner", blocker_codes)
            self.assertIn("missing_test", blocker_codes)
            self.assertIn("missing_acceptance_gate", blocker_codes)
            self.assertIn("missing_observable_criteria", blocker_codes)
            self.assertIn("missing_evidence", blocker_codes)
            self.assertIn("high_coverage_blocker", blocker_codes)
            self.assertEqual([], list((root / "projects" / "company-knowledge-core" / "tasks").glob("*.draft.md")))

    def test_context_pack_includes_requirement_tree_traceability_for_all_roles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            register_project_and_requirement_tree_agents(root)
            write_valid_records(root)
            tree_path = root / "projects" / "company-knowledge-core" / "requirements" / "requirement-trees" / "rt.company-knowledge-core.ai-native-os.v20260621095500.json"
            tree = json.loads(tree_path.read_text(encoding="utf-8"))
            tree["status"] = "accepted"
            tree["reviewRefs"] = ["reviews/product-manager-review.md", "reviews/project-manager-review.md"]
            write_json(tree_path, tree)
            compile_buffer = io.StringIO()
            with contextlib.redirect_stdout(compile_buffer):
                self.assertEqual(
                    main(
                        [
                            "--root",
                            str(root),
                            "requirement",
                            "tree",
                            "compile",
                            "--project",
                            "company-knowledge-core",
                            "--tree",
                            "rt.company-knowledge-core.ai-native-os.v20260621095500",
                        ]
                    ),
                    0,
                )
            compiled = json.loads(compile_buffer.getvalue())
            expected_focus = {
                "development": "Development focus",
                "test": "Test focus",
                "design": "Design focus",
                "ops": "Ops focus",
                "review": "Review focus",
                "governance": "Governance focus",
            }
            for draft_ref in compiled["taskDraftRefs"]:
                draft = load_object(root / draft_ref)
                with self.subTest(role=draft["taskType"]):
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(
                            main(
                                [
                                    "--root",
                                    str(root),
                                    "start",
                                    "--project",
                                    "company-knowledge-core",
                                    "--agent",
                                    draft["assignee"],
                                    "--task",
                                    draft["taskId"],
                                    "--retrieval-limit",
                                    "0",
                                ]
                            ),
                            0,
                        )
                    context = (root / ".zhenzhi" / "context" / "current.md").read_text(encoding="utf-8")
                    self.assertIn("## Requirement Tree Traceability", context)
                    self.assertIn("BR-001", context)
                    self.assertIn("UREQ-001", context)
                    self.assertIn("PREQ-001", context)
                    self.assertIn("ANOS-REQ-010", context)
                    self.assertIn("TEST-RT-001", context)
                    self.assertIn("GATE-RT-001", context)
                    self.assertIn("scenario=Requirement statement.", context)
                    self.assertIn("productRequirement=Requirement statement.", context)
                    self.assertIn("observableCriteria=Test case passes and evidence is attached.", context)
                    self.assertIn("evidenceRequired=tests/test_requirement_tree_object_model.py", context)
                    self.assertIn("highOrCriticalBlockers: 0", context)
                    self.assertIn(expected_focus[draft["taskType"]], context)

    def test_requirement_tree_workbench_read_model_exposes_chain_and_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            write_requirement_tree_workbench_fixture(root)
            model = requirement_tree_workbench_read_model(Bundle(root), "company-knowledge-core", "rt.company-knowledge-core.ai-native-os.v20260621095500")
            self.assertEqual(model["kind"], "RequirementTreeWorkbenchReadModel")
            self.assertEqual(model["counts"]["chains"], 1)
            chain = model["chains"][0]
            self.assertEqual(chain["businessRequirement"]["nodeRef"], "BR-001")
            self.assertEqual(chain["userRequirement"]["nodeRef"], "UREQ-001")
            self.assertEqual(chain["productRequirement"]["nodeRef"], "PREQ-001")
            self.assertEqual(chain["functionalRequirement"]["nodeRef"], "ANOS-REQ-010")
            self.assertEqual(chain["tasks"][0]["taskId"], "kt-example")
            self.assertTrue(chain["tasks"][0]["resolved"])
            self.assertEqual(chain["results"][0]["resultId"], "tr-example")
            self.assertEqual(chain["testRefs"], ["TEST-RT-001"])
            self.assertEqual(chain["acceptanceGates"][0]["gateRef"], "GATE-RT-001")
            diagnostics = model["diagnostics"]
            self.assertTrue(any(item["ref"] == "ANOS-REQ-011" for item in diagnostics["unmapped"]))
            self.assertTrue(any(item["ref"] == "ANOS-REQ-011" for item in diagnostics["untested"]))
            self.assertTrue(any(item["ref"] == "ANOS-REQ-011" and item["reason"] == "Needs test mapping." for item in diagnostics["blocked"]))
            self.assertTrue(any(item["ref"] == "ANOS-REQ-010" and item["count"] == 3 for item in diagnostics["assumptionHeavyItems"]))

            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.assertEqual(main(["--root", str(root), "requirement", "tree", "workbench", "--project", "company-knowledge-core"]), 0)
            cli_model = json.loads(buffer.getvalue())
            self.assertEqual(cli_model["kind"], "RequirementTreeWorkbenchReadModel")
            self.assertEqual(cli_model["treeId"], model["treeId"])

    def test_requirement_tree_workbench_api_route_returns_read_model(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            write_minimal_bundle(root)
            write_requirement_tree_workbench_fixture(root)
            try:
                server = KnowledgeHTTPServer(("127.0.0.1", 0), Bundle(root), api_token="")
            except PermissionError as exc:
                self.skipTest(f"socket bind not allowed in sandbox: {exc}")
            except KnowledgeError as exc:
                if "DATABASE_URL" in str(exc) or "PostgreSQL" in str(exc):
                    self.skipTest(f"API server requires database in this environment: {exc}")
                raise
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f"http://127.0.0.1:{server.server_port}/v0/requirement-tree/workbench?projectId=company-knowledge-core"
                model = json.load(urllib.request.urlopen(url))
            finally:
                server.shutdown()
                thread.join(timeout=5)
            self.assertEqual(model["kind"], "RequirementTreeWorkbenchReadModel")
            self.assertEqual(model["chains"][0]["functionalRequirement"]["nodeRef"], "ANOS-REQ-010")
            self.assertGreaterEqual(model["counts"]["unmapped"], 1)

    def test_requirement_tree_cli_scope_exposes_accepted_requirement_tree_slices_only(self) -> None:
        parser = make_parser()
        parser.parse_args(["requirement", "tree", "import", "--project", "company-knowledge-core"])
        parser.parse_args(["requirement", "tree", "validate"])
        parser.parse_args(["requirement", "tree", "compile"])
        parser.parse_args(["requirement", "tree", "workbench"])
        parser.parse_args(["requirement", "tree", "backfill-existing-work", "--project", "company-knowledge-core"])
        for out_of_scope_command in ["context-pack", "backfill", "queue"]:
            with self.subTest(out_of_scope_command=out_of_scope_command):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        parser.parse_args(["requirement", "tree", out_of_scope_command])


if __name__ == "__main__":
    unittest.main()
