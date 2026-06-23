---
type: ReviewRecord
title: ANOS-REQ-161 telemetry retention architecture product review
description: Product Manager Agent review of the Architecture technical solution for ANOS-REQ-161 before Development handoff.
timestamp: "2026-06-23T11:55:55Z"
projectId: company-knowledge-core
reviewerAgent: agent.company.product-manager
status: accepted_with_assumptions
decision: accepted_with_assumptions
requirementRefs:
  - ANOS-REQ-161
  - ANOS-REQ-160
taskRef: projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-architecture-product-review.md
receiverReviewRef: projects/company-knowledge-core/receiver-reviews/receiver-review.anos-req-161.architecture-product-review.md
technicalSolutionRef: projects/company-knowledge-core/technical-solutions/anos-req-161-telemetry-retention-technical-solution.md
architectureTaskResultRef: task-results/tr-kt-anos-req-161-telemetry-retention-architecture.md
acceptanceMatrixRef: docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md
prdRef: docs/product/ai-native-os/execution-telemetry-retention-prd.md
handoffTo: agent.company.development
auditRefs:
  - knowledge/audit/audit.20260623T115555Z-anos-req-161-architecture-product-review.md
---

# Architecture Product Review

## 接收结论

Product Manager Agent 复核结论：`accepted_with_assumptions`。

架构技术方案可交 Development 使用，但 Development release 必须保留本复核列出的条件，且不得把本结论理解为关闭整条 ANOS-REQ-161。当前复核只接受 Architecture 方案进入研发实现，不启动研发、不测试实现、不改写架构。

不判为 `needs_rework` 的理由：

1. 方案覆盖 ANOS-REQ-161-001 至 ANOS-REQ-161-008，并映射到验收矩阵 ANOS-161-AC-001 至 ANOS-161-AC-010。
2. 方案保持产品语义：执行遥测是短期可见性、任务说明、聚合指标、受保护证据和成长信号的分层材料，不是长期 raw truth。
3. 方案保留硬边界：不以前置外部日志平台、核心语义重写、全量 raw 长存、逐条删除审计作为 V0 条件。
4. 方案明确 Development 必须加载 `development-engineering-quality-gate` 并运行 `scripts/quality/development_quality_gate.py`。

## ANOS-REQ-161 覆盖判断

| Requirement | 架构覆盖判断 | 产品复核结论 |
| --- | --- | --- |
| ANOS-REQ-161-001 | Ingestion classifier assigns `eventType`, `scope`, `retentionClass`, protected candidate, sensitivity, dedupe key, event time, and source ref; routes heartbeat, lease, progress, tool/model usage, result writeback, and error report into current state, timeline, audit, metrics, or learning paths. | 覆盖，保持入口分级语义。 |
| ANOS-REQ-161-002 | `ExecutionCurrentState` read model overwrites latest heartbeat, current task, current phase, last step, load, lease, and safe error summary by keyed upsert. | 覆盖，避免无限追加 raw 状态。 |
| ANOS-REQ-161-003 | Closeout compaction triggers on TaskResult writeback, terminal statuses, `waiting_acceptance`, or inactive lease crossing the hot window; output is `TaskExecutionSummary`. | 覆盖，保留任务解释摘要和 evidence refs。 |
| ANOS-REQ-161-004 | `TelemetryRetentionWorker` performs expiry, hot timeline compaction, metrics/diagnostic rollup, learning promotion, protected skip handling, and batch reporting. | 覆盖，Development/Test 需验证 worker lifecycle。 |
| ANOS-REQ-161-005 | Dry-run produces a deterministic plan/report without mutation; apply mutates only after manifest staging and emits explainable counts and reasons. | 覆盖，dry-run/apply 分离清楚。 |
| ANOS-REQ-161-006 | Protected-ref scan covers TaskResult, AuditLog, ReviewRecord, knowledge, AgentImprovementProposal, EvalCase, active lease/task, blockers, incidents, SourceMaterial, MetricsReport, and cited telemetry batches. | 覆盖，保护优先级高于 TTL 和 cleanup。 |
| ANOS-REQ-161-007 | Apply writes one batch AuditLog summary with counts, skipped categories, manifest ref, rollup refs, promotion refs, actor/job identity, and dry-run digest. | 覆盖，明确拒绝逐条删除 AuditLog。 |
| ANOS-REQ-161-008 | Error/rework/quality-gate/boundary/manual-correction signals go through learning classifier and idempotent promotion into AgentImprovementProposal/EvalCase candidates before cleanup. | 覆盖，成长信号不被普通清理删除。 |

补充判断：ANOS-161-AC-003 的 timeline 阶段变化、ANOS-161-AC-010 的 metrics rollup 在方案中有对应承载；实现阶段必须用验收矩阵证明。

## 非目标保留

本复核确认 Architecture 方案保留以下非目标：

- 不引入外部日志平台作为 V0 前置。
- 不重写 Scheduler / Runner / TaskResult / AuditLog 核心语义。
- 不把所有 raw telemetry 长期保存为事实来源。
- 不为每条删除写 AuditLog；只允许每次 apply 写一条批量摘要。
- 不删除受 TaskResult、AuditLog、ReviewRecord、人类验收、KnowledgeItem、AgentImprovementProposal、EvalCase、active lease/task、blocker、incident 或 SourceMaterial 保护的数据。
- 不把 Architecture 方案接受等同于实现完成、测试通过或整条 ANOS-REQ-161 关闭。

## Development Release Conditions

Development 可由 PM 下一步派发，但必须满足：

1. Development Agent 先创建 ReceiverReview，结论必须为 `accepted_for_work` 或 `accepted_with_assumptions`。
2. Development 只实现已接受的 Architecture 方案，不得扩大到外部日志平台、核心对象语义重写或长期 raw telemetry 平台化。
3. Development 必须加载 `development-engineering-quality-gate`，并在交付前运行 `scripts/quality/development_quality_gate.py`。
4. Development TaskResult 必须列出 changed files、tests/checks、quality gate output、ANOS-161-AC-001 至 ANOS-161-AC-010 覆盖、风险和 Test handoff。
5. Apply 模式在通过 dry-run、manifest staging、protected refs、idempotency、batch AuditLog 和 rollback/recovery 验证前不得被视为可发布。
6. Test Agent 后续必须覆盖 dry-run no mutation、apply batch summary、protected skip reasons、learning promotion、metrics rollup、redaction/permission、failure recovery 和 status valid。

## 风险 / 假设

- 受保护引用扫描是最大实现风险；Development/Test 需要构造覆盖 TaskResult、Audit、ReviewRecord、KnowledgeItem、SourceMaterial、AgentImprovementProposal、EvalCase、active lease/task、blocker、incident 的 fixture。
- Learning signal promotion 需要阈值和去重，避免把普通错误噪音全部提升为成长对象。
- Apply 恢复必须依赖 manifest/idempotency；不得靠人工清理状态来恢复。
- TTL 默认值可配置，但 protected-ref priority、dry-run/apply separation、batch AuditLog、development quality gate 是不可放松条件。

## 产品结论

`accepted_with_assumptions`。Architecture solution 可以交 Development 使用；PM 下一步可派发 `kt-anos-req-161-telemetry-retention-development`，但 Development task 仍需按其 own ReceiverReview、质量门和测试交接完成。

