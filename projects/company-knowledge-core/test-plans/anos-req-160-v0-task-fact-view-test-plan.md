---
type: ReviewRecord
title: ANOS-REQ-160 V0 只读任务事实视图测试计划
description: 将 22 条验收矩阵转为可执行测试范围，覆盖只读边界、状态解释、证据缺口、验收路由、旧任务兼容和敏感信息脱敏。
timestamp: "2026-06-23T08:09:08Z"
projectId: company-knowledge-core
taskId: kt-anos-req-160-v0-task-fact-view-test
status: submitted
ownerAgent: agent.company.test
reviewerAgent: agent.company.test
requirementRefs:
  - ANOS-REQ-160
sourceRefs:
  - docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md
  - docs/product/ai-native-os/task-execution-productization-prd.md
  - projects/company-knowledge-core/technical-solutions/anos-req-160-v0-task-fact-view-technical-solution.md
  - projects/company-knowledge-core/product-reviews/anos-req-160-v0-task-fact-view-architecture-product-review.md
  - projects/company-knowledge-core/tasks/kt-anos-req-160-v0-task-fact-view-development.md
  - projects/company-knowledge-core/tasks/kt-anos-req-160-v0-task-fact-view-test.md
scope:
  - task_fact_view_read_only_projection
  - active_task_status_coverage
  - result_and_evidence_gap_diagnostics
  - waiting_runner_and_acceptance_route_diagnostics
  - legacy_task_gap_compatibility
  - sensitive_information_redaction
  - reviewable_acceptance_evidence
---

# ANOS-REQ-160 V0 只读任务事实视图测试计划

## 测试结论口径

V0 验收只判断只读任务事实视图是否正确展示现有事实、缺口、权限和下一步。任何新增核心对象、重写执行链路、改变任务状态机、暴露写操作、泄露 secret/token/password 或未授权正文，均为 P0 不通过。

验收状态定义：

- `pass`: 有自动化、API/CLI/UI 输出、截图或代码审查证据，且满足预期。
- `fail`: 已执行且违反验收预期。
- `blocked`: 缺研发 TaskResult、缺可验收入口、缺测试数据或缺权限，无法执行。
- `not_run`: 当前阶段未到执行条件。

## 当前输入观察

- 测试任务：`projects/company-knowledge-core/tasks/kt-anos-req-160-v0-task-fact-view-test.md`。
- 研发任务：`projects/company-knowledge-core/tasks/kt-anos-req-160-v0-task-fact-view-development.md`，当前 `status: pending`，`resultRef: ""`。
- 当前未发现研发 TaskResult：`task-results/tr-kt-anos-req-160-v0-task-fact-view-development.md` 不存在。
- 因缺研发交付，完整验收执行入口暂未满足；本计划先固化 22 条测试设计。

## 测试数据要求

至少准备以下 ProjectTask / TaskResult / 关联对象 fixture 或真实样例：

- `pending`、`waiting_runner`、`processing`、`blocked`、`waiting_acceptance`、`done`、`failed` 任务各至少 1 条。
- done 但无 `resultRef` 的任务。
- done 且有 TaskResult、但缺 `evidenceRefs` 或 `testsOrChecks` 的任务。
- waiting_runner 且有 Runner 匹配事实、以及无法判断等待原因的任务。
- waiting_acceptance 且有/缺 `acceptanceOwner`、`acceptancePolicy`、`reviewRefs`、`resultRef` 的任务。
- 历史任务：缺 `requirementRefs`、`qualityEvaluation` 或 `commonRulesEvaluation`。
- 状态/结果不一致任务：task `status=done` 但 TaskResult `result=blocked/rejected`，以及 task 非 done 但已有结果。
- 含 dangling refs 的 TaskResult、SourceMaterial、Review、Audit 引用。
- 未识别 task status 样例。
- evidence/source/audit 中含 secret-like 字段、token、password、受限材料正文的样例。
- 模拟局部加载失败样例，验证读失败不写回 ProjectTask 或 TaskResult。

## 验收矩阵

