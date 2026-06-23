---
type: Workflow
title: 阶段二多设备 Runner 协作闭环技术方案
description: 同事电脑接入同一项目中枢、多设备 Runner 路由、租约、结果写回和工作台读模型技术方案。
timestamp: "2026-06-22T12:06:19Z"
projectId: company-knowledge-core
taskId: kt-v2-colleague-runner-architecture-solution
ownerAgent: agent.company.architecture
status: draft
phase: phase-2
sourceMaterialRefs:
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator-orchestrator.md
  - docs/product/ai-native-os/phase-2-multi-device-runner-collaboration-prd.md
  - projects/company-knowledge-core/design/phase2-multi-device-runner-workbench-design.md
  - projects/company-knowledge-core/desktop-workbench-slice0/index.md
  - projects/company-knowledge-core/desktop-workbench-slice0/shared-frontend-foundation.ts
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js
  - docs/scheduler/task-dispatch-model.md
  - docs/harness/agent-ring-distributed-runner-proof-harness.md
  - projects/company-knowledge-core/technical-solutions/ai-native-os-scheduler-runner-result.md
relatedImplementationRefs:
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/server.py
  - scripts/distributed_runner_proof_harness.py
reviewPath:
  - Product Manager Agent architecture review
  - Project Manager Agent delivery acceptance
  - Development Agent implementation handoff after product acceptance
  - Test Agent multi-device evidence gate
updatedAt: "2026-06-22T12:06:19Z"
---

# 阶段二多设备 Runner 协作闭环技术方案

## 1. 结论

阶段二在现有 V1 单机闭环上增加“同事电脑接入同一项目中枢”的中枢契约，不把 Agent Ring 内部实现合并进本仓库。Core 继续只负责项目事实、设备/Runner 注册、授权、调度、租约、上下文裁剪、结果写回、通知和审计；Agent Ring 和本地 Codex/Claude/模型/工具继续负责真实执行。

最小可交付切片：

```txt
项目 Owner 邀请同事
-> 同事设备注册 Device
-> 设备上的执行面注册 Runner
-> 项目侧配对授权
-> Scheduler 只把任务路由给合格在线 Runner
-> Runner 领取任务租约并拉取裁剪后的上下文
-> Runner 本地执行并持续心跳
-> Runner 写回 TaskResult + AgentRun + 证据
-> 中枢生成 NotificationRecord + AuditLog
-> 工作台用中文展示协作设备、任务路由、阻塞和下一步
```

本方案引用并遵守 `projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator-orchestrator.md`：阶段二必须分离产品、设计、架构、研发、测试和 PM 结论；主工作台必须用户可读；TaskResult 必须记录该技能引用或证据说明。

## 2. 现有基线

已存在可复用基线：

- `docs/scheduler/task-dispatch-model.md` 定义 Scheduler 只分派、不执行；短期以 Runner 拉取匹配为主，中期支持中心主动分配。
- `projects/company-knowledge-core/technical-solutions/ai-native-os-scheduler-runner-result.md` 已定义 `taskRuntime`、`AgentRunner`、租约字段和 TaskResult 验收规则。
- `zhenzhi_knowledge/core.py` 已有 `register_agent_runner`、`runner_can_schedule_task`、`select_runner_for_task`、`claim_project_task`、`heartbeat_project_task_lease`、`project_task_context_payload`、`finish_project_task`。
- `zhenzhi_knowledge/server.py` 已暴露 `/v0/runners/register`、`/v0/runners/heartbeat`、`/v0/tasks/claim`、`/v0/tasks/heartbeat`、`/v0/tasks/pull`、`/v0/tasks/finish` 等 Agent Ring stub API。
- `scripts/distributed_runner_proof_harness.py` 已定义真实双 Runner 证据契约，要求两个不同 host 产生注册、心跳、领取、拉取、写回、取消、重试、交接、超时恢复和隔离拒绝证据。
- V1 工作台 `desktop-workbench-slice0` 已有 `RunnerLeaseState`、`DesktopWorkbenchReadModel`、只读降级、Runner 配对诊断和“桌面不能直接改租约/TaskResult/AgentRun”的桥接边界。

