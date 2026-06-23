---
type: ProjectTask
title: AI Native OS RT PM - coverage matrix
description: Produce the BR -> UREQ -> ProductRequirement -> ANOS -> existing task/result -> test -> acceptance coverage matrix before any Requirement Tree implementation is released.
timestamp: "2026-06-21T09:08:00Z"
taskId: kt-ai-native-os-rt-pm-coverage-matrix
taskType: project_management
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"project_management","category":"planning","stage":"coverage_matrix","requiredCapabilities":["project_management","requirement_traceability"],"requiredTools":[],"sourceRefs":["docs/product/ai-native-os/requirement-tree.md","docs/product/ai-native-os/requirements.md","docs/product/ai-native-os/test-cases.md","docs/product/ai-native-os/acceptance-checklist.md","projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-resplit-plan.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"pm_review","acceptancePath":"pm_review","reviewPath":"pm_self_review","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - project_management
  - requirement_traceability
requiredAgents:
  - agent.company.project-manager
executorAgent: agent.company.project-manager
status: done
priority: critical
currentStage: coverage_matrix
sourceMaterialRefs:
  - docs/product/ai-native-os/requirement-tree.md
  - docs/product/ai-native-os/requirements.md
  - docs/product/ai-native-os/test-cases.md
  - docs/product/ai-native-os/acceptance-checklist.md
expectedOutput:
  - Coverage matrix for 5 BR, 15 UREQ, product requirements, 74 ANOS functional requirements, existing task results, tests, and launch gates.
  - Classification of each row as complete, partial, uncovered, or blocked.
  - Explicit Desktop Slice 0 partial status where full desktop runtime is not proven.
assignedRunner: runner.meimei-mac-local-pm-rt
leaseOwner: runner.meimei-mac-local-pm-rt
leaseTokenHash: 037529aa97f894e566ac94c8d0f92a8cbee5a54470894675103c079bce978386
leaseProofHash: 037529aa97f894e566ac94c8d0f92a8cbee5a54470894675103c079bce978386
leaseIssuedAt: "2026-06-21T09:37:32Z"
leaseExpiresAt: "2026-06-21T10:37:32Z"
leaseHeartbeatAt: "2026-06-21T09:37:32Z"
heartbeatAt: "2026-06-21T09:37:32Z"
leaseVersion: 2
leaseAttempt: 1
taskVersion: 2
updatedAt: "2026-06-21T09:43:53Z"
notificationRefs:
  - notifications/notification.20260621T093732700557Z.md
  - notifications/notification.20260621T094301813774Z.md
  - notifications/notification.20260621T094301814631Z.md
  - notifications/notification.20260621T094301815619Z.md
  - notifications/notification.20260621T094353702959Z.md
resultRef: task-results/tr-kt-ai-native-os-rt-pm-coverage-matrix.md
completedAt: "2026-06-21T09:43:01Z"
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-rt-pm-coverage-matrix-handoff.md
---

# PM Scope

This task prevents Development Agent from implementing against an incomplete traceability baseline.
