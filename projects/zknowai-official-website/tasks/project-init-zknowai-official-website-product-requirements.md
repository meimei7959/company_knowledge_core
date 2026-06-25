---
type: ProjectTask
title: 产品经理结构化新项目需求和 V1 范围
description: ProjectTask assigned to agent.company.product-manager.
timestamp: "2026-06-25T03:09:35Z"
taskId: project-init-zknowai-official-website-product-requirements
taskType: product_requirement
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"product_requirement","category":"product","stage":"","requiredCapabilities":["product_requirement"],"requiredTools":[],"sourceRefs":["projects/zknowai-official-website/sources/source.20260625T030935030481Z.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"product_requirement","acceptancePath":"pm_review","reviewPath":"product_prd_gate","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: zknowai-official-website
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
requester: 梅晓华
assignee: agent.company.product-manager
status: pending
priority: normal
dueAt: ""
sourceMaterialRefs:
  - projects/zknowai-official-website/sources/source.20260625T030935030481Z.md
expectedOutput:
  - Requirement tree, V1 scope, and acceptance criteria are ready.
resultRef: ""
notificationRefs:
  - notifications/notification.20260625T030935032179Z.md
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
handoffContract: {"from":"agent.company.product-manager","to":"agent.company.design","requiredArtifacts":["requirement brief","user scenarios","acceptance criteria","boundary conditions"]}
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

产品经理结构化新项目需求和 V1 范围

## Work Source

- workSourceType: project_setup
- requirementRefs: PROJECT-INIT
- defectRefs: none
- sourceReason: Project Manager generated a profile-based first task queue for workspaceProfile=development. This is a PM-confirmation queue; downstream agents must produce receiver review before formal execution.
- researchQuestion: none

## Source Materials

- projects/zknowai-official-website/sources/source.20260625T030935030481Z.md

## Expected Output

- Requirement tree, V1 scope, and acceptance criteria are ready.

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: agent.company.product-manager
- to: agent.company.design
- requiredArtifacts:
  - requirement brief
  - user scenarios
  - acceptance criteria
  - boundary conditions

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.
