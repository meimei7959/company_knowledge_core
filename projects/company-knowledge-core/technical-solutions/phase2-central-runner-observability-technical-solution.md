---
type: Workflow
title: Phase 2 中枢/Runner 注册与进展上报技术方案
description: 基于已部署中枢 knowledge-api 与多设备 Runner 的注册、接入、观测、审计和工作台边界方案。
projectId: company-knowledge-core
phase: phase2
status: draft
createdAt: "2026-06-23"
sourceRefs:
  - docs/strategy/zhenzhi-ai-native-knowledge-system.md
  - docs/architecture/central-processor-and-agent-ring.md
  - docs/protocols/agent-ring-communication-protocol.md
  - docs/scheduler/task-dispatch-model.md
  - docs/product/ai-native-os/phase-2-multi-device-runner-collaboration-prd.md
  - projects/company-knowledge-core/technical-solutions/phase2-multi-device-runner-collaboration-technical-solution.md
  - projects/company-knowledge-core/desktop-workbench-slice0/shared-frontend-foundation.ts
  - scripts/distributed_runner_proof_harness.py
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/cli.py
---

# Phase 2 中枢/Runner 注册与进展上报技术方案

## 1. 结论

Phase 2 方案二采用已部署中枢 `http://124.221.138.151/knowledge-api` 作为项目事实入口和调度事实源，多设备 Runner 作为本地执行节点。系统分三层：

1. 工作台：入口可操作，执行监管只读。
2. 中枢 API：项目、Runner、工具、任务、租约、事件、审计、通知和只读监管模型的唯一事实入口。
3. Runner CLI/Agent Ring：本地电脑注册、领取任务、执行工具/模型、缓冲进展事件、写回 TaskResult 与 AgentRun。

关键边界：

- 工作台可以创建项目、生成电脑接入邀请/配对码、注册工具或提交工具注册申请。
- 工作台可以查看任务执行、进展、模型/token/tool/Agent 状态和异常。
- 工作台不直接派单、不抢租约、不修复任务、不改执行结果、不伪造 TaskResult/AgentRun。
- 调度和执行状态变更只允许 Scheduler 与持有有效 lease token 的 Runner 写入。

## 2. 范围

本方案覆盖：

- API/CLI 边界。
- Runner 注册。
- 配对码或 Token。
- Runner 心跳。
- 任务领取。
- 任务进展事件。
- 模型、token、tool 上报。
- Agent 会话状态。
- 幂等。
- 离线恢复。
- 项目隔离。
- 审计。
- 工作台“入口可操作，执行监管只读”模型。
- 可复用的现有 CLI/core/harness 能力。

本方案不覆盖：

- Agent Ring 本地执行器内部实现。
- 本地 Codex/Claude/local model 调度细节。
- 工具密钥内容存储。
- 工作台视觉设计。
- 具体数据库迁移脚本。

## 3. 架构原则

### 3.1 中枢拥有事实，不拥有执行

中枢拥有：

- Project。
- ProjectTask / KnowledgeTask。
- TaskResult。
- AgentRun。
- AgentRunner。
- ToolAsset。
- SourceMaterial。
- NotificationRecord。
- AuditLog。
- 调度、租约、状态机、审计、通知、工作台 read/write command 结果。

中枢不拥有：

- 本地模型 runtime。
- 本地工具密钥。
- 本地 Agent Ring 实现。
- 电脑上的源码执行环境。
- 直接分布式执行能力。

### 3.2 工作台双面边界

工作台分成两个明确能力面：

1. 可操作入口。
   - 创建项目。
   - 生成电脑接入邀请或配对码。
   - 注册工具。
   - 提交工具注册申请。

2. 只读监管。
   - 查看任务队列、任务执行、Runner lease、进展事件。
   - 查看模型、token、tool 使用摘要。
   - 查看 Agent session 状态。
   - 查看异常、失败、离线恢复状态。
   - 不允许直接派单、直接修复、直接改结果、直接重写 AgentRun。

### 3.3 所有写入必须可审计

所有工作台入口写入、Runner 写入、Scheduler 写入、审批动作都必须生成 AuditLog。对外展示使用人可读摘要；内部 ID 只作为可追溯引用。

### 3.4 Lease 是执行写入边界

Runner 只能在持有有效 lease token 时执行任务写入：

- pull context。
- extend task heartbeat。
- append progress event。
- write TaskResult。
- write AgentRun。

中枢只存 token hash / proof hash，不存明文 lease token。

## 4. 角色与信任边界

| 角色 | 权限边界 |
| --- | --- |
| Human Owner | 配置项目、审批高风险工具、查看监管状态、接受/拒绝结果 |
| Workbench User | 可按权限创建项目、生成配对邀请、提交工具注册申请、查看执行监管 |
| Workbench Admin | 可批准电脑接入、批准工具注册、管理项目成员和权限 |
| Scheduler | 计算候选 Runner、发放/释放 lease、标记 waiting_runner/claimed/processing |
| Runner | 注册能力、心跳、领取任务、上报进展、写回结果 |
| Agent Session | Runner 内部一个 Agent 执行会话，报告当前任务和状态 |
| Knowledge Review Agent | 只检查知识候选，不替代执行结果审批 |

安全边界：

- 工作台用户身份不等于 Runner 身份。
- Runner token 不等于用户登录 token。
- lease token 不等于长期 API token。
- 工具注册申请不等于工具可执行权限。
- 只读监管查询不产生执行副作用。

## 5. API/CLI 边界

### 5.1 API 边界

中枢 API 负责：

