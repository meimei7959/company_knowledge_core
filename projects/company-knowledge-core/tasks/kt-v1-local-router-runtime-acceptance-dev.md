---
type: ProjectTask
title: V1 acceptance development task - Local Router runtime proof
description: ProjectTask assigned to agent.company.development.
timestamp: "2026-06-22T03:19:27Z"
taskId: kt-v1-local-router-runtime-acceptance-dev
taskType: implementation
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"implementation","category":"engineering","stage":"implementation","requiredCapabilities":["implementation"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/product-reviews/ai-native-agent-v1-executable-product-package.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.development
status: done
priority: critical
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/product-reviews/ai-native-agent-v1-executable-product-package.md
expectedOutput:
  - Runtime proof result and worktree binding.
resultRef: task-results/tr-kt-v1-local-router-runtime-acceptance-dev.md
notificationRefs:
  - notifications/notification.20260622T031927610699Z.md
  - notifications/notification.20260622T031927615002Z.md
  - notifications/notification.20260622T031927618887Z.md
  - notifications/notification.20260622T031927619746Z.md
  - notifications/notification.20260622T031927620486Z.md
  - notifications/notification.20260622T034607233583Z.md
auditRefs: []
assignedRunner: runner.v1.local.dev
executorAgent: agent.company.development
leaseOwner: runner.v1.local.dev
leaseTokenHash: cf76834a41fc5d596d3823e03081c3994eb32a80258d2055894f3b629556d105
leaseProofHash: cf76834a41fc5d596d3823e03081c3994eb32a80258d2055894f3b629556d105
leaseIssuedAt: "2026-06-22T03:19:27Z"
leaseExpiresAt: "2026-06-22T03:29:27Z"
leaseHeartbeatAt: "2026-06-22T03:19:27Z"
leaseVersion: 2
leaseAttempt: 1
heartbeatAt: "2026-06-22T03:19:27Z"
taskVersion: 2
handoffContract: {"from":"agent.company.development","to":"agent.company.test","requiredArtifacts":["technical plan","change summary","self-test result","risk notes"]}
qualityGateRequired: true
attemptNumber: 1
maxAttempts: 3
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-v1-local-router-runtime-acceptance-dev-handoff.md
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-22T03:46:07Z"
currentStage: implementation
requiredCapabilities:
  - implementation
technicalSolutionRequired: false
completedAt: "2026-06-22T03:19:27Z"
---

## Request

V1 acceptance development task - Local Router runtime proof

## Source Materials

- projects/company-knowledge-core/product-reviews/ai-native-agent-v1-executable-product-package.md

## Expected Output

- Runtime proof result and worktree binding.

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
