---
type: ProjectTask
title: Mature AI Native OS collaboration and self-improvement loop
description: Make Agent discussion, decisions, follow-up tasks, failure learning, eval generation, skill updates, and guide updates form a closed improvement loop.
timestamp: "2026-06-20T03:00:00Z"
taskId: KT-OS-COLLABORATION-SELF-IMPROVEMENT
taskType: os_master_task
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - agent_discussion
  - decision_record
  - followup_task
  - agent_improvement
  - eval_case_generation
requiredAgents:
  - agent.company-knowledge-core.project-manager
  - agent.company-knowledge-core.knowledge-engineering
  - agent.company-knowledge-core.test
preferredRunner: []
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-os-agent-collaboration-protocol.md
  - projects/company-knowledge-core/tasks/kt-os-self-improvement-pipeline.md
  - docs/agent-team/company-agent-team-operating-guide.md
expectedOutput:
  - discussion session workflow
  - decision and follow-up task creation
  - improvement proposal generation
  - eval case and capability report
  - guide update gate
resultRef: task-results/tr-kt-os-collaboration-self-improvement.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-20T03:30:00Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_master_task","category":"project","stage":"","requiredCapabilities":["os_master_task","agent_discussion","decision_record","followup_task","agent_improvement","eval_case_generation"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-os-agent-collaboration-protocol.md","projects/company-knowledge-core/tasks/kt-os-self-improvement-pipeline.md","docs/agent-team/company-agent-team-operating-guide.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
updatedAt: "2026-06-21T07:18:05Z"
---

## Goal

Agents must collaborate and improve like a digital company team: discuss, decide, execute, evaluate, learn, and update working rules.

## Covers

- `KT-OS-AGENT-COLLABORATION-PROTOCOL`
- `KT-OS-SELF-IMPROVEMENT-PIPELINE`

## Completion Standard

- Discussion cannot finish without decision, follow-up task, rejection, or human-decision path.
- Failed or rejected output creates improvement proposal and eval case when useful.
- Capability reports show whether Agents are improving.
- Agent Team guide update gate prevents process changes without documentation evidence.

## Test Method

- Discussion session, turn, finalization, decision, follow-up task, and notification tests.
- Failed result and human rejection create improvement tests.
- Agent capability report and guide gate validation tests.
