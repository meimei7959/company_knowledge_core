---
type: ProjectTask
taskId: kt-v2-pm-control-lease-development
projectId: company-knowledge-core
status: pending
assignee: agent.company.development
requester: agent.company.project-manager
workflow: phase2-pm-control-lease-orchestrator
createdAt: 2026-06-23T02:57:45Z
dependsOn:
  - kt-v2-pm-control-lease-product-review
---

# 研发任务：PM 主控租约实现

## 开工条件

产品需求、架构方案、产品复核均通过。

## 实现范围

- core/server/cli 中补 PM 主控租约能力。
- PM 写操作必须校验租约。
- 无租约或无效租约拒绝写入并审计。
- 工作台 read model 和页面展示主控 PM、协同 PM、备用 PM、租约健康、接管记录。
- 补单元测试、API/CLI 测试、工作台测试。

## 产出

- `task-results/tr-kt-v2-pm-control-lease-development.md`

## 失败回路

测试失败必须回研发 Agent 返工。
