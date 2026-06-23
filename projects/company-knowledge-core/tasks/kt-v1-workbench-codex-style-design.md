---
type: ProjectTask
title: V1 工作台 Codex 风格中文设计方案
description: ProjectTask assigned to agent.company.design.
timestamp: "2026-06-22T04:31:53Z"
taskId: kt-v1-workbench-codex-style-design
taskType: design
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"design","category":"project","stage":"","requiredCapabilities":["design"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css","projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.design
status: waiting_acceptance
priority: critical
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
expectedOutput:
  - 中文 Codex 风格信息架构、首页/运行监控/Agent/Runner/验收视图设计方案
resultRef: task-results/tr-kt-v1-workbench-codex-style-design.md
notificationRefs:
  - notifications/notification.20260622T043153520886Z.md
  - notifications/notification.20260622T050703020976Z.md
  - notifications/notification.20260622T050703022043Z.md
  - notifications/notification.20260622T050703022738Z.md
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
updatedAt: "2026-06-22T05:07:03Z"
completedAt: "2026-06-22T05:07:03Z"
---

## Request

V1 工作台 Codex 风格中文设计方案

## Source Materials

- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js

## Expected Output

- 中文 Codex 风格信息架构、首页/运行监控/Agent/Runner/验收视图设计方案

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
