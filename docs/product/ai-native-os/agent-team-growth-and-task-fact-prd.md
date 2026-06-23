---
type: ProductRequirementPackage
requirementId: ANOS-REQ-160-FUSION-V1
title: Agent 团队成长与任务事实视图融合方案
description: 基于 ANOS-REQ-160，将任务事实视图、项目经理 Agent 主控交付、子 Agent worker 协作、任务来源追溯、接收审查和 Agent 能力成长沉淀融合为短期 V1 产品方案。
timestamp: "2026-06-23T09:05:00Z"
projectId: company-knowledge-core
ownerAgent: agent.company.product-manager
status: draft
phase: agent-team-growth-task-fact-fusion
scopeVersion: V1
sourceBaseline:
  - docs/product/ai-native-os/task-execution-productization-prd.md
  - docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md
  - docs/product/ai-native-os/task-source-receiver-review-prd.md
  - docs/agent-team/company-agent-team-operating-guide.md
  - docs/agent-team/project-manager-agent-skill-pack.md
relatedRequirements:
  - ANOS-REQ-160
updatedAt: "2026-06-23T09:05:00Z"
---

# Agent 团队成长与任务事实视图融合方案

## 一句话目标

让用户在一个任务工作台里同时看清两件事：当前项目任务是否形成业务交付闭环，以及这次交付暴露出的 Agent 团队能力缺口是否已经沉淀为可复用的改进资产。

## 背景判断

现有 ANOS-REQ-160 已确认主线：任务事实视图 -> PM Agent 调度子 Agent worker -> worker 完成角色工作 -> PM Agent 收敛结果并写回 TaskResult、证据和审计 -> 失败、返工、阻塞和人工纠偏进入 AgentImprovementProposal、EvalCase、Skill 或角色规则更新。

任务来源模型和 ReceiverReview 已补齐“任务为什么存在、下游能不能接”的追溯门禁。项目经理 Agent Skill Pack 已明确 PM 负责项目启动、任务队列健康、跨角色协调、验收路由、风险升级和交付闭环，但不能代写 PRD、UX、代码、测试或最终人类验收。

本方案把这些资料收敛为短期 V1 产品口径：不先追求每个角色都是长期独立 Agent，而是由项目经理 Agent 主控，调度子 Agent 完成业务交付，并把任务事实和成长信号放到同一个工作台视图里。

## 假设

- 本版不考虑隐私脱敏，工作台按已有权限与证据引用策略展示可见内容。
- 两台电脑各自处理不同项目，不把多电脑共同抢一个项目纳入本版。
- 两台电脑共享公司级 Agent 团队能力、角色规则、Skill、EvalCase 和版本发布口径。
- 子 Agent 在短期内可以是 PM 调度的 worker，不要求拥有长期身份、独立队列或完整自治闭环。
- 信息不足时，以现有 ProjectTask、KnowledgeTask、TaskResult、AgentRun、ReceiverReview、ReviewRecord、NotificationRecord、AuditLog、AgentImprovementProposal、EvalCase 等对象承载，不新增核心对象。

## 目标

1. 让 Project Owner 能从任务工作台判断任务状态、下一步负责人、结果证据、验收路由和风险缺口。
2. 让项目经理 Agent 能用同一事实视图调度子 Agent、收敛 worker 结果、创建后续任务、返工任务或人工决策事项。
3. 让产品、设计、架构、研发、测试、知识工程等子 Agent 的输出都有角色边界、输入、证据和 TaskResult provenance。
4. 让失败、返工、阻塞、人类验收不通过和人工纠偏自动暴露为成长信号，并沉淀为改进候选。
5. 让不同电脑上的不同项目复用同一套公司级 Agent 能力版本，避免每个项目从零积累经验。

## 非目标

1. 不做隐私脱敏方案。
2. 不做多电脑共同领取、抢占或并发执行同一个项目。
3. 不新增 `TaskFactView`、`ExecutionFact`、`TaskTimeline` 等核心对象作为真源。
4. 不重写 Scheduler、Agent Ring、Runner claim、lease、heartbeat、finish 或 TaskResult 写回链路。
5. 不让 worker 输出直接等同最终任务结论；PM 必须收敛。
6. 不让项目经理 Agent 替代产品、设计、架构、研发、测试、知识工程或人类验收人的职责。
7. 不把未经 Review 的经验直接升级为公司级规则、Skill 或知识。
8. 不写技术实现代码，不定义具体数据库表、接口字段实现或前端组件实现。

