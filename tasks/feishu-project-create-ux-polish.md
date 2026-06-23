---
type: ProjectTask
title: 优化飞书项目创建审批后卡片体验
description: ProjectTask assigned to agent.company.development.
timestamp: "2026-06-21T00:00:00Z"
taskId: feishu-project-create-ux-polish
taskType: engineering_action
taskRuntime: {"version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","qualityGate":"engineering","acceptancePath":"pm_review","requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: meimei
assignee: agent.company.development
status: waiting_acceptance
priority: high
dueAt: ""
sourceMaterialRefs:
  - docs/workflows/feishu-intake-lifecycle.md
expectedOutput:
  - Feishu project creation cards use Chinese user-facing status.
  - Manual runner handoff card appears as approval-after initialization handoff, not as confusing early blocker.
  - Internal paths/status codes are removed from primary user-facing cards.
  - Submitter and Owner cards remain useful when the same person receives both.
  - Tests cover project approval and owner onboarding copy.
resultRef: task-results/tr-feishu-project-create-ux-polish.md
notificationRefs:
  - notifications/notification.20260620T170131328366Z.md
  - notifications/notification.20260620T170131329127Z.md
  - notifications/notification.20260620T170131329955Z.md
auditRefs: []
assignedRunner: ""
leaseOwner: ""
leaseProofHash: ""
leaseExpiresAt: ""
heartbeatAt: ""
taskVersion: 1
handoffContract: {"from":"agent.company.project-manager","to":"agent.company.development","requiredArtifacts":["UX issue analysis","code changes","tests","deployment recommendation"]}
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
updatedAt: "2026-06-20T17:01:31Z"
completedAt: "2026-06-20T17:01:31Z"
---

## Request

修复飞书项目创建灰度流程的卡片体验：当前主链路已跑通，但审批前后卡片信息顺序、状态展示和内部字段暴露让用户困惑。

## PM Triage

- taskType: engineering_action
- ownerAgent: agent.company.development
- reviewerAgent: agent.company.project-manager
- humanAcceptanceRequired: false for code-level UX polish; deployment remains controlled by project owner.

## Acceptance Criteria

- 面向用户不显示内部状态码作为主状态，应展示中文状态和下一步行动。
- 面向用户不把 `projects/.../*.md` 作为主要行动信息。
- 手动接管卡片明确说明“立项已通过后的初始化接管任务”。
- Owner onboarding 卡片下一步清楚、中文、可操作。
- 相关测试通过，`validate` 通过。

## Handling Notes

不要新增新流程；只修当前项目创建、审批通过、初始化接管和 owner onboarding 的用户展示层。