- 接收工作台入口命令。
- 接收 Runner 注册、心跳、任务领取、任务事件、结果写回。
- 提供工作台监管 read model。
- 执行权限、幂等、审计、项目隔离和审批检查。

建议 API 版本：

- 保留现有 `/v0` Runner/任务闭环接口。
- 新增 `/v0/workbench/*` 入口命令。
- 新增 `/v0/task-events` 和 `/v0/runner-telemetry`，承接进展与遥测。
- 输出 read model 仍保持 `apiVersion`、`kind` 字段。

### 5.2 CLI 边界

CLI 负责本地操作封装：

- Runner 注册与配对。
- Runner 心跳 daemon。
- 本地 lease state 保存。
- task claim / pull / heartbeat / finish。
- progress event 本地缓冲和补发。
- Agent session register / heartbeat。
- 工具能力扫描和工具注册申请。

CLI 不负责：

- 决定全局调度策略。
- 绕过审批直接启用高风险工具。
- 修改其他 Runner 的 lease。
- 修改已提交 TaskResult。
- 在工作台外伪造用户审批。

### 5.3 API 与 CLI 调用关系

```txt
Workbench
  -> POST /v0/workbench/projects
  -> POST /v0/workbench/runner-invitations
  -> POST /v0/workbench/tools
  -> POST /v0/workbench/tool-registration-requests
  -> GET  /v0/workbench/projects/{projectId}/execution-read-model

Runner CLI / Agent Ring
  -> POST /v0/runners/register
  -> POST /v0/runners/heartbeat
  -> POST /v0/tasks/claim
  -> POST /v0/tasks/pull
  -> POST /v0/tasks/heartbeat
  -> POST /v0/task-events
  -> POST /v0/runner-telemetry
  -> POST /v0/agent-sessions/register
  -> POST /v0/agent-sessions/heartbeat
  -> POST /v0/tasks/finish

Scheduler
  -> reads ProjectTask, AgentRunner, ToolAsset, Policy
  -> writes assignment recommendation, lease, stale lease recovery, audit
```

## 6. 工作台可操作入口

### 6.1 创建项目

接口：

```txt
POST /v0/workbench/projects
```

请求字段：

```json
{
  "projectId": "company-knowledge-core",
  "name": "Company Knowledge Core",
  "owner": "user.meimei",
  "sourceMode": "local_repo",
  "repositoryRefs": ["/Users/meimei/Documents/company_knowledge_core"],
  "defaultAssignees": ["agent.company.project-manager"],
  "deduplicationRef": "workbench:create-project:company-knowledge-core:20260623"
}
```

写入：

- Project。
- 初始 ProjectTask 或 ProjectLaunch 记录。
- NotificationRecord。
- AuditLog。

权限：

- `project.create`。
- 如果绑定已有 repo，需要 `project.repository.attach`。
- 如果生成初始任务，需要 `task.create`。

审批：

- 普通本地项目可自动创建。
- 涉及外部 repo、权限变更、客户资料、成员邀请，必须生成审批请求或 ProjectTask，不直接执行外部副作用。

幂等：

- `deduplicationRef` 与 `projectId` 唯一。
- 重复请求返回已有 Project 和 AuditLog 引用。

安全：

- 不允许在创建项目时存密钥。
- repositoryRefs 必须落在允许 scope 内。
- 人可读错误优先：如“项目已存在”，内部冲突码作为附加字段。

### 6.2 生成电脑接入邀请/配对码

接口：

```txt
POST /v0/workbench/runner-invitations
```

请求字段：

```json
{
  "projectId": "company-knowledge-core",
  "runnerLabel": "Meimei MacBook Pro",
  "requestedCapabilities": ["development", "git", "knowledge_sync"],
  "expiresInSeconds": 900,
  "deduplicationRef": "workbench:runner-invite:company-knowledge-core:meimei-mbp"
}
```

响应字段：

```json
{
  "apiVersion": "v0.1",
  "kind": "RunnerInvitation",
  "invitationId": "runner-invitation.company-knowledge-core.20260623",
  "pairingCode": "847-291",
  "pairingCodeExpiresAt": "2026-06-23T10:15:00Z",
  "runnerRegistrationUrl": "http://124.221.138.151/knowledge-api/v0/runners/register",
  "scopePreview": {
    "projectId": "company-knowledge-core",
    "capabilities": ["development", "git", "knowledge_sync"]
  }
}
```

写入：

- RunnerInvitation 或 CredentialRequest。
- AuditLog：`runner.invitation.create`。
- NotificationRecord：可选，发给项目 Owner 或待接入人。

权限：

- `runner.invitation.create`。
- 如果邀请允许敏感 dataScopes，需要 `runner.scope.approve` 或人审。

审批：

- 只允许本项目、低风险能力、无敏感数据 scope 的邀请可自动生成。
- 包含生产权限、客户数据、外部工具写权限、审批代办能力时，生成 approval request。

安全：

- 配对码短期有效，只展示一次。
- 中枢只存 `pairingCodeHash`。
- 配对码不能直接执行任务，只能兑换 runner bootstrap token。
- bootstrap token 只能完成首次 `/v0/runners/register`。
- Runner 长期 token 必须可轮换、可撤销、按项目 scope 限制。

### 6.3 注册工具

接口：

```txt
POST /v0/workbench/tools
```

适用：

- 低风险、只读、已批准 tool type。
- 不含密钥。
- 不扩大项目权限。

请求字段：

```json
{
  "projectId": "company-knowledge-core",
  "toolName": "local-git-status",
  "toolType": "cli",
  "riskLevel": "low",
  "allowedOperations": ["read_repo_status"],
  "runnerScopes": ["runner.meimei-mac-local-codex"],
  "deduplicationRef": "workbench:tool-register:company-knowledge-core:local-git-status"
}
```

