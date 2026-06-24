---
type: ProjectTask
title: 测试 Agent 制定交付验收清单
description: ProjectTask assigned to agent.company.test.
timestamp: "2026-06-24T12:37:34Z"
taskId: project-init-billing-lite-test-checklist
taskType: testing
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"testing","category":"testing","stage":"","requiredCapabilities":["testing"],"requiredTools":[],"sourceRefs":["projects/billing-lite/sources/source.20260624T123734337892Z.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"testing","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: billing-lite
workSourceType: project_setup
requirementRefs:
  - PROJECT-INIT
requirementObjectRefs: []
acceptanceCriteriaRefs: []
defectRefs: []
defectObjectRefs: []
incidentRefs: []
operationRefs: []
knowledgeTaskRefs: []
researchQuestion: ""
sourceReason: Project Manager generated a profile-based first task queue for workspaceProfile=delivery. This is a PM-confirmation queue; downstream agents must produce receiver review before formal execution.
receiverReviewRefs: []
requester: 梅晓华
assignee: agent.company.test
status: pending
priority: normal
dueAt: ""
sourceMaterialRefs:
  - projects/billing-lite/sources/source.20260624T123734337892Z.md
expectedOutput:
  - Test checklist covers acceptance criteria and regression route.
resultRef: ""
notificationRefs:
  - notifications/notification.20260624T123734342612Z.md
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
attemptNumber: 1
maxAttempts: 3
followupTaskRefs: []
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
pmControlLeaseId: ""
pmControlLeaseGeneration: ""
pmControlPrimaryPm: ""
pmControlLeaseRef: ""
updatedAt: "2026-06-24T12:37:34Z"
---

## Request

测试 Agent 制定交付验收清单

## Work Source

- workSourceType: project_setup
- requirementRefs: PROJECT-INIT
- defectRefs: none
- sourceReason: Project Manager generated a profile-based first task queue for workspaceProfile=delivery. This is a PM-confirmation queue; downstream agents must produce receiver review before formal execution.
- researchQuestion: none

## Source Materials

- projects/billing-lite/sources/source.20260624T123734337892Z.md

## Expected Output

- Test checklist covers acceptance criteria and regression route.

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
