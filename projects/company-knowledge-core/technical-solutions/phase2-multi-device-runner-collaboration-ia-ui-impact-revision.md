---
type: KnowledgeItem
title: 阶段二产品 IA 与 UI/交互设计对技术方案影响复核与修订方案
description: Architecture impact review and technical-solution addendum for Phase 2 multi-device Runner collaboration after Product IA and UI/interaction revision.
timestamp: "2026-06-22T12:46:28Z"
artifactId: ts.phase2.multi-device-runner-collaboration.ia-ui-impact-revision
projectId: company-knowledge-core
ownerAgent: agent.company.architecture
taskId: kt-v2-colleague-runner-architecture-ia-design-impact-review
status: draft
sourceMaterialRefs:
  - docs/product/ai-native-os/phase-2-multi-device-runner-collaboration-prd.md
  - projects/company-knowledge-core/product-information-architecture/phase2-colleague-runner-workbench-information-architecture.md
  - projects/company-knowledge-core/design/phase2-multi-device-runner-workbench-ui-interaction-revision.md
  - projects/company-knowledge-core/technical-solutions/phase2-multi-device-runner-collaboration-technical-solution.md
operatingRuleRefs:
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator.md
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - agents/agent.company.architecture.md
  - projects/company-knowledge-core/project.md
updatedAt: "2026-06-22T12:46:28Z"
---

# 阶段二产品 IA 与 UI/交互设计对技术方案影响复核与修订方案

## 结论

产品 IA 和 UI/交互返工设计不推翻原技术方案。原方案中的 DeviceRegistration、AgentRunner 扩展、PairingRequest、RunnerAuthorization、Scheduler 硬过滤、租约/心跳/写回、Context Pack 裁剪、CollaborationWorkbenchReadModel、工作台 UI 约束和 API/Gateway 切片仍是正确主干。

但 IA/UI 明确了更多用户可读字段、危险动作、只读/过期降级、未知状态兜底、窄屏交互和审计可读摘要。原方案已有方向，但不够可执行。研发前必须把本文作为技术方案 addendum 一并交 PM 复核；PM 通过后再进入研发。

影响级别：中低。影响范围是 read model、写操作 API 契约、状态/降级策略、审计摘要和验收检查；不要求重做身份模型、租约一致性、调度核心或 Agent Ring 边界。

## 复核依据

- PRD 要求同事电脑接入同一项目中枢、调度到最合适 Runner、结果写回、离线/超时恢复、权限拦截和审批等待。
- 产品 IA 要求工作台入口为“协作设备”，对象覆盖项目、设备、Runner、授权、路由、恢复、结果、证据、审计和技术详情；主界面禁曝内部 id、raw status、路径、endpoint、token、secret 和错误栈。
- UI/交互返工设计要求 read model 直接给可读字段，RouteBoard 解释“分配给谁/为什么/卡点/下一步”，危险动作二次确认，加载失败保留最近安全数据，未知状态显示“需处理”。
- 原技术方案已覆盖设备/Runner/授权/路由/租约/写回/Context Pack/read model/API/测试策略，但 `collaborationSummary`、危险动作 API、只读/过期策略和审计摘要需要更明确。

## 影响矩阵

