---
type: ProjectTask
title: AI Native OS RT test - Requirement Tree workbench slice
description: Test Requirement Tree workbench traceability.
timestamp: "2026-06-21T09:08:00Z"
taskId: kt-ai-native-os-rt-test-workbench-slice
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"engineering","stage":"test","requiredCapabilities":["testing","workbench","requirement_traceability"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-ai-native-os-rt-dev-workbench-slice.md","task-results/tr-kt-ai-native-os-rt-dev-workbench-slice.md","zhenzhi_knowledge/core.py","zhenzhi_knowledge/cli.py","zhenzhi_knowledge/server.py","tests/test_requirement_tree_object_model.py"],"repositoryRefs":["/Users/meimei/Documents/company_knowledge_core"],"dataScopes":["local_repo"],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"test_then_pm_review","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - testing
  - workbench
  - requirement_traceability
requiredAgents:
  - agent.company.test
executorAgent: agent.company.test
status: done
priority: high
currentStage: test
releasedByTaskResultRef: task-results/tr-kt-ai-native-os-rt-dev-workbench-slice.md
releasedAt: "2026-06-21T11:06:00Z"
releaseReason: Development Agent completed Requirement Tree workbench read model and submitted TaskResult; Test Agent verification is required.
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-rt-dev-workbench-slice.md
  - task-results/tr-kt-ai-native-os-rt-dev-workbench-slice.md
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/cli.py
  - zhenzhi_knowledge/server.py
  - tests/test_requirement_tree_object_model.py
expectedOutput:
  - Workbench traceability and risk display are verified.
startedAt: "2026-06-21T11:05:32Z"
updatedAt: "2026-06-21T11:09:57Z"
resultRef: task-results/tr-kt-ai-native-os-rt-test-workbench-slice.md
completedAt: "2026-06-21T11:09:22Z"
notificationRefs:
  - notifications/notification.20260621T110922141819Z.md
  - notifications/notification.20260621T110922142480Z.md
  - notifications/notification.20260621T110922143505Z.md
  - notifications/notification.20260621T110957022343Z.md
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-rt-test-workbench-slice-handoff.md
---

# Test Boundary

- Verify read model shows BR -> UREQ -> ProductRequirement -> ANOS -> Task -> Result -> Test -> Acceptance.
- Verify unmapped, untested, blocked, and assumption-heavy diagnostics are visible.
- Verify CLI `requirement tree workbench`.
- Verify API route behavior where local environment supports it; otherwise record existing skip reason.
- Confirm no desktop UI, historical backfill, or live Agent Ring execution was introduced.
- Do not modify implementation. Failed tests return to Development Agent repair.
