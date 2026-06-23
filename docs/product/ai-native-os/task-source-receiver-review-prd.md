---
type: ProductRequirementPackage
title: 任务来源模型、缺陷对象与接收审查机制产品需求
description: 定义 ProjectTask/KnowledgeTask 的任务来源追溯、Defect 缺陷对象、ReceiverReview 下游接收审查，以及 CLI/API/模板/Skill/健康检查/测试接入验收口径。
timestamp: "2026-06-23T07:30:00Z"
projectId: company-knowledge-core
ownerAgent: agent.company.product-manager
status: draft
phase: phase-2
sourceBaseline:
  - docs/product/ai-native-os/prd.md
  - docs/product/ai-native-os/requirements.md
  - docs/product/ai-native-os/agent-collaboration-contract.md
  - zhenzhi_knowledge/core.py
relatedRequirements:
  - ANOS-REQ-030
  - ANOS-REQ-033
  - ANOS-REQ-051
  - ANOS-REQ-052
  - ANOS-REQ-060
  - ANOS-REQ-061
  - ANOS-REQ-063
  - ANOS-REQ-070
  - ANOS-REQ-110
updatedAt: "2026-06-23T07:30:00Z"
---

# 任务来源模型、缺陷对象与接收审查机制产品需求

## 一句话目标

让每个任务都能说清楚“为什么存在、来自哪里、下游能不能接着做”，并把这个判断落到可校验对象、CLI/API、模板、Skill、项目健康检查和自动化测试里。

## 背景

AI Native Agent 团队的任务链路已经具备项目、任务、结果、Agent 分工和调度能力，但上游交付物到下游开工之间仍缺一个稳定门禁。

典型风险：

- 产品经理输出需求后，架构师直接写技术方案；如果需求目标偏、信息缺、验收口径不清，研发和测试会沿着错误方向推进。
- 研发任务无法稳定追到需求，测试无法通过任务找到原始需求或缺陷。
- Bugfix 任务常常来自测试失败、线上问题或审计发现，未必能绑定需求，但必须能绑定 Defect。
- 下游 Agent 接收上游交付物时，没有标准化记录说明“接受、带假设接受、打回返工、需要人类决策”。

本需求补齐三层机制：任务来源模型、Defect 缺陷对象、ReceiverReview 接收审查对象。

## 产品原则

1. 所有项目任务必须有来源：任务不能只说“要做什么”，还要说“为什么要做”。
2. Feature 必须追需求：功能开发任务必须绑定 `requirementRefs`。
3. Bugfix 必须追缺陷：缺陷修复任务必须绑定 `defectRefs`，允许没有需求。
4. 下游先审查再开工：架构、设计、研发、测试等下游 Agent 接收上游交付物前，必须产出 `ReceiverReview`。
5. 审查结果必须可执行：结果只能落在四类 decision 中，并直接决定继续、带假设继续、返工或找人决策。
6. 规则必须进系统：CLI/API、模板、Skill、项目健康检查、测试都要接入，不能只停留在文档。

## 范围

### 本期必须实现

- ProjectTask / KnowledgeTask 新增并持久化任务来源字段。
- Feature / bugfix / research / knowledge_ingest / maintenance 等任务来源规则进入校验。
- 新增 Defect 对象，承接 bugfix 来源和回归证据。
- 新增 ReceiverReview 对象，承接下游接收审查。
- TaskResult 写回时继承核心追溯字段。
- CLI 支持任务来源、缺陷创建、缺陷修复任务创建、接收审查创建。
- API 支持任务来源字段、缺陷对象、接收审查对象。
- 项目健康检查暴露来源追溯和接收审查风险。
- 模板、Skill、岗位规则更新。
- 自动化测试覆盖正向和失败路径。

### 本期不做

- 不强制所有 bugfix 都绑定需求；bugfix 的最低追溯对象是 Defect。
- 不让 ReceiverReview 替代产品验收、测试验收或人类最终验收；它是下游开工前的输入质量门禁。
- 不把接收审查做成纯人工流程；Agent 必须能自动产出并被系统校验。
- 不要求历史任务一次性全部补齐；历史迁移可通过健康检查暴露并分批修复。

## 任务来源模型

ProjectTask / KnowledgeTask 必须支持以下字段：

