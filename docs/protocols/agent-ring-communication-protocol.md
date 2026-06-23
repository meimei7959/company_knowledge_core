# Agent Ring Communication Protocol

## Purpose

Agent Ring is the external Agent workstation that connects distributed computers to the central processor.

This repository does not implement Agent Ring. This repository defines the central contract that Agent Ring must follow:

- register each computer as an execution node;
- register the Agents, tools, models, repositories, and permissions available on that node;
- receive or pull tasks from the scheduler;
- claim tasks with a lease;
- run local Codex, Claude, local models, browsers, scripts, or other approved tools;
- write back TaskResult, AgentRun, artifacts, evidence, and status;
- heartbeat so the scheduler knows which distributed processors are online.

## System Roles

```txt
Agent Hub
  Human or Agent-facing entrypoint. Creates projects, source materials, and tasks.

Central Processor
  This project. Owns scheduler state, knowledge state, task queues, runner registry, protocol, review, audit, and notifications.

Agent Scheduler
  Central component. Matches tasks to Agent Ring nodes by capability, permission, resource, data locality, and load.

Knowledge Core
  Central memory. Stores Project, ProjectTask, KnowledgeTask, SourceMaterial, TaskResult, KnowledgeItem, ToolAsset, Agent, AgentRunner, AuditLog.

Agent Ring
  External workstation runtime. Runs on each computer. Registers local Agents and capabilities, executes assigned tasks, and writes results back.

Distributed Computer
  Physical or virtual machine where Agent Ring runs.
```

## Boundary

Central Processor owns:

- task lifecycle and state machine;
- project/task context bundle contract;
- runner registration schema;
- capability taxonomy;
- scheduler decision records;
- task lease and heartbeat contract;
- writeback schema;
- audit and review gates;
- notification triggers.

Agent Ring owns:

- desktop/service implementation;
- local process supervision;
- local Codex / Claude / model / tool invocation;
- local filesystem, repository, and browser integration;
- local logs and crash recovery;
- user or unattended execution mode.

The central processor must not assume how Agent Ring is implemented. Agent Ring must not bypass central task state, approval policy, writeback rules, or audit.

## Task Context Pull

Agent Ring pulls task context through the central API after it owns a valid lease:

```txt
POST /v0/tasks/pull
```

Request:

```json
{
  "taskId": "KT-20260618-001",
  "runnerId": "runner.mac-mini-01",
  "leaseToken": "<lease token>"
}
```

Response includes both a human-readable context pack and a structured `projectContextBundle`:

```json
{
  "kind": "TaskContext",
  "task": {},
  "projectContextBundle": {
    "project": {},
    "task": {},
    "knowledge": {},
    "executionHistory": {},
    "handoff": {}
  },
  "contextRef": ".zhenzhi/context/task.kt-20260618-001.md",
  "context": "# Current Task Context..."
}
```

The text context helps Codex, Claude, or local models read the job. The structured bundle helps Agent Ring move work between computers without asking the user to repeat project history.

## Runner Registration

Agent Ring registers each computer as an `AgentRunner`.

Required fields:

```yaml
runnerId: runner.mac-mini-01
ringVersion: 0.1.0
hostName: mac-mini-01
hostType: macos
status: online
mode: unattended
capabilities:
  - codex_cli
  - claude_cli
  - local_model:qwen3-8b
  - git
  - browser_automation
  - feishu_doc_read
agents:
  - agent.knowledge-steward
  - agent.backend-dev
availableProjects:
  - company-knowledge-core
repoAccess:
  - company_knowledge_core
dataScopes:
  - company_internal
resource:
  cpu: 10
  memoryGb: 24
  gpu: apple
load:
  activeTasks: 0
  queueDepth: 0
lastHeartbeatAt: 2026-06-18T00:00:00Z
```

Rules:

- Registration is a claim, not proof. The scheduler should verify critical capabilities through health checks.
- Capability and permission are separate. A runner can have `git` capability but still lack permission to write a specific repository.
- Secrets stay in Agent Ring or a secure secret manager. The central processor stores secret references only.

## Task Matching

Task cards should declare execution needs:

```yaml
taskId: KT-20260618-001
taskType: knowledge_capture
requiredCapabilities:
  - feishu_doc_read
  - long_context_summary
  - knowledge_structuring
requiredAgents:
  - agent.knowledge-steward
allowedDataScopes:
  - company_internal
preferredRunner:
assignedRunner:
leaseOwner:
leaseExpiresAt:
status: pending
```

Scheduler matching inputs:

- task type;
- required capabilities;
- required Agents;
- project/repository/data permissions;
- source material location;
- runner status and heartbeat;
- runner load;
- failure and retry history;
- cost or model preference.

## Task State Machine

Current MVP state machine:

