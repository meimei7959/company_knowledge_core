---
type: ProjectTask
title: Hand off to agent.company.test for kt-ai-native-os-rt-test-workbench-slice regression.
description: ProjectTask assigned to agent.company.test.
timestamp: "2026-06-21T11:09:56Z"
taskId: kt-ai-native-os-rt-dev-workbench-slice-handoff
taskType: role_handoff
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"role_handoff","category":"project","stage":"","requiredCapabilities":["role_handoff"],"requiredTools":[],"sourceRefs":["task-results/tr-kt-ai-native-os-rt-test-context-pack-slice.md","task-results/tr-kt-ai-native-os-rt-dev-context-pack-slice.md","docs/product/ai-native-os/requirement-tree.md","task-results/tr-kt-ai-native-os-rt-dev-workbench-slice.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.test
status: pending
priority: high
dueAt: ""
sourceMaterialRefs:
  - task-results/tr-kt-ai-native-os-rt-test-context-pack-slice.md
  - task-results/tr-kt-ai-native-os-rt-dev-context-pack-slice.md
  - docs/product/ai-native-os/requirement-tree.md
  - task-results/tr-kt-ai-native-os-rt-dev-workbench-slice.md
expectedOutput:
  - Read upstream TaskResult and artifacts.
  - Accept handoff or return changes_requested with clear blocker.
  - Produce the next role output according to the company Agent Team guide.
resultRef: ""
notificationRefs:
  - notifications/notification.20260621T110956894183Z.md
  - notifications/notification.20260621T110956895089Z.md
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
updatedAt: "2026-06-21T11:09:56Z"
parentTaskId: kt-ai-native-os-rt-dev-workbench-slice
originTaskId: kt-ai-native-os-rt-dev-workbench-slice
triggerResultRef: task-results/tr-kt-ai-native-os-rt-dev-workbench-slice.md
handoffFrom: ""
handoffTo: agent.company.test
qualityGate: passed
---

## Request

Hand off to agent.company.test for kt-ai-native-os-rt-test-workbench-slice regression.

## Source Materials

- task-results/tr-kt-ai-native-os-rt-test-context-pack-slice.md
- task-results/tr-kt-ai-native-os-rt-dev-context-pack-slice.md
- docs/product/ai-native-os/requirement-tree.md
- task-results/tr-kt-ai-native-os-rt-dev-workbench-slice.md

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
