---
type: ProjectTask
title: Review outcome to publisher/indexer closure
description: Make Knowledge Review outcomes executable so reviewed knowledge routes to index, approval, retry, clarification, conflict resolution, or rejection.
timestamp: "2026-06-19T00:00:00Z"
taskId: TASK-REVIEW-OUTCOME-PUBLISHER-CLOSURE
taskType: engineering_action
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.knowledge-engineering
requiredCapabilities:
  - knowledge_review
  - publisher
  - indexer
  - retry
  - approval_routing
requiredAgents:
  - agent.core.knowledge-review
  - agent.core.knowledge-ops
  - agent.core.knowledge-steward
status: done
priority: high
sourceMaterialRefs:
  - docs/workflows/knowledge-ingest-orchestration.md
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/server.py
expectedOutput:
  - ReviewRecord for each review finish action
  - pass_as_observed publishes observed knowledge and rebuilds index
  - needs_human_approval creates approval task
  - changes_requested creates retry task
  - needs_clarification creates clarification task
  - conflict_detected creates ConflictRecord and conflict resolution task
  - reject marks target rejected and notifies requester
resultRef: ""
notificationRefs: []
auditRefs: []
completedAt: "2026-06-19T00:00:00Z"
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","knowledge_review","publisher","indexer","retry","approval_routing"],"requiredTools":[],"sourceRefs":["docs/workflows/knowledge-ingest-orchestration.md","zhenzhi_knowledge/core.py","zhenzhi_knowledge/server.py"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
---

## Request

Complete the second half of the knowledge ingest loop after Knowledge Review.

## Definition Of Done

- Review Agent can finish a review with an explicit outcome.
- Every outcome has a deterministic next hop or terminal state.
- Accepted observed knowledge is indexed.
- Non-accepted outcomes create executable follow-up tasks or rejection records.
- Tests cover publish/index, approval, retry, clarification, conflict, and rejection routing.

## Completion Evidence

- Targeted review outcome tests passed.
- Full `tests.test_cli` passed.
