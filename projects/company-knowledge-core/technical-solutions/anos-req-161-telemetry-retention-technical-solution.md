---
type: Workflow
title: ANOS-REQ-161 execution telemetry retention technical solution
description: V0 architecture for classifying, compacting, retaining, cleaning, auditing, and promoting execution telemetry without changing core task semantics.
timestamp: "2026-06-23T11:48:19Z"
solutionId: anos-req-161-telemetry-retention-technical-solution
projectId: company-knowledge-core
ownerAgent: agent.company.architecture
status: draft
requirementRefs:
  - ANOS-REQ-161
  - ANOS-REQ-160
sourceRefs:
  - docs/product/ai-native-os/execution-telemetry-retention-prd.md
  - docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md
  - projects/company-knowledge-core/product-reviews/anos-req-161-telemetry-retention-product-requirement-acceptance.md
  - task-results/tr-kt-anos-req-161-product-requirement-acceptance.md
  - docs/product/ai-native-os/phase-2-central-runner-observability-prd.md
  - docs/product/ai-native-os/task-execution-productization-prd.md
  - docs/schemas/core-objects.md
receiverReviewRef: projects/company-knowledge-core/receiver-reviews/receiver-review.anos-req-161.architecture.md
auditRefs:
  - knowledge/audit/audit.20260623T114819Z-anos-req-161-architecture.md
---

# Technical Solution

## Decision

Accept the ANOS-REQ-161 architecture path as a repository-local V0 retention system: telemetry enters through a classification boundary, updates Current State by upsert, appends only bounded hot Task Timeline records, compacts terminal task history into summaries, keeps MetricsReport-style rollups, and uses a TelemetryRetentionWorker to dry-run or apply cleanup with protected-reference scanning and one batch AuditLog summary per apply.

This design does not introduce an external log platform as a prerequisite. It does not rewrite Scheduler, Runner, TaskResult, AuditLog, lease, finish, or result writeback semantics. Raw telemetry is operational input, not long-term truth.

## Data Carriers

V0 carriers are supporting read models and manifests, not new core truth objects.

| Carrier | Purpose | Retention posture |
| --- | --- | --- |
| `ExecutionTelemetryEvent` read model | Normalized ingestion record for heartbeat, lease, progress, tool/model usage, result writeback, and error reports. | Short-lived raw/hot data only. |
| `ExecutionCurrentState` read model | Latest runner/task status snapshot for task fact views and operator diagnosis. | Upserted; one logical current row per runner/task/scope. |
| `TaskExecutionTimeline` read model | Bounded task timeline for phase and notable event reconstruction while work is active or recently closed. | Hot raw entries compacted at closeout or TTL. |
| `TaskExecutionSummary` read model | Closeout summary derived from timeline, TaskResult, AgentRun, key errors, tool/model totals, and acceptance route. | Longer-lived product-readable summary. |
| `TelemetryRetentionBatch` manifest | Dry-run/apply plan, counters, protected skips, rollup outputs, and batch digest. | Retained as operational evidence. |
| `MetricsReport` or equivalent rollup | Aggregated runner/task telemetry, diagnostic counts, cleanup counts, and SLO indicators. | Long-lived aggregate, no raw sensitive payload. |
| `AgentImprovementProposal` / `EvalCase` candidates | Learning signal promoted from rejected, rework, quality gate failure, boundary violation, repeated blocker, manual correction. | Protected from cleanup after promotion. |
| `AuditLog` | Batch apply summary only, plus architecture/task lifecycle audit. | Protected core evidence. |

File-backed V0 can live under `.zhenzhi/telemetry/` for operational read models and under existing object directories for promoted core objects:

- `.zhenzhi/telemetry/current-state/*.json`
- `.zhenzhi/telemetry/task-timeline/*.jsonl`
- `.zhenzhi/telemetry/task-summary/*.json`
- `.zhenzhi/telemetry/retention-batches/*.json`
- `knowledge/metrics/` or existing MetricsReport location for aggregate reports, if used by current repository conventions
- `agent-improvement-proposals/` and `eval-cases/` or existing approved object locations for promoted learning candidates

If V0 later moves to an API/database store, keep the same logical objects and retention behavior.

## Ingestion Classification

All telemetry ingestion must pass a classifier before persistence. The classifier assigns `eventType`, `scope`, `retentionClass`, `protectedCandidate`, `sensitivity`, `dedupeKey`, `eventTime`, and `sourceRef`.

