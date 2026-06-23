---
type: ProjectTask
title: 阶段二多设备 Runner 协作闭环架构方案
description: 架构师基于产品需求包输出同事电脑接入同一项目中枢、多设备 Runner 协作闭环技术方案。
timestamp: "2026-06-22T11:54:41Z"
taskId: kt-phase-2-multi-device-runner-architecture-handoff
taskType: technical_solution
projectId: company-knowledge-core
requester: agent.company.product-manager
assignee: agent.company.architecture
currentStage: technical_solution
status: pending
priority: high
requiredCapabilities:
  - architecture
  - scheduler_design
  - runner_integration
  - security_boundary_design
requiredAgents:
  - agent.company.architecture
sourceMaterialRefs:
  - docs/product/ai-native-os/phase-2-multi-device-runner-collaboration-prd.md
  - docs/product/ai-native-os/requirement-tree.md
  - docs/product/ai-native-os/requirements.md
  - docs/product/ai-native-os/test-cases.md
  - docs/scheduler/task-dispatch-model.md
  - docs/harness/agent-ring-distributed-runner-proof-harness.md
expectedOutput:
  - 阶段二多设备 Runner 架构方案
  - Runner 身份、授权、租约、心跳、上下文拉取、结果写回模型
  - 失败恢复状态机
  - 双 Runner 验收 harness 方案
  - 开发任务拆分建议
acceptanceCriteria:
  - 覆盖 P2-RUN-001 到 P2-RUN-010。
  - 覆盖 P2-AC-001 到 P2-AC-010。
  - 明确 V1 单机闭环保留路径。
  - 明确 Core 与外部 Agent Ring 的边界。
  - 明确安全、审计、通知、TaskResult、AgentRun 写回。
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"technical_solution","category":"project","stage":"technical_solution","requiredCapabilities":["architecture","scheduler_design","runner_integration","security_boundary_design"],"requiredTools":[],"sourceRefs":["docs/product/ai-native-os/phase-2-multi-device-runner-collaboration-prd.md","docs/product/ai-native-os/requirement-tree.md","docs/product/ai-native-os/requirements.md","docs/product/ai-native-os/test-cases.md","docs/scheduler/task-dispatch-model.md","docs/harness/agent-ring-distributed-runner-proof-harness.md"],"repositoryRefs":["/Users/meimei/Documents/company_knowledge_core"],"dataScopes":["company-knowledge-core"],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
handoffContract: {"fromAgent":"agent.company.product-manager","handoffTo":"agent.company.architecture","handoffSummary":"产品需求包已准备好，请输出阶段二多设备 Runner 协作闭环技术方案。","requiredArtifacts":["architecture solution","state machine","security boundary","harness plan","implementation task split"],"artifactRefs":["docs/product/ai-native-os/phase-2-multi-device-runner-collaboration-prd.md"],"openRisks":["Agent Ring 仍是外部执行层，需要保持契约边界。","阶段二必须保留 V1 单机闭环，不应重写已验收基础。"],"nextSuggestedTask":"Architecture Agent produce phase-2 technical solution.","terminalReason":""}
updatedAt: "2026-06-22T11:54:41Z"
---

## Request

请基于产品需求包输出阶段二技术方案：同事电脑接入同一项目中枢，多设备 Runner 共同领取、执行、写回任务，并保持权限、审计、通知、验收和 V1 单机闭环兼容。

## Architecture Inputs

- 产品包：[docs/product/ai-native-os/phase-2-multi-device-runner-collaboration-prd.md](../../../docs/product/ai-native-os/phase-2-multi-device-runner-collaboration-prd.md)
- 现有 Runner 功能需求：ANOS-REQ-060 到 ANOS-REQ-063。
- 现有调度需求：ANOS-REQ-050 到 ANOS-REQ-056。
- 现有测试线索：TC-RUN-001 到 TC-RUN-004、TC-SCH-001 到 TC-SCH-007、TC-E2E-004。

## Must Answer

1. Runner 如何注册、授权、心跳、暂停、禁用。
2. 调度器如何匹配、发租约、续租、释放、处理 stale lease。
3. 同事电脑如何拉取被裁剪的上下文包。
4. 本地执行如何写回 TaskResult、AgentRun、NotificationRecord、AuditLog。
5. 越权、离线、工具缺失、写回失败如何恢复。
6. 工作台/中枢 read model 需要哪些状态字段。
7. 最小双 Runner harness 如何验收。

## Done Means

架构方案能直接交给 Project Manager 拆分研发、测试、运维任务；不能只停留在概念图。

## Phase 2 Workflow Gate

- Must follow `projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator-orchestrator.md` before execution.
- Must preserve role boundary: Product, Design, Architecture, Development, Test, and PM conclusions are separate artifacts.
- Main workbench UI must be user-readable Chinese and hide internal fields from primary content.
