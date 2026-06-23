---
type: KnowledgeItem
title: Agent workflow terminal closure rule
description: Future Agent teams must design workflow orchestration from terminal outcomes backward, with evaluation, retry, escalation, notification, audit, and API-level tests.
timestamp: 2026-06-19T10:52:00Z
owner: codex
status: draft
scope: engineering
sourceRef: docs/memory/project-memory.md
confidence: high
knowledgeType: operating-rule
projectId: company-knowledge-core
tags:
  - agent-team
  - workflow
  - scheduler
  - review
  - quality-gate
  - closed-loop
evidenceRefs:
  - docs/memory/project-memory.md
  - docs/workflows/knowledge-ingest-orchestration.md
  - projects/company-knowledge-core/tasks/kt-review-outcome-publisher-closure.md
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/server.py
  - tests/test_cli.py
---

## Summary

开发任何 Agent 团队工作流时，不能只实现“创建下一张任务卡”。任务卡只是中间状态，不是结果。

正确设计方式是从终态倒推：

```txt
输入 -> 执行 -> 结果评价 -> Review -> 发布/审批/返工/澄清/冲突处理/拒绝 -> 通知 -> 可审计记录
```

只有当所有可能状态都有下一跳、失败结果会被评价并重试或修复、成功结果进入可用状态、请求方收到通知、审计记录可追踪时，这个工作流才算闭环。

## Structured Knowledge

### Rule

未来建设开发团队 Agent、运营团队 Agent 或其他项目 Agent 时，必须先定义该团队要交付的“终态产品结果”，再定义 Agent 岗位、技能、任务类型和调度机制。

### Required Workflow Elements

- terminal outcomes: 明确成功、失败、需审批、需澄清、冲突、拒绝等终态。
- quality evaluation: 每个 Agent 输出必须有可评价标准。
- retry and repair: 不达标时要自动创建返工、修复或澄清任务，不能停在失败状态。
- reviewer handoff: Review Agent 不能只写意见，必须把结果路由到 Publisher、Approval、Retry、Conflict Resolution 或 Rejection。
- notification: 每个重要状态变化都要通知请求方或下一责任 Agent。
- audit: 调度、评价、Review、发布、拒绝、冲突处理都要有可追踪记录。
- API contract: 对外接口返回值要包含下一跳证据，例如 `followupTaskRefs`、`publishedRefs`、`notificationRefs`、`reviewRecordRef`。
- lifecycle tests: 测试必须覆盖从入口 API 到终态的完整生命周期，不只测某个函数。

### Failure Pattern

这次知识记录链路的失败根因是：实现停在 `TaskResult -> qualityEvaluation -> review/retry/repair`，但没有把 `Knowledge Review` 后面的 Publisher、Indexer、Approval、返工、通知串成可执行闭环。

这导致系统表面上“创建了任务”，实际目标“知识可落库、可检索、可追责”没有达成。

### Correct Implementation Pattern

知识记录闭环现在应按如下方式实现：

```txt
SourceMaterial
-> KnowledgeTask
-> TaskResult
-> qualityEvaluation
-> knowledge_review task
-> /v0/review/finish
-> one of:
   pass_as_observed -> update KnowledgeItem observed -> rebuild index -> notify requester
   needs_human_approval -> create approval task -> notify human owner
   changes_requested -> create retry task -> notify Knowledge Engineering Agent
   needs_clarification -> create clarification task -> notify requester
   conflict_detected -> create ConflictRecord and resolution task -> notify Knowledge Steward Agent
   reject -> mark target rejected -> notify requester
```

## Applicability

适用于：

- 知识工程 Agent 团队。
- 后续开发团队 Agent。
- 运营团队 Agent。
- 任何由 Agent Hub / Scheduler / Agent Ring 串起来的多 Agent 工作流。

不适用于：

- 一次性人工讨论。
- 不进入项目任务系统的临时问答。

## Evidence

- `docs/memory/project-memory.md` 已记录工程铁律。
- `docs/workflows/knowledge-ingest-orchestration.md` 已记录 `/v0/review/finish` 的可执行路由。
- `zhenzhi_knowledge/core.py` 已实现 `apply_knowledge_review_result`。
- `zhenzhi_knowledge/server.py` 已暴露 `/v0/review/finish`。
- `tests/test_cli.py` 已覆盖核心函数和 HTTP 生命周期。
