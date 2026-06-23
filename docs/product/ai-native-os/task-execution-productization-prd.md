---
type: ProductRequirementPackage
requirementId: ANOS-REQ-160
title: AI-native OS 任务执行产品化与 Agent 成长闭环优化需求
description: 以 ANOS-REQ-160 统一承载任务事实视图、PM 调度子 Agent worker、经验沉淀和能力升级闭环，先交付 V0 只读事实视图，再渐进跑通业务自运转和 Agent 自成长。
timestamp: "2026-06-23T07:45:45Z"
projectId: company-knowledge-core
ownerAgent: agent.company.product-manager
status: draft
phase: execution-productization-worker-learning-loop
scopeVersion: V0-to-V2
sourceBaseline:
  - docs/strategy/zhenzhi-ai-native-knowledge-system.md
  - docs/product/ai-native-os/phase-2-central-runner-observability-prd.md
  - docs/product/ai-native-os/phase-2-pm-control-lease-prd.md
  - docs/protocols/agent-workbench-integration-brief.md
  - docs/agent-team/company-agent-team-operating-guide.md
  - projects/company-knowledge-core/tasks/kt-os-self-improvement-pipeline.md
  - agents/agent.company.product-manager.md
  - docs/agent-team/product-manager-agent-role-and-skill-pack.md
relatedRequirements:
  - ANOS-REQ-160
acceptanceMatrixRef: docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md
updatedAt: "2026-06-23T08:10:00Z"
---

# AI-native OS 任务执行产品化与 Agent 成长闭环优化需求

## 融合结论

ANOS-REQ-160 作为统一需求，不再只表达“任务事实视图”，而是承载当前阶段 AI-native OS 的一条主线：

```txt
PM Agent 调度子 Agent worker
-> worker 完成架构 / 研发 / 测试 / 审查等角色工作
-> PM Agent 收敛结果并写回任务事实、TaskResult、证据和审计
-> 系统识别失败、阻塞、返工和人工纠偏
-> 生成 AgentImprovementProposal / EvalCase / skill 或角色规则更新
-> 下次 PM 调度时使用升级后的能力
```

本需求仍然坚持渐进交付。V0 先交付只读任务事实视图；V1 在同一事实口径上规范 PM 调度 worker 的记录和收敛；V2 将任务执行中的经验转成 Agent 能力升级闭环。

本需求不新增核心对象，不重写 Scheduler、Agent Ring、Runner claim/lease/heartbeat/finish、TaskResult 写回或验收执行链路。正式独立 Agent 继续作为未来成熟形态保留，但当前可交付版本优先采用 PM Agent 主控 + 子 Agent worker 执行 + 系统化经验沉淀。

## PRD 质量协议

| 工序 | 本轮结论 |
| --- | --- |
| 需求澄清器 | 第一性问题：用户为什么不信任当前任务闭环？答案是事实分散，任务状态不能直接解释结果、证据、责任人和下一步。 |
| 取证器 | 证据来自现有战略、工作台协议、Runner 可观测性、PM control lease PRD、产品经理 Agent 规则和任务运行契约；未做外部市场调研。 |
| 成案器 | 选择统一需求、分阶段交付：V0 只读事实视图，V1 PM-worker 调度闭环，V2 Agent 成长闭环。 |
| 反方审查器 | 反方风险：融合后被误做成大而全平台。修正：一个需求编号，一条主线，V0 不扩大实现面，V1/V2 只在 V0 事实基础上渐进。 |
| PRD 质量检查器 | 已覆盖用户、场景、目标、触发条件、系统响应、边界、异常、空状态和可测试验收标准。 |
| 交付包生成器 | 交付正式 PRD、验收矩阵、PM TaskResult 和 AuditLog，供架构 Agent 输出技术方案。 |

## 一句话目标

让用户打开任一 `ProjectTask` 时，能看懂任务执行闭环和能力成长闭环：任务是什么、为什么做、PM 调度了哪些 worker、谁负责、在哪里执行、当前状态代表什么、结果和证据在哪里、验收由谁处理、暴露了什么经验或能力缺口、下一步是什么。

## 背景判断

当前系统已有 `ProjectTask`、`AgentRunner`、`TaskResult`、`AgentRun`、`ReviewRecord`、`NotificationRecord`、`AuditLog`、PM Health、Runner 工作台和知识治理规则。可信度问题不是缺对象，而是现有对象没有被稳定组织成一个面向人的任务事实视图。