```txt
pending
-> processing
-> done

blocked and rejected may be entered when execution cannot proceed.
```

Current MVP mapping:

- `pending`: task exists and can be discovered by Agent Ring.
- `processing`: Agent Ring, StubRunner, or local Codex has pulled the task context and is responsible for writeback.
- `done`: TaskResult has been written and notification/review can continue.
- `blocked`: missing capability, permission, source, or runtime condition.
- `rejected`: task should not be executed or stored.

Lease-aware state machine:

```txt
pending
-> waiting_runner
-> processing
-> waiting_acceptance
-> done

processing may also enter changes_requested, blocked, or rejected.
changes_requested and blocked may return to pending, waiting_runner, or processing after repair.
```

State meaning:

- `pending`: task exists and can be discovered.
- `waiting_runner`: task is ready but no Runner is currently handling it.
- `processing`: Agent Ring accepted the task, owns the lease, and is executing or preparing writeback.
- `waiting_acceptance`: TaskResult passed machine checks and is waiting for project-manager or human acceptance.
- `changes_requested`: TaskResult needs repair or rework.
- `done`: task is complete and notification can be sent.
- `blocked`: missing capability, permission, source, or runtime condition.
- `rejected`: task should not be executed or stored.

## Lease And Heartbeat

MVP:

- Runner heartbeat is supported at runner level.
- Task pull currently moves a task from `pending` to `processing`.
- The central processor records audit logs for runner registration, runner heartbeat, task claim, task heartbeat, task pull, and task finish.
- The central processor returns lease token to Agent Ring at claim time, but stores only `leaseProofHash`, not the plaintext token.

Current lease contract:

Agent Ring should claim work with a lease:

```yaml
leaseOwner: runner.mac-mini-01
leaseToken: lease.20260618T000000Z.abc123
leaseExpiresAt: 2026-06-18T00:10:00Z
heartbeatAt: 2026-06-18T00:01:00Z
```

Rules:

- A runner may execute only while it owns a valid lease.
- Heartbeat extends or confirms the lease.
- If heartbeat expires, scheduler may release or reassign the task.
- Writes without the current lease token must be rejected.

## Writeback Contract

Agent Ring writes back:

- TaskResult;
- AgentRun;
- artifact refs;
- evidence refs;
- SourceMaterial extraction refs;
- KnowledgeItem drafts if knowledge was produced;
- status transition request;
- logs as storage refs, not large inline dumps.

TaskResult must include:

```yaml
taskId: KT-20260618-001
runnerId: runner.mac-mini-01
executorAgent: agent.knowledge-steward
result: done
summary: ...
outputRefs: []
knowledgeRefs: []
sourceMaterialRefs: []
evidenceRefs: []
logsRef: storage://...
completedAt: 2026-06-18T00:00:00Z
```

`ProjectTask.status` is not the same field as `TaskResult.result`. The task routing status must remain one of `pending`, `waiting_runner`, `processing`, `waiting_acceptance`, `changes_requested`, `blocked`, `done`, or `rejected`. Do not write lease names, result names, quality decisions, or human-acceptance policy values into `ProjectTask.status`.

Knowledge rules:

- Raw material remains SourceMaterial.
- AI summaries must cite SourceMaterial or evidence refs.
- KnowledgeItem starts as draft/observed.
- verified, approved, active, permissions, secrets, and customer commitments require review or approval.

## Minimum API Surface

Implemented MVP HTTP endpoints:

```txt
POST /v0/runners/register
POST /v0/runners/heartbeat
GET  /v0/runners
GET  /v0/tasks?status=<status>&assignee=<runnerId>&projectId=<projectId>&taskType=<taskType>
GET  /v0/tasks/<taskId>
POST /v0/tasks/claim
POST /v0/tasks/heartbeat
POST /v0/tasks/pull
POST /v0/tasks/finish
POST /v0/tasks/cancel
POST /v0/tasks/retry
POST /v0/tasks/handoff
```

`POST /v0/runners/register` request:

```json
{
  "runnerId": "runner.mac-mini",
  "name": "Mac mini Runner",
  "hostType": "macos",
  "mode": "unattended",
  "agents": ["codex"],
  "capabilities": ["knowledge_capture"],
  "availableProjects": ["core"],
  "repoAccess": [],
  "dataScopes": [],
  "ringVersion": "0.1.0"
}
```

`POST /v0/runners/heartbeat` request:

```json
{
  "runnerId": "runner.mac-mini",
  "status": "online",
  "load": "0"
}
```

`GET /v0/runners` returns registered runner state for the Agent Ring Console and scheduler workbench read model. The response includes runner identity, status, mode, capabilities, available projects, heartbeat/load fields, current work, and metrics where available. It is a central read model of runner records and leases; it is not proof that separate physical or virtual computers are actually supervised by Agent Ring.

