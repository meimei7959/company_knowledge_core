---
type: ProjectTask
title: 项目经理最终验收 V1 工作台 Agent 体系执行链路
description: ProjectTask assigned to agent.company.project-manager.
timestamp: "2026-06-22T04:34:09Z"
taskId: kt-v1-workbench-codex-style-pm-final-acceptance
taskType: acceptance
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"acceptance","category":"project","stage":"","requiredCapabilities":["acceptance"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-design.md","projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-review.md","projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-dev.md","projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-test.md","projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-final-acceptance.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.project-manager
status: waiting_acceptance
priority: critical
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-design.md
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-review.md
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-dev.md
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-test.md
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-final-acceptance.md
expectedOutput:
  - 项目经理 Agent 只基于各岗位 TaskResult 做流程验收，确认没有主线程越权代工、没有跳过产品/研发/测试结论
resultRef: task-results/tr-kt-v1-workbench-codex-style-pm-final-acceptance.md
notificationRefs:
  - notifications/notification.20260622T043409710321Z.md
  - notifications/notification.20260622T063428645843Z.md
  - notifications/notification.20260622T063428648261Z.md
  - notifications/notification.20260622T063716661967Z.md
  - notifications/notification.20260622T063716662826Z.md
  - notifications/notification.20260622T063716663557Z.md
auditRefs: []
assignedRunner: ""
executorAgent: agent.company.project-manager
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
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-pm-final-acceptance-retry.md
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-22T06:37:16Z"
completedAt: "2026-06-22T06:37:16Z"
improvementRefs:
  - knowledge/agent-improvements/agent-improvement.20260622T063428647236Z.md
---

## Request

项目经理最终验收 V1 工作台 Agent 体系执行链路

## Source Materials

- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-design.md
- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-review.md
- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-dev.md
- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-test.md
- projects/company-knowledge-core/tasks/kt-v1-workbench-codex-style-product-final-acceptance.md

## Expected Output

- 项目经理 Agent 只基于各岗位 TaskResult 做流程验收，确认没有主线程越权代工、没有跳过产品/研发/测试结论

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
