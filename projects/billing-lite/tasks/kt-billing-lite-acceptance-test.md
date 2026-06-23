---
type: ProjectTask
title: Billing Lite acceptance test suite
description: Test Agent creates and runs the Billing Lite acceptance suite across product, API, payment verification, restore, revoke, idempotency, and no-login entitlement flows.
timestamp: "2026-06-23T11:55:53Z"
updatedAt: "2026-06-23T12:32:54Z"
taskId: kt-billing-lite-acceptance-test
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"engineering","stage":"test","requiredCapabilities":["testing","payment_testing","security_testing","requirement_traceability"],"requiredTools":[],"sourceRefs":["projects/billing-lite/sources/sm-billing-lite-prd-v1.md","projects/billing-lite/tasks/kt-billing-lite-mvp-development.md","projects/billing-lite/tasks/kt-billing-lite-payment-channel-integration.md"],"repositoryRefs":[],"dataScopes":["local_repo"],"qualityGate":"engineering","acceptancePath":"product_and_pm_review","reviewPath":"test_then_product_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":true,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: billing-lite
requester: agent.company.project-manager
assignee: agent.company.test
status: pending
priority: high
workSourceType: feature
requirementRefs:
  - BILLING-LITE-PRD-V1
sourceMaterialRefs:
  - projects/billing-lite/sources/sm-billing-lite-prd-v1.md
prerequisiteTaskRefs:
  - projects/billing-lite/tasks/kt-billing-lite-mvp-development.md
  - projects/billing-lite/tasks/kt-billing-lite-payment-channel-integration.md
expectedOutput:
  - Acceptance matrix for PRD AC-01 through AC-13.
  - API, idempotency, duplicate callback, refund/revoke, restore, and no-login test evidence.
  - Risk list and release recommendation.
nextAction: Product Manager and human owner review acceptance evidence.
operatingRuleRefs:
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
notificationRefs:
  - notifications/notification.20260623T123254354598Z.md
  - notifications/notification.20260623T123254355380Z.md
---


