---
type: ProjectTask
title: Feishu to Agent Ring task dispatch
description: Route complex Feishu requests into central tasks that Agent Ring runners can claim.
timestamp: "2026-06-18T00:00:00Z"
taskId: KT-FEISHU-AGENT-RING-DISPATCH
taskType: engineering_action
projectId: company-knowledge-core
requester: zhenzhi-central-processor
assignee: zhenzhi-knowledge-core
requiredCapabilities:
  - task_creation
  - scheduler_matching
  - agent_ring_protocol
  - project_context_bundle
requiredAgents:
  - scheduler-agent
  - agent-ring-integration-agent
preferredRunner: []
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - docs/agent-team/deepseek-feishu-routing-plan.md
  - docs/protocols/agent-ring-communication-protocol.md
  - docs/protocols/project-context-sync-protocol.md
expectedOutput:
  - mapping from DeepSeek routing decision to ProjectTask/KnowledgeTask
  - task context bundle generation requirements
  - runner capability requirements per task type
  - notification behavior after task result writeback
resultRef: task-results/tr-kt-feishu-agent-ring-dispatch.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-18T11:29:07Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","task_creation","scheduler_matching","agent_ring_protocol","project_context_bundle"],"requiredTools":[],"sourceRefs":["docs/agent-team/deepseek-feishu-routing-plan.md","docs/protocols/agent-ring-communication-protocol.md","docs/protocols/project-context-sync-protocol.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
updatedAt: "2026-06-21T07:18:05Z"
---

## Request

Ensure Feishu requests that are too complex for the bot become central tasks and are dispatched to eligible Agent Ring runners.

## Examples

- meeting note parsing -> KnowledgeTask
- long document extraction -> KnowledgeTask
- repo bootstrap -> ProjectTask
- code implementation -> ProjectTask
- handoff or cross-computer continuation -> handoff task

## Definition of Done

- DeepSeek routing decisions map deterministically to ProjectTask, KnowledgeTask, credential request, or safe direct response.
- Complex Feishu requests create tasks with project name/id resolution, readable title, source refs, required capabilities, expected output, risk level, and notification target.
- Tasks that require execution are eligible for Agent Ring or StubRunner dispatch and include enough context bundle requirements.
- Requester receives a human-readable task card with next step and status; no raw internal ID is the only explanation.
- Task result writeback triggers notification and review state updates.

## Test Plan

- E2E test meeting note message creates SourceMaterial + KnowledgeTask with required capabilities.
- E2E test long document/material message routes to KnowledgeTask, not direct bot answer.
- E2E test repo bootstrap/project init routes to ProjectTask.
- E2E test ambiguous project name asks clarification before task creation.
- StubRunner test claims and completes a Feishu-created task.
- Notification test verifies requester receives status/result after TaskResult writeback.
- Run `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate`.
- Run `python3 -m unittest tests.test_cli`.

## Self-Verification Checklist

- Confirm no complex work is executed directly inside Feishu bot handler.
- Confirm all created tasks link SourceMaterial or project context.
- Confirm human-facing cards use project names and task titles.
- Confirm task can be completed by StubRunner before real Agent Ring exists.
