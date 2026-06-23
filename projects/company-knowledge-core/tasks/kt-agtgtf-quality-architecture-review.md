---
type: ProjectTask
title: 架构复核 Agent 成长任务事实 V1 工程质量拆分边界
description: 架构师 Agent 复核 development quality gate 失败项，明确哪些属于本次 V1 必须修复，哪些属于历史工程债，并给研发拆分边界。
timestamp: "2026-06-23T10:08:00Z"
taskId: kt-agtgtf-quality-architecture-review
projectId: company-knowledge-core
assignee: agent.company.architecture
status: pending
priority: high
workSourceType: bugfix
defectRefs:
  - DEF-AGTGTF-QUALITY-GATE-001
defectObjectRefs:
  - projects/company-knowledge-core/defects/def-agtgtf-quality-gate-001.md
requirementRefs:
  - ANOS-REQ-160-FUSION-V1
sourceReason: Development quality gate failed after V1 implementation; architecture must define scoped remediation boundaries before development continues.
receiverReviewRefs: []
resultRef: ""
---

# 架构复核工程质量边界

## Inputs

- `projects/company-knowledge-core/defects/def-agtgtf-quality-gate-001.md`
- `task-results/tr-kt-agent-team-growth-task-fact-development.md`
- `projects/company-knowledge-core/technical-solutions/agent-team-growth-and-task-fact-technical-solution.md`
- `scripts/quality/development_quality_gate.py`

## Required Decision

架构师 Agent 必须输出：

- 本次 V1 必须修复的问题。
- 可作为历史工程债单独分期的问题。
- 研发任务拆分边界。
- 是否允许 task-specific quality gate 使用 `--paths`，以及哪些路径必须过。
- 是否需要把 `build_task_fact_view` 从 `core.py` 拆到模块边界。
- 是否需要把 task fact V1 测试从 `tests/test_cli.py` 拆到独立测试文件。

## Expected Outputs

- `projects/company-knowledge-core/technical-solutions/agent-team-growth-task-fact-quality-remediation-plan.md`
- `task-results/tr-kt-agtgtf-quality-architecture-review.md`

## Acceptance Criteria

- 明确不允许继续向 god files 堆叠新逻辑。
- 明确本次 bugfix 的 pass 标准。
- 明确研发和测试的后续任务边界。
