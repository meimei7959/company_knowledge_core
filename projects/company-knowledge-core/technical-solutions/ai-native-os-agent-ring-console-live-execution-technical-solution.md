---
type: Workflow
title: AI Native OS Agent Ring Console and live distributed execution technical solution
description: Technical solution for Agent Ring Console productization and live multi-runner execution evidence.
timestamp: "2026-06-21T12:45:00Z"
projectId: company-knowledge-core
taskId: kt-ai-native-os-gap-tech-agent-ring-console-live-execution
authorAgent: agent.company.development
status: draft
requirementRefs:
  - UREQ-008
  - ANOS-REQ-060
  - ANOS-REQ-061
  - ANOS-REQ-062
  - ANOS-REQ-063
acceptanceGateRefs:
  - GATE-AC-EXE-002
  - GATE-AC-EXE-003
  - GATE-AC-UI-004
sourceMaterialRefs:
  - .zhenzhi/context/task.kt-ai-native-os-gap-tech-agent-ring-console-live-execution.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-gap-tech-agent-ring-console-live-execution.md
  - projects/company-knowledge-core/product-reviews/ai-native-os-requirement-tree-final-product-acceptance.md
  - projects/company-knowledge-core/coordination/ai-native-os-full-product-gap-execution-plan.md
  - docs/protocols/agent-ring-communication-protocol.md
  - docs/architecture/central-processor-and-agent-ring.md
  - projects/company-knowledge-core/technical-solutions/ai-native-os-scheduler-runner-result.md
  - projects/company-knowledge-core/technical-solutions/ai-native-os-desktop-workbench-console.md
reviewPath:
  - Product Manager Agent product acceptance review
  - Project Manager Agent delivery review
  - Test Agent paired evidence review before implementation closeout
implementationBlockedUntilAccepted: true
---

# Agent Ring Console And Live Execution Technical Solution

## 1. Decision Summary

Build a productized Agent Ring Console on top of the existing scheduler, runner, lease, TaskResult, Notification, and AuditLog foundation. The current code proves local/manual runner workflow and a scheduler workbench read model, but Product Manager acceptance explicitly keeps UREQ-008 / ANOS-REQ-060..063 blocked because there is no complete runner registry UI/API, lease/history UI, manual handoff product flow, scope/audit UI, or live distributed Agent Ring evidence.

This solution keeps the repository boundary intact:

- Central processor owns scheduler state, task queue, runner registry, lease protocol, review gates, notifications, audit, and persisted knowledge objects.
- Agent Ring owns desktop/service implementation and local execution on distributed computers.
- Agent Ring must not bypass central task state, approval policy, writeback rules, notification, or audit.

Implementation must not start until Product Manager Agent and Project Manager Agent accept this technical solution.

## 2. Current Baseline

Existing code already provides the core runtime primitives:

- `register_agent_runner` writes `AgentRunner` records with `runnerId`, host metadata, agents, capabilities, projects, repositories, data scopes, heartbeat, `currentLeases`, `staleLeases`, `failedLeases`, `taskHistory`, and audit.
- `heartbeat_agent_runner` refreshes runner status, load, capabilities, available projects, and audit.
- `select_runner_for_task` matches task requirements to online runners.
- `claim_project_task` validates runner scope, secret readiness, environment readiness, version, and active lease before issuing a lease token, execution context, notification, and audit.
- `heartbeat_project_task_lease` exists behind `/v0/tasks/heartbeat` for active lease renewal.
- `repair_stale_task_leases` repairs expired or heartbeat-stale leases and records runner state.
- `schedule_project_tasks` can assign or claim eligible tasks and repair stale leases before scheduling.
- `run_agent_worker` can claim and submit minimal technical-solution tasks, but it is not live external Agent Ring execution.
- `finish_project_task` writes `TaskResult`, operating rule refs, common rule evaluation, quality evaluation, acceptance policy, runner lease finish history, notification, and audit.
- `/v0/scheduler/workbench`, `/v0/runners/register`, `/v0/runners/heartbeat`, `/v0/tasks/claim`, `/v0/tasks/heartbeat`, and task finish API paths exist as a foundation.

Gap: those pieces are not yet a product Agent Ring Console and do not prove two independent distributed computers executing tasks end-to-end through claim, heartbeat, cancel, retry, finish, TaskResult, AgentRun, Notification, and AuditLog.

## 3. Requirement Coverage