阶段二要扩展上述基线，而不是重做 V1 单机页面或直接实现 Agent Ring 产品。

## 3. 架构边界

### 3.1 Core owns

- Shared Project Center：项目、任务、SourceMaterial、TaskResult、AgentRun、NotificationRecord、AuditLog、Decision、Policy、Runner/Device 读写事实。
- Scheduler：任务归一化、Runner 匹配、路由解释、租约发放、心跳判断、超时恢复、转派、暂停和禁用。
- Permission Gate：项目范围、角色范围、仓库范围、工具范围、数据范围、审批状态、secret readiness。
- Context Pack：按授权范围生成本次任务上下文，不包含越权材料或密钥。
- Result Center：验证 TaskResult、AgentRun、证据、测试/检查、质量评价和验收路径。
- Workbench Read Model：给桌面/Web 控制台提供用户可读状态，不把 raw internal fields 放到主信息。

### 3.2 Core does not own

- Agent Ring 内部进程管理、模型执行、远程桌面、公网穿透、大规模集群调度。
- 同事电脑上的源码、密钥、原始本地日志和未注册工具。
- 越权材料读取、密钥值保存、未审核知识发布。
- 研发实现结论、测试通过结论、产品验收结论；这些必须分别由对应岗位 TaskResult 产生。

## 4. 共享项目中枢

共享项目中枢是所有设备和 Runner 的唯一事实源。中枢按项目提供四类写入面：

| 面 | 写入对象 | 规则 |
| --- | --- | --- |
| 协作准入 | Device、AgentRunner、PairingRequest、AuthorizationGrant | 未授权不可领取任务。 |
| 调度执行 | ProjectTask/KnowledgeTask、RoutingDecision、Lease | 单任务单有效租约，所有状态变化写审计。 |
| 上下文与结果 | ContextPackRef、TaskResult、AgentRun、EvidenceRef | 本地文件不是最终状态，写回中枢才可验收。 |
| 用户可见状态 | NotificationRecord、WorkbenchReadModel、AuditLog | 主信息中文可读，技术字段进入折叠证据层。 |

建议新增逻辑对象，不必第一阶段都落成独立文件类型；可以先作为 API/read-model 子对象实现，后续再实体化：

- `DeviceRegistration`：一台同事电脑的身份、Owner、显示名、平台、项目接入状态。
- `RunnerAuthorization`：某个 Runner 在某项目内可执行的 Agent、任务类型、仓库、工具和资料范围。
- `PairingRequest`：邀请、配对、审批、过期、撤销证据。
- `RoutingDecision`：任务为什么分给某台设备，为什么拒绝其他设备。

## 5. 设备注册模型

设备代表“同事电脑”，Runner 代表“这台电脑上的执行面”。一台设备可以有多个 Runner，例如本地 Codex Runner、Claude Runner、测试 Runner；Runner 不能脱离 Device 和项目授权独立接单。

### 5.1 DeviceRegistration 字段

| 字段 | 说明 | 主 UI 是否显示 |
| --- | --- | --- |
| `deviceId` | 中枢内部设备引用 | 否，仅技术详情。 |
| `projectId` | 绑定项目 | 显示项目中文名，不显示内部路径。 |
| `ownerRef` | 同事或管理员 | 显示中文姓名/团队。 |
| `displayName` | 电脑可读名称 | 是，例如“张三的 MacBook Pro”。 |
| `platform` | macOS/Windows/Linux | 可作为辅助信息。 |
| `deviceTrustState` | pending/authorized/revoked/expired | 主 UI 映射为“等待确认/已加入/已撤销/授权已过期”。 |
| `lastSeenAt` | 最近在线 | 显示“刚刚/10 分钟前”。 |
| `pairingRef` | 配对记录 | 只在证据入口显示。 |
| `riskFlags` | 权限、网络、版本风险 | 显示中文风险标签。 |