| Inbound event | Primary path | Default retentionClass | Notes |
| --- | --- | --- | --- |
| `heartbeat` | Current State upsert, optional low-detail diagnostic counter | `ephemeral_state` | Never writes ordinary heartbeat AuditLog. |
| `lease_update` | Current State upsert plus protected active-lease marker | `hot_task` while active, then `closeout_summary` | Active lease always blocks cleanup. |
| `progress_update` | Current State current step plus bounded timeline append | `hot_task` | Keep phase changes and notable progress; collapse noisy repeats. |
| `tool_usage` | Timeline aggregate bucket and metrics rollup | `diagnostic_metric` | Store command/tool names and safe counters, not secret payloads. |
| `model_usage` | Metrics rollup and optional task summary totals | `diagnostic_metric` | Token/cost/latency aggregates only. |
| `result_writeback` | TaskResult/AgentRun refs, closeout trigger, timeline summary | `protected_result_ref` and `closeout_summary` | Never deletes TaskResult or evidence refs. |
| `error_report` | Current State last error summary, timeline notable event, learning classifier | `hot_task` or `learning_signal` | Promote repeated, rejected, quality-gate, boundary, or manual-correction signals before cleanup. |

Retention class precedence:

1. `protected_core_ref`: TaskResult, AuditLog, ReviewRecord, verified/approved KnowledgeItem, human acceptance artifact, active task/lease, unresolved blocker, incident, AgentImprovementProposal, EvalCase, and cited evidence.
2. `learning_signal`: candidate evidence for improvement/eval promotion.
3. `closeout_summary`: terminal task summary required by task fact views.
4. `diagnostic_metric`: aggregate MetricsReport or equivalent rollup.
5. `hot_task`: active or recently completed task timeline records.
6. `ephemeral_state`: heartbeat/current state noise that can be overwritten or deleted after freshness window.

Protected class wins over TTL and cleanup mode.

## Current State Upsert

Current State is a read model keyed by `projectId`, `runnerId`, `taskId` when present, and `scope` when task is absent. It is overwritten, not appended, for heartbeat, load, current task, current phase, last step, last heartbeat, last lease, and last safe error summary.

Upsert behavior:

- Same `dedupeKey` and older `eventTime` is ignored.
- Newer state replaces previous values field by field.
- Sensitive details are redacted at ingestion; only safe summaries survive.
- `lastErrorSummary` stores class, short safe message, linked timeline event, and whether learning promotion is pending.
- Active task or active lease state writes a protected marker consumed by retention scans.

This preserves the task fact view without turning raw heartbeat history into truth.

## Task Timeline And Closeout Compaction

Task Timeline stores only bounded hot events needed to explain execution while a task is active or recently completed:

- phase changes
- lease changes
- result writeback boundary
- notable progress milestones
- safe error summaries
- tool/model usage buckets
- quality gate outcomes
- worker boundary violations
- manual corrections and rework events

Closeout compaction triggers when any of these appear:

- TaskResult writeback for the task
- task terminal status such as `done`, `blocked`, `rejected`, or equivalent repository state
- task status `waiting_acceptance`
- explicit retention worker detection that task has no active lease and has crossed the hot window

Compaction output is `TaskExecutionSummary`:

- task identity and final status
- start/end/closeout timestamps, if known
- phase list and final current state
- resultRef, AgentRun refs, evidenceRefs, receiverReviewRefs, auditRefs
- key errors and recoveries
- tool/model aggregate totals
- quality gate and acceptance route
- learning signals promoted or pending
- protected refs found
- raw timeline entries compacted/deleted/skipped counts

After summary write succeeds and protected refs are recorded, raw hot timeline entries can be deleted or compacted according to retention policy. Summary and protected refs remain.

## TelemetryRetentionWorker

`TelemetryRetentionWorker` is a scheduled or manually invoked background job. It may run inside existing CLI/runtime infrastructure; it is not a new Scheduler semantics layer.

Worker phases:

1. Discover telemetry carriers and candidate windows.
2. Classify records and recompute retentionClass when source state changed.
3. Scan protected refs before deletion or compaction.
4. Build deterministic dry-run plan with counts and reasons.
5. Roll up diagnostic/metrics data.
6. Promote learning-signal candidates before cleanup.
7. In apply mode, stage batch manifest, compact summaries, delete only unprotected expired raw records, write rollups, then write one AuditLog summary.
8. Emit stable report for Test Agent.

Worker cadence should be configurable. Recommended V0 default: dry-run available on demand, apply manual or scheduled daily for local repository runs, with small batch limits to reduce blast radius.

