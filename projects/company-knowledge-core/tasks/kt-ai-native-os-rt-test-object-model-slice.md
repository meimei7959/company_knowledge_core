---
type: ProjectTask
title: AI Native OS RT test - object model slice
description: Test the Requirement Tree object model slice independently.
timestamp: "2026-06-21T09:08:00Z"
taskId: kt-ai-native-os-rt-test-object-model-slice
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"engineering","stage":"test","requiredCapabilities":["testing","requirement_traceability","quality_gate"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-ai-native-os-rt-dev-object-model-slice.md","task-results/tr-kt-ai-native-os-rt-dev-object-model-slice.md","zhenzhi_knowledge/core.py","zhenzhi_knowledge/cli.py","tests/test_requirement_tree_object_model.py"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"test_then_pm_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - testing
  - requirement_traceability
  - quality_gate
requiredAgents:
  - agent.company.test
executorAgent: agent.company.test
status: blocked
priority: critical
currentStage: test
releasedByTaskResultRef: task-results/tr-kt-ai-native-os-rt-dev-object-model-slice.md
releasedAt: "2026-06-21T10:05:00Z"
releaseReason: Development Agent completed the object model slice and submitted TaskResult; independent Test Agent verification is required before PM acceptance.
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-rt-dev-object-model-slice.md
  - task-results/tr-kt-ai-native-os-rt-dev-object-model-slice.md
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/cli.py
  - tests/test_requirement_tree_object_model.py
expectedOutput:
  - Positive and negative object model tests.
  - Failed tests return to Development Agent repair task.
startedAt: "2026-06-21T10:05:53Z"
updatedAt: "2026-06-21T10:10:11Z"
resultRef: task-results/tr-kt-ai-native-os-rt-test-object-model-slice.md
completedAt: "2026-06-21T10:10:11Z"
notificationRefs:
  - notifications/notification.20260621T101011406850Z.md
  - notifications/notification.20260621T101011409247Z.md
  - notifications/notification.20260621T101011409920Z.md
improvementRefs:
  - knowledge/agent-improvements/agent-improvement.20260621T101011408268Z.md
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-rt-test-object-model-slice-blocker.md
---

# Test Boundary

Do not modify implementation.

# PM Release Constraints

- Verify only the Requirement Tree object model slice.
- Confirm importer, compiler, context pack, workbench, historical backfill, and ProjectTask queue generation were not introduced.
- If tests fail or scope boundaries are violated, return a repair task to Development Agent instead of fixing implementation in the test task.
