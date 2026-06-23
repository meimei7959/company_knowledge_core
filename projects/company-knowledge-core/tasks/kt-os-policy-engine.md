---
type: ProjectTask
title: AI Native OS Policy Engine hardening
description: Centralize rules for auto-run, auto-accept, human approval, security block, escalation, and project-specific overrides.
timestamp: "2026-06-20T02:40:00Z"
taskId: KT-OS-POLICY-ENGINE
taskType: os_maturity_hardening
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - policy_engine
  - acceptance_policy
  - risk_gate
  - override_audit
requiredAgents:
  - agent.company-knowledge-core.project-manager
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
  - knowledge/policies/policy.company-knowledge-engineering.md
  - knowledge/policies/policy.knowledge-review.md
expectedOutput:
  - PolicyDecision object
  - auto-accept and human-required rules
  - override and escalation flow
  - policy evaluation tests
resultRef: []
notificationRefs:
  - notifications/notification.20260621T052918743288Z.md
  - notifications/notification.20260621T053349650620Z.md
  - notifications/notification.20260621T053430464078Z.md
  - notifications/notification.20260621T055524582850Z.md
  - notifications/notification.20260621T055554627863Z.md
  - notifications/notification.20260621T055613441882Z.md
  - notifications/notification.20260621T061855439694Z.md
  - notifications/notification.20260621T062940731017Z.md
auditRefs: []
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_maturity_hardening","category":"project","stage":"","requiredCapabilities":["os_maturity_hardening","policy_engine","acceptance_policy","risk_gate","override_audit"],"requiredTools":[],"sourceRefs":["knowledge/policies/policy.company-knowledge-engineering.md","knowledge/policies/policy.knowledge-review.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Make governance explicit so normal work is autonomous and high-risk work is controlled.

## Supports Mature OS Capability

Policy Engine.

## Requirements

- Policy engine returns allow, deny, require-human, require-owner-approval, require-retry, require-repair, or escalate.
- Decisions include matched rule, reason, actor, input summary, and audit ref.
- Project-level policy can tighten company policy but cannot weaken safety rules.

## Completion Standard

- PM Agent can auto-accept low-risk outputs.
- High-risk outputs require human or owner approval.
- Policy decisions are visible in TaskResult and NotificationRecord.

## Test Method

- Policy evaluation tests for low, medium, high, and blocked risk.
- Override audit test.
- Project policy precedence test.
