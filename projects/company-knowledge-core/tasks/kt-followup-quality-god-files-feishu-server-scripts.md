---
type: ProjectTask
title: 历史工程债治理：Feishu、server 与脚本质量债
description: 跟踪 Feishu、server、script 和 skill script 的历史大文件/长函数问题。
timestamp: "2026-06-23T10:25:00Z"
taskId: kt-followup-quality-god-files-feishu-server-scripts
projectId: company-knowledge-core
assignee: agent.company.architecture
status: pending
priority: medium
workSourceType: maintenance
sourceReason: Architecture remediation plan classified Feishu/server/script findings as historical engineering debt that must be tracked separately.
requirementRefs:
  - FOLLOWUP-QUALITY-GOD-FILES-FEISHU-001
  - FOLLOWUP-QUALITY-GOD-FILES-SERVER-001
  - FOLLOWUP-QUALITY-SCRIPTS-001
defectRefs:
  - DEF-AGTGTF-QUALITY-GATE-001
defectObjectRefs:
  - projects/company-knowledge-core/defects/def-agtgtf-quality-gate-001.md
receiverReviewRefs: []
resultRef: ""
---

# 历史工程债治理：Feishu、server 与脚本质量债

## Scope

规划并分期治理 `zhenzhi_knowledge/feishu.py`、`zhenzhi_knowledge/server.py`、相关 scripts 和 skill scripts 的历史大文件/长函数问题。

## Boundary

本任务是独立质量债，不作为 ANOS-REQ-160-FUSION-V1 scoped remediation 的当前阻塞项。
