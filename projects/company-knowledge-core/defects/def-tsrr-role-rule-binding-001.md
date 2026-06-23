---
type: Defect
title: 岗位 Agent 规则未直接接入任务来源与 ReceiverReview 机制
description: Bug or quality issue that can create bugfix ProjectTasks without a product requirement.
timestamp: "2026-06-23T07:43:59Z"
defectId: DEF-TSRR-ROLE-RULE-BINDING-001
projectId: company-knowledge-core
reporter: agent.company.test
owner: agent.company.development
severity: medium
status: closed
requirementRefs: []
sourceTaskRef: projects/company-knowledge-core/tasks/kt-task-source-receiver-review-development.md
sourceResultRef: task-results/tr-kt-task-source-receiver-review-development.md
evidenceRefs:
  - projects/company-knowledge-core/test-reports/task-source-receiver-review-test-report.md
  - agents/agent.company.project-manager.md
  - agents/agent.company.product-manager.md
  - agents/agent.company.architecture.md
  - agents/agent.company.design.md
  - agents/agent.company.development.md
  - agents/agent.company.test.md
  - docs/agent-team/role-operating-specs.json
  - task-results/tr-kt-20260623-002.md
expectedBehavior: 各岗位 Agent 卡和角色规则必须直接声明 workSourceType、requirementRefs、defectRefs、ReceiverReview/Defect 使用规则；下游 Agent 开工前必须能从自身岗位规则读到接收审查门禁。
actualBehavior: 模板与 skill pack 已包含机制，但 agents/agent.company.*.md 多数未直接包含关键字段和 ReceiverReview/Defect 开工规则，role-operating-specs.json 也缺少 workSourceType 字段字面约束。
reproductionSteps:
  - 运行模板/岗位规则静态探针，检查 templates、agents/agent.company.*.md、docs/agent-team/role-operating-specs.json 是否包含任务来源和 ReceiverReview/Defect 关键字段。
  - 观察 templates 全部通过，但 project-manager/product-manager/architecture/design/development/test Agent 卡与 role-operating-specs 存在缺失。
fixTaskRefs:
  - projects/company-knowledge-core/tasks/kt-20260623-002.md
auditRefs:
  - knowledge/audit/audit.20260623T074359410682Z.md
  - knowledge/audit/audit.20260623T074441Z-task-source-receiver-review-regression.md
  - knowledge/audit/audit.20260623T075045Z-tsrr-role-rule-binding-fix.md
  - knowledge/audit/audit.20260623T075557Z-tsrr-role-rule-binding-regression-passed.md
regressionEvidenceRefs:
  - projects/company-knowledge-core/test-reports/task-source-receiver-review-test-report.md
  - task-results/tr-kt-task-source-receiver-review-test.md
  - tests/test_cli.py
updatedAt: "2026-06-23T07:55:57Z"
---

## Expected Behavior

各岗位 Agent 卡和角色规则必须直接声明 workSourceType、requirementRefs、defectRefs、ReceiverReview/Defect 使用规则；下游 Agent 开工前必须能从自身岗位规则读到接收审查门禁。

## Actual Behavior

模板与 skill pack 已包含机制，但 agents/agent.company.*.md 多数未直接包含关键字段和 ReceiverReview/Defect 开工规则，role-operating-specs.json 也缺少 workSourceType 字段字面约束。

## Reproduction Steps

- 运行模板/岗位规则静态探针，检查 templates、agents/agent.company.*.md、docs/agent-team/role-operating-specs.json 是否包含任务来源和 ReceiverReview/Defect 关键字段。
- 观察 templates 全部通过，但 project-manager/product-manager/architecture/design/development/test Agent 卡与 role-operating-specs 存在缺失。

## Evidence

- projects/company-knowledge-core/test-reports/task-source-receiver-review-test-report.md
- agents/agent.company.project-manager.md
- agents/agent.company.product-manager.md
- agents/agent.company.architecture.md
- agents/agent.company.design.md
- agents/agent.company.development.md
- agents/agent.company.test.md
- docs/agent-team/role-operating-specs.json

## Regression Result

已回归通过并关闭。测试 Agent 复验确认 6 张岗位 Agent 卡和 `docs/agent-team/role-operating-specs.json` 均已直接绑定任务来源字段、Defect 字段和 ReceiverReview 接收审查门禁；核心 P0 行为回归 6 项通过。
