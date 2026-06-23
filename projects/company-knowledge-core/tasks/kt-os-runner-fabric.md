---
type: ProjectTask
title: AI Native OS Runner Fabric hardening
description: Make distributed computers first-class execution nodes with capabilities, tools, load, heartbeat, lease, and reliability scoring.
timestamp: "2026-06-20T02:40:00Z"
taskId: KT-OS-RUNNER-FABRIC
taskType: os_maturity_hardening
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - runner_registry
  - capability_matching
  - lease_management
  - heartbeat
requiredAgents:
  - agent.company-knowledge-core.project-manager
  - agent.company-knowledge-core.development
preferredRunner: []
assignedRunner: runner.meimei-mac-local-codex
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: waiting_runner
priority: high
dueAt: []
sourceMaterialRefs:
  - docs/protocols/agent-workbench-integration-brief.md
  - docs/scheduler/task-dispatch-model.md
expectedOutput:
  - RunnerFabric contract
  - capability matching score
  - heartbeat and stale-runner rules
  - lease recovery flow
resultRef: []
notificationRefs:
  - notifications/notification.20260621T052918744419Z.md
  - notifications/notification.20260621T053349651589Z.md
  - notifications/notification.20260621T053430465002Z.md
  - notifications/notification.20260621T055524584014Z.md
  - notifications/notification.20260621T055554628929Z.md
  - notifications/notification.20260621T055613442854Z.md
  - notifications/notification.20260621T061855456305Z.md
  - notifications/notification.20260621T062940771412Z.md
auditRefs: []
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_maturity_hardening","category":"project","stage":"","requiredCapabilities":["os_maturity_hardening","runner_registry","capability_matching","lease_management","heartbeat"],"requiredTools":[],"sourceRefs":["docs/protocols/agent-workbench-integration-brief.md","docs/scheduler/task-dispatch-model.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Make task execution target registered computers and Agent Workbench runners, not informal people.

## Supports Mature OS Capability

Runner Fabric.

## Requirements

- Runner records include capabilities, tools, local AI surfaces, data scopes, repository access, load, heartbeat, and reliability score.
- Scheduler chooses runners by capability, risk, permission, load, and health.
- Claimed tasks use leases and can be recovered when a runner is stale.

## Completion Standard

- A task can be matched, claimed, heartbeated, completed, or recovered.
- Stale runners stop receiving new tasks.
- Runner selection decision is auditable.

## Test Method

- Harness test for runner registration, heartbeat, claim, lease expiry, and reassignment.
- Contract test for Agent Workbench compatibility.
- Negative test for missing capability and expired heartbeat.