ANOS-REQ-160 的产品化优化方向正确，但如果只做事实视图，会解决“看不清任务”的问题，却没有完整回答用户真正关心的两个目标：业务角色能否自运转，以及 Agent 能否持续成长。因此本需求将“任务事实视图、PM 调度 worker、经验沉淀与能力升级”融合为同一条产品主线。

当前判断：正式独立 Agent 的对象和契约已经存在，但完整执行闭环尚未稳定跑通。早期不应强行让每个角色都成为正式独立 Agent。更稳的路径是先由 PM Agent 统一调度子 Agent worker，并把 worker 的输出、问题和经验外部化到系统资产里。这样既能交付业务闭环，也能为未来正式独立 Agent 积累可复用能力。

## 用户和场景

| 用户 | V0 要回答的问题 | 不在 V0 回答的问题 |
| --- | --- | --- |
| Project Owner | 任务现在处于什么状态？谁负责下一步？结果和证据在哪里？ | 是否自动改派、自动验收、自动修复执行链路。 |
| Product Manager Agent | 任务是否已经有可验收结果？需求和验收标准是否能被追溯？ | PM Health 是否重算项目健康。 |
| Architecture Agent | 需要基于哪些现有字段设计读模型和 UI/API 映射？ | 是否调整核心对象边界。 |
| Development Agent | V0 页面要读哪些字段、如何处理缺口和旧任务？ | 是否改 Scheduler、Runner 或 TaskResult 写入。 |
| Test Agent | 哪些状态、缺口、权限和旧数据场景必须验收？ | 是否签署产品最终验收。 |
| 子 Agent worker | 我被 PM 派去完成哪个角色工作？边界是什么？输出和证据交给谁？ | 是否拥有长期身份或独立任务队列。 |
| Agent 能力维护者 | 哪些失败、返工、人工纠偏应该升级为 skill / eval / role spec？ | 是否直接把未经验证的经验变成公司级规则。 |

## 运行模式判断

| 模式 | 本阶段定位 | 使用边界 |
| --- | --- | --- |
| PM Agent + 子 Agent worker | 当前默认交付模式。PM Agent 主控任务闭环，worker 承担专业执行。 | worker 可以临时并行，但输出必须被 PM 收敛到 TaskResult、证据、审计和改进项。 |
| 正式独立 Agent | 未来成熟形态。适合稳定角色、长期队列、可恢复执行和独立追责。 | 只有当最小任务闭环、AgentRun、TaskResult、审计和验收都稳定后，再逐步升级。 |
| 纯人工协调 | 兜底模式。用于高风险决策、验收、权限、安全和客户承诺。 | 不替代系统记录，人工纠偏也要沉淀为任务事实或改进提案。 |

## 分阶段范围

### V0：只读任务事实视图

本期必须做：

1. 提供单个 `ProjectTask` 的只读任务事实视图。
2. 任务事实视图只消费现有对象和字段，不创建新的核心对象类型。
3. 展示任务身份、需求来源、状态解释、责任人、Runner/Agent、执行环境、TaskResult、证据、验收、审计和下一步。
4. 对缺失字段给出可读缺口，不静默隐藏。
5. 对旧任务兼容显示 `legacy gap`，避免把历史数据缺口误判为新执行失败。
6. 对 `pending`、`waiting_runner`、`processing`、`blocked`、`waiting_acceptance`、`done`、`failed` 提供用户解释和下一步。
7. 权限和敏感信息按现有策略脱敏，不暴露 secret、token、完整本地隐私路径或未授权证据内容。
8. 输出可交给架构、研发、测试的验收矩阵。
9. 如果任务由 PM 调度子 Agent worker 完成，V0 至少展示 worker 角色、输入摘要、输出摘要、证据引用和 PM 收敛结论；缺失时标记为 worker trace gap。

本期明确不做：

1. 不新增 `TaskFactView`、`ExecutionFact`、`TaskTimeline` 等核心对象。
2. 不改写 `ProjectTask.status` 枚举，不新增执行状态机。
3. 不重写 Scheduler、Agent Ring、Runner claim、lease、heartbeat、finish 或 TaskResult 写回链路。
4. 不提供任务编辑、领取、改派、重试、验收、拒绝或关闭操作。
5. 不做 PM Health 重构；V0 只为 V1 提供可复用的事实口径。
6. 不做历史任务数据迁移；仅在视图层标注旧字段缺口。
7. 不改变 Knowledge Review、Human Acceptance、AuditLog 或 NotificationRecord 契约。
8. 不把任务事实视图作为独立真源写回知识库。
9. 不要求 worker 拥有长期记忆或独立任务队列。
10. 不把正式独立 Agent 作为 V0 前置条件。

