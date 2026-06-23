---
type: ProjectTask
title: AI Native OS product scope exception review
description: Product Manager Agent decides whether local-equivalent runner evidence and repository-local desktop evidence can be accepted as a scoped launch boundary, or whether full product acceptance must stay blocked.
timestamp: "2026-06-21T13:55:41Z"
taskId: kt-ai-native-os-product-scope-exception-review
taskType: product_acceptance
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"product_acceptance","category":"product","stage":"scope_exception_review","requiredCapabilities":["product_management","acceptance","risk_review"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/coordination/ai-native-os-full-implementation-run-status.md","projects/company-knowledge-core/coordination/ai-native-os-blocker-resolution-plan.md","task-results/tr-kt-ai-native-os-test-agent-ring-console-live-execution.md","task-results/tr-kt-ai-native-os-test-desktop-client-cross-platform.md","task-results/tr-kt-ai-native-os-env-feishu-api-postgres-readiness.md"],"repositoryRefs":["/Users/meimei/Documents/company_knowledge_core"],"dataScopes":["local_repo"],"qualityGate":"product","acceptancePath":"human_and_pm_review","reviewPath":"product_scope_exception","riskLevel":"critical","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":false,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredAgents:
  - agent.company.product-manager
executorAgent: agent.company.product-manager
status: waiting_acceptance
priority: critical
currentStage: scope_exception_review
expectedOutput:
  - Product Manager Agent verdict on whether local-equivalent runner evidence and repository-local desktop evidence can be accepted for a reduced launch scope.
  - Explicit non-goals, user-facing limits, launch label, risk copy, and blockers.
  - If rejected, final acceptance remains blocked until full native/distributed/live evidence exists.
auditRefs:
  - knowledge/audit/audit.20260621T135541Z-ai-native-os-blocker-resolution-plan.md
  - knowledge/audit/audit.20260621T152200Z-ai-native-os-product-scope-exception-reconciled.md
resultRef: task-results/tr-kt-ai-native-os-product-scope-exception-review.md
updatedAt: "2026-06-21T13:57:08Z"
---

# Boundary

Only Product Manager Agent may issue this product verdict. Project Manager Agent may not substitute its own product judgment.
