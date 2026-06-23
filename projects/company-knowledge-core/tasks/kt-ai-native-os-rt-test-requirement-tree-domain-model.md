---
type: ProjectTask
title: AI Native OS RT test - Requirement Tree domain model
description: Independently test Requirement Tree domain model implementation and traceability validation.
timestamp: "2026-06-21T08:58:00Z"
taskId: kt-ai-native-os-rt-test-requirement-tree-domain-model
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"engineering","stage":"test","requiredCapabilities":["testing","requirement_traceability","quality_gate"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-ai-native-os-rt-dev-requirement-tree-domain-model.md","docs/product/ai-native-os/requirement-tree.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"test_then_pm_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - testing
  - requirement_traceability
  - quality_gate
requiredAgents:
  - agent.company.test
executorAgent: agent.company.test
status: rejected
priority: critical
currentStage: test
blockedByTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-rt-dev-requirement-tree-domain-model.md
sourceMaterialRefs:
  - docs/product/ai-native-os/requirement-tree.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-rt-dev-requirement-tree-domain-model.md
expectedOutput:
  - Test Agent verifies Requirement Tree object model, importer/validator readiness, and traceability failure cases.
  - Failures return to Development Agent through a repair task.
---

# Test Rule

Test Agent must not repair implementation directly.

# PM Re-Split Decision

Rejected before release. This test task was too broad and is replaced by paired test tasks per implementation slice in `projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-resplit-plan.md`.