### 5.2 注册流程

```txt
Owner 生成邀请
-> 中枢创建 PairingRequest，设置项目、有效期、允许工作类型和审批人
-> 同事电脑打开邀请并提交 DeviceRegistration
-> 设备进入“等待确认”
-> Owner/管理员确认授权范围
-> 中枢创建 RunnerAuthorization
-> 设备进入“已加入项目”，Runner 才能注册为可调度
```

注册必须写 AuditLog：邀请创建、邀请撤销、设备申请、授权确认、授权拒绝、授权过期、设备禁用。

## 6. Runner 注册模型

现有 `AgentRunner` 已覆盖 `runnerId`、`machineId`、`hostType`、`status`、`agents`、`capabilities`、`availableProjects`、`repoAccess`、`dataScopes`、`load`、`lastHeartbeatAt`。阶段二扩展时保持兼容：

| 字段 | 阶段二要求 |
| --- | --- |
| `deviceId` | 绑定 DeviceRegistration；缺失时只能作为 V1/manual Runner。 |
| `displayName` | 从设备名 + 执行面生成，例如“张三的 Mac - Codex 执行器”。 |
| `ownerRef` | 同事或团队 Owner。 |
| `authorizationRefs` | 指向项目内 RunnerAuthorization。 |
| `toolScopes` | 已批准工具列表或工具类别。 |
| `repositoryScopes` | 仓库读/写/测试范围，显示时映射为业务名称。 |
| `dataScopes` | 可读资料范围，不能包含密钥值。 |
| `runnerVersion` | Agent Ring stub 或本地 runner 版本。 |
| `heartbeatSummary` | 在线、降级、离线的用户可读摘要。 |
| `currentLeases` | 当前任务占用摘要。 |

Runner 注册 API 短期继续使用 `/v0/runners/register`，新增字段必须向后兼容。未授权 Runner 可以注册为 `pending_authorization` 或 `online_not_schedulable`，但 `runner_can_schedule_task` 必须拒绝它领取任务。

## 7. 配对与授权

配对不是直接授予任务执行权。配对只证明“这台电脑由这个用户确认加入这个项目”；授权才决定“这台电脑上的 Runner 能执行哪些工作”。

### 7.1 PairingRequest

状态机：

```txt
draft
-> invited
-> accepted_by_device
-> pending_project_confirmation
-> authorized
-> expired
-> revoked
-> rejected
```

关键安全规则：

- 邀请 token 或 pairing proof 只返回一次，持久记录只保存 hash/proof ref。
- 邀请默认 24 小时，可选 1 小时、24 小时、7 天。
- 设备提交配对后仍需项目侧确认，不自动接任务。
- 任何撤销、过期、拒绝立即让关联 Runner 停止接新任务。
- 正在执行的租约可按策略暂停、续租到完成、转派或取消；必须写审计和通知。

### 7.2 RunnerAuthorization

授权拆分为六个维度：

- `projectScope`：当前项目或指定任务。
- `roleScope`：设计、开发、测试、资料整理、项目管理等业务角色。
- `capabilityScope`：对应 requiredCapabilities。
- `toolScope`：允许调用的已注册 ToolAsset。
- `repositoryScope`：仓库读、写、测试、分支或工作区范围。
- `dataScope`：可读 SourceMaterial/KnowledgeItem/上下文范围。

权限策略：

- 默认最小权限。
- 能力与权限分离：有 `development` capability 不代表有代码仓库权限。
- 高风险工具、权限、安全、客户承诺仍需人审。
- secret 值不进入 Runner、TaskResult、AgentRun、ContextPack 或工作台。

## 8. 任务路由策略

