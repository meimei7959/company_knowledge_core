---
type: ProjectTask
title: ANOS-REQ-160 V0 只读任务事实视图技术方案
description: ProjectTask assigned to agent.company.architecture.
timestamp: "2026-06-23T07:55:12Z"
taskId: kt-anos-req-160-v0-task-fact-view-architecture
taskType: technical_solution
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"technical_solution","category":"project","stage":"architecture_handoff","requiredCapabilities":["technical_solution","architecture_review","requirement_traceability"],"requiredTools":[],"sourceRefs":["docs/product/ai-native-os/task-execution-productization-prd.md","docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md","task-results/tr-anos-req-160-pm-requirement-detail.md"],"repositoryRefs":[],"dataScopes":["ProjectTask","AgentRunner","TaskResult","AgentRun","ReviewRecord","NotificationRecord","AuditLog","SourceMaterial"],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.architecture
status: waiting_acceptance
priority: high
dueAt: ""
workSourceType: feature
requirementRefs:
  - ANOS-REQ-160
requirementObjectRefs:
  - docs/product/ai-native-os/task-execution-productization-prd.md
acceptanceCriteriaRefs:
  - docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md
receiverReviewRefs:
  - projects/company-knowledge-core/receiver-reviews/receiver-review.anos-req-160.architecture.md
sourceMaterialRefs:
  - docs/product/ai-native-os/task-execution-productization-prd.md
  - docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md
  - task-results/tr-anos-req-160-pm-requirement-detail.md
  - docs/protocols/agent-workbench-integration-brief.md
  - docs/strategy/zhenzhi-ai-native-knowledge-system.md
expectedOutput:
  - 先由 Architecture Agent 记录 ReceiverReview，decision 必须是 accepted_for_work 或 accepted_with_assumptions 后再产出技术方案。
  - 输出 ANOS-REQ-160 V0 只读任务事实视图技术方案。
  - 明确事实视图从现有对象取数字段映射，不新增核心对象。
  - 明确 API/UI/CLI 或读模型承载方式，以及权限和敏感信息脱敏策略。
  - 明确不改写 Scheduler、Agent Ring、Runner claim/lease/heartbeat/finish、TaskResult 写回和验收执行链路。
  - 明确 V0 实现任务拆分建议、风险、回滚方式和测试 Agent 验收输入。
resultRef: task-results/tr-kt-anos-req-160-v0-task-fact-view-architecture.md
notificationRefs:
  - notifications/notification.20260623T075512Z-anos-req-160-architecture-task.md
auditRefs:
  - knowledge/audit/audit.20260623T075512Z-anos-req-160-architecture-task-created.md
  - knowledge/audit/audit.20260623T080106Z-anos-req-160-architecture.md
operatingRuleRefs:
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
  - docs/agent-team/role-operating-specs.json
assignedRunner: ""
executorAgent: agent.company.architecture
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
handoffContract: {"from":"agent.company.project-manager","to":"agent.company.architecture","requiredArtifacts":["technical solution","field mapping","scope boundary proof","risk and test handoff"],"artifactRefs":["docs/product/ai-native-os/task-execution-productization-prd.md","docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md","task-results/tr-anos-req-160-pm-requirement-detail.md"],"summary":"请基于 ANOS-REQ-160 V0 PRD 输出只读任务事实视图技术方案；禁止新增核心对象或重写执行链路。"}
qualityGateRequired: true
attemptNumber: 1
maxAttempts: 3
followupTaskRefs: []
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-23T08:01:06Z"
completedAt: "2026-06-23T08:01:06Z"
---

# ANOS-REQ-160 V0 只读任务事实视图技术方案任务

## Request

基于 Product Manager Agent 已完成的 ANOS-REQ-160 V0 PRD 和验收矩阵，输出架构技术方案。

## Source Materials

- `docs/product/ai-native-os/task-execution-productization-prd.md`
- `docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md`
- `task-results/tr-anos-req-160-pm-requirement-detail.md`
- `docs/protocols/agent-workbench-integration-brief.md`
- `docs/strategy/zhenzhi-ai-native-knowledge-system.md`

## Must Answer

1. 单任务事实视图从哪些现有对象和字段取数。
2. 读模型/API/UI/CLI 如何承载，且为什么不构成新核心对象。
3. `done` 缺证据、`waiting_runner` 缺原因、`waiting_acceptance` 缺 owner、旧任务 legacy gap 如何展示。
4. 权限不足和敏感信息如何脱敏。
5. 哪些代码边界允许改，哪些执行链路必须保持不动。
6. 研发任务如何拆，测试 Agent 如何按验收矩阵验证。

## ReceiverReview Gate

Architecture Agent 开工前必须记录 ReceiverReview，确认已接收以下输入：

- PRD 范围是 V0 只读任务事实视图。
- 验收矩阵可测试。
- 不新增核心对象、不重写执行链路是硬边界。
- 若输入不足，必须 decision=`needs_rework` 并列出缺口，不能直接写技术方案。

## Hard Boundary

不得新增核心对象，不得新增执行状态机，不得重写 Scheduler、Agent Ring、Runner claim/lease/heartbeat/finish、TaskResult 写回或验收执行链路。

## Done Means

架构方案可直接交 Product Manager Agent 复核；通过后再由 Project Manager Agent 创建研发和测试任务。
