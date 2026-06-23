# Knowledge Ingest Orchestration Workflow

This workflow makes knowledge recording a closed production line instead of a single Agent action.

It applies to material received from Feishu bot, CLI, API, Agent Ring, or manual local runner.

## Goal

Every knowledge intake must end in one of these durable outcomes:

- reusable knowledge indexed after review;
- human approval requested;
- clarification requested from submitter;
- retry task created for an execution Agent;
- repair task created for Knowledge Ops;
- explicit rejection with source, reason, and audit trail.

No task may silently stop after one Agent writes a partial result.

## Agent Roles

| Agent | Role | Output |
| --- | --- | --- |
| Agent Hub / Intake Agent | Receives request, classifies public/project knowledge, registers SourceMaterial, creates KnowledgeTask | SourceMaterial, KnowledgeTask, NotificationRecord |
| Knowledge Engineering Agent | Reads SourceMaterial, extracts evidence, summarizes, structures draft knowledge | TaskResult, KnowledgeItem draft, evidence refs |
| Scheduler Quality Gate | Deterministically evaluates every TaskResult before downstream routing | AgentResultEvaluation, follow-up task |
| Knowledge Engineering Agent review sub-agent | Checks structure, evidence, confidence, scope, sensitivity, duplicate and conflict risk | Review task result, approval route |
| Knowledge Engineering Agent ops sub-agent | Repairs broken context, missing source, missing tool, permission, sync, or runner handoff | repair result, retry task or clarification |
| Publisher / Indexer | Moves review-approved knowledge into searchable/indexed state | index update, notification, audit |

## State Flow

```txt
SourceMaterial.created
-> KnowledgeTask.pending
-> waiting_runner or processing
-> TaskResult.result
-> AgentResultEvaluation
-> knowledge_review / knowledge_retry / knowledge_repair
-> review result
-> observed/indexed or approval_required or changes_requested or rejected
-> requester notification
-> closed
```

## Deterministic Result Evaluation

Every `TaskResult` produced for `KnowledgeTask` or `knowledge_retry` is evaluated before routing.

Minimum pass criteria:

- summary exists;
- at least one `KnowledgeItem` draft or explicit knowledge output exists;
- source evidence exists through `sourceMaterialRefs` or `evidenceRefs`;
- output is linked to original task, runner/executor, and source material;
- no blocked/rejected/failed status.

Evaluation output is stored on `TaskResult.qualityEvaluation`:

```yaml
type: AgentResultEvaluation
status: passed | failed | blocked
passed: true | false
decision: review_required | retry_required | repair_required
score: 0-100
attemptNumber: 1
maxAttempts: 3
retryable: true | false
reasons: []
```

## Routing Rules

### Passed

When evaluation passes:

```txt
TaskResult + KnowledgeItem draft
-> create knowledge_review task
-> assignee: agent.core.knowledge-review
-> notify Knowledge Engineering Agent review sub-agent
```

The original task is not considered reusable-knowledge complete yet. It has only completed the extraction stage.

### Failed But Retryable

When required output is missing and `attemptNumber < maxAttempts`:

```txt
TaskResult failed
-> create knowledge_retry task
-> assignee: original execution Agent
-> include previous TaskResult as failure evidence
```

The retry task must reuse the same source material and correct the missing output.

### Blocked Or Exhausted

When executor reports `blocked`, source cannot be resolved, permission/tool/context is missing, or retry attempts are exhausted:

```txt
TaskResult blocked/failed
-> create knowledge_repair task
-> assignee: agent.core.knowledge-ops
-> notify Ops and requester
```

Knowledge Ops must repair the handoff, ask for missing material, or produce an explicit unresolved record.

## Review Outcomes

Knowledge Engineering Agent review sub-agent may return:

- `pass_as_observed`: low-risk sourced lesson can become observed/indexable;
- `changes_requested`: create retry task for Knowledge Engineering Agent;
- `needs_clarification`: notify submitter and create clarification task;
- `needs_human_approval`: create Feishu approval and reviewer brief;
- `conflict_detected`: create ConflictRecord and route to Steward/Ops;
- `reject`: close with reason and notify requester.

Verified knowledge, active policy, approved tools/skills, permissions, security changes, customer commitments, and cross-team standards always require human approval.

The executable review endpoint is:

```txt
POST /v0/review/finish
{
  "reviewTaskId": "<knowledge_review task id>",
  "outcome": "pass_as_observed | needs_human_approval | changes_requested | needs_clarification | conflict_detected | reject",
  "reviewer": "agent.core.knowledge-review",
  "summary": "<review finding>",
  "targetRefs": ["knowledge/<category>/<item>.md"]
}
```

`pass_as_observed` updates accepted KnowledgeItem drafts to `observed`, rebuilds the index, writes ReviewRecord, and notifies the requester.

`needs_human_approval`, `changes_requested`, `needs_clarification`, and `conflict_detected` create executable follow-up tasks. `reject` marks targets rejected and notifies the requester.

## Manual Runner Mode

Before Agent Ring is ready:

```txt
Feishu/CLI creates KnowledgeTask
-> task status waiting_runner
-> notification card gives task ID and context pull instruction
-> local Codex/Claude session executes as Knowledge Engineering Agent
-> task finish writes TaskResult and KnowledgeItem draft
-> Scheduler automatically creates review/retry/repair follow-up task
```

The human starts or supervises the local Agent, but the next step is decided by the scheduler.

## Completion Standard

A knowledge intake is complete only when:

- SourceMaterial is preserved;
- TaskResult exists;
- qualityEvaluation exists;
- failed outputs have retry/repair follow-up;
- passed outputs have KnowledgeReview task;
- reviewed outputs are indexed or approval/clarification/rejection is recorded;
- requester receives notification;
- AuditLog records the lifecycle.