Scheduler 采用“过滤 -> 排序 -> 解释 -> 发放租约”。

### 8.1 硬过滤

Runner 必须同时满足：

- Device 已授权且未撤销、未过期。
- Runner 状态为 online/idle/busy 且心跳未过期。
- `availableProjects` 包含当前项目。
- `agents`/`agentIds` 与任务 `assignee`、`executorAgent`、`requiredAgents` 不冲突。
- `capabilities` 满足 `taskRuntime.requiredCapabilities`。
- `toolScopes` 满足 `requiredTools`。
- `repositoryScopes` 覆盖 `repositoryRefs`。
- `dataScopes` 覆盖任务所需 SourceMaterial/Knowledge scope。
- 所需 credential readiness 和 environment readiness 已满足。
- 未被暂停、禁用或处于 draining 且禁止新任务。

不满足时不得发放租约。拒绝原因必须写入 `RoutingDecision`、AuditLog 和用户可读提示。

### 8.2 排序

候选 Runner 排序建议：

1. 显式 preferredRunner 或人工指定。
2. 精确匹配任务 Agent/角色。
3. 能力覆盖最小但足够，避免把高权限 Runner 用在低权限任务。
4. 当前负载低。
5. 同项目近期成功率高。
6. 心跳最新。
7. leaseAttempt 少，避免反复失败设备。

排序输出不直接显示内部分数，工作台显示三行解释：

- 分配给谁：同事电脑中文名。
- 为什么分配：具备对应工作类型、项目授权、当前空闲。
- 当前卡点：无卡点/等待授权/设备离线/结果待回传。

### 8.3 无候选 Runner

任务进入 `waiting_runner`，同时生成：

- 用户可读原因：例如“当前没有能处理开发任务且有代码仓库权限的同事电脑”。
- 下一步动作：邀请同事、补充授权、换任务类型、手动处理。
- NotificationRecord 给项目经理 Agent 或 Owner。
- AuditLog 记录调度判断和缺失条件。

## 9. 租约、心跳与结果写回

### 9.1 租约不变量

延续现有 `claim_project_task` 规则：

- 同一任务同一时间最多一个有效租约。
- 租约 token 只返回给领取 Runner；中枢只保存 hash。
- `heartbeat`、`pull`、`finish` 必须校验 `runnerId + leaseToken`。
- 非租约 Owner 写回必须拒绝并审计。
- 过期租约不能 finish。
- 转派或重试必须递增 `leaseAttempt` 和 task version。

### 9.2 状态映射

内部任务状态保持现有任务路由状态，工作台映射为用户语义：

| 内部状态/事件 | 工作台状态 | 用户说明 |
| --- | --- | --- |
| pending / waiting_runner | 待分配 | 正在匹配可执行同事电脑。 |
| processing + fresh lease | 执行中 | 某台同事电脑正在处理。 |
| processing + stale lease | 需人工处理 | 设备可能离线，任务需要恢复。 |
| blocked + approvalRequest | 等待授权 | 需要审批或补充权限。 |
| writeback retry | 等待回传 | 结果和证据正在同步。 |
| waiting_acceptance | 待验收 | 结果已写回，等待复核。 |
| done | 已完成 | 结果已验收或关闭。 |
| rejected / changes_requested | 需修改 | 结果未通过，需要返工。 |

### 9.3 心跳

两层心跳：

- Runner heartbeat：设备/执行面在线、负载、版本、最近错误、可用项目和能力。
- Task lease heartbeat：某个任务租约仍被 Runner 持有并继续执行。

默认过期阈值沿用现有 30 分钟；阶段二建议按任务风险和执行类型配置：

- 普通文档/设计/产品任务：10-30 分钟。
- 长跑测试或构建：5-10 分钟心跳，租约可续到更长。
- 高风险权限/工具任务：更短心跳，离线立即转人工确认。

### 9.4 结果写回

`/v0/tasks/finish` 必须写回：