| Requirement | Product capability | Acceptance evidence |
| --- | --- | --- |
| ANOS-REQ-060 | Runner Registry Console: register, authorize, inspect, disable, and scope Agent Ring runners. | Console screen and API evidence for at least two registered runners, each with host identity, capabilities, projects, repo scopes, data scopes, heartbeat, health proof, and audit trail. |
| ANOS-REQ-061 | Lease and execution history: queue, assigned runner, active lease, heartbeat, attempt, stale repair, cancel, retry, finish history. | End-to-end event timeline showing claim, heartbeat, stale detection, cancel, retry, finish, TaskResult, AgentRun, NotificationRecord, and AuditLog. |
| ANOS-REQ-062 | Manual handoff: human-readable handoff from Console to an operator or runner, with central state and audit preserved. | Manual handoff UI/API changes task to handoff state, sends notification, records handoff summary, and resumes through approved runner claim or explicit human closeout. |
| ANOS-REQ-063 | Scope and audit: prevent unauthorized runner/task access and expose readable audit. | Negative tests for project/repo/data/tool scope denial; Console shows who/what/when/why and masks secrets while linking audit refs. |

These requirements remain blocked until live evidence uses at least two independent `AgentRunner` records or equivalent real distributed execution. Two tabs or two simulated processes on the same local runtime are not enough for final product acceptance unless Product Manager explicitly accepts them as equivalent.

## 4. Target Architecture

### 4.1 Components

- Agent Ring Console: central UI for runner registry, queue, leases, task history, manual handoff, scope readiness, and audit.
- Central Agent Ring API: authenticated HTTP endpoints for Console and Agent Ring nodes.
- Scheduler core: existing matching, lease, stale repair, retry, and result writeback logic.
- Agent Ring runner service: external process on each distributed computer. It registers, heartbeats, claims tasks, pulls context, executes locally, writes AgentRun and TaskResult, and reports artifacts.
- Operational store: PostgreSQL-backed runtime tables for live sessions, with Git bundle object writeback as durable review/audit evidence. For current repository implementation, file-backed storage remains supported behind the same API contract.

### 4.2 Data Flow

1. Runner registers with host identity, runner version, supported agents, capabilities, project scopes, repository scopes, data scopes, tool scopes, and health proof.
2. Console shows runner registry and queue readiness from central read model.
3. Scheduler assigns or runner claims a task only if scope, capability, credential readiness, environment readiness, and active lease checks pass.
4. Agent Ring pulls generated context after claim with a valid lease token.
5. Runner heartbeats while executing; task lease heartbeat updates separate from runner heartbeat.
6. Runner writes `AgentRun` draft/start event when execution begins.
7. Runner finishes through central API, which validates lease proof and writes `TaskResult`, `AgentRun`, `NotificationRecord`, `AuditLog`, and runner task history.
8. Product/PM/Test review sees the same timeline in Console and object refs in Git bundle.

## 5. API Contract

Keep existing endpoints and add product-specific Agent Ring Console routes. Every mutation must require actor, runner, idempotency key, source channel, and audit reason.

### 5.1 Runner Registry

- `GET /v0/agent-ring/runners?projectId=...`
  - Returns runners, status, lastHeartbeatAt, capabilities, project scopes, repo scopes, data scopes, current leases, task history summary, health proof status, last audit refs.
- `POST /v0/runners/register`
  - Existing route remains.
  - Add `machineFingerprint`, `agentRingVersion`, `toolScopes`, `credentialReadinessRefs`, `healthProof`, `displayLocation`, `operatorContactRef`.
- `POST /v0/runners/heartbeat`
  - Existing route remains.
  - Add `load`, `runningTaskIds`, `disk/network/model readiness`, and optional degraded reason.
- `POST /v0/agent-ring/runners/disable`
  - Sets runner offline/degraded, cancels or drains current leases by policy, writes notification and audit.

### 5.2 Queue And Lease Lifecycle

- `GET /v0/agent-ring/queue?projectId=...`
  - Returns pending, waiting_runner, processing, blocked, changes_requested, waiting_acceptance.
- `POST /v0/tasks/claim`
  - Existing route remains.
  - Must validate project/repo/data/tool scope, secret readiness, env readiness, task version, and no conflicting lease.
- `POST /v0/tasks/heartbeat`
  - Existing route remains.
  - Extends lease if valid; rejects stale token or wrong runner.
- `POST /v0/agent-ring/tasks/cancel`
  - Marks cancel requested, notifies runner/operator, writes audit.
  - If runner acknowledges, releases lease and moves task to `blocked`, `changes_requested`, or `pending` by reason.
