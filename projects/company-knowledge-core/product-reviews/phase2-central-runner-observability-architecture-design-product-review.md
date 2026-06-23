---
type: ReviewRecord
title: Phase 2 方案二中枢 Runner 观测工作台架构与设计产品复核
projectId: company-knowledge-core
reviewerAgent: agent.company.product-manager
status: accepted
reviewedAt: "2026-06-23T00:00:00Z"
prdRef: docs/product/ai-native-os/phase-2-central-runner-observability-prd.md
reviewTargets:
  - projects/company-knowledge-core/technical-solutions/phase2-central-runner-observability-technical-solution.md
  - projects/company-knowledge-core/design/phase2-central-runner-observability-workbench-design.md
---

# Phase 2 方案二中枢 Runner 观测工作台架构与设计产品复核

## 复核结论

通过。

技术方案与设计稿已满足 PRD 更新后的核心边界：工作台是“登记入口可操作，执行监管只读”。当前产物可以进入后续工程拆解与测试用例细化。

## 复核范围

1. PRD：`docs/product/ai-native-os/phase-2-central-runner-observability-prd.md`
2. 技术方案：`projects/company-knowledge-core/technical-solutions/phase2-central-runner-observability-technical-solution.md`
3. 设计稿：`projects/company-knowledge-core/design/phase2-central-runner-observability-workbench-design.md`

## 覆盖检查

| PRD 要求 | 技术方案复核 | 设计稿复核 | 产品结论 |
| --- | --- | --- | --- |
| 工作台可创建项目 | 已定义 `POST /v0/workbench/projects`、权限、审批、幂等和审计。 | 顶部有“创建项目”；表单含项目名称、负责人、目标、资料范围、可见范围；提交前确认；说明不会自动派发任务。 | 通过 |
| 工作台可电脑注册 / 邀请 | 已定义 RunnerInvitation / 配对码、bootstrap token、Runner 注册协议、授权范围、审批和审计。 | 顶部有“邀请/注册电脑”；流程覆盖选择项目、负责人、电脑显示名、可做工作、Agent、模型、工具、资料范围、确认和审批中状态。 | 通过 |
| 工作台可工具注册 / 申请 | 已定义 `POST /v0/workbench/tools` 与 `POST /v0/workbench/tool-registration-requests`，区分低风险登记和高风险申请，含 Tool Owner 审批。 | 顶部有“注册工具”；表单含工具名称、用途、负责人、适用项目、可使用 Agent、风险等级、凭据状态、审批人。 | 通过 |
| 执行监管区域只读 | 已明确不提供 `dispatchTask`、`repairTask`、`overwriteTaskResult`、`editAgentRun`、`forceCompleteTask`、`claimAsWorkbench`；执行写入只允许 Scheduler 或持有效 lease token 的 Runner。 | “执行监管只读”列明只允许查看、筛选、复制摘要、打开证据 / 审批 / 审计；禁止派发、取消、转派、验收、启停、重试、修改 Agent / 模型 / token / 工具授权、写 TaskResult / AgentRun。 | 通过 |
| 用户能看懂几台电脑、几个项目 | 技术方案提供工作台 read model、runnerRegistry、metrics、telemetrySummary。 | 首屏指标明确“4 个项目”“6 台电脑接入”；项目选择支持全部项目和单项目视图。 | 通过 |
| 用户能看懂项目任务明细 | 技术方案返回 activeQueue、selectedTask、runnerLeases、progressEvents、auditTrail、notifications。 | 项目页含项目任务明细，任务表首列任务名称、第二列对应需求，并展示任务、待验收、风险和最近更新。 | 通过 |
| 用户能看懂电脑明细 | 技术方案覆盖 Runner 注册、心跳、当前工作、Agent session、telemetry。 | 电脑入口和详情覆盖负责人、电脑显示名、可做工作、Agent、模型、工具、资料范围、审批状态和上报状态。 | 通过 |
| 模型 / token / tool / Agent 状态 | 已定义 runner telemetry、modelUsage、toolUsage、Agent session register / heartbeat，按项目、任务、Runner、Agent session 聚合。 | 监管区明确展示 Agent、模型、token 消耗、工具和异常；电脑注册也暴露 Codex、Claude、本地模型和可用工具。 | 通过 |
| 权限 / 审批 / 审计 | 技术方案将权限、审批、审计放在 API 边界，所有工作台入口写入、Runner 写入、Scheduler 写入、审批动作生成 AuditLog。 | 入口表单和反馈文案要求记录申请人、负责人、项目范围、可做工作、审批结论、工具风险和权限范围；有“审批与审计”区。 | 通过 |
| 幂等 | 技术方案覆盖创建项目、邀请电脑、注册工具、工具申请、Runner register、heartbeat、task event、telemetry、Agent session 的 idempotencyKey 与 CommandRecord 规则。 | 设计稿不展开幂等细节，但这是技术实现责任；设计无冲突。 | 通过 |
| 结果不可篡改 | 技术方案禁止覆盖 TaskResult / AgentRun，租约边界限制执行写入。 | 设计稿禁止直接写入 TaskResult、AgentRun、审计或通知，禁止改模型选择、token 数字或工具授权。 | 通过 |

## 产品可接受依据

### 登记入口

产品要求不是“所有工作台区域都只读”，而是登记入口可操作。技术方案和设计稿均覆盖三个入口：

1. 创建项目。
2. 邀请 / 注册电脑。
3. 注册工具 / 提交工具申请。

三类入口均体现提交、确认、审批、状态反馈和审计记录，不会自动变成执行动作。

### 执行监管

执行监管区域满足只读边界。任务派发、租约、执行修复、结果写回仍属于 Scheduler、Runner、审批流或 Agent Ring，不由工作台直接操作。设计稿也给出禁止入口和禁用说明文案，用户不会误以为可以在监管区改任务状态。

### 可理解性

设计稿用中文业务文案替代内部对象名，明确要求不要把 `projectId`、仓库路径或内部代号作为主文案。首屏能回答“几个项目、几台电脑、哪些任务在跑、哪里异常、哪些入口需要处理”。项目、电脑、工具、任务、审批与审计都有清晰入口。

### 治理口径

技术方案对权限、审批、审计、幂等、token 脱敏和 lease 边界均有实现口径。设计稿对确认摘要、审批中状态、审计入口和敏感信息不展示也有产品表达。产品侧可接受。

## 非阻塞实施注意项

1. 工程实现时，工作台入口写操作只能创建登记 / 申请 / 请求型对象，不得顺手创建任务租约或修改执行状态。
2. “修复”“重试”“转派”“验收通过”即使在 UI 上出现，也必须是请求或跳转到审批 / 调度流程，不能成为直接写任务结果的按钮。
3. telemetry 中的 token、模型、工具信息必须保留 unknown / missing 状态，不能用 0 或空字符串掩盖未上报。
4. 审计入口必须能从项目、电脑、工具、任务四个视角追溯登记、审批、拒绝、授权范围变化和执行上报。
5. 设计稿未展开幂等交互文案，工程实现重复提交时需要返回“已提交过同一申请”或“同一幂等键内容冲突”的用户可读提示。

## 返工项

无阻塞返工项。

## 放行条件

1. 架构与设计可进入工程拆解。
2. 测试用例必须覆盖：创建项目、电脑邀请 / 注册、工具注册 / 申请、执行监管只读、权限拒绝、审批拒绝、幂等重复提交、模型 / token / tool / Agent 状态展示。
3. 真实双机验收仍按 PRD 执行，不能用同一电脑多进程代替。
