---
type: ProjectTask
title: 研发修复 task fact V1 CLI/API 接线边界
description: 研发 Agent 在 projector 模块边界修复后，收敛 CLI/API/workbench 接线，避免继续扩大 cli.py/server.py/core.py 大函数。
timestamp: "2026-06-23T10:10:00Z"
taskId: kt-agtgtf-quality-dev-cli-api-boundary
projectId: company-knowledge-core
assignee: agent.company.development
status: done
priority: high
workSourceType: bugfix
defectRefs:
  - DEF-AGTGTF-QUALITY-GATE-001
defectObjectRefs:
  - projects/company-knowledge-core/defects/def-agtgtf-quality-gate-001.md
requirementRefs:
  - ANOS-REQ-160-FUSION-V1
sourceReason: development_quality_gate flags cli.py/server.py/core.py large file and long symbol risks; task fact V1 entry wiring must be scoped.
receiverReviewRefs: []
resultRef: task-results/tr-kt-agtgtf-quality-dev-cli-api-boundary.md
---

# 研发修复 CLI/API 接线边界

## Inputs

- `projects/company-knowledge-core/tasks/kt-agtgtf-quality-dev-projector-module.md`
- `projects/company-knowledge-core/technical-solutions/agent-team-growth-task-fact-quality-remediation-plan.md`
- `projects/company-knowledge-core/defects/def-agtgtf-quality-gate-001.md`

## Scope

- 保持 CLI/API/workbench 使用同一 task fact V1 read model。
- 若需要修改 `cli.py` 或 `server.py`，只能做薄入口接线，不新增大块业务逻辑。
- 优先把业务逻辑留在 projector 模块。
- 不做同项目多电脑协作、不做隐私脱敏新增能力。

## Expected Outputs

- 研发变更引用。
- TaskResult：`task-results/tr-kt-agtgtf-quality-dev-cli-api-boundary.md`

## Acceptance Criteria

- CLI/API/workbench task fact fixture 行为保持一致。
- task-specific quality gate 对本任务改动路径通过，或剩余历史大文件项有架构确认。
- `python3 -m zhenzhi_knowledge.cli validate` 通过。
