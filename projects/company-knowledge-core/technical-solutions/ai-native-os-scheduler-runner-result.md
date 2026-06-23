---
type: Workflow
title: AI Native OS Scheduler / Runner / Result / Auto Execution Technical Solution
projectId: company-knowledge-core
taskId: kt-ai-native-os-tech-solution-scheduler-runner-result
ownerAgent: agent.company.development
status: draft
updatedAt: "2026-06-21T06:30:00Z"
requirementRefs:
  - ANOS-REQ-050
  - ANOS-REQ-051
  - ANOS-REQ-052
  - ANOS-REQ-053
  - ANOS-REQ-054
  - ANOS-REQ-055
  - ANOS-REQ-056
  - ANOS-REQ-060
  - ANOS-REQ-061
  - ANOS-REQ-062
  - ANOS-REQ-063
  - ANOS-REQ-070
  - ANOS-REQ-071
  - ANOS-REQ-072
  - ANOS-REQ-073
sourceMaterialRefs:
  - docs/product/ai-native-os/requirements.md
  - docs/scheduler/task-dispatch-model.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-tech-solution-scheduler-runner-result.md
  - projects/company-knowledge-core/coordination/auto-execution-system-delivery-plan.md
  - projects/company-knowledge-core/coordination/ai-native-os-agent-execution-governance.md
---

# Scheduler / Runner / Result / Auto Execution Technical Solution

## 1. Scope And Design Goal

This solution owns the automatic execution spine for AI Native OS:

- Scheduler normalizes dispatchable work into `taskRuntime`, ranks eligible work, assigns or exposes work to runners, and runs stale repair.
- Runner registry represents available execution capacity, current leases, heartbeat, scopes, tools, repositories, and history.
- Agent Worker claims work through a lease, prepares execution context, invokes the selected local agent/tool path, and writes back `TaskResult`.
- Result Center validates evidence, routes acceptance, creates follow-up repair/retry work, and prevents silent closure.
- PM Autopilot runs finite control cycles that select the next safest action, never hidden unbounded execution.

The minimum stable system must move:

```txt
Task created
-> taskRuntime normalized
-> PM Autopilot ranks and dispatches
-> Agent Worker claims with lease
-> Worker heartbeats and writes TaskResult
-> Result Center validates evidence
-> PM Autopilot accepts, rejects, repairs, or escalates
-> Test Agent validates implementation work
-> failed tests return to Development Agent repair
```

Non-goals for this slice:

- no implementation of the external Agent Ring product itself;
- no direct source-code execution by Scheduler;
- no automatic bypass of approval, security, human review, or tool ownership gates;
- no closure based only on a generated document when engineering/test evidence is required.

## 2. Requirement Coverage

| Requirement | Solution commitment |
| --- | --- |
| ANOS-REQ-050 | Add deterministic `taskRuntime` normalization before any dispatch. Runtime stores task type, required capabilities/tools, source refs, acceptance path, review path, risk, permission, and closure evidence policy. |
| ANOS-REQ-051 | Match task to both eligible runner and executor Agent. Mismatch becomes `waiting_runner` or `blocked` with readable reason. |
| ANOS-REQ-052 | Claim creates lease owner, opaque lease token/proof hash, task version, and expiry. Finish/result writeback without current lease fails. |
| ANOS-REQ-053 | Scheduler tick handles heartbeat freshness, stale lease repair, retry, cancellation, and escalation. Critical stale tasks alert PM Agent and Ops path. |
| ANOS-REQ-054 | Engineering acceptance requires implementation evidence and test evidence. Knowledge draft alone cannot close engineering work. |
| ANOS-REQ-055 | Knowledge capture acceptance requires SourceMaterial, draft KnowledgeItem, evidence packet, and review path. |
| ANOS-REQ-056 | Product discovery acceptance requires RequirementState and PRD/product quality gate. Missing user, market, business model, or acceptance criteria blocks closure. |
| ANOS-REQ-060 | Runner registry exposes runner id, machine, owner, heartbeat, load, status, Agents, tools, repositories, data scopes. |
| ANOS-REQ-061 | Runner view exposes active leases, stale/failed leases, task history, and repair controls. |
| ANOS-REQ-062 | Manual handoff uses the same lease/result contract and still writes AgentRun or equivalent record, TaskResult, NotificationRecord, and AuditLog. |
| ANOS-REQ-063 | Runner scope checks block repo, source, tool, and knowledge access outside allowed scopes and audit the denial. |
| ANOS-REQ-070 | TaskResult schema requires summary, outputRefs, evidenceRefs, risks, blockers, nextAction, executorAgent, runner, source links, and requirementRefs. |
| ANOS-REQ-071 | Result Center displays acceptance path from `taskRuntime`: product acceptance, test acceptance, knowledge review, human approval, or combinations. |
| ANOS-REQ-072 | Rejected result creates a repair/retry/follow-up task with exact gap and owner. |
| ANOS-REQ-073 | Repeatable/systemic Agent failure creates Agent improvement proposal or Eval/repair task linked to failure evidence. |

