---
type: ProjectTask
taskId: kt-v2-pm-control-lease-architecture
projectId: company-knowledge-core
status: pending
assignee: agent.company.architecture
requester: agent.company.project-manager
workflow: phase2-pm-control-lease-orchestrator
createdAt: 2026-06-23T02:57:45Z
dependsOn:
  - kt-v2-pm-control-lease-product
---

# 架构任务：PM 主控租约技术方案

## 任务

架构 Agent 输出技术方案。

必须覆盖：

- PMControlLease 数据模型。
- 主控/协同/备用 PM 会话模型。
- PM 写操作租约校验。
- 无租约、过期租约、非主控租约、项目不匹配租约的拒绝语义和审计。
- 接管流程和异常恢复。
- API、CLI、core、workbench read model 复用与新增。
- 对已有 Runner/工作台/登记入口能力的兼容性。

## 产出

- `projects/company-knowledge-core/technical-solutions/phase2-pm-control-lease-technical-solution.md`

## 完成标准

- 研发可按方案实现。
- 测试可按方案写验收用例。
