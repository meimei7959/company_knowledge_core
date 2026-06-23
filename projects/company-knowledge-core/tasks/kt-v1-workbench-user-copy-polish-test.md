---
type: ProjectTask
title: 测试验收 V1 工作台用户可读中文文案
description: ProjectTask assigned to agent.company.test.
timestamp: "2026-06-22T08:45:23Z"
taskId: kt-v1-workbench-user-copy-polish-test
taskType: testing
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"testing","category":"testing","stage":"","requiredCapabilities":["testing"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-v1-workbench-user-copy-polish.md","task-results/tr-kt-v1-workbench-user-copy-polish.md","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js","projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js","projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"testing","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.test
status: waiting_acceptance
priority: critical
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-user-copy-polish.md
  - task-results/tr-kt-v1-workbench-user-copy-polish.md
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
expectedOutput:
  - 测试 Agent 从用户视角验证用户可见文案中文化、主Agent术语统一、路由链路可读、英文内部术语不再直出
resultRef: task-results/tr-kt-v1-workbench-user-copy-polish-test.md
notificationRefs:
  - notifications/notification.20260622T084523986946Z.md
  - notifications/notification.20260622T084939086426Z.md
  - notifications/notification.20260622T084939087268Z.md
  - notifications/notification.20260622T084939088192Z.md
  - notifications/notification.20260622T085033619214Z.md
  - notifications/notification.20260622T085100821656Z.md
  - notifications/notification.20260622T085100822537Z.md
  - notifications/notification.20260622T085100823245Z.md
  - notifications/notification.20260622T092106138425Z.md
  - notifications/notification.20260622T092510819661Z.md
  - notifications/notification.20260622T092510823259Z.md
  - notifications/notification.20260622T092510826026Z.md
  - notifications/notification.20260622T110750336007Z.md
  - notifications/notification.20260622T111534225790Z.md
  - notifications/notification.20260622T111534227365Z.md
  - notifications/notification.20260622T111534228462Z.md
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
taskVersion: 4
handoffContract: {"from":"agent.company.test","to":"agent.company.project-manager","requiredArtifacts":["test conclusion","defect list","release recommendation","blockers"]}
qualityGateRequired: true
attemptNumber: 3
maxAttempts: 3
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-user-copy-polish-test-retry.md
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-22T11:15:34Z"
completedAt: "2026-06-22T11:15:34Z"
manualHandoff: {"handoffTo":"agent.company.product-manager","summary":"测试通过，无缺陷；路由链路完整，可进入产品复验。","nextAction":"请产品经理 Agent 从用户理解角度做产品复验。","preferredRunner":"","handoffRef":"projects/company-knowledge-core/handoff.kt-v1-workbench-user-copy-polish-test.manual.20260622T085033617863Z.md","createdAt":"2026-06-22T08:50:33Z","createdBy":"agent.company.test"}
handoffRefs:
  - projects/company-knowledge-core/handoff.kt-v1-workbench-user-copy-polish-test.manual.20260622T085033617863Z.md
nextAction: Runner should claim the retry lease and write back fresh evidence.
retryRequestedAt: "2026-06-22T11:07:50Z"
retryRequestedBy: agent.company.project-manager
retryReason: Development Agent repaired log.md whitespace blocker after user-copy polish; Test Agent must rerun full regression and quality gates for project selector, user-facing copy, and route chain display.
retryHistory:
  - {"fromStatus":"waiting_acceptance","reason":"Development Agent third pass added project selector and user-facing routing copy; Test Agent must regress project selector, user-language copy, hidden internal ids, and route chain display.","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T09:21:06Z"}
  - {"fromStatus":"changes_requested","reason":"Development Agent repaired log.md whitespace blocker after user-copy polish; Test Agent must rerun full regression and quality gates for project selector, user-facing copy, and route chain display.","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T11:07:50Z"}
failureReasons:
  - Development Agent third pass added project selector and user-facing routing copy; Test Agent must regress project selector, user-language copy, hidden internal ids, and route chain display.
  - Development Agent repaired log.md whitespace blocker after user-copy polish; Test Agent must rerun full regression and quality gates for project selector, user-facing copy, and route chain display.
improvementRefs:
  - knowledge/agent-improvements/agent-improvement.20260622T092510822175Z.md
---

## Request

测试验收 V1 工作台用户可读中文文案

## Source Materials

- projects/company-knowledge-core/tasks/kt-v1-workbench-user-copy-polish.md
- task-results/tr-kt-v1-workbench-user-copy-polish.md
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js

## Expected Output

- 测试 Agent 从用户视角验证用户可见文案中文化、主Agent术语统一、路由链路可读、英文内部术语不再直出

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: agent.company.test
- to: agent.company.project-manager
- requiredArtifacts:
  - test conclusion
  - defect list
  - release recommendation
  - blockers

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.
