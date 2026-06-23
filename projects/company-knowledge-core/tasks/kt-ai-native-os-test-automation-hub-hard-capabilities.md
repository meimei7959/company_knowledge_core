---
type: ProjectTask
title: AI Native OS test - automation hub hard capabilities
description: Test the four automation hub hard capabilities after Development Agent implementation.
timestamp: "2026-06-21T08:25:00Z"
taskId: kt-ai-native-os-test-automation-hub-hard-capabilities
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"engineering","stage":"test","requiredCapabilities":["testing","scheduler","agent_worker","approval_relay","environment_readiness","workbench"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-ai-native-os-dev-automation-hub-hard-capabilities.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"test_then_pm_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - testing
  - scheduler
  - agent_worker
  - approval_relay
  - environment_readiness
  - workbench
requiredAgents:
  - agent.company.test
executorAgent: agent.company.test
status: done
priority: critical
currentStage: test
blockedByTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-dev-automation-hub-hard-capabilities.md
requirementRefs:
  - ANOS-REQ-050
  - ANOS-REQ-051
  - ANOS-REQ-052
  - ANOS-REQ-053
  - ANOS-REQ-054
  - ANOS-REQ-055
  - ANOS-REQ-056
  - ANOS-REQ-070
  - ANOS-REQ-071
  - ANOS-REQ-072
  - ANOS-REQ-073
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-dev-automation-hub-hard-capabilities.md
expectedOutput:
  - Test Agent independently verifies execution context transfer, exception recovery, supervision workbench, and environment readiness.
  - Test Agent runs focused tests, full unittest discovery, and full repository validate.
  - If tests fail, Test Agent writes a failing TaskResult and PM creates a development repair task instead of fixing in PM thread.
updatedAt: "2026-06-21T08:47:37Z"
assignedRunner: runner.meimei-mac-local-test-hub
leaseOwner: runner.meimei-mac-local-test-hub
leaseTokenHash: 8bb2381ffb1a425896ae5a289525543870923f92e6e92a8b79e4131210253640
leaseProofHash: 8bb2381ffb1a425896ae5a289525543870923f92e6e92a8b79e4131210253640
leaseIssuedAt: "2026-06-21T08:38:09Z"
leaseExpiresAt: "2026-06-21T09:38:09Z"
leaseHeartbeatAt: "2026-06-21T08:38:09Z"
heartbeatAt: "2026-06-21T08:38:09Z"
leaseVersion: 3
leaseAttempt: 2
taskVersion: 3
notificationRefs:
  - notifications/notification.20260621T083759907378Z.md
  - notifications/notification.20260621T083809094779Z.md
  - notifications/notification.20260621T084502791927Z.md
  - notifications/notification.20260621T084502792719Z.md
  - notifications/notification.20260621T084502793338Z.md
  - notifications/notification.20260621T084737642247Z.md
resultRef: task-results/tr-kt-ai-native-os-test-automation-hub-hard-capabilities.md
completedAt: "2026-06-21T08:45:02Z"
---

# Test Rules

- Do not modify implementation files.
- Do not repair failures directly.
- Return approval requests to PM/main window.
- If token/context limits or temporary waits happen, checkpoint and continue after recovery.
