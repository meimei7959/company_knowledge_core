---
type: ProjectTask
title: 研发修复 task fact V1 projector 模块边界
description: 研发 Agent 将本次新增 task-fact-view.v1 投影逻辑从 core.py 的长函数/大文件增长中拆出，建立可测试模块边界。
timestamp: "2026-06-23T10:09:00Z"
taskId: kt-agtgtf-quality-dev-projector-module
projectId: company-knowledge-core
assignee: agent.company.development
status: waiting_acceptance
priority: high
workSourceType: bugfix
defectRefs:
  - DEF-AGTGTF-QUALITY-GATE-001
defectObjectRefs:
  - projects/company-knowledge-core/defects/def-agtgtf-quality-gate-001.md
requirementRefs:
  - ANOS-REQ-160-FUSION-V1
sourceReason: development_quality_gate flags build_task_fact_view/core.py large growth and long symbol; projector logic needs module boundary.
receiverReviewRefs: []
resultRef: task-results/tr-kt-agtgtf-quality-dev-projector-module.md
---

# 研发修复 projector 模块边界

## Inputs

- `projects/company-knowledge-core/tasks/kt-agtgtf-quality-architecture-review.md`
- `projects/company-knowledge-core/defects/def-agtgtf-quality-gate-001.md`
- `zhenzhi_knowledge/core.py`
- `task-results/tr-kt-agent-team-growth-task-fact-development.md`

## Scope

- 新建或复用独立模块承载 task fact V1 projection helpers。
- 缩短 `build_task_fact_view`，让 `core.py` 只保留兼容入口和 orchestration。
- 不改 PRD、产品评审或测试报告。
- 不处理 CLI parser 大函数，不处理全量历史工程债。

## Expected Outputs

- 研发变更引用。
- TaskResult：`task-results/tr-kt-agtgtf-quality-dev-projector-module.md`

## Acceptance Criteria

- 本任务相关路径运行 `development_quality_gate.py --paths <changed projector/core paths> --architecture-review-ref <quality plan>` 通过，或剩余项被架构方案明确标为历史债。
- `python3 -m unittest tests.test_cli.CliTests.test_task_fact_view_core_cli_api_and_p0_gaps` 通过或被迁移后的等价测试通过。
- `python3 -m zhenzhi_knowledge.cli validate` 通过。
