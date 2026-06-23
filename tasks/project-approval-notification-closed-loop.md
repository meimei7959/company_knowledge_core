---
type: ProjectTask
title: 修复飞书项目立项审批通过后的通知闭环
description: ProjectTask assigned to agent.company.development.
timestamp: "2026-06-20T15:24:33Z"
taskId: project-approval-notification-closed-loop
taskType: engineering_action
projectId: agent-hub
requester: meimei
assignee: agent.company.development
status: done
priority: normal
dueAt: ""
sourceMaterialRefs:
  - docs/workflows/feishu-intake-lifecycle.md
expectedOutput: []
resultRef: task-results/tr-project-approval-notification-closed-loop.md
notificationRefs:
  - notifications/notification.20260620T152433565005Z.md
  - notifications/notification.20260620T155004657672Z.md
  - notifications/notification.20260620T155004659792Z.md
  - notifications/notification.20260620T155004660458Z.md
auditRefs: []
assignedRunner: ""
leaseOwner: ""
leaseProofHash: ""
leaseExpiresAt: ""
heartbeatAt: ""
taskVersion: 1
handoffContract: {"from":"agent.company-knowledge-core.knowledge-engineering","to":"agent.core.knowledge-review","requiredArtifacts":["original source","summary","structured draft","evidence refs"]}
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
updatedAt: "2026-06-20T15:50:04Z"
completedAt: "2026-06-20T15:50:04Z"
improvementRefs: []
---

## Request

修复飞书项目立项审批通过后的通知闭环

## Source Materials

- docs/workflows/feishu-intake-lifecycle.md

## Expected Output

- TaskResult with summary, evidence, and next actions.

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Correction Note

- 2026-06-20: This task was initially created through the generic task intake path and was incorrectly typed as `KnowledgeTask`.
- Corrected to `ProjectTask` because the actual work was an engineering approval-notification closed-loop fix, not source-material extraction.
- The generated retry task was superseded; no knowledge-draft retry is required for this engineering fix.

## Handoff Contract

- from: agent.company-knowledge-core.knowledge-engineering
- to: agent.core.knowledge-review
- requiredArtifacts:
  - original source
  - summary
  - structured draft
  - evidence refs

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.
