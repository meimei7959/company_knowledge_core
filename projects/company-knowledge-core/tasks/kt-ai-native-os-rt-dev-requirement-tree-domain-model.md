---
type: ProjectTask
title: AI Native OS RT development - Requirement Tree domain model
description: Implement first-class Requirement Tree domain objects and validation roots for BusinessRequirement, UserRequirement, UserScenario, ProductRequirement, FunctionalRequirementMapping, and RequirementTreeSnapshot.
timestamp: "2026-06-21T08:58:00Z"
taskId: kt-ai-native-os-rt-dev-requirement-tree-domain-model
taskType: development
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"development","category":"engineering","stage":"implementation","requiredCapabilities":["development","requirement_traceability","schema_migration"],"requiredTools":[],"sourceRefs":["docs/product/ai-native-os/requirement-tree.md","projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-delta-task-list.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"development_then_test","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - development
  - requirement_traceability
  - schema_migration
requiredAgents:
  - agent.company.development
executorAgent: agent.company.development
status: rejected
priority: critical
currentStage: implementation
sourceMaterialRefs:
  - docs/product/ai-native-os/requirement-tree.md
  - projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-delta-task-list.md
expectedOutput:
  - New or extended domain model supports BR, UREQ, scenario, product requirement, functional mapping, and tree snapshot.
  - Validation rejects orphan mappings and missing acceptance criteria.
  - Tests prove 5 BR, 15 UREQ, and 74 functional requirement mapping can be represented.
---

# PM Scope

This task starts the Requirement Tree implementation wave. It must not reinterpret the 74 functional requirements as the full requirement set.

# PM Re-Split Decision

Rejected before release. PM retrospective found this task too large because it mixed domain model, validation root, import readiness, and full mapping proof. It is replaced by the task ladder in `projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-resplit-plan.md`.
