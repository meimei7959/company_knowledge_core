---
type: ProductRequirementPackage
requirementId: ANOS-REQ-161
title: AI-native OS 执行遥测保留与后台清理机制
description: 定义 Runner/worker 进展、心跳、工具/模型使用、错误、结果写回等执行遥测的分级、保留、压缩、归档、删除和审计策略，保障业务闭环、任务事实视图和 Agent 成长闭环，同时避免中枢沉积过期冗余数据。
timestamp: "2026-06-23T10:05:00Z"
projectId: company-knowledge-core
ownerAgent: agent.company.product-manager
status: draft
phase: telemetry-retention
scopeVersion: V0
sourceBaseline:
  - docs/product/ai-native-os/phase-2-central-runner-observability-prd.md
  - docs/product/ai-native-os/task-execution-productization-prd.md
  - docs/product/ai-native-os/agent-team-growth-and-task-fact-prd.md
  - docs/schemas/core-objects.md
relatedRequirements:
  - ANOS-REQ-161
  - ANOS-REQ-160
  - ANOS-REQ-160-FUSION-V1
acceptanceMatrixRef: docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md
updatedAt: "2026-06-23T10:05:00Z"
---

# AI-native OS 执行遥测保留与后台清理机制

## 一句话目标

让所有 Runner / worker 可以向中枢上报必要进展，但中枢只长期保存业务事实、责任事实、交付事实、审计事实和成长信号；普通运行噪音按策略覆盖、压缩、聚合、归档或删除。

## 背景

现有 Phase 2 设计要求 Runner 上报 heartbeat、lease_update、progress_update、tool_usage、model_usage、result_writeback 和 error_report。这个方向能保障 Owner、PM、Test、Architecture 看见任务状态，但如果所有上报都长期保存，中枢会快速积累大量过期、重复、低价值数据。

ANOS-REQ-161 定义执行遥测保留策略。它不是新的任务系统，也不是日志平台；它是 ANOS-REQ-160 任务事实视图和 Agent 成长闭环的基础数据治理机制。

## 产品原则

1. 上报入口先分级，不把所有数据都变成长期事实。
2. 当前状态覆盖写，历史只保留关键阶段和证据。
3. TaskResult 是交付真相，AuditLog 是权责真相，MetricsReport 是聚合真相。
4. Agent 成长只吃高价值失败、返工、人工纠偏和质量门失败。
5. 后台清理必须支持 dry-run、保护引用、批量审计和可恢复策略。

## 数据分层

| 层级 | 数据 | 用途 | 保留策略 |
| --- | --- | --- | --- |
| Current State | runner last heartbeat、current task、current step、load、last error summary | 看现在发生什么 | upsert 覆盖写；旧 raw 短期保留 |
| Task Timeline | started、phase changed、blocked、recovered、tool evidence、result writeback | 看任务如何走到现在 | 任务生命周期内长期保留摘要 |
| TaskResult | outputRefs、evidenceRefs、testsOrChecks、qualityEvaluation、terminalReason | 判断是否可验收 | 长期保留 |
| AuditLog | lease、权限、验收、人工纠偏、结果写入、清理摘要 | 追责和合规 | 长期保留 |
| MetricsReport | token、耗时、成功率、错误率、重试率 | 趋势和预算 | 聚合长期保留，raw 短期 |
| Learning Signal | rejected、rework、manual correction、quality gate failure、worker boundary violation | Agent 自成长 | 长期保留，进入 AgentImprovementProposal / EvalCase |

## Retention Class

每条遥测或临时记录必须能归类到 retention class。

| retentionClass | 数据例子 | 默认处理 |
| --- | --- | --- |
| ephemeral | raw heartbeat、重复 progress_update | 24 小时后删除 |
| hot_task | 当前任务进展、临时 timeline raw | 任务完成后 7 天压缩 |
| diagnostic | error detail、tool/model raw usage、debug detail | 30 天聚合，90 天删除或归档 |
| evidence | TaskResult evidence、testsOrChecks、outputRefs | 跟随 TaskResult 生命周期 |
| audit | lease、权限、验收、人工纠偏、结果写入、清理摘要 | 长期保留 |
| learning | rejected、rework、质量门失败、AgentImprovementProposal、EvalCase | 长期保留 |
| metrics | token、耗时、成功率聚合 | 聚合长期保留，删除 raw 噪音 |

## 功能需求

### ANOS-REQ-161-001 上报入口分级

中枢接收 heartbeat、lease_update、progress_update、tool_usage、model_usage、result_writeback、error_report 时，必须判断 retentionClass、是否进入 Current State、是否进入 Task Timeline、是否需要 Audit、是否可能成为 Learning Signal。

### ANOS-REQ-161-002 当前状态覆盖写

heartbeat、当前步骤、Runner 负载、当前任务、last error summary 等状态类数据默认覆盖写，不无限追加。任务事实视图优先读取 Current State 和 Task Timeline 摘要。

### ANOS-REQ-161-003 任务完成触发压缩

TaskResult 写回、任务进入 done/failed/blocked terminal 或 waiting_acceptance 时，系统必须触发 task closeout compaction：压缩普通 progress raw，保留阶段变化、阻塞、恢复、证据引用、质量门结果和结果写回。

### ANOS-REQ-161-004 后台清理 worker

系统需要 `TelemetryRetentionWorker` 或等价后台任务，定期执行：删除过期 ephemeral、压缩 hot_task、聚合 diagnostic/metrics、提升 learning signal、跳过受保护引用，并输出批量审计摘要。

### ANOS-REQ-161-005 dry-run 与 apply 双模式

清理任务必须先支持 dry-run，展示将删除、压缩、聚合、提升和跳过的对象数量及原因；apply 模式才真正执行删除或归档。

### ANOS-REQ-161-006 保护规则

清理不得删除 TaskResult、AuditLog、human acceptance、verified knowledge、仍被 TaskResult 引用的 evidence、active lease、active task progress、unresolved blocker、open incident、AgentImprovementProposal、EvalCase 及其必要证据。

### ANOS-REQ-161-007 批量审计摘要

清理不能每删一条都写 AuditLog。每次清理写一条批量审计摘要，包含 deleted、compacted、rolledUp、promoted、archived、skippedProtectedRefs 和 error count。

### ANOS-REQ-161-008 成长信号提升

验收拒绝、重复返工、人工纠偏、质量门失败、worker 越界、缺测试、缺证据、大文件增长等事件不得被普通清理删除；必须先判断是否生成或关联 AgentImprovementProposal / EvalCase。

## 明确不做

1. 不引入外部日志平台作为 V0 前置。
2. 不把所有 raw telemetry 长期保存。
3. 不把普通 heartbeat、普通 progress 写入 AuditLog。
4. 不删除仍被任务结果、审计、验收、知识或成长对象引用的数据。
5. 不改变 Scheduler、Runner、TaskResult、AuditLog 的核心语义。

## 成功指标

1. Owner / PM 仍能看到当前任务和关键历史。
2. TaskResult、AuditLog、MetricsReport、Learning Signal 保留完整。
3. 普通运行噪音不会无限增长。
4. 清理可 dry-run、可审计、可解释。
5. 任务事实视图不依赖已过期 raw telemetry。

## 后续交接

本需求需要 Architecture Agent 输出技术方案，明确数据落点、状态投影、TTL 字段、后台 worker、dry-run/apply CLI 或 API、保护引用检查和审计摘要格式。Development Agent 不直接按本草案实现。