## 3. Core Model Changes

### 3.1 taskRuntime

`taskRuntime` is the scheduler-owned normalized contract. It is created or refreshed before dispatch and copied into `TaskResult` for audit.

Required fields:

- `runtimeVersion`
- `taskType`
- `stage`
- `requiredCapabilities`
- `requiredTools`
- `sourceRefs`
- `repositoryRefs`
- `dataScopes`
- `acceptancePath`: one of `engineering_test`, `knowledge_review`, `product_prd_gate`, `pm_acceptance`, `human_approval`, `release_gate`
- `reviewPath`
- `riskLevel`
- `permissionPolicy`
- `closurePolicy`
- `approvalRelayRequired`
- `testEvidenceRequired`
- `knowledgeEvidenceRequired`
- `productEvidenceRequired`
- `manualHandoffAllowed`

Normalization rule:

```txt
task fields + project policy + requirementRefs + source refs
-> normalize taskRuntime
-> validate required evidence policy
-> dispatch only if runtime is complete
```

The scheduler must not infer task type from title text once `taskRuntime` exists.

### 3.2 AgentRunner

Runner registry record:

- `runnerId`
- `machineId`
- `owner`
- `status`: `online`, `idle`, `busy`, `draining`, `offline`, `disabled`
- `heartbeatAt`
- `load`
- `agentIds`
- `capabilities`
- `tools`
- `repositoryScopes`
- `dataScopes`
- `currentLeases`
- `taskHistory`
- `lastFailure`
- `manualHandoff`

Visibility rule: Workbench and CLI must let PM/Ops answer "which runner can execute this task, why, and what it is doing now."

### 3.3 Lease

Lease fields on task:

- `leaseOwner`
- `leaseTokenHash`
- `leaseIssuedAt`
- `leaseExpiresAt`
- `leaseHeartbeatAt`
- `leaseVersion`
- `leaseAttempt`
- `assignedRunner`
- `executorAgent`

The raw token is returned only once to the claiming runner. Persistent storage keeps a hash/proof. All heartbeat, cancel, and finish operations include the token and expected task version.

Lease invariants:

- one active lease per task;
- finish/writeback requires current non-expired lease;
- stale lease cannot finish;
- stale critical lease triggers alert and repair;
- lease renewal is allowed only while heartbeat is fresh and policy permits;
- reassignment increments `leaseAttempt` and task version.

### 3.4 TaskResult

Required fields:

- `resultId`
- `taskId`
- `requirementRefs`
- `taskRuntime`
- `summary`
- `status`: `submitted`, `accepted`, `rejected`, `needs_repair`, `blocked`, `failed`, `cancelled`
- `outputRefs`
- `evidenceRefs`
- `sourceMaterialRefs`
- `executorAgent`
- `runner`
- `leaseProof`
- `risks`
- `blockers`
- `nextAction`
- `checks`
- `approvalRequest`
- `qualityEvaluation`
- `createdAt`

