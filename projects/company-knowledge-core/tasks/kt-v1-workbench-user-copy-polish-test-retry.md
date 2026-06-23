---
type: ProjectTask
title: Retry task output for kt-v1-workbench-user-copy-polish-test
description: ProjectTask assigned to agent.company.test.
timestamp: "2026-06-22T09:25:10Z"
taskId: kt-v1-workbench-user-copy-polish-test-retry
taskType: testing
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"testing","category":"testing","stage":"","requiredCapabilities":["testing"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-v1-workbench-user-copy-polish.md","task-results/tr-kt-v1-workbench-user-copy-polish.md","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js","projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js","projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js","task-results/tr-kt-v1-workbench-user-copy-polish-test.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"testing","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.test
status: pending
priority: critical
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-user-copy-polish.md
  - task-results/tr-kt-v1-workbench-user-copy-polish.md
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
  - task-results/tr-kt-v1-workbench-user-copy-polish-test.md
expectedOutput:
  - Repair the failed output according to qualityEvaluation reasons.
  - Return TaskResult with evidence/artifacts and handoff contract.
resultRef: ""
notificationRefs:
  - notifications/notification.20260622T092510843293Z.md
  - notifications/notification.20260622T092510844810Z.md
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
taskVersion: 1
handoffContract: {"from":"agent.company.test","to":"agent.company.project-manager","requiredArtifacts":["test conclusion","defect list","release recommendation","blockers"]}
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
updatedAt: "2026-06-22T09:25:10Z"
parentTaskId: kt-v1-workbench-user-copy-polish-test
originTaskId: kt-v1-workbench-user-copy-polish-test
retryOf: kt-v1-workbench-user-copy-polish-test
triggerResultRef: task-results/tr-kt-v1-workbench-user-copy-polish-test.md
qualityGate: failed
failureReasons:
  - tests/checks reported failure
---

## Request

Retry task output for kt-v1-workbench-user-copy-polish-test

## Source Materials

- projects/company-knowledge-core/tasks/kt-v1-workbench-user-copy-polish.md
- task-results/tr-kt-v1-workbench-user-copy-polish.md
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
- task-results/tr-kt-v1-workbench-user-copy-polish-test.md

## Expected Output

- Repair the failed output according to qualityEvaluation reasons.
- Return TaskResult with evidence/artifacts and handoff contract.

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
