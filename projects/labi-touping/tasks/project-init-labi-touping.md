---
type: ProjectTask
title: "Initialize project: 蜡笔投屏"
description: ProjectTask assigned to agent.labi-touping.project-manager.
timestamp: "2026-06-24T11:40:05Z"
taskId: project-init-labi-touping
taskType: project_initialization
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"project_initialization","category":"project","stage":"","requiredCapabilities":["project_initialization"],"requiredTools":[],"sourceRefs":["projects/labi-touping/launch.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project_management","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: labi-touping
workSourceType: maintenance
requirementRefs: []
requirementObjectRefs: []
acceptanceCriteriaRefs: []
defectRefs: []
defectObjectRefs: []
incidentRefs: []
operationRefs: []
knowledgeTaskRefs: []
researchQuestion: ""
sourceReason: ""
receiverReviewRefs: []
requester: agent.company.project-manager
assignee: agent.labi-touping.project-manager
status: waiting_runner
priority: normal
dueAt: ""
sourceMaterialRefs:
  - projects/labi-touping/launch.md
expectedOutput:
  - Confirm project scope, milestones, Agent team, Runner, repo, project group, and first tasks.
  - Write TaskResult with handoff, blockers, and first executable backlog.
resultRef: ""
notificationRefs:
  - notifications/notification.20260624T114005755326Z.md
  - notifications/notification.20260624T114005756698Z.md
auditRefs: []
assignedRunner: ""
executorAgent: agent.labi-touping.project-manager
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
handoffContract: {"from":"agent.company.project-manager","to":"agent.company.product-manager","requiredArtifacts":["project goal","scope","priority","constraints","milestones"]}
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

Initialize project: 蜡笔投屏

## Work Source

- workSourceType: maintenance
- requirementRefs: none
- defectRefs: none
- sourceReason: none
- researchQuestion: none

## Source Materials

- projects/labi-touping/launch.md

## Expected Output

- Confirm project scope, milestones, Agent team, Runner, repo, project group, and first tasks.
- Write TaskResult with handoff, blockers, and first executable backlog.

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: agent.company.project-manager
- to: agent.company.product-manager
- requiredArtifacts:
  - project goal
  - scope
  - priority
  - constraints
  - milestones

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.
