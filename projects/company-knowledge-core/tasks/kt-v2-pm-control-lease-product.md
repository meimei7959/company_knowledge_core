---
type: ProjectTask
taskId: kt-v2-pm-control-lease-product
projectId: company-knowledge-core
status: processing
assignee: agent.company.product-manager
requester: agent.company.project-manager
workflow: phase2-pm-control-lease-orchestrator
createdAt: 2026-06-23T02:57:45Z
---

# 产品任务：同一项目多电脑 PM 主控租约

## 任务

产品经理 Agent 定义同一项目多电脑场景下的 PM 主控租约需求。

必须覆盖：

- 为什么同一项目只能一个主控 PM。
- 主控 PM、协同 PM、备用 PM 的用户角色和权限边界。
- 哪些 PM 写操作必须带租约。
- 中枢拒绝无租约写入时用户看到什么。
- 工作台如何展示主控 PM、协同 PM、备用 PM、租约健康、接管记录。
- 接管流程、异常恢复、验收标准。

## 产出

- `docs/product/ai-native-os/phase-2-pm-control-lease-prd.md`

## 完成标准

- 研发能知道要实现哪些对象、字段、API 和工作台展示。
- 测试能据此验证冲突防护和接管流程。