- `POST /v0/agent-ring/tasks/retry`
  - Creates retry attempt, increments attempt, clears stale lease fields, links previous TaskResult/AgentRun, writes notification and audit.
- `POST /v0/tasks/finish`
  - Existing finish path remains the authoritative writeback.
  - Requires lease proof unless authorized manual closeout path is used.

### 5.3 AgentRun Writeback

Add central writeback endpoints:

- `POST /v0/agent-runs/start`
  - Creates AgentRun with taskId, runnerId, executorAgent, leaseProofHash, contextRef, startedAt, status `running`.
- `POST /v0/agent-runs/event`
  - Appends structured events: context_pulled, command_started, command_finished, artifact_written, notification_sent, cancel_seen, error.
- `POST /v0/agent-runs/finish`
  - Finalizes AgentRun and links TaskResult.

`TaskResult` remains the task closure object. `AgentRun` is execution evidence and must never be used alone as reusable knowledge.

### 5.4 Console Read Model

Extend `scheduler_workbench_read_model` or add `agent_ring_console_read_model`:

- `runners[]`
- `queue[]`
- `activeLeases[]`
- `leaseHistory[]`
- `manualHandoffs[]`
- `scopeReadiness[]`
- `notifications[]`
- `auditTrail[]`
- `acceptanceEvidence[]`

The read model must resolve human-readable names and labels, not only raw IDs.

## 6. Console UX

The Console is an operational tool, not a marketing page.

### 6.1 Runner Registry View

Columns:

- Runner name, runnerId, host type, machine fingerprint status.
- Agent Ring version and compatible API version.
- Online/degraded/offline status and heartbeat age.
- Supported agents and capabilities.
- Project/repo/data/tool scopes.
- Current leases and load.
- Last health check and last audit event.

Actions:

- Register runner.
- Disable runner.
- Refresh heartbeat.
- View scope diagnostics.
- View task history.

### 6.2 Queue And Lease View

Shows task cards or table rows with:

- task title, taskId, requirement refs, priority, stage.
- assignedRunner, leaseOwner, leaseExpiresAt, leaseHeartbeatAt, attempt.
- environment readiness and missing requirements.
- next action: claim, cancel, retry, manual handoff, open result.

### 6.3 Execution Timeline

For each task:

- claim event.
- context pull event.
- runner heartbeat and lease heartbeat.
- AgentRun events.
- cancel/retry/stale events.
- finish event.
- TaskResult, NotificationRecord, AuditLog refs.

### 6.4 Manual Handoff Panel

Manual handoff must show:

- reason.
- handoffTo.
- readable instructions.
- allowed runner scopes.
- expected writeback command.
- explicit risk and acceptance path.

Manual handoff must not mutate private runner state directly. It writes central handoff state, notification, and audit, then the receiving runner or human closes through approved API/CLI.

### 6.5 Scope And Audit Panel

Shows:

- project scope.
- repository scope.
- data scope.
- tool scope.
- credential readiness refs.
- denied claims with reason.
- AuditLog timeline with actor, source channel, policy result, object ref, before/after, and readable summary.

Secrets are never displayed. Secret refs and credential readiness status are displayable.

## 7. State Machine

### 7.1 Normal Execution

`pending -> waiting_runner -> processing -> waiting_acceptance -> done`

Required write events:

- assign: Notification + AuditLog.
- claim: lease token, contextRef, Notification + AuditLog, runner currentLeases.
- AgentRun start: AgentRun + AuditLog.
- heartbeat: task lease heartbeat + runner heartbeat audit sampling.
- finish: TaskResult + AgentRun finish + Notification + AuditLog + runner taskHistory.

### 7.2 Stale Lease

`processing -> waiting_runner` or `processing -> blocked`

Policy:

- If heartbeat missing and no critical side effect is in progress, release lease to `waiting_runner`.
- If critical external side effect may be in progress, move to `blocked` with manual PM review.
- Always record stale lease in runner `staleLeases`, task history, Notification, and AuditLog.

### 7.3 Cancel

`processing -> cancel_requested -> blocked|pending|changes_requested`

Policy:

- Console cancel records central intent first.
- Runner acknowledges cancel on next heartbeat or finish.
- If runner is unreachable, stale lease repair handles recovery.
- Cancel never deletes TaskResult/AgentRun; it finalizes AgentRun as `cancelled` or `interrupted`.

### 7.4 Retry

`blocked|changes_requested|waiting_runner -> pending|processing`

Policy:

- Retry creates new attempt and links prior task result/run.
- Retry reason, requester, old runner, new runner, and changes requested are audited.
- Max attempts come from task runtime; exceeding max attempts requires PM/human decision.

### 7.5 Manual Handoff

`waiting_runner|blocked|changes_requested -> handoff_requested -> waiting_runner|processing`

Policy:

- Handoff has readable instructions and target role/runner.
- Handoff cannot bypass scope checks.
- Handoff creates Notification and AuditLog before any runner claim.

## 8. Implementation Slices And Paired Test Tasks

### Slice 0: Contract And Traceability Freeze

Implementation task: `kt-ai-native-os-impl-agent-ring-contract-read-model`

- Add final Agent Ring Console API contract docs and route envelope schemas.
- Add traceability mapping from UREQ-008 / ANOS-REQ-060..063 to slices, tests, and acceptance gates.
- Confirm Product/PM accepted scope before code work starts.

Paired test task: `kt-ai-native-os-test-agent-ring-contract-read-model`

- Validate schema fields, source refs, requirement refs, and acceptance gate refs.
- Negative check: implementation cannot close without Product/PM review refs.

### Slice 1: Runner Registry API And Scope Model

Implementation task: `kt-ai-native-os-impl-agent-ring-runner-registry-scope`

- Extend `AgentRunner` schema with machine fingerprint, health proof, tool scopes, credential readiness refs, and operator contact.
- Harden register/heartbeat/disable endpoints.
- Enforce project/repo/data/tool scopes in claim path.

Paired test task: `kt-ai-native-os-test-agent-ring-runner-registry-scope`

- Unit tests for register/upsert/heartbeat/disable.
- Negative claim tests for wrong project, repo, data scope, tool scope, missing secret readiness, missing env var.
- Audit and notification assertions for blocked claims.

### Slice 2: Console Read Model And Runner Registry UI

Implementation task: `kt-ai-native-os-impl-agent-ring-console-registry-ui`

- Add `agent_ring_console_read_model`.
- Build Runner Registry, Queue, Lease, Manual Handoff, Scope/Audit views.
- Keep Desktop Workbench read model compatibility.

Paired test task: `kt-ai-native-os-test-agent-ring-console-registry-ui`

- Snapshot/read-model tests for runners, queue, active leases, scope readiness, audit refs.
- UI route tests for empty, ready, degraded, waiting_runner, processing, blocked, stale states.

### Slice 3: Lease Lifecycle API

Implementation task: `kt-ai-native-os-impl-agent-ring-lease-lifecycle`

- Add cancel and retry endpoints.
- Harden claim/heartbeat/finish idempotency and stale token rejection.
- Ensure stale repair records runner `staleLeases`, task state, Notification, AuditLog, and retry readiness.

Paired test task: `kt-ai-native-os-test-agent-ring-lease-lifecycle`

- Claim, heartbeat, stale repair, cancel, retry, finish lifecycle tests.
- Race tests for expected task version and conflicting lease owner.
- Idempotency tests for duplicate claim/finish/cancel/retry.

### Slice 4: AgentRun And TaskResult Writeback

Implementation task: `kt-ai-native-os-impl-agent-ring-agentrun-taskresult`

- Add AgentRun start/event/finish writeback.
- Link AgentRun to TaskResult and TaskResult back to AgentRun.
- Enforce `operatingRuleRefs`, `commonRulesEvaluation`, `qualityEvaluation`, acceptance policy, Notification, and AuditLog on every finish.

Paired test task: `kt-ai-native-os-test-agent-ring-agentrun-taskresult`

- Finish path tests for done, submitted, blocked, rejected, cancelled.
- Verify AgentRun, TaskResult, NotificationRecord, AuditLog, runner taskHistory, and task resultRef are all present.
- Verify reusable knowledge is not auto-promoted.

### Slice 5: Manual Handoff Product Flow

Implementation task: `kt-ai-native-os-impl-agent-ring-manual-handoff`

- Add handoff request and accept/decline endpoints.
- Add Console handoff panel and notification template.
- Preserve central state and scope checks during handoff.

Paired test task: `kt-ai-native-os-test-agent-ring-manual-handoff`

- Handoff from blocked/waiting_runner to target role.
- Claim after handoff by authorized runner.
- Decline/timeout path with notification and audit.

### Slice 6: Live Two-Runner Execution Harness

Implementation task: `kt-ai-native-os-impl-agent-ring-live-two-runner-harness`