## Dry-Run And Apply

Dry-run and apply share the same planner. Dry-run must not mutate files or data.

Stable report fields:

- `batchId`
- `mode`
- `startedAt`
- `policyVersion`
- `candidateCountsByClass`
- `plannedDeleteCountsByClass`
- `plannedCompactCountsByClass`
- `plannedRollupCounts`
- `learningPromotionCandidates`
- `protectedSkipCounts`
- `protectedSkipRefs`
- `reasons`
- `errors`
- `wouldWriteRefs`
- `digest`

Apply adds:

- `appliedDeleteCountsByClass`
- `appliedCompactCountsByClass`
- `rollupRefs`
- `promotionRefs`
- `auditRef`
- `batchManifestRef`
- `completedAt`

CLI surface:

- `zhenzhi-knowledge telemetry ingest --type <eventType> --runner <runnerId> --task <taskId> --file <json>`
- `zhenzhi-knowledge telemetry retention run --dry-run --project <projectId> --window <duration>`
- `zhenzhi-knowledge telemetry retention run --apply --project <projectId> --batch-limit <n>`
- `zhenzhi-knowledge telemetry retention show --batch <batchId>`

API prototype surface:

- `POST /api/telemetry/events`
- `GET /api/tasks/{taskId}/execution-current-state`
- `GET /api/tasks/{taskId}/execution-timeline`
- `GET /api/tasks/{taskId}/execution-summary`
- `POST /api/telemetry/retention/dry-run`
- `POST /api/telemetry/retention/apply`

API and CLI must return the same report shape.

## Protected Refs Scan

Before deleting or compacting raw records, the worker scans:

- `TaskResult.outputRefs`, `TaskResult.evidenceRefs`, `TaskResult.testsOrChecks`, and result files
- `AuditLog.targetRef`, details, and audit refs
- `ReviewRecord`, product reviews, receiver reviews, and human acceptance artifacts
- `KnowledgeItem` draft/observed/verified/approved refs and source evidence
- `AgentImprovementProposal` and `EvalCase` refs
- active leases, active tasks, `waiting_acceptance` tasks, unresolved blockers, open incidents
- `SourceMaterial` refs needed for task evidence
- `MetricsReport` and task summaries that cite telemetry batches

If a raw telemetry record is cited by protected evidence, cleanup must skip it or replace the citation with a summary ref only after the protected owner accepts the rewrite. No silent protected-ref deletion.

## Audit Summary

Apply writes one batch AuditLog, not one AuditLog per deleted row/file.

Audit details must include:

- batchId and policyVersion
- mode `apply`
- candidate, deleted, compacted, promoted, rolled-up, and skipped counts
- protected skip categories and sample refs
- batch manifest ref
- rollup refs
- promotion refs
- actor/job identity
- dry-run digest matched by apply, when apply follows a dry-run

AuditLog never stores secrets or raw telemetry payloads.

## Diagnostics And Metrics Rollup

Long-term metrics are aggregates, not raw logs:

- heartbeat freshness distribution
- runner online/offline/stale counts
- task phase duration buckets
- tool/model usage totals by safe category
- error class counts
- cleanup candidates/deleted/skipped counts
- closeout compaction lag
- learning signal counts and promotion outcomes

MetricsReport or equivalent rollup should be queryable by project, runner, task type, and time bucket. It must not become a backdoor raw telemetry store.

## Learning Signal Promotion

Learning classifier checks before cleanup:

- rejected TaskResult
- rework request
- manual correction
- repeated blocker
- quality gate failure
- worker boundary violation
- permission/approval/identity failure
- recurring integration failure

Promotions create candidates only:

- `AgentImprovementProposal` for agent/process repair
- `EvalCase` for regression coverage
- optional follow-up ProjectTask when the signal needs owner action

Promotion must cite safe evidence and summary refs. It does not create verified knowledge, policy, skill changes, or role changes without the existing review gates.

## Failure Recovery And Idempotency

Use deterministic `batchId` from project, policy version, time window, mode, and candidate digest. Re-running the same dry-run over unchanged input produces the same plan digest.

Apply recovery rules:

- Write batch manifest in `planned` state before mutation.
- Mark per-carrier operations as `applied`, `skipped_protected`, or `failed` in the manifest.
- If interrupted, rerun recomputes candidates and resumes from manifest state.
- Summary upserts are idempotent by `taskId` plus closeout version.
- Rollups are idempotent by metric bucket and source batchId.
- Promotions are idempotent by signal fingerprint, taskId, agentId, and failure class.
- Audit summary is written once per successful apply batch; reruns update manifest, not duplicate AuditLog, unless a new batch digest is created.

