---
type: ProjectTask
title: AI Native OS test - Feishu/API/PostgreSQL live path
description: Test Agent verifies live Feishu/API/PostgreSQL implementation after the paired Development Agent TaskResult exists.
timestamp: "2026-06-21T13:07:34Z"
taskId: kt-ai-native-os-test-feishu-api-postgres-live
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"engineering","stage":"test","requiredCapabilities":["testing","feishu","api_gateway","postgresql","ops"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-ai-native-os-impl-feishu-api-postgres-live.md","task-results/tr-kt-ai-native-os-impl-feishu-api-postgres-live.md","projects/company-knowledge-core/test-plans/ai-native-os-launch-acceptance-evidence-matrix.md"],"repositoryRefs":["/Users/meimei/Documents/company_knowledge_core"],"dataScopes":["local_repo"],"qualityGate":"engineering","acceptancePath":"pm_and_product_review","reviewPath":"test_then_pm_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":false,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredAgents:
  - agent.company.test
executorAgent: agent.company.test
status: blocked
priority: critical
currentStage: test
blockedByTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-impl-feishu-api-postgres-live.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-env-feishu-api-postgres-readiness.md
expectedOutput:
  - TestResult/TaskResult covering Feishu ingress, permissions, idempotency, notification/audit writeback, API envelope, DB migration/rollback, health/metrics, and skip elimination.
  - Regression instructions if failed, assigned back to Development Agent.
auditRefs:
  - knowledge/audit/audit.20260621T130734Z-ai-native-os-implementation-queue.md
  - knowledge/audit/audit.20260621T133118Z-ai-native-os-desktop-and-feishu-reconcile.md
  - knowledge/audit/audit.20260621T134400Z-ai-native-os-feishu-readiness-blocked.md
blockedReason: "Paired live test remains blocked until kt-ai-native-os-env-feishu-api-postgres-readiness passes."
---

# Blocked Until

Unblock only after `task-results/tr-kt-ai-native-os-impl-feishu-api-postgres-live.md` exists and references changed implementation files or explicit environment blockers.
