---
type: ProjectTask
title: Agent Ring protocol integration handoff
description: Define how the external Agent Ring workstation connects to the central processor.
timestamp: "2026-06-18T00:00:00Z"
taskId: KT-AGENT-RING-PROTOCOL
taskType: engineering_action
projectId: company-knowledge-core
requester: zhenzhi-central-processor
assignee: agent-ring-team
requiredCapabilities:
  - runner_registration
  - task_claim
  - heartbeat
  - local_agent_execution
  - task_result_writeback
requiredAgents:
  - agent-ring-implementation
preferredRunner: []
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - docs/protocols/agent-ring-communication-protocol.md
  - docs/architecture/central-processor-and-agent-ring.md
expectedOutput:
  - Agent Ring implements runner registration
  - Agent Ring implements task polling or claiming
  - Agent Ring writes TaskResult and heartbeat according to protocol
resultRef: task-results/tr-kt-agent-ring-protocol.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-18T11:15:40Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","runner_registration","task_claim","heartbeat","local_agent_execution","task_result_writeback"],"requiredTools":[],"sourceRefs":["docs/protocols/agent-ring-communication-protocol.md","docs/architecture/central-processor-and-agent-ring.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
updatedAt: "2026-06-21T07:18:05Z"
---

## Request

Build Agent Ring as an external workstation/connector that registers distributed computers and local Agents with the central processor.

## Boundary

This repository owns the central processor, protocol, scheduler state, task queue, knowledge state, review, audit, and notifications.

Agent Ring owns its own runtime implementation, UI/service shape, local Codex / Claude / model invocation, local logs, and process supervision.

## Protocol References

- `docs/protocols/agent-ring-communication-protocol.md`
- `docs/architecture/central-processor-and-agent-ring.md`

## Expected Output

- Runner registration contract implemented or reviewed.
- Task polling/claiming contract implemented or reviewed.
- Heartbeat and lease behavior implemented or reviewed.
- TaskResult writeback contract implemented or reviewed.

## Definition of Done

- Agent Ring contract supports runner registration, capability reporting, heartbeat, task polling/claiming, lease ownership, context pull, TaskResult writeback, and status transitions.
- Central processor rejects invalid claims, expired leases, stale task versions, and writebacks without the current lease token.
- Protocol docs and any API/CLI contract examples match the implemented payload shapes.
- Agent Ring remains external; this repository stores protocol, records, tests, and central-side handlers only.
- Real Agent Ring implementer can use this task and linked protocol docs without needing undocumented assumptions.

## Test Plan

- Contract test valid runner registration and heartbeat.
- Contract test task poll/claim with required capability and project permission.
- Contract test rejected claim for missing capability, invalid status, or stale task version.
- Contract test TaskResult writeback with valid lease token and rejected writeback with invalid/expired token.
- Contract test idempotent registration and result submission.
- Run `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate`.
- Run `python3 -m unittest tests.test_cli`.

## Self-Verification Checklist

- Confirm no Agent Ring runtime implementation leaked into central repository scope.
- Confirm protocol docs, task fields, and tests use the same names for runner, lease, heartbeat, and result fields.
- Confirm every state transition writes or references audit evidence.
- Confirm failure responses are actionable for the external Agent Ring implementer.
