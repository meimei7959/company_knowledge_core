# Execution Contract Lifecycle

## Purpose

`executionContract` is the task-level execution contract used by Zhenzhi runners.

It borrows the useful discipline from spec-first workflow tools without adopting their directory layout, status machine, or workflow ownership. The contract belongs to the existing `ProjectTask` / `KnowledgeTask` lifecycle and is evaluated through `TaskResult`, `AgentRun`, `AuditLog`, scheduler, and review gates.

## What It Solves

- Agents execute against a stable, reviewable task contract instead of loose chat context.
- Source, expected output, requirement, defect, and runtime changes are detected before closure.
- Resume, compaction, and handoff can compare hashes instead of guessing whether context is still valid.
- Reviewers see whether the result came from the current task facts.

## Contract Source Facts

The source hash covers task facts that affect execution:

- `taskId`, `taskType`, `projectId`, title, and work source type;
- linked requirements, acceptance criteria, defects, incidents, operations, and knowledge tasks;
- research question, source reason, outcome slice, source materials, and expected output;
- handoff contract;
- required secrets, required environment variables, explicit human acceptance requirement, and handoff contract;
- normalized runtime constraints, including required capabilities, tools, evidence policy, risk, permission policy, and closure policy.

It intentionally excludes lease state, runner heartbeat, notification refs, result refs, timestamps, and task status.

## Lifecycle

```txt
Task created
-> taskRuntime normalized
-> executionContract generated with sourceFactsHash
-> Scheduler / Agent Ring dispatches task
-> Runner pulls context and checks contract freshness
-> Runner executes local work
-> task finish writes TaskResult
-> finish guard records executionContractEvaluation
-> stale or missing contract blocks closure
```

## Refresh Rule

Refresh the contract before execution or closure when any contract source fact changes.

CLI:

```bash
zhenzhi-knowledge task contract <task-id> --actor <agent-or-runner>
```

This updates the task's `executionContract`, records `task.execution_contract.refresh` in `AuditLog`, and returns the refreshed contract plus evaluation.

## Finish Guard

`finish_project_task` evaluates `executionContractEvaluation`.

If the task runtime declares `executionContractRequired: true`, then successful close requires:

- `executionContract` exists;
- `executionContract.version` is `execution-contract.v1`;
- stored `sourceFactsHash` equals the current task facts hash.

Missing or stale contracts produce a blocked `TaskResult` instead of silent closure.

## Boundaries

This contract does not replace:

- Scheduler runner matching;
- Agent Ring lease ownership;
- `SourceMaterial` registration;
- `AuditLog`;
- `NotificationRecord`;
- Knowledge Review Agent;
- human approval for verified knowledge, policies, permissions, tools, security, or customer commitments.

It is only the execution discipline layer inside the existing Zhenzhi lifecycle.