- `TaskResult`：summary、outputRefs、evidenceRefs、testsOrChecks、operatingRuleRefs、commonRulesEvaluation、qualityEvaluation、acceptancePolicy、handoffContract 或 terminalReason。
- `AgentRun`：runId、projectId、agentId、task、contextRefs、toolsUsed、knowledgeUsed、outputRefs、codeRefs、humanReview、result、lessons。
- `NotificationRecord`：结果提交、待验收、阻塞、转派或失败。
- `AuditLog`：claim、pull、heartbeat、finish、拒绝、取消、重试、交接、转派。

写回失败不等于任务失败。Runner 应本地保留可重试 writeback envelope，只存结果摘要、证据引用和 token hash，不保存 secret。中枢显示“结果暂未同步完成”，允许重试同步或人工接管。

## 10. 上下文包裁剪

Context Pack 是 Runner 执行的边界，不是全项目导出。

必须包含：

- 任务卡、`taskRuntime`、验收路径、完成标准。
- 公司宪法、任务运行契约、人类验收策略、公共规则、岗位规则、项目规则。
- 本次任务需要的 PRD、设计、技术方案、SourceMaterial、代码引用或测试要求。
- 允许工具、允许仓库、允许数据范围。
- TaskResult 写回契约、审计/通知要求。

必须排除：

- 未授权项目资料。
- 未授权仓库或本地路径。
- secret 值、token、密码。
- 与任务无关的 raw logs、聊天记录、截图和临时文件。

上下文拉取失败进入可恢复状态：

| 原因 | 状态 | 下一步 |
| --- | --- | --- |
| 权限不足 | blocked / needs_approval | 发起授权或换 Runner。 |
| 资料不存在 | blocked | 让 PM 或资料 Owner 补齐 SourceMaterial。 |
| secret readiness 缺失 | blocked | 请求 credential ready，不暴露值。 |
| API 不可达 | safe fallback | 保持租约，提示重试或转人工。 |

## 11. 异常恢复

### 11.1 状态机

```txt
waiting_runner
-> processing
-> waiting_acceptance
-> done

processing -> stale_lease -> recovery_pending -> waiting_runner | processing | cancelled
processing -> runner_offline -> recovery_pending
processing -> writeback_failed -> waiting_writeback -> waiting_acceptance
processing -> needs_approval -> blocked
blocked -> pending | waiting_runner after approval
changes_requested -> pending | waiting_runner after repair task
```

### 11.2 处理策略

| 异常 | 中枢动作 | 用户可读说明 |
| --- | --- | --- |
| Runner 离线 | 标记设备离线，任务进入恢复队列，通知 PM。 | “同事电脑暂时离线，可等待恢复或转交。” |
| 租约超时 | 禁止原租约 finish，允许重新领取或人工取消。 | “任务占用已过期，需要恢复处理。” |
| 双领取冲突 | 第二个 claim 拒绝，记录冲突审计。 | “任务已分配给另一台设备。” |
| 越权拉取 | 拒绝 Context Pack，审计 scope mismatch。 | “这台电脑缺少必要授权。” |
| 工具缺失 | 阻塞或换 Runner。 | “这台电脑没有可用的批准工具。” |
| 写回失败 | 保持待回传，可重试同步。 | “结果暂未同步完成。” |
| 审批等待 | 创建 approvalRequest，停止执行或限制只读。 | “需要审批人确认后继续。” |
| Runner 禁用 | 阻止新任务，处理已有租约。 | “这台设备已暂停接单。” |

## 12. 工作台信息模型

V1 的 `DesktopWorkbenchReadModel` 保留，阶段二新增协作设备视图，建议 schema 升级为 `desktop-workbench-read-model.v2`，同时兼容 v1 字段。

### 12.1 新增 read model

