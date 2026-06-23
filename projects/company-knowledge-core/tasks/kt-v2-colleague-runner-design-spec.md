---
type: ProjectTask
title: 阶段二：同事接入工作台页面设计规范
description: ProjectTask assigned to agent.company.design.
timestamp: "2026-06-22T11:54:29Z"
taskId: kt-v2-colleague-runner-design-spec
taskType: design_spec
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"design_spec","category":"design","stage":"","requiredCapabilities":["design_spec"],"requiredTools":[],"sourceRefs":["用户要求页面必须加入设计规范，不能太乱"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"design_spec","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.design
status: waiting_acceptance
priority: high
dueAt: ""
sourceMaterialRefs:
  - 用户要求页面必须加入设计规范，不能太乱
expectedOutput:
  - 输出中文工作台页面信息架构、视觉/交互规范、状态/权限/异常表达和研发验收清单
  - 明确工作台是给真实用户看的页面，不是工程调试面板；所有主标题、按钮、状态、提示、证据入口必须中文可理解
  - 明确哪些内部字段不得作为主信息暴露，包括 runtimeMetrics、sessionId、runnerId、deviceId、capability code、raw status、文件路径
resultRef: task-results/tr-kt-v2-colleague-runner-design-spec.md
notificationRefs:
  - notifications/notification.20260622T115429094835Z.md
  - notifications/notification.20260622T120336471264Z.md
  - notifications/notification.20260622T120336472102Z.md
  - notifications/notification.20260622T120336473033Z.md
auditRefs: []
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
updatedAt: "2026-06-22T12:03:36Z"
completedAt: "2026-06-22T12:03:36Z"
---

## Request

阶段二：同事接入工作台页面设计规范

## Source Materials

- 用户要求页面必须加入设计规范，不能太乱

## Expected Output

- 输出中文工作台页面信息架构、视觉/交互规范、状态/权限/异常表达和研发验收清单
- 明确工作台是给真实用户看的页面，不是工程调试面板；所有主标题、按钮、状态、提示、证据入口必须中文可理解
- 明确哪些内部字段不得作为主信息暴露，包括 runtimeMetrics、sessionId、runnerId、deviceId、capability code、raw status、文件路径
- 设计验收清单必须包含“普通用户能否看懂当前状态、下一步操作、阻塞原因、处理人”的逐项检查

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
- Must preserve role boundary: Product, Design, Architecture, Development, Test, and PM conclusions are separate artifacts.
- Main workbench UI must be user-readable Chinese and hide internal fields from primary content.
