---
type: ProjectTask
title: 产品评审 V1 工作台 Codex 风格设计
description: ProjectTask assigned to agent.company.product-manager.
timestamp: "2026-06-22T04:31:53Z"
taskId: kt-v1-workbench-codex-style-product-review
taskType: product_review
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"product_review","category":"project","stage":"","requiredCapabilities":["product_review"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-design.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.product-manager
status: waiting_acceptance
priority: critical
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-design.md
expectedOutput:
  - 产品经理 Agent 判断设计是否满足用户看懂 Agent 系统运行状态
resultRef: task-results/tr-kt-v1-workbench-codex-style-product-review.md
notificationRefs:
  - notifications/notification.20260622T043153538818Z.md
  - notifications/notification.20260622T051212877290Z.md
  - notifications/notification.20260622T051212878124Z.md
  - notifications/notification.20260622T051212878888Z.md
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
attemptNumber: 1
maxAttempts: 3
followupTaskRefs: []
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-22T05:12:12Z"
completedAt: "2026-06-22T05:12:12Z"
---

## Request

产品评审 V1 工作台 Codex 风格设计

## Source Materials

- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-design.md

## Expected Output

- 产品经理 Agent 判断设计是否满足用户看懂 Agent 系统运行状态

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
