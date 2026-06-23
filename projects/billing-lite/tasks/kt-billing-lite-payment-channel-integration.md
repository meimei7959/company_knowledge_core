---
type: ProjectTask
title: Billing Lite payment channel integration
description: Development Agent implements Apple, Google, and external PSP / License channel integrations behind the approved adapter contract.
timestamp: "2026-06-23T11:55:53Z"
updatedAt: "2026-06-23T11:55:53Z"
taskId: kt-billing-lite-payment-channel-integration
taskType: development
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"development","category":"engineering","stage":"payment_integration","requiredCapabilities":["development","apple_iap","google_play_billing","psp_webhook","license_activation","security"],"requiredTools":[],"sourceRefs":["projects/billing-lite/sources/sm-billing-lite-prd-v1.md","projects/billing-lite/tasks/kt-billing-lite-architecture-solution.md"],"repositoryRefs":[],"dataScopes":["local_repo"],"qualityGate":"engineering","acceptancePath":"test_then_product_review","reviewPath":"development_then_test","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":true,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: billing-lite
requester: agent.company.project-manager
assignee: agent.company.development
status: pending
priority: high
workSourceType: feature
requirementRefs:
  - BILLING-LITE-PRD-V1
sourceMaterialRefs:
  - projects/billing-lite/sources/sm-billing-lite-prd-v1.md
prerequisiteTaskRefs:
  - projects/billing-lite/tasks/kt-billing-lite-mvp-development.md
expectedOutput:
  - Apple verification, notification, restore, and Offer Code handling.
  - Google verification, RTDN, and restore handling.
  - PSP / Apple Pay order, webhook, amount verification, and License activation handling.
  - Tests proving duplicate submissions do not duplicate entitlement.
nextAction: Test Agent validates channel-specific acceptance cases.
operatingRuleRefs:
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
---
