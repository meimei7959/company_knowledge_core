---
type: Workflow
title: Agent team growth and task fact V1 technical solution
description: Architecture solution for ANOS-REQ-160-FUSION-V1, covering PM-controlled worker delivery, task fact projection, growth signal capture, and shared Agent team capability version.
timestamp: "2026-06-23T09:07:14Z"
solutionId: agent-team-growth-and-task-fact-technical-solution
projectId: company-knowledge-core
ownerAgent: agent.company.architecture
status: draft
requirementRefs:
  - ANOS-REQ-160
  - ANOS-REQ-160-FUSION-V1
sourceRefs:
  - projects/company-knowledge-core/receiver-reviews/receiver-review.agent-team-growth-task-fact.architecture.md
  - docs/product/ai-native-os/agent-team-growth-and-task-fact-prd.md
  - docs/product/ai-native-os/task-execution-productization-prd.md
  - docs/product/ai-native-os/task-execution-productization-acceptance-matrix.md
  - docs/strategy/zhenzhi-ai-native-knowledge-system.md
---

# Agent team growth and task fact V1 technical solution

## Conclusion

ReceiverReview decision is `accepted_with_assumptions`, so architecture work proceeds.

V1 should extend ANOS-REQ-160 from a read-only task fact view into a controlled delivery loop:

1. Agent Hub registers work intake as traceable ProjectTask or KnowledgeTask.
2. Scheduler keeps Project Manager Agent as delivery controller.
3. Project Manager Agent decomposes into role-scoped worker tasks.
4. Each worker creates ReceiverReview before work, then writes TaskResult, AgentRun, evidence, and audit.
5. Project Manager Agent consolidates worker outputs into parent TaskResult and acceptance route.
6. Task fact projection displays source, execution, acceptance, evidence, and growth signals.
7. Failures, rework, repeated blockers, manual corrections, and role-boundary violations create draft AgentImprovementProposal and EvalCase links.

No V1 design includes multiple computers jointly competing for or co-executing one project. Two computers may run different projects in parallel, but both resolve the same Agent team capability version before task assignment.

## Architecture boundary

V1 is an orchestration and projection upgrade over existing core objects. It must not create a new truth source for tasks or replace Scheduler, Agent Ring, AgentRun, TaskResult, or review gates.

Allowed changes:

- Extend task fact projection schema and UI/API consumers.
- Add or formalize link fields on existing ProjectTask, TaskResult, AgentRun, AgentRunner, ReceiverReview, AgentImprovementProposal, and EvalCase records.
- Add Scheduler validation for PM-controlled worker decomposition and Agent team capability version compatibility.
- Add draft growth-signal generation and review routing.
- Add harness checks and acceptance tests for lifecycle coverage.

Not allowed in V1:

- Multi-computer cooperative execution for one project.
- Multiple computers racing to claim the same project scope.
- Automatic publication of skill, role-rule, policy, or verified knowledge changes.
- New durable core object that duplicates ProjectTask, TaskResult, AgentRun, or AgentRunner.
- Product PRD rewrite, implementation code, or Test Agent report inside this architecture deliverable.

## System flow

```text
Agent Hub intake
-> SourceMaterial / ProjectTask / KnowledgeTask registration
-> Scheduler assigns parent task to Project Manager Agent
-> PM creates child worker tasks with role boundary, acceptance refs, and evidence expectations
-> Worker ReceiverReview gate
-> Agent Ring or local runner executes worker task
-> Worker writes AgentRun + TaskResult + evidence + audit
-> PM consolidates parent TaskResult and acceptance route
-> Task fact projection reads parent + workers + evidence + reviews
-> Growth detector drafts AgentImprovementProposal / EvalCase when signals exist
```

## Data contract

### Parent task

Parent ProjectTask remains the delivery control record.

Required V1 fields or refs:

| Field | Purpose |
| --- | --- |
| `taskId`, `projectId`, `workSourceType`, `requirementRefs`, `sourceMaterialRefs` | Source and traceability. |
| `assignee: agent.company.project-manager` | PM is V1 delivery controller. |
| `workerTaskRefs` | Child worker ProjectTask or KnowledgeTask refs. |
| `agentTeamCapabilityVersionRef` | Shared capability version used by this project. |
| `acceptanceCriteriaRefs`, `receiverReviewRefs`, `resultRef`, `auditRefs`, `notificationRefs` | Existing lifecycle trace. |

### Worker task

Worker task is a normal ProjectTask or KnowledgeTask, not a new object.

Required V1 fields or refs:

| Field | Purpose |
| --- | --- |
| `parentTaskRef` | Links worker task to PM-controlled parent. |
| `workerRole` / `assignee` | Role boundary, such as product, design, architecture, development, test, operations, or knowledge engineering. |
| `workerInputRefs` | PRD, design, technical solution, test matrix, source material, or prior TaskResult refs. |
| `receiverReviewRefs` | Worker acceptance gate before work. |
| `resultRef`, `agentRunRefs`, `evidenceRefs` | Worker output and execution proof. |
| `boundaryNotes` | Explicit non-goals, permissions, and "do not代工" constraints. |

### TaskResult

TaskResult remains the writeback contract. V1 requires:

- `summary`, `outputRefs`, `evidenceRefs`, `testsOrChecks`.
- `operatingRuleRefs`, `commonRulesEvaluation`, `qualityEvaluation`.
- `acceptancePolicy` and `handoffContract` or `terminalReason`.
- `workerResultRefs` on parent TaskResult when PM consolidates child work.
- `growthSignalRefs` when draft improvement proposals or eval cases are created.

### AgentRun

AgentRun records execution. V1 projection should read:

- executor Agent, runner, host label, started/completed timestamps, status, tool refs, context pack refs, and output refs.
- parent/child task relation when a worker run belongs to a PM-controlled parent.

### Agent team capability version

Do not add a new core object for V1. Represent shared team capability as a versioned reference produced from existing records:

- Agent records and role rules.
- ToolAsset records and allowed tool versions.
- `docs/agent-team/company-skill-registry.json`.
- eval baseline refs and current acceptance policy refs.
- optional immutable digest stored as `agentTeamCapabilityVersionRef` on ProjectTask and AgentRunner registration.

Scheduler must reject or mark `capability_version_mismatch` when a runner cannot prove the required capability version for a task. Two computers can run different projects if both satisfy the required version. V1 does not coordinate joint work on one project.

## Task fact projection

Extend existing `task-fact-view` read model to version `task-fact-view.v1` while preserving V0 fields.

Required blocks:

| Block | Read source | Required behavior |
| --- | --- | --- |
| `identity` | ProjectTask / KnowledgeTask | Show task identity, project, priority, status, and requirement refs. |
| `source` | SourceMaterial, requirement refs, source reason | Show why task exists and what input triggered it. |
| `receiverReview` | ReceiverReview refs | Show decision, assumptions, issues, reviewer, and reviewed time. |
| `execution` | AgentRunner, AgentRun, lease fields | Show executor, runner, host label, phase, heartbeat, and gaps. |
| `workerParticipation` | parent/child task refs, worker TaskResult refs | Show each worker role, boundary, input, output, evidence, and PM consolidation status. |
| `resultEvidence` | TaskResult | Show result status, summary, output refs, evidence refs, tests/checks, and missing evidence gaps. |
| `acceptance` | TaskResult.acceptancePolicy, ReviewRecord | Show acceptance owner, route, human-review requirement, and current acceptance status. |
| `growthSignals` | TaskResult quality, blockers, AgentImprovementProposal, EvalCase | Show failed quality, rework, manual correction, blocked repeat, proposal refs, eval case refs, and learning-loop gaps. |
| `auditNotification` | AuditLog, NotificationRecord | Show last audit action, notification delivery, and missing audit gaps. |
| `capabilityVersion` | ProjectTask, AgentRunner, skill registry digest | Show required version, runner version, match/mismatch, and project isolation. |

Projection must never infer success from missing evidence. Missing required trace displays explicit gaps such as `worker trace gap`, `result evidence gap`, `learning loop gap`, `capability version gap`, or `audit gap`.

## API / CLI contract

