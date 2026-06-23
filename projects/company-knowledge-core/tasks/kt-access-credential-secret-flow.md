---
type: ProjectTask
title: Access credential and secretRef flow
description: Upgrade token requests into access credential requests with secretRef, approval, Agent Ring, and Secret Manager boundaries.
timestamp: "2026-06-18T00:00:00Z"
taskId: KT-ACCESS-CREDENTIAL-SECRET-FLOW
taskType: engineering_action
projectId: company-knowledge-core
requester: zhenzhi-central-processor
assignee: zhenzhi-knowledge-core
requiredCapabilities:
  - credential_request
  - secret_ref
  - approval_flow
  - audit_log
  - agent_ring_secret_readiness
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
  - docs/protocols/access-credential-request-flow.md
  - docs/agent-team/deepseek-feishu-routing-plan.md
  - docs/harness/agent-ring-stub-test-strategy.md
expectedOutput:
  - CredentialRequest object or task shape
  - Feishu private-chat credential request flow
  - secretRef-only persistence rule
  - central API token vs runner token vs local tool secret decision logic
  - StubRunner tests for secretRef present/missing
  - audit and notification rules
resultRef: task-results/tr-kt-access-credential-secret-flow.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-18T11:07:57Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","credential_request","secret_ref","approval_flow","audit_log","agent_ring_secret_readiness"],"requiredTools":[],"sourceRefs":["docs/protocols/access-credential-request-flow.md","docs/agent-team/deepseek-feishu-routing-plan.md","docs/harness/agent-ring-stub-test-strategy.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
updatedAt: "2026-06-21T07:18:05Z"
---

## Request

Replace the old "bot sends token" mental model with access credential request management.

The central processor owns request, approval, scope, `secretRef`, audit, and notification. Secret values live in server secret store, Secret Manager, or Agent Ring local secure store.

## Required Coverage

- central API token;
- Agent Ring runner registration token;
- local Codex / Claude / Git / browser tool credential;
- DeepSeek API key for Feishu bot;
- project-private third-party service token;
- private chat only for personal setup instructions;
- group chat requests redirected to private chat;
- no plaintext secret in knowledge, tasks, logs, audit details, or group messages.

## Definition of Done

- Credential request flow distinguishes central API token, runner registration token, local tool secret, model API key, and project service token.
- Feishu private-chat flow creates a request record or task with requester, purpose, project, credential type, scope, risk, expiry, and approver.
- Central processor persists `secretRef`, owner, scope, expiry, and audit records only; plaintext secret values are never stored in Markdown, logs, AuditLog details, task descriptions, or group messages.
- Group-chat credential requests are redirected to private chat without exposing setup instructions or secret values.
- Agent Ring or StubRunner path can report credential readiness by `secretRef`.
- Documentation and user-facing replies use "access credential" semantics while preserving the existing "申请知识工程 token" shortcut.

## Test Plan

- Unit test Feishu private credential request creates the expected request/task fields.
- Unit test group-chat credential request returns private-chat guidance and creates no plaintext secret.
- Validation test scans generated project/task/audit files and finds no secret-looking values.
- StubRunner test covers required `secretRef` present and missing cases.
- Regression test keeps the old shortcut "申请知识工程 token" working.
- Run `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate`.
- Run `python3 -m unittest tests.test_cli`.

## Self-Verification Checklist

- Confirm no plaintext token/key appears in changed files or generated fixtures.
- Confirm all approval and audit records are human-readable and use `secretRef`.
- Confirm central API token and local tool token are not treated as the same ownership case.
- Confirm failure states explain what owner or Agent Ring action is needed.
- Confirm tests prove both allowed and blocked paths.
