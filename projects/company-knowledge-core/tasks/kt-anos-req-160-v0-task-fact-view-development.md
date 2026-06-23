---
type: ProjectTask
title: ANOS-REQ-160 V0 只读任务事实视图研发实现
description: ProjectTask assigned to agent.company.development.
timestamp: "2026-06-23T08:02:54Z"
taskId: kt-anos-req-160-v0-task-fact-view-development
taskType: implementation
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"implementation","category":"project","stage":"development","requiredCapabilities":["implementation","cli_api","frontend_development","security_redaction"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/technical-solutions/anos-req-160-v0-task-fact-view-technical-solution.md","projects/company-knowledge-core/product-reviews/anos-req-160-v0-task-fact-view-architecture-product-review.md","docs/product/ai-native-os/task-execution-productization-prd.md","docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md"],"repositoryRefs":[],"dataScopes":["ProjectTask","AgentRunner","TaskResult","AgentRun","ReviewRecord","NotificationRecord","AuditLog","SourceMaterial"],"qualityGate":"project","acceptancePath":"test_then_product_review","reviewPath":"test_review","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.development
status: waiting_acceptance
priority: high
workSourceType: feature
requirementRefs:
  - ANOS-REQ-160
requirementObjectRefs:
  - docs/product/ai-native-os/task-execution-productization-prd.md
acceptanceCriteriaRefs:
  - docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md
sourceMaterialRefs:
  - projects/company-knowledge-core/technical-solutions/anos-req-160-v0-task-fact-view-technical-solution.md
  - projects/company-knowledge-core/product-reviews/anos-req-160-v0-task-fact-view-architecture-product-review.md
  - docs/product/ai-native-os/task-execution-productization-prd.md
  - docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md
expectedOutput:
  - 实现 V0 只读任务事实视图 projection / serializer。
  - 提供 CLI/API/Workbench 至少一个可验收只读入口，优先按技术方案实现。
  - 覆盖状态解释、缺口分类、证据/验收/审计展示、旧任务兼容和敏感信息脱敏。
  - 不新增核心对象，不改执行链路，不增加写操作。
  - 返回 TaskResult，列出变更文件、测试证据、未覆盖项和后续测试入口。
resultRef: task-results/tr-kt-anos-req-160-v0-task-fact-view-development.md
notificationRefs:
  - notifications/notification.20260623T080254Z-anos-req-160-development-task.md
  - notifications/notification.20260623T081453773859Z.md
  - notifications/notification.20260623T081453774922Z.md
  - notifications/notification.20260623T081453775756Z.md
  - notifications/notification.20260623T081759743801Z.md
  - notifications/notification.20260623T081759745075Z.md
  - notifications/notification.20260623T081759745840Z.md
auditRefs:
  - knowledge/audit/audit.20260623T080254Z-anos-req-160-dev-test-tasks-created.md
operatingRuleRefs:
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
assignedRunner: ""
executorAgent: agent.company.development
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
handoffContract: {"from":"agent.company.project-manager","to":"agent.company.development","requiredArtifacts":["implementation summary","changed files","test evidence","TaskResult"],"artifactRefs":["projects/company-knowledge-core/technical-solutions/anos-req-160-v0-task-fact-view-technical-solution.md","projects/company-knowledge-core/product-reviews/anos-req-160-v0-task-fact-view-architecture-product-review.md"],"summary":"Implement ANOS-REQ-160 V0 read-only task fact view only; do not add core objects or rewrite execution chain."}
qualityGateRequired: true
attemptNumber: 1
maxAttempts: 3
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-anos-req-160-v0-task-fact-view-test.md
guideUpdateRequired: false
guideUpdated: false
updatedAt: "2026-06-23T08:17:59Z"
completedAt: "2026-06-23T08:17:59Z"
---

# Development Task

Implement ANOS-REQ-160 V0 only.

## Hard Stop

Do not implement PM Health V1, task actions, status machine changes, Runner lease writes, or TaskResult write-chain changes.
