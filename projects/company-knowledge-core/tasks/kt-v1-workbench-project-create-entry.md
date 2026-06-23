---
type: ProjectTask
title: 实现工作台新建项目入口
description: ProjectTask assigned to agent.company.development.
timestamp: "2026-06-22T11:41:35Z"
taskId: kt-v1-workbench-project-create-entry
taskType: implementation
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"implementation","category":"engineering","stage":"","requiredCapabilities":["implementation"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css","projects/company-knowledge-core/desktop-workbench-slice0/shared-frontend-foundation.ts"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.development
status: waiting_acceptance
priority: critical
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css
  - projects/company-knowledge-core/desktop-workbench-slice0/shared-frontend-foundation.ts
expectedOutput:
  - 研发 Agent 在工作台实现中文新建项目入口、项目选择器说明、项目创建包预览、受控提交/复制入口，并补 validator/test 防回归
resultRef: task-results/tr-kt-v1-workbench-project-create-entry.md
notificationRefs:
  - notifications/notification.20260622T114135272024Z.md
  - notifications/notification.20260622T114726638787Z.md
  - notifications/notification.20260622T114726640393Z.md
  - notifications/notification.20260622T114726641179Z.md
auditRefs: []
assignedRunner: ""
executorAgent: agent.company.development
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
handoffContract: {"from":"agent.company.development","to":"agent.company.architecture","requiredArtifacts":["implementation plan","change summary","self-test result","risk notes"]}
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
updatedAt: "2026-06-22T11:47:26Z"
completedAt: "2026-06-22T11:47:26Z"
---

## Request

实现工作台新建项目入口

## Source Materials

- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css
- projects/company-knowledge-core/desktop-workbench-slice0/shared-frontend-foundation.ts

## Expected Output

- 研发 Agent 在工作台实现中文新建项目入口、项目选择器说明、项目创建包预览、受控提交/复制入口，并补 validator/test 防回归

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: agent.company.development
- to: agent.company.architecture
- requiredArtifacts:
  - implementation plan
  - change summary
  - self-test result
  - risk notes

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.