写入：

- ToolAsset。
- AuditLog：`tool.register`。

权限：

- `tool.register.low_risk`。

安全：

- 禁止提交 secret value。
- tool command 需要结构化字段，不接受自由 shell 片段作为可执行事实。
- ToolAsset 只记录能力、owner、scope、risk，不保存凭据。

### 6.4 提交工具注册申请

接口：

```txt
POST /v0/workbench/tool-registration-requests
```

适用：

- 写权限工具。
- 外部 SaaS/API 工具。
- 需要 token/key 的工具。
- 影响客户、权限、财务、生产环境的工具。

请求字段：

```json
{
  "projectId": "company-knowledge-core",
  "toolName": "lark-approval-writer",
  "toolType": "lark_api",
  "riskLevel": "high",
  "requestedOperations": ["create_approval_instance"],
  "secureStorageRule": "secret_ref_required",
  "owner": "user.meimei",
  "justification": "用于项目审批闭环，不存储明文 token。",
  "deduplicationRef": "workbench:tool-request:company-knowledge-core:lark-approval-writer"
}
```

写入：

- ToolRegistrationRequest 或 CredentialRequest。
- ProjectTask：需要工具 Owner 审批时创建。
- NotificationRecord。
- AuditLog：`tool.registration_request.create`。

审批：

- Tool Owner approval 必须先于工具启用。
- 审批通过后才创建 active ToolAsset 或更新 tool status。
- 审批拒绝后，工具保持 `requested` 或 `rejected`，Runner 不可调用。

安全：

- 申请可描述密钥需求，但不接收密钥值。
- 凭据只允许通过 secret reference 或外部 vault reference 绑定。
- 审批记录必须说明可执行范围、项目 scope、数据 scope、撤销方式。

## 7. 工作台只读监管模型

工作台监管面查询：

```txt
GET /v0/workbench/projects/{projectId}/execution-read-model
GET /v0/scheduler/workbench?projectId={projectId}
GET /v0/v1/workbench?projectId={projectId}
```

返回聚合：

- activeQueue。
- selectedTask。
- runnerRegistry。
- runnerLeases。
- currentWork。
- runnerCandidates。
- leaseStatus。
- leaseHistory。
- executionContextStatus。
- progressEvents。
- telemetrySummary。
- agentSessions。
- auditTrail。
- notifications。
- metrics。
- exceptions。
- recoveryStatus。

监管面禁止命令：

- 不提供 `dispatchTask`。
- 不提供 `repairTask`。
- 不提供 `overwriteTaskResult`。
- 不提供 `editAgentRun`。
- 不提供 `forceCompleteTask`。
- 不提供 `claimAsWorkbench`。

需要动作时，工作台只能创建“请求型对象”：

- retry request。
- manual handoff request。
- tool registration request。
- human acceptance decision。
- project task for repair。

这些请求再由 Scheduler、Runner 或对应审批流处理。

## 8. Runner 注册协议

### 8.1 首次注册流程

```txt
Workbench 生成 RunnerInvitation
-> 人把 pairingCode 交给同事电脑
-> Runner CLI 输入中枢 URL + pairingCode
-> Runner CLI 调 /v0/runners/register
-> 中枢校验 pairingCodeHash、有效期、项目 scope、能力 scope
-> 中枢创建/更新 AgentRunner
-> 中枢返回 runnerId、runnerAccessRef、allowedProjects、heartbeatInterval
-> Runner CLI 本地保存 token 到系统安全存储或本地 secret store
-> Runner 开始 heartbeat
```

### 8.2 注册接口

现有 harness 已覆盖：

```txt
POST /v0/runners/register
```

建议请求字段：

```json
{
  "runnerId": "runner.meimei-mbp-codex",
  "name": "Meimei MBP Codex",
  "pairingCode": "847-291",
  "hostType": "macos",
  "mode": "unattended",
  "ringVersion": "0.2.0",
  "agents": ["agent.company.development"],
  "capabilities": ["development", "git", "knowledge_sync"],
  "tools": [
    {
      "toolName": "codex",
      "toolVersion": "gpt-5-codex",
      "riskLevel": "local_execution"
    }
  ],
  "models": [
    {
      "provider": "openai",
      "model": "gpt-5-codex",
      "mode": "hosted"
    }
  ],
  "availableProjects": ["company-knowledge-core"],
  "repositoryScopes": ["/Users/meimei/Documents/company_knowledge_core"],
  "dataScopes": ["local_repo"],
  "deduplicationRef": "runner-register:runner.meimei-mbp-codex:install-001"
}
```

响应字段：

```json
{
  "apiVersion": "v0.1",
  "kind": "RunnerRegistrationResult",
  "runnerRef": "runners/runner.meimei-mbp-codex.md",
  "runnerId": "runner.meimei-mbp-codex",
  "runnerAccessRef": "<shown once>",
  "accessExpiresAt": null,
  "heartbeatIntervalSeconds": 30,
  "allowedProjects": ["company-knowledge-core"],
  "auditRef": "audit/audit.20260623.runner-register.md"
}
```

中枢存储：

- `runnerAccessRefHash`。
- `pairingProofHash`。
- `availableProjects`。
- `capabilities`。
- `repositoryScopes`。
- `dataScopes`。
- `tools` 摘要，不含密钥。
- `models` 摘要，不含 API key。
- `lastHeartbeatAt`。

审计：

- `runner.register`。
- `runner.upsert`。
- `runner.pairing.consume`。

## 9. Token 与配对码

Token 分三类：

