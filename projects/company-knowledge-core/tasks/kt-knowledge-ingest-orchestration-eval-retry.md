---
type: ProjectTask
title: Knowledge ingest orchestration with evaluation and retry
description: Add scheduler-level quality evaluation, retry, repair, and review routing for knowledge intake TaskResult writeback.
timestamp: "2026-06-19T00:00:00Z"
taskId: TASK-KNOWLEDGE-INGEST-ORCHESTRATION-EVAL-RETRY
taskType: engineering_action
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.knowledge-engineering
requiredCapabilities:
  - knowledge_capture
  - task_orchestration
  - quality_evaluation
  - retry
  - review_gate
requiredAgents:
  - agent.company-knowledge-core.knowledge-engineering
  - agent.core.knowledge-review
  - agent.core.knowledge-ops
preferredRunner:
  - runner.meimei-mac-codex
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - docs/workflows/knowledge-ingest-orchestration.md
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/feishu.py
expectedOutput:
  - TaskResult qualityEvaluation
  - Passed extraction routes to Knowledge Review task
  - Failed extraction routes to retry task until maxAttempts
  - Blocked or exhausted extraction routes to Knowledge Ops repair task
  - Manual runner cards explain central context pull
resultRef: ""
notificationRefs: []
auditRefs: []
completedAt: "2026-06-19T00:00:00Z"
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","knowledge_capture","task_orchestration","quality_evaluation","retry","review_gate"],"requiredTools":[],"sourceRefs":["docs/workflows/knowledge-ingest-orchestration.md","zhenzhi_knowledge/core.py","zhenzhi_knowledge/feishu.py"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
---

## Request

Make knowledge recording a closed loop: every Agent result must be evaluated, failed work must retry or repair, and successful extraction must hand off to Knowledge Review automatically.

## Definition Of Done

- `finish_project_task` writes deterministic `qualityEvaluation` for knowledge execution tasks.
- Passing TaskResult creates a `knowledge_review` follow-up task assigned to Knowledge Review Agent.
- Failing but retryable TaskResult creates a `knowledge_retry` follow-up task assigned to the original execution Agent.
- Blocked or exhausted TaskResult creates a `knowledge_repair` follow-up task assigned to Knowledge Ops Agent.
- Follow-up tasks are linked from the TaskResult and original task.
- Knowledge Engineering Agent has active `knowledge:draft` policy.
- Manual runner notification tells local Agents to pull central task context before reading local paths.

## Test Plan

- Unit test successful extraction creates KnowledgeItem draft and review follow-up.
- Unit test missing draft creates retry follow-up.
- Unit test blocked extraction creates repair follow-up.
- HTTP/Feishu intake idempotency test counts only intake tasks, allowing scheduler follow-up tasks.
- Run `python3 -m unittest tests.test_cli`.
- Run `python3 -m zhenzhi_knowledge.cli validate`.

## Completion Evidence

- `tests.test_cli`: 76 tests passed.
- Repository validation: valid.
