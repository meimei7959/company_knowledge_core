---
taskId: kt-v2-central-runner-observability-architecture
projectId: company-knowledge-core
type: ProjectTask
status: processing
assignee: agent.company.architecture
requester: agent.company.project-manager
workflow: phase2-central-runner-observability-orchestrator
createdAt: 2026-06-23T01:43:59Z
---

# 架构任务：中枢 API 与 Runner 上报协议

## 任务

架构 Agent 输出技术方案，明确：

- 已部署中枢地址如何承载 Runner 注册、心跳、任务领取、进展事件和 TaskResult 写回。
- Runner 配对码或 Token 如何生成、使用、吊销。
- Runner 注册、心跳、任务进展、模型/token/tool 上报、Agent 会话上报的数据契约。
- 工作台登记入口 API 如何创建项目、生成电脑接入邀请、提交工具注册或工具注册申请。
- 工作台运行监管查询模型如何从中枢生成。
- 多项目隔离和 Runner 项目授权。
- 幂等、离线恢复、重复写回、任务租约过期、异常重试。
- 审计记录和敏感信息过滤。
- 现有 CLI/core/read model 哪些可复用，哪些需要新增。

## 产出

- `projects/company-knowledge-core/technical-solutions/phase2-central-runner-observability-technical-solution.md`

## 完成标准

- 研发能按方案实现 API、CLI 和 read model。
- 测试能按方案验证注册、上报、查询、异常恢复和项目隔离。
- 方案必须区分登记入口和运行监管；登记入口可操作，运行监管不允许直接篡改执行状态或结果。
