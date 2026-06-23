---
type: ProjectTask
title: 测试验收 V1 工作台 Codex 风格中文界面
description: ProjectTask assigned to agent.company.test.
timestamp: "2026-06-22T04:31:53Z"
taskId: kt-v1-workbench-codex-style-test
taskType: testing
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"testing","category":"testing","stage":"","requiredCapabilities":["testing"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-dev.md","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"testing","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.test
status: waiting_acceptance
priority: critical
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-dev.md
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
expectedOutput:
  - 测试 Agent 验证中文可读、状态正确、真实数据可见、工作台校验通过
resultRef: task-results/tr-kt-v1-workbench-codex-style-test.md
notificationRefs:
  - notifications/notification.20260622T043153547516Z.md
  - notifications/notification.20260622T053944198266Z.md
  - notifications/notification.20260622T053944199148Z.md
  - notifications/notification.20260622T053944199832Z.md
  - notifications/notification.20260622T054748949607Z.md
  - notifications/notification.20260622T055122336609Z.md
  - notifications/notification.20260622T055122337542Z.md
  - notifications/notification.20260622T055122338260Z.md
  - notifications/notification.20260622T061748562502Z.md
  - notifications/notification.20260622T062246538935Z.md
  - notifications/notification.20260622T062246539794Z.md
  - notifications/notification.20260622T062246540475Z.md
auditRefs: []
assignedRunner: ""
executorAgent: agent.company.test
leaseOwner: ""
leaseTokenHash: ""
leaseProofHash: ""
leaseIssuedAt: ""
leaseExpiresAt: ""
leaseHeartbeatAt: ""
leaseVersion: 1
leaseAttempt: 0
heartbeatAt: ""
taskVersion: 3
handoffContract: {"from":"agent.company.test","to":"agent.company.product-manager","requiredArtifacts":["test conclusion","defect list","release recommendation","blockers"],"handoffSummary":"第 3 轮回归通过；DEFECT-002 raw status detail DOM 已关闭，允许进入产品最终验收。"}
qualityGateRequired: true
attemptNumber: 3
maxAttempts: 3
followupTaskRefs: []
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-22T06:22:46Z"
completedAt: "2026-06-22T06:22:46Z"
retryRequestedAt: "2026-06-22T06:17:48Z"
retryRequestedBy: agent.company.project-manager
retryReason: "Development Agent fixed Product final acceptance defect: raw status values in detail DOM; Test Agent must run regression for V1 single-machine closed-loop workbench."
retryHistory:
  - {"fromStatus":"changes_requested","reason":"Development Agent fixed DEFECT-001 status localization; Test Agent must run regression and update V1 single-machine closed-loop acceptance.","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T05:47:48Z"}
  - {"fromStatus":"waiting_acceptance","reason":"Development Agent fixed Product final acceptance defect: raw status values in detail DOM; Test Agent must run regression for V1 single-machine closed-loop workbench.","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T06:17:48Z"}
failureReasons:
  - Development Agent fixed DEFECT-001 status localization; Test Agent must run regression and update V1 single-machine closed-loop acceptance.
  - Development Agent fixed Product final acceptance defect: raw status values in detail DOM; Test Agent must run regression for V1 single-machine closed-loop workbench.
nextAction: 交给 agent.company.product-manager 做产品最终验收。
---

## Request

测试验收 V1 工作台 Codex 风格中文界面

## Source Materials

- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-dev.md
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html

## Expected Output

- 测试 Agent 验证中文可读、状态正确、真实数据可见、工作台校验通过

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: agent.company.test
- to: agent.company.product-manager
- requiredArtifacts:
  - test conclusion
  - defect list
  - release recommendation
  - blockers
- handoffSummary: 第 3 轮回归通过；DEFECT-002 raw status detail DOM 已关闭，允许进入产品最终验收。

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.