| 字段 | 用途 | 要求 |
| --- | --- | --- |
| `workSourceType` | 任务来源类型。 | 必填或可由旧数据推断；新任务必须显式写入。 |
| `requirementRefs` | 需求文档或需求编号引用。 | Feature 必填。 |
| `requirementObjectRefs` | 结构化需求对象引用。 | 有结构化对象时填写。 |
| `acceptanceCriteriaRefs` | 验收标准引用。 | Feature 推荐填写；高风险任务应填写。 |
| `defectRefs` | 缺陷编号或缺陷文件引用。 | Bugfix 必填。 |
| `defectObjectRefs` | 结构化 Defect 对象引用。 | 有 Defect 对象时填写。 |
| `incidentRefs` | 事故、故障或异常引用。 | 来自事故恢复时填写。 |
| `operationRefs` | 运维操作、readiness、部署记录引用。 | 运维或维护任务填写。 |
| `knowledgeTaskRefs` | 关联知识任务引用。 | 知识加工或知识依赖任务填写。 |
| `researchQuestion` | 研究问题。 | Research 至少填写研究问题、资料或预期输出之一。 |
| `sourceReason` | 任务存在原因。 | 对非 feature / bugfix 任务尤为重要。 |
| `receiverReviewRefs` | 下游接收审查引用。 | 下游角色接收上游后写入。 |

### `workSourceType` 枚举

| 类型 | 含义 | 最低追溯要求 |
| --- | --- | --- |
| `feature` | 来自产品需求、功能需求、验收标准的功能建设。 | 必须有 `requirementRefs`。 |
| `bugfix` | 来自测试失败、用户反馈、线上缺陷、审计发现的修复。 | 必须有 `defectRefs`；可以没有 `requirementRefs`。 |
| `project_setup` | 项目初始化、环境准备、团队建设、工作流搭建。 | 必须有 `sourceReason` 或项目初始化来源。 |
| `research` | 调研、方案探索、可行性验证。 | 至少有 `researchQuestion`、资料来源或预期输出。 |
| `knowledge_ingest` | 文档、会议、资料、外部素材进入知识系统。 | 至少有资料来源引用。 |
| `maintenance` | 运维、重构、清理、治理、readiness、非需求型维护。 | 至少有 `sourceReason`、资料来源或预期输出。 |

### 关键校验规则

1. 新建 feature 任务时，如果没有 `requirementRefs`，系统必须拒绝或健康检查标红。
2. 新建 bugfix 任务时，如果没有 `defectRefs`，系统必须拒绝或健康检查标红。
3. Bugfix 可以没有 `requirementRefs`；系统不得因为 bugfix 无需求而拒绝。
4. Research 任务必须能说明研究问题、输入资料或预期输出。
5. Knowledge ingest 任务必须能追到资料来源。
6. Maintenance 任务必须能说明原因、来源或预期输出。
7. TaskResult 必须继承任务上的 `workSourceType`、`requirementRefs`、`defectRefs`、`acceptanceCriteriaRefs`、`receiverReviewRefs`，保证结果可追溯。

## Defect 对象

Defect 用于承接 bugfix 来源。它不是需求对象，也不强制依赖需求。

### 字段

| 字段 | 用途 | 要求 |
| --- | --- | --- |
| `defectId` | 缺陷唯一标识。 | 必填。 |
| `projectId` | 所属项目。 | 必填。 |
| `reporter` | 发现者，可为测试 Agent、用户、审计或系统。 | 必填。 |
| `severity` | 严重程度。 | 必填，需可用于排序。 |
| `status` | 缺陷状态。 | 必填。 |
| `requirementRefs` | 关联需求。 | 可选。 |
| `sourceTaskRef` | 发现缺陷的任务。 | 有则填写。 |
| `sourceResultRef` | 发现缺陷的 TaskResult。 | 有则填写。 |
| `evidenceRefs` | 失败日志、截图、测试报告、审计记录等证据。 | 必填或由创建入口要求至少一项证据/说明。 |
| `expectedBehavior` | 期望表现。 | 必填。 |
| `actualBehavior` | 实际表现。 | 必填。 |
| `reproductionSteps` | 复现步骤。 | 必填；不可复现时必须说明原因。 |
| `fixTaskRefs` | 修复任务引用。 | 创建修复任务后回填。 |
| `regressionEvidenceRefs` | 回归证据。 | 缺陷进入 fixed/closed 前必须有。 |

### 状态

| 状态 | 含义 |
| --- | --- |
| `triaged` | 已确认并进入分流。 |
| `in_progress` | 修复中。 |
| `fixed` | 已修复，等待或已有回归证据。 |
| `regression_required` | 必须回归验证。 |
| `reopened` | 回归失败或问题复现。 |
| `closed` | 修复和回归均完成。 |

### 产品规则

- 测试 Agent 发现实现缺陷时，应创建 Defect，再创建 bugfix 任务。
- `create_bugfix_task` 创建的任务必须写 `workSourceType=bugfix` 和对应 `defectRefs`。
- Defect 有需求引用时，系统应展示“影响需求”；没有需求引用时，展示“缺陷来源”，不得把它视为非法。
- Defect 状态为 `fixed` 但没有 `regressionEvidenceRefs` 时，项目健康检查必须提示风险。

## ReceiverReview 对象

ReceiverReview 是下游 Agent 接收上游交付物前的输入质量门禁。

