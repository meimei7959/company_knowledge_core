---
type: ProjectTask
title: AI Native OS Tool Registry and persistence policy hardening
description: Govern tool usage, risk, permissions, result persistence, and audit without unnecessarily blocking tool invocation.
timestamp: "2026-06-20T02:40:00Z"
taskId: KT-OS-TOOL-REGISTRY-POLICY
taskType: os_maturity_hardening
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - tool_registry
  - tool_risk_policy
  - result_persistence_policy
  - audit
requiredAgents:
  - agent.company-knowledge-core.project-manager
  - agent.company-knowledge-core.knowledge-engineering
preferredRunner: []
assignedRunner: runner.meimei-mac-local-codex
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: waiting_runner
priority: high
dueAt: []
sourceMaterialRefs:
  - docs/tools/core-tool-contract.md
  - projects/company-knowledge-core/tools.md
expectedOutput:
  - ToolAsset policy contract
  - invocation versus persistence distinction
  - risk-based approval rules
  - audit and secret-safety tests
resultRef: []
notificationRefs:
  - notifications/notification.20260621T052918748084Z.md
  - notifications/notification.20260621T053349654761Z.md
  - notifications/notification.20260621T053430467713Z.md
  - notifications/notification.20260621T055524587625Z.md
  - notifications/notification.20260621T055554632522Z.md
  - notifications/notification.20260621T055613445714Z.md
  - notifications/notification.20260621T061855459470Z.md
  - notifications/notification.20260621T062940779581Z.md
auditRefs: []
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_maturity_hardening","category":"project","stage":"","requiredCapabilities":["os_maturity_hardening","tool_registry","tool_risk_policy","result_persistence_policy","audit"],"requiredTools":[],"sourceRefs":["docs/tools/core-tool-contract.md","projects/company-knowledge-core/tools.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Let Agents use tools while controlling what outputs can enter projects or knowledge.

## Supports Mature OS Capability

Tool Registry.

## Requirements

- Tool invocation permission is separate from result persistence permission.
- ToolAsset declares risk, owner, required scopes, allowed Agents, output sensitivity, persistence rules, and approval rules.
- Secret values and customer-sensitive outputs cannot be stored as knowledge.

## Completion Standard

- Low-risk tools can be used without creating unnecessary bottlenecks.
- High-risk persistence creates approval or blocks with readable reason.
- Every tool invocation and persistence decision is auditable.

## Test Method

- Tool validation tests.
- Invocation allowed but persistence blocked test.
- Secret leakage prevention test.
