---
type: ProjectTask
title: Mature AI Native OS policy and quality gates
description: Combine policy, evaluation, acceptance, retry, repair, escalation, and human confirmation into one quality-control loop.
timestamp: "2026-06-20T03:00:00Z"
taskId: KT-OS-POLICY-QUALITY-GATES
taskType: os_master_task
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - policy_engine
  - quality_evaluation
  - acceptance_gate
  - retry_repair_escalation
requiredAgents:
  - agent.company-knowledge-core.project-manager
  - agent.company-knowledge-core.test
preferredRunner: []
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: critical
dueAt: []
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-os-policy-engine.md
  - projects/company-knowledge-core/tasks/kt-os-evaluation-engine.md
  - docs/workflows/evaluation-lifecycle.md
expectedOutput:
  - policy decision contract
  - quality evaluation contract
  - retry and repair routing
  - human acceptance and PM auto-accept rules
resultRef: task-results/tr-kt-os-policy-quality-gates.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-20T03:30:00Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_master_task","category":"project","stage":"","requiredCapabilities":["os_master_task","policy_engine","quality_evaluation","acceptance_gate","retry_repair_escalation"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-os-policy-engine.md","projects/company-knowledge-core/tasks/kt-os-evaluation-engine.md","docs/workflows/evaluation-lifecycle.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
updatedAt: "2026-06-21T07:18:05Z"
---

## Goal

Every output is judged before it moves the company forward. Good work advances; weak work retries or repairs; risky work is escalated or human-gated.

## Covers

- `KT-OS-POLICY-ENGINE`
- `KT-OS-EVALUATION-ENGINE`

## Completion Standard

- TaskResult includes qualityEvaluation and acceptancePolicy where applicable.
- Policy can auto-accept low-risk work and require human acceptance for high-risk or handoff work.
- Failed evaluation creates retry, repair, escalation, or self-improvement task.
- Repeated failures stop looping and escalate.

## Test Method

- Role handoff, retry, escalation, human acceptance, rejection, and Feishu acceptance-card tests.
- Tool approval and high-risk execution tests.
- Evaluation failure creates knowledge and improvement evidence.
