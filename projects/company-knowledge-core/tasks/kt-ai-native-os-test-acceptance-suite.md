---
type: ProjectTask
title: AI Native OS test and acceptance suite
description: Convert AI Native OS test cases and acceptance checklist into executable E2E, negative, regression, and release-gate validation.
timestamp: "2026-06-21T05:13:34Z"
taskId: kt-ai-native-os-test-acceptance-suite
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"project","stage":"","requiredCapabilities":["test","test_planning","e2e_testing","regression_gate","acceptance_traceability"],"requiredTools":[],"sourceRefs":["docs/product/ai-native-os/test-cases.md","docs/product/ai-native-os/acceptance-checklist.md","docs/product/ai-native-os/requirements.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - test_planning
  - e2e_testing
  - regression_gate
  - acceptance_traceability
requiredAgents:
  - agent.company.test
executorAgent: agent.company.test
status: waiting_runner
priority: high
sourceMaterialRefs:
  - docs/product/ai-native-os/test-cases.md
  - docs/product/ai-native-os/acceptance-checklist.md
  - docs/product/ai-native-os/requirements.md
requirementRefs:
  - ANOS-REQ-001
  - ANOS-REQ-002
  - ANOS-REQ-003
  - ANOS-REQ-004
  - ANOS-REQ-005
  - ANOS-REQ-006
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
  - ANOS-REQ-050
  - ANOS-REQ-051
  - ANOS-REQ-052
  - ANOS-REQ-053
  - ANOS-REQ-054
  - ANOS-REQ-055
  - ANOS-REQ-056
  - ANOS-REQ-060
  - ANOS-REQ-061
  - ANOS-REQ-062
  - ANOS-REQ-063
  - ANOS-REQ-070
  - ANOS-REQ-071
  - ANOS-REQ-072
  - ANOS-REQ-073
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
expectedOutput:
  - ANOS-REQ to test case to acceptance gate traceability.
  - E2E, negative, regression, and EvalRun release gate plan or implementation.
  - Launch blocker report.
updatedAt: "2026-06-21T07:18:05Z"
notificationRefs:
  - notifications/notification.20260621T052918734015Z.md
  - notifications/notification.20260621T053349643776Z.md
  - notifications/notification.20260621T053430457973Z.md
  - notifications/notification.20260621T055524574688Z.md
  - notifications/notification.20260621T055554616722Z.md
  - notifications/notification.20260621T055613429489Z.md
  - notifications/notification.20260621T061855453857Z.md
  - notifications/notification.20260621T062940760743Z.md
assignedRunner: runner.meimei-mac-local-codex
---

## Acceptance

- AC-TEST-001 through AC-TEST-005 are measurable.
- Failed permission, evidence, stale lease, criteria, tool, notification, and EvalRun cases block release.
