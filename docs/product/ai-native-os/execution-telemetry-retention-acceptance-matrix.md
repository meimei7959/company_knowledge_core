---
type: AcceptanceMatrix
requirementId: ANOS-REQ-161
title: ANOS-REQ-161 执行遥测保留与后台清理验收矩阵
description: 验收执行遥测分级、当前状态覆盖写、任务完成压缩、后台清理、保护引用、批量审计和成长信号提升。
timestamp: "2026-06-23T10:05:00Z"
projectId: company-knowledge-core
ownerAgent: agent.company.product-manager
status: draft
prdRef: docs/product/ai-native-os/execution-telemetry-retention-prd.md
---

# ANOS-REQ-161 执行遥测保留与后台清理验收矩阵

| ID | 优先级 | 需求 | 验收方式 | 预期结果 |
| --- | --- | --- | --- | --- |
| ANOS-161-AC-001 | P0 | 上报入口能识别 retentionClass | 单元/集成测试覆盖 heartbeat、progress_update、tool_usage、model_usage、result_writeback、error_report | 每类上报被分到正确 retentionClass 和处理路径。 |
| ANOS-161-AC-002 | P0 | Current State 覆盖写 | 连续上报同一 Runner heartbeat / current step | 只保留最新状态；不生成无限历史。 |
| ANOS-161-AC-003 | P0 | 阶段变化进入 Task Timeline | 模拟任务阶段变化、阻塞、恢复、结果写回 | timeline 保留关键变化，重复 progress 被压缩。 |
| ANOS-161-AC-004 | P0 | TaskResult 写回触发 closeout compaction | 完成一个有 progress raw 的任务 | 普通 raw 被压缩；证据、质量门、阻塞/恢复和结果写回保留。 |
| ANOS-161-AC-005 | P0 | 后台清理支持 dry-run | 运行 retention cleanup dry-run | 输出将删除、压缩、聚合、提升、跳过的对象及原因，不修改数据。 |
| ANOS-161-AC-006 | P0 | apply 执行受保护清理 | 运行 retention cleanup apply | 删除过期 ephemeral，压缩 hot_task，聚合 metrics，跳过保护引用。 |
| ANOS-161-AC-007 | P0 | 保护规则生效 | 构造被 TaskResult / Audit / EvalCase 引用的数据 | 清理跳过受保护对象并说明原因。 |
| ANOS-161-AC-008 | P0 | 清理写批量 AuditLog | 执行一次 apply | 只写批量审计摘要，不为每条删除制造 AuditLog 噪音。 |
| ANOS-161-AC-009 | P0 | 成长信号不被误删 | 构造 rejected / rework / quality gate failure / manual correction | 事件被提升或保留为 Learning Signal 候选，不被普通清理删除。 |
| ANOS-161-AC-010 | P1 | Metrics 聚合保留 | 构造 tool/model raw usage | raw 到期后聚合到 MetricsReport 或等价统计，长期指标可查。 |
| ANOS-161-AC-011 | P1 | 任务事实视图不依赖过期 raw | 清理完成后查看任务事实视图 | 当前状态、关键 timeline、TaskResult、Audit、Learning Signal 仍可展示。 |

## 不通过条件

1. 普通 heartbeat / progress 长期无限追加。
2. 清理删除 TaskResult、AuditLog、验收、verified knowledge 或受保护 evidence。
3. 清理没有 dry-run。
4. 清理每条删除都写 AuditLog，制造新的数据噪音。
5. 失败、返工、人工纠偏、质量门失败被当作普通噪音删除。