### 字段

| 字段 | 用途 | 要求 |
| --- | --- | --- |
| `reviewId` | 审查唯一标识。 | 必填。 |
| `projectId` | 所属项目。 | 必填。 |
| `upstreamRef` | 上游交付物引用。 | 必填。 |
| `receiverAgent` | 下游接收方 Agent。 | 必填。 |
| `reviewerAgent` | 执行审查的 Agent。 | 必填，通常等于接收方。 |
| `decision` / `status` | 审查结论。 | 必须使用四类枚举之一。 |
| `artifactRefs` | 被审查的文档、任务或结果。 | 必填。 |
| `checklist` | 按岗位输入标准检查的条目。 | 必填。 |
| `issues` | 问题列表。 | `needs_rework` / `human_decision_required` 必填。 |
| `assumptions` | 继续工作的明确假设。 | `accepted_with_assumptions` 必填。 |

### 决策枚举

| 决策 | 何时使用 | 后续动作 |
| --- | --- | --- |
| `accepted_for_work` | 输入完整、目标清楚、验收口径明确，下游可以直接开工。 | 继续下游任务。 |
| `accepted_with_assumptions` | 输入可继续，但存在明确、可管理、已记录的假设。 | 继续下游任务；TaskResult 必须保留假设。 |
| `needs_rework` | 输入缺关键信息、方向不合理、质量不足或无法支撑下游工作。 | 打回上游返工；不得继续正式下游实现。 |
| `human_decision_required` | 存在范围、优先级、责任、风险或验收口径冲突，需要人类决策。 | 暂停下游正式开工，创建人工决策事项。 |

### 决策字段规则

1. `needs_rework` 必须写 `issues`。
2. `human_decision_required` 必须写 `issues`。
3. `accepted_with_assumptions` 必须写 `assumptions`。
4. `accepted_for_work` 不应有阻断级 `issues`。
5. 下游 Agent 必须按自己的输入验收标准检查，不能随机泛化审查。
6. ReceiverReview 必须能被任务、TaskResult 或健康检查引用。

## 各岗位接收审查标准

| 接收方 | 上游输入 | 必查项 |
| --- | --- | --- |
| 架构师 Agent | 产品需求 / PRD / 需求树 / 验收标准。 | 目标清楚、范围可实现、约束明确、验收标准可转成技术方案、缺信息已列出。 |
| 设计 Agent | 信息架构 / 页面需求 / 用户场景 / 设计目标。 | 页面目标、用户角色、关键流程、内容层级、可读性和交互约束明确。 |
| 研发 Agent | 技术方案 / 设计规范 / 任务包。 | 需求可追溯、方案边界明确、接口/数据/状态/错误处理清楚、测试入口明确。 |
| 测试 Agent | 研发交付 / TaskResult / 需求和验收标准。 | 可找到原始需求或缺陷、测试范围明确、验收标准可执行、证据入口存在。 |
| 产品经理 Agent | 架构/设计/研发/测试交付物。 | 是否满足产品目标、用户体验、范围边界和验收口径。 |
| 项目经理 Agent | 各岗位交付物和 ReceiverReview。 | 是否允许进入下一环节、是否需要返工或人类决策、任务链路是否闭环。 |

## CLI 需求

### `task create`

必须新增或扩展参数：

- `--work-source-type`
- `--requirement-ref`
- `--defect-ref`
- `--source-reason`

验收口径：

- 创建 feature 任务无 `--requirement-ref` 时失败，并提示“功能任务必须关联需求”。
- 创建 bugfix 任务无 `--defect-ref` 时失败，并提示“缺陷修复任务必须关联缺陷”。
- 创建 bugfix 任务有 `--defect-ref`、无 `--requirement-ref` 时成功。
- 创建 research / knowledge_ingest / maintenance 时，缺少最低来源说明要失败或进入健康风险。

### `defect create`

必须支持创建 Defect，至少接收：

- 项目、报告人、严重程度、期望表现、实际表现、复现步骤、证据引用、可选需求引用。

### `defect create-fix-task`

必须基于 Defect 创建 bugfix 任务：

- 自动写 `workSourceType=bugfix`。
- 自动写 `defectRefs`。
- 允许 `requirementRefs` 为空。
- 创建后回填或关联 `fixTaskRefs`。

### `receiver-review create`

必须支持创建 ReceiverReview：

- 指定项目、上游引用、接收方 Agent、审查方 Agent、decision/status、artifactRefs、checklist、issues、assumptions。
- 对四类 decision 执行字段规则。

## API 需求

### `/v0/tasks`

- 创建/更新任务时支持任务来源字段。
- 服务端执行与 CLI 一致的来源校验。
- 返回任务详情时展示 `workSourceType` 和追溯字段。

### `/v0/defects`

