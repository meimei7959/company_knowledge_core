---
type: ProjectTask
title: AI Native OS environment readiness - Feishu/API/PostgreSQL live path
description: Development/Ops Agent prepares or verifies the environment required to run live Feishu/API/PostgreSQL acceptance tests.
timestamp: "2026-06-21T13:31:18Z"
taskId: kt-ai-native-os-env-feishu-api-postgres-readiness
taskType: development
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"development","category":"ops","stage":"environment_readiness","requiredCapabilities":["development","ops","feishu","api_gateway","postgresql"],"requiredTools":[],"sourceRefs":["task-results/tr-kt-ai-native-os-impl-feishu-api-postgres-live.md","projects/company-knowledge-core/technical-solutions/ai-native-os-feishu-api-postgres-live-technical-solution.md"],"repositoryRefs":["/Users/meimei/Documents/company_knowledge_core"],"dataScopes":["local_repo"],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"environment_readiness_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":false,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredAgents:
  - agent.company.development
executorAgent: agent.company.development
status: blocked
priority: critical
currentStage: environment_readiness
sourceMaterialRefs:
  - task-results/tr-kt-ai-native-os-impl-feishu-api-postgres-live.md
expectedOutput:
  - Readiness command or script that checks Feishu callback/message/card/API route, PostgreSQL operational store, migration, rollback, health, metrics, and backup prerequisites without exposing secrets.
  - Clear pass/fail/blocker result with human-readable missing configuration labels.
  - If readiness cannot be completed on this computer, a precise blocker with owner, required input, and next action.
  - TaskResult and AuditLog that allow Project Manager Agent to unblock or keep blocked kt-ai-native-os-test-feishu-api-postgres-live.
auditRefs:
  - knowledge/audit/audit.20260621T133118Z-ai-native-os-desktop-and-feishu-reconcile.md
  - knowledge/audit/audit.20260621T134400Z-ai-native-os-feishu-readiness-blocked.md
resultRef: task-results/tr-kt-ai-native-os-env-feishu-api-postgres-readiness.md
blockedReason: "Staging Feishu credentials, callback URL, API token/port, PostgreSQL connection, backup refs, pg dump ref, and network Feishu API probe are not configured on this computer."
updatedAt: "2026-06-21T13:31:54Z"
---

# Boundary

This task must not store secret values. It may report readable labels such as "Feishu app credential missing" or "PostgreSQL connection not configured", but not raw tokens, passwords, or connection strings.
