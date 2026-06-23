---
taskId: kt-v2-central-runner-real-dual-host-acceptance
projectId: company-knowledge-core
type: ProjectTask
status: pending
assignee: agent.company.test
requester: agent.company.project-manager
workflow: phase2-central-runner-observability-orchestrator
createdAt: 2026-06-23T01:43:59Z
dependsOn:
  - kt-v2-central-runner-observability-test
---

# 最终验收任务：真实双机 Runner 闭环

## 验收目标

证明两台真实电脑接入同一个部署中枢，并完成一次任务从调度到结果写回的闭环。

## 验收步骤

1. 你的电脑注册为 Runner A。
2. 同事电脑注册为 Runner B。
3. 工作台能发起或展示创建项目、电脑接入邀请和工具注册申请。
4. 两台电脑都向同一个中枢地址上报心跳。
5. 项目经理 Agent 创建或选择一个测试任务。
6. 调度器把任务分配给其中一台 Runner。
7. Runner 上报任务进展、Agent、工具、Codex/Claude、模型和 token。
8. Runner 写回 TaskResult。
9. 工作台展示两台电脑、项目、任务进展、登记状态和结果。
10. 测试 Agent 出具验收报告。
11. 产品经理 Agent 验收用户可理解、登记入口和监管边界。
12. 项目经理 Agent 验收调度和过程证据。

## 不接受

- 只用本机模拟两台电脑。
- 只展示静态假数据。
- 工作台能直接派单、修复、转交、禁用 Runner、写回结果或批准验收。
- 登记入口缺少权限、确认、幂等或审计。
- 缺少模型、token、工具或 Agent 上报字段。
- 缺少审计证据。
