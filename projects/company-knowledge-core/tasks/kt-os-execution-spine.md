---
type: ProjectTask
title: Mature AI Native OS execution spine
description: Unify workflow state machine, events, notifications, audit, and lifecycle closure into the operating spine for all company work.
timestamp: "2026-06-20T03:00:00Z"
taskId: KT-OS-EXECUTION-SPINE
taskType: os_master_task
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - workflow_state_machine
  - event_bus
  - notification_delivery
  - audit
requiredAgents:
  - agent.company-knowledge-core.project-manager
preferredRunner: []
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: critical
dueAt: []
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-os-workflow-state-machine.md
  - projects/company-knowledge-core/tasks/kt-os-event-notification-bus.md
  - projects/company-knowledge-core/tasks/kt-task-notification-loop.md
expectedOutput:
  - valid lifecycle states for all work objects
  - typed state transition audit
  - notification retry and dead-letter handling
  - lifecycle closure tests
resultRef: task-results/tr-kt-os-execution-spine.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-20T03:30:00Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_master_task","category":"project","stage":"","requiredCapabilities":["os_master_task","workflow_state_machine","event_bus","notification_delivery","audit"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-os-workflow-state-machine.md","projects/company-knowledge-core/tasks/kt-os-event-notification-bus.md","projects/company-knowledge-core/tasks/kt-task-notification-loop.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
updatedAt: "2026-06-21T07:18:05Z"
---

## Goal

All work must move through an explicit lifecycle. No project, task, discussion, knowledge review, notification, or improvement item may depend on a human asking "what happened next".

## Covers

- `KT-OS-WORKFLOW-STATE-MACHINE`
- `KT-OS-EVENT-NOTIFICATION-BUS`

## Completion Standard

- State transitions reject illegal backward moves and closed-state mutation.
- Terminal and gated states create next task, notification, audit, closure, retry, repair, escalation, or human-decision request.
- Notifications support pending, sent, failed, retrying, and dead-letter states.
- Operators can query pending, failed, retrying, and dead-letter notifications.

## Test Method

- Task lifecycle tests cover create, claim, finish, blocked, retry, acceptance, and close.
- Notification tests cover failed, retrying, dead-letter, and audit actions.
- CLI and HTTP notification delivery endpoints are covered.
