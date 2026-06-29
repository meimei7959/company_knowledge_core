# Task Dispatch Model

## Purpose

The scheduler matches tasks from the central processor to external Agent Ring runners.

It does not execute work directly. It decides which distributed computer should execute a task.
The execution pool is made of distributed Agent Ring runners registered from external computers.

## Inputs

- ProjectTask / KnowledgeTask.
- SourceMaterial.
- requiredCapabilities.
- requiredAgents.
- project and data permissions.
- AgentRunner registry.
- runner heartbeat and load.
- retry and failure history.
- risk level and approval policy.

## Outputs

- assignedRunner.
- executorAgent.
- lease fields.
- scheduler decision record.
- updated task status.

## Dispatch Modes

### Short Term: Pull Matching

Each Agent Ring runner polls for tasks it can handle.

```txt
runner heartbeat
-> runner polls pending tasks
-> central processor filters by capability and permission
-> runner claims one task
```

This is simple and resilient while the system is small.

### Mid Term: Central Assignment

The scheduler actively assigns tasks to runners.

```txt
pending task
-> scheduler ranks runners
-> assignedRunner set
-> runner claims assigned task
```

This supports load balancing, priority, and retry policies.

### Long Term: Agent Compute Network

The scheduler manages a distributed Agent compute network:

- capacity planning;
- model/tool routing;
- data locality;
- cost-aware scheduling;
- automatic retry and failover;
- compatibility checks between task, Agent, tool, and runner.

## Dispatch Requirements

Every dispatched task must have:

- taskId;
- taskType;
- taskRuntime;
- executionContract with a fresh sourceFactsHash when taskRuntime requires it;
- status;
- requiredCapabilities;
- lease owner/token/expiry after claim;
- audit trail;
- clear writeback contract.

`taskRuntime` is the scheduler's normalized task contract. It is produced before dispatch and contains:

- category;
- qualityGate;
- acceptancePath;
- executionContractRequired and executionContractFreshnessRequired;
- requiresSourceMaterial;
- requiresKnowledgeDraft;
- requiresTests.

The scheduler must use `taskRuntime` instead of guessing from title text. Engineering tasks are evaluated by engineering/test evidence, not by KnowledgeItem draft requirements. Knowledge capture tasks are evaluated by SourceMaterial, KnowledgeItem draft, and review path. Project initialization tasks are evaluated by launch context, runner/manual handoff, first task list, and PM review.

`executionContract` is the runner-facing closure contract generated from the task facts and normalized runtime. If source material, expected output, linked requirement/defect refs, handoff contract, or runtime constraints change, the runner or project manager must refresh it with `zhenzhi-knowledge task contract <task-id>` before execution or closure. `TaskResult.executionContractEvaluation` records whether the result came from the current task facts.

Project initialization tasks additionally require:

- `taskType: project_initialization`;
- assignee set to `agent.<project>.project-manager`;
- required capabilities including `project_initialization`, `git`, `knowledge_sync`, and local execution capability;
- `launch.md` as a source material or context reference;
- repo mode and repo reference, or an explicit blocker when they are missing;
- Runner assignment, runner lease metadata, or `waiting_runner`;
- `TaskResult` writeback contract with evidence, blockers, risks, and next action.
- startup milestones M0-M3; no guessed product roadmap milestones.
- first `ProjectTask` list or a blocker explaining why first tasks cannot be created yet.

Project initialization is not complete when the task is merely created. It is complete only after the Project Manager Agent or its runner writes the result and the requester/project owner receives the status.

After initialization result writeback, scheduler flow continues by dispatching the first ProjectTasks. Common first tasks are repository setup, implementation planning, material ingest, tool/skill request, permission request, product discovery, or review preparation. Product discovery is dispatched only when the project has a Product Manager Agent or explicit human product owner. If intake says product work is already clear or not needed, the scheduler skips product discovery and keeps the skip reason from `launch.md`; it does not create a separate confirmation task. Each first task still follows normal claim, lease, result, notification, and review rules.

Project Manager Agent initialization result evaluation:

- `pass`: launch, owner/approval, repo path, Agent team, group, Runner/manual handoff, risks, and first ProjectTasks are explicit.
- `blocked`: repo access, project Owner, approval, Runner, or required launch context is missing and no safe manual handoff exists.
- `needs_human_approval`: repo creation, permissions, member invitations, customer commitments, policy changes, or high-risk tools are required.
- `needs_repair`: TaskResult, AgentRun/manual handoff record, notification, audit trail, first task list, or launch status is missing or inconsistent.

## Project Follow-Up Dispatch

After initialization, Scheduler should treat Project Manager Agent follow-up as a recurring project-health task.

Inputs:

- active ProjectTasks and KnowledgeTasks;
- TaskResult status and age;
- Runner lease, heartbeat, retry, and failure history;
- approval state;
- Review queue state;
- project group and notification delivery state;
- milestone and due/review dates from `launch.md`, project updates, or task cards.

Follow-up outputs:

- project state: `on_track`, `at_risk`, `blocked`, or `needs_decision`;
- updated next actions;
- new follow-up ProjectTasks;
- repair/retry tasks when output quality is insufficient;
- alert notification when risk crosses threshold;
- Decision or approval request when human ownership is required.

Risk thresholds:

- Any critical-path task without owner or next action -> `at_risk`.
- Any stale Runner lease or failed notification on a critical task -> alert Project Manager Agent and Knowledge Engineering Agent ops sub-agent.
- Any task blocked by approval, repo access, permission, product decision, or customer input -> `needs_decision` or `blocked`.
- Any rejected Review, repeated repair, missing evidence, or missing test/check -> `needs_repair`.
- Any unapproved scope/date/customer/security change -> human approval before dispatch.

## Scheduler Tick

The scheduler must run a repeatable tick instead of relying on humans to notice pending files.

```txt
TaskResult handoff_ready + accepted/auto_accepted
-> release follow-up ProjectTask when missing
-> scan pending / waiting_runner ProjectTasks
-> match eligible online AgentRunner
-> assign Runner or claim with lease when requested
-> if no Runner matches, set waiting_runner and notify owner / Project Manager Agent
```

CLI:

```bash
zhenzhi-knowledge scheduler tick --project <project-id>
zhenzhi-knowledge scheduler tick --project <project-id> --claim
```

The tick is intentionally not a hidden code executor. It advances orchestration state:

- creates missing follow-up tasks from accepted handoff-ready results;
- assigns eligible runners;
- optionally claims tasks and creates leases/context handoff;
- marks un-runnable work as `waiting_runner`;
- creates notifications and audit records.

Actual implementation, testing, approval, release, and external side effects still happen through the assigned runner, TaskResult writeback, review gates, and approval paths.

This closes the product-manager-to-project-manager handoff:

```txt
Product Manager Agent writes accepted handoff-ready product package
-> Scheduler tick releases Project Manager Agent follow-up task
-> Scheduler tick assigns or claims eligible Project Manager Runner
-> Project Manager Agent writes execution plan and downstream task queue
-> Scheduler tick dispatches downstream tasks or marks them waiting_runner
```

## Risk Rules

- Low-risk knowledge capture may be auto-executed by eligible runners.
- Engineering actions may be auto-prepared and executed only when policy allows.
- Permission, token, customer commitment, deletion, and verified publication tasks require review or approval.
- Project initialization may prepare repo/group/Agent/team actions before approval, but external side effects such as creating a repo, changing permissions, or inviting members require the configured approval path.
