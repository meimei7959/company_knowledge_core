---
type: ProjectTask
title: AI Native Agent V1 Product Final Acceptance
description: ProjectTask assigned to agent.company.product-manager.
timestamp: "2026-06-22T03:23:34Z"
taskId: kt-ai-native-agent-v1-product-final-acceptance
taskType: product_review
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"product_review","category":"project","stage":"solution_review","requiredCapabilities":["product_review","product_management"],"requiredTools":[],"sourceRefs":["runtime/acceptance-runs/v1.acceptance.20260622t031927643283z.md","task-results/tr-kt-ai-native-agent-v1-test-closed-loop-acceptance.md","task-results/tr-kt-ai-native-agent-v1-pm-product-final-acceptance.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.product-manager
currentStage: solution_review
technicalSolutionRequired: false
requiredCapabilities:
  - product_review
  - product_management
status: done
priority: high
dueAt: ""
sourceMaterialRefs:
  - runtime/acceptance-runs/v1.acceptance.20260622t031927643283z.md
  - task-results/tr-kt-ai-native-agent-v1-test-closed-loop-acceptance.md
  - task-results/tr-kt-ai-native-agent-v1-pm-product-final-acceptance.md
expectedOutput:
  - Product final acceptance verdict for V1 single-machine closed loop.
resultRef: task-results/tr-kt-ai-native-agent-v1-product-final-acceptance.md
notificationRefs:
  - notifications/notification.20260622T032334026499Z.md
  - notifications/notification.20260622T032401735251Z.md
  - notifications/notification.20260622T032401739068Z.md
  - notifications/notification.20260622T032401740041Z.md
  - notifications/notification.20260622T032401740882Z.md
  - notifications/notification.20260622T032527603064Z.md
  - notifications/notification.20260622T032928694175Z.md
  - notifications/notification.20260622T032938703681Z.md
  - notifications/notification.20260622T032938708001Z.md
  - notifications/notification.20260622T032938709014Z.md
  - notifications/notification.20260622T032938709871Z.md
  - notifications/notification.20260622T032945441425Z.md
auditRefs: []
assignedRunner: runner.meimei-mac-local-product-rt
executorAgent: agent.company.product-manager
leaseOwner: runner.meimei-mac-local-product-rt
leaseTokenHash: 58818faf10adabec3d90e22ec31badcfda8a62c73113e2ba28459f63d2e83d17
leaseProofHash: 58818faf10adabec3d90e22ec31badcfda8a62c73113e2ba28459f63d2e83d17
leaseIssuedAt: "2026-06-22T03:29:38Z"
leaseExpiresAt: "2026-06-22T03:39:38Z"
leaseHeartbeatAt: "2026-06-22T03:29:38Z"
leaseVersion: 3
leaseAttempt: 2
heartbeatAt: "2026-06-22T03:29:38Z"
taskVersion: 4
handoffContract: {"from":"","to":"","requiredArtifacts":["summary","evidence refs","next action or terminal reason"]}
qualityGateRequired: true
attemptNumber: 2
maxAttempts: 3
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-final-acceptance-handoff.md
  - projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-final-acceptance-handoff-02.md
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-22T03:29:45Z"
completedAt: "2026-06-22T03:29:38Z"
retryRequestedAt: "2026-06-22T03:29:28Z"
retryRequestedBy: agent.company.project-manager
retryReason: upgrade-product-final-acceptance-result-contract
retryHistory:
  - {"fromStatus":"done","reason":"upgrade-product-final-acceptance-result-contract","actor":"agent.company.project-manager","previousRunnerId":"runner.meimei-mac-local-product-rt","at":"2026-06-22T03:29:28Z"}
failureReasons:
  - upgrade-product-final-acceptance-result-contract
nextAction: Runner should claim the retry lease and write back fresh evidence.
preferredRunner: runner.meimei-mac-local-product-rt
---

## Request

AI Native Agent V1 Product Final Acceptance

## Source Materials

- runtime/acceptance-runs/v1.acceptance.20260622t031927643283z.md
- task-results/tr-kt-ai-native-agent-v1-test-closed-loop-acceptance.md
- task-results/tr-kt-ai-native-agent-v1-pm-product-final-acceptance.md

## Expected Output

- Product final acceptance verdict for V1 single-machine closed loop.

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
