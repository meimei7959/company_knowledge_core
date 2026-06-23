---
type: ProjectTask
title: 研发修复 task fact V1 测试模块边界
description: 研发 Agent 将本次新增 task fact V1 测试从 tests/test_cli.py 巨型测试文件中拆出或模块化，降低 long_symbol 和 large_growth 风险。
timestamp: "2026-06-23T10:11:00Z"
taskId: kt-agtgtf-quality-dev-test-boundary
projectId: company-knowledge-core
assignee: agent.company.development
status: done
priority: high
workSourceType: bugfix
defectRefs:
  - DEF-AGTGTF-QUALITY-GATE-001
defectObjectRefs:
  - projects/company-knowledge-core/defects/def-agtgtf-quality-gate-001.md
requirementRefs:
  - ANOS-REQ-160-FUSION-V1
sourceReason: development_quality_gate flags tests/test_cli.py large growth and long task fact V1 test method; V1 tests need a scoped module boundary.
receiverReviewRefs: []
resultRef: task-results/tr-kt-agtgtf-quality-dev-test-boundary.md
---

# 研发修复测试模块边界

## Inputs

- `tests/test_cli.py`
- `projects/company-knowledge-core/test-plans/agent-team-growth-task-fact-test-plan.md`
- `projects/company-knowledge-core/defects/def-agtgtf-quality-gate-001.md`

## Scope

- 拆分或模块化本次新增的 task fact V1 测试 fixture。
- 保留现有测试覆盖，不降低断言。
- 不重构全部历史 `tests/test_cli.py`。
- 不改研发实现逻辑，除非测试拆分必须暴露公共 helper。

## Expected Outputs

- 新测试文件或测试 helper 边界。
- TaskResult：`task-results/tr-kt-agtgtf-quality-dev-test-boundary.md`

## Acceptance Criteria

- task fact V1 测试不再以一个超长方法堆在 `tests/test_cli.py`。
- 新测试可独立运行。
- 相关 `development_quality_gate.py --paths <new/changed test paths>` 通过，或历史项有架构确认。
- 全量 `tests.test_cli` 或等价回归通过。
