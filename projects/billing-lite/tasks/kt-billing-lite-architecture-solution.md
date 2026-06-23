---
type: ProjectTask
title: Billing Lite architecture solution
description: Architecture Agent designs the minimal V0 service, data model, payment adapter boundary, security model, idempotency, refund/revoke handling, and rollout gates.
timestamp: "2026-06-23T11:55:53Z"
updatedAt: "2026-06-23T12:48:28Z"
taskId: kt-billing-lite-architecture-solution
taskType: technical_solution
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"technical_solution","category":"project","stage":"architecture_handoff","requiredCapabilities":["technical_solution","payment_architecture","security_review","data_modeling","workflow_design"],"requiredTools":[],"sourceRefs":["projects/billing-lite/sources/sm-billing-lite-prd-v1.md","projects/billing-lite/tasks/kt-billing-lite-product-requirement-acceptance.md"],"repositoryRefs":[],"dataScopes":["ProjectTask","SourceMaterial","TaskResult","Decision","Policy","AuditLog"],"qualityGate":"architecture_solution","acceptancePath":"product_review","reviewPath":"architecture_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":true,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: billing-lite
requester: agent.company.project-manager
assignee: agent.company.architecture
status: processing
priority: high
workSourceType: feature
requirementRefs:
  - BILLING-LITE-PRD-V1
sourceMaterialRefs:
  - projects/billing-lite/sources/sm-billing-lite-prd-v1.md
prerequisiteTaskRefs:
  - projects/billing-lite/tasks/kt-billing-lite-product-requirement-acceptance.md
expectedOutput:
  - Technical solution for catalog, order, transaction, entitlement, license, callback, audit, monitoring, and admin surfaces.
  - Adapter contracts for Apple, Google, and external PSP.
  - Trust boundary and secret handling design.
  - Idempotency, retry, refund, revoke, restore, and rollback plan.
  - Implementation slice plan mapped to launch gates.
nextAction: Product Manager reviews architecture before development tasks start.
operatingRuleRefs:
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
---

## Hard Boundary

Do not build a general payment platform. Preserve the no-account P0 model and keep channel differences behind adapter boundaries.
