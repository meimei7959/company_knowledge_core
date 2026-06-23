---
type: ProjectTask
title: 阶段二：同事电脑接入同一项目中枢产品需求包
description: ProjectTask assigned to agent.company.product-manager.
timestamp: "2026-06-22T11:54:28Z"
taskId: kt-v2-colleague-runner-product-requirements
taskType: product_requirements
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"product_requirements","category":"project","stage":"","requiredCapabilities":["product_requirements"],"requiredTools":[],"sourceRefs":["用户要求阶段二按产品经理整理需求后进入架构/研发/测试闭环"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.product-manager
status: waiting_acceptance
priority: high
dueAt: ""
sourceMaterialRefs:
  - 用户要求阶段二按产品经理整理需求后进入架构/研发/测试闭环
expectedOutput:
  - 输出中文产品需求包：业务目标、用户角色、用户场景、功能需求、非功能需求、边界、验收标准、交付架构师输入
resultRef: task-results/tr-kt-v2-colleague-runner-product-requirements.md
notificationRefs:
  - notifications/notification.20260622T115428943810Z.md
  - notifications/notification.20260622T120336309987Z.md
  - notifications/notification.20260622T120336311401Z.md
  - notifications/notification.20260622T120336312845Z.md
auditRefs: []
operatingRuleRefs:
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator-orchestrator.md
assignedRunner: ""
executorAgent: agent.company.product-manager
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
handoffContract: {"from":"","to":"","requiredArtifacts":["summary","evidence refs","next action or terminal reason"]}
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
updatedAt: "2026-06-22T12:03:36Z"
completedAt: "2026-06-22T12:03:36Z"
---

## Request

阶段二：同事电脑接入同一项目中枢产品需求包

## Source Materials

- 用户要求阶段二按产品经理整理需求后进入架构/研发/测试闭环

## Expected Output

- 输出中文产品需求包：业务目标、用户角色、用户场景、功能需求、非功能需求、边界、验收标准、交付架构师输入

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: current assignee
- to: terminal or project manager decision
- requiredArtifacts:
  - summary
  - evidence refs
  - next action or terminal reason

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.

## Phase 2 Workflow Gate

- Must follow `projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator-orchestrator.md` before execution.
- Must preserve role boundary: Product, Design, Architecture, Development, Test, and PM conclusions are separate artifacts.
- Main workbench UI must be user-readable Chinese and hide internal fields from primary content.
