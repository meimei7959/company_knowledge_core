---
type: ReviewRecord
title: ANOS-REQ-161 telemetry retention product requirement acceptance
description: Product Manager Agent acceptance and Architecture handoff for execution telemetry retention, closeout compaction, cleanup, protected references, and learning-signal promotion.
timestamp: "2026-06-23T11:43:15Z"
projectId: company-knowledge-core
reviewerAgent: agent.company.product-manager
status: accepted_with_assumptions
decision: accepted_for_architecture
requirementRefs:
  - ANOS-REQ-161
  - ANOS-REQ-160
taskRef: projects/company-knowledge-core/tasks/kt-anos-req-161-execution-telemetry-retention-requirement.md
receiverReviewRef: projects/company-knowledge-core/receiver-reviews/receiver-review.anos-req-161.product-requirement.md
acceptanceMatrixRef: docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md
prdRef: docs/product/ai-native-os/execution-telemetry-retention-prd.md
handoffTo: agent.company.architecture
auditRefs:
  - knowledge/audit/audit.20260623T114315Z-anos-req-161-product-requirement-acceptance.md
---

# Product Requirement Acceptance

## 接收结论

Product Manager Agent 接受 ANOS-REQ-161 产品需求包，decision 为 `accepted_with_assumptions`，并放行 Architecture Agent 进入技术方案。

接收理由：

1. PRD 已定义执行遥测保留的产品目标、分层、retention class、closeout compaction、cleanup dry-run/apply、保护规则、审计摘要和成长信号提升。
2. 验收矩阵覆盖 P0 行为：分类、覆盖写、timeline、closeout compaction、dry-run、apply、protected refs、批量 AuditLog、learning signal、metrics rollup。
3. 边界清楚：不引入外部日志平台作为 V0 前置，不重写 Scheduler / Runner / TaskResult / AuditLog 核心语义，不长期保存所有 raw telemetry。
4. 产品交接对象是 Architecture Agent，不是 Development Agent；研发必须等待技术方案和后续 ReceiverReview。

## 是否需要继续产品细化

不需要阻塞架构的产品细化。

保留给 Architecture 的轻量细化项：

- 明确数据落点、索引、幂等键、引用扫描边界和 batch summary schema。
- 明确 `TelemetryRetentionWorker` 或等价后台任务的触发方式、运行频率、失败重试和恢复策略。
- 明确 dry-run/apply 的 CLI 或 API 表面，以及哪些计数和 skipped reason 必须稳定输出。
- 明确 TTL 字段如何表达默认值和可配置性，但不得改变产品默认语义。

## Retention Class Table

| retentionClass | 数据例子 | 默认处理 | 产品验收口径 |
| --- | --- | --- | --- |
| `ephemeral` | raw heartbeat、重复 progress_update | 24 小时后删除 | 只服务当前可见性，不进入长期事实和 AuditLog 噪音。 |
| `hot_task` | 当前任务进展、临时 timeline raw | 任务完成后 7 天压缩 | closeout 后只保留关键 timeline 摘要和证据引用。 |
| `diagnostic` | error detail、tool/model raw usage、debug detail | 30 天聚合，90 天删除或归档 | 先聚合到 MetricsReport 或诊断摘要，再清理 raw。 |
| `evidence` | TaskResult evidence、testsOrChecks、outputRefs | 跟随 TaskResult 生命周期 | 受 TaskResult/验收保护，不被普通 cleanup 删除。 |
| `audit` | lease、权限、验收、人工纠偏、结果写入、清理摘要 | 长期保留 | 只记录权责事实和批量清理摘要，不记录普通 heartbeat/progress。 |
| `learning` | rejected、rework、质量门失败、AgentImprovementProposal、EvalCase | 长期保留 | 清理前必须判断提升或关联成长对象。 |
| `metrics` | token、耗时、成功率、错误率、重试率聚合 | 聚合长期保留，删除 raw 噪音 | raw 到期可清理，聚合趋势必须可查。 |

## 分层产品口径

| 层级 | 保留内容 | 退出 raw 的规则 | 验收重点 |
| --- | --- | --- | --- |
| Current State | runner last heartbeat、current task、current step、load、last error summary | upsert 覆盖写；旧 raw 短期保留 | 任务事实视图看到最新状态，不产生无限历史。 |
| Task Timeline | started、phase changed、blocked、recovered、tool evidence、result writeback | 重复 progress 压缩；生命周期内保留摘要 | 能解释任务如何走到当前结果。 |
| TaskResult | outputRefs、evidenceRefs、testsOrChecks、qualityEvaluation、terminalReason | 不清理；长期保留 | 交付真相和验收入口。 |
| Audit | lease、权限、验收、人工纠偏、结果写入、清理摘要 | 不为普通 heartbeat/progress 写审计 | 权责真相可追溯，噪音不污染 AuditLog。 |
| Metrics | token、耗时、成功率、错误率、重试率 | raw usage 到期聚合后清理 | 趋势、预算和容量判断仍可查。 |
| Learning Signal | rejected、rework、manual correction、quality gate failure、worker boundary violation | 清理前先提升或关联成长对象 | Agent 改进证据不被普通 cleanup 误删。 |

