---
type: ProjectTask
title: AI Native OS Context Pack Engine hardening
description: Make every task portable across computers by producing a complete, bounded, evidence-linked context pack.
timestamp: "2026-06-20T02:40:00Z"
taskId: KT-OS-CONTEXT-PACK-ENGINE
taskType: os_maturity_hardening
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - context_pack
  - cross_runner_handoff
  - evidence_refs
requiredAgents:
  - agent.company-knowledge-core.knowledge-engineering
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
  - docs/protocols/project-context-sync-protocol.md
  - docs/protocols/agent-workbench-integration-brief.md
expectedOutput:
  - ProjectContextPack contract
  - pack generation command or API
  - pack validation command
  - cross-runner handoff harness
resultRef: []
notificationRefs:
  - notifications/notification.20260621T052918738050Z.md
  - notifications/notification.20260621T053349646445Z.md
  - notifications/notification.20260621T053430460136Z.md
  - notifications/notification.20260621T055524578437Z.md
  - notifications/notification.20260621T055554623422Z.md
  - notifications/notification.20260621T055613437739Z.md
  - notifications/notification.20260621T061855435553Z.md
  - notifications/notification.20260621T062940720076Z.md
auditRefs: []
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_maturity_hardening","category":"project","stage":"","requiredCapabilities":["os_maturity_hardening","context_pack","cross_runner_handoff","evidence_refs"],"requiredTools":[],"sourceRefs":["docs/protocols/project-context-sync-protocol.md","docs/protocols/agent-workbench-integration-brief.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Allow any qualified Runner to continue a project without re-explaining context.

## Supports Mature OS Capability

Context Pack Engine.

## Requirements

- Context pack includes project state, task state, source refs, evidence refs, decisions, previous TaskResults, AgentRuns, environment manifest, repositories, tool refs, secret refs, and known blockers.
- Pack excludes secret values and local-only paths as canonical state.
- Pack is bounded and prioritized so Agents do not drown in stale context.

## Completion Standard

- A task can be pulled on Runner A, reassigned to Runner B, and completed with the same required context.
- Missing source, missing evidence, stale repository ref, or unavailable tool creates a typed blocker.

## Test Method

- Contract test generates a context pack for a project task.
- Handoff test simulates two runners and verifies no required context is lost.
- Security test verifies secret values are never embedded.
