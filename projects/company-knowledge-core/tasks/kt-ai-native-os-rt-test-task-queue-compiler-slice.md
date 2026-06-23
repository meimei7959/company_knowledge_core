---
type: ProjectTask
title: AI Native OS RT test - task queue compiler slice
description: Test Requirement Tree task queue compiler.
timestamp: "2026-06-21T09:08:00Z"
taskId: kt-ai-native-os-rt-test-task-queue-compiler-slice
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"engineering","stage":"test","requiredCapabilities":["testing","scheduler","requirement_traceability"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-ai-native-os-rt-dev-task-queue-compiler-slice.md","task-results/tr-kt-ai-native-os-rt-dev-task-queue-compiler-slice.md","zhenzhi_knowledge/core.py","zhenzhi_knowledge/cli.py","tests/test_requirement_tree_object_model.py"],"repositoryRefs":["/Users/meimei/Documents/company_knowledge_core"],"dataScopes":["local_repo"],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"test_then_pm_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - testing
  - scheduler
  - requirement_traceability
requiredAgents:
  - agent.company.test
executorAgent: agent.company.test
status: done
priority: critical
currentStage: test
releasedByTaskResultRef: task-results/tr-kt-ai-native-os-rt-dev-task-queue-compiler-slice.md
releasedAt: "2026-06-21T10:38:00Z"
releaseReason: Development Agent completed task queue compiler slice and submitted TaskResult; Test Agent verification is required.
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-rt-dev-task-queue-compiler-slice.md
  - task-results/tr-kt-ai-native-os-rt-dev-task-queue-compiler-slice.md
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/cli.py
  - tests/test_requirement_tree_object_model.py
expectedOutput:
  - Compiler generates role-specific tasks with correct refs.
  - Incomplete tree is blocked.
startedAt: "2026-06-21T10:41:10Z"
updatedAt: "2026-06-21T10:44:49Z"
resultRef: task-results/tr-kt-ai-native-os-rt-test-task-queue-compiler-slice.md
completedAt: "2026-06-21T10:44:16Z"
notificationRefs:
  - notifications/notification.20260621T104416128821Z.md
  - notifications/notification.20260621T104416129480Z.md
  - notifications/notification.20260621T104416130005Z.md
  - notifications/notification.20260621T104449377983Z.md
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-rt-test-task-queue-compiler-slice-handoff.md
---

# Test Boundary

- Verify compiler generates Development, Test, Design, Ops, Review, and Governance ProjectTask drafts with BR/UREQ/ProductRequirement/ANOS/test/acceptance refs.
- Verify incomplete trees or high blockers create blocker diagnostics and no executable task drafts.
- Verify CLI `requirement tree compile`.
- Confirm output remains draft-only and does not enter the scheduler executable queue.
- Do not modify implementation. Failed tests return to Development Agent repair.
