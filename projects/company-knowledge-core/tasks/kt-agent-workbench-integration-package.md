---
type: ProjectTask
title: Agent Workbench integration package
description: Prepare the protocol, examples, contract test, and readiness checklist that the external Agent Workbench team needs to connect to the central processor.
timestamp: "2026-06-19T02:10:00Z"
taskId: TASK-AGENT-WORKBENCH-INTEGRATION-PACKAGE
taskType: integration_enablement
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.executor
requiredCapabilities:
  - agent_ring
  - api_contract
  - documentation
  - testing
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
  - docs/protocols/agent-workbench-integration-brief.md
  - docs/protocols/agent-ring-communication-protocol.md
  - docs/harness/agent-ring-stub-test-strategy.md
  - scripts/agent_ring_contract.py
expectedOutput:
  - workbench integration quickstart
  - sample API payloads
  - contract test run instructions
  - readiness checklist for first real Agent Workbench connection
resultRef: task-results/tr-task-agent-workbench-integration-package.md
notificationRefs:
  - notifications/notification.20260619T025644634921Z.md
auditRefs: []
completedAt: "2026-06-19T02:56:44Z"
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"integration_enablement","category":"project","stage":"","requiredCapabilities":["integration_enablement","agent_ring","api_contract","documentation","testing"],"requiredTools":[],"sourceRefs":["docs/protocols/agent-workbench-integration-brief.md","docs/protocols/agent-ring-communication-protocol.md","docs/harness/agent-ring-stub-test-strategy.md","scripts/agent_ring_contract.py"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Let the Agent Workbench developer connect without guessing central processor behavior.

The central processor should provide a clear integration package: what the workbench owns, what the central processor owns, how to register a Runner, how to claim and finish tasks, how to handle leases and failures, and how to prove the connection works.

## Scope

Included:

- API base URL and auth explanation.
- Runner registration sample.
- Runner heartbeat sample.
- Task query sample.
- Claim / pull / task heartbeat / finish sample.
- Failure path examples.
- Contract test command.
- Readiness checklist.

Excluded:

- Workbench subscription design.
- Workbench Agent marketplace.
- Workbench model routing.
- Workbench Skill/tool UI.
- Local desktop service implementation.

## Definition of Done

- A developer-facing quickstart exists and links to the full protocol.
- Every required API call has one copy-pasteable JSON example.
- The package explains lease token handling and why stale/expired leases must not write results.
- The package explains capability matching and missing capability behavior.
- The package explains access-reference handling: central processor stores refs and policy, not local private values.
- `python3 scripts/agent_ring_contract.py` is documented as the first acceptance test.
- The package states that Agent Workbench's own subscriptions, Agent configuration, Codex/Claude/local model integration, Skill/tool management, local security, and UI remain owned by the Workbench project.
- The package includes a clear "first real connection" checklist.

## Test Plan

- Run `python3 scripts/agent_ring_contract.py`.
- Run `python3 -m unittest tests.test_cli`.
- Manually compare quickstart payloads with `zhenzhi_knowledge/server.py` endpoint shapes.
- Verify docs link from `docs/protocols/agent-workbench-integration-brief.md`.
- Ask a non-implementer to identify the first three API calls from the quickstart without reading source code.

## Self-Verification Checklist

- [ ] Quickstart written.
- [ ] Sample payloads included.
- [ ] Contract test command included.
- [ ] Failure paths included.
- [ ] Workbench product scope not constrained.
- [ ] First connection checklist included.
