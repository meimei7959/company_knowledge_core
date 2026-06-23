import unittest

from zhenzhi_knowledge.core import parse_frontmatter, task_result_passed, validate_pm_delivery_gates


REQ = "REQ-PM-GATE"


def task(task_id: str, assignee: str, status: str = "done", title: str = "", task_type: str = "") -> dict:
    return {
        "type": "ProjectTask",
        "taskId": task_id,
        "assignee": assignee,
        "status": status,
        "title": title,
        "taskType": task_type,
        "requirementRefs": [REQ],
    }


def result(task_id: str, executor: str, status: str = "done", decision: str = "close") -> dict:
    return {
        "type": "TaskResult",
        "taskId": task_id,
        "executorAgent": executor,
        "status": status,
        "requirementRefs": [REQ],
        "qualityEvaluation": {"status": "passed", "decision": decision},
        "acceptancePolicy": {"acceptanceStatus": "accepted"},
    }


def closeout() -> dict:
    return {
        "type": "ProjectManagerAction",
        "actor": "agent.company.project-manager",
        "intent": "closeout",
        "exitState": "closed_with_gate_passed",
        "pmDeliveryGate": {"enforce": True, "requirementRefs": [REQ], "requireProductAcceptance": True},
    }


class PmDeliveryGateTests(unittest.TestCase):
    def test_nested_status_does_not_override_task_result_top_level_status(self) -> None:
        frontmatter, _body = parse_frontmatter(
            """---
type: TaskResult
taskId: DEV
executorAgent: agent.company.development
status: done
qualityEvaluation:
  status: done_with_historical_debt
  passed: true
  decision: complete_for_scope
residualDebt:
  - trackingId: FOLLOWUP-001
    status: open
---

# Result
"""
        )

        self.assertEqual("done", frontmatter["status"])
        self.assertEqual("done_with_historical_debt", frontmatter["qualityEvaluation"]["status"])
        self.assertEqual("open", frontmatter["residualDebt"][0]["status"])

    def test_nested_quality_status_open_or_blocked_does_not_override_passing_top_level_status(self) -> None:
        for nested_status in ("open", "blocked"):
            with self.subTest(nested_status=nested_status):
                frontmatter, _body = parse_frontmatter(
                    f"""---
type: TaskResult
taskId: DEV
executorAgent: agent.company.development
status: done
qualityEvaluation:
  status: {nested_status}
---

# Result
"""
                )

                self.assertEqual("done", frontmatter["status"])
                self.assertEqual(nested_status, frontmatter["qualityEvaluation"]["status"])
                self.assertTrue(task_result_passed(frontmatter))

    def test_closeout_gate_accepts_existing_done_task_result_with_nested_status(self) -> None:
        dev_result, _body = parse_frontmatter(
            """---
type: TaskResult
taskId: DEV
executorAgent: agent.company.development
status: done
requirementRefs:
  - REQ-PM-GATE
qualityEvaluation:
  status: done_with_historical_test_cli_debt
  passed: true
  decision: complete_for_v1_test_boundary
residualDebt:
  - trackingId: FOLLOWUP-QUALITY-GOD-FILES-TEST-001
    status: open
acceptancePolicy:
  acceptanceStatus: accepted
---
"""
        )
        records = [
            ("tasks/dev.md", task("DEV", "agent.company.development", title="Implement feature", task_type="implementation")),
            ("task-results/dev.md", dev_result),
            ("tasks/test.md", task("TEST", "agent.company.test", title="Execute feature test", task_type="test_execution")),
            ("task-results/test.md", result("TEST", "agent.company.test")),
            ("tasks/product.md", task("PRODUCT", "agent.company.product-manager", title="Product acceptance", task_type="product_acceptance")),
            ("task-results/product.md", result("PRODUCT", "agent.company.product-manager", status="accepted")),
            ("pm-actions/closeout.md", closeout()),
        ]

        self.assertFalse([problem for problem in validate_pm_delivery_gates(records) if "pmDeliveryGate" in problem])

    def test_preparation_only_blocked_test_result_does_not_block_closeout(self) -> None:
        prep_result = result("TEST-PLAN", "agent.company.test", status="blocked", decision="blocked")
        prep_result.update(
            {
                "summary": "Test-plan preparation complete; formal execution blocked until development handoff.",
                "pmCloseoutScope": "test_plan_preparation_only",
            }
        )
        records = [
            ("tasks/dev.md", task("DEV", "agent.company.development", title="Implement feature", task_type="implementation")),
            ("task-results/dev.md", result("DEV", "agent.company.development")),
            ("tasks/test-plan.md", task("TEST-PLAN", "agent.company.test", title="Prepare test plan", task_type="test_plan")),
            ("task-results/test-plan.md", prep_result),
            ("tasks/test.md", task("TEST", "agent.company.test", title="Execute feature test", task_type="test_execution")),
            ("task-results/test.md", result("TEST", "agent.company.test")),
            ("tasks/product.md", task("PRODUCT", "agent.company.product-manager", title="Product acceptance", task_type="product_acceptance")),
            ("task-results/product.md", result("PRODUCT", "agent.company.product-manager", status="accepted")),
            ("pm-actions/closeout.md", closeout()),
        ]

        self.assertFalse([problem for problem in validate_pm_delivery_gates(records) if "pmDeliveryGate" in problem])

    def test_real_pending_or_failed_test_execution_still_blocks_closeout(self) -> None:
        records = [
            ("tasks/dev.md", task("DEV", "agent.company.development", title="Implement feature", task_type="implementation")),
            ("task-results/dev.md", result("DEV", "agent.company.development")),
            ("tasks/test.md", task("TEST", "agent.company.test", status="pending", title="Execute feature test", task_type="test_execution")),
            ("tasks/product.md", task("PRODUCT", "agent.company.product-manager", title="Product acceptance", task_type="product_acceptance")),
            ("task-results/product.md", result("PRODUCT", "agent.company.product-manager", status="accepted")),
            ("pm-actions/closeout.md", closeout()),
        ]
        pending_problems = validate_pm_delivery_gates(records)
        self.assertTrue(any("cannot close while Test task TEST is pending without TaskResult" in problem for problem in pending_problems))

        failed_records = [
            ("tasks/dev.md", task("DEV", "agent.company.development", title="Implement feature", task_type="implementation")),
            ("task-results/dev.md", result("DEV", "agent.company.development")),
            ("tasks/test.md", task("TEST", "agent.company.test", status="done", title="Execute feature test", task_type="test_execution")),
            ("task-results/test.md", result("TEST", "agent.company.test", status="failed", decision="repair_required")),
            ("tasks/product.md", task("PRODUCT", "agent.company.product-manager", title="Product acceptance", task_type="product_acceptance")),
            ("task-results/product.md", result("PRODUCT", "agent.company.product-manager", status="accepted")),
            ("pm-actions/closeout.md", closeout()),
        ]
        failed_problems = validate_pm_delivery_gates(failed_records)
        self.assertTrue(any("requires passing Test TaskResult for TEST" in problem for problem in failed_problems))


