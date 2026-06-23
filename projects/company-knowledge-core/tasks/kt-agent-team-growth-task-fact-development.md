---
type: ProjectTask
title: 实现 Agent 团队成长与任务事实视图 V1
description: 研发 Agent 基于产品 PRD、架构技术方案和产品评审，实现 task-fact-view.v1、PM-worker 链路、成长信号和能力版本展示/校验。
timestamp: "2026-06-23T09:24:00Z"
taskId: kt-agent-team-growth-task-fact-development
projectId: company-knowledge-core
assignee: agent.company.development
status: waiting_acceptance
priority: high
workSourceType: feature
requirementRefs:
  - ANOS-REQ-160
  - ANOS-REQ-160-FUSION-V1
requirementObjectRefs:
  - docs/product/ai-native-os/agent-team-growth-and-task-fact-prd.md
acceptanceCriteriaRefs:
  - docs/product/ai-native-os/agent-team-growth-and-task-fact-prd.md
  - docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md
sourceReason: 产品经理 Agent 已接受架构方案，允许进入研发实现。
receiverReviewRefs:
  - projects/company-knowledge-core/receiver-reviews/receiver-review.agent-team-growth-task-fact.development.md
resultRef: task-results/tr-kt-agent-team-growth-task-fact-development.md
auditRefs:
  - knowledge/audit/audit.20260623T093708Z-agent-team-growth-task-fact-development.md
---

# 实现 Agent 团队成长与任务事实视图 V1

## Required Inputs

- `docs/product/ai-native-os/agent-team-growth-and-task-fact-prd.md`
- `projects/company-knowledge-core/technical-solutions/agent-team-growth-and-task-fact-technical-solution.md`
- `projects/company-knowledge-core/product-reviews/agent-team-growth-task-fact-architecture-product-review.md`
- `docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md`
- `docs/product/ai-native-os/task-source-receiver-review-prd.md`

## Required Flow

1. Development Agent must create a `ReceiverReview` before implementation.
2. If accepted, implement the agreed V1 scope.
3. Development Agent must not rewrite PRD, design, architecture, or test reports.
4. If product/architecture input is insufficient, write `accepted_with_assumptions` or `needs_rework`; do not silently invent scope.

## Implementation Scope

- Extend task fact read model to `task-fact-view.v1`.
- Preserve V0 compatibility.
- Add blocks for source, ReceiverReview, execution, worker participation, result/evidence, acceptance, growth signals, audit/notification, and capability version.
- Add gap taxonomy: `worker trace gap`, `result evidence gap`, `learning loop gap`, `capability version gap`, `audit gap`, and related machine-readable reasons from architecture.
- Support PM parent task and worker child task projection using existing task/result/review/evidence refs.
- Surface draft growth signal refs from AgentImprovementProposal and EvalCase where present; mark gap when signal should exist but is missing.
- Expose same facts through CLI/API and existing workbench read model where applicable.
- Do not implement multi-computer co-execution or same-project task racing.
- Do not implement new privacy-desensitization product scope.

## Expected Outputs

- ReceiverReview for development input.
- Code/config/docs changes required for V1 implementation.
- Tests or fixtures proving the main lifecycle.
- `task-results/tr-kt-agent-team-growth-task-fact-development.md`

## Acceptance Criteria

- CLI/API/task fact read model can render V1 projection for fixture tasks.
- Missing ReceiverReview, worker TaskResult, evidence, audit, growth signal, or capability version appear as explicit gaps, not inferred success.
- Parent PM task can show worker participation and PM consolidation refs.
- Capability version match/mismatch is visible.
- Existing V0 fact view behavior remains compatible.
- `python3 -m zhenzhi_knowledge.cli validate` passes.
- Relevant unit/integration tests pass.