## Permissions And Redaction

Telemetry ingestion accepts only registered runner/task context or an authorized operator. Retention apply requires an operator or scheduled worker identity allowed to mutate telemetry read models. Product/UI readers get redacted summaries only.

Redaction rules:

- never store secrets, tokens, full prompts with sensitive material, raw command output, or private payloads in long-term telemetry
- store safe labels, counts, classes, timestamps, refs, and short summaries
- retain protected evidence only when it is already an approved evidence ref or has a required review path

## Implementation Slices

Recommended Development breakdown:

1. Define telemetry read-model schema, retention policy config, report shape, and fixture data.
2. Implement ingestion classifier and Current State upsert.
3. Implement bounded Task Timeline append and closeout summary compaction.
4. Implement protected-ref scanner.
5. Implement TelemetryRetentionWorker dry-run planner.
6. Implement apply mode with batch manifest, summary compaction, deletion, rollup, promotion, and single AuditLog summary.
7. Implement CLI/API surfaces with the same report schema.
8. Add diagnostics/metrics rollup and task fact view integration points.
9. Add full lifecycle tests and hand off to Test Agent.

Development task must load `development-engineering-quality-gate` and run `scripts/quality/development_quality_gate.py` before handoff.

## Test Handoff

Development/Test must cover:

- ANOS-161-AC-001 classification by event type and retentionClass
- ANOS-161-AC-002 Current State overwrite, no heartbeat append explosion
- ANOS-161-AC-003 task timeline phase/notable event retention
- ANOS-161-AC-004 closeout compaction from TaskResult/terminal/waiting_acceptance
- ANOS-161-AC-005 dry-run no mutation and stable report fields
- ANOS-161-AC-006 apply deletes/compacts only eligible data
- ANOS-161-AC-007 protected refs block cleanup
- ANOS-161-AC-008 one batch AuditLog summary, no per-delete AuditLog
- ANOS-161-AC-009 learning signals promoted before cleanup
- ANOS-161-AC-010 metrics/diagnostic rollups survive raw cleanup
- idempotent rerun and interrupted apply recovery
- permission and redaction checks
- `python3 -m zhenzhi_knowledge.cli status`

Architecture-only boundary assertions can be checked by reviewing this document, ReceiverReview, TaskResult, and audit refs. No production cleanup should be considered accepted until Development and Test evidence exists.

## Risks

- Protected-ref scanner misses an evidence path. Mitigation: scanner tests with TaskResult, AuditLog, ReviewRecord, KnowledgeItem, AgentImprovementProposal, EvalCase, active lease, blocker, and incident fixtures.
- Apply deletes too aggressively. Mitigation: dry-run/apply shared planner, batch limits, manifest staging, protected priority, and rollback from staged refs where possible.
- Raw telemetry becomes de facto truth. Mitigation: short TTL defaults, summary/rollup carriers, and task fact views cite core objects first.
- Learning promotion creates noisy repair objects. Mitigation: fingerprint dedupe and thresholds for repeated signals.
- Metrics rollup leaks sensitive payload. Mitigation: schema allowlist of safe aggregate fields.

## Rollback

Rollback apply by batch:

1. Stop retention worker or disable apply mode.
2. Read `TelemetryRetentionBatch` manifest and batch AuditLog.
3. Restore compacted/deleted raw records from staged backup when V0 storage supports backup; if no backup exists, keep summaries and mark raw records unrecoverable in a follow-up incident.
4. Revert generated summaries, rollups, and promotions only if they are not protected by downstream TaskResult, AuditLog, acceptance, knowledge, or human review refs.
5. Write one corrective AuditLog summary for the rollback.
6. Rerun dry-run and status validation before re-enabling apply.

Core TaskResult, AuditLog, ReviewRecord, verified knowledge, acceptance artifacts, AgentImprovementProposal, EvalCase, and active work refs must not be deleted as rollback cleanup.

## Development Handoff

Ready for Development after Product/PM accepts this architecture result. Handoff package:

- this technical solution
- ReceiverReview
- ANOS-REQ-161 PRD and acceptance matrix
- product requirement acceptance
- architecture TaskResult
- audit log

Development must preserve the hard boundaries and produce implementation evidence before Test Agent begins final acceptance.
