---
type: ProjectTask
title: AI Native OS automation gap - Agent finish permission boundary repair
description: Development Agent repairs the CLI/task finish permission path so non-knowledge tasks can close without requiring knowledge:draft when no reusable lesson is being written.
timestamp: "2026-06-21T12:53:50Z"
taskId: kt-ai-native-os-gap-dev-agent-finish-permission-boundary
taskType: development
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"development","category":"engineering","stage":"implementation","requiredCapabilities":["development","scheduler","agent_worker","permission_policy"],"requiredTools":[],"sourceRefs":["task-results/tr-kt-ai-native-os-gap-test-launch-evidence-matrix.md","projects/company-knowledge-core/coordination/ai-native-os-full-product-gap-execution-plan.md"],"repositoryRefs":["/Users/meimei/Documents/company_knowledge_core"],"dataScopes":["local_repo"],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"implementation_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":false,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredAgents:
  - agent.company.development
executorAgent: agent.company.development
status: waiting_acceptance
priority: critical
currentStage: implementation
sourceMaterialRefs:
  - task-results/tr-kt-ai-native-os-gap-test-launch-evidence-matrix.md
expectedOutput:
  - Root-cause fix for finish permission check when --no-reusable-lesson or equivalent no-knowledge closeout is used.
  - Regression tests proving development/test/design/product task closeout does not require knowledge:draft unless reusable knowledge is written.
  - TaskResult with changed files, tests, residual risks, and handoff to Test Agent.
auditRefs:
  - knowledge/audit/audit.20260621T125350Z-ai-native-os-finish-permission-boundary-task.md
  - knowledge/audit/audit.20260621T132446Z-ai-native-os-finish-permission-boundary-reconciled.md
resultRef: task-results/tr-kt-ai-native-os-gap-dev-agent-finish-permission-boundary.md
---

# Background

Test Agent reported that formal closeout was blocked by:

```text
agent agent.company.test lacks write permission: knowledge:draft
```

This blocks automatic execution because a Test Agent must be able to finish a non-knowledge testing task and write TaskResult/AgentRun evidence without receiving reusable-knowledge draft permission.

# Acceptance

- The fix addresses the permission decision root cause, not only one Agent ID.
- `knowledge:draft` remains required when the Agent actually writes reusable knowledge.
- Non-knowledge task closeout with explicit no-reusable-lesson intent is allowed for authorized task executors.
- Tests cover success and negative paths.
- Test Agent must run regression before PM acceptance.
