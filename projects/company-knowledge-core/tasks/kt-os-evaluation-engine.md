---
type: ProjectTask
title: AI Native OS Evaluation Engine hardening
description: Ensure every Agent deliverable is evaluated and routed to accept, retry, repair, escalate, or improvement.
timestamp: "2026-06-20T02:40:00Z"
taskId: KT-OS-EVALUATION-ENGINE
taskType: os_maturity_hardening
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - quality_evaluation
  - retry_policy
  - repair_task
  - acceptance_gate
requiredAgents:
  - agent.company-knowledge-core.project-manager
  - agent.company-knowledge-core.test
  - agent.company-knowledge-core.knowledge-engineering
preferredRunner: []
assignedRunner: runner.meimei-mac-local-codex
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: waiting_runner
priority: critical
dueAt: []
sourceMaterialRefs:
  - docs/workflows/evaluation-lifecycle.md
expectedOutput:
  - EvaluationResult contract
  - role-specific acceptance criteria
  - retry and repair routing
  - evaluation coverage tests
resultRef: []
notificationRefs:
  - notifications/notification.20260621T052918740122Z.md
  - notifications/notification.20260621T053349647731Z.md
  - notifications/notification.20260621T053430461168Z.md
  - notifications/notification.20260621T055524579660Z.md
  - notifications/notification.20260621T055554624569Z.md
  - notifications/notification.20260621T055613438952Z.md
  - notifications/notification.20260621T061855436753Z.md
  - notifications/notification.20260621T062940722937Z.md
auditRefs: []
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_maturity_hardening","category":"project","stage":"","requiredCapabilities":["os_maturity_hardening","quality_evaluation","retry_policy","repair_task","acceptance_gate"],"requiredTools":[],"sourceRefs":["docs/workflows/evaluation-lifecycle.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Prevent bad Agent output from silently becoming progress.

## Supports Mature OS Capability

Evaluation Engine.

## Requirements

- Every TaskResult receives qualityEvaluation with score, criteria, evidence, verdict, and next action.
- Failed outputs create retry, repair, escalation, or improvement tasks.
- Evaluation policy is role-specific and task-type-specific.

## Completion Standard

- No TaskResult can close a task without evaluation unless policy explicitly permits.
- Retry loops have max attempts and escalation.
- Evaluation failure notifies the PM Agent and relevant executor.

## Test Method

- Good result accepted test.
- Low score retry test.
- Repeated failure escalation test.
- Evaluation missing blocker test.
