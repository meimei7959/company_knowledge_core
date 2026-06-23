---
type: ProjectTask
title: AI Native OS test - governance, quality, ops, and API
description: Validate governance gates, review routing, notification repair, admin disable, quality metrics, feedback, experiment guard, and API envelope behavior.
timestamp: "2026-06-21T07:18:00Z"
taskId: kt-ai-native-os-test-governance-quality-ops-api
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"engineering","stage":"test","requiredCapabilities":["testing","governance","api","quality_gate"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-ai-native-os-impl-governance-quality-ops-api.md","task-results/tr-kt-ai-native-os-impl-governance-quality-ops-api.md","projects/company-knowledge-core/technical-solutions/ai-native-os-governance-quality-ops-api.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_and_product_review","reviewPath":"test_then_pm_review","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - testing
  - governance
  - api
  - quality_gate
requiredAgents:
  - agent.company.test
executorAgent: agent.company.test
status: done
priority: critical
currentStage: test
requirementRefs:
  - ANOS-REQ-080
  - ANOS-REQ-081
  - ANOS-REQ-082
  - ANOS-REQ-083
  - ANOS-REQ-084
  - ANOS-REQ-090
  - ANOS-REQ-091
  - ANOS-REQ-092
  - ANOS-REQ-093
  - ANOS-REQ-100
  - ANOS-REQ-101
  - ANOS-REQ-102
  - ANOS-REQ-110
  - ANOS-REQ-111
  - ANOS-REQ-112
  - ANOS-REQ-113
  - ANOS-REQ-114
  - ANOS-REQ-120
  - ANOS-REQ-121
  - ANOS-REQ-122
  - ANOS-REQ-130
  - ANOS-REQ-131
  - ANOS-REQ-132
  - ANOS-REQ-133
  - ANOS-REQ-140
  - ANOS-REQ-141
  - ANOS-REQ-142
  - ANOS-REQ-150
  - ANOS-REQ-151
  - ANOS-REQ-152
sourceMaterialRefs:
  - task-results/tr-kt-ai-native-os-impl-governance-quality-ops-api.md
  - projects/company-knowledge-core/technical-solutions/ai-native-os-governance-quality-ops-api.md
expectedOutput:
  - Test Agent validates governance, quality, ops, and API regression coverage.
  - Test Agent confirms review gates do not block traceable work-state writes.
  - Any failure must be returned to Development Agent through a repair task.
updatedAt: "2026-06-21T08:12:51Z"
assignedRunner: runner.meimei-mac-local-test-1
leaseOwner: runner.meimei-mac-local-test-1
leaseTokenHash: 56a5302f4ab6dbfb0bddf67c2b264a49995cb71df6b6b1ad402ca38e5729c79c
leaseProofHash: 56a5302f4ab6dbfb0bddf67c2b264a49995cb71df6b6b1ad402ca38e5729c79c
leaseIssuedAt: "2026-06-21T07:45:04Z"
leaseExpiresAt: "2026-06-21T08:15:04Z"
leaseHeartbeatAt: "2026-06-21T07:45:04Z"
heartbeatAt: "2026-06-21T07:45:04Z"
leaseVersion: 3
leaseAttempt: 2
taskVersion: 3
notificationRefs:
  - notifications/notification.20260621T071855545661Z.md
  - notifications/notification.20260621T074504828245Z.md
  - notifications/notification.20260621T074633505607Z.md
  - notifications/notification.20260621T074633507271Z.md
  - notifications/notification.20260621T074633508105Z.md
  - notifications/notification.20260621T081251950612Z.md
resultRef: task-results/tr-kt-ai-native-os-test-governance-quality-ops-api.md
completedAt: "2026-06-21T07:46:33Z"
---

# Test Scope

Validate governance and API behavior without modifying implementation files.

# Required Checks

- Run focused governance/API tests.
- Run broader unit discovery when feasible.
- Confirm safety boundaries, review routing, notification repair, and API envelopes have test evidence.
- Confirm external Feishu/API delivery remains an explicit risk, not an implicit pass.
