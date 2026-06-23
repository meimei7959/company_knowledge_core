---
type: ProjectTask
taskId: kt-task-source-receiver-review-development
projectId: company-knowledge-core
status: done
assignee: agent.company.development
requester: agent.company.project-manager
workflow: task-source-receiver-review-orchestrator
createdAt: 2026-06-23T07:05:00Z
workSourceType: feature
requirementRefs:
  - ANOS-REQ-030
  - ANOS-REQ-033
  - ANOS-REQ-051
  - ANOS-REQ-052
  - ANOS-REQ-060
  - ANOS-REQ-061
  - ANOS-REQ-063
  - ANOS-REQ-070
  - ANOS-REQ-110
acceptanceCriteriaRefs:
  - docs/product/ai-native-os/task-source-receiver-review-prd.md
  - projects/company-knowledge-core/technical-solutions/task-source-receiver-review-technical-solution.md
  - projects/company-knowledge-core/test-plans/task-source-receiver-review-test-plan.md
receiverReviewRefs:
  - receiver-reviews/company-knowledge-core/receiver-review-task-source-receiver-review-development.md
resultRef: task-results/tr-kt-task-source-receiver-review-development.md
completedAt: 2026-06-23T07:14:00Z
auditRefs:
  - knowledge/audit/audit.20260623T071430Z-task-source-receiver-review-development.md
dependsOn:
  - tr-task-source-receiver-review-product
  - tr-task-source-receiver-review-architecture
  - tr-task-source-receiver-review-test-plan
---

# 研发任务：任务来源、Defect 与 ReceiverReview 机制落地

## 背景

产品经理 Agent 已输出产品需求，架构师 Agent 已输出技术方案，测试 Agent 已输出验收矩阵。当前 `zhenzhi_knowledge/core.py` 只有模型第一段实现，CLI/API/模板/岗位规则/测试尚未闭环。

## 研发范围

- 接入 `validate_bundle`，让任务来源、Defect、ReceiverReview 成为仓库级硬校验。
- `TaskResult` 写回时继承 `workSourceType`、需求、缺陷、验收标准和接收审查追溯字段。
- `create_requirement_task` 直接生成 `workSourceType=feature` 任务。
- 补齐 `create_bugfix_task`、`create_receiver_review` 的状态流转和引用写回。
- CLI 支持任务来源、缺陷创建、缺陷修复任务创建、接收审查创建。
- API 支持任务来源字段、Defect、ReceiverReview。
- 项目健康检查暴露来源追溯、接收审查阻断、缺陷未回归等风险。
- 更新模板和岗位规则。
- 新增或更新自动化测试，覆盖产品和测试计划中的 P0 场景。

## 角色边界

研发 Agent 开工前必须先产出接收审查记录，判断产品需求、架构方案和测试计划是否足够支撑研发。若 `ReceiverReview` 为 `needs_rework` 或 `human_decision_required`，不得继续实现，应交回项目经理 Agent 路由。

研发 Agent 不得替测试 Agent 写最终验收结论，不得替产品经理 Agent 做产品验收。

## 产出

- 代码和测试变更。
- 研发接收审查记录。
- `task-results/tr-kt-task-source-receiver-review-development.md`
- 审计记录。

## 验收入口

- `python3 -m zhenzhi_knowledge.cli validate`
- 相关单元测试。
- `git diff --check`
