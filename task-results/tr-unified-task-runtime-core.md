---
type: TaskResult
title: Result for unified-task-runtime-core
description: Result of task unified-task-runtime-core.
timestamp: "2026-06-20T16:31:14Z"
resultId: TR-unified-task-runtime-core
taskId: unified-task-runtime-core
projectId: company-knowledge-core
assignee: agent.company.development
taskRuntime: {"version":"task-runtime.v1","taskType":"workflow_runtime_core","category":"engineering","qualityGate":"engineering","acceptancePath":"pm_review","requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
runnerId: ""
executorAgent: ""
status: done
summary: 统一任务运行内核最小版本已实现：任务创建会生成 taskRuntime profile，自动分诊默认负责 Agent；工程任务不再走知识草稿质量门，知识任务仍要求 SourceMaterial 和 KnowledgeItem draft；工程类任务必须有测试或检查；TaskResult 会记录 taskRuntime，便于项目经理 Agent、通知和验收路由判断下一步。
outputRefs:
  - zhenzhi_knowledge/core.py
  - tests/test_cli.py
  - docs/agent-team/company-agent-team-operating-guide.md
  - docs/agent-team/common-agent-operating-rules.md
  - docs/scheduler/task-dispatch-model.md
knowledgeRefs: []
sourceMaterialRefs:
  - docs/strategy/zhenzhi-ai-native-knowledge-system.md
  - docs/agent-team/company-agent-team-operating-guide.md
  - docs/agent-team/common-agent-operating-rules.md
  - projects/company-knowledge-core/pm-reviews/pm-review-unified-task-runtime-core.md
evidenceRefs:
  - tasks/unified-task-runtime-core.md
  - projects/company-knowledge-core/pm-reviews/pm-review-unified-task-runtime-core.md
testsOrChecks:
  - python3 -m unittest tests.test_cli
  - python3 -m zhenzhi_knowledge.cli validate
nextActions:
  - 用飞书创建灰度项目验证 taskRuntime 和通知展示
  - 用记录知识入口验证 KnowledgeTask 质量门仍然生效
handoffContract: {"fromAgent":"agent.company.development","handoffTo":"","handoffSummary":"统一任务运行内核已完成最小可运行闭环，覆盖工程修复、知识沉淀、项目初始化三类任务；建议下一步用飞书项目创建和知识记录各跑一次线上灰度。","requiredArtifacts":["summary","evidence refs","next action or terminal reason"],"artifactRefs":["zhenzhi_knowledge/core.py","tests/test_cli.py","docs/agent-team/company-agent-team-operating-guide.md","docs/agent-team/common-agent-operating-rules.md","docs/scheduler/task-dispatch-model.md","tasks/unified-task-runtime-core.md","projects/company-knowledge-core/pm-reviews/pm-review-unified-task-runtime-core.md"],"openRisks":[],"nextSuggestedTask":"用飞书创建灰度项目验证 taskRuntime 和通知展示","terminalReason":"No next role declared; Project Manager Agent should close or create the next task."}
commonRulesEvaluation: {"version":"common-agent-rules.v1","status":"passed","passed":true,"rulesRef":"docs/agent-team/common-agent-operating-rules.md","guideRef":"docs/agent-team/company-agent-team-operating-guide.md","checkedRules":["summary","evidence_or_artifacts","quality_evaluation","handoff_or_terminal_reason","engineering_tests_or_checks"],"reasons":[],"ruleIssueRequired":false}
qualityEvaluation: {"type":"AgentResultEvaluation","status":"passed","passed":true,"decision":"close","score":95,"attemptNumber":1,"maxAttempts":3,"retryable":false,"reasons":[],"nextOwnerAgent":""}
acceptancePolicy: {"version":"acceptance.v1","acceptanceStatus":"accepted","humanAcceptanceRequired":true,"acceptanceRequiredByDefault":true,"projectManager":"agent.company.project-manager","humanReviewer":"meimei","decidedBy":"meimei","decisionReason":"人类 Owner 确认统一任务运行内核可进入部署灰度。","acceptedBy":"meimei","acceptedAt":"2026-06-20T16:34:29Z","rejectedBy":"","rejectedAt":"","requiresNextTaskCreation":false}
improvementRefs: []
evalCaseRefs: []
followupTaskRefs: []
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
completedAt: "2026-06-20T16:31:14Z"
updatedAt: "2026-06-20T16:34:29Z"
---

## Summary

统一任务运行内核最小版本已实现：任务创建会生成 taskRuntime profile，自动分诊默认负责 Agent；工程任务不再走知识草稿质量门，知识任务仍要求 SourceMaterial 和 KnowledgeItem draft；工程类任务必须有测试或检查；TaskResult 会记录 taskRuntime，便于项目经理 Agent、通知和验收路由判断下一步。

## Evidence

- tasks/unified-task-runtime-core.md
- projects/company-knowledge-core/pm-reviews/pm-review-unified-task-runtime-core.md

## Outputs

- zhenzhi_knowledge/core.py
- tests/test_cli.py
- docs/agent-team/company-agent-team-operating-guide.md
- docs/agent-team/common-agent-operating-rules.md
- docs/scheduler/task-dispatch-model.md

## Next Actions

- 用飞书创建灰度项目验证 taskRuntime 和通知展示
- 用记录知识入口验证 KnowledgeTask 质量门仍然生效

## Handoff

- fromAgent: agent.company.development
- handoffTo: none
- summary: 统一任务运行内核已完成最小可运行闭环，覆盖工程修复、知识沉淀、项目初始化三类任务；建议下一步用飞书项目创建和知识记录各跑一次线上灰度。
- nextSuggestedTask: 用飞书创建灰度项目验证 taskRuntime 和通知展示
- terminalReason: No next role declared; Project Manager Agent should close or create the next task.
- artifactRefs:
  - zhenzhi_knowledge/core.py
  - tests/test_cli.py
  - docs/agent-team/company-agent-team-operating-guide.md
  - docs/agent-team/common-agent-operating-rules.md
  - docs/scheduler/task-dispatch-model.md
  - tasks/unified-task-runtime-core.md
  - projects/company-knowledge-core/pm-reviews/pm-review-unified-task-runtime-core.md
- openRisks:
  - none

## Quality Evaluation

- status: passed
- decision: close
- score: 95
- attempt: 1/3
- reasons: none

## Common Operating Rules

- status: passed
- rulesRef: docs/agent-team/common-agent-operating-rules.md
- guideRef: docs/agent-team/company-agent-team-operating-guide.md
- reasons: none

## Acceptance

- status: waiting_acceptance
- humanAcceptanceRequired: True
- projectManager: agent.company.project-manager
- humanReviewer: meimei
- reason: none

## Agent Improvement

- improvementRefs: none
- evalCaseRefs: none

## Tests Or Checks

- python3 -m unittest tests.test_cli
- python3 -m zhenzhi_knowledge.cli validate

## Agent Team Guide Gate

- guideUpdateRequired: False
- guideUpdated: False
- guideRef: none
- guideFeishuUrl: none
- guideRevision: none
- guideAuditRefs: none
