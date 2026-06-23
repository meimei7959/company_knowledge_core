---
type: ProjectTask
title: AI Native OS test - Agent finish permission boundary repair
description: Test Agent regresses the Development Agent fix for non-knowledge task finish permissions and reusable-knowledge write checks.
timestamp: "2026-06-21T13:15:34Z"
taskId: kt-ai-native-os-test-agent-finish-permission-boundary
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"engineering","stage":"regression","requiredCapabilities":["testing","scheduler","agent_worker","permission_policy"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-ai-native-os-gap-dev-agent-finish-permission-boundary.md","task-results/tr-kt-ai-native-os-gap-dev-agent-finish-permission-boundary.md","zhenzhi_knowledge/core.py","tests/test_cli.py","scripts/agent_ring_contract.py"],"repositoryRefs":["/Users/meimei/Documents/company_knowledge_core"],"dataScopes":["local_repo"],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"test_regression_then_pm_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":false,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredAgents:
  - agent.company.test
executorAgent: agent.company.test
status: waiting_acceptance
priority: critical
currentStage: regression
sourceMaterialRefs:
  - task-results/tr-kt-ai-native-os-gap-dev-agent-finish-permission-boundary.md
expectedOutput:
  - Independent regression result for no-reusable-lesson closeout without knowledge:draft.
  - Negative test result proving KnowledgeItem/reusable lesson write still requires knowledge:draft.
  - TaskResult with pass/fail, evidence, and either PM handoff or Development Agent repair instructions.
auditRefs:
  - knowledge/audit/audit.20260621T131534Z-ai-native-os-finish-permission-boundary-test-task.md
  - knowledge/audit/audit.20260621T132446Z-ai-native-os-finish-permission-boundary-reconciled.md
resultRef: task-results/tr-kt-ai-native-os-test-agent-finish-permission-boundary.md
updatedAt: "2026-06-21T13:16:02Z"
---

# Regression Scope

This test protects the automatic execution loop. A non-knowledge Development/Test/Design/Product task must be able to close with TaskResult evidence without `knowledge:draft` when no reusable knowledge is written.

The same executor must still be blocked when it attempts to write reusable knowledge without `knowledge:draft`.
