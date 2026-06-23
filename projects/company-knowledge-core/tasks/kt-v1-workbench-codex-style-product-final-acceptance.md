---
type: ProjectTask
title: 产品最终验收 V1 工作台 Codex 风格中文界面
description: ProjectTask assigned to agent.company.product-manager.
timestamp: "2026-06-22T04:34:09Z"
taskId: kt-v1-workbench-codex-style-product-final-acceptance
taskType: product_review
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"product_review","category":"project","stage":"","requiredCapabilities":["product_review"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-test.md","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.product-manager
status: waiting_acceptance
priority: critical
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-test.md
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css
expectedOutput:
  - 产品经理 Agent 基于测试证据确认工作台是否满足中文可读、Codex 风格、真实运行状态可见、V1 单机闭环验收口径
resultRef: task-results/tr-kt-v1-workbench-codex-style-product-final-acceptance.md
notificationRefs:
  - notifications/notification.20260622T043409710095Z.md
  - notifications/notification.20260622T060450262014Z.md
  - notifications/notification.20260622T060450264567Z.md
  - notifications/notification.20260622T060450265296Z.md
  - notifications/notification.20260622T062414410501Z.md
  - notifications/notification.20260622T063000204869Z.md
  - notifications/notification.20260622T063000205746Z.md
  - notifications/notification.20260622T063000206446Z.md
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
taskVersion: 2
handoffContract: {"from":"","to":"","requiredArtifacts":["summary","evidence refs","next action or terminal reason"]}
qualityGateRequired: true
attemptNumber: 2
maxAttempts: 3
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-final-acceptance-retry.md
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-22T06:30:00Z"
completedAt: "2026-06-22T06:30:00Z"
improvementRefs:
  - knowledge/agent-improvements/agent-improvement.20260622T060450263500Z.md
retryRequestedAt: "2026-06-22T06:24:14Z"
retryRequestedBy: agent.company.project-manager
retryReason: Test Agent third regression passed after DEFECT-002 fix; Product Agent must re-run final acceptance for V1 single-machine closed-loop Codex-style Chinese workbench.
retryHistory:
  - {"fromStatus":"changes_requested","reason":"Test Agent third regression passed after DEFECT-002 fix; Product Agent must re-run final acceptance for V1 single-machine closed-loop Codex-style Chinese workbench.","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T06:24:14Z"}
failureReasons:
  - Test Agent third regression passed after DEFECT-002 fix; Product Agent must re-run final acceptance for V1 single-machine closed-loop Codex-style Chinese workbench.
nextAction: Runner should claim the retry lease and write back fresh evidence.
---

## Request

产品最终验收 V1 工作台 Codex 风格中文界面

## Source Materials

- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-test.md
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css

## Expected Output

- 产品经理 Agent 基于测试证据确认工作台是否满足中文可读、Codex 风格、真实运行状态可见、V1 单机闭环验收口径

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
