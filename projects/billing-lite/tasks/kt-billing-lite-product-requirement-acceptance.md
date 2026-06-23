---
type: ProjectTask
title: Billing Lite product requirement acceptance
description: Product Manager Agent reviews PRD V1.0, freezes P0 scope, maps acceptance criteria, and identifies unresolved decisions before architecture starts.
timestamp: "2026-06-23T11:55:53Z"
updatedAt: "2026-06-23T12:35:11Z"
taskId: kt-billing-lite-product-requirement-acceptance
taskType: product_review
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"product_review","category":"project","stage":"requirement_acceptance","requiredCapabilities":["product_review","requirement_traceability","acceptance_criteria"],"requiredTools":[],"sourceRefs":["projects/billing-lite/sources/sm-billing-lite-prd-v1.md"],"repositoryRefs":[],"dataScopes":["Project","ProjectTask","SourceMaterial","TaskResult","Decision","AuditLog"],"qualityGate":"product_requirement_acceptance","acceptancePath":"human_review","reviewPath":"product_review","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":true,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: billing-lite
requester: agent.company.project-manager
assignee: agent.company.product-manager
status: processing
priority: high
workSourceType: feature
requirementRefs:
  - BILLING-LITE-PRD-V1
sourceMaterialRefs:
  - projects/billing-lite/sources/sm-billing-lite-prd-v1.md
expectedOutput:
  - Product requirement acceptance review.
  - P0/P1/P2 scope matrix.
  - Acceptance criteria matrix covering AC-01 through AC-13 and technical acceptance.
  - Open decision list for first app, first SKU, PSP, Windows P0, device limit, and credential ownership.
nextAction: Architecture Agent can start only after this task is accepted or accepted with assumptions.
operatingRuleRefs:
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
---

## Hard Boundary

Do not expand P0 into consumer account, cross-platform membership, subscription, finance ledger, invoice, tax, or marketing automation.
