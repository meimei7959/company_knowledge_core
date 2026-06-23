---
type: ProjectTask
title: AI Native OS implementation - cross-platform desktop client
description: Development Agent implements the accepted Mac/Windows desktop client shell and runtime integration.
timestamp: "2026-06-21T13:07:34Z"
taskId: kt-ai-native-os-impl-desktop-client-cross-platform
taskType: development
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"development","category":"engineering","stage":"implementation","requiredCapabilities":["development","desktop","cross_platform","workbench","agent_worker"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/product-reviews/ai-native-os-full-product-gap-acceptance-criteria.md","projects/company-knowledge-core/product-reviews/ai-native-os-full-product-gap-solution-product-review.md","projects/company-knowledge-core/design/ai-native-os-desktop-client-design-solution.md"],"repositoryRefs":["/Users/meimei/Documents/company_knowledge_core"],"dataScopes":["local_repo"],"qualityGate":"engineering","acceptancePath":"test_then_pm_and_product_review","reviewPath":"implementation_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":false,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredAgents:
  - agent.company.development
executorAgent: agent.company.development
status: waiting_acceptance
priority: critical
currentStage: implementation
sourceMaterialRefs:
  - projects/company-knowledge-core/design/ai-native-os-desktop-client-design-solution.md
expectedOutput:
  - Cross-platform desktop client implementation plan converted into working app shell or repository scaffold accepted by the current codebase.
  - Runtime state views for project progress, Agent current work, runner/lease/history, approvals, notifications, failures, and settings.
  - TaskResult with changed files, tests, packaging/runtime evidence, residual risks, and handoff to kt-ai-native-os-test-desktop-client-cross-platform.
auditRefs:
  - knowledge/audit/audit.20260621T130734Z-ai-native-os-implementation-queue.md
  - knowledge/audit/audit.20260621T132122Z-ai-native-os-desktop-test-release.md
resultRef: task-results/tr-kt-ai-native-os-impl-desktop-client-cross-platform.md
updatedAt: "2026-06-21T13:10:34Z"
---

# Release Boundary

Use the accepted design solution as source of truth. Do not replace desktop implementation with a static document-only artifact.
