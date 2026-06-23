---
type: ProjectTask
title: Billing Lite MVP development
description: Development Agent implements the approved Billing Lite foundation after product and architecture reviews pass.
timestamp: "2026-06-23T11:55:53Z"
updatedAt: "2026-06-23T11:55:53Z"
taskId: kt-billing-lite-mvp-development
taskType: development
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"development","category":"engineering","stage":"implementation","requiredCapabilities":["development","api","data_model","payment_integration","security"],"requiredTools":[],"sourceRefs":["projects/billing-lite/sources/sm-billing-lite-prd-v1.md","projects/billing-lite/tasks/kt-billing-lite-architecture-solution.md"],"repositoryRefs":[],"dataScopes":["local_repo"],"qualityGate":"engineering","acceptancePath":"test_then_product_review","reviewPath":"development_then_test","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":true,"requiresKnowledgeDraft":false,"requiresTests":true}
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
  - projects/billing-lite/tasks/kt-billing-lite-product-requirement-acceptance.md
  - projects/billing-lite/tasks/kt-billing-lite-architecture-solution.md
expectedOutput:
  - Base API and storage implementation.
  - Product catalog, installation, entitlement, transaction, and audit flows.
  - Admin/configuration minimal surface.
  - Unit and integration tests for idempotency and entitlement issuance.
nextAction: Test Agent runs acceptance suite after development TaskResult is submitted.
operatingRuleRefs:
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
---