```txt
CollaborationWorkbenchReadModel
  schemaVersion
  project
  generatedAt
  staleStatePolicy
  collaborationSummary
  devices[]
  runners[]
  pairingRequests[]
  authorizations[]
  routeBoard[]
  recoveryItems[]
  notifications[]
  evidencePanels[]
  permissionGatedActions[]
  technicalDetails[]
```

### 12.2 devices[]

| 字段 | 说明 |
| --- | --- |
| `displayName` | “张三的 MacBook Pro”。 |
| `ownerLabel` | “张三”。 |
| `availabilityLabel` | 可接任务、正在执行、等待授权、离线、需处理。 |
| `workTypeLabels` | 设计、开发、测试、资料整理。 |
| `authorizationSummary` | 当前项目、指定任务、只读资料、不可访问代码。 |
| `currentTaskLabel` | 任务标题或“暂无任务”。 |
| `lastSeenLabel` | 刚刚、10 分钟前。 |
| `riskLabels` | 权限不足、授权将过期、只读。 |
| `primaryAction` | 查看、确认授权、转交、暂停接单。 |
| `technicalRef` | 折叠区内部引用。 |

### 12.3 routeBoard[]

| 字段 | 说明 |
| --- | --- |
| `taskLabel` | 任务标题。 |
| `businessStatus` | 待分配、等待授权、执行中、等待回传、需人工处理、待验收、已完成。 |
| `assignedDeviceLabel` | 同事电脑中文名。 |
| `routeReason` | 具备工作类型、项目授权、空闲。 |
| `blockerLabel` | 无卡点、等待授权、设备离线、结果待回传。 |
| `nextOwnerLabel` | 下一步责任人。 |
| `nextAction` | 邀请同事、补充授权、转交任务、查看证据。 |
| `evidenceRefs` | 可读证据入口。 |

### 12.4 permissionGatedActions[]

所有写动作都必须有：

- 中文按钮名。
- 服务端权限 gate。
- idempotencyKey。
- 审计目标。
- 禁用原因中文文案。

## 13. 用户可读 UI 约束

研发实现必须把技术对象翻译为业务语言：

| 技术对象 | 主 UI 中文 |
| --- | --- |
| Runner | 协作设备 / 执行器 |
| Agent Ring | 执行网络 |
| Lease | 任务占用 |
| Claim | 任务已分配 |
| Heartbeat | 在线状态 |
| Capability | 可做工作 |
| Scope | 授权范围 |
| AuditLog | 操作记录 |
| TaskResult | 结果与证据 |

禁止作为主信息显示：

- `runnerId`、`deviceId`、`sessionId`、`leaseId`、`claimId`。
- capability code、raw status、runtimeMetrics。
- 本地文件路径、API endpoint、错误堆栈。
- token、secret、密码。

如果缺少可读名称，显示“未命名的同事电脑”，并提示补充名称。不能回退显示 `runner-xxx`。

主界面必须覆盖：

- 空状态：“还没有同事电脑加入这个项目” + “邀请同事”。
- 加载：“正在读取项目协作设备”。
- 失败：“暂时无法更新设备状态” + “重试”。
- 只读降级：“当前为只读模式，只展示最近一次同步结果”。
- 禁用按钮原因：“无权限邀请同事”“只读模式下不能暂停设备”。

## 14. API/Gateway 切片建议

保留现有 v0 Agent Ring API，新增或扩展以下能力：

| API | 目的 |
| --- | --- |
| `POST /v0/devices/pairing/invite` | 创建邀请和 PairingRequest。 |
| `POST /v0/devices/pairing/accept` | 同事电脑提交接入申请。 |
| `POST /v0/devices/pairing/authorize` | 项目侧确认授权范围。 |
| `POST /v0/devices/pairing/revoke` | 撤销邀请或授权。 |
| `GET /v0/projects/{projectId}/collaboration-read-model` | 返回协作设备工作台读模型。 |
| `POST /v0/runners/register` | 扩展 deviceId、authorizationRefs、displayName。 |
| `POST /v0/runners/heartbeat` | 扩展 currentTasks、version、lastErrorSummary。 |
| `POST /v0/tasks/claim` | 继续发放租约，新增 RoutingDecisionRef。 |
| `POST /v0/tasks/pull` | 按 RunnerAuthorization 裁剪 Context Pack。 |
| `POST /v0/tasks/finish` | 强制 AgentRun evidence ref 或等价运行记录。 |

