---
type: ProjectTask
title: 阶段二：同事接入工作台 UI 与交互设计返工
description: ProjectTask assigned to agent.company.design.
timestamp: "2026-06-22T12:18:14Z"
taskId: kt-v2-colleague-runner-ui-interaction-design-revision
taskType: design_spec
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"design_spec","category":"design","stage":"","requiredCapabilities":["design_spec"],"requiredTools":[],"sourceRefs":["用户指出设计 Agent 应主责 UI 设计和交互设计，不能只提供信息架构"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"design_spec","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.design
status: waiting_acceptance
priority: high
dueAt: ""
sourceMaterialRefs:
  - 用户指出设计 Agent 应主责 UI 设计和交互设计，不能只提供信息架构
expectedOutput:
  - 输出阶段二工作台 UI/交互设计补充：页面布局、主次信息、组件清单、按钮/弹窗/抽屉、配对授权交互、任务路由状态、错误和权限状态、窄屏布局、视觉规范、开发标注和测试检查项
resultRef: task-results/tr-kt-v2-colleague-runner-ui-interaction-design-revision.md
notificationRefs:
  - notifications/notification.20260622T121814068779Z.md
auditRefs:
  - knowledge/audit/audit.20260622T122017Z-phase2-colleague-runner-ui-interaction-design-revision.md
operatingRuleRefs:
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator-orchestrator.md
assignedRunner: ""
executorAgent: agent.company.design
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
handoffContract: {"from":"agent.company.design","to":"agent.company.architecture","requiredArtifacts":["flow/state spec","interaction rules","edge states","implementation notes"]}
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
updatedAt: "2026-06-22T12:20:17Z"
---

## Request

阶段二：同事接入工作台 UI 与交互设计返工

## Source Materials

- 用户指出设计 Agent 应主责 UI 设计和交互设计，不能只提供信息架构

## Expected Output

- 输出阶段二工作台 UI/交互设计补充：页面布局、主次信息、组件清单、按钮/弹窗/抽屉、配对授权交互、任务路由状态、错误和权限状态、窄屏布局、视觉规范、开发标注和测试检查项

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: agent.company.design
- to: agent.company.architecture
- requiredArtifacts:
  - flow/state spec
  - interaction rules
  - edge states
  - implementation notes

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.

## Phase 2 Workflow Gate

- Must follow `projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator-orchestrator.md` before execution.
- Design Agent must produce UI design and interaction design. Information architecture is only supporting material.
- Main workbench UI must be user-readable Chinese and hide internal fields from primary content.
