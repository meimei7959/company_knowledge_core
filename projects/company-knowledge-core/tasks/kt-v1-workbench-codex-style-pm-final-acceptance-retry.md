---
type: ProjectTask
title: Retry task output for kt-v1-workbench-codex-style-pm-final-acceptance
description: ProjectTask assigned to agent.company.project-manager.
timestamp: "2026-06-22T06:34:28Z"
taskId: kt-v1-workbench-codex-style-pm-final-acceptance-retry
taskType: acceptance
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"acceptance","category":"project","stage":"","requiredCapabilities":["acceptance"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-design.md","projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-review.md","projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-dev.md","projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-test.md","projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-final-acceptance.md","task-results/tr-kt-v1-workbench-codex-style-pm-final-acceptance.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.project-manager
status: cancelled
priority: critical
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-design.md
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-review.md
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-dev.md
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-test.md
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-final-acceptance.md
  - task-results/tr-kt-v1-workbench-codex-style-pm-final-acceptance.md
expectedOutput:
  - Repair the failed output according to qualityEvaluation reasons.
  - Return TaskResult with evidence/artifacts and handoff contract.
resultRef: ""
notificationRefs:
  - notifications/notification.20260622T063428662453Z.md
  - notifications/notification.20260622T063428663432Z.md
  - notifications/notification.20260622T063822045002Z.md
auditRefs: []
assignedRunner: ""
executorAgent: agent.company.project-manager
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
updatedAt: "2026-06-22T06:38:22Z"
parentTaskId: kt-v1-workbench-codex-style-pm-final-acceptance
originTaskId: kt-v1-workbench-codex-style-pm-final-acceptance
retryOf: kt-v1-workbench-codex-style-pm-final-acceptance
triggerResultRef: task-results/tr-kt-v1-workbench-codex-style-pm-final-acceptance.md
qualityGate: failed
failureReasons:
  - tests/checks reported failure
cancelledAt: "2026-06-22T06:38:22Z"
cancelledBy: agent.company.project-manager
cancelReason: "Superseded by corrected PM final acceptance TaskResult: task-results/tr-kt-v1-workbench-codex-style-pm-final-acceptance.md now has qualityEvaluation passed/close. This retry was auto-created when repository hygiene risk from log.md trailing whitespace was mistakenly recorded as a failed test check; it is not a V1 closure blocker."
nextAction: Review cancellation reason and create a retry task only if the owner approves.
---

## Request

Retry task output for kt-v1-workbench-codex-style-pm-final-acceptance

## Source Materials

- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-design.md
- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-review.md
- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-dev.md
- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-test.md
- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-final-acceptance.md
- task-results/tr-kt-v1-workbench-codex-style-pm-final-acceptance.md

## Expected Output

- Repair the failed output according to qualityEvaluation reasons.
- Return TaskResult with evidence/artifacts and handoff contract.

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