| ID | 优先级 | 测试方式 | 执行要点 | 通过证据 |
| --- | --- | --- | --- | --- |
| ANOS-160-AC-001 | P0 | UI/API/CLI 功能测试 | 对 7 种活跃状态样例打开事实视图，检查 `taskId/title/projectId/status/updatedAt`。 | 输出或截图覆盖全部状态。 |
| ANOS-160-AC-002 | P0 | 架构/代码审查 | 检查实现 diff、schema、模板、对象索引，确认未新增 `TaskFactView` 等核心对象类型。 | diff 审查记录，列出允许的 read model/projection/serializer/UI 文件。 |
| ANOS-160-AC-003 | P0 | 架构/回归审查 | 检查 Scheduler、Agent Ring、runner claim/lease/heartbeat/finish、TaskResult 写回路径无行为性重写。 | diff 审查记录加相关回归测试结果。 |
| ANOS-160-AC-004 | P0 | UI/API 只读测试 | 检查事实视图无编辑、领取、改派、重试、验收、拒绝、关闭、知识写回、证据修改入口。 | UI 截图或 API schema/route 列表。 |
| ANOS-160-AC-005 | P0 | 追溯展示测试 | feature task 带 `requirementRefs/sourceMaterialRefs/acceptanceCriteriaRefs` 时展示引用，缺失时展示缺口类型。 | JSON/页面输出含引用和 gap。 |
| ANOS-160-AC-006 | P0 | done 缺结果负向测试 | done task 缺 `resultRef` 或 TaskResult 时，状态解释显示完成来源并标 `result evidence gap`。 | 输出不得出现完整闭环/accepted/passed。 |
| ANOS-160-AC-007 | P0 | done 缺证据负向测试 | done task 有 TaskResult 但缺 `evidenceRefs/testsOrChecks` 时展示 `resultRef` 和 `current gap` 或 `legacy gap`。 | 输出含缺口，不误判证据完整。 |
| ANOS-160-AC-008 | P0 | waiting_runner 诊断测试 | 有/缺 Runner 匹配事实时展示等待原因；无法判断时显示 `waiting reason unknown` 和缺失字段。 | 输出含 waiting reason 或 unknown gap。 |
| ANOS-160-AC-009 | P0 | waiting_acceptance 路由测试 | 展示 `acceptanceOwner/acceptancePolicy/reviewRefs/resultRef`；缺 owner 时标验收路由缺口。 | 输出含 owner/resultRef 或明确 route gap。 |
| ANOS-160-AC-010 | P0 | blocked 恢复路径测试 | blocked task 有/缺 blocker 时展示原因、owner、下一步；缺信息显示 `blocker detail missing`。 | 输出含 blocker detail 或 missing gap。 |
| ANOS-160-AC-011 | P1 | processing 责任测试 | 展示 executorAgent、runner/host、currentPhase、lastHeartbeatAt；缺字段显性标记。 | 输出含执行责任和心跳字段。 |
| ANOS-160-AC-012 | P1 | pending 下一步测试 | pending task 展示补条件、分配 Runner 或人工确认下一步；无法判断标 `next step unknown`。 | 输出含 next step owner/reason 或 unknown。 |
| ANOS-160-AC-013 | P0 | legacy 兼容测试 | 历史任务缺 `requirementRefs/qualityEvaluation/commonRulesEvaluation` 时不崩溃不白屏，已有事实正常显示。 | 输出含 `legacy gap`。 |
| ANOS-160-AC-014 | P0 | 状态/结果冲突测试 | task status 与 TaskResult result 不一致时显示 `status/result mismatch`、raw status、resultRef。 | 输出含 mismatch 诊断。 |
| ANOS-160-AC-015 | P0 | 质量规则缺口测试 | TaskResult 缺 `qualityEvaluation/commonRulesEvaluation` 时显示缺口，不默认 passed/accepted。 | 输出含质量/规则 gap。 |
| ANOS-160-AC-016 | P0 | 审计通知展示测试 | 有 AuditLog/NotificationRecord 时展示最近审计动作和通知状态；缺审计标 `audit gap`。 | 输出含 audit/notification 或 audit gap。 |
| ANOS-160-AC-017 | P0 | 安全脱敏测试 | evidence/source/audit 含 secret-like、token、password、受限材料时只展示脱敏引用、标题、类型、权限说明。 | 输出不含 secret 值，含 redaction/access note。 |
| ANOS-160-AC-018 | P1 | 权限受限测试 | 当前用户/Agent 无权读证据正文时，仅展示证据存在和访问限制。 | 输出含 restricted，不含正文。 |
| ANOS-160-AC-019 | P1 | dangling ref 测试 | 引用不存在的 TaskResult、SourceMaterial、Review、Audit 时显示 `dangling ref`、字段和值，不抛内部异常。 | 输出含 dangling ref 诊断。 |
| ANOS-160-AC-020 | P1 | unknown status 测试 | 未识别 status 时展示 raw status、来源对象、`unknown status` 和契约修复提示。 | 输出含 unknown status。 |
| ANOS-160-AC-021 | P1 | 局部加载失败测试 | 模拟事实视图依赖读取失败，展示失败来源和重试提示，校验 ProjectTask/TaskResult 未变。 | 输出含加载失败来源；前后文件 hash 一致。 |
| ANOS-160-AC-022 | P0 | 测试报告审查 | 测试报告逐项列出 P0 证据：自动化/API/截图/代码审查。 | 报告中每个 P0 有证据或明确 blocked/fail。 |

## 建议自动化入口

- `python3 -m unittest tests.test_cli` 或新增专用测试文件覆盖 projector/serializer/CLI。
- `python3 -m zhenzhi_knowledge.cli task fact-view <task-id> --format json` 或等价只读 CLI。
- `GET /v0/tasks/{taskId}/fact-view` 或等价只读 API。
- Workbench 单任务事实视图 DOM/截图检查。
- `python3 -m zhenzhi_knowledge.cli validate`。
- `git diff --check`。

## 发布阻断条件

- 缺研发 TaskResult 或缺可验收入口。
- 任一 P0 验收项 fail。
- P0 项只有人工声明、无报告证据。
- 新增核心对象或新状态机。
- 事实视图含写操作或触发 ProjectTask/TaskResult/Review/Audit/KnowledgeItem/Runner lease 写入。
- done 缺证据仍显示完整闭环。
- waiting_acceptance 看不到 owner/resultRef 或缺口。
- legacy gap 崩溃、白屏或误显示完整。
- 输出泄露 secret、token、密码或未授权材料正文。
