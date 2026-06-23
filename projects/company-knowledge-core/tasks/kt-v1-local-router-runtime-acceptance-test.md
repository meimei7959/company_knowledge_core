---
type: ProjectTask
title: V1 acceptance test task - Local Router runtime proof
description: ProjectTask assigned to agent.company.test.
timestamp: "2026-06-22T03:19:27Z"
taskId: kt-v1-local-router-runtime-acceptance-test
taskType: testing
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"testing","category":"testing","stage":"testing","requiredCapabilities":["testing"],"requiredTools":[],"sourceRefs":["task-results/tr-kt-v1-local-router-runtime-acceptance-dev.md","runtime/worktrees/worktree.kt-v1-local-router-runtime-acceptance-dev.agent.company.development.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"testing","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.test
status: done
priority: critical
dueAt: ""
sourceMaterialRefs:
  - task-results/tr-kt-v1-local-router-runtime-acceptance-dev.md
  - runtime/worktrees/worktree.kt-v1-local-router-runtime-acceptance-dev.agent.company.development.md
expectedOutput:
  - Acceptance test report with pass/fail evidence.
resultRef: task-results/tr-kt-v1-local-router-runtime-acceptance-test.md
notificationRefs:
  - notifications/notification.20260622T031927633386Z.md
  - notifications/notification.20260622T031927636702Z.md
  - notifications/notification.20260622T031927639774Z.md
  - notifications/notification.20260622T031927640490Z.md
  - notifications/notification.20260622T031927641107Z.md
  - notifications/notification.20260622T034607256854Z.md
auditRefs: []
assignedRunner: runner.v1.local.test
executorAgent: agent.company.test
leaseOwner: runner.v1.local.test
leaseTokenHash: b2f1da9d3d6bdc1fe9894ffc8f6f08a99ff5609dbaba2536b556abcf492bf330
leaseProofHash: b2f1da9d3d6bdc1fe9894ffc8f6f08a99ff5609dbaba2536b556abcf492bf330
leaseIssuedAt: "2026-06-22T03:19:27Z"
leaseExpiresAt: "2026-06-22T03:29:27Z"
leaseHeartbeatAt: "2026-06-22T03:19:27Z"
leaseVersion: 2
leaseAttempt: 1
heartbeatAt: "2026-06-22T03:19:27Z"
taskVersion: 2
handoffContract: {"from":"agent.company.test","to":"agent.company.project-manager","requiredArtifacts":["test conclusion","defect list","release recommendation","blockers"]}
qualityGateRequired: true
attemptNumber: 1
maxAttempts: 3
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-v1-local-router-runtime-acceptance-test-handoff.md
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-22T03:46:07Z"
currentStage: testing
requiredCapabilities:
  - testing
technicalSolutionRequired: false
completedAt: "2026-06-22T03:19:27Z"
---

## Request

V1 acceptance test task - Local Router runtime proof

## Source Materials

- task-results/tr-kt-v1-local-router-runtime-acceptance-dev.md
- runtime/worktrees/worktree.kt-v1-local-router-runtime-acceptance-dev.agent.company.development.md

## Expected Output

- Acceptance test report with pass/fail evidence.

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
