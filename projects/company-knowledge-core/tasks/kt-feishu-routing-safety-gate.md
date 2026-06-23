---
type: ProjectTask
title: Feishu routing safety gate
description: Validate DeepSeek routing output before any tool call, task creation, or knowledge write.
timestamp: "2026-06-18T00:00:00Z"
taskId: KT-FEISHU-ROUTING-SAFETY
taskType: engineering_action
projectId: company-knowledge-core
requester: zhenzhi-central-processor
assignee: zhenzhi-knowledge-core
requiredCapabilities:
  - model_output_validation
  - safety_policy
  - audit_log
  - permission_gate
requiredAgents:
  - knowledge-review-agent
  - scheduler-agent
preferredRunner: []
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - docs/agent-team/deepseek-feishu-routing-plan.md
  - docs/protocols/access-credential-request-flow.md
  - docs/tools/core-tool-contract.md
expectedOutput:
  - routing decision validator
  - risk-level mapping
  - high-risk refusal/approval path
  - secretRef-only persistence checks
  - tests for deletion, token, permission, and unregistered-tool requests
resultRef: task-results/tr-kt-feishu-routing-safety.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-18T11:29:31Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","model_output_validation","safety_policy","audit_log","permission_gate"],"requiredTools":[],"sourceRefs":["docs/agent-team/deepseek-feishu-routing-plan.md","docs/protocols/access-credential-request-flow.md","docs/tools/core-tool-contract.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
updatedAt: "2026-06-21T07:18:05Z"
---

## Request

Add a safety gate after DeepSeek routing and before any action.

## Required Behavior

- Reject malformed routing JSON.
- Ask clarification when confidence is low.
- Refuse or create approval tasks for high-risk requests.
- Never execute unregistered tools.
- Never send secrets in group chats.
- Never persist plaintext secrets; persist `secretRef`, owner, scope, expiry, and audit only.
- Write audit records for blocked high-risk intents.

## Definition of Done

- Every DeepSeek routing decision passes through a schema validator and policy gate before any action.
- Risk levels map to allowed direct action, clarification, task creation, approval request, or refusal.
- Dangerous requests for deletion, permission changes, token/secret exposure, verified publication, customer commitment, or unregistered tools cannot execute directly.
- Credential paths persist only `secretRef` and metadata.
- Blocked high-risk requests create audit records with safe summaries and no sensitive values.
- Safety gate behavior is consistent across menu shortcuts, free-text messages, private chats, and group chats.

## Test Plan

- Unit tests for malformed routing JSON, unknown intent, unknown tool, and missing risk level.
- Unit tests for deletion, permission change, secret exposure, token request in group, verified publication, and customer commitment.
- Unit tests for low-risk safe query and status request.
- File scan test ensures no plaintext secret appears after credential request handling.
- Regression test verifies legitimate task creation still works after safety gate.
- Run `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate`.
- Run `python3 -m unittest tests.test_cli`.

## Self-Verification Checklist

- Confirm safety gate defaults to deny or clarify, not execute.
- Confirm audit messages are useful but do not leak sensitive content.
- Confirm model output is treated as untrusted input.
- Confirm tests cover both private and group chat differences.
