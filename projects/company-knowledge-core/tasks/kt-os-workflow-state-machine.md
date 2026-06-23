---
type: ProjectTask
title: AI Native OS Workflow State Machine hardening
description: Standardize lifecycle states for project, task, discussion, knowledge, notification, evaluation, and improvement workflows.
timestamp: "2026-06-20T02:40:00Z"
taskId: KT-OS-WORKFLOW-STATE-MACHINE
taskType: os_maturity_hardening
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - workflow_state_machine
  - lifecycle_validation
  - transition_audit
requiredAgents:
  - agent.company-knowledge-core.project-manager
preferredRunner: []
assignedRunner: runner.meimei-mac-local-codex
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: waiting_runner
priority: critical
dueAt: []
sourceMaterialRefs:
  - docs/workflows/feishu-intake-lifecycle.md
  - docs/workflows/knowledge-lifecycle.md
  - docs/workflows/evaluation-lifecycle.md
expectedOutput:
  - unified state transition table
  - invalid transition blocker
  - transition audit record
  - workflow lifecycle tests
resultRef: []
notificationRefs:
  - notifications/notification.20260621T052918749025Z.md
  - notifications/notification.20260621T053349655762Z.md
  - notifications/notification.20260621T053430468776Z.md
  - notifications/notification.20260621T055524588760Z.md
  - notifications/notification.20260621T055554633657Z.md
  - notifications/notification.20260621T055613446665Z.md
  - notifications/notification.20260621T061855441591Z.md
  - notifications/notification.20260621T062940733744Z.md
auditRefs: []
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_maturity_hardening","category":"project","stage":"","requiredCapabilities":["os_maturity_hardening","workflow_state_machine","lifecycle_validation","transition_audit"],"requiredTools":[],"sourceRefs":["docs/workflows/feishu-intake-lifecycle.md","docs/workflows/knowledge-lifecycle.md","docs/workflows/evaluation-lifecycle.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Remove hidden manual flow. Every unit of work must move through explicit states.

## Supports Mature OS Capability

Task and Workflow Engine.

## Requirements

- Define valid state machines for ProjectTask, KnowledgeTask, DiscussionSession, KnowledgeItem, TaskResult, NotificationRecord, and AgentImprovementProposal.
- Invalid transitions are blocked and audited.
- Terminal states always trigger the correct next step or closure.

## Completion Standard

- No workflow can remain in an unhandled terminal-adjacent state.
- Every state transition has actor, reason, timestamp, previous state, next state, and audit ref.
- Validation reports unreachable, duplicated, or missing terminal states.

## Test Method

- Unit tests for valid and invalid transitions.
- Lifecycle tests for task created to closed, retry, blocked, and human-decision-required paths.
- Regression test proving a completed node creates notification or next task when required.
