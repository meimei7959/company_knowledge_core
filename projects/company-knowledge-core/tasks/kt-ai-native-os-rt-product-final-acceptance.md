---
type: ProjectTask
title: AI Native OS Requirement Tree final product acceptance
description: ProjectTask assigned to agent.company.product-manager.
timestamp: "2026-06-21T11:35:55Z"
taskId: kt-ai-native-os-rt-product-final-acceptance
taskType: product_review
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"product_review","category":"project","stage":"","requiredCapabilities":["product_review"],"requiredTools":[],"sourceRefs":["docs/product/ai-native-os/requirement-tree.md","docs/product/ai-native-os/requirements.md","docs/product/ai-native-os/test-cases.md","docs/product/ai-native-os/acceptance-checklist.md","projects/company-knowledge-core/pm-reviews/requirement-tree-systematic-delivery-closeout.md","task-results/tr-kt-ai-native-os-rt-test-existing-work-backfill.md","projects/company-knowledge-core/requirements/backfills/requirement-tree-existing-work-backfill.20260621112327.json"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.product-manager
status: waiting_acceptance
priority: critical
dueAt: ""
sourceMaterialRefs:
  - docs/product/ai-native-os/requirement-tree.md
  - docs/product/ai-native-os/requirements.md
  - docs/product/ai-native-os/test-cases.md
  - docs/product/ai-native-os/acceptance-checklist.md
  - projects/company-knowledge-core/pm-reviews/requirement-tree-systematic-delivery-closeout.md
  - task-results/tr-kt-ai-native-os-rt-test-existing-work-backfill.md
  - projects/company-knowledge-core/requirements/backfills/requirement-tree-existing-work-backfill.20260621112327.json
expectedOutput:
  - Product Manager Agent verifies whether all 74 functional requirements are implemented according to the approved requirement tree and acceptance boundaries.
  - Return accepted, partially_accepted, or changes_requested with product gaps and boundaries.
  - Distinguish traceability/system foundation completion from full desktop client UI and live distributed Agent Ring execution.
resultRef: task-results/tr-kt-ai-native-os-rt-product-final-acceptance.md
notificationRefs:
  - notifications/notification.20260621T113555390611Z.md
  - notifications/notification.20260621T114245972475Z.md
  - notifications/notification.20260621T114245973302Z.md
  - notifications/notification.20260621T114245973981Z.md
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
updatedAt: "2026-06-21T11:42:45Z"
startedAt: "2026-06-21T11:35:55Z"
completedAt: "2026-06-21T11:42:45Z"
---

## Request

AI Native OS Requirement Tree final product acceptance

## Source Materials

- docs/product/ai-native-os/requirement-tree.md
- docs/product/ai-native-os/requirements.md
- docs/product/ai-native-os/test-cases.md
- docs/product/ai-native-os/acceptance-checklist.md
- projects/company-knowledge-core/pm-reviews/requirement-tree-systematic-delivery-closeout.md
- task-results/tr-kt-ai-native-os-rt-test-existing-work-backfill.md
- projects/company-knowledge-core/requirements/backfills/requirement-tree-existing-work-backfill.20260621112327.json

## Expected Output

- Product Manager Agent verifies whether all 74 functional requirements are implemented according to the approved requirement tree and acceptance boundaries.
- Return accepted, partially_accepted, or changes_requested with product gaps and boundaries.
- Distinguish traceability/system foundation completion from full desktop client UI and live distributed Agent Ring execution.

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
