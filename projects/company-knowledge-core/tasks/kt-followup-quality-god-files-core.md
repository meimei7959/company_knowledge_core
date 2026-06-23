---
type: ProjectTask
title: 历史工程债治理：core.py 模块拆分
description: 跟踪 zhenzhi_knowledge/core.py 历史 god-file、大函数和长期增长问题，独立于 ANOS-REQ-160-FUSION-V1 本轮修复。
timestamp: "2026-06-23T10:25:00Z"
taskId: kt-followup-quality-god-files-core
projectId: company-knowledge-core
assignee: agent.company.architecture
status: pending
priority: medium
workSourceType: maintenance
sourceReason: Architecture remediation plan classified FOLLOWUP-QUALITY-GOD-FILES-CORE-001 as historical engineering debt that must be tracked separately.
requirementRefs:
  - FOLLOWUP-QUALITY-GOD-FILES-CORE-001
defectRefs:
  - DEF-AGTGTF-QUALITY-GATE-001
defectObjectRefs:
  - projects/company-knowledge-core/defects/def-agtgtf-quality-gate-001.md
receiverReviewRefs: []
resultRef: ""
---

# 历史工程债治理：core.py 模块拆分

## Scope

规划并分期治理 `zhenzhi_knowledge/core.py` 的历史大文件、大函数和领域混杂问题。

## Boundary

本任务是独立质量债，不作为 ANOS-REQ-160-FUSION-V1 task-fact projector scoped gate 的当前阻塞项。
