---
type: ProjectTask
title: Mature AI Native OS knowledge governance loop
description: Close source material, extraction, draft, review, approval, publish, index, query, graph, stale, and conflict workflows.
timestamp: "2026-06-20T03:00:00Z"
taskId: KT-OS-KNOWLEDGE-GOVERNANCE-LOOP
taskType: os_master_task
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.knowledge-engineering
requiredCapabilities:
  - source_material
  - knowledge_review
  - publish_index
  - query_with_sources
  - graph_conflict_stale
requiredAgents:
  - agent.company-knowledge-core.knowledge-engineering
  - agent.company-knowledge-core.knowledge-query
preferredRunner: []
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: critical
dueAt: []
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-os-knowledge-core-governance.md
  - docs/workflows/knowledge-ingest-orchestration.md
  - docs/workflows/knowledge-lifecycle.md
expectedOutput:
  - public and project material intake
  - evidence-backed draft knowledge
  - review and approval routing
  - query citations and status labels
  - graph, stale, and conflict handling
resultRef: task-results/tr-kt-os-knowledge-governance-loop.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-20T03:30:00Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_master_task","category":"project","stage":"","requiredCapabilities":["os_master_task","source_material","knowledge_review","publish_index","query_with_sources","graph_conflict_stale"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-os-knowledge-core-governance.md","docs/workflows/knowledge-ingest-orchestration.md","docs/workflows/knowledge-lifecycle.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
updatedAt: "2026-06-21T07:18:05Z"
---

## Goal

Knowledge must become a reusable company asset only after source-backed extraction, review, publication, and indexed retrieval.

## Covers

- `KT-OS-KNOWLEDGE-CORE-GOVERNANCE`

## Completion Standard

- Material intake saves raw source and creates processing task.
- Draft knowledge includes source, evidence, scope, confidence, and limits.
- Review routes to publish/index, human approval, retry, clarification, conflict, or reject.
- Query returns citations and distinguishes verified knowledge from draft reference.

## Test Method

- Material ingest to task finish to draft tests.
- Knowledge review, approval, publish, search, and HTTP query tests.
- Stale, conflict, graph export, and graph impact tests.