- Register `runner.meimei-mac-local-dev-rt` and one independent second runner, for example `runner.lighthouse-cloud-dev-rt`, or another Product Manager accepted real distributed runner.
- Run two different tasks through central API from separate hosts or equivalent real distributed execution environment.
- Capture signed evidence: runner registration, heartbeat, claim, context pull, AgentRun, finish, TaskResult, Notification, AuditLog.

Paired test task: `kt-ai-native-os-test-agent-ring-live-two-runner-harness`

- Live E2E test for two runners.
- One stale/cancel/retry scenario.
- One successful finish scenario.
- Evidence package attached to PM review.

### Slice 7: Product Acceptance Evidence Pack

Implementation task: `kt-ai-native-os-impl-agent-ring-acceptance-evidence-pack`

- Generate acceptance evidence matrix for ANOS-REQ-060..063.
- Link implementation results, test results, Console screenshots, API responses, AgentRun refs, TaskResult refs, Notification refs, and AuditLog refs.

Paired test task: `kt-ai-native-os-test-agent-ring-acceptance-evidence-pack`

- Validate each acceptance gate has concrete evidence.
- Verify no requirement is promoted to complete from inferred backfill only.
- Submit to Product Manager Agent and Project Manager Agent review.

## 9. Environment Readiness

Required before implementation closeout:

- Central API reachable from every runner over authenticated HTTPS or accepted local secure tunnel.
- API token or approved credential reference for each runner; no raw secret in repository.
- PostgreSQL operational store available for live runtime acceptance, or explicit Product Manager waiver accepting file-backed store for this phase.
- Two independent runner environments:
  - runner A: `runner.meimei-mac-local-dev-rt`.
  - runner B: a second physical/virtual host, for example `runner.lighthouse-cloud-dev-rt`, or another accepted distributed computer.
- Each runner has:
  - synchronized clock.
  - matching Agent Ring API version.
  - repo checkout or declared repository access.
  - executor agent availability.
  - required CLI/tools.
  - environment variables configured through runner-local secret manager.
  - network path to central API.
  - write permission only through central API/approved CLI.
- Feishu/Lark notification live path ready for delivery evidence, callback/error recovery, and user-readable feedback.
- Audit storage writable and searchable.
- Acceptance evidence directory or review record target agreed by PM and Test Agent.

Readiness gate:

- If second runner or live notification path is unavailable, implementation may land behind disabled feature flags, but ANOS-REQ-060..063 must remain blocked.

## 10. Rollback Plan

Feature flags:

- `AGENT_RING_CONSOLE_ENABLED`
- `AGENT_RING_LIVE_CLAIM_ENABLED`
- `AGENT_RING_CANCEL_RETRY_ENABLED`
- `AGENT_RUN_WRITEBACK_ENABLED`

Rollback steps:

1. Disable live claim flag; Console becomes read-only.
2. Disable cancel/retry mutations; only PM/manual CLI repair remains.
3. Mark degraded/offending runners offline and drain current leases.
4. Run stale lease repair to return safe tasks to `waiting_runner` or `blocked`.
5. Preserve TaskResult, AgentRun, NotificationRecord, and AuditLog; never delete execution evidence.
6. Restore previous route behavior from Git revert or deployment rollback.
7. Notify project owner and affected task requesters with readable reason and next action.

Data rollback:

- New runtime fields are additive.
- If PostgreSQL runtime store fails, central API falls back to file-backed bundle only when Product Manager accepts reduced live evidence status.
- Any partial AgentRun remains linked as `interrupted` or `failed`, not removed.

## 11. Out Of Scope

- Building the full external Agent Ring desktop/service implementation inside this repository.
- Storing raw secrets, tokens, or passwords in knowledge files.
- Promoting ANOS-REQ-060..063 to complete without live two-runner evidence.
- Replacing Product Manager or Project Manager review with automated acceptance.
- Direct distributed execution by the central processor; central schedules and records, Agent Ring executes.

## 12. Acceptance Checklist

Product Manager review can accept this technical solution when it agrees that:

- All ANOS-REQ-060..063 gaps are covered by named implementation slices.
- Every implementation slice has a paired test task.
- Claim, heartbeat, stale, cancel, retry, finish, TaskResult, AgentRun, Notification, and AuditLog are all in scope.
- Runner registry, lease/history, manual handoff, scope/audit UI and API are all in scope.
- Environment readiness explicitly requires two independent runners or Product Manager accepted equivalent real distributed execution.
- Rollback keeps audit evidence and does not erase work state.

Implementation can start only after this solution receives Product Manager Agent and Project Manager Agent acceptance.
