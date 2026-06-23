---
type: ProjectTask
title: Mature AI Native OS Runner distributed execution network
description: Make Agent Ring runners, leases, heartbeats, task pull, context packs, and cross-computer handoff operate as one execution network.
timestamp: "2026-06-20T03:00:00Z"
taskId: KT-OS-RUNNER-EXECUTION-NETWORK
taskType: os_master_task
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - runner_registry
  - capability_matching
  - task_claim
  - context_pack
  - cross_runner_handoff
requiredAgents:
  - agent.company-knowledge-core.project-manager
  - agent.company-knowledge-core.development
preferredRunner: []
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: critical
dueAt: []
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-os-runner-fabric.md
  - projects/company-knowledge-core/tasks/kt-os-context-pack-engine.md
  - docs/protocols/agent-workbench-integration-brief.md
expectedOutput:
  - runner registration and heartbeat
  - lease-based task claim and recovery
  - portable task context pack
  - Agent Workbench contract tests
resultRef: task-results/tr-kt-os-runner-execution-network.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-20T03:30:00Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_master_task","category":"project","stage":"","requiredCapabilities":["os_master_task","runner_registry","capability_matching","task_claim","context_pack","cross_runner_handoff"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-os-runner-fabric.md","projects/company-knowledge-core/tasks/kt-os-context-pack-engine.md","docs/protocols/agent-workbench-integration-brief.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
updatedAt: "2026-06-21T07:18:05Z"
---

## Goal

Any qualified registered computer can receive, claim, execute, and hand off work without losing context.

## Covers

- `KT-OS-RUNNER-FABRIC`
- `KT-OS-CONTEXT-PACK-ENGINE`

## Completion Standard

- Runner registry records capabilities, projects, repositories, data scopes, load, and heartbeat.
- Task claim uses lease token and rejects invalid or stale claims.
- Context pack includes required project, task, source, evidence, decision, policy, environment, and handoff data without secret values.
- Agent Workbench can use the protocol without implementation-specific guessing.

## Test Method

- Runner register and heartbeat tests.
- Task pull, claim, heartbeat, finish, and HTTP lifecycle tests.
- Context pack and environment manifest tests.
- Agent Workbench contract script.
