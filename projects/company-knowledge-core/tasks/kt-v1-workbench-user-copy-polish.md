---
type: ProjectTask
title: 修复 V1 工作台用户可读中文文案
description: ProjectTask assigned to agent.company.development.
timestamp: "2026-06-22T08:31:20Z"
taskId: kt-v1-workbench-user-copy-polish
taskType: implementation
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"implementation","category":"engineering","stage":"","requiredCapabilities":["implementation"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css","projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
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
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
expectedOutput:
  - 研发 Agent 修复工作台用户可见英文、内部术语和组Agent误写，统一中文用户视角文案，并补 validator/test 防回归
resultRef: task-results/tr-kt-v1-workbench-user-copy-polish.md
notificationRefs:
  - notifications/notification.20260622T083120502514Z.md
  - notifications/notification.20260622T084419909765Z.md
  - notifications/notification.20260622T084419911858Z.md
  - notifications/notification.20260622T084419912935Z.md
  - notifications/notification.20260622T085753381528Z.md
  - notifications/notification.20260622T090853172369Z.md
  - notifications/notification.20260622T090853174201Z.md
  - notifications/notification.20260622T090853175632Z.md
  - notifications/notification.20260622T091015272024Z.md
  - notifications/notification.20260622T092012433949Z.md
  - notifications/notification.20260622T092012436114Z.md
  - notifications/notification.20260622T092012437341Z.md
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
updatedAt: "2026-06-22T09:20:12Z"
completedAt: "2026-06-22T09:20:12Z"
retryRequestedAt: "2026-06-22T09:10:15Z"
retryRequestedBy: agent.company.project-manager
retryReason: "User screenshot shows the workbench is still system-centric, not user-centric: confusing header copy, raw project/runtime ids, deviceId, session ids, raw capability values, and no unified project selector. Development Agent must add a project selector and hide/translate internal fields into user-facing Chinese copy."
retryHistory:
  - {"fromStatus":"waiting_acceptance","reason":"Product review found remaining user-visible English/internal copy in rendered DOM: Run next V1 acceptance stage, Review cancellation reason, Human confirmation queue, Notification center, Projects/Capabilities. Development Agent must systemically localize all user-facing workbench copy and strengthen regression checks.","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T08:57:53Z"}
  - {"fromStatus":"waiting_acceptance","reason":"User screenshot shows the workbench is still system-centric, not user-centric: confusing header copy, raw project/runtime ids, deviceId, session ids, raw capability values, and no unified project selector. Development Agent must add a project selector and hide/translate internal fields into user-facing Chinese copy.","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T09:10:15Z"}
failureReasons:
  - Product review found remaining user-visible English/internal copy in rendered DOM: Run next V1 acceptance stage, Review cancellation reason, Human confirmation queue, Notification center, Projects/Capabilities. Development Agent must systemically localize all user-facing workbench copy and strengthen regression checks.
  - User screenshot shows the workbench is still system-centric, not user-centric: confusing header copy, raw project/runtime ids, deviceId, session ids, raw capability values, and no unified project selector. Development Agent must add a project selector and hide/translate internal fields into user-facing Chinese copy.
nextAction: Runner should claim the retry lease and write back fresh evidence.
---

## Request

修复 V1 工作台用户可读中文文案

## Source Materials

- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js

## Expected Output

- 研发 Agent 修复工作台用户可见英文、内部术语和组Agent误写，统一中文用户视角文案，并补 validator/test 防回归

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