## 短期 V1 范围

### 必须包含

1. 单个 ProjectTask 的融合事实视图：任务身份、来源、状态解释、责任人、Runner/Agent、执行过程、worker 参与、结果证据、质量评价、验收、成长信号、通知审计和下一步。
2. PM 调度子 Agent worker 的记录口径：worker role、输入、边界、允许动作、禁止动作、期望输出、证据要求、交付接收人、PM consolidation。
3. 任务来源追溯：`workSourceType`、`requirementRefs`、`acceptanceCriteriaRefs`、`defectRefs`、`sourceReason`、`receiverReviewRefs` 等字段在任务和 TaskResult 中可追溯。
4. ReceiverReview 接收审查：下游 Agent 开工前声明接受、带假设接受、要求返工或需要人类决策。
5. PM 验收路由：通过后创建下一岗位任务，拒绝或要求修改时创建返工任务，冲突时创建人工决策事项。
6. 自动沉淀入口：当质量评价失败、验收打回、重复阻塞、人工纠偏或角色边界违规时，生成 AgentImprovementProposal 和 EvalCase 草稿。
7. 双电脑不同项目复用：工作台展示当前电脑/项目任务事实，同时标明使用的公司级 Agent 能力版本。

### 暂不包含

1. 跨电脑抢同一项目任务、租约竞争、冲突合并或协同编辑。
2. 全自动升级公司级规则；公司级 Skill、角色规则、工作流或调度规则更新仍走 Review/审批。
3. PM Health 重构；V1 只复用事实口径和必要健康提示。
4. 旧任务数据迁移；旧任务缺字段只显示 `legacy gap`。
5. 独立 Agent 长期身份治理；成熟后再从 worker 迁移为正式独立 Agent。

## 角色边界

| 角色 | 本版职责 | 边界 |
| --- | --- | --- |
| 项目经理 Agent | 主控项目任务队列、拆任务、派 worker、收敛结果、验收路由、返工/升级、状态通知、复盘触发。 | 不代写 PRD、设计、代码、测试报告、知识发布；不绕过人类验收。 |
| 产品经理 Agent | 输出需求、PRD、验收标准和产品验收意见，提供 feature 任务的需求与验收引用。 | 不负责项目调度和跨角色闭环。 |
| 设计 Agent | 接收产品输入，产出信息架构、交互状态、体验风险和设计交付。 | 不替代产品目标或技术方案。 |
| 架构师 Agent | 接收产品/设计输入，产出技术方案、架构约束和代码架构审查。 | 不替代研发实现或测试签收。 |
| 研发 Agent | 基于任务和技术方案完成实现与开发证据。 | 不自验收产品通过。 |
| 测试 Agent | 基于需求、验收标准和研发交付完成测试、回归和质量结论。 | 不修改研发文件，不替代 PM 收敛或人类最终验收。 |
| 知识工程 Agent | 判断经验是否沉淀为知识、Skill、EvalCase、指南更新，并执行 Review 路径。 | 不把草稿经验直接发布为 verified/policy。 |
| 子 Agent worker | 接收 PM 派发的角色工作，按边界产出结果、证据和缺口。 | 不拥有最终任务结论，不越权执行其他角色职责。 |
| 人类 Reviewer / Owner | 对人类门禁事项、跨团队规则、权限、安全、客户承诺和最终验收做确认。 | 不需要重读全部原始日志，但要能看到可读结论、范围和证据引用。 |

## 核心流程

```txt
项目目标 / 需求 / 反馈进入
-> 项目经理 Agent 建立或选择项目
-> 识别 workSourceType、需求/缺陷/资料/原因引用
-> 拆分 ProjectTask / KnowledgeTask
-> 按角色调度子 Agent worker
-> 子 Agent 开工前生成 ReceiverReview
-> 子 Agent 完成角色工作并写入 TaskResult、证据、质量评价和交接摘要
-> PM Agent 在融合事实视图中收敛 worker 输出
-> 通过：进入验收门或创建下一岗位任务
-> 不通过：创建返工/修复/升级任务
-> 人类决策需要：创建决策事项并通知
-> 失败、返工、阻塞、人工纠偏同步生成成长信号
-> 知识工程 Agent Review 后沉淀为 EvalCase、Skill、角色规则、工作流或项目经验
```