| IA/UI 要求 | 原技术方案覆盖情况 | 修订结论 |
| --- | --- | --- |
| 主入口“协作设备”，主界面中文业务含义 | 第 13、15.3 节已覆盖 | 不改主架构；作为 UI 验收硬门禁保留。 |
| `devices[]` 可读字段 | 第 12.2 节已列 displayName、ownerLabel、availabilityLabel 等 | 不需新增对象；研发必须直接从 read model 取可读字段。 |
| `routeBoard[]` 分配原因、卡点、下一步 | 第 12.3 节已覆盖 | 不需新增对象；未知/缺失字段不得回退显示内部状态。 |
| `collaborationSummary` 首屏摘要 | 第 12.1 节只列对象名，字段不完整 | 需要补字段契约。 |
| 只读、加载失败、数据过期保留最近安全数据 | 原方案有 staleStatePolicy 名称，缺行为 | 需要补降级策略。 |
| 撤销授权、暂停接单、禁用电脑、取消任务、转交执行中任务 | 原方案有 revoke、manual transfer 和通用 permission gate，缺完整动作清单 | 需要补写 API/action contract。 |
| 危险动作二次确认和可读审计摘要 | 原方案要求写 AuditLog 和 displayMessage，缺 impact summary | 需要补 preflight/confirmation/auditSummary。 |
| 技术详情默认折叠、脱敏 | 第 13、15 节方向正确 | 需要列入 read model 技术详情契约和 validator。 |
| 窄屏保留项目选择、邀请、设备状态、任务路由 | 原方案只说窄屏保留核心 | 需要补工作台验收项；不影响后端主模型。 |

## 技术方案修订

### 1. `CollaborationWorkbenchReadModel` 补强

原方案第 12.1 节保留，补充 `collaborationSummary` 字段：

| 字段 | 说明 |
| --- | --- |
| `projectLabel` | 当前项目中文名。 |
| `collaborationAllowedLabel` | 当前项目是否允许同事电脑加入。 |
| `availableDeviceCount` / `availableDeviceCountLabel` | 可接任务电脑数量和中文摘要。 |
| `activeRouteSummary` | 当前任务路由摘要，例如“2 个任务执行中，1 个等待授权”。 |
| `pendingAuthorizationCount` / `pendingAuthorizationLabel` | 待确认授权数量和中文摘要。 |
| `exceptionCount` / `exceptionLabel` | 离线、超时、写回失败、越权等异常数量和中文摘要。 |
| `lastSyncLabel` | 最近同步时间，可显示“刚刚”“10 分钟前”。 |
| `dataFreshness` | `fresh`、`stale`、`partial`，主界面只显示中文映射。 |
| `primaryAction` | 首屏主动作，例如“邀请同事”“处理授权”“查看异常”。 |

强制约束：

- 主模板只渲染 label/display 字段。
- raw enum、id、endpoint、路径、错误栈只能进入 `technicalDetails[]`。
- 未知状态统一映射为“需处理”，并把原始值放入脱敏技术详情。

### 2. `staleStatePolicy` 行为明确

`staleStatePolicy` 必须包含：

| 字段 | 说明 |
| --- | --- |
| `preserveLastKnownSafeData` | 加载失败或 API 不可达时保留最近一次安全可显示数据。 |
| `disableUnsafeWrites` | 数据过期或权限不明时禁用写操作。 |
| `disabledReasonLabel` | 禁用按钮的中文原因。 |
| `retryActionLabel` | 用户可见重试动作。 |
| `technicalRef` | 折叠技术详情引用。 |

降级规则：

- 读模型局部失败不能清空设备列表和路由看板的已知安全摘要。
- 写操作必须以服务端 permission gate 为准；前端禁用只是提示，不是安全边界。
- API 不可达时显示“暂时无法确认最新状态”，并保留最近同步时间。

### 3. 写操作和危险动作契约补强

原方案第 14 节 API/Gateway 切片保留，增加或明确以下动作；可作为单独 endpoint，也可在统一 action endpoint 中用 action type 表达，但服务端必须校验权限、写 AuditLog、返回 `displayMessage`。

| 动作 | 最小契约 |
| --- | --- |
| 邀请同事电脑 | 创建 PairingRequest；不暴露 token 原文。 |
| 确认授权 | 写 RunnerAuthorization；返回授权范围中文摘要。 |
| 撤销授权 | 使对应授权不可调度；如有活跃租约，进入恢复/转派流程。 |
| 暂停接单 / 恢复接单 | 修改 Runner 可调度状态，不删除注册记录。 |
| 禁用电脑 / 启用电脑 | 设备级 gate；禁用后所有绑定 Runner 不可领取新任务。 |
| 释放租约 / 取消任务 | 校验 owner/PM 权限和 expectedVersion；写恢复或取消证据。 |
| 转交执行中任务 | 结束旧租约或标记 stale/recovery，重新走候选 Runner 过滤和 RoutingDecision。 |

