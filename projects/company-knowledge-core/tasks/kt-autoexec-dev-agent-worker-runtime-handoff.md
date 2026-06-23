---
type: ProjectTask
title: PM review worker runtime evidence.
description: ProjectTask assigned to agent.company.test.
timestamp: "2026-06-21T06:14:22Z"
taskId: kt-autoexec-dev-agent-worker-runtime-handoff
taskType: role_handoff
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"role_handoff","category":"project","stage":"","requiredCapabilities":["role_handoff"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/coordination/auto-execution-system-delivery-plan.md","projects/company-knowledge-core/coordination/ai-native-os-development-stage-control.md","task-results/tr-kt-autoexec-dev-agent-worker-runtime.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.test
status: waiting_runner
priority: critical
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/coordination/auto-execution-system-delivery-plan.md
  - projects/company-knowledge-core/coordination/ai-native-os-development-stage-control.md
  - task-results/tr-kt-autoexec-dev-agent-worker-runtime.md
expectedOutput:
  - Read upstream TaskResult and artifacts.
  - Accept handoff or return changes_requested with clear blocker.
  - Produce the next role output according to the company Agent Team guide.
resultRef: ""
notificationRefs:
  - notifications/notification.20260621T061422542747Z.md
  - notifications/notification.20260621T061422544578Z.md
  - notifications/notification.20260621T061855433014Z.md
auditRefs: []
assignedRunner: ""
leaseOwner: ""
leaseProofHash: ""
leaseExpiresAt: ""
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
updatedAt: "2026-06-21T07:18:05Z"
parentTaskId: kt-autoexec-dev-agent-worker-runtime
originTaskId: kt-autoexec-dev-agent-worker-runtime
triggerResultRef: task-results/tr-kt-autoexec-dev-agent-worker-runtime.md
handoffFrom: ""
handoffTo: agent.company.test
qualityGate: passed
---

## Request

PM review worker runtime evidence.

## Source Materials

- projects/company-knowledge-core/coordination/auto-execution-system-delivery-plan.md
- projects/company-knowledge-core/coordination/ai-native-os-development-stage-control.md
- task-results/tr-kt-autoexec-dev-agent-worker-runtime.md

## Expected Output

- Read upstream TaskResult and artifacts.
- Accept handoff or return changes_requested with clear blocker.
- Produce the next role output according to the company Agent Team guide.

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
