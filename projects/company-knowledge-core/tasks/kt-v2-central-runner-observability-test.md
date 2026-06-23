---
taskId: kt-v2-central-runner-observability-test
projectId: company-knowledge-core
type: ProjectTask
status: pending
assignee: agent.company.test
requester: agent.company.project-manager
workflow: phase2-central-runner-observability-orchestrator
createdAt: 2026-06-23T01:43:59Z
dependsOn:
  - kt-v2-central-runner-observability-development
---

# 测试任务：中枢监管与 Runner 上报验收

## 测试范围

- Runner 注册、重复注册、Token 错误、Token 吊销。
- 心跳、离线、恢复、租约过期。
- 任务领取、进展上报、模型/token/tool 上报、TaskResult 写回。
- 多项目隔离：Runner 不能看到未授权项目任务。
- 工作台登记入口：创建项目、电脑注册/邀请、工具注册/申请必须走权限、确认、幂等和审计。
- 工作台运行监管只读：不能触发派单、禁用、转交、修复、验收、写回或篡改结果。
- 工作台中文可读：用户能看懂电脑、项目、任务、需求、模型、token、工具、Codex/Claude 执行器类型和异常。
- 敏感信息过滤。

## 完成标准

- 自动化测试覆盖 API/CLI/read model。
- 浏览器或客户端截图验证工作台主视图。
- 测试必须覆盖登记入口成功、重复提交、无权限、审批中和失败状态。
- 测试失败时必须生成返工任务给研发 Agent，不由项目经理 Agent 直接修。