Closure rule: A task can move to `waiting_acceptance`, `accepted`, or `done` only after Result Center validates the required fields and the acceptance path.

## 4. State Machines

### 4.1 Task Dispatch State

```txt
draft
-> ready_for_runtime
-> dispatchable
-> waiting_runner
-> claimed
-> running
-> result_submitted
-> waiting_acceptance
-> done
```

Failure and side paths:

```txt
dispatchable -> blocked
waiting_runner -> blocked
claimed/running -> stale
stale -> repair_pending
repair_pending -> dispatchable
result_submitted -> rejected
rejected -> repair_pending
running -> approval_relay_requested
approval_relay_requested -> blocked | running | repair_pending
running -> cancelled
```

State transition guards:

- `ready_for_runtime -> dispatchable`: `taskRuntime` complete.
- `dispatchable -> waiting_runner`: no eligible runner or no permitted runner.
- `waiting_runner -> claimed`: runner has capability, scope, status, and valid claim token.
- `claimed -> running`: context pack prepared and lease heartbeat recorded.
- `running -> result_submitted`: TaskResult has valid lease proof.
- `result_submitted -> waiting_acceptance`: required result fields present.
- `waiting_acceptance -> done`: acceptance path passes.
- `result_submitted -> rejected`: evidence, tests, review, or approval path fails.

### 4.2 Runner State

```txt
registered
-> online
-> idle
-> busy
-> draining
-> offline
```

Repair paths:

```txt
online -> unhealthy -> disabled
busy + heartbeat missed -> stale
stale -> offline | repaired
disabled -> online requires PM/Ops action
```

Runner is eligible only when:

- status is `online`, `idle`, or capacity-available `busy`;
- heartbeat is fresh;
- load is below policy limit;
- capability/tool/repo/data scopes satisfy `taskRuntime`;
- no denied approval or policy violation is attached.

### 4.3 Result Review State

```txt
submitted
-> schema_validated
-> acceptance_routed
-> accepted
```

Reject/repair paths:

```txt
schema_validated -> rejected_missing_fields
acceptance_routed -> needs_test
acceptance_routed -> needs_product_review
acceptance_routed -> needs_knowledge_review
acceptance_routed -> needs_human_approval
accepted/rejected -> follow_up_task_created
failed_repeatable -> improvement_proposal_created
```

### 4.4 Test Failure Repair Loop

```txt
Development TaskResult submitted
-> Test Agent runs required tests
-> test pass
-> PM/Product acceptance
```

Failure path:

```txt
Test Agent failure
-> PM records failed test evidence
-> PM creates/reopens Development repair task
-> Development Agent fixes and writes repair TaskResult
-> Test Agent reruns failed tests + regression set
-> PM accepts only after green evidence
```

PM Agent must not silently patch implementation after Test Agent failure. Emergency PM patch is allowed only with incident record and follow-up Development review task.

## 5. PM Approval Relay

Problem: Sub-agent approval prompts can appear in a child window and stall because PM Agent cannot see or approve them.

Solution: approval is a first-class TaskResult/blocker payload, not an interactive child-window prompt.

Sub-agent rule:

```txt
Before a tool/command likely needs approval:
-> stop work
-> write approvalRequest payload
-> return TaskResult status blocked or needs_approval
-> PM Autopilot routes request in main control flow
```

`approvalRequest` fields:

- `requestedAction`
- `toolOrCommand`
- `reason`
- `expectedReadScope`
- `expectedWriteScope`
- `risk`
- `policyRef`
- `fallbackIfDenied`
- `urgency`
- `owner`

PM Autopilot decisions:

- run safe inspection in main window;
- ask human owner in main window;
- split no-approval subtask;
- block task visibly;
- reject request and create alternate task.

Acceptance rule: A slice cannot be accepted while any sub-agent approval is hidden, pending in child window, or missing from PM-visible approval records.

## 6. PM Autopilot Runtime

PM Autopilot is a finite orchestration loop. It does not execute arbitrary implementation work.

Cycle:

```txt
load project state
-> refresh taskRuntime for dispatchable tasks
-> detect stale leases and blocked approvals
-> rank next task
-> assign/claim if allowed
-> review submitted TaskResults
-> create repair/retry/follow-up tasks
-> emit decision log and stop after max cycles
```

Inputs:

- active ProjectTasks and KnowledgeTasks;
- `taskRuntime`;
- runner heartbeat/load/scope;
- TaskResult age/status/evidence;
- approval state;
- review queue;
- notification status;
- requirement coverage matrix.

Decision priority:

1. critical stale lease, failed notification, or hidden approval blocker;
2. submitted TaskResult waiting for acceptance or rejection;
3. failed test requiring Development repair;
4. critical/high implementation or technical solution task with eligible runner;
5. test task unblocked by development result;
6. product/knowledge/review tasks;
7. medium/low follow-up tasks.

Decision output:

- `decisionId`
- `selectedTaskId`
- `action`
- `reason`
- `requirementRefs`
- `runnerCandidate`
- `blockedReason`
- `createdTaskRefs`
- `notificationRefs`
- `auditRefs`

## 7. Agent Worker Runtime

Agent Worker is the runner-side worker adapter. For the current repository it can be local/manual first; later it maps to external Agent Ring.

Worker loop:

```txt
register/heartbeat runner
-> poll eligible tasks or receive assignment
-> claim with lease
-> pull context pack
-> run allowed agent workflow
-> heartbeat while active
-> write AgentRun/manual handoff record
-> write TaskResult with lease proof
-> release lease or mark blocked
```

Worker must check before execution:

- taskRuntime exists and is complete;
- task scope matches runner scopes;
- required tool is registered and permitted;
- approval is already granted or not required;
- context pack includes required source refs;
- output contract is known.

If a required command/tool would require approval, Worker stops and emits `approvalRequest`; it does not open a hidden approval prompt.

## 8. Scheduler / Runner / Result APIs

These are contract-level APIs; implementation may expose them as CLI, HTTP, or local file-backed functions first.

### Scheduler

```txt
POST /scheduler/runtime/normalize
input: taskId
output: taskRuntime, blockers

POST /scheduler/tick
input: projectId, maxCycles, claimMode, dryRun
output: decisions, stateChanges, blockers

POST /scheduler/tasks/{taskId}/assign
input: runnerId, executorAgent
output: assigned task or mismatch reason

POST /scheduler/tasks/{taskId}/cancel
input: reason, actor
output: cancellation record, notification

POST /scheduler/leases/repair-stale
input: projectId, taskId optional
output: repaired/reassigned/escalated leases
```

### Runner

```txt
POST /runners/register
input: runnerId, machine, owner, agents, capabilities, tools, repos, dataScopes
output: registry record

POST /runners/{runnerId}/heartbeat
input: load, status, currentLeases
output: accepted, policy warnings

GET /runners/{runnerId}/tasks
input: capability/scope filters
output: eligible tasks with taskRuntime

POST /tasks/{taskId}/claim
input: runnerId, executorAgent, expectedVersion
output: leaseToken, leaseExpiresAt, contextPackRef

POST /tasks/{taskId}/lease-heartbeat
input: runnerId, leaseToken, progress, currentStep
output: renewed or denied

POST /tasks/{taskId}/finish
input: runnerId, leaseToken, taskResult
output: accepted writeback or rejection reason
```

### Result Center

```txt
POST /results/submit
input: taskResult
output: validation result, acceptance route

POST /results/{resultId}/accept
input: reviewer, acceptanceEvidence
output: task transition, follow-up tasks

POST /results/{resultId}/reject
input: reviewer, gap, requiredRepairOwner
output: repair/retry task

POST /results/{resultId}/route
input: resultId
output: product/test/knowledge/human approval route
```

## 9. CLI Surface

Minimum CLI commands:

```bash
zhenzhi-knowledge scheduler normalize --task <task-id>
zhenzhi-knowledge scheduler tick --project <project-id> --max-cycles 1 --dry-run
zhenzhi-knowledge scheduler tick --project <project-id> --max-cycles 5 --claim
zhenzhi-knowledge scheduler stale-repair --project <project-id>

zhenzhi-knowledge runner register --runner <runner-id> --manifest <file>
zhenzhi-knowledge runner heartbeat --runner <runner-id>
zhenzhi-knowledge runner tasks --runner <runner-id>
zhenzhi-knowledge runner claim --task <task-id> --runner <runner-id> --agent <agent-id>
zhenzhi-knowledge runner lease-heartbeat --task <task-id> --runner <runner-id>
zhenzhi-knowledge runner finish --task <task-id> --result <task-result-file>

zhenzhi-knowledge result validate --result <task-result-file>
zhenzhi-knowledge result route --result <result-id>
zhenzhi-knowledge result reject --result <result-id> --gap <gap-id>
```

Manual handoff uses the same CLI:

```bash
zhenzhi-knowledge runner claim --task <task-id> --runner manual.<owner> --agent <agent-id>
zhenzhi-knowledge runner finish --task <task-id> --result <task-result-file>
```

## 10. Implementation Slices

### Slice A: Runtime Normalization And Closure Policy

Deliver:

- `taskRuntime` builder for ProjectTask and KnowledgeTask.
- Acceptance path resolver for engineering, knowledge, product, PM, human approval, release gate.
- Missing-field blocker output.
- Contract tests for ANOS-REQ-050, 054, 055, 056.

Exit criteria:

- engineering task cannot close from knowledge draft alone;
- product discovery blocks when core RequirementState fields are missing;
- knowledge capture blocks without SourceMaterial and review path.

### Slice B: Runner Registry And Lease Core

Deliver:

- runner registry schema and views;
- register/heartbeat;
- claim with lease token/proof hash;
- lease heartbeat, expiry, finish validation;
- stale repair decision.

Exit criteria:

- invalid/expired lease cannot finish;
- stale critical task alerts PM/Ops;
- runner scopes are visible.

### Slice C: Agent Worker Adapter

Deliver:

- finite worker loop;
- context pack pull;
- approval preflight;
- AgentRun/manual handoff record;
- TaskResult writeback.

Exit criteria:

- manual handoff writes the same records as automated handoff;
- approval-needed work returns PM-visible `approvalRequest`;
- no child-window approval is required for normal worker operation.

### Slice D: Result Center And Repair Loop

Deliver:

- TaskResult schema validation;
- result route resolver;
- reject-to-repair task creation;
- failed test route back to Development Agent;
- repeat/systemic failure improvement proposal.

Exit criteria:

- missing evidence blocks closure;
- rejected result creates exact repair task;
- Test Agent failure creates Development repair task and regression requirement.

### Slice E: PM Autopilot

Deliver:

- finite `scheduler tick` cycle;
- priority/ranking;
- stale repair;
- submitted-result review;
- decision log;
- max cycle cap and dry-run mode.

Exit criteria:

- high-priority technical work wins over medium design work;
- autopilot does not run unbounded;
- every state change has decision evidence.

### Slice F: Workbench Data Surface

Deliver:

- read models for task queue, runner registry, leases, TaskResults, blockers, requirement coverage, PM decisions;
- controls for retry, reassign, pause, accept, reject;
- stale and approval blocker indicators.

Exit criteria:

- PM can see running task, owner, lease, stale state, result evidence, and next action without reading raw files.

### Slice G: Closed-Loop Test Suite

Deliver:

- end-to-end test for create -> normalize -> claim -> heartbeat -> result -> review -> follow-up;
- stale lease test;
- approval relay test;
- test-failure repair loop test;
- unauthorized scope test;
- missing evidence result test.

Exit criteria:

- closed loop passes without manual command-by-command steering;
- failures produce visible repair tasks, not silent PM patches.

## 11. Test Strategy

Unit tests:

- `taskRuntime` normalization for engineering, knowledge, product tasks;
- runner eligibility and scope mismatch reasons;
- lease token validation, expiry, renewal, version mismatch;
- TaskResult schema and closure policy validation;
- result route resolver.

Contract tests:

- Agent Ring-compatible register, heartbeat, poll, claim, context pull, finish;
- manual handoff writes AgentRun or equivalent, TaskResult, NotificationRecord, AuditLog;
- finish without lease token fails;
- stale lease is repairable and visible.

End-to-end tests:

- PM Autopilot picks critical/high task, assigns eligible runner, receives TaskResult, routes acceptance.
- Development result triggers Test Agent task; failing test returns Development repair; repaired result triggers regression; green test allows PM acceptance.
- Sub-agent needing approval returns `approvalRequest`; PM handles it in main flow; task remains blocked until decision.
- Knowledge capture and product discovery use their own acceptance paths, not engineering closure rules.

Negative tests:

- unauthorized repo/tool/data scope blocked and audited;
- TaskResult missing evidenceRefs blocked;
- stale runner cannot finish with old lease;
- repeated Agent failure creates improvement proposal;
- hidden approval/pending child-window marker blocks acceptance.

Release gate:

- repository validation must pass;
- closed-loop suite must pass;
- requirement coverage report must show ANOS-REQ-050..056, 060..063, 070..073 covered by development and test evidence.

## 12. Product Manager Agent Discussion Questions

1. Should PM Autopilot auto-claim tasks in normal mode, or default to dry-run plus explicit `--claim` until the closed-loop suite is stable?
2. What SLA makes a lease stale for critical, high, medium, and low tasks?
3. Which approval request types can PM Agent decide alone, and which must always ask the human owner?
4. Should manual handoff runner ids be person-based (`manual.<owner>`) or machine/session-based (`manual.<owner>.<session>`) for audit clarity?
5. For failed tests, should PM always create a new repair task, or reopen the original Development task when the same owner and slice are unchanged?
6. What is the minimum Workbench visibility required before enabling auto-claim outside local grey release?
7. Which repeat-failure threshold creates an Agent improvement proposal: same failure twice, same requirement twice, or same agent/tool category twice?

## 13. Risks And Rollback

| Risk | Impact | Mitigation | Rollback |
| --- | --- | --- | --- |
| Autopilot advances too many transitions | Wrong task accepted or blocked | `maxCycles`, dry-run, decision log, policy guards | Disable `--claim`; run tick in dry-run/read-only mode. |
| Lease token leaks into durable files | Runner spoofing risk | store hash/proof only; raw token returned once | Rotate lease token; expire active leases; require re-claim. |
| Stale repair reassigns active work | Duplicate execution | heartbeat grace, task version check, finish token validation | Mark task `repair_pending`; require PM manual reassign. |
| Approval hidden in sub-agent | Delivery stalls invisibly | approval preflight and `approvalRequest` blocker | Block task and return request to PM main flow. |
| PM patches after test failure | Role integrity and audit break | enforce test-failure repair rule | Create incident + Development review task; revert/repair through Development owner. |
| Missing evidence still closes task | False completion | Result Center schema + closure policy gate | Reopen task, reject result, create repair task. |
| Runner scope too broad | Unauthorized repo/tool/data access | capability/scope matcher and audit denial | Disable runner, narrow manifest, re-register. |
| External Agent Ring not ready | Auto execution blocked | manual handoff uses same lease/result contract | Continue local/manual runner grey release. |

## 14. Acceptance Checklist For This Solution

- Covers ANOS-REQ-050..056, ANOS-REQ-060..063, ANOS-REQ-070..073.
- Defines Scheduler, Runner, Agent Worker, PM Autopilot, Result Center boundaries.
- Defines state machines for task dispatch, runner, result review, test repair loop.
- Defines PM approval relay so sub-agent approval cannot stall in child window.
- Defines test-failure route back to Development Agent and retest regression.
- Defines API/CLI contracts without entering implementation.
- Defines implementation slices and test strategy.
- Lists PM/Product discussion questions and rollback plan.
