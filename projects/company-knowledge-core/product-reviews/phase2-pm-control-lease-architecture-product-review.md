---
type: ReviewRecord
title: Phase 2 PM Control Lease Architecture Product Review
projectId: company-knowledge-core
reviewerAgent: agent.company.product-manager
status: accepted
decision: approved_for_engineering
createdAt: "2026-06-23T12:10:00Z"
sourceRefs:
  - docs/product/ai-native-os/phase-2-pm-control-lease-prd.md
  - projects/company-knowledge-core/technical-solutions/phase2-pm-control-lease-technical-solution.md
  - projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-product-review.md
outputForTask: kt-v2-pm-control-lease-product-review
---

# Phase 2 PM Control Lease Architecture Product Review

## 复核结论

通过。架构方案满足产品需求，可交研发 Agent 实现。

方案覆盖同一项目单主控 PM、协同 / 备用边界、所有 PM 调度写操作带租约、中枢拒绝无效租约并审计、工作台展示、用户可理解文案、验收可测试。未发现阻断研发开工的产品缺口。

## 复核范围

本次只做产品复核，不改代码。

复核材料：

- `docs/product/ai-native-os/phase-2-pm-control-lease-prd.md`
- `projects/company-knowledge-core/technical-solutions/phase2-pm-control-lease-technical-solution.md`
- `projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-product-review.md`

## 产品需求对齐矩阵

| 产品要求 | 架构方案覆盖情况 | 结论 |
| --- | --- | --- |
| 同一项目同一时间只能一个主控 PM 持有调度租约。 | `Acquire` 流程在存在健康 active 租约时拒绝；项目级 fencing token 递增；并发测试要求同项目最多一个 active 租约。 | 通过 |
| 协同 PM 和备用 PM 可查看、评论、准备接管，但不能改项目调度。 | `ProjectPmParticipant` 定义 `primary`、`collaborator`、`standby`；校验要求请求 PM 等于 `primaryPmAgentId` 且具备能力；协同 / 备用写入会以 non-primary 或 permission mismatch 拒绝。 | 通过 |
| 所有 PM 写操作必须带租约。 | `Protected PM Writes` 覆盖项目计划、任务创建/更新、派发控制、验收路由、恢复路由、调度通知、工作台 PM 命令；API/CLI 均要求 PM 写上下文或租约参数。 | 通过 |
| 中枢拒绝无租约、过期租约、非主控租约、项目不匹配租约并审计。 | `validate_pm_control_lease_for_write` 为核心唯一校验；失败调用 `deny_pm_control_lease_write`；拒绝必须不写目标业务对象，写 `pm_control_lease.denied`，返回稳定错误码和中文文案。 | 通过 |
| 接管必须显性，记录前任、后任、原因、时间、租约变化和审计。 | `PmLeaseTakeoverRecord` 覆盖 from/to PM、operator、reason、previous status、new lease、occurredAt、auditRef；健康主控接管需确认，过期/失联接管需原因。 | 通过 |
| 工作台展示主控 PM、协同 PM、备用 PM、租约健康、接管记录。 | `PMControlWorkbenchReadModel` 包含 `currentLease`、`participants`、`takeoverRecords`、`denialSummaries`、`healthExplanation`；展示要求包含主控卡片、协同/备用列表、拒绝摘要、接管历史。 | 通过 |
| 用户可理解，不以内部 ID 作为主说明。 | 拒绝语义提供中文 display message；工作台 read model 使用 `DisplayObjectRef`、`nextAction`、`healthExplanation`，展示 PM 名、Owner、电脑、健康、到期和最近心跳。 | 通过 |
| 验收可测试。 | 测试策略覆盖 core、protected write、API、CLI、workbench、Runner 回归、并发/idempotency。关键失败路径包含 missing、expired、non-primary、project mismatch、stale fencing token。 | 通过 |
| 不回归已有 Runner 任务租约和多设备能力。 | 兼容性章节明确 Runner 注册、heartbeat、claim、TaskResult/AgentRun writeback 继续使用 Runner/task lease，不要求 PMControlLease。 | 通过 |

## 关键产品判断

### 单主控机制足够

方案把主控 PM 租约提升为项目级控制面，并用项目 latest fencing token 防旧主控写入。这个设计能同时处理并发申请、旧租约重放、接管后旧主控继续写入三类冲突，满足“同一项目同一时间只能一个主控 PM”的产品目标。

### 协同 / 备用边界清楚

协同 PM 和备用 PM 在数据模型、核心校验、工作台展示中都有独立角色。产品要求的“可查看、可准备、不可静默写入”已落到校验条件：请求 PM 必须是当前租约 `primaryPmAgentId`，且具备项目权限和动作能力。备用 PM 只有接管成功后才变成新主控。

### 写入保护口径完整

受保护写操作清单覆盖产品 PRD 中所有项目级 PM 调度写入，且明确排除 Runner heartbeat、Runner claim/writeback、只读查询、系统审计等不应受 PM 租约保护的路径。产品上可接受。

### 拒绝和审计满足可追溯

拒绝路径要求“先审计再抛错”，并明确不写目标业务对象。审计字段包含项目、请求 PM、当前主控 PM、动作、原因、来源、租约状态和时间，能支持用户解释、问题追踪和测试断言。

### 工作台能支撑用户理解

方案提供 PM 控制 read model，并要求项目详情展示主控卡片、协同/备用列表、拒绝摘要、接管历史和健康解释。该信息结构能满足用户判断“谁在管、谁能接、为什么被拒、下一步做什么”。

## 非阻断建议

以下不影响交研发，但建议研发实现时一并落实：

1. 工作台 `takeoverRecords` 和 `denialSummaries` 不要长期保持 `Record<string, unknown>[]` 的弱类型形态；实现时应收敛为明确展示字段，避免前端只能猜字段。
2. 中文 display message 已覆盖拒绝场景；实现时请同时返回 `nextAction`，保证页面能展示“联系主控 PM / 发起接管 / 刷新状态”等下一步建议。
3. 健康状态阈值需要在架构或实现中给出可配置默认值，例如 expiring、stale、expired 的时间边界，便于测试写稳定断言。
4. 工作台展示应隐藏或弱化 `leaseId`、`fencingToken` 等内部信息，把 PM 名称、项目名、电脑名和可读状态作为主信息。

## 研发准入结论

可交研发 Agent。

研发实现必须以架构方案中的核心校验函数为唯一权威入口，不能只在 API、CLI 或前端做租约检查。验收时必须证明：

1. 同一项目最多一个 active PM 主控租约。
2. 所有 PM 调度写入口先验租约，再写业务对象。
3. 无效租约拒绝不写目标对象，且写 `pm_control_lease.denied` 审计。
4. 接管生成新租约、接管记录和审计，旧 token 失效。
5. 工作台展示主控 PM、协同 PM、备用 PM、租约健康、拒绝摘要和接管记录。
6. 用户看到中文可理解文案和下一步建议。
7. Runner 注册、heartbeat、任务 claim、TaskResult/AgentRun writeback 不因 PM 控制租约回归。

## 返工项

无阻断返工项。

## 变更记录

| 时间 | 变更 | 说明 |
| --- | --- | --- |
| 2026-06-23 | 新增 | 完成 PM 主控租约架构方案产品复核，结论为通过，可交研发。 |
