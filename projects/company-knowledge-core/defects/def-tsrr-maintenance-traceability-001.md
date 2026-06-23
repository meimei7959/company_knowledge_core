---
type: Defect
title: Maintenance workSourceType 缺少来源输入时 validate 未失败
description: Bug or quality issue that can create bugfix ProjectTasks without a product requirement.
timestamp: "2026-06-23T07:28:07Z"
defectId: DEF-TSRR-MAINTENANCE-TRACEABILITY-001
projectId: company-knowledge-core
reporter: agent.company.test
owner: agent.company.development
severity: medium
status: closed
requirementRefs: []
sourceTaskRef: projects/company-knowledge-core/tasks/kt-task-source-receiver-review-development.md
sourceResultRef: task-results/tr-kt-task-source-receiver-review-development.md
evidenceRefs:
  - projects/company-knowledge-core/test-plans/task-source-receiver-review-test-plan.md
  - projects/company-knowledge-core/test-reports/task-source-receiver-review-test-report.md
  - zhenzhi_knowledge/core.py
  - tests/test_cli.py
expectedBehavior: workSourceType=maintenance 且没有 sourceReason/sourceMaterialRefs/expectedOutput 等来源输入时，validate_bundle 必须报错。
actualBehavior: validate_bundle 对 workSourceType=maintenance 且来源输入为空的任务未报错。
reproductionSteps:
  - 创建 ProjectTask：workSourceType=maintenance，且不填写 sourceReason、sourceMaterialRefs、expectedOutput。
  - 运行 validate_bundle。
  - 观察结果：没有 maintenance task requires 类错误。
fixTaskRefs:
  - projects/company-knowledge-core/tasks/kt-20260623-001.md
regressionEvidenceRefs:
  - projects/company-knowledge-core/test-reports/task-source-receiver-review-test-report.md
  - task-results/tr-kt-task-source-receiver-review-test.md
  - tests/test_cli.py
auditRefs:
  - knowledge/audit/audit.20260623T072807275887Z.md
  - knowledge/audit/audit.20260623T073547Z-tsrr-maintenance-traceability-fix.md
  - knowledge/audit/audit.20260623T074441Z-task-source-receiver-review-regression.md
updatedAt: "2026-06-23T07:44:41Z"
---

## Expected Behavior

workSourceType=maintenance 且没有 sourceReason/sourceMaterialRefs/expectedOutput 等来源输入时，validate_bundle 必须报错。

## Actual Behavior

validate_bundle 对 workSourceType=maintenance 且来源输入为空的任务未报错。

## Reproduction Steps

- 创建 ProjectTask：workSourceType=maintenance，且不填写 sourceReason、sourceMaterialRefs、expectedOutput。
- 运行 validate_bundle。
- 观察结果：没有 maintenance task requires 类错误。

## Evidence

- projects/company-knowledge-core/test-plans/task-source-receiver-review-test-plan.md
- projects/company-knowledge-core/test-reports/task-source-receiver-review-test-report.md
- zhenzhi_knowledge/core.py
- tests/test_cli.py

## Regression Result

Closed by `agent.company.test` after rerunning `TSRR-007`.

- `python3 -m unittest tests.test_cli.CliTests.test_task_source_traceability_validation_rules`: passed.
- `python3 -m unittest tests.test_cli`: passed, 191 tests.
- `projects/company-knowledge-core/test-reports/task-source-receiver-review-test-report.md` records the maintenance regression as passed.
