---
type: ProjectTask
title: Retry task output for kt-v1-workbench-codex-style-product-final-acceptance
description: ProjectTask assigned to agent.company.product-manager.
timestamp: "2026-06-22T06:04:50Z"
taskId: kt-v1-workbench-codex-style-product-final-acceptance-retry
taskType: product_review
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"product_review","category":"project","stage":"","requiredCapabilities":["product_review"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-test.md","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css","task-results/tr-kt-v1-workbench-codex-style-product-final-acceptance.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.product-manager
status: pending
priority: critical
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-test.md
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css
  - task-results/tr-kt-v1-workbench-codex-style-product-final-acceptance.md
expectedOutput:
  - Repair the failed output according to qualityEvaluation reasons.
  - Return TaskResult with evidence/artifacts and handoff contract.
resultRef: ""
notificationRefs:
  - notifications/notification.20260622T060450278987Z.md
  - notifications/notification.20260622T060450279860Z.md
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
taskVersion: 1
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
updatedAt: "2026-06-22T06:04:50Z"
parentTaskId: kt-v1-workbench-codex-style-product-final-acceptance
originTaskId: kt-v1-workbench-codex-style-product-final-acceptance
retryOf: kt-v1-workbench-codex-style-product-final-acceptance
triggerResultRef: task-results/tr-kt-v1-workbench-codex-style-product-final-acceptance.md
qualityGate: failed
failureReasons:
  - tests/checks reported failure
---

## Request

Retry task output for kt-v1-workbench-codex-style-product-final-acceptance

## Source Materials

- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-test.md
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css
- task-results/tr-kt-v1-workbench-codex-style-product-final-acceptance.md

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