| 类型 | 生命周期 | 用途 | 存储 |
| --- | --- | --- | --- |
| pairingCode | 5-15 分钟 | 首次证明邀请 | 中枢仅存 hash |
| runnerAccessRef | 长期，可撤销 | Runner 身份认证 | 中枢仅存 hash，Runner 本地 secret store |
| leaseAccessRef | 短期 | 单任务执行写入 | 中枢仅存 leaseProofHash / leaseAccessRefHash |

规则：

- pairingCode 一次性使用。
- runnerAccessRef 可轮换；轮换生成 AuditLog。
- leaseAccessRef 只在 claim 响应中返回一次。
- TaskResult 只记录 lease proof，不记录明文 token。
- 日志、进展事件、异常、工作台 read model 不展示明文 token。

## 10. Runner 心跳

现有接口：

```txt
POST /v0/runners/heartbeat
```

请求字段：

```json
{
  "runnerId": "runner.meimei-mbp-codex",
  "status": "busy",
  "load": "1/3",
  "capabilities": ["development", "git"],
  "availableProjects": ["company-knowledge-core"],
  "currentLeases": ["KT-20260623-001"],
  "agentSessions": ["session.company-knowledge-core.agent.company.development"],
  "lastErrorSummary": "",
  "deduplicationRef": "runner-heartbeat:runner.meimei-mbp-codex:20260623T101500Z"
}
```

状态枚举：

- `online`。
- `idle`。
- `busy`。
- `degraded`。
- `offline`。

中枢行为：

- 更新 AgentRunner `lastHeartbeatAt`、`status`、`load`。
- 合并 capabilities / availableProjects。
- 检测 heartbeat stale。
- 写 AuditLog：`runner.heartbeat`。
- 只把 heartbeat 摘要进 read model。

降级规则：

- 超过 2 个心跳周期：`degraded`。
- 超过 lease 过期时间：任务进入 stale lease recovery。
- 超过项目配置离线阈值：Runner 标记 `offline`。

## 11. 任务领取与租约

现有接口：

```txt
POST /v0/tasks/claim
POST /v0/tasks/pull
POST /v0/tasks/heartbeat
POST /v0/tasks/finish
```

领取请求：

```json
{
  "taskId": "KT-20260623-001",
  "runnerId": "runner.meimei-mbp-codex",
  "leaseSeconds": 900,
  "deduplicationRef": "task-claim:KT-20260623-001:runner.meimei-mbp-codex:attempt-1"
}
```

领取响应：

```json
{
  "apiVersion": "v0.1",
  "kind": "TaskClaimResult",
  "taskId": "KT-20260623-001",
  "runnerId": "runner.meimei-mbp-codex",
  "leaseAccessRef": "<shown once>",
  "leaseExpiresAt": "2026-06-23T10:30:00Z",
  "auditRef": "audit/audit.20260623.task-claim.md"
}
```

claim 校验：

- task 属于 Runner allowedProjects。
- Runner capability 覆盖 taskRuntime.requiredCapabilities。
- requiredTools 已注册并获批。
- dataScopes 与 repositoryScopes 覆盖任务范围。
- Runner 在线或最近 heartbeat 未 stale。
- 任务状态允许 `pending` / `waiting_runner` / stale reclaim。

pull 校验：

- runnerId 与 leaseOwner 一致。
- leaseAccessRef hash 匹配。
- lease 未过期。

finish 校验：

- runnerId 与 leaseOwner 一致。
- leaseAccessRef hash 匹配。
- TaskResult contract 通过。
- `operatingRuleRefs` 与 `commonRulesEvaluation` 必须存在。
- 知识产物走 Knowledge Review Agent gate。

工作台不能调用 claim/pull/finish。

## 12. 任务进展事件

新增接口：

```txt
POST /v0/task-events
GET  /v0/tasks/{taskId}/events
```

用途：

- Runner 在执行中上报阶段性进展。
- 中枢可在工作台展示，不把进展事件当作最终结果。
- 离线时 Runner 本地缓冲，恢复后按序补发。

事件请求：

```json
{
  "eventId": "evt.KT-20260623-001.runner.meimei-mbp-codex.000042",
  "taskId": "KT-20260623-001",
  "projectId": "company-knowledge-core",
  "runnerId": "runner.meimei-mbp-codex",
  "agentSessionId": "session.company-knowledge-core.agent.company.development",
  "leaseProof": "sha256:...",
  "eventType": "progress",
  "phase": "implementation",
  "status": "running",
  "percent": 55,
  "message": "已完成接口边界梳理，正在补审计与幂等方案。",
  "artifactRefs": [],
  "evidenceRefs": [],
  "sequence": 42,
  "occurredAt": "2026-06-23T10:18:00Z",
  "deduplicationRef": "task-event:KT-20260623-001:runner.meimei-mbp-codex:000042"
}
```

事件类型：

- `started`。
- `progress`。
- `checkpoint`。
- `tool_invocation_started`。
- `tool_invocation_finished`。
- `model_call_started`。
- `model_call_finished`。
- `blocked`。
- `error`。
- `recovered`。
- `result_submitted`。

写入规则：

- 每个事件生成或关联 AuditLog。
- 同一 `(taskId, runnerId, sequence)` 幂等。
- 同一 `eventId` 幂等。
- 事件只能 append，不能 update/delete。
- 错误事件可被后续 `recovered` 事件覆盖展示状态，但原始错误保留。

只读展示：

- 工作台展示最新 phase、最近 20 条事件、异常摘要、恢复建议。
- 工作台不把事件摘要写成 TaskResult。

## 13. 模型/token/tool 上报

新增接口：