### V1：PM 调度子 Agent worker 闭环

V1 在 V0 事实视图基础上补齐 PM 调度 worker 的产品契约：

1. PM Agent 能明确记录本任务需要哪些 worker 角色，例如 Architecture、Development、Test、Review。
2. 每个 worker 都有清晰的输入、边界、允许动作、禁止动作、输出格式和证据要求。
3. worker 的结果必须被 PM Agent 收敛，不能直接替代 PM 的任务结论。
4. Development worker 可以实现；Test worker 可以准备/执行验收和风险检查，但不能抢研发文件或自行宣布产品验收通过。
5. worker 输出进入 TaskResult、Review、Audit、Notification 或相关 evidenceRefs，不只停留在聊天上下文。
6. 任务事实视图能显示 worker 参与记录和 PM 收敛状态。
7. Development worker 必须加载 `development-engineering-quality-gate`，并在 handoff 前运行 `tool.development-engineering-quality-toolkit`。
8. PM Agent 不得把缺少研发质量门证据的 Development worker 输出推进到完整闭环。

### V2：Agent 经验沉淀和能力升级闭环

V2 在 V1 的 worker 记录基础上补齐自成长：

1. 被拒绝、返工、阻塞、反复失败、人工纠偏或低质量输出必须触发改进候选。
2. 改进候选需要归因到角色能力、工具能力、流程契约、上下文准备、验收标准或知识缺口。
3. 有复用价值的问题生成 `AgentImprovementProposal`。
4. 重要改进必须生成或更新 `EvalCase`，再修改 skill、role spec、workflow 或 operating guide。
5. skill / role spec / workflow 更新必须有验证、版本、审计和回滚路径。
6. 下次 PM 调度同类 worker 时，能引用升级后的能力，而不是依赖临时上下文记忆。

## 事实视图字段

V0 事实视图是读模型或 UI projection，不是核心对象。字段必须从现有对象解析，页面可按区块呈现。

| 区块 | 必显事实 | 缺失处理 |
| --- | --- | --- |
| 任务身份 | taskId、title、projectId、workSourceType、priority、createdAt、updatedAt | 缺关键身份字段时显示 `missing task identity`。 |
| 需求来源 | requirementRefs、sourceMaterialRefs、acceptanceCriteriaRefs、receiverReviewRefs | 新 feature 任务缺 requirementRefs 标为 `current gap`；旧任务标为 `legacy gap`。 |
| 当前状态 | raw status、用户解释、lastUpdated、nextStepOwner、nextStepReason | 不只显示状态码；缺下一步责任人时标 `missing next owner`。 |
| 执行责任 | assignedAgent、executorAgent、assignedRunner、leaseOwner、runnerId、executionHost label | 缺 Runner 不等于失败，按状态解释等待或遗留缺口。 |
| 执行过程 | currentPhase、lastHeartbeatAt、startedAt、completedAt、AgentRun refs | 没有 AgentRun 时显示 `not recorded`，不伪造时间线。 |
| worker 参与 | worker role、worker input、boundary、output summary、evidenceRefs、PM consolidation | 缺 worker 记录时显示 `worker trace gap`；没有使用 worker 时显示 `not applicable`。 |
| 结果证据 | resultRef、result status、summary、outputRefs、evidenceRefs、testsOrChecks | done 缺 resultRef 或 evidenceRefs 时必须标 `result evidence gap`。 |
| 质量规则 | qualityEvaluation、commonRulesEvaluation、operatingRuleRefs | 缺规则评价时显示缺口；不得默认 passed。 |
| 验收 | acceptancePolicy、acceptanceStatus、acceptanceOwner、reviewRefs | waiting_acceptance 必须显示验收人或验收路由缺口。 |
| 成长信号 | rejected、rework、manual correction、blocked repeat、improvementProposalRefs、evalCaseRefs | 有问题但未生成改进候选时显示 `learning loop gap`。 |
| 审计通知 | auditRefs、notificationRefs、lastAuditAction | 没有审计引用时显示 `audit gap`，不隐藏。 |

