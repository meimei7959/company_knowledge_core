---
type: HarnessSpec
title: Agent Ring Distributed Runner Proof Harness
timestamp: "2026-06-21T14:01:50Z"
owner: agent.company.development
status: blocked_on_second_real_runner
scope: real_two_runner_agent_ring_lifecycle_proof
---

# Agent Ring Distributed Runner Proof Harness

## Purpose

This harness defines the proof required to remove the distributed Agent Ring evidence blocker. It must be run with two real runner hosts, not two local aliases on one computer.

This task did not execute the real distributed proof on this computer because only the local Mac runner environment is available. Local dual-runner lifecycle evidence already passed, but it remains local-equivalent evidence and does not prove separate host identity, network interruption behavior, cross-machine filesystem boundaries, or real Agent Ring process supervision.

Current product decision: local dual-runner equivalent evidence is not accepted as a completion-scope exception. The only unblocking path is real distributed runner evidence or a formally recorded blocker that names the missing runner, network, and credential conditions.

## Required Environment

- Central API started from the knowledge bundle with `python3 -m zhenzhi_knowledge.cli --root /Users/meimei/Documents/company_knowledge_core api serve --host 0.0.0.0 --port 8765`.
- `ZHENZHI_KNOWLEDGE_API_TOKEN` set on the central API and both runner hosts.
- Runner A and Runner B on two distinct physical or virtual hosts.
- Distinct `runnerId` and `hostLabel` values.
- Both runners can reach the same central API URL.
- The coordinator has prepared proof tasks for happy path, cancel/retry, handoff, stale lease repair, and runner isolation.

## Evidence Contract

Each runner command writes JSONL events with:

- `proofRunId`
- `scenario`
- `hostLabel`
- `runnerId`
- `step`
- `method`
- `path`
- `payloadHash`
- `httpStatus`
- `ok`
- `response.kind`
- `response.task.status`, `response.task.leaseOwner`, `response.task.leaseExpiresAt` when returned
- `response.taskResult.resultId`, `response.taskResult.runnerId`, `response.taskResult.executorAgent` when returned
- `response.leaseTokenHash` when a claim returns a lease token

Lease tokens may be stored only in each runner's local `--state-file`. Submitted evidence must contain token hashes only.

Required proof steps:

| Capability | Required evidence step |
| --- | --- |
| Runner registration | `runner_register` from Runner A and Runner B |
| Runner heartbeat | `runner_heartbeat` from Runner A and Runner B |
| Runner read model | `runner_list` showing both runners |
| Lease claim | `task_claim` with `leaseTokenHash` |
| Context pull | `task_pull` by lease owner |
| Task heartbeat | `task_heartbeat` by lease owner |
| TaskResult writeback | `task_finish` with `response.resultRef` and `response.taskResult` |
| Cancel | `task_cancel` preserving lease/audit history |
| Retry | `task_retry` with human-readable reason and preferred runner |
| Handoff | `task_handoff` with target agent, evidence refs, and preferred runner |
| AgentRun | TaskResult evidence refs must include the AgentRun record produced by the executing runner |
| Notification | Read model or API evidence must show notification record for state transition or handoff |
| Audit | Audit API or file evidence must show runner register, heartbeat, claim, pull, cancel, retry, handoff, finish |
| Stale lease repair | `stale_lease_reclaim` from the other runner after previous lease expiration |
| Runner isolation | `runner_isolation_rejected` expected HTTP error when non-owner runner writes with invalid or foreign lease |

## Runnable Harness

Harness script:

```bash
python3 scripts/distributed_runner_proof_harness.py --help
```

Coordinator:

```bash
export ZK_API_BASE_URL="http://<central-host>:8765"
export ZHENZHI_KNOWLEDGE_API_TOKEN="<redacted>"
export ZK_PROOF_RUN_ID="distributed-proof-$(date -u +%Y%m%dT%H%M%SZ)"
```

Runner A:

