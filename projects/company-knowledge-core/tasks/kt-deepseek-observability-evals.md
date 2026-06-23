---
type: ProjectTask
title: DeepSeek routing observability and evals
description: Add logs, cost tracking, and eval cases for DeepSeek-powered Feishu routing.
timestamp: "2026-06-18T00:00:00Z"
taskId: KT-DEEPSEEK-OBSERVABILITY-EVALS
taskType: engineering_action
projectId: company-knowledge-core
requester: zhenzhi-central-processor
assignee: zhenzhi-knowledge-core
requiredCapabilities:
  - model_eval
  - observability
  - cost_tracking
  - regression_tests
requiredAgents:
  - knowledge-review-agent
  - scheduler-agent
preferredRunner: []
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: medium
dueAt: []
sourceMaterialRefs:
  - docs/agent-team/deepseek-feishu-routing-plan.md
expectedOutput:
  - routing eval cases
  - misroute review workflow
  - token/cost/error metrics
  - fallback tests for DeepSeek outage
resultRef: task-results/tr-kt-deepseek-observability-evals.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-18T11:28:32Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","model_eval","observability","cost_tracking","regression_tests"],"requiredTools":[],"sourceRefs":["docs/agent-team/deepseek-feishu-routing-plan.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
updatedAt: "2026-06-21T07:18:05Z"
---

## Request

Make DeepSeek routing measurable and reviewable.

## Required Coverage

- create project with existing repo;
- create project from scratch;
- query knowledge by project name;
- capture meeting notes;
- request token privately;
- request token in group;
- request deletion or permission change;
- submit long document;
- ambiguous free-text request;
- DeepSeek API failure or malformed JSON.

## Definition of Done

- Routing eval suite covers project creation, knowledge query, material capture, credential request, tool request, dangerous requests, ambiguous text, and API failure.
- Each eval asserts expected intent, risk level, direct-handle vs task routing, missing fields, and recommended reply type.
- Observability records model name, mode, latency, token usage or estimated cost, error class, fallback path, and user/chat scope without storing sensitive prompt data unnecessarily.
- Misrouted cases can be reviewed and converted into regression evals.
- DeepSeek outage or malformed JSON falls back to deterministic safe guidance instead of executing actions.

## Test Plan

- Unit tests for routing eval fixtures and expected structured routing decisions.
- Unit tests for malformed JSON, timeout, API error, and low confidence fallback.
- Metrics test verifies token/cost/error fields are captured without secret leakage.
- Regression tests cover private vs group credential requests.
- Run `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate`.
- Run `python3 -m unittest tests.test_cli`.

## Self-Verification Checklist

- Confirm eval cases include both success and refusal/clarification paths.
- Confirm logs do not contain API keys, plaintext secrets, or full sensitive user content.
- Confirm every failed model response becomes safe no-op, clarification, or task creation.
- Confirm new evals are easy to extend when production misroutes appear.
