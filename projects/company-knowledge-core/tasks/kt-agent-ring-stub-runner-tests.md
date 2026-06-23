---
type: ProjectTask
title: Agent Ring stub runner tests
description: Build a stub runner test harness so the central processor can be tested before Agent Ring is implemented.
timestamp: "2026-06-18T00:00:00Z"
taskId: KT-AGENT-RING-STUB-RUNNER-TESTS
taskType: engineering_action
projectId: company-knowledge-core
requester: zhenzhi-central-processor
assignee: zhenzhi-knowledge-core
requiredCapabilities:
  - test_harness
  - runner_registration
  - task_claim
  - context_bundle
  - task_result_writeback
  - lease_reassignment
  - secret_ref_simulation
requiredAgents:
  - scheduler-agent
  - knowledge-review-agent
  - agent-ring-integration-agent
preferredRunner: []
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - docs/harness/agent-ring-stub-test-strategy.md
  - docs/protocols/agent-ring-communication-protocol.md
  - docs/protocols/project-context-sync-protocol.md
  - docs/protocols/access-credential-request-flow.md
expectedOutput:
  - in-process or CLI stub runner
  - central chain E2E test without real Agent Ring
  - deterministic TaskResult writeback
  - lease expiry and reassignment test
  - secretRef present/missing tests without plaintext secret values
  - contract test vectors reusable by real Agent Ring
resultRef: task-results/tr-kt-agent-ring-stub-runner-tests.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-18T11:15:52Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","test_harness","runner_registration","task_claim","context_bundle","task_result_writeback","lease_reassignment","secret_ref_simulation"],"requiredTools":[],"sourceRefs":["docs/harness/agent-ring-stub-test-strategy.md","docs/protocols/agent-ring-communication-protocol.md","docs/protocols/project-context-sync-protocol.md","docs/protocols/access-credential-request-flow.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
updatedAt: "2026-06-21T07:18:05Z"
---

## Request

Add tests that prove the central processor works before the external Agent Ring workstation is ready.

## Required Flow

```txt
Feishu/CLI intake
-> SourceMaterial
-> KnowledgeTask or ProjectTask
-> StubRunner registration
-> task poll/claim
-> context bundle pull
-> fake secretRef readiness check when task requires credentials
-> deterministic TaskResult writeback
-> AgentRun/audit/review/notification state
```

## Boundary

The stub runner tests the central contract. It must not pretend to validate local Codex quality, desktop stability, browser sessions, or real local tool side effects.

## Definition of Done

- StubRunner can register as an AgentRunner with deterministic capabilities, agent identity, heartbeat, and load.
- StubRunner can poll or receive an eligible task, claim it with lease fields, pull context, write a deterministic TaskResult, and update task status.
- StubRunner tests cover SourceMaterial -> KnowledgeTask -> TaskResult and ProjectTask -> TaskResult paths.
- StubRunner tests cover expired lease and reassignment to a second stub runner.
- StubRunner tests cover required `secretRef` present and missing without using plaintext secrets.
- Contract vectors are reusable later against real Agent Ring.

## Test Plan

- E2E test Feishu/CLI intake creates SourceMaterial and KnowledgeTask, then StubRunner completes it.
- E2E test ProjectTask dispatch creates TaskResult with runnerId, executorAgent, source refs, evidence refs, and checks.
- Failure test missing capability blocks assignment.
- Failure test expired heartbeat releases or reassigns task.
- Failure test missing `secretRef` returns blocked status and does not write plaintext secret.
- Regression test ensures StubRunner output never claims real code/browser/local-tool execution happened.
- Run `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate`.
- Run `python3 -m unittest tests.test_cli`.

## Self-Verification Checklist

- Confirm StubRunner tests fail if TaskResult lacks taskId, runnerId, executorAgent, source refs, or status.
- Confirm central chain can be tested without real Agent Ring installed.
- Confirm simulated output is clearly marked deterministic/stubbed.
- Confirm reassignment tests prove project continuation is not tied to one computer.
