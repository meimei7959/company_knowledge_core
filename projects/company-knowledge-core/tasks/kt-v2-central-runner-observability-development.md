---
taskId: kt-v2-central-runner-observability-development
projectId: company-knowledge-core
type: ProjectTask
status: pending
assignee: agent.company.development
requester: agent.company.project-manager
workflow: phase2-central-runner-observability-orchestrator
createdAt: 2026-06-23T01:43:59Z
dependsOn:
  - kt-v2-central-runner-observability-product
  - kt-v2-central-runner-observability-architecture
  - kt-v2-central-runner-observability-design
---

# 研发任务：实现中枢监管与 Runner 上报

## 开工条件

产品 PRD、架构方案、设计方案和产品复核均完成后才能开工。

## 实现范围

- 中枢 API 支持 Runner 注册、心跳、任务领取、进展上报、TaskResult 写回和只读查询。
- 中枢 API 支持从工作台发起项目创建、电脑接入邀请、工具注册或工具注册申请，并写入权限、审批和审计记录。
- 登记类 API 必须有幂等键，重复点击或网络重试不得创建重复项目、重复电脑邀请或重复工具申请。
- Runner 客户端或 CLI 支持按中枢地址注册电脑、持续心跳、上报任务进展、模型、token、工具、Codex/Claude 执行器类型和 Agent 会话。
- 工作台提供登记入口，并展示项目列表、电脑列表、项目任务明细和电脑详情。
- 工作台所有面向用户文案为中文，内部 id 只作为辅助证据，不作为主展示。
- 敏感信息过滤：不展示原始 token、密钥、Cookie、SSH 私钥。
- 输出接入说明：同事电脑如何接入当前中枢。

## 完成标准

- 本地测试通过。
- 工作台显示至少一台本机 Runner 的真实 read model。
- 模型、token、工具、Codex/Claude、Agent、电脑、项目、需求映射字段完整。
- 工作台只有登记类写入口；运行监管区域没有任何会直接改变执行状态或结果的操作入口。
