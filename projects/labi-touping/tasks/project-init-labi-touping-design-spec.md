---
type: ProjectTask
title: 设计 Agent 输出界面体验和交互规范
description: ProjectTask assigned to agent.company.design.
timestamp: "2026-06-24T11:40:05Z"
taskId: project-init-labi-touping-design-spec
taskType: design_spec
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"design_spec","category":"design","stage":"","requiredCapabilities":["design_spec"],"requiredTools":[],"sourceRefs":["projects/labi-touping/sources/source.20260624T114005757381Z.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"design_spec","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: labi-touping
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
sourceReason: Project Manager generated a profile-based first task queue for workspaceProfile=development. This is a PM-confirmation queue; downstream agents must produce receiver review before formal execution.
receiverReviewRefs: []
requester: agent.company.project-manager
assignee: agent.company.design
status: pending
priority: normal
dueAt: ""
sourceMaterialRefs:
  - projects/labi-touping/sources/source.20260624T114005757381Z.md
expectedOutput:
  - Human-readable UI/UX design spec is ready when the product has user-facing screens.
  - Design spec must cover mobile App screens, PC client screens, cross-device pairing/casting flow, empty/error/loading states, and user-readable Chinese copy.
resultRef: ""
notificationRefs:
  - notifications/notification.20260624T114005759709Z.md
auditRefs: []
assignedRunner: ""
executorAgent: agent.company.design
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
handoffContract: {"from":"agent.company.design","to":"agent.company.architecture","requiredArtifacts":["flow/state spec","interaction rules","edge states","implementation notes"]}
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
updatedAt: "2026-06-24T11:40:05Z"
---

## Request

设计 Agent 输出界面体验和交互规范

## Work Source

- workSourceType: project_setup
- requirementRefs: PROJECT-INIT
- defectRefs: none
- sourceReason: Project Manager generated a profile-based first task queue for workspaceProfile=development. This is a PM-confirmation queue; downstream agents must produce receiver review before formal execution.
- researchQuestion: none

## Source Materials

- projects/labi-touping/sources/source.20260624T114005757381Z.md

## Expected Output

- Human-readable UI/UX design spec is ready when the product has user-facing screens.
- Design spec must cover mobile App screens, PC client screens, cross-device pairing/casting flow, empty/error/loading states, and user-readable Chinese copy.

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: agent.company.design
- to: agent.company.architecture
- requiredArtifacts:
  - flow/state spec
  - interaction rules
  - edge states
  - implementation notes

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.
