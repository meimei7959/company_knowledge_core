---
type: ProjectTask
title: 桢知科技官网 项目初始化
description: ProjectTask assigned to agent.zknowai-official-website.project-manager.
timestamp: "2026-06-25T03:09:35Z"
taskId: project-init-zknowai-official-website
taskType: project_initialization
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"project_initialization","category":"project","stage":"","requiredCapabilities":["project_initialization"],"requiredTools":[],"sourceRefs":["projects/zknowai-official-website/launch.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project_management","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: zknowai-official-website
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
requester: 梅晓华
assignee: agent.zknowai-official-website.project-manager
status: waiting_runner
priority: normal
dueAt: ""
sourceMaterialRefs:
  - projects/zknowai-official-website/launch.md
expectedOutput:
  - 确认项目范围、里程碑、Agent 团队、Runner、仓库、项目群和首批任务。
  - 写回 TaskResult，说明交接、阻塞和第一批可执行任务队列。
resultRef: ""
notificationRefs:
  - notifications/notification.20260625T030935025662Z.md
  - notifications/notification.20260625T030935026948Z.md
auditRefs: []
assignedRunner: ""
executorAgent: agent.zknowai-official-website.project-manager
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
updatedAt: "2026-06-25T03:09:35Z"
---

## Request

桢知科技官网 项目初始化

## Work Source

- workSourceType: maintenance
- requirementRefs: none
- defectRefs: none
- sourceReason: none
- researchQuestion: none

## Source Materials

- projects/zknowai-official-website/launch.md

## Expected Output

- 确认项目范围、里程碑、Agent 团队、Runner、仓库、项目群和首批任务。
- 写回 TaskResult，说明交接、阻塞和第一批可执行任务队列。

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
