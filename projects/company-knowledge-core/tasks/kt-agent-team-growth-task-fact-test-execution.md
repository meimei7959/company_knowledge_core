---
type: ProjectTask
title: 执行 Agent 团队成长与任务事实视图 V1 测试验收
description: 测试 Agent 基于已完成的研发 TaskResult 和测试计划，执行 V1 task-fact-view、PM-worker 链路、成长信号和能力版本测试。
timestamp: "2026-06-23T09:41:00Z"
taskId: kt-agent-team-growth-task-fact-test-execution
projectId: company-knowledge-core
assignee: agent.company.test
status: done
priority: high
workSourceType: feature
requirementRefs:
  - ANOS-REQ-160
  - ANOS-REQ-160-FUSION-V1
requirementObjectRefs:
  - docs/product/ai-native-os/agent-team-growth-and-task-fact-prd.md
acceptanceCriteriaRefs:
  - docs/product/ai-native-os/agent-team-growth-and-task-fact-prd.md
  - docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md
sourceReason: 研发 Agent 已完成实现并提交 TaskResult，需要测试 Agent 执行正式测试验收。
receiverReviewRefs:
  - projects/company-knowledge-core/receiver-reviews/receiver-review.agent-team-growth-task-fact.test-execution.md
resultRef: task-results/tr-kt-agent-team-growth-task-fact-test-execution.md
---

# 执行测试验收

## Required Inputs

- `projects/company-knowledge-core/test-plans/agent-team-growth-task-fact-test-plan.md`
- `task-results/tr-kt-agent-team-growth-task-fact-development.md`
- `projects/company-knowledge-core/receiver-reviews/receiver-review.agent-team-growth-task-fact.development.md`
- `docs/product/ai-native-os/agent-team-growth-and-task-fact-prd.md`
- `projects/company-knowledge-core/technical-solutions/agent-team-growth-and-task-fact-technical-solution.md`

## Required Flow

1. Test Agent creates ReceiverReview for development handoff before execution.
2. Execute tests from the prepared test plan.
3. If implementation defects are found, create Defect and a bugfix task for Development Agent.
4. If tests pass, write test report and TaskResult.

## Expected Outputs

- ReceiverReview for test execution input.
- `projects/company-knowledge-core/test-reports/agent-team-growth-task-fact-test-report.md`
- `task-results/tr-kt-agent-team-growth-task-fact-test-execution.md`

## Acceptance Criteria

- V1 projection blocks and gap taxonomy are verified.
- API/CLI/workbench read model parity is checked where implementation exists.
- PM-worker lifecycle and growth signal scenarios are covered.
- Same-project multi-computer co-execution remains unsupported.
- `python3 -m zhenzhi_knowledge.cli validate` passes.
- Relevant unit/integration tests pass.
