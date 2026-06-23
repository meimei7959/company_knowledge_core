---
type: ProjectTask
title: Feishu DeepSeek intent router
description: Add DeepSeek paid API as the Feishu bot intent routing and field extraction layer.
timestamp: "2026-06-18T00:00:00Z"
taskId: KT-FEISHU-DEEPSEEK-ROUTER
taskType: engineering_action
projectId: company-knowledge-core
requester: zhenzhi-central-processor
assignee: zhenzhi-knowledge-core
requiredCapabilities:
  - feishu_bot
  - deepseek_api
  - intent_routing
  - json_output
requiredAgents:
  - scheduler-agent
  - knowledge-architecture-agent
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
expectedOutput:
  - DeepSeek API configuration via secret refs
  - routing prompt and JSON schema
  - fallback behavior when model call fails
  - tests for menu and free-text routing
resultRef: task-results/tr-kt-feishu-deepseek-router.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-18T11:05:31Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","feishu_bot","deepseek_api","intent_routing","json_output"],"requiredTools":[],"sourceRefs":["docs/agent-team/deepseek-feishu-routing-plan.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
updatedAt: "2026-06-21T07:18:05Z"
---

## Request

Connect the Feishu bot to DeepSeek paid API for intent recognition, field extraction, and reply/card planning.

## Boundary

DeepSeek chooses a routing decision. Server-side code validates the decision and executes only registered safe actions.

DeepSeek must not directly perform durable writes, permission changes, deletion, secret reveal, or engineering execution.

## Definition of Done

- Feishu bot can call DeepSeek paid API through configuration that uses secret refs or environment secrets, not committed keys.
- Routing prompt returns a structured JSON decision matching the documented routing schema.
- Server-side parser validates intent, confidence, risk, required fields, direct-handle flag, task type, and allowed tool suggestions.
- Model failure, timeout, malformed JSON, or low confidence falls back to safe clarification or deterministic menu guidance.
- Existing fixed menu shortcuts still work without model dependency.
- No model decision directly performs durable writes; all writes pass server-side validation.

## Test Plan

- Unit test model adapter request construction without real API key.
- Unit test JSON parsing for valid and malformed model outputs.
- Unit test low confidence and missing fields produce clarification.
- Unit test menu shortcuts bypass or safely use routing without regression.
- Integration test with mocked DeepSeek response for create project, query knowledge, capture material, and credential request.
- Safety test ensures model-suggested unregistered tool call is ignored/rejected.
- Run `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate`.
- Run `python3 -m unittest tests.test_cli`.

## Self-Verification Checklist

- Confirm DeepSeek API key is never committed or printed.
- Confirm fallback path works when DeepSeek is unavailable.
- Confirm routing decisions are auditable and reproducible from test fixtures.
- Confirm direct bot actions are limited to safe answer/clarification/status paths.
