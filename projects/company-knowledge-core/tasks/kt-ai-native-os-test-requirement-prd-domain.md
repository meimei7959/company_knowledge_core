---
type: ProjectTask
title: AI Native OS test - requirement, PRD, and decision domain
description: Validate Requirement, PRD, AcceptanceCriteria, Decision, and ImpactReview implementation for the accepted requirement domain slice.
timestamp: "2026-06-21T07:18:00Z"
taskId: kt-ai-native-os-test-requirement-prd-domain
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"engineering","stage":"test","requiredCapabilities":["testing","quality_gate","requirement_traceability"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-ai-native-os-impl-requirement-prd-domain.md","task-results/tr-kt-ai-native-os-impl-requirement-prd-domain.md","projects/company-knowledge-core/technical-solutions/ai-native-os-requirement-prd-domain.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_and_product_review","reviewPath":"test_then_pm_review","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - testing
  - quality_gate
  - requirement_traceability
requiredAgents:
  - agent.company.test
executorAgent: agent.company.test
status: done
priority: critical
currentStage: test
requirementRefs:
  - ANOS-REQ-010
  - ANOS-REQ-011
  - ANOS-REQ-012
  - ANOS-REQ-013
  - ANOS-REQ-014
  - ANOS-REQ-015
  - ANOS-REQ-016
  - ANOS-REQ-020
  - ANOS-REQ-021
  - ANOS-REQ-022
  - ANOS-REQ-023
  - ANOS-REQ-024
sourceMaterialRefs:
  - task-results/tr-kt-ai-native-os-impl-requirement-prd-domain.md
  - projects/company-knowledge-core/technical-solutions/ai-native-os-requirement-prd-domain.md
expectedOutput:
  - Test Agent runs focused Requirement/PRD/Decision regression tests.
  - Test Agent checks TaskResult evidence, requirementRefs, operating rules, and open risks.
  - If any test fails, Test Agent writes a failing TaskResult with reproducible evidence and PM creates a development repair task.
updatedAt: "2026-06-21T08:12:51Z"
assignedRunner: runner.meimei-mac-local-test-1
leaseOwner: runner.meimei-mac-local-test-1
leaseTokenHash: dde58826e75c8ec49ce60601195cd57760548e8f3e9fc4302468539f0ee0e1fb
leaseProofHash: dde58826e75c8ec49ce60601195cd57760548e8f3e9fc4302468539f0ee0e1fb
leaseIssuedAt: "2026-06-21T07:45:04Z"
leaseExpiresAt: "2026-06-21T08:15:04Z"
leaseHeartbeatAt: "2026-06-21T07:45:04Z"
heartbeatAt: "2026-06-21T07:45:04Z"
leaseVersion: 3
leaseAttempt: 2
taskVersion: 3
notificationRefs:
  - notifications/notification.20260621T071855551374Z.md
  - notifications/notification.20260621T074504822565Z.md
  - notifications/notification.20260621T074549494767Z.md
  - notifications/notification.20260621T074549495675Z.md
  - notifications/notification.20260621T074549496333Z.md
  - notifications/notification.20260621T081251736527Z.md
resultRef: task-results/tr-kt-ai-native-os-test-requirement-prd-domain.md
completedAt: "2026-06-21T07:45:49Z"
---

# Test Scope

Validate the completed implementation without modifying product code.

# Required Checks

- Run the focused Requirement/PRD/Decision CLI regression test.
- Run the broader CLI regression suite when feasible.
- Confirm every requirementRef in this task is covered by test evidence or explicit risk.
- Confirm failure handling routes back to Development Agent, not PM self-repair.
