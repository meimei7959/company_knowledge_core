---
type: ProjectTask
title: AI Native OS test - desktop native proof
description: Test Agent verifies the native desktop proof slice after Development Agent evidence exists.
timestamp: "2026-06-21T13:55:41Z"
taskId: kt-ai-native-os-test-desktop-native-proof
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"engineering","stage":"native_proof_test","requiredCapabilities":["testing","desktop","cross_platform","native_runtime","security"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-ai-native-os-impl-desktop-native-proof.md","task-results/tr-kt-ai-native-os-impl-desktop-native-proof.md"],"repositoryRefs":["/Users/meimei/Documents/company_knowledge_core"],"dataScopes":["local_repo"],"qualityGate":"engineering","acceptancePath":"pm_and_product_review","reviewPath":"test_then_pm_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":false,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredAgents:
  - agent.company.test
executorAgent: agent.company.test
status: blocked
priority: critical
currentStage: native_proof_test
blockedByTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-impl-desktop-native-proof.md
expectedOutput:
  - Test Agent verdict on native desktop proof evidence.
  - Explicit pass/fail/blocker list for Mac/Windows packaging, updater, secure storage, deep link, notifications, and runner pairing.
auditRefs:
  - knowledge/audit/audit.20260621T135541Z-ai-native-os-blocker-resolution-plan.md
  - knowledge/audit/audit.20260621T141032Z-ai-native-os-desktop-native-proof-blocked.md
blockedReason: "Paired native proof test remains blocked because implementation proof is blocked."
---

# Blocked Until

Unblock only after `task-results/tr-kt-ai-native-os-impl-desktop-native-proof.md` exists.
