---
type: ProjectTask
title: Agent Workbench central contract tests
description: Provide executable contract tests so the external Agent Workbench team can verify integration with the central processor.
timestamp: "2026-06-19T00:00:00Z"
taskId: TASK-AGENT-WORKBENCH-CONTRACT-TESTS
taskType: engineering_action
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.executor
requiredCapabilities:
  - contract_tests
  - agent_ring
  - api_testing
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
expectedOutput:
  - contract test harness
  - sample Runner registration payload
  - sample task claim/pull/finish sequence
  - failure case assertions
resultRef: task-results/tr-task-agent-workbench-contract-tests.md
notificationRefs:
  - notifications/notification.20260619T014801638492Z.md
  - notifications/notification.20260619T014853029109Z.md
auditRefs: []
completedAt: "2026-06-19T01:48:53Z"
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","contract_tests","agent_ring","api_testing"],"requiredTools":[],"sourceRefs":["docs/protocols/agent-workbench-integration-brief.md","docs/protocols/agent-ring-communication-protocol.md","docs/harness/agent-ring-stub-test-strategy.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
---

## Request

Give the Agent Workbench team a testable contract, not only prose documentation.

## Definition of Done

- A contract test can run against a local test bundle and against the HTTP API.
- It verifies health, register, heartbeat, task query, claim, task heartbeat, pull, finish, and TaskResult.
- It verifies failure paths: unauthorized, missing capability, stale version, invalid lease token, expired lease.
- Test fixture does not require real secrets or real Codex execution.
- Documentation explains how Agent Workbench developers should run the tests.

## Test Plan

- Add or update Python unittest coverage.
- Add a small CLI or script for workbench developers if needed.
- Run `python3 -m unittest tests.test_cli`.

## Self-Verification Checklist

- [x] Happy path contract covered.
- [x] Failure paths covered.
- [x] No real secret required.
- [x] Documentation linked from Agent Workbench brief.