## Closeout Compaction

触发条件：

- TaskResult 写回。
- 任务进入 `done`、`failed`、`blocked` terminal 或 `waiting_acceptance`。

必须保留：

- 阶段变化、阻塞、恢复、证据引用、质量门结果、结果写回。
- TaskResult、AuditLog、human acceptance、verified knowledge、AgentImprovementProposal、EvalCase 及其必要证据。

必须压缩：

- 普通 progress raw。
- 重复 current-step updates。
- 与结果无关的短期 heartbeat/history noise。

## Cleanup Dry-Run / Apply

`dry-run` 必须先可用，且不修改数据。输出至少包含：

- `deleted` candidate count。
- `compacted` candidate count。
- `rolledUp` metrics/diagnostic count。
- `promoted` learning signal count。
- `archived` count。
- `skippedProtectedRefs` count and reason。
- `errors` count and reason。

`apply` 才允许执行删除、压缩、聚合、提升或归档。每次 apply 只能写一条批量 AuditLog 摘要，不能为每条删除制造审计噪音。

## Protected Refs

Cleanup 不得删除：

- TaskResult 和其 evidenceRefs / outputRefs / testsOrChecks 必要证据。
- AuditLog。
- human acceptance、ReviewRecord、仍在验收链中的交付物。
- verified knowledge、知识治理对象和被知识对象引用的必要证据。
- active lease、active task progress、unresolved blocker、open incident。
- AgentImprovementProposal、EvalCase 及其必要证据。
- 被 TaskResult、Audit、验收、知识、成长对象引用的数据。

## ANOS-REQ-161 覆盖

| Requirement | 产品验收口径 | 验收矩阵 |
| --- | --- | --- |
| ANOS-REQ-161-001 | 上报入口必须识别 retentionClass，并判断 Current State、Task Timeline、Audit、Learning Signal 路径。 | ANOS-161-AC-001 |
| ANOS-REQ-161-002 | heartbeat/current step/load/current task/last error summary 覆盖写，不无限追加。 | ANOS-161-AC-002 |
| ANOS-REQ-161-003 | TaskResult 写回或 terminal/waiting_acceptance 触发 closeout compaction。 | ANOS-161-AC-004 |
| ANOS-REQ-161-004 | 后台 worker 删除过期 ephemeral、压缩 hot_task、聚合 metrics/diagnostic、提升 learning、跳过保护引用。 | ANOS-161-AC-005, ANOS-161-AC-006, ANOS-161-AC-010 |
| ANOS-REQ-161-005 | dry-run 不修改数据；apply 才执行；输出可解释计数和原因。 | ANOS-161-AC-005, ANOS-161-AC-006 |
| ANOS-REQ-161-006 | 保护规则优先于 TTL 和 cleanup。 | ANOS-161-AC-007 |
| ANOS-REQ-161-007 | cleanup apply 写批量 AuditLog 摘要，不逐条写删除审计。 | ANOS-161-AC-008 |
| ANOS-REQ-161-008 | rejected/rework/manual correction/quality gate failure/worker boundary violation 等先判断成长提升，不被普通清理删除。 | ANOS-161-AC-009 |

补充覆盖：Task Timeline 阶段变化保留对应 ANOS-161-AC-003；Metrics 聚合长期保留对应 ANOS-161-AC-010。

## 明确不做

- 不实现 cleanup。
- 不写或修改代码。
- 不引入外部日志平台作为 V0 前置。
- 不重写 Scheduler / Runner / TaskResult / AuditLog 核心语义。
- 不把所有 raw telemetry 长期保存。
- 不把普通 heartbeat/progress 写 AuditLog。
- 不删除受 TaskResult/Audit/验收/知识/成长对象保护的数据。

## Architecture Handoff

Architecture Agent 下一步输出技术方案，必须回答：

1. 哪些对象或 read model 承载 Current State、Task Timeline raw/summary、retentionClass、TTL、protected refs、cleanup batch summary。
2. 上报入口如何分类 heartbeat、lease_update、progress_update、tool_usage、model_usage、result_writeback、error_report。
3. closeout compaction 如何由 TaskResult 写回、terminal 状态或 `waiting_acceptance` 触发。
4. dry-run/apply 的 CLI 或 API 如何设计，输出字段如何稳定供 Test Agent 验收。
5. protected reference 扫描如何覆盖 TaskResult、AuditLog、ReviewRecord、KnowledgeItem、AgentImprovementProposal、EvalCase、active lease、active task、blocker、incident。
6. MetricsReport 或等价统计如何保留长期聚合，同时删除 raw 噪音。
7. Learning Signal 如何提升到 AgentImprovementProposal / EvalCase 候选。
8. 哪些验收用例由 Development/Test 实现验证，哪些仅作为产品边界断言。

架构不得把外部日志平台、全量 raw telemetry 长存、普通 heartbeat AuditLog、核心语义重写作为 V0 前置方案。