```txt
POST /v0/runner-telemetry
GET  /v0/workbench/projects/{projectId}/telemetry-summary
```

请求字段：

```json
{
  "telemetryId": "tel.KT-20260623-001.runner.meimei-mbp-codex.000017",
  "projectId": "company-knowledge-core",
  "taskId": "KT-20260623-001",
  "runnerId": "runner.meimei-mbp-codex",
  "agentSessionId": "session.company-knowledge-core.agent.company.development",
  "leaseProof": "sha256:...",
  "modelUsage": [
    {
      "provider": "openai",
      "model": "gpt-5-codex",
      "inputUsageUnits": 12000,
      "outputUsageUnits": 1800,
      "cachedInputUsageUnits": 6000,
      "estimatedCost": null
    }
  ],
  "toolUsage": [
    {
      "toolId": "tool.local.git",
      "toolName": "git",
      "operation": "diff",
      "status": "success",
      "riskLevel": "local_repo_read",
      "durationMs": 320
    }
  ],
  "resourceUsage": {
    "durationMs": 95000,
    "retryCount": 0
  },
  "occurredAt": "2026-06-23T10:19:00Z",
  "deduplicationRef": "telemetry:KT-20260623-001:runner.meimei-mbp-codex:000017"
}
```

上报边界：

- 上报模型名、provider、token 计数、缓存计数、估算成本。
- 上报工具名、工具 ID、operation、状态、耗时、risk。
- 不上报 prompt 原文。
- 不上报模型响应原文，除非已经作为 evidence/artifact 受控存储。
- 不上报 secret、token、cookie、完整命令含密钥参数。
- 工具 stderr/stdout 只允许摘要或 artifactRef。

工作台展示：

- 按项目、任务、Runner、Agent session 聚合。
- 可查看异常工具调用和失败率。
- 可查看 token 趋势和单任务用量。
- 不展示密钥、不展示原始敏感日志。

## 14. Agent 会话状态

现有 core 已有 V1 AgentSession：

- `register_v1_agent_session`。
- `heartbeat_v1_agent_session`。
- `list_v1_agent_sessions`。
- `v1_workbench_read_model`。

Phase 2 沿用并扩展为多 Runner session：

接口：

```txt
POST /v0/agent-sessions/register
POST /v0/agent-sessions/heartbeat
GET  /v0/agent-sessions?projectId={projectId}
```

注册字段：

```json
{
  "sessionId": "session.company-knowledge-core.agent.company.development.runner.meimei-mbp-codex",
  "projectId": "company-knowledge-core",
  "agentId": "agent.company.development",
  "runnerId": "runner.meimei-mbp-codex",
  "deviceId": "device.meimei-mbp",
  "capabilities": ["development", "git"],
  "status": "idle",
  "deduplicationRef": "agent-session-register:session.company-knowledge-core.agent.company.development.runner.meimei-mbp-codex"
}
```

心跳字段：

```json
{
  "sessionId": "session.company-knowledge-core.agent.company.development.runner.meimei-mbp-codex",
  "status": "busy",
  "currentTaskId": "KT-20260623-001",
  "currentPhase": "implementation",
  "lastEventId": "evt.KT-20260623-001.runner.meimei-mbp-codex.000042",
  "deduplicationRef": "agent-session-heartbeat:session.company-knowledge-core.agent.company.development.runner.meimei-mbp-codex:20260623T101900Z"
}
```

状态枚举：

- `idle`。
- `busy`。
- `waiting_tool`。
- `waiting_model`。
- `blocked`。
- `degraded`。
- `offline`。

工作台监管：

- 展示 session -> runner -> task 映射。
- 展示当前 phase 和 heartbeat。
- 不允许从工作台直接改 session 状态。

## 15. 幂等模型

所有写接口必须带 `deduplicationRef`：

- 工作台创建项目。
- 工作台生成 RunnerInvitation。
- 工作台注册工具。
- 工作台提交工具注册申请。
- Runner register。
- Runner heartbeat。
- task claim。
- task pull。
- task heartbeat。
- task event append。
- runner telemetry append。
- Agent session register / heartbeat。
- task finish。

幂等存储：

- `CommandRecord` 或等价表。
- 字段：`commandId`、`route`、`actorRef`、`permissionDecision`、`deduplicationRef`、`requestHash`、`responseHash`、`auditRef`、`notificationRefs`、`status`、`createdAt`、`updatedAt`。

幂等规则：

- 相同 actor + route + deduplicationRef + requestHash：返回原 response。
- 相同 actor + route + deduplicationRef + 不同 requestHash：返回 conflict。
- append event 以 `eventId` 和 `sequence` 双重去重。
- task finish 以 `(taskId, runnerId, leaseProof, resultId)` 去重。
- heartbeat 幂等不生成过量 NotificationRecord，但可记录采样 AuditLog 或聚合审计。

现有可复用点：

- `normalize_command_envelope`。
- `WRITE_COMMAND_TYPES`。
- tests 中已有 `deduplicationRef` / CommandRecord 字段约束。

## 16. 离线恢复

Runner 本地维护：

- runner token。
- lease token，按 taskId 存本地安全状态。
- outbound event queue。
- outbound telemetry queue。
- last acknowledged sequence。
- task context cache。

离线行为：

1. Runner 继续本地执行，但每个事件写本地 queue。
2. task heartbeat 失败时，Runner 标记本地状态 `network_degraded`。
3. lease 未过期前恢复：补发事件、补发遥测、继续 heartbeat。
4. lease 已过期后恢复：先调用 reconcile。
5. 如果中枢已把任务释放给别人，Runner 不允许 finish，只能提交 `late_result_candidate` evidence 或人工恢复请求。

