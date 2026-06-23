---
type: ProjectTask
title: AI Native OS RT test - import and validation slice
description: Test Requirement Tree import and validation.
timestamp: "2026-06-21T09:08:00Z"
taskId: kt-ai-native-os-rt-test-import-validation-slice
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"engineering","stage":"test","requiredCapabilities":["testing","requirement_traceability","validation"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-ai-native-os-rt-dev-import-validation-slice.md","task-results/tr-kt-ai-native-os-rt-dev-import-validation-slice.md","docs/product/ai-native-os/requirement-tree.md","zhenzhi_knowledge/core.py","zhenzhi_knowledge/cli.py","tests/test_requirement_tree_object_model.py"],"repositoryRefs":["/Users/meimei/Documents/company_knowledge_core"],"dataScopes":["local_repo"],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"test_then_pm_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - testing
  - requirement_traceability
  - validation
requiredAgents:
  - agent.company.test
executorAgent: agent.company.test
status: done
priority: critical
currentStage: test
releasedByTaskResultRef: task-results/tr-kt-ai-native-os-rt-dev-import-validation-slice.md
releasedAt: "2026-06-21T10:25:00Z"
releaseReason: Development Agent completed import and validation slice and submitted TaskResult; Test Agent independent verification is required.
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-rt-dev-import-validation-slice.md
  - task-results/tr-kt-ai-native-os-rt-dev-import-validation-slice.md
  - docs/product/ai-native-os/requirement-tree.md
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/cli.py
  - tests/test_requirement_tree_object_model.py
expectedOutput:
  - Valid tree fixture passes.
  - Broken tree fixtures fail with readable diagnostics.
startedAt: "2026-06-21T10:29:54Z"
updatedAt: "2026-06-21T10:32:42Z"
resultRef: task-results/tr-kt-ai-native-os-rt-test-import-validation-slice.md
completedAt: "2026-06-21T10:32:08Z"
notificationRefs:
  - notifications/notification.20260621T103208934114Z.md
  - notifications/notification.20260621T103208935010Z.md
  - notifications/notification.20260621T103208935725Z.md
  - notifications/notification.20260621T103242149917Z.md
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-rt-test-import-validation-slice-handoff.md
---

# Test Boundary

- Test Requirement Tree import and traceability validation only.
- Verify import count expectations for 5 BR, 15 UREQ, product requirements, and 74 ANOS mappings.
- Verify invalid inputs produce readable diagnostics for orphan refs, missing owner, missing test, missing acceptance gate, and missing observable criteria.
- Confirm compiler, context pack, workbench, historical backfill, and ProjectTask queue generation remain out of scope.
- Do not modify implementation. Failed tests return to Development Agent repair.