所有危险动作必须先返回或展示：

- `impactSummary`: 会影响哪些电脑、任务、授权或证据。
- `confirmationRequired`: true。
- `confirmationLabel`: 中文确认文案。
- `displayMessage`: 成功/失败中文说明。
- `auditSummary`: 操作记录可读摘要。
- `technicalRef`: 脱敏技术详情引用。

### 4. 调度和恢复不变量补充

- `runner_can_schedule_task` 必须拒绝未授权、过期授权、撤销授权、暂停接单、禁用电脑、心跳过期或数据范围不满足的 Runner。
- 撤销授权、禁用电脑、释放租约、转交任务都必须产生 RoutingDecision 或 RecoveryItem，使工作台能解释“为什么不能派给这台电脑”和“下一步谁处理”。
- 活跃任务被撤销授权或禁用设备影响时，不得静默失败；状态进入 `recovery_pending` 或 `waiting_runner`，并保留旧证据引用。
- `changes_requested` 返工任务重新进入待分配时，必须重新执行授权和范围过滤，不沿用旧租约。

### 5. 审计和通知可读摘要

每个写动作除原始 AuditLog 外，还必须给工作台 read model 提供可读操作记录：

| 字段 | 说明 |
| --- | --- |
| `operationLabel` | “撤销张三 Mac 的代码仓库写权限”。 |
| `actorLabel` | 操作人显示名或岗位。 |
| `targetLabel` | 电脑、任务、授权或结果的中文名称。 |
| `businessImpactLabel` | 对任务路由、权限、结果写回的影响。 |
| `createdAtLabel` | 用户可读时间。 |
| `technicalRef` | 原始审计引用，折叠展示。 |

### 6. 验收和测试补充

研发/测试任务应在原方案第 15 节基础上补以下检查：

- `collaborationSummary` 字段完整，首屏不用计算内部状态。
- `devices[]`、`routeBoard[]` 缺字段时不渲染 raw id/status。
- 未知状态显示“需处理”，原始值只进技术详情。
- API 失败返回 `displayMessage`，按钮禁用有中文原因。
- 撤销授权、暂停接单、禁用电脑、取消任务、转交任务均有二次确认和 AuditLog。
- 加载失败/数据过期保留最近安全数据，写操作被禁用。
- 技术详情默认折叠并脱敏 token、secret、路径、错误栈。
- 窄屏保留项目选择、邀请入口、设备状态、任务路由和权限/异常提示。

## 不需要修订的部分

- Agent Ring 仍是外部系统；本仓库只定义调度、记录、读模型和 gateway prototype。
- Core 不拥有 full source code、secret 值、GEO/customer schema 或分布式电脑执行。
- 原 DeviceRegistration、PairingRequest、RunnerAuthorization、AgentRunner 扩展、租约一致性、Context Pack 裁剪和 TaskResult/AgentRun 写回主模型继续有效。
- 阶段二仍不以本机双 Runner 替代真实双 host 最终验收，除非产品经理明确接受阶段性替代证据。

## 产品经理复核建议

建议 PM 重新复核原技术方案加本文 addendum。若通过，可把研发任务输入改为：

1. `projects/company-knowledge-core/technical-solutions/phase2-multi-device-runner-collaboration-technical-solution.md`
2. `projects/company-knowledge-core/technical-solutions/phase2-multi-device-runner-collaboration-ia-ui-impact-revision.md`
3. 产品 IA 和 UI/交互返工设计。

PM 复核重点：

- 是否接受“原方案主干不变 + addendum 补强”的路径。
- 是否要求把 addendum 合并回原技术方案正文后再交研发。
- 真实双 host 验收缺口是否仍记录为阶段二最终验收风险。
