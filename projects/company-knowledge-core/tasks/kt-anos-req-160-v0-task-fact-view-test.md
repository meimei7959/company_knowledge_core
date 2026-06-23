---
type: ProjectTask
title: ANOS-REQ-160 V0 只读任务事实视图测试验收
description: ProjectTask assigned to agent.company.test.
timestamp: "2026-06-23T08:02:54Z"
taskId: kt-anos-req-160-v0-task-fact-view-test
taskType: test_validation
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test_validation","category":"project","stage":"test","requiredCapabilities":["test_validation","acceptance_matrix","security_regression"],"requiredTools":[],"sourceRefs":["docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md","projects/company-knowledge-core/tasks/kt-anos-req-160-v0-task-fact-view-development.md"],"repositoryRefs":[],"dataScopes":["ProjectTask","TaskResult","AgentRun","ReviewRecord","NotificationRecord","AuditLog","SourceMaterial"],"qualityGate":"project","acceptancePath":"product_review","reviewPath":"product_review","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.test
status: pending
priority: high
workSourceType: feature
requirementRefs:
  - ANOS-REQ-160
requirementObjectRefs:
  - docs/product/ai-native-os/task-execution-productization-prd.md
acceptanceCriteriaRefs:
  - docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md
sourceMaterialRefs:
  - docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md
  - projects/company-knowledge-core/technical-solutions/anos-req-160-v0-task-fact-view-technical-solution.md
  - projects/company-knowledge-core/tasks/kt-anos-req-160-v0-task-fact-view-development.md
expectedOutput:
  - 将 22 条验收矩阵转成测试执行结果。
  - P0 必须覆盖 done 缺 result/evidence、waiting_runner 缺原因、waiting_acceptance 缺 owner/resultRef、旧任务 legacy gap、敏感信息脱敏、不新增核心对象、不重写执行链路。
  - 输出测试报告和 TaskResult；失败项必须回派 Development Agent。
resultRef: ""
notificationRefs:
  - notifications/notification.20260623T080254Z-anos-req-160-test-task.md
auditRefs:
  - knowledge/audit/audit.20260623T080254Z-anos-req-160-dev-test-tasks-created.md
operatingRuleRefs:
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
assignedRunner: ""
executorAgent: agent.company.test
leaseOwner: ""
leaseTokenHash: ""
leaseProofHash: ""
leaseIssuedAt: ""
leaseExpiresAt: ""
leaseHeartbeatAt: ""
leaseVersion: 1
leaseAttempt: 0
heartbeatAt: ""
taskVersion: 1
handoffContract: {"from":"agent.company.project-manager","to":"agent.company.test","requiredArtifacts":["test report","acceptance matrix result","TaskResult"],"artifactRefs":["docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md"],"summary":"Validate ANOS-REQ-160 V0 after Development TaskResult is available."}
qualityGateRequired: true
attemptNumber: 1
maxAttempts: 3
followupTaskRefs: []
guideUpdateRequired: false
guideUpdated: false
updatedAt: "2026-06-23T08:02:54Z"
dependsOn:
  - projects/company-knowledge-core/tasks/kt-anos-req-160-v0-task-fact-view-development.md
---

# Test Task

Validate ANOS-REQ-160 V0 against the acceptance matrix after Development Agent writes its TaskResult.
