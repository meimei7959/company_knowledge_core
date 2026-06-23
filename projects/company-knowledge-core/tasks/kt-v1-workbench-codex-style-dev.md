---
type: ProjectTask
title: 研发实现 V1 工作台 Codex 风格中文界面
description: ProjectTask assigned to agent.company.development.
timestamp: "2026-06-22T04:31:53Z"
taskId: kt-v1-workbench-codex-style-dev
taskType: implementation
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"implementation","category":"engineering","stage":"","requiredCapabilities":["implementation"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-design.md","projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-review.md","projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.development
status: waiting_acceptance
priority: critical
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-design.md
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-review.md
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
expectedOutput:
  - 研发 Agent 实现中文 Codex 风格工作台，接真实 live read model
resultRef: task-results/tr-kt-v1-workbench-codex-style-dev.md
notificationRefs:
  - notifications/notification.20260622T043153533528Z.md
  - notifications/notification.20260622T052716672834Z.md
  - notifications/notification.20260622T052716673669Z.md
  - notifications/notification.20260622T052716674423Z.md
  - notifications/notification.20260622T054143418222Z.md
  - notifications/notification.20260622T054602581075Z.md
  - notifications/notification.20260622T054602581937Z.md
  - notifications/notification.20260622T054602582633Z.md
  - notifications/notification.20260622T060614118095Z.md
  - notifications/notification.20260622T061636515741Z.md
  - notifications/notification.20260622T061636516622Z.md
  - notifications/notification.20260622T061636517320Z.md
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
taskVersion: 3
handoffContract: {"from":"agent.company.development","to":"agent.company.test","requiredArtifacts":["technical plan","change summary","self-test result","risk notes"]}
qualityGateRequired: true
attemptNumber: 3
maxAttempts: 3
followupTaskRefs: []
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-22T06:16:36Z"
completedAt: "2026-06-22T06:16:36Z"
retryRequestedAt: "2026-06-22T06:06:14Z"
retryRequestedBy: agent.company.project-manager
retryReason: Product final acceptance found raw status values in DOM detail fields (<dd>offline</dd>, <dd>done</dd>); Development Agent must localize detail value rendering and add regression coverage.
retryHistory:
  - {"fromStatus":"waiting_acceptance","reason":"Test Agent found DEFECT-001: Runner history statuses retried/escalated render as English; Development Agent must repair Chinese status mapping before regression.","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T05:41:43Z"}
  - {"fromStatus":"waiting_acceptance","reason":"Product final acceptance found raw status values in DOM detail fields (<dd>offline</dd>, <dd>done</dd>); Development Agent must localize detail value rendering and add regression coverage.","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T06:06:14Z"}
failureReasons:
  - Test Agent found DEFECT-001: Runner history statuses retried/escalated render as English; Development Agent must repair Chinese status mapping before regression.
  - Product final acceptance found raw status values in DOM detail fields (<dd>offline</dd>, <dd>done</dd>); Development Agent must localize detail value rendering and add regression coverage.
nextAction: Runner should claim the retry lease and write back fresh evidence.
---

## Request

研发实现 V1 工作台 Codex 风格中文界面

## Source Materials

- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-design.md
- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-review.md
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js

## Expected Output

- 研发 Agent 实现中文 Codex 风格工作台，接真实 live read model

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: agent.company.development
- to: agent.company.test
- requiredArtifacts:
  - technical plan
  - change summary
  - self-test result
  - risk notes

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.
