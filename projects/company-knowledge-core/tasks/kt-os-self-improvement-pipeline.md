---
type: ProjectTask
title: AI Native OS Self-Improvement Pipeline hardening
description: Convert failures and manual corrections into skill changes, eval cases, guide updates, and controlled Agent version rollout.
timestamp: "2026-06-20T02:40:00Z"
taskId: KT-OS-SELF-IMPROVEMENT-PIPELINE
taskType: os_maturity_hardening
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.knowledge-engineering
requiredCapabilities:
  - agent_improvement
  - eval_case_generation
  - skill_update
  - rollout
requiredAgents:
  - agent.company-knowledge-core.knowledge-engineering
  - agent.company-knowledge-core.project-manager
  - agent.company-knowledge-core.test
preferredRunner: []
assignedRunner: runner.meimei-mac-local-codex
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: waiting_runner
priority: high
dueAt: []
sourceMaterialRefs:
  - docs/agent-team/company-agent-team-operating-guide.md
expectedOutput:
  - AgentImprovementProposal lifecycle
  - eval case generation from failures
  - skill update and rollout gate
  - rollback and metrics loop
resultRef: []
notificationRefs:
  - notifications/notification.20260621T052918745589Z.md
  - notifications/notification.20260621T053349652571Z.md
  - notifications/notification.20260621T053430465924Z.md
  - notifications/notification.20260621T055524585083Z.md
  - notifications/notification.20260621T055554630253Z.md
  - notifications/notification.20260621T055613443836Z.md
  - notifications/notification.20260621T061855457412Z.md
  - notifications/notification.20260621T062940774072Z.md
auditRefs: []
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_maturity_hardening","category":"project","stage":"","requiredCapabilities":["os_maturity_hardening","agent_improvement","eval_case_generation","skill_update","rollout"],"requiredTools":[],"sourceRefs":["docs/agent-team/company-agent-team-operating-guide.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Make Agents become more reliable after failures instead of repeating the same mistakes.

## Supports Mature OS Capability

Self-Improvement Pipeline.

## Requirements

- Low-quality, rejected, repeated retry, blocked, or manually corrected outputs generate AgentImprovementProposal.
- Improvement creates or updates eval cases before changing skills.
- Skill changes require evaluation, version bump, guide update, and rollout record.

## Completion Standard

- Repeated failure produces improvement task without manual request.
- A passed improvement updates Skill version and Agent guide.
- Failed improvement remains isolated and does not affect company-wide behavior.

## Test Method

- Rejected TaskResult creates improvement proposal.
- Improvement proposal creates eval case.
- Passing eval promotes skill version; failing eval blocks promotion.