Development Agent should extend existing surfaces instead of creating parallel readers:

- `GET /v0/projects/{projectId}/tasks/{taskId}/fact-view` may return `schemaVersion: task-fact-view.v1` when V1 fields exist, while preserving V0-compatible keys.
- `zhenzhi-knowledge task fact --project <projectId> --task <taskId> --format json|markdown` should display the same facts and gaps as the API.
- Scheduler validation should expose machine-readable reasons: `missing_pm_controller`, `missing_worker_review`, `missing_worker_result`, `capability_version_mismatch`, `growth_signal_gap`, and `unsupported_multi_computer_project_execution`.

## Workbench contract

Workbench can consume the read model in six panes:

1. Task source and identity.
2. PM control and worker task list.
3. ReceiverReview and assumptions/issues.
4. Execution timeline and runner host.
5. Result, evidence, tests/checks, and acceptance route.
6. Growth signals and capability version.

The UI should show readable labels and next owners, not raw IDs as primary text. Raw refs can remain secondary evidence links.

## Governance and safety

- Every write path must create AuditLog.
- Worker cannot start without ReceiverReview unless parent task records an explicit legacy gap.
- PM may consolidate worker results but must not replace specialized Agent outputs.
- Growth proposals are drafts until reviewed. Verified knowledge, policy, role-rule, permission, or security-affecting changes require human approval.
- Sensitive refs must be redacted in projection according to existing permission rules.
- Review gates must not block raw material registration, task creation, TaskResult writeback, notification, or audit.

## Development task split

| Task | Owner | Scope |
| --- | --- | --- |
| DEV-1 task fact V1 projection | Development Agent | Extend existing read model from V0 to V1 blocks, gap taxonomy, markdown/json parity, and backward compatibility. |
| DEV-2 PM-worker lifecycle contract | Development Agent | Add parent/worker task refs, worker ReceiverReview validation, parent TaskResult consolidation refs, and Scheduler checks. |
| DEV-3 capability version compatibility | Development Agent | Compute/read `agentTeamCapabilityVersionRef`, bind ProjectTask and AgentRunner compatibility, reject unsupported same-project multi-computer execution. |
| DEV-4 growth signal draft routing | Development Agent | Generate/link draft AgentImprovementProposal and EvalCase records from failed quality, rework, manual correction, repeated blockers, and role-boundary violations. |
| DEV-5 API/CLI/workbench integration | Development Agent | Expose same V1 projection through API, CLI, and workbench panes without duplicating fact derivation. |
| DEV-6 audit and notification hardening | Development Agent | Ensure new writes and lifecycle transitions create AuditLog and notification refs where required. |

## Test focus

Testing should cover lifecycle, not only single functions:

- Unit tests for V1 projection blocks and gap taxonomy.
- Contract tests proving API and CLI return consistent facts for same task.
- Scheduler tests for PM-controlled worker tasks, missing ReceiverReview, missing worker TaskResult, and capability version mismatch.
- Integration fixture covering parent PM task with product, architecture, development, and test workers.
- Negative test proving V1 rejects or marks unsupported multi-computer same-project cooperation/competition.
- Growth tests for failed quality, rework, manual correction, repeated blocker, and role-boundary violation creating draft improvement/eval refs.
- Permission/redaction tests for sensitive SourceMaterial, ToolAsset, and evidence refs.
- Workbench tests for readable task source, execution, acceptance, evidence, growth signal, and capability-version display.

## Risks

- Existing records may not consistently contain parent/worker refs; Development Agent should preserve legacy display with explicit gaps.
- Capability version digest may require a deterministic source list; until formalized, treat mismatches as blocking for new V1 tasks and as gaps for legacy tasks.
- Growth signal generation can over-trigger; V1 should draft and route for review, not auto-publish changes.
- Workbench may lag API/CLI; acceptance should require API/CLI contract first, then UI parity for selected fixtures.

## Handoff

Project Manager Agent should create paired Development and Test tasks from this solution. Development owns implementation and code evidence. Test Agent owns test plan, test execution, and quality report. Architecture Agent should review high-risk implementation before final release handoff.