- 支持创建、查询 Defect。
- 支持从 Defect 创建修复任务，或暴露给 CLI 调用同一能力。

### `/v0/receiver-reviews`

- 支持创建、查询 ReceiverReview。
- 服务端执行 decision 字段规则。
- 支持按任务、上游引用、接收方 Agent 查询。

## 模板需求

必须更新或新增：

- `templates/project-task.md`：增加 Work Source 区块和来源字段。
- `templates/task-result.md`：增加继承后的追溯字段。
- `templates/defect.md`：新增 Defect 模板。
- `templates/receiver-review.md`：新增 ReceiverReview 模板。

模板必须使用中文说明字段含义，允许保留代码字段名。

## Skill 与岗位规则需求

| 岗位 | 必须更新 |
| --- | --- |
| 项目经理 Agent | 拆任务、派任务、返工任务、维护任务时必须声明 `workSourceType`；feature 必须绑定需求；bugfix 必须来自 Defect；进入下一岗位前检查 ReceiverReview。 |
| 产品经理 Agent | 输出需求、PRD、验收标准时必须给 feature 任务提供可追溯需求引用和验收标准引用。 |
| 架构师 Agent | 接收产品交付物前必须产出 ReceiverReview；未接受不得写正式技术方案。 |
| 设计 Agent | 接收页面/用户场景/产品输入前必须产出 ReceiverReview；重点检查人能看懂、流程清楚、设计输入完整。 |
| 研发 Agent | 接收技术方案/设计/任务包前必须产出 ReceiverReview；需要返工时不得直接开发。 |
| 测试 Agent | 接收研发交付前必须产出 ReceiverReview；发现缺陷时创建 Defect，bugfix 不强绑 Requirement。 |

## 项目健康检查

健康检查必须暴露以下风险：

| 风险 | 说明 |
| --- | --- |
| feature 任务无需求 | `workSourceType=feature` 但缺 `requirementRefs`。 |
| bugfix 任务无缺陷 | `workSourceType=bugfix` 但缺 `defectRefs`。 |
| bugfix fixed 但无回归证据 | Defect 状态为 `fixed` 或 `closed` 前缺 `regressionEvidenceRefs`。 |
| ReceiverReview 打回 | `decision=needs_rework`，必须显示上游、接收方、问题。 |
| ReceiverReview 需要人类决策 | `decision=human_decision_required`，必须显示需要决策的问题。 |
| 带假设继续 | `decision=accepted_with_assumptions`，必须显示假设，后续 TaskResult 需保留。 |
| TaskResult 追溯断裂 | TaskResult 缺少从任务继承的核心追溯字段。 |

## 测试验收标准

必须新增测试覆盖：

1. Feature 任务无 `requirementRefs` 时校验失败。
2. Bugfix 任务无 `defectRefs` 时校验失败。
3. Bugfix 有 Defect、无 Requirement 时校验通过。
4. Research / knowledge_ingest / maintenance 缺最低来源说明时能被拒绝或健康检查暴露。
5. ReceiverReview `needs_rework` 无 `issues` 时校验失败。
6. ReceiverReview `human_decision_required` 无 `issues` 时校验失败。
7. ReceiverReview `accepted_with_assumptions` 无 `assumptions` 时校验失败。
8. TaskResult 写回继承 `workSourceType`、`requirementRefs`、`defectRefs`、`acceptanceCriteriaRefs`、`receiverReviewRefs`。
9. 项目健康检查能看到 feature 无需求、bugfix 无缺陷、ReceiverReview 打回、人类决策、Defect fixed 无回归证据。
10. CLI 与 API 的任务创建、Defect 创建、bugfix 任务创建、ReceiverReview 创建路径一致。

## 发布级验收口径

本机制只有同时满足以下条件，才算产品验收通过：

- 数据模型字段存在并能持久化。
- `validate_bundle` 或等价仓库校验接入任务来源、Defect、ReceiverReview 规则。
- TaskResult 写回保留任务来源和接收审查追溯。
- CLI 与 API 均可创建并校验相关对象。
- 模板和岗位 Skill 均已更新。
- 项目健康检查能把风险讲清楚，不能只输出内部字段名。
- 自动化测试覆盖正向、拒绝、返工和健康检查路径。
- 下游 Agent 的正式任务产物中可以看到 ReceiverReview 引用，证明流程真在跑。

## 交付顺序建议

1. 架构 Agent 基于本 PRD 输出技术方案，确认模型、校验、API、CLI 和健康检查接入点。
2. 研发 Agent 实现模型、校验、写回继承、CLI/API、模板和 Skill 改造。
3. 测试 Agent 按验收标准做全链路测试。
4. 产品经理 Agent 验收是否满足任务来源追溯和接收审查口径。
5. 项目经理 Agent 确认流程可持续运转，并将本机制纳入后续任务编排。