新增接口：

```txt
POST /v0/runners/reconcile
```

请求：

```json
{
  "runnerId": "runner.meimei-mbp-codex",
  "knownLeases": [
    {
      "taskId": "KT-20260623-001",
      "leaseProof": "sha256:...",
      "lastLocalSequence": 57
    }
  ],
  "lastHeartbeatAt": "2026-06-23T10:20:00Z",
  "deduplicationRef": "runner-reconcile:runner.meimei-mbp-codex:20260623T102500Z"
}
```

响应：

```json
{
  "kind": "RunnerReconcileResult",
  "actions": [
    {
      "taskId": "KT-20260623-001",
      "action": "resume",
      "acceptedFromSequence": 43
    }
  ]
}
```

恢复动作：

- `resume`：lease 仍有效或可续租。
- `reclaim_required`：需要重新 claim。
- `stop_and_discard`：任务已由其他 Runner 完成。
- `submit_late_evidence`：结果不能直接 finish，可作为 evidence 给 PM 判断。
- `manual_review_required`：出现冲突或重复执行风险。

审计：

- `runner.reconcile`。
- `task.lease.resume`。
- `task.lease.expired`。
- `task.late_result_candidate`。

## 17. 项目隔离

项目隔离规则：

- Runner 注册时声明 `availableProjects`。
- Task claim 必须校验 task.projectId 在 availableProjects 内。
- repositoryScopes 必须覆盖任务 repositoryRefs。
- dataScopes 必须覆盖 taskRuntime.dataScopes。
- requiredTools 必须是项目批准工具。
- Agent session projectId 必须与 task.projectId 一致。
- Workbench read model 必须按项目过滤。
- 工作台入口写入必须带 projectId。

跨项目禁止：

- Runner A 持有 Project X token，不能 claim Project Y 任务。
- Project X 工具批准不能默认用于 Project Y。
- Project X 进展事件不能出现在 Project Y read model。
- 工作台用户有 Project X 权限，不代表有 Project Y 管理权限。

审计字段必须包含：

- actorRef。
- projectRef / projectId。
- targetRef。
- route。
- permissionDecision。
- policyResult。
- requestHash。
- responseHash。

## 18. 权限与审批

### 18.1 权限点

| 权限 | 用途 |
| --- | --- |
| `project.create` | 工作台创建项目 |
| `project.repository.attach` | 项目绑定 repo |
| `runner.invitation.create` | 生成电脑接入邀请 |
| `runner.register` | Runner 使用 pairingCode 注册 |
| `runner.heartbeat` | Runner 心跳 |
| `task.claim` | Runner 领取任务 |
| `task.pull` | Runner 拉取 context |
| `task.event.append` | Runner 上报进展 |
| `runner.telemetry.append` | Runner 上报模型/tool/token 摘要 |
| `task.finish` | Runner 写 TaskResult / AgentRun |
| `tool.register.low_risk` | 工作台注册低风险工具 |
| `tool.registration.request` | 工作台提交工具申请 |
| `tool.approve` | Tool Owner 审批 |
| `workbench.execution.read` | 工作台监管只读 |

### 18.2 审批路径

需要审批：

- 工具有写权限。
- 工具需要 secret。
- 工具会访问客户数据。
- 工具影响权限、安全、生产环境、客户承诺。
- Runner requestedCapabilities 包含敏感能力。
- Runner dataScopes 超过项目默认 scope。
- 项目创建带外部副作用，如建 repo、邀人、改权限。

不需要审批：

- 本地低风险只读工具注册。
- 创建不含外部副作用的项目草稿。
- 生成低风险、短期、项目内 Runner pairing code。
- Runner 心跳、进展事件、遥测上报。

审批输出：

- approved：更新 ToolAsset / Runner scope。
- rejected：保持申请记录，不启用。
- changes_requested：创建修复任务或退回申请人。

## 19. 审计模型

所有写入都要 AuditLog。

审计 action 建议：

- `workbench.project.create`。
- `workbench.runner_invitation.create`。
- `workbench.tool.register`。
- `workbench.tool_registration_request.create`。
- `runner.pairing.consume`。
- `runner.register`。
- `runner.upsert`。
- `runner.heartbeat`。
- `task.claim`。
- `task.pull`。
- `task.heartbeat`。
- `task.event.append`。
- `runner.telemetry.append`。
- `agent_session.register`。
- `agent_session.heartbeat`。
- `task.finish`。
- `task.lease.stale`。
- `task.lease.reclaim`。
- `runner.reconcile`。
- `tool.approve`。
- `tool.reject`。

审计可读性：

- `summary` 写人可读解释。
- `details` 写结构化摘要，不含 secret。
- token 只写 hash/proof。
- 错误审计要写下一步建议。

## 20. 安全边界

禁止：

- 工作台直接派单。
- 工作台直接修改 TaskResult。
- 工作台直接修改 AgentRun。
- 工作台用用户 token 代替 Runner token 执行任务。
- Runner 使用过期 lease 写 finish。
- 任意 API 返回 secret/token 明文。
- 工具注册时保存 token/key/password。
- 进展事件包含 prompt 原文或敏感日志。

允许：

- 工作台创建任务或请求，让 Scheduler 后续调度。
- 工作台提交 retry/recovery request，让 PM/Scheduler/Runner 处理。
- Runner 上报本地工具/模型使用摘要。
- Runner 提交 evidence/artifact refs。
- 中枢将异常、审计、状态聚合到 read model。

密钥处理：