## 信息模型

本方案不新增核心对象，使用现有对象形成读模型或工作台 projection。

| 信息块 | 来源对象/字段 | 工作台展示口径 |
| --- | --- | --- |
| 任务身份 | ProjectTask / KnowledgeTask | taskId、title、projectId、priority、status、createdAt、updatedAt。 |
| 任务来源 | ProjectTask / KnowledgeTask | `workSourceType`、`requirementRefs`、`acceptanceCriteriaRefs`、`defectRefs`、`sourceReason`、`sourceMaterialRefs`。 |
| 接收审查 | ReceiverReview | 接收角色、输入引用、decision、issues、assumptions、createdBy、reviewedAt。 |
| PM 调度 | ProjectTask、TaskResult、AuditLog | worker role、输入摘要、边界、允许/禁止动作、期望输出、证据要求、交付接收人。 |
| 执行过程 | AgentRun、AgentRunner、TaskResult | assignedAgent、executorAgent、assignedRunner、leaseOwner、runnerId、currentPhase、heartbeat、startedAt、completedAt。 |
| 结果证据 | TaskResult、ReviewRecord | result status、summary、outputRefs、evidenceRefs、testsOrChecks、qualityEvaluation、commonRulesEvaluation。 |
| 验收路由 | TaskResult、acceptancePolicy、ReviewRecord | acceptanceStatus、acceptanceOwner、humanAcceptanceRequired、decisionReason、followupTaskRefs。 |
| 成长信号 | TaskResult、AgentImprovementProposal、EvalCase、ActorFeedback | failed quality、rework、manual correction、blocked repeat、improvementProposalRefs、evalCaseRefs。 |
| 审计通知 | AuditLog、NotificationRecord | lastAuditAction、auditRefs、notificationRefs、投递状态和失败原因。 |
| 能力版本 | Agent / Skill / role spec / guide refs | 当前项目使用的公司级 Agent Team 版本、Skill 版本、EvalCase 版本和适用范围。 |

## 工作台视图

### 1. 任务事实总览

- 显示任务标题、状态解释、下一步责任人、下一步原因。
- Feature 缺 `requirementRefs` 标为当前缺口；旧任务缺字段标为历史缺口。
- `done` 但缺 TaskResult、证据或 tests/checks 时，不显示为完整闭环。

### 2. PM 调度与 worker 面板

- 展示 PM 派出的 worker 列表、角色、输入、边界和交付接收人。
- 每个 worker 必须有输出摘要、证据引用和 PM consolidation。
- PM consolidation 只能是接受、部分接受、拒绝、要求返工或转人工。

### 3. 来源与接收审查面板

- 展示任务来源类型、需求/缺陷/资料/研究问题/原因引用。
- 展示 ReceiverReview 决策：`accepted_for_work`、`accepted_with_assumptions`、`needs_rework`、`human_decision_required`。
- `accepted_with_assumptions` 必须显示假设；`needs_rework` 和 `human_decision_required` 必须显示问题。

### 4. 结果、证据与验收面板

- 展示 TaskResult、质量评价、规则评价、证据、检查、交接摘要。
- `waiting_acceptance` 必须显示验收人、验收策略和 Review/TaskResult 引用。
- 验收拒绝或要求修改时，必须显示返工任务或待创建返工任务的缺口。

### 5. 成长信号面板

- 展示本任务触发的 AgentImprovementProposal、EvalCase 草稿、Skill/角色规则更新建议。
- 区分项目级 `reuseScope: project` 和公司级 `reuseScope: company`。
- 对未沉淀的失败/返工显示 `learning loop gap`。

### 6. 双电脑项目视图

- 每台电脑只显示自己当前项目的任务队列、Runner/工作台上下文和本地执行状态。
- 公司级能力版本作为共享引用展示，不把两台电脑的任务放进同一个抢占队列。
- 当项目经验重复出现两次以上，提示知识工程 Agent 评估是否升级为公司级经验。

## 自动沉淀机制

### 触发条件

1. `TaskResult.qualityEvaluation.passed = false`。
2. ReceiverReview 选择 `needs_rework` 或 `human_decision_required`。
3. 人类或 PM 在验收门选择 `changes_requested` 或 `rejected`。
4. 同类阻塞在同项目或多项目重复出现。
5. 子 Agent 越过角色边界，或 PM 聚合非 PM 产物但缺少 owning Agent TaskResult provenance。
6. 人类明确指出流程、Skill、角色职责或交接标准需要沉淀。