所有写 API 必须服务端校验权限、写 AuditLog，并返回用户可读 `displayMessage`。

## 15. 测试策略

### 15.1 单元测试

- Runner 能力、项目、Agent、仓库、工具、数据范围匹配。
- 未授权/过期/撤销设备不可调度。
- `runner_can_schedule_task` 对 stale heartbeat 拒绝。
- 租约 token hash 校验、expectedVersion 校验、非 owner 写回拒绝。
- Context Pack 裁剪不包含越权资料和 secret。
- 工作台状态映射不暴露 raw internal fields。

### 15.2 集成测试

- 两个 Runner 注册到同一项目。
- 两个不同任务分配给不同 Runner。
- 同一任务双 claim，第二个被拒绝。
- Runner A 领取后心跳续租、拉取上下文、写回 TaskResult/AgentRun。
- Runner A 离线或租约超时后 Runner B 重新领取。
- Runner 缺仓库/工具/数据权限时拒绝，并生成通知和审计。
- 写回失败进入等待回传，并可重试。
- 人工暂停、禁用、转派生成 AuditLog 和 NotificationRecord。

### 15.3 工作台验收

- 主导航显示“协作设备”。
- 项目选择器切换后，设备、邀请、任务路由、权限状态全部刷新。
- 设备列表主列没有 `runnerId`、`deviceId`、raw status、路径、token。
- 邀请、配对、授权、路由、证据、异常恢复形成闭环。
- 空、加载、失败、只读、禁用状态都有中文解释和下一步。
- 窄屏保留项目选择器、邀请入口、设备状态和任务路由。

### 15.4 分布式 proof

真实阶段二验收必须延续 `docs/harness/agent-ring-distributed-runner-proof-harness.md` 的要求：

- 至少两个不同真实 host 或受控真实虚拟 host。
- 证据 JSONL 覆盖 runner_register、runner_heartbeat、runner_list、task_claim、task_pull、task_heartbeat、task_finish、cancel、retry、handoff、stale_lease_reclaim、runner_isolation_rejected。
- 本地双 Runner 模拟只能作为研发自测，不可替代真实同事电脑接入验收。

## 16. 阶段边界

### 16.1 阶段二做

- 共享项目中枢下的 Device + Runner 注册。
- 邀请、配对、授权、撤销、过期。
- Scheduler 多 Runner 匹配、路由解释、租约、心跳、恢复。
- Context Pack 按授权裁剪。
- TaskResult + AgentRun + evidence + notification + audit 写回。
- 工作台“协作设备”中文读模型和状态。
- 双 Runner/三 Runner harness，覆盖成功、冲突、离线、越权和写回。
- 保留 V1 单机 Runner 能力。

### 16.2 阶段二不做

- 不实现 Agent Ring 内部执行网络产品。
- 不做公网穿透、企业 MDM、远程桌面和大规模集群调度。
- 不把同事电脑本地文件当作中枢事实。
- 不让未授权 Runner 读取项目资料。
- 不把技术字段作为主 UI。
- 不一次覆盖所有业务 Agent 的完整生产效率指标。

## 17. 研发拆分建议

建议按低耦合切片交付：

