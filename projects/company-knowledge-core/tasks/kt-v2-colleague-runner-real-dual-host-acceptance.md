---
type: ProjectTask
title: 阶段二：真实同事电脑双 host 验收
description: ProjectTask assigned to agent.company.test.
timestamp: "2026-06-22T13:50:14Z"
taskId: kt-v2-colleague-runner-real-dual-host-acceptance
taskType: test_validation
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test_validation","category":"project","stage":"","requiredCapabilities":["test_validation"],"requiredTools":[],"sourceRefs":["产品最终验收 blocked：本机 simulate-phase2 不能替代真实同事电脑/真实双 host 验收"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.test
status: pending
priority: high
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/test-reports/phase2-colleague-runner-regression-visible-path-report.md
  - task-results/tr-kt-v2-colleague-runner-product-final-acceptance.md
  - projects/company-knowledge-core/reviews/phase2-colleague-runner-product-final-acceptance.md
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator.md
  - 产品最终验收 blocked：本机 simulate-phase2 不能替代真实同事电脑/真实双 host 验收
expectedOutput:
  - 在真实同事电脑或真实第二 host 接入同一项目中枢后，验证设备注册、Runner 注册、配对授权、任务路由、租约心跳、TaskResult/AgentRun 写回、工作台可视化和异常恢复；写回真实双 host TaskResult 供产品复验
resultRef: ""
notificationRefs:
  - notifications/notification.20260622T135014830150Z.md
auditRefs: []
operatingRuleRefs:
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator.md
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
updatedAt: "2026-06-22T13:50:14Z"
---

## Request

阶段二：真实同事电脑双 host 验收

## Source Materials

- 产品最终验收 blocked：本机 simulate-phase2 不能替代真实同事电脑/真实双 host 验收

## Expected Output

- 在真实同事电脑或真实第二 host 接入同一项目中枢后，验证设备注册、Runner 注册、配对授权、任务路由、租约心跳、TaskResult/AgentRun 写回、工作台可视化和异常恢复；写回真实双 host TaskResult 供产品复验

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

## Real Dual Host Gate

- This task is blocked until a real colleague computer or real second host is available and authorized.
- Simulated two-host evidence may be referenced as readiness evidence, but cannot close this task.
- Test Agent must produce real dual-host TaskResult before Product Manager Agent can re-run final acceptance.
