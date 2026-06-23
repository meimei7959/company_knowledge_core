---
type: ProjectTask
title: AI Native OS Event Bus and Notification hardening
description: Make state changes produce reliable, retryable, auditable notifications and machine-consumable events.
timestamp: "2026-06-20T02:40:00Z"
taskId: KT-OS-EVENT-NOTIFICATION-BUS
taskType: os_maturity_hardening
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - event_bus
  - notification_delivery
  - retry
  - dead_letter
requiredAgents:
  - agent.company-knowledge-core.project-manager
  - agent.company-knowledge-core.development
preferredRunner: []
assignedRunner: runner.meimei-mac-local-codex
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: waiting_runner
priority: critical
dueAt: []
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-task-notification-loop.md
  - docs/ops/central-processor-ops-runbook.md
expectedOutput:
  - EventRecord contract
  - notification routing matrix
  - retry and dead-letter flow
  - delivery status API or CLI
resultRef: []
notificationRefs:
  - notifications/notification.20260621T052918741271Z.md
  - notifications/notification.20260621T053349648701Z.md
  - notifications/notification.20260621T053430462168Z.md
  - notifications/notification.20260621T055524580699Z.md
  - notifications/notification.20260621T055554625657Z.md
  - notifications/notification.20260621T055613439961Z.md
  - notifications/notification.20260621T061855437740Z.md
  - notifications/notification.20260621T062940725596Z.md
auditRefs: []
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_maturity_hardening","category":"project","stage":"","requiredCapabilities":["os_maturity_hardening","event_bus","notification_delivery","retry","dead_letter"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-task-notification-loop.md","docs/ops/central-processor-ops-runbook.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Ensure Agents, Runners, requesters, and human sponsors know what changed without asking.

## Supports Mature OS Capability

Event Bus and Notification.

## Requirements

- State changes emit typed events.
- Notification routing decides PM Agent, executor Agent, requester, human sponsor, or Agent Ring target.
- Delivery has status, retry count, last error, dead-letter, and audit refs.

## Completion Standard

- Task creation, claim, completion, retry, blocked, human-decision-required, approval, publish, and close all trigger expected notifications.
- Failed delivery does not hide workflow state.
- Operators can query undelivered or dead-letter notifications.

## Test Method

- Event-to-notification routing tests.
- Delivery retry and dead-letter tests.
- Feishu and Agent Ring notification contract tests.