1. **Device/Pairing 数据契约**：新增 PairingRequest、DeviceRegistration、RunnerAuthorization 最小对象或 read-model 子对象；补权限与审计。
2. **Runner 注册扩展**：扩展 `/v0/runners/register` 和 `/v0/runners/heartbeat`，兼容现有 AgentRunner；加入 deviceId、displayName、authorizationRefs、version、lastErrorSummary。
3. **授权 gate 与路由解释**：在 Scheduler 匹配前加入 Device/Authorization 过滤；输出 RoutingDecision 和用户可读拒绝原因。
4. **租约恢复增强**：完善 stale lease、runner offline、writeback_failed、manual transfer 的状态、通知和审计。
5. **Context Pack 裁剪**：按授权范围裁剪 source、repo、tool、data；新增越权测试。
6. **Result writeback 强化**：要求 AgentRun ref 或等价运行记录；验证 TaskResult 必填字段和 evidence refs。
7. **协作设备读模型**：提供 `/collaboration-read-model`；复用 V1 `DesktopWorkbenchReadModel`，新增 devices、pairing、routeBoard、recoveryItems。
8. **工作台 UI 切片**：把 Runner 入口升级为“协作设备”；实现邀请、配对、授权、设备列表、任务路由、异常恢复和技术详情折叠。
9. **Harness 与验证器**：扩展 `distributed_runner_proof_harness.py` 和工作台 validator，覆盖真实双 host 与用户可读检查。
10. **产品复核和测试闭环**：产品经理先复核本方案；研发实现后测试 Agent 出具多设备验收 TaskResult；PM 再决定最终接受。

## 18. 验收映射

| PRD 验收 | 技术承诺 |
| --- | --- |
| P2-AC-001 两台 Runner 注册同项目 | Device + Runner registry，runner_list/read model 可见。 |
| P2-AC-002 两任务分给不同 Runner | Scheduler 排序和 RoutingDecision 记录。 |
| P2-AC-003 同任务不可双执行 | 单有效租约 + token hash + expectedVersion。 |
| P2-AC-004 离线/超时可恢复 | stale_lease/recovery_pending/转派/取消。 |
| P2-AC-005 越权不能拉资料/工具 | Authorization gate + Context Pack 裁剪。 |
| P2-AC-006 TaskResult 完整 | finish 校验 + Result Center 质量评价。 |
| P2-AC-007 AgentRun 写回 | finish evidence 要求 AgentRun ref。 |
| P2-AC-008 多设备状态可见 | CollaborationWorkbenchReadModel。 |
| P2-AC-009 暂停/禁用/转派有审计通知 | 写 API 统一 AuditLog + NotificationRecord。 |
| P2-AC-010 不破坏 V1 单机闭环 | 现有 AgentRunner/lease API 向后兼容。 |

## 19. 风险与开放问题

| 风险 | 处理 |
| --- | --- |
| 第二台真实 Runner host 不可用 | 记录 blocker；本地模拟只能作为自测，不能作为真实验收。 |
| 授权模型过细导致 UI 复杂 | 主 UI 只显示业务摘要，细项放授权详情和技术证据。 |
| AgentRun 目前可能只作为 evidenceRef 写入 | 研发切片中补强 finish 契约或验证器，要求 AgentRun ref。 |
| 旧 Runner 无 deviceId | 兼容为 V1/manual Runner，但不可作为同事电脑接入验收唯一证据。 |
| 网络抖动导致误判离线 | 区分“降级/离线/过期”，保留最近同步状态，写恢复动作。 |
| 权限拒绝提示暴露内部字段 | 工作台 validator 加用户可读检查，主界面禁止 raw fields。 |

## 20. Product Review Handoff

本方案可交产品经理 Agent 复核。复核重点：

- 是否满足阶段二 PRD 的业务目标、功能需求、非功能需求和 P2-AC-001 至 P2-AC-010。
- 是否遵守设计规范：主 UI 中文业务表达，内部字段只进技术详情/证据。
- 是否接受阶段边界：Core 只调度和记录，Agent Ring 外部执行；真实分布式验收必须使用两个真实 host。
- 是否同意研发按第 17 节拆分，并在产品接受后才进入 Development Agent 实现。