## 状态解释

| raw status | 用户解释 | V0 必须显示的下一步 |
| --- | --- | --- |
| pending | 任务已创建，还没进入执行。 | 谁需要补条件、分配 Runner 或确认任务。 |
| waiting_runner | 任务正在等待可用 Runner。 | 等待原因：能力、权限、在线状态、租约或匹配条件。 |
| processing | Runner 或 Agent 正在执行。 | executorAgent、runner/host、当前阶段和最近心跳。 |
| blocked | 任务无法继续。 | 阻塞原因、owner、恢复动作或需要人工介入。 |
| waiting_acceptance | 任务已有结果，等待验收。 | acceptanceOwner、验收标准、resultRef 和 evidenceRefs。 |
| done | 任务完成。 | resultRef、证据、验收记录、完成时间；缺证据时不得显示为完整闭环。 |
| failed | 执行失败。 | 失败原因、可否重试、下一责任人和相关审计。 |
| unknown | 状态无法识别。 | 展示原始值、数据来源和需研发/数据修复的缺口。 |

## 功能需求

### ANOS-REQ-160-V0-001 任务事实视图入口

用户从任务列表、PM/项目检查、Runner 相关视图或结果引用进入某个任务时，能打开该任务的事实视图。入口可以是现有页面链接、CLI 输出引用或工作台详情页，不要求 V0 新建导航体系。

### ANOS-REQ-160-V0-002 只读事实展示

视图不得提供编辑、领取、改派、重试、验收、拒绝、关闭、写回知识或修改证据的操作。任何行动按钮如需保留，只能跳到现有链路或显示不可用状态，不能在 V0 实现新写链路。

### ANOS-REQ-160-V0-003 现有对象映射

所有展示事实必须可追溯到现有对象或文件引用，包括 `ProjectTask`、`AgentRunner`、`TaskResult`、`AgentRun`、`ReviewRecord`、`NotificationRecord`、`AuditLog`、`SourceMaterial` 和 acceptance criteria。不能通过新增核心对象补事实。

### ANOS-REQ-160-V0-004 缺口显性化

字段缺失、引用不存在、状态与结果不一致、验收缺 owner、done 缺证据、waiting_runner 缺等待原因等情况必须显示为缺口。缺口分类为 `current gap`、`legacy gap` 或 `not applicable`。

### ANOS-REQ-160-V0-005 旧任务兼容

历史任务缺少新契约字段时，页面仍可打开，并展示已有事实和 `legacy gap`。不得因为旧任务缺少字段而白屏、崩溃或展示“全部完成”。

### ANOS-REQ-160-V0-006 状态解释和下一步

每个 raw status 必须配用户解释和下一步。下一步至少包括责任角色、需要动作和事实依据；无法判断时显示 `next step unknown` 与缺失原因。

### ANOS-REQ-160-V0-007 证据和验收可见

有 TaskResult 的任务必须展示 resultRef、summary、outputRefs、evidenceRefs、testsOrChecks、qualityEvaluation、commonRulesEvaluation 和 acceptancePolicy。waiting_acceptance 必须展示验收 owner 或验收路由缺口。

### ANOS-REQ-160-V0-008 权限和敏感信息

视图不得泄露 secret、token、密码、完整敏感本地路径、未授权证据内容或不可公开的原始材料。权限不足时展示引用、类型、脱敏标题和访问限制说明。

### ANOS-REQ-160-V0-009 架构交接

本 PRD 完成后，由 Architecture Agent 输出技术方案，明确读模型来源、字段映射、UI/API 承载方式、权限策略和不改写执行链路的实现边界。Development Agent 不直接按本 PRD 开工。

### ANOS-REQ-160-V1-001 PM worker 调度契约

PM Agent 调度 worker 时，必须记录 worker role、任务输入、边界、允许动作、禁止动作、期望输出、证据要求和交付接收人。该记录可以进入 TaskResult、Audit、Review 或任务事实视图可解析的现有字段，不新增核心对象。

### ANOS-REQ-160-V1-002 worker 输出收敛

worker 输出不得直接等同于最终任务结论。PM Agent 必须对 worker 输出做收敛：接受、部分接受、拒绝、要求返工或转人工，并将收敛结论写入任务结果或审计。

### ANOS-REQ-160-V1-003 worker 权限边界

