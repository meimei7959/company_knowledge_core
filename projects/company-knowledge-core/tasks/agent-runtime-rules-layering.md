---
type: ProjectTask
title: 落地分层 Agent 行为规范和运行时校验
description: ProjectTask assigned to agent.company.development.
timestamp: "2026-06-21T02:19:00Z"
taskId: agent-runtime-rules-layering
taskType: engineering_action
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action"],"requiredTools":[],"sourceRefs":["docs/agent-team/common-agent-operating-rules.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: meimei
assignee: agent.company.development
status: waiting_acceptance
priority: high
dueAt: ""
sourceMaterialRefs:
  - docs/agent-team/common-agent-operating-rules.md
expectedOutput:
  - 短规则分层：宪法、任务运行契约、人审策略、岗位/项目上下文
  - task start/pull 注入规则引用，task finish 写入 operatingRuleRefs 和 commonRulesEvaluation
  - 测试证明规则不是只落到文档，而是落到 TaskResult 和 context pack
resultRef: task-results/tr-agent-runtime-rules-layering.md
notificationRefs:
  - notifications/notification.20260621T021900608975Z.md
  - notifications/notification.20260621T023236446891Z.md
  - notifications/notification.20260621T023236448085Z.md
  - notifications/notification.20260621T023236448705Z.md
  - notifications/notification.20260621T025038978640Z.md
  - notifications/notification.20260621T025038979477Z.md
  - notifications/notification.20260621T025038980375Z.md
  - notifications/notification.20260621T053327960322Z.md
  - notifications/notification.20260621T053327961260Z.md
  - notifications/notification.20260623T092039567033Z.md
  - notifications/notification.20260623T092039568456Z.md
  - notifications/notification.20260623T092653857719Z.md
  - notifications/notification.20260623T092653860226Z.md
  - notifications/notification.20260623T105919642749Z.md
  - notifications/notification.20260623T105919644481Z.md
  - notifications/notification.20260623T111945158516Z.md
  - notifications/notification.20260623T111945160261Z.md
  - notifications/notification.20260624T033246178250Z.md
  - notifications/notification.20260624T033246179567Z.md
  - notifications/notification.20260624T040043514669Z.md
  - notifications/notification.20260624T040043516148Z.md
  - notifications/notification.20260624T044859979369Z.md
  - notifications/notification.20260624T044859980694Z.md
auditRefs: []
assignedRunner: ""
leaseOwner: ""
leaseProofHash: ""
leaseExpiresAt: ""
heartbeatAt: ""
taskVersion: 1
handoffContract: {"from":"agent.company.development","to":"agent.company.test","requiredArtifacts":["technical plan","change summary","self-test result","risk notes"]}
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
updatedAt: "2026-06-24T04:48:59Z"
completedAt: "2026-06-21T02:50:38Z"
---

## Request

落地分层 Agent 行为规范和运行时校验

## Source Materials

- docs/agent-team/common-agent-operating-rules.md

## Expected Output

- 短规则分层：宪法、任务运行契约、人审策略、岗位/项目上下文
- task start/pull 注入规则引用，task finish 写入 operatingRuleRefs 和 commonRulesEvaluation
- 测试证明规则不是只落到文档，而是落到 TaskResult 和 context pack

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: agent.company.development
- to: agent.company.test
- requiredArtifacts:
  - technical plan
  - change summary
  - self-test result
  - risk notes

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.
