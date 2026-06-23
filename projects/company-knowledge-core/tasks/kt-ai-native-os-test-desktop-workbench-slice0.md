---
type: ProjectTask
title: AI Native OS test - desktop workbench Slice 0
description: Validate Desktop Workbench Slice 0 static proof, shared frontend boundary, native bridge manifest, and cross-platform gate checklist.
timestamp: "2026-06-21T07:18:00Z"
taskId: kt-ai-native-os-test-desktop-workbench-slice0
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"engineering","stage":"test","requiredCapabilities":["testing","desktop","cross_platform","quality_gate"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-ai-native-os-impl-desktop-workbench-slice0.md","task-results/tr-kt-ai-native-os-impl-desktop-workbench-slice0.md","projects/company-knowledge-core/technical-solutions/ai-native-os-desktop-workbench-console.md","projects/company-knowledge-core/product-reviews/ai-native-os-desktop-workbench-revision-review.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_and_product_review","reviewPath":"test_then_pm_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - testing
  - desktop
  - cross_platform
  - quality_gate
requiredAgents:
  - agent.company.test
executorAgent: agent.company.test
status: done
priority: critical
currentStage: test
requirementRefs:
  - ANOS-REQ-001
  - ANOS-REQ-002
  - ANOS-REQ-003
  - ANOS-REQ-004
  - ANOS-REQ-005
  - ANOS-REQ-006
  - ANOS-REQ-030
  - ANOS-REQ-031
  - ANOS-REQ-032
  - ANOS-REQ-033
  - ANOS-REQ-034
  - ANOS-REQ-040
  - ANOS-REQ-041
  - ANOS-REQ-042
  - ANOS-REQ-043
  - ANOS-REQ-044
  - ANOS-REQ-045
sourceMaterialRefs:
  - task-results/tr-kt-ai-native-os-impl-desktop-workbench-slice0.md
  - projects/company-knowledge-core/technical-solutions/ai-native-os-desktop-workbench-console.md
  - projects/company-knowledge-core/product-reviews/ai-native-os-desktop-workbench-revision-review.md
expectedOutput:
  - Test Agent validates Slice 0 artifacts and static proof checks.
  - Test Agent separates proven Slice 0 scope from blocked full Desktop runtime scope.
  - Any failure must be returned to Development Agent through a repair task.
updatedAt: "2026-06-21T08:12:52Z"
notificationRefs:
  - notifications/notification.20260621T071805378818Z.md
  - notifications/notification.20260621T071838529374Z.md
  - notifications/notification.20260621T074504829568Z.md
  - notifications/notification.20260621T074517752474Z.md
  - notifications/notification.20260621T074552661710Z.md
  - notifications/notification.20260621T074552662506Z.md
  - notifications/notification.20260621T074552663287Z.md
  - notifications/notification.20260621T081252058682Z.md
assignedRunner: runner.meimei-mac-local-test-4
leaseOwner: runner.meimei-mac-local-test-4
leaseTokenHash: ed275dd9c63aa749bc62b1c39b325db7a0b97925f9beff594e716a927c6919c2
leaseProofHash: ed275dd9c63aa749bc62b1c39b325db7a0b97925f9beff594e716a927c6919c2
leaseIssuedAt: "2026-06-21T07:45:17Z"
leaseExpiresAt: "2026-06-21T08:15:17Z"
leaseHeartbeatAt: "2026-06-21T07:45:17Z"
heartbeatAt: "2026-06-21T07:45:17Z"
leaseVersion: 3
leaseAttempt: 2
taskVersion: 3
resultRef: task-results/tr-kt-ai-native-os-test-desktop-workbench-slice0.md
completedAt: "2026-06-21T07:45:52Z"
---

# Test Scope

Validate the accepted Slice 0 only. Do not treat full Desktop Workbench runtime as accepted until OS matrix, signing certificates, Windows runner, and release-owner inputs exist.

# Required Checks

- Run `scripts/validate_desktop_workbench_slice0.py`.
- Run `tests.test_desktop_workbench_slice0`.
- Confirm the native bridge manifest covers Mac/Windows assumptions without hardcoding one shell.
- Confirm blocked full-runtime gates are explicit in TaskResult open risks.
