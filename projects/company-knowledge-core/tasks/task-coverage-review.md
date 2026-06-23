---
type: ProjectTask
title: Task Coverage Review
description: Coverage review for central processor, Feishu DeepSeek routing, Agent Ring, StubRunner, and access credential tasks.
timestamp: "2026-06-18T00:00:00Z"
taskId: TASK-COVERAGE-REVIEW
taskType: project_initialization
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.project-manager
requiredCapabilities:
  - project_initialization
  - task_review
  - quality_gate
requiredAgents:
  - agent.company-knowledge-core.project-manager
preferredRunner:
  - runner.meimei-mac-codex
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: medium
dueAt: []
sourceRef: projects/company-knowledge-core/tasks/index.md
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/index.md
expectedOutput:
  - task coverage map
  - task quality gate
  - completion criteria
resultRef: []
notificationRefs: []
auditRefs: []
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"project_initialization","category":"project","stage":"","requiredCapabilities":["project_initialization","task_review","quality_gate"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/index.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project_management","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
updatedAt: "2026-06-21T07:18:05Z"
---

# Task Coverage Review

## Purpose

This review checks whether the current task set covers the upgraded product architecture:

- Feishu remains the entrance.
- DeepSeek powers Feishu intent routing.
- Central processor owns scheduler and knowledge engineering.
- Agent Ring is external.
- StubRunner covers central-chain testing before Agent Ring exists.
- Token requests become access credential requests with `secretRef`.

## Coverage Map

| Area | Task | Coverage |
| --- | --- | --- |
| Agent Ring protocol | `KT-AGENT-RING-PROTOCOL` | external runner registration, polling/claiming, heartbeat, TaskResult writeback |
| Project portability | `KT-PROJECT-CONTEXT-SYNC` | ProjectContextBundle, environment manifest, handoff, reassignment |
| Feishu + DeepSeek router | `KT-FEISHU-DEEPSEEK-ROUTER` | model config, routing prompt/schema, fallback |
| Feishu safety gate | `KT-FEISHU-ROUTING-SAFETY` | model output validation, high-risk block, secretRef-only rule |
| Feishu cards | `KT-FEISHU-CARD-WORKFLOW` | card states, confirmation, readable task cards |
| Feishu -> Agent Ring dispatch | `KT-FEISHU-AGENT-RING-DISPATCH` | complex work becomes ProjectTask/KnowledgeTask |
| DeepSeek observability | `KT-DEEPSEEK-OBSERVABILITY-EVALS` | eval cases, cost/error metrics, outage fallback |
| No Agent Ring testing | `KT-AGENT-RING-STUB-RUNNER-TESTS` | StubRunner lifecycle, deterministic writeback, reassignment |
| Access credentials | `KT-ACCESS-CREDENTIAL-SECRET-FLOW` | credential request, approval, secretRef, Agent Ring readiness |

## Important Boundaries

Central processor owns:

- request intake;
- approval and policy;
- task creation;
- runner registry records;
- task state;
- `secretRef`;
- audit and notification.

Central processor does not own:

- plaintext local tool tokens;
- Agent Ring desktop/service runtime;
- local Codex/Claude execution;
- local browser or filesystem state;
- real Secret Manager implementation unless explicitly added later.

## End-To-End Test Path Before Agent Ring

```txt
Feishu/CLI request
-> DeepSeek routing decision or deterministic test router
-> safety gate
-> SourceMaterial / ProjectTask / KnowledgeTask / CredentialRequest task
-> StubRunner registration
-> StubRunner claim with lease
-> context bundle pull
-> fake secretRef readiness check
-> deterministic TaskResult / AgentRun writeback
-> review/audit/notification state
```

This tests central orchestration without pretending to test local workstation execution.

## Remaining Implementation Work

The task set is complete enough for the current planning layer. Implementation is still pending for:

- actual DeepSeek API adapter;
- routing JSON validator;
- access credential request object or task shape;
- Feishu interactive cards;
- StubRunner implementation;
- scheduler claim/lease APIs;
- real Agent Ring contract tests when the external workstation exists.

## Completion Criteria For This Phase

This planning phase is complete when:

- every major product flow has a task;
- every task links to the controlling architecture/protocol doc;
- every ProjectTask has `Definition of Done`, `Test Plan`, and `Self-Verification Checklist`;
- access credential flow no longer assumes central plaintext token storage;
- no-Agent-Ring testing has an explicit StubRunner strategy;
- existing Feishu entrance remains in the plan.

The implementation phase is not complete until the tasks above are built and tested.

## Definition of Done

- Major product flows are represented by task cards.
- Each active task has completion standards.
- Boundaries between central processor and Agent Ring are explicit.
- Remaining implementation work is visible and not hidden inside prose.
- Task quality gate is documented for future task closeout.

## Test Plan

- Compare tasks in `projects/company-knowledge-core/tasks/index.md` with the coverage map.
- Check every ProjectTask for Definition of Done, Test Plan, and Self-Verification Checklist.
- Confirm no central task requires Agent Ring to expose local secrets or internal implementation.

## Self-Verification Checklist

- [x] Coverage map exists.
- [x] Central/Agent Ring boundaries recorded.
- [x] Task quality gate recorded.
- [x] New project initialization task list supersedes old remaining-work notes.

## Task Quality Gate

Before any ProjectTask can move from `pending` to `done`:

- its Definition of Done must be satisfied by concrete files, behavior, tests, or documented review evidence;
- its Test Plan must be executed or explicitly marked not applicable with reason;
- its Self-Verification Checklist must be checked by the completing Agent;
- `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate` must pass;
- relevant unit/integration tests must pass;
- TaskResult must summarize evidence, test output, remaining risks, and next actions.