class PmDeliveryGateHistoricalDebtTests(unittest.TestCase):
    def test_blocked_development_result_without_superseding_evidence_blocks_closeout(self) -> None:
        dev_result = result("DEV", "agent.company.development", status="blocked", decision="repair_required")
        records = [
            ("tasks/dev.md", task("DEV", "agent.company.development", status="waiting_acceptance", title="Implement feature", task_type="implementation")),
            ("task-results/dev.md", dev_result),
            ("tasks/test.md", task("TEST", "agent.company.test", title="Execute feature test", task_type="test_execution")),
            ("task-results/test.md", result("TEST", "agent.company.test")),
            ("tasks/product.md", task("PRODUCT", "agent.company.product-manager", title="Product acceptance", task_type="product_acceptance")),
            ("task-results/product.md", result("PRODUCT", "agent.company.product-manager", status="accepted")),
            ("pm-actions/closeout.md", closeout()),
        ]

        problems = validate_pm_delivery_gates(records)
        self.assertTrue(any("requires passing Development TaskResult for DEV" in problem for problem in problems))

    def test_historical_debt_blocked_development_result_with_regression_and_product_acceptance_does_not_block_closeout(self) -> None:
        dev_result = result("DEV", "agent.company.development", status="blocked", decision="partial_due_historical_core_quality_gate")
        dev_result.update(
            {
                "summary": "Partial result blocked only by architecture-classified historical quality debt.",
                "resultId": "TR-DEV",
                "defectRefs": ["DEF-QUALITY-001"],
                "qualityEvaluation": {
                    "status": "blocked",
                    "passed": False,
                    "decision": "partial_due_historical_core_quality_gate",
                    "reasons": ["Historical debt tracked by follow-up task remains outside current delivery scope."],
                },
                "acceptancePolicy": {"acceptanceStatus": "blocked_pending_pm_or_human_decision"},
            }
        )
        test_result = result("TEST", "agent.company.test")
        test_result.update(
            {
                "resultId": "TR-TEST",
                "defectRefs": ["DEF-QUALITY-001"],
                "sourceMaterialRefs": ["task-results/TR-DEV.md", "projects/tasks/DEV.md"],
                "summary": "Regression passed; historical debt remains linked to follow-up.",
            }
        )
        product_result = result("PRODUCT", "agent.company.product-manager", status="accepted", decision="accepted")
        product_result.update(
            {
                "defectRefs": ["DEF-QUALITY-001"],
                "sourceMaterialRefs": ["task-results/TR-TEST.md"],
                "summary": "Product reacceptance accepted after regression.",
            }
        )
        records = [
            ("tasks/dev.md", task("DEV", "agent.company.development", status="waiting_acceptance", title="Implement feature", task_type="implementation")),
            ("task-results/dev.md", dev_result),
            ("tasks/test.md", task("TEST", "agent.company.test", title="Execute feature test", task_type="test_execution")),
            ("task-results/test.md", test_result),
            ("tasks/product.md", task("PRODUCT", "agent.company.product-manager", title="Product acceptance", task_type="product_acceptance")),
            ("task-results/product.md", product_result),
            ("pm-actions/closeout.md", closeout()),
        ]

        self.assertFalse([problem for problem in validate_pm_delivery_gates(records) if "pmDeliveryGate" in problem])


if __name__ == "__main__":
    unittest.main()
