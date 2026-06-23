---
type: Workflow
workflowId: phase2-pm-control-lease-orchestrator
projectId: company-knowledge-core
owner: agent.company.project-manager
status: draft
createdAt: 2026-06-23T02:57:45Z
source: user-request
---

# 同一项目多电脑 PM 主控租约编排器

## 目标

在同一个项目被多台电脑、多条会话或多个项目经理 Agent 同时接入时，确保同一时间只有一个主控 PM 持有调度租约。其他 PM 只能作为协同 PM 或备用 PM，不能直接写调度状态。

## 必须实现

- 同一项目同一时间只能一个主控 PM 持有调度租约。
- 协同 PM 和备用 PM 可以查看、评论、准备接管，但不能执行会改变项目调度状态的写操作。
- 所有 PM 写操作必须携带有效调度租约。
- 中枢拒绝无租约、过期租约、非主控租约或项目不匹配租约的写入，并写审计。
- 工作台展示主控 PM、协同 PM、备用 PM、租约健康、租约到期、最近心跳和接管记录。
- 接管必须有原因、操作者、前任主控、后任主控、时间、租约变化和审计记录。

## 编排顺序

1. 产品经理 Agent 输出产品需求和验收口径。
2. 架构 Agent 输出 PM 主控租约的数据模型、API、CLI、工作台 read model、拒绝审计和异常恢复方案。
3. 产品经理 Agent 复核架构方案。
4. 研发 Agent 实现 core/server/cli/workbench/tests。
5. 测试 Agent 验证单主控、协同/备用只读、无租约拒绝、接管、审计、工作台展示和兼容性。
6. 产品经理 Agent 做产品验收。
7. 项目经理 Agent 做过程验收；若真实多电脑证据缺失，自动创建真实部署补验任务。

## 项目经理边界

PM Agent 只能创建流程、任务、风险、审计、交接和验收路由。PM Agent 不得直接实现 core、API、CLI、前端或测试代码。

如果 PM Agent 在协调中产生实现补丁，该补丁只算草稿，必须由研发 Agent 接管、测试 Agent 验证、产品 Agent 验收后才能计入进度。

## 研发准入

研发 Agent 必须在以下材料存在后开工：

- 产品需求。
- 架构技术方案。
- 产品对架构方案的复核。
- 明确测试任务和失败回路。

## 验收门禁

- 本地 API/CLI 单元测试通过。
- 工作台展示中文、用户可理解，不用内部 ID 作为主信息。
- 无有效 PM 调度租约的写入口必须失败，且必须写 `pm_control_lease.denied` 或等价审计。
- 主控 PM 租约过期后，备用 PM 只能通过接管流程成为新主控，不能静默写入。
- 已有单机/多设备 Runner 能力不回归。
