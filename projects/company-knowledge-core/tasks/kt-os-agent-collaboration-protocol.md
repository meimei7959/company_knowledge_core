---
type: ProjectTask
title: AI Native OS Agent Collaboration Protocol hardening
description: Make Agent-to-Agent discussion a typed workflow that ends in decision, follow-up task, rejection, or human-decision request.
timestamp: "2026-06-20T02:40:00Z"
taskId: KT-OS-AGENT-COLLABORATION-PROTOCOL
taskType: os_maturity_hardening
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - agent_discussion
  - decision_record
  - cross_role_handoff
  - human_decision_request
requiredAgents:
  - agent.company-knowledge-core.project-manager
  - agent.company-knowledge-core.product-manager
  - agent.company-knowledge-core.design
  - agent.company-knowledge-core.development
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
  - docs/protocols/agent-workbench-integration-brief.md
expectedOutput:
  - DiscussionSession lifecycle
  - DiscussionTurn and DiscussionSummary contract
  - decision and follow-up task generation
  - visible discussion notification flow
resultRef: []
notificationRefs:
  - notifications/notification.20260621T052918735267Z.md
  - notifications/notification.20260621T053349645116Z.md
  - notifications/notification.20260621T053430458990Z.md
  - notifications/notification.20260621T055524577070Z.md
  - notifications/notification.20260621T055554622077Z.md
  - notifications/notification.20260621T055613436426Z.md
  - notifications/notification.20260621T061855455183Z.md
  - notifications/notification.20260621T062940764936Z.md
auditRefs: []
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_maturity_hardening","category":"project","stage":"","requiredCapabilities":["os_maturity_hardening","agent_discussion","decision_record","cross_role_handoff","human_decision_request"],"requiredTools":[],"sourceRefs":["docs/agent-team/company-agent-team-operating-guide.md","docs/protocols/agent-workbench-integration-brief.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Let product, design, development, test, operations, and knowledge Agents discuss like a company team while producing executable outcomes.

## Supports Mature OS Capability

Agent Collaboration Protocol.

## Requirements

- Discussion has initiator, goal, participants, required decision, context refs, deadline, and exit condition.
- Each turn is attributed to an Agent and can cite evidence.
- Discussion ends only as consensus decision, PM decision, human-decision-required, follow-up task, or rejected proposal.

## Completion Standard

- No discussion remains as loose chat with no outcome.
- Human observers can inspect discussion summary and evidence.
- Accepted discussion outcome creates Decision or ProjectTask.

## Test Method

- Discussion happy path test from issue to decision.
- Conflict path test requiring human decision.
- Follow-up task creation test.
