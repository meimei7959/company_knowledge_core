---
type: ProjectTask
title: 建设统一任务运行内核
description: 收敛现有分散流程，把任务状态、Agent 交付契约、PM 分诊、验收和通知变成系统可执行机制。
timestamp: "2026-06-21T00:00:00Z"
taskId: unified-task-runtime-core
taskType: workflow_runtime_core
projectId: company-knowledge-core
requester: meimei
assignee: agent.company.development
status: done
priority: high
dueAt: ""
sourceMaterialRefs:
  - docs/strategy/zhenzhi-ai-native-knowledge-system.md
  - docs/agent-team/company-agent-team-operating-guide.md
  - docs/agent-team/common-agent-operating-rules.md
  - projects/company-knowledge-core/pm-reviews/pm-review-unified-task-runtime-core.md
expectedOutput:
  - Unified task lifecycle definition.
  - Executable PM triage and role handoff mechanism.
  - Unified TaskResult delivery contract.
  - Status-driven notification and acceptance routing.
  - Tests proving the lifecycle can run without adding ad hoc process.
resultRef: task-results/tr-unified-task-runtime-core.md
notificationRefs:
  - notifications/notification.20260620T163114255110Z.md
  - notifications/notification.20260620T163114256087Z.md
  - notifications/notification.20260620T163114256815Z.md
  - notifications/notification.20260620T163429551113Z.md
auditRefs: []
assignedRunner: ""
leaseOwner: ""
leaseProofHash: ""
leaseExpiresAt: ""
heartbeatAt: ""
taskVersion: 1
handoffContract: {"from":"agent.company.project-manager","to":"agent.company.development","requiredArtifacts":["runtime design","state transition contract","TaskResult contract","notification and acceptance rules","tests"]}
qualityGateRequired: true
attemptNumber: 1
maxAttempts: 3
followupTaskRefs: []
guideUpdateRequired: false
guideUpdated: false
guideRef: docs/agent-team/company-agent-team-operating-guide.md
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-20T16:34:29Z"
completedAt: "2026-06-20T16:31:14Z"
---

## Request

把“统一任务生命周期、统一交付契约、统一调度器、统一验收机制、统一事件通知机制”落成可执行的任务运行内核，用它替代继续叠加零散流程和人工约定。

## Root Cause

这次审批通知闭环虽然最终修复成功，但过程暴露出系统性问题：

- Agent 岗位职责已经定义，但运行时没有强制按岗位推进。
- 任务状态没有成为唯一驱动力，下一步仍依赖人或当前会话临时判断。
- 任务类型和 handoff contract 可能错配，导致工程任务被知识任务质量门误判。
- 验收、通知、知识更新判断不是统一事件驱动，而是分散在各流程里。
- 每修一个问题就补一个流程，会让系统越来越复杂。

## Target Runtime

统一任务生命周期：

```txt
创建 -> 分诊 -> 接管 -> 执行 -> 提交结果 -> 自检 -> 复核 -> 验收 -> 发布/关闭
```

异常分支：

```txt
blocked / needs_repair / retrying / cancelled
```

每个状态必须明确：

- 当前负责 Agent。
- 必须交付的对象。
- 进入下一状态的完成标准。
- 是否需要项目经理验收。
- 是否需要人类验收。
- 需要发送哪些通知。

## Expected Output

- 状态机定义收敛为一个可测试的 runtime contract。
- PM triage 能在任务创建前判断任务类型、负责 Agent、验收路径和 handoff contract。
- 所有 Agent 结果写回统一 `TaskResult` 契约，不再按流程自由发挥。
- 任务状态变化统一生成通知，不再各功能单独拼通知。
- 生产级流程变更必须经过 PM review，必要时触发 human acceptance。
- 新机制覆盖项目创建、工程修复、知识沉淀三类典型任务。

## Acceptance Criteria

- 创建工程修复任务时，不会被知识沉淀质量门要求 KnowledgeItem draft。
- 创建知识沉淀任务时，必须要求 SourceMaterial、KnowledgeItem draft、Review 路径。
- 创建项目初始化任务时，必须要求项目经理 Agent 接管或 Runner 接管路径。
- 任一任务完成时，必须有 Agent 自检、PM review、验收策略和通知记录。
- 任务结果缺少证据、测试或 handoff/terminal reason 时，不允许进入 `done`。
- 需要人审的任务不会自动通过；不需要人审的任务会记录自动放行理由。
- 状态变更能驱动通知，且通知成功/失败都有记录。
- 测试覆盖任务创建、分诊、写回、质量门、验收、通知、异常重试。

## Handling Notes

第一阶段先在当前中央处理器内实现最小闭环，不依赖 Agent Ring 已完成。

执行方式：

1. 项目经理 Agent 完成任务分诊和 runtime design。
2. 研发 Agent 实现统一状态机、TaskResult contract 和通知路由。
3. 测试 Agent 用项目创建、知识沉淀、工程修复三类任务验证闭环。
4. 项目经理 Agent 复核是否减少复杂度，而不是新增更多流程。
5. 通过后更新 Agent Team 工作指南和相关协议文档。

## PM Triage

- reviewRef: `projects/company-knowledge-core/pm-reviews/pm-review-unified-task-runtime-core.md`
- decision: assign_to_development
- nextAgent: agent.company.development

## Handoff Contract

- from: agent.company.project-manager
- to: agent.company.development
- requiredArtifacts:
  - runtime design
  - state transition contract
  - TaskResult contract
  - notification and acceptance rules
  - tests

## Quality Gate

- 不能只写文档，必须有可运行代码、测试和至少一个端到端验证。
- 不能新增一堆互相独立的流程；实现应收敛现有流程。
- 不能破坏已有 Feishu、KnowledgeTask、ProjectTask、Agent Ring stub 流程。
- 新增状态或字段必须说明为什么不能复用现有对象。

## Guide Gate

完成后必须更新：

- `docs/agent-team/company-agent-team-operating-guide.md`
- `docs/agent-team/common-agent-operating-rules.md`
- `docs/scheduler/task-dispatch-model.md`
- `docs/protocols/agent-ring-communication-protocol.md`（如接口契约变化）
