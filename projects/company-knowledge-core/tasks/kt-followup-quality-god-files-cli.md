---
type: ProjectTask
title: 历史工程债治理：cli.py 命令模块拆分
description: 跟踪 zhenzhi_knowledge/cli.py 历史 parser/main 大函数和命令组耦合问题。
timestamp: "2026-06-23T10:25:00Z"
taskId: kt-followup-quality-god-files-cli
projectId: company-knowledge-core
assignee: agent.company.architecture
status: pending
priority: medium
workSourceType: maintenance
sourceReason: Architecture remediation plan classified FOLLOWUP-QUALITY-GOD-FILES-CLI-001 as historical engineering debt that must be tracked separately.
requirementRefs:
  - FOLLOWUP-QUALITY-GOD-FILES-CLI-001
defectRefs:
  - DEF-AGTGTF-QUALITY-GATE-001
defectObjectRefs:
  - projects/company-knowledge-core/defects/def-agtgtf-quality-gate-001.md
receiverReviewRefs: []
resultRef: ""
---

# 历史工程债治理：cli.py 命令模块拆分

## Scope

规划并分期治理 `zhenzhi_knowledge/cli.py` 的命令 parser、handler 和大函数问题。

## Boundary

本任务是独立质量债，不作为 ANOS-REQ-160-FUSION-V1 scoped remediation 的当前阻塞项。
