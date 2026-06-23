---
type: ProjectTask
title: Task lifecycle notification loop
description: Notify requesters and project context when tasks are created, claimed, blocked, finished, or need manual Runner action.
timestamp: "2026-06-19T00:00:00Z"
taskId: TASK-TASK-NOTIFICATION-LOOP
taskType: engineering_action
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.executor
requiredCapabilities:
  - notification
  - feishu_cards
  - task_lifecycle
requiredAgents:
  - agent.company-knowledge-core.executor
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
  - zhenzhi_knowledge/feishu.py
  - zhenzhi_knowledge/core.py
expectedOutput:
  - notification records
  - Feishu requester notifications
  - project log/task notification refs
resultRef: task-results/tr-task-task-notification-loop.md
notificationRefs:
  - notifications/notification.20260619T012710282668Z.md
auditRefs: []
completedAt: "2026-06-19T01:27:10Z"
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","notification","feishu_cards","task_lifecycle"],"requiredTools":[],"sourceRefs":["zhenzhi_knowledge/feishu.py","zhenzhi_knowledge/core.py"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
---

## Request

Close the loop after task creation and task completion.

## Definition of Done

- Task creation records notification target and source message where available.
- `waiting_runner` triggers a readable notification explaining who or what should pick it up.
- Task claim and blocked states are visible in project context.
- Task finish sends requester a completion or blocked notification with result summary and links.
- Notification failures create audit records and do not hide task state changes.
- Tests cover created, waiting_runner, blocked, finished, and notification failure paths.

## Test Plan

- Unit test notification record generation.
- Simulate Feishu response success and failure.
- Verify task `notificationRefs` and audit logs.
- Run `python3 -m unittest tests.test_cli`.

## Self-Verification Checklist

- [x] Requester gets closure.
- [x] Project context records notification state.
- [x] Failure path audited.
- [x] Tests cover lifecycle.