不同 worker 的动作边界必须清晰。Development worker 可执行实现；Test worker 可准备/执行测试与风险检查；Architecture worker 可审查结构和方案；Review worker 可指出风险。验收通过、知识发布、权限变更和跨团队规则仍按既有 Review/Human Acceptance 契约。

### ANOS-REQ-160-V1-004 Development worker 工程质量门

Development worker 在实现前必须加载研发工程质量 skill，声明变更范围、高风险文件和预期检查；实现后必须运行研发质量工具，输出 pass/warn/fail 证据。失败时不得直接 handoff 为完成，只能 repair、route to Architecture/Test/PM，或记录明确 blocker。

### ANOS-REQ-160-V1-005 大文件和高风险文件控制

当任务触及 `zhenzhi_knowledge/core.py`、`zhenzhi_knowledge/cli.py`、`zhenzhi_knowledge/server.py`、`zhenzhi_knowledge/feishu.py` 或 Scheduler / Runner / TaskResult / Audit / Review / PM lease / permission / index 路径时，必须有架构审查证据或明确架构 handoff。新增逻辑优先进入清晰模块边界，不继续堆叠到 god file。

### ANOS-REQ-160-V2-001 改进候选识别

当任务出现低质量输出、验收拒绝、重复返工、人工纠偏、阻塞恢复或 worker 越界时，系统必须能把该事件标记为改进候选，并关联 taskId、role、worker output、PM 收敛结论和证据。

### ANOS-REQ-160-V2-002 AgentImprovementProposal 生成

有复用价值的改进候选必须生成或关联 `AgentImprovementProposal`，说明问题归因、影响角色、建议修改、复用范围、风险和验证方式。

### ANOS-REQ-160-V2-003 eval + skill rollout

Agent 能力升级不得只靠写经验。关键改进必须生成或更新 eval case，通过验证后再更新 skill、role operating spec、workflow 或 guide，并写审计和版本记录。

## 空状态和异常

| 场景 | 展示要求 |
| --- | --- |
| 找不到任务 | 显示任务不存在或无权限，保留请求 taskId，不暴露内部异常栈。 |
| 引用对象不存在 | 展示缺失引用和来源字段，标记 `dangling ref`。 |
| 权限不足 | 展示可见元信息和访问限制，不展示敏感内容。 |
| 字段格式不兼容 | 展示原始字段名、缺口类型和需要修复的数据契约。 |
| 状态未知 | 展示 raw status、来源对象和 `unknown status`。 |
| 数据加载失败 | 展示可重试提示和错误来源，不改变任务状态。 |

## 成功指标

1. 研发和测试能用验收矩阵逐项验证 V0。
2. 用户无需阅读多个治理对象即可判断单个任务的执行事实。
3. `done` 缺证据、`waiting_runner` 缺原因、`waiting_acceptance` 缺 owner 等关键假闭环能被直接看见。
4. V0 实现不引入新核心对象，不修改执行写链路。

## 待决策事项

| 决策项 | 当前建议 | 决策 owner |
| --- | --- | --- |
| V0 承载形态 | 优先复用现有工作台任务详情或只读 API/CLI 输出，不建新产品模块。 | Architecture Agent |
| 字段映射来源 | 由架构方案列出字段到现有对象的映射表。 | Architecture Agent |
| 权限策略 | 继承现有材料、审计、结果访问策略；敏感值只显示脱敏引用。 | Architecture Agent + Security/Owner |
| worker 记录落点 | 优先复用 TaskResult、Audit、Review 和 evidenceRefs；不新增核心对象。 | Architecture Agent |
| 改进候选触发阈值 | 先覆盖验收拒绝、重复返工、人工纠偏和阻塞恢复；低风险经验可后续扩展。 | Product Manager Agent |
| V1 是否让 PM Health 消费事实视图 | V0 不做，仅保留后续候选。 | PM Agent |

## 验收入口

正式验收矩阵见：

- `docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md`

## 交付边界

本 PRD 是产品需求细化和验收定义，不是技术方案、设计稿、研发实现或测试报告。后续顺序为：

```txt
Product Manager Agent integrated PRD
-> Architecture Agent technical solution for V0
-> Development Agent V0 implementation
-> Test Agent V0 validation
-> Product Manager Agent V0 acceptance
-> V1 PM-worker orchestration requirement refinement
-> V2 Agent learning loop requirement refinement
-> human acceptance when required
```