`POST /v0/tasks/pull` request:

```json
{
  "taskId": "KT-20260618-001",
  "runnerId": "runner.mac-mini",
  "leaseToken": "lease token returned by claim"
}
```

Response includes:

```json
{
  "kind": "TaskContext",
  "contextRef": ".zhenzhi/context/task.kt-20260618-001.md",
  "context": "portable task context markdown",
  "task": {
    "taskId": "KT-20260618-001",
    "status": "processing"
  }
}
```

`POST /v0/tasks/finish` request:

```json
{
  "taskId": "KT-20260618-001",
  "result": "done",
  "runnerId": "runner.mac-mini",
  "leaseToken": "lease token returned by claim",
  "executorAgent": "agent.codex.local",
  "summary": "What changed and why it is complete.",
  "outputRefs": [],
  "knowledgeRefs": [],
  "evidenceRefs": ["projects/core/sources/source.20260618T000000Z.md"],
  "testsOrChecks": ["deterministic stub runner writeback"],
  "nextActions": []
}
```

Task lifecycle control endpoints:

```txt
POST /v0/tasks/cancel
POST /v0/tasks/retry
POST /v0/tasks/handoff
```

Control requests identify the task, actor, and reason. Lease-scoped flows must preserve current lease and audit semantics.

`cancel` moves a cancellable task out of active execution and records the cancellation reason. `retry` returns eligible failed, blocked, cancelled, or changes-requested work to an executable routing state with retry history preserved. `handoff` records manual handoff intent, target Agent or runner context when supplied, and the reason another executor should continue the work.

MVP idempotency and safety:

- `register` is upsert by `runnerId`; repeated registration updates title, agents, capabilities, project availability, repo access, data scopes, mode, and heartbeat timestamp.
- `heartbeat` is safe to repeat and updates runner status, load, capabilities, and project availability.
- `GET /v0/runners` is read-only and should expose central runner/task read state without mutating leases, task status, or TaskResult records.
- `claim` rejects stale task versions, active leases owned by another runner, missing runner capabilities, missing project availability, and missing `secretRef` readiness.
- `pull` and `finish` reject expired leases, invalid lease tokens, or writebacks from a runner that does not own the lease.
- `pull` requires the current lease token when a task has been claimed, creates a fresh portable context pack, and records audit.
- `finish` requires the current lease token when a task has been claimed, writes exactly one TaskResult for the task id, and links it from the task.
- `cancel`, `retry`, and `handoff` must preserve audit history, lease history, and human-readable reason fields so PM and Agent handoff review can reconstruct why the task left the previous executor state.
- Expired leases can be claimed by another runner, which supports computer-to-computer reassignment.

Tested local lifecycle evidence:

- Local dual-runner equivalent tests cover runner registry/read model, current work, CLI cancel/retry/handoff, HTTP `GET /v0/runners`, HTTP `POST /v0/tasks/cancel|retry|handoff`, lease history, manual handoff, scope audit, audit trail, metrics, stale lease repair, retry lifecycle, finish permission regression, repository validation, and scoped diff checking.
- This evidence verifies central processor behavior under local equivalent runner scenarios.
- It does not prove real distributed Agent Ring runtime properties such as separate host identity, network interruption behavior, cross-machine filesystem boundaries, or real Agent Ring process supervision.

Future API endpoints:

```txt
POST /v0/tasks/<taskId>/status
GET  /v0/projects/<projectId>/context
GET  /v0/projects/<projectId>/environment
```

Future idempotency requirements:

- result writeback accepts an idempotency key from Agent Ring.

## Context Sync

Agent Ring must not rely on hidden local state from one computer. Before execution or reassignment, it should pull a portable context bundle from the central processor.

The bundle includes project state, task state, source and evidence refs, relevant knowledge, decisions, recent TaskResults, AgentRuns, required tools, repository refs, environment requirements, secret refs, and handoff notes.

Detailed contract: [Project Context Sync Protocol](project-context-sync-protocol.md).

## MVP Flow

```txt
Agent Hub creates KnowledgeTask
-> Scheduler marks task pending
-> Agent Ring registers or heartbeats runner
-> Agent Ring lists matching tasks through /v0/tasks
-> Agent Ring pulls task context through /v0/tasks/pull
-> Agent Ring runs local Codex / Claude / model / tool
-> Agent Ring writes TaskResult and artifacts through /v0/tasks/finish
-> Knowledge Review gates knowledge drafts
-> Agent Hub notifies result
```

## Open Decisions

- Whether first implementation is pull-based only or also supports scheduler push.
- Exact authentication method for Agent Ring.
- Whether runner health checks are initiated by central processor or self-reported by Agent Ring.
- How Agent Ring launches Codex / Claude in unattended mode.
- Artifact storage target for large logs and generated files.
