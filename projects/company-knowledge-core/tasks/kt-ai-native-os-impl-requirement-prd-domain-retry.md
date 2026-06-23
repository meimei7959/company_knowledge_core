---
type: ProjectTask
title: Retry task output for kt-ai-native-os-impl-requirement-prd-domain
description: ProjectTask assigned to agent.company.project-manager.
timestamp: "2026-06-21T07:13:25Z"
taskId: kt-ai-native-os-impl-requirement-prd-domain-retry
taskType: development
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"development","category":"engineering","stage":"","requiredCapabilities":["development"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/technical-solutions/ai-native-os-requirement-prd-domain.md","projects/company-knowledge-core/product-reviews/ai-native-os-technical-solutions-product-review.md","task-results/tr-kt-ai-native-os-impl-requirement-prd-domain.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.project-manager
status: waiting_runner
priority: critical
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/technical-solutions/ai-native-os-requirement-prd-domain.md
  - projects/company-knowledge-core/product-reviews/ai-native-os-technical-solutions-product-review.md
  - task-results/tr-kt-ai-native-os-impl-requirement-prd-domain.md
expectedOutput:
  - Repair the failed output according to qualityEvaluation reasons.
  - Return TaskResult with evidence/artifacts and handoff contract.
resultRef: ""
notificationRefs:
  - notifications/notification.20260621T071325773977Z.md
  - notifications/notification.20260621T071325774846Z.md
  - notifications/notification.20260621T071805373558Z.md
  - notifications/notification.20260621T072134031197Z.md
  - notifications/notification.20260621T074620284112Z.md
  - notifications/notification.20260621T074620284882Z.md
  - notifications/notification.20260621T074620285612Z.md
auditRefs: []
assignedRunner: runner.meimei-mac-local-codex
executorAgent: agent.company.project-manager
leaseOwner: ""
leaseTokenHash: ""
leaseProofHash: ""
leaseIssuedAt: "2026-06-21T07:21:34Z"
leaseExpiresAt: ""
leaseHeartbeatAt: ""
leaseVersion: 2
leaseAttempt: 1
heartbeatAt: ""
taskVersion: 3
handoffContract: {"from":"agent.company.development","to":"agent.company.test","requiredArtifacts":["technical plan","change summary","self-test result","risk notes"]}
qualityGateRequired: true
attemptNumber: 2
maxAttempts: 3
followupTaskRefs: []
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-21T07:46:20Z"
parentTaskId: kt-ai-native-os-impl-requirement-prd-domain
originTaskId: kt-ai-native-os-impl-requirement-prd-domain
retryOf: kt-ai-native-os-impl-requirement-prd-domain
triggerResultRef: task-results/tr-kt-ai-native-os-impl-requirement-prd-domain.md
qualityGate: failed
failureReasons:
  - missing tests/checks
  - common rule: engineering/test task missing tests or checks
staleLeaseOwner: runner.meimei-mac-local-codex
staleLeaseDetectedAt: "2026-06-21T07:46:20Z"
staleLeaseReason: lease_expired
---

## Request

Retry task output for kt-ai-native-os-impl-requirement-prd-domain

## Source Materials

- projects/company-knowledge-core/technical-solutions/ai-native-os-requirement-prd-domain.md
- projects/company-knowledge-core/product-reviews/ai-native-os-technical-solutions-product-review.md
- task-results/tr-kt-ai-native-os-impl-requirement-prd-domain.md

## Expected Output

- Repair the failed output according to qualityEvaluation reasons.
- Return TaskResult with evidence/artifacts and handoff contract.

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