### 沉淀产物

| 产物 | 默认状态 | 用途 |
| --- | --- | --- |
| AgentImprovementProposal | draft | 记录失败原因、影响角色、建议改进和复用范围。 |
| EvalCase | draft | 把失败、返工或人工纠偏转成回归用例。 |
| Skill / checklist 更新建议 | draft / review_required | 改进角色执行步骤、输入检查和输出格式。 |
| role spec / operating guide 更新建议 | review_required | 调整岗位职责、交接标准或调度规则。 |
| 项目经验 | observed / draft | 保留项目特定上下文，不默认升级为公司级知识。 |

### 晋级规则

- 只影响单个客户、仓库、环境或项目的经验，留在项目级。
- 影响多个项目、多个角色或多个员工的经验，进入公司级 Review。
- 项目级经验重复出现两次以上，知识工程 Agent 应提出公司级抽象建议。
- 涉及岗位、Skill、Workflow、调度规则、Agent Ring、知识政策的公司级更新，必须同步更新相关指南并通过 Review/审批。

## 与 ANOS-REQ-160 的关系

本方案是 ANOS-REQ-160 的短期 V1 融合落地口径，不替代原 PRD。

| ANOS-REQ-160 分期 | 原口径 | 本方案承接方式 |
| --- | --- | --- |
| V0 只读任务事实视图 | 看清任务事实、缺口、证据、验收和下一步。 | 作为融合工作台底座。 |
| V1 PM 调度子 Agent worker | 记录 PM-worker 契约、worker 输出和 PM 收敛。 | 作为短期主交付范围。 |
| V2 Agent 成长闭环 | AgentImprovementProposal、EvalCase、Skill/角色规则/工作流更新。 | 本版只做触发、展示、草稿沉淀和 Review 路由，不做全自动发布。 |
| 后续正式独立 Agent | 成熟 worker 逐步替代为正式独立 Agent。 | 本版保留迁移方向，但不作为上线前置条件。 |

## 验收标准

### P0

1. 任一活跃 ProjectTask 可打开融合事实视图，显示任务身份、来源、状态解释、责任人、结果证据、验收路由、成长信号和下一步。
2. 视图只读，不提供编辑、领取、改派、重试、验收、拒绝、关闭、写回知识等操作。
3. 不新增核心对象，不重写 Scheduler、Agent Ring、Runner claim/lease/heartbeat/finish 或 TaskResult 写回链路。
4. PM 调度 worker 时，能看到 worker role、输入、边界、允许动作、禁止动作、输出格式、证据要求和交付接收人。
5. Worker 输出必须由 PM 收敛；worker 结果不能直接显示为最终任务结论。
6. TaskResult 必须保留 `workSourceType`、`requirementRefs`、`defectRefs`、`acceptanceCriteriaRefs`、`receiverReviewRefs` 等追溯字段。
7. Feature 无需求引用、bugfix 无缺陷引用、ReceiverReview 打回、人类决策、done 缺结果/证据必须在工作台显示为缺口。
8. PM closeout、PM acceptance、release acceptance 或 final acceptance 必须有 `pmDeliveryGate` 或明确 `pmCloseoutScope: process_status_only`。

### P1

1. `accepted_with_assumptions` 必须展示假设，并要求后续 TaskResult 保留假设。
2. `needs_rework` 和 `human_decision_required` 必须展示问题、责任人和下一步。
3. 失败、返工、重复阻塞或人工纠偏能生成 AgentImprovementProposal 和 EvalCase 草稿。
4. 成长信号面板能区分项目级和公司级复用范围。
5. 两台电脑各自不同项目时，能看到各自项目任务事实，并显示共享 Agent 团队能力版本。

### 不通过条件

1. 只展示状态码，不解释下一步责任人和原因。
2. `done` 缺 TaskResult 或证据却显示为完整闭环。
3. PM 直接宣称非 PM 产物通过，但缺 owning Agent TaskResult provenance。
4. Worker 越权执行其他角色职责，工作台没有暴露边界问题。
5. 返工或失败只创建新任务，没有记录成长信号或沉淀缺口。
6. 把两台电脑纳入同项目抢任务或冲突解决范围。
7. 把未经 Review 的项目经验发布为公司级规则、Skill 或 verified 知识。