- 中枢不保存 secret values。
- ToolAsset 只保存 secretRef / secureStorageRule。
- Runner 本地工具凭据由本机 secret store 或外部 vault 管理。
- API 日志必须做 token redaction。

## 21. 数据对象建议

复用对象：

- AgentRunner。
- ProjectTask / KnowledgeTask。
- TaskResult。
- AgentRun。
- ToolAsset。
- NotificationRecord。
- AuditLog。
- AgentSession。

新增或一等化对象：

- RunnerInvitation。
- RunnerTokenRecord。
- TaskProgressEvent。
- RunnerTelemetryEvent。
- ToolRegistrationRequest。
- CommandRecord。
- RunnerReconcileRecord。

TaskProgressEvent 必备字段：

- eventId。
- projectId。
- taskId。
- runnerId。
- agentSessionId。
- leaseProof。
- eventType。
- phase。
- status。
- sequence。
- message。
- artifactRefs。
- evidenceRefs。
- occurredAt。
- deduplicationRef。

RunnerTelemetryEvent 必备字段：

- telemetryId。
- projectId。
- taskId。
- runnerId。
- agentSessionId。
- leaseProof。
- modelUsage。
- toolUsage。
- resourceUsage。
- occurredAt。
- deduplicationRef。

## 22. 现有 CLI/core 可复用点

### 22.1 core 可复用

已存在并可直接复用或扩展：

- `register_agent_runner`：创建/更新 AgentRunner，写 runner.register / runner.upsert 审计。
- `heartbeat_agent_runner`：更新 Runner 状态、load、capabilities、availableProjects，写 runner.heartbeat 审计。
- `schedule_project_tasks`：调度候选、claim 流程入口。
- `pull_project_task`：校验 lease，生成 context pack，写 task.pull 审计。
- `finish_project_task`：校验 lease，写 TaskResult，评估质量、acceptancePolicy、commonRulesEvaluation，写通知和审计。
- `register_v1_agent_session`：AgentSession 注册。
- `heartbeat_v1_agent_session`：AgentSession 心跳。
- `list_v1_agent_sessions`：按项目读取 session。
- `scheduler_workbench_read_model`：聚合 task queue、Runner registry、lease、audit、metrics。
- `v1_workbench_read_model`：聚合 device/session/task/result/runtime 面板。
- `create_audit_log`：统一审计。
- `normalize_command_envelope`：命令幂等和写命令约束基础。
- `secret_fingerprint` / `leaseAccessRefHash` / `leaseProofHash`：token proof 处理基础。
- `repair_stale_task_leases`：stale lease 修复基础。

### 22.2 CLI 可复用

已存在并可承接：

- `zhenzhi-knowledge runner register`。
- `zhenzhi-knowledge runner heartbeat`。
- `zhenzhi-knowledge runner list`。
- `zhenzhi-knowledge scheduler workbench`。
- `zhenzhi-knowledge v1 session register`。
- `zhenzhi-knowledge v1 session heartbeat`。
- `zhenzhi-knowledge v1 session list`。
- `zhenzhi-knowledge v1 workbench export`。
- `zhenzhi-knowledge start` / `finish` 本地 Agent 工作闭环。
- `api_request` / `use_api_backend` 支持远端 API backend。

需要新增 CLI：

- `zhenzhi-knowledge runner pair`：输入 pairingCode，完成 register/token 保存。
- `zhenzhi-knowledge runner daemon`：周期 heartbeat、event flush、telemetry flush、reconcile。
- `zhenzhi-knowledge runner event append`：本地任务进展事件。
- `zhenzhi-knowledge runner telemetry append`：模型/token/tool 摘要。
- `zhenzhi-knowledge runner reconcile`：离线恢复。
- `zhenzhi-knowledge workbench project create`：工作台或命令行创建项目。
- `zhenzhi-knowledge workbench runner invite`：生成接入邀请。
- `zhenzhi-knowledge workbench tool register`：低风险工具注册。
- `zhenzhi-knowledge workbench tool request`：高风险工具注册申请。

### 22.3 Harness 可复用

`scripts/distributed_runner_proof_harness.py` 已覆盖：

- `runner_register`。
- `runner_heartbeat`。
- `runner_list`。
- `task_claim`。
- `task_pull`。
- `task_heartbeat`。
- `task_finish`。
- `stale_lease_reclaim`。
- `runner_isolation_rejected`。

Phase 2 需要扩展 harness：

- `workbench_project_create`。
- `workbench_runner_invitation_create`。
- `workbench_tool_register`。
- `workbench_tool_registration_request_create`。
- `task_event_append`。
- `runner_telemetry_append`。
- `agent_session_register`。
- `agent_session_heartbeat`。
- `runner_reconcile`。
- `workbench_execution_read_model`。
- `workbench_forbidden_dispatch_rejected`。
- `workbench_forbidden_result_mutation_rejected`。

## 23. API 清单

### 23.1 工作台入口写 API

| Method | Path | 作用 | 写入对象 |
| --- | --- | --- | --- |
| POST | `/v0/workbench/projects` | 创建项目 | Project, ProjectTask, AuditLog |
| POST | `/v0/workbench/runner-invitations` | 生成电脑接入邀请/配对码 | RunnerInvitation, AuditLog |
| POST | `/v0/workbench/tools` | 注册低风险工具 | ToolAsset, AuditLog |
| POST | `/v0/workbench/tool-registration-requests` | 提交工具注册申请 | ToolRegistrationRequest, ProjectTask, NotificationRecord, AuditLog |

### 23.2 工作台监管只读 API

