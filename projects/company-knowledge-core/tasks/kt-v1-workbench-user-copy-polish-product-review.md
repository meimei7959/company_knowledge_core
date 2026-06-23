---
type: ProjectTask
title: 产品复验 V1 工作台用户可读中文文案
description: ProjectTask assigned to agent.company.product-manager.
timestamp: "2026-06-22T08:51:52Z"
taskId: kt-v1-workbench-user-copy-polish-product-review
taskType: product_review
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"product_review","category":"project","stage":"","requiredCapabilities":["product_review"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-v1-workbench-user-copy-polish-test.md","task-results/tr-kt-v1-workbench-user-copy-polish-test.md","projects/company-knowledge-core/test-reports/v1-workbench-user-copy-polish-test-report.md","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.product-manager
status: waiting_acceptance
priority: critical
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-user-copy-polish-test.md
  - task-results/tr-kt-v1-workbench-user-copy-polish-test.md
  - projects/company-knowledge-core/test-reports/v1-workbench-user-copy-polish-test-report.md
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
expectedOutput:
  - 产品经理 Agent 从用户视角复验 V1 工作台中文文案、主Agent术语、路由链路表达是否满足用户理解
resultRef: task-results/tr-kt-v1-workbench-user-copy-polish-product-review.md
notificationRefs:
  - notifications/notification.20260622T085152049043Z.md
  - notifications/notification.20260622T111648583903Z.md
  - notifications/notification.20260622T112050432098Z.md
  - notifications/notification.20260622T112050433406Z.md
  - notifications/notification.20260622T112050434359Z.md
auditRefs: []
assignedRunner: ""
executorAgent: agent.company.product-manager
leaseOwner: ""
leaseTokenHash: ""
leaseProofHash: ""
leaseIssuedAt: ""
leaseExpiresAt: ""
leaseHeartbeatAt: ""
leaseVersion: 1
leaseAttempt: 0
heartbeatAt: ""
taskVersion: 2
handoffContract: {"from":"","to":"","requiredArtifacts":["summary","evidence refs","next action or terminal reason"]}
qualityGateRequired: true
attemptNumber: 2
maxAttempts: 3
followupTaskRefs: []
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-22T11:20:50Z"
retryRequestedAt: "2026-06-22T11:16:48Z"
retryRequestedBy: agent.company.project-manager
retryReason: Test Agent final regression passed after project selector and user-facing copy repairs; Product Agent must re-review user perspective and route-chain clarity.
retryHistory:
  - {"fromStatus":"pending","reason":"Test Agent final regression passed after project selector and user-facing copy repairs; Product Agent must re-review user perspective and route-chain clarity.","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T11:16:48Z"}
failureReasons:
  - Test Agent final regression passed after project selector and user-facing copy repairs; Product Agent must re-review user perspective and route-chain clarity.
nextAction: Runner should claim the retry lease and write back fresh evidence.
completedAt: "2026-06-22T11:20:50Z"
---

## Request

产品复验 V1 工作台用户可读中文文案

## Source Materials

- projects/company-knowledge-core/tasks/kt-v1-workbench-user-copy-polish-test.md
- task-results/tr-kt-v1-workbench-user-copy-polish-test.md
- projects/company-knowledge-core/test-reports/v1-workbench-user-copy-polish-test-report.md
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js

## Expected Output

- 产品经理 Agent 从用户视角复验 V1 工作台中文文案、主Agent术语、路由链路表达是否满足用户理解

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: current assignee
- to: terminal or project manager decision
- requiredArtifacts:
  - summary
  - evidence refs
  - next action or terminal reason

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.
