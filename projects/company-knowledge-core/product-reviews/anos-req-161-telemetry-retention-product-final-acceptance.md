---
type: ReviewRecord
title: ANOS-REQ-161 telemetry retention product final acceptance
description: Product Manager Agent final acceptance for execution telemetry retention, cleanup, protected references, metrics rollup, and learning signal promotion.
timestamp: "2026-06-23T12:23:36Z"
projectId: company-knowledge-core
reviewerAgent: agent.company.product-manager
status: accepted
decision: accepted
businessConclusion: accepted_for_v0
requirementRefs:
  - ANOS-REQ-161
  - ANOS-REQ-160
taskRef: projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-product-acceptance.md
receiverReviewRef: projects/company-knowledge-core/receiver-reviews/receiver-review.anos-req-161.product-final-acceptance.md
prdRef: docs/product/ai-native-os/execution-telemetry-retention-prd.md
acceptanceMatrixRef: docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md
developmentTaskResultRef: task-results/tr-kt-anos-req-161-telemetry-retention-development.md
testTaskResultRef: task-results/tr-kt-anos-req-161-telemetry-retention-test.md
testReportRef: projects/company-knowledge-core/test-reports/anos-req-161-telemetry-retention-test-report.md
auditRefs:
  - knowledge/audit/audit.20260623T122336Z-anos-req-161-product-final-acceptance.md
---

# ANOS-REQ-161 Telemetry Retention Product Final Acceptance

## 结论

产品最终验收结论：accepted。

ANOS-REQ-161 V0 的产品语义通过验收。已交付行为覆盖上报入口分级、当前状态覆盖写、任务完成 closeout compaction、后台清理 worker、dry-run/apply 双模式、保护引用优先、批量 AuditLog summary、成长信号结构化保留和 metrics rollup。测试证据显示 6 个 unittest 通过，补充验收探针 26 项通过，仓库状态校验 valid yes。

本次批准范围是 repository-local、file-backed V0。外部日志平台、生产调度 cadence、外部存储集成、operator CLI command、扩大后的生产保护引用 fixture 属于 scope deferral，不阻塞 V0。

## Requirement Acceptance

| Requirement | 产品判断 | 证据 | 结论 |
| --- | --- | --- | --- |
| ANOS-REQ-161-001 上报入口分级 | delivered behavior can classify heartbeat, progress_update, tool_usage, model_usage, result_writeback, error_report, learning error into current state, timeline, metrics, protected, and learning routes. | Test TaskResult acceptanceResults 001; test report Acceptance Coverage; `classify_telemetry_event` / `_retention_class` / `_routes_for` in `zhenzhi_knowledge/telemetry_retention.py`. | accepted |
| ANOS-REQ-161-002 当前状态覆盖写 | delivered behavior keeps one logical current-state record per runner/task key and overwrites latest heartbeat/progress/load/error summary instead of appending unbounded noise. | Test TaskResult acceptanceResults 002; test report current-state upsert evidence; `_upsert_current_state` in implementation. | accepted |
| ANOS-REQ-161-003 任务完成触发压缩 | terminal or waiting_acceptance task timeline compacts into task summary and keeps evidence refs while raw hot events can expire. | Test TaskResult acceptanceResults 003; test report closeout compaction evidence; `_compact_timelines` and terminal task fixture. | accepted |
| ANOS-REQ-161-004 后台清理 worker | worker plans and applies deletion, compaction, rollup, learning promotion, protected skips, and report counts. | Development TaskResult summary; Test TaskResult acceptanceResults 004/005; `TelemetryRetentionWorker.dry_run` and `TelemetryRetentionWorker.apply`. | accepted |
| ANOS-REQ-161-005 dry-run 与 apply 双模式 | dry-run reports candidates and reasons without mutation; apply performs eligible cleanup and writes summaries, rollups, promotions, and audit refs. | Test report Dry-Run And Apply Report Shape; unittest dry-run/apply tests; supplemental probe counts. | accepted |
| ANOS-REQ-161-006 保护规则 | protected result refs and cited refs from TaskResult, AuditLog/human acceptance, verified knowledge, and open blocker fixtures survive cleanup. | Test report Protected Ref Checks; Test TaskResult acceptanceResults 006; `_protected_ref_text` / `_protected_reason`. | accepted |
| ANOS-REQ-161-007 批量审计摘要 | apply writes one batch AuditLog with `policyResult: batch_summary` and does not create per-row deletion audit noise. | Test TaskResult acceptanceResults 007; test report batch AuditLog evidence; `_write_batch_audit`. | accepted |
| ANOS-REQ-161-008 成长信号提升 | rejected/rework/manual correction/quality gate failure/boundary violation style signals are retained and promoted into AgentImprovementProposal/EvalCase candidates before cleanup. | Test TaskResult acceptanceResults 008; test report learning signal and metrics rollup evidence; `_promote_learning_signals`. | accepted |

## Product Semantics

| Product concern | Final judgment |
| --- | --- |
| 当前状态覆盖写 | accepted. Repeated heartbeat/progress signals preserve latest operator-facing state without raw status growth. |
| 关键事实长期化 | accepted. Task closeout summary, protected result refs, metrics rollup, and learning promotions create durable artifacts. |
| 普通噪音清理 | accepted. Expired unprotected ephemeral/hot telemetry is delete-eligible and removed in apply mode. |
| 成长信号结构化保留 | accepted. Learning signals are skipped from deletion and promoted into improvement/eval candidates. |
| dry-run/apply 可解释性 | accepted. Reports include counts, delete candidates, protected skips, compact tasks, learning candidates, digest, and apply refs. |
| protected refs 优先级 | accepted. Protection precedes TTL cleanup. |
| AuditLog 可读性 | accepted. One batch summary avoids deleting row-by-row audit noise while preserving counts and refs. |
| metrics rollup | accepted. Cleanup rollup is retained as MetricsReport under `knowledge/metrics/`. |

## Non-Goals

These PRD non-goals remain respected:

- No full external log platform in V0.
- No raw telemetry warehouse or hosted-only storage assumption.
- No direct Agent Ring implementation ownership in this repository.
- No reusable knowledge publication from raw telemetry without review path.

## Scope Deferrals

| Deferred item | Product judgment | Blocking V0? |
| --- | --- | --- |
| External logging platform or centralized production log store | Explicit PRD non-goal for this slice. Repository-local retention semantics are enough for V0. | no |
| Operator CLI command for retention worker | Development TaskResult lists no operator CLI command. PRD does not make this a V0 blocker; module-level worker contract and tests cover required behavior. | no |
| Production scheduler cadence | Apply mode is file-backed and callable; production scheduling cadence is a later integration choice. | no |
| External store integration | V0 is repository-local; broader storage integration should add fixtures before production cleanup automation. | no |
| Broader protected-reference fixtures | Current text/ref scan is conservative and adequate for V0; expand when new storage surfaces are added. | no |

## Final Decision

Overall status: accepted.

Rejected items: none.

Changes requested: none for V0.

Follow-up scope: create future integration tasks only when production retention automation, external log store integration, or operator-facing CLI controls are scheduled.