| Method | Path | 作用 |
| --- | --- | --- |
| GET | `/v0/workbench/projects/{projectId}/execution-read-model` | 执行监管聚合 |
| GET | `/v0/scheduler/workbench?projectId={projectId}` | 调度监管聚合 |
| GET | `/v0/workbench/projects/{projectId}/telemetry-summary` | 模型/token/tool 摘要 |
| GET | `/v0/tasks/{taskId}/events` | 任务事件流 |
| GET | `/v0/agent-sessions?projectId={projectId}` | Agent session 列表 |
| GET | `/v0/audit?projectId={projectId}` | 审计查询 |

### 23.3 Runner 写 API

| Method | Path | 作用 |
| --- | --- | --- |
| POST | `/v0/runners/register` | Runner 注册 |
| POST | `/v0/runners/heartbeat` | Runner 心跳 |
| POST | `/v0/tasks/claim` | 领取任务 lease |
| POST | `/v0/tasks/pull` | 拉取 context |
| POST | `/v0/tasks/heartbeat` | 延续任务 lease |
| POST | `/v0/task-events` | 追加任务进展事件 |
| POST | `/v0/runner-telemetry` | 追加模型/token/tool 上报 |
| POST | `/v0/agent-sessions/register` | Agent session 注册 |
| POST | `/v0/agent-sessions/heartbeat` | Agent session 心跳 |
| POST | `/v0/tasks/finish` | 写 TaskResult / AgentRun |
| POST | `/v0/runners/reconcile` | 离线恢复对账 |

## 24. 状态机

任务状态沿用：

```txt
pending
-> waiting_runner
-> claimed
-> processing
-> waiting_acceptance
-> done
```

旁路状态：

```txt
manual_handoff
approval_relay_requested
repair_pending
changes_requested
blocked
rejected
cancelled
```

Runner 状态：

```txt
online -> idle -> busy -> idle
online/busy -> degraded -> offline
offline -> online -> reconcile
```

Agent session 状态：

```txt
idle -> busy -> waiting_tool/waiting_model -> busy -> idle
busy -> blocked
busy -> degraded -> offline
offline -> recovered/reconcile
```

## 25. 验收标准

必须通过：

1. 工作台创建项目成功，生成 Project、AuditLog、可读通知或返回。
2. 工作台生成 Runner 配对码，配对码只显示一次，中枢只存 hash。
3. Runner 使用配对码注册成功，获得 runnerAccessRef，AgentRunner 可在 registry 查询。
4. Runner 心跳更新 lastHeartbeatAt、status、load。
5. Runner claim 后获得 leaseAccessRef，中枢只存 leaseProofHash。
6. Runner pull 必须带正确 leaseAccessRef。
7. Runner progress event 可 append，重复 event 幂等。
8. Runner telemetry 可 append，不含 prompt、secret、明文 token。
9. Agent session register / heartbeat 可在 read model 展示。
10. 离线后 Runner 可 reconcile；lease 过期时不能直接 finish。
11. 项目隔离拒绝跨项目 claim、event、telemetry、finish。
12. 工作台可读监管展示任务、进展、模型/token/tool/Agent 状态和异常。
13. 工作台不能直接派单、修复、篡改 TaskResult 或 AgentRun。
14. 工具低风险注册可直接写 ToolAsset；高风险工具生成审批申请。
15. 所有写入有 AuditLog，审计不含 secret。
16. 现有 distributed runner harness 扩展后覆盖双 Runner、多项目隔离、stale lease、工作台禁写执行面。

## 26. 实施顺序

1. 补工作台入口 API：project create、runner invitation、tool register、tool request。
2. 补权限和 CommandRecord 幂等层。
3. 扩展 Runner register：pairingCode、runnerAccessRef、models/tools 摘要。
4. 增加 task progress event append。
5. 增加 runner telemetry append。
6. 扩展 AgentSession 到 runner-aware。
7. 增加 runner reconcile。
8. 扩展 workbench execution read model。
9. 扩展 distributed runner proof harness。
10. 对接已部署 `http://124.221.138.151/knowledge-api` 做真实 API 路径验证。

## 27. 风险与处理

| 风险 | 处理 |
| --- | --- |
| 工作台入口被误用成执行控制台 | API 分命名空间，执行写接口不接受 workbench actor |
| 配对码泄漏 | 短期、一次性、scope 限制、只换 bootstrap token |
| Runner token 泄漏 | token hash 存储、可撤销、按项目 scope、审计异常 |
| 离线 Runner 晚提交覆盖结果 | finish 强制 lease 校验，late result 只能进 evidence |
| 遥测泄漏敏感内容 | schema 禁止 prompt/secret/raw log，服务端 redaction |
| 工具注册绕过审批 | riskLevel + requestedOperations 决定 ToolAsset 直写或审批申请 |
| 跨项目数据污染 | 所有查询与写入强制 projectId + scope 校验 |
| 幂等冲突导致重复任务或重复事件 | CommandRecord + eventId/sequence 去重 |

## 28. 最终边界

工作台是项目入口和监管台，不是执行器。

可操作：

- 创建项目。
- 发起电脑接入。
- 注册低风险工具。
- 提交高风险工具注册申请。
- 提交验收/审批类人类决策。

只读监管：

- 任务执行状态。
- Runner lease。
- 任务进展事件。
- 模型/token/tool 用量。
- Agent session 状态。
- 异常和恢复状态。
- 审计和通知。

禁止：

- 直接派单。
- 直接抢 lease。
- 直接修复任务。
- 直接篡改 TaskResult。
- 直接篡改 AgentRun。
- 绕过工具审批。

这个边界保证 Phase 2 多设备 Runner 能在同一中枢下协作，同时保留中心事实、审计、审批和项目隔离。
