# Agent Ring Stub Test Strategy

## Purpose

Agent Ring is external and not implemented in this repository yet.

The central processor still needs end-to-end tests before Agent Ring is ready. We should test the full central chain with a stub runner that behaves like Agent Ring at the protocol boundary, without launching local Codex, Claude, browsers, or real tools.

## Principle

Test the contract, not the future workstation implementation.

The stub runner should simulate:

- runner registration;
- heartbeat;
- task polling;
- task claim with lease;
- context bundle pull;
- deterministic task execution result;
- TaskResult writeback;
- AgentRun writeback;
- status transition;
- blocked/error writeback;
- notification trigger.

The stub runner should not simulate:

- local Codex quality;
- actual code changes;
- browser sessions;
- full desktop process supervision;
- real secret access;
- real external tool side effects.

## Test Layers

### Layer 1: Protocol Unit Tests

Goal: prove central processor accepts and validates Agent Ring protocol messages.

Cases:

- valid runner registration;
- missing required runner capability;
- heartbeat updates online status;
- task claim requires valid task status;
- writeback requires matching lease token;
- result writeback is idempotent;
- invalid result refs are rejected;
- expired lease allows reassignment.

### Layer 2: Central Chain E2E With Stub Runner

Goal: prove a Feishu or CLI request can travel through the central system without real Agent Ring.

Flow:

```txt
Feishu message or CLI material ingest
-> SourceMaterial created
-> KnowledgeTask created
-> StubRunner registers
-> StubRunner polls and claims task
-> central processor returns context bundle
-> StubRunner writes deterministic TaskResult
-> optional KnowledgeItem draft is created
-> review/notification state is updated
-> audit trail exists
```

Expected proof:

- SourceMaterial exists and links original input.
- Task status changes from `pending` to `processing`/`submitted`/`done`.
- TaskResult links taskId, runnerId, executorAgent, source refs, evidence refs.
- AgentRun or equivalent execution record exists.
- AuditLog records key writes.
- User-facing notification can mention task title, project name, and result.

### Layer 3: Failure And Reassignment

Goal: prove the scheduler can recover when a runner disappears.

Cases:

- runner claims task and stops heartbeating;
- lease expires;
- scheduler releases or reassigns task;
- second stub runner claims task;
- second runner pulls latest context bundle and handoff note;
- final TaskResult is accepted.

### Layer 4: Contract Tests For Real Agent Ring

When the external Agent Ring exists, it must run the same contract tests against this central processor.

The same test vectors should work with:

- in-process stub runner;
- CLI script stub runner;
- HTTP client stub runner;
- real Agent Ring integration.

Current executable contract harness:

```bash
python3 scripts/agent_ring_contract.py
```

The script creates a temporary local bundle, starts the central processor HTTP API on `127.0.0.1`, and verifies:

- `/health`;
- unauthorized protected API access;
- runner registration;
- runner heartbeat;
- task query;
- task claim with lease;
- stale `expectedVersion` rejection;
- invalid lease token rejection;
- task context pull;
- task heartbeat;
- TaskResult finish;
- missing capability rejection;
- expired lease rejection;
- final bundle validation.

It uses only deterministic fixture data and no real secrets, Codex execution, Claude execution, browser automation, or external tools.

## Stub Runner Modes

### In-Process Stub

Best for unit tests. It calls Python functions directly.

Use for:

- fast lifecycle checks;
- validation rules;
- idempotency;
- lease logic.

### CLI Stub

Best for current repository workflow. It uses `zhenzhi-knowledge` commands and files.

Use for:

- task pull/start/finish flow;
- context pack generation;
- TaskResult files;
- bundle validation.

### HTTP Stub

Best once API endpoints are stable.

Use for:

- API auth;
- request/response shape;
- idempotency keys;
- external Agent Ring compatibility.

## Deterministic Stub Output

The stub runner should write predictable output so tests can assert exact fields:

```yaml
runnerId: runner.stub.local
executorAgent: agent.stub.knowledge
summary: Stub processed task for contract test.
sourceMaterialRefs:
  - <copied from task>
evidenceRefs:
  - <source material ref>
knowledgeRefs:
  - <optional draft KnowledgeItem>
testsOrChecks:
  - stub-runner-contract-ok
nextActions:
  - review generated draft
```

If the task asks for engineering execution, the stub should not pretend to change code. It should write a TaskResult that says execution was simulated and point to the expected output contract.

## What This Lets Us Test Now

- DeepSeek/Feishu routing creates the right task.
- Safety gate blocks high-risk direct execution.
- Task cards are created with readable fields.
- Scheduler can assign to a runner-like entity.
- Context bundle contains enough state for execution.
- Result writeback and notification path work.
- Project portability and reassignment behavior are testable before real Agent Ring.

## What Remains Untested Until Real Agent Ring

- local Codex/Claude invocation;
- desktop service stability;
- local file/repo/browser integration;
- machine resource scheduling accuracy;
- real tool permission enforcement on the workstation;
- local crash recovery.

These must be covered later by Agent Ring's own tests plus shared contract tests.