```bash
export ZK_RUNNER_ID="runner.real.host-a"
export ZK_HOST_LABEL="host-a"
export ZK_EVIDENCE_FILE="artifacts/distributed-runner-proof/${ZK_PROOF_RUN_ID}/host-a.jsonl"
python3 scripts/distributed_runner_proof_harness.py register
python3 scripts/distributed_runner_proof_harness.py heartbeat-runner
python3 scripts/distributed_runner_proof_harness.py list-runners
python3 scripts/distributed_runner_proof_harness.py --scenario happy claim --task-id <TASK_HAPPY> --expected-version 1
python3 scripts/distributed_runner_proof_harness.py --scenario happy pull --task-id <TASK_HAPPY>
python3 scripts/distributed_runner_proof_harness.py --scenario happy heartbeat-task --task-id <TASK_HAPPY>
python3 scripts/distributed_runner_proof_harness.py --scenario happy finish --task-id <TASK_HAPPY> --summary "Runner A completed distributed happy path." --evidence-ref runs/<run-id>/agent-run.host-a.md --test-or-check distributed-happy-path
python3 scripts/distributed_runner_proof_harness.py --scenario happy list-notifications --task-id <TASK_HAPPY>
python3 scripts/distributed_runner_proof_harness.py --scenario happy list-audit --task-id <TASK_HAPPY>
python3 scripts/distributed_runner_proof_harness.py --scenario cancel-retry claim --task-id <TASK_CANCEL_RETRY>
python3 scripts/distributed_runner_proof_harness.py --scenario cancel-retry cancel --task-id <TASK_CANCEL_RETRY> --reason "Distributed proof cancel leg."
python3 scripts/distributed_runner_proof_harness.py --scenario cancel-retry retry --task-id <TASK_CANCEL_RETRY> --reason "Distributed proof retry to Runner B." --preferred-runner runner.real.host-b
python3 scripts/distributed_runner_proof_harness.py --scenario stale-repair claim --task-id <TASK_STALE> --lease-seconds 1
```

Runner B:

```bash
export ZK_RUNNER_ID="runner.real.host-b"
export ZK_HOST_LABEL="host-b"
export ZK_EVIDENCE_FILE="artifacts/distributed-runner-proof/${ZK_PROOF_RUN_ID}/host-b.jsonl"
python3 scripts/distributed_runner_proof_harness.py register
python3 scripts/distributed_runner_proof_harness.py heartbeat-runner
python3 scripts/distributed_runner_proof_harness.py list-runners
python3 scripts/distributed_runner_proof_harness.py --scenario isolation finish-expect-rejected --task-id <TASK_HAPPY>
python3 scripts/distributed_runner_proof_harness.py --scenario cancel-retry claim --task-id <TASK_CANCEL_RETRY>
python3 scripts/distributed_runner_proof_harness.py --scenario handoff claim --task-id <TASK_HANDOFF>
python3 scripts/distributed_runner_proof_harness.py --scenario handoff handoff --task-id <TASK_HANDOFF> --to agent.company.development --summary "Distributed handoff proof from Runner B to Runner A." --preferred-runner runner.real.host-a --evidence-ref artifacts/distributed-runner-proof/${ZK_PROOF_RUN_ID}/host-b.jsonl
python3 scripts/distributed_runner_proof_harness.py --scenario handoff list-notifications --task-id <TASK_HANDOFF>
python3 scripts/distributed_runner_proof_harness.py --scenario handoff list-audit --task-id <TASK_HANDOFF>
sleep 2
python3 scripts/distributed_runner_proof_harness.py --scenario stale-repair claim --task-id <TASK_STALE> --step-name stale_lease_reclaim
```

Coordinator verification after collecting both JSONL files:

```bash
python3 scripts/distributed_runner_proof_harness.py verify \
  --evidence artifacts/distributed-runner-proof/${ZK_PROOF_RUN_ID}/host-a.jsonl \
  --evidence artifacts/distributed-runner-proof/${ZK_PROOF_RUN_ID}/host-b.jsonl
```

## Formal Blocker

Blocker id: `blocker.real-distributed-runner-proof.20260621T140150Z`

Current status: blocked on unavailable second real runner host and unavailable real Agent Ring process supervision on this computer.

Exit condition:

- Two distinct real hosts produce JSONL evidence for the required steps above.
- Evidence verifies with `scripts/distributed_runner_proof_harness.py verify`.
- TaskResult links AgentRun, TaskResult, notification, and audit evidence from the real run.

Until then, `kt-ai-native-os-test-distributed-runner-proof` must remain blocked. It may be unlocked only to test the blocker and harness contract, not to pass product distributed-runner proof.
