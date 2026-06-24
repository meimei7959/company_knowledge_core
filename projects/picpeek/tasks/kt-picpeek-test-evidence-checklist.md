---
type: ProjectTask
title: PicPeek 软著运行与截图证据清单
description: ProjectTask assigned to agent.company.test.
timestamp: "2026-06-24T01:42:32Z"
taskId: kt-picpeek-test-evidence-checklist
taskType: evidence_planning
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"evidence_planning","category":"project","stage":"","requiredCapabilities":["evidence_planning"],"requiredTools":[],"sourceRefs":["/Users/meimei/Documents/picpeek/01_源码镜像/picpeek/README.zh-CN.md"],"repositoryRefs":["/Users/meimei/Documents/picpeek/01_源码镜像/picpeek"],"dataScopes":["project_workspace"],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: picpeek
workSourceType: research
requirementRefs: []
requirementObjectRefs: []
acceptanceCriteriaRefs: []
defectRefs: []
defectObjectRefs: []
incidentRefs: []
operationRefs: []
knowledgeTaskRefs: []
researchQuestion: PicPeek 软著申请需要哪些可验证运行证据、截图和人工确认材料？
sourceReason: 为软著申请准备测试/截图/验收证据清单。
receiverReviewRefs: []
requester: 梅晓华
assignee: agent.company.test
status: pending
priority: normal
dueAt: ""
sourceMaterialRefs:
  - /Users/meimei/Documents/picpeek/01_源码镜像/picpeek/README.zh-CN.md
expectedOutput:
  - 输出软著材料所需的运行检查项、界面截图清单、功能验证路径和人工确认项；不得修改原代码。
resultRef: ""
notificationRefs:
  - notifications/notification.20260624T014232454765Z.md
auditRefs: []
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
pmControlLeaseId: ""
pmControlLeaseGeneration: ""
pmControlPrimaryPm: ""
pmControlLeaseRef: ""
updatedAt: "2026-06-24T01:42:32Z"
---

## Request

PicPeek 软著运行与截图证据清单

## Work Source

- workSourceType: research
- requirementRefs: none
- defectRefs: none
- sourceReason: 为软著申请准备测试/截图/验收证据清单。
- researchQuestion: PicPeek 软著申请需要哪些可验证运行证据、截图和人工确认材料？

## Source Materials

- /Users/meimei/Documents/picpeek/01_源码镜像/picpeek/README.zh-CN.md

## Expected Output

- 输出软著材料所需的运行检查项、界面截图清单、功能验证路径和人工确认项；不得修改原代码。

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
