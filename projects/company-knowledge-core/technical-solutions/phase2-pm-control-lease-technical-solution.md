---
type: Workflow
solutionId: phase2-pm-control-lease-technical-solution
title: Phase 2 PM Control Lease Technical Solution
status: draft
owner: agent.company.architecture
projectId: company-knowledge-core
sourceRefs:
  - docs/product/ai-native-os/phase-2-pm-control-lease-prd.md
  - projects/company-knowledge-core/workflows/phase2-pm-control-lease-orchestrator.md
  - projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-architecture.md
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/server.py
  - zhenzhi_knowledge/cli.py
  - projects/company-knowledge-core/desktop-workbench-slice0/shared-frontend-foundation.ts
---

# Phase 2 PM Control Lease Technical Solution

## 1. Goal

同一项目同一时间只允许一个主控 PM Agent 持有有效项目级调度租约。所有由 PM Agent 发起、会改变项目调度状态的写操作，必须在 core 落库前通过 PMControlLease 校验。无租约、过期、非主控、项目不匹配、旧 fencing token 都必须拒绝、不可写目标对象，并写 AuditLog。

PMControlLease 是项目级调度意图锁，不替代已有 Runner 任务租约。Runner 登记、Runner heartbeat、任务 claim/heartbeat/result writeback 继续走现有 AgentRunner 和 ProjectTask lease 机制。

## 2. Existing Baseline

- `core.py` 已有 `AgentRunner` 登记、Runner pairing、任务 claim/heartbeat、审计、通知、scheduler/workbench read model。
- `claim_project_task()` 已用 `leaseOwner`、`leaseProofHash`、`leaseExpiresAt` 保护单个任务执行租约。
- `create_audit_log()` 已写 `knowledge/audit/*.md`，可复用为 PM 租约拒绝、接管、释放、续约审计。
- `server.py` 已集中处理 `/v0/runners/register`、`/v0/tasks/claim`、`/v0/tasks/heartbeat` 等 API。
- `cli.py` 已有 `runner`、`workbench`、`task` 命令入口。
- `shared-frontend-foundation.ts` 的 workbench read model 已支持 `runnerLeases`、`agentSessions`、`permissionGatedActions`，可加 optional PM control 字段保持兼容。

## 3. Data Model

### 3.1 PMControlLease

建议存储位置：

```txt
projects/<projectId>/pm-control-leases/<leaseId>.md
projects/<projectId>/pm-control-leases/index.md
```

frontmatter:

```yaml
type: PMControlLease
leaseId: pmlease.<projectId>.<timestamp>
projectId: company-knowledge-core
primaryPmAgentId: agent.company.project-manager
sessionId: session.company-knowledge-core.agent-company-project-manager
runnerId: runner.macbook-main
deviceId: device.macbook-main
status: active
leaseGeneration: 7
leaseProofHash: <secret_fingerprint(raw token)>
acquiredAt: "2026-06-23T10:00:00Z"
expiresAt: "2026-06-23T10:10:00Z"
lastHeartbeatAt: "2026-06-23T10:05:00Z"
releasedAt: ""
takenOverAt: ""
takeoverPolicy:
  staleAfterSeconds: 120
  expiresAfterSeconds: 600
  healthyTakeoverRequiresOwnerConfirmation: true
previousLeaseId: ""
takeoverRecordRef: ""
auditRefs: []
deduplicationRef: "pmlease:company-knowledge-core:agent.company.project-manager:..."
sourceChannel: agent_ring
```

Status values:

- `active`: 当前可写。
- `expiring`: 未过期，但接近到期；仍可按策略写入。
- `stale`: heartbeat 延迟；旧租约不可继续写入，除非策略明确允许短 grace。
- `expired`: 已到期；不可写。
- `released`: 主控主动释放；不可写。
- `taken_over`: 已被新 PM 接管；不可写。

Design rules:

- 每个 `projectId` 最多一个 `status in {active, expiring}` 且未过期的最新租约。
- `leaseGeneration` 对项目单调递增。接管或重新 acquire 必须生成更大的 token。
- API/CLI 只返回 raw lease token 一次；持久化只存 `leaseProofHash`。
- 工作台默认展示人可读 label，不以 `leaseId` 为主展示。

### 3.2 ProjectPmParticipant

建议存储位置：

```txt
projects/<projectId>/pm-participants/<pmAgentId>.md
```

frontmatter:

```yaml
type: ProjectPmParticipant
projectId: company-knowledge-core
pmAgentId: agent.company.project-manager
role: primary
allowedRoles:
  - primary
  - collaborator
  - standby
sessionIds:
  - session.company-knowledge-core.agent-company-project-manager
runnerIds:
  - runner.macbook-main
deviceIds:
  - device.macbook-main
standbyPriority: 10
capabilities:
  - task_breakdown
  - acceptance_routing
  - risk_recovery
status: online
lastActiveAt: "2026-06-23T10:05:00Z"
currentLeaseId: pmlease.company-knowledge-core.20260623T100000Z
```

Role meaning:

- `primary`: 当前持有效 lease 的主控 PM。
- `collaborator`: 可读、可准备建议，不可写调度状态。
- `standby`: 可读、可准备接管；接管成功前不可写调度状态。

### 3.3 PmLeaseTakeoverRecord

建议存储位置：

```txt
projects/<projectId>/pm-control-leases/takeovers/<takeoverId>.md
```

frontmatter:

```yaml
type: PmLeaseTakeoverRecord
takeoverId: pmtakeover.<projectId>.<timestamp>
projectId: company-knowledge-core
fromPmAgentId: agent.company.old-pm
toPmAgentId: agent.company.new-pm
requestedBy: agent.company.new-pm
confirmedBy: human.project-owner
reason: "主控失联，租约已过期"
previousLeaseId: pmlease.company-knowledge-core.1
previousLeaseStatus: expired
newLeaseId: pmlease.company-knowledge-core.2
leaseGenerationBefore: 7
leaseGenerationAfter: 8
requestedAt: "2026-06-23T10:12:00Z"
completedAt: "2026-06-23T10:12:05Z"
auditRef: knowledge/audit/audit....md
```

## 4. Session Model

PM session builds on existing `AgentSession`, `AgentDevice`, and `AgentRunner` records.

- 主控 PM session: `ProjectPmParticipant.role=primary` and `currentLeaseId` points to the only active PMControlLease.
- 协同 PM session: participant exists, has project permission, but no active lease. It may read project state and produce local/suggested artifacts, but cannot call protected PM write functions successfully.
- 备用 PM session: participant has `standbyPriority` and takeover capability. It may call takeover endpoints when current lease is `stale`, `expired`, `released`, or when owner confirmation is supplied for healthy takeover.

Session liveness source:

- Prefer current `AgentSession.lastHeartbeatAt` for PM session health.
- Use `AgentRunner.lastHeartbeatAt` and `AgentDevice.status` as supporting health signals.
- PM lease health is computed from lease `expiresAt` and `lastHeartbeatAt`; Runner task lease health remains independent.

## 5. Protected PM Writes

Protected writes are writes by PM Agent actors that change project scheduling intent:

- Project schedule plan or workflow phase changes.
- `ProjectTask` / `KnowledgeTask` create or update: priority, assignee, workflow, blocked state, exposed-to-runner state.
- Dispatch controls: expose, pause, resume, retry, cancel, preferred Runner switch.
- Acceptance routing: reviewer assignment, waiting-acceptance transitions, follow-up task creation.
- Recovery routing: stale task repair, manual handoff, repair task creation.
- NotificationRecord writes that announce PM scheduling changes.
- Workbench PM command buttons that trigger any of the above.

Not protected by PMControlLease:

- Runner registration and pairing.
- Runner heartbeat.
- Runner task claim/heartbeat/writeback guarded by existing task lease.
- Raw SourceMaterial registration.
- AuditLog creation by the central system.
- Read-only API/CLI/workbench calls.
- Human approval decisions, unless the same request also performs PM scheduling mutation.

## 6. Core Validation Design

Add a single core guard and route every protected PM write through it:

```python
def validate_pm_control_lease_for_write(
    bundle: Bundle,
    project_id: str,
    pm_agent_id: str,
    lease_id: str,
    lease_generation: int | str,
    action: str,
    source_channel: str = "api",
    request_ref: str = "",
) -> dict[str, Any]:
    ...
```

Validation order:

1. Required fields: `projectId`, `pmAgentId`, `leaseId`, `leaseGeneration`.
2. Lease exists.
3. Lease belongs to same project.
4. Lease status is `active`, or computed `expiring` with policy still allowing writes.
5. `expiresAt` is in the future.
6. Request PM equals `primaryPmAgentId`.
7. Request `leaseGeneration` equals current project latest token.
8. PM participant has project access and role/capability allowing requested action.
9. Source channel is known and allowed.

On success, return normalized lease plus `leaseRef`, `primaryPmAgentId`, `runnerId`, `deviceId`, and `auditContext`.

On failure, call one helper:

```python
def deny_pm_control_lease_write(
    bundle: Bundle,
    project_id: str,
    pm_agent_id: str,
    action: str,
    reason_code: str,
    target_ref: str = "",
    lease_id: str = "",
    current_lease: dict[str, Any] | None = None,
    source_channel: str = "api",
) -> NoReturn:
    ...
```

The helper must write `AuditLog` before raising `KnowledgeError` or a future typed `LeaseValidationError`.

## 7. Rejection Semantics And Audit

All rejected PM writes:

- Must not write the target business object.
- Must write `AuditLog` action `pm_control_lease.denied`.
- Must include readable details: project, requested PM, current primary PM, requested action, reason, source, lease id if supplied, current lease status, current expiresAt, request time.
- Should return a stable machine error code and Chinese display message.

Recommended reason codes:

| Case | Code | HTTP | CLI exit | Display message |
| --- | --- | --- | --- | --- |
| Missing lease fields | `pm_control_lease_missing` | 409 | 2 | 当前 PM 没有项目主控租约，不能改项目调度。 |
| Lease not found | `pm_control_lease_not_found` | 409 | 2 | 未找到提交的 PM 主控租约，请刷新主控状态。 |
| Expired/stale lease | `pm_control_lease_expired` | 409 | 2 | PM 主控租约已过期，需续约或由备用 PM 接管。 |
| Non-primary PM | `pm_control_lease_not_primary` | 409 | 2 | 当前写入者不是项目主控 PM，只能查看或提交建议。 |
| Project mismatch | `pm_control_lease_project_mismatch` | 409 | 2 | 租约属于其他项目，不能用于当前项目写入。 |
| Stale fencing token | `pm_control_lease_stale_lease_generation` | 409 | 2 | 该租约令牌已失效，项目可能已被接管。 |
| Permission/capability mismatch | `pm_control_lease_permission_denied` | 403 | 2 | 当前 PM 没有执行该调度动作的权限。 |

Audit detail example:

```txt
projectId=company-knowledge-core
requestedPmAgentId=agent.company.collaborator
currentPrimaryPmAgentId=agent.company.project-manager
action=project_task.update_priority
reasonCode=pm_control_lease_not_primary
leaseId=pmlease.company-knowledge-core.20260623T100000Z
currentLeaseStatus=active
sourceChannel=api
targetRef=projects/company-knowledge-core/tasks/kt-example.md
```

## 8. Lease Lifecycle

### 8.1 Acquire

Use when no active lease exists or previous lease is `expired` / `released`.

Flow:

1. Validate PM participant and project access.
2. Repair computed stale/expired lease state first.
3. If current active healthy lease exists, reject with `pm_control_lease_already_active`.
4. Increment project fencing token.
5. Create PMControlLease with raw token returned once.
6. Mark participant role/currentLeaseId.
7. Write `pm_control_lease.acquired` audit.

### 8.2 Heartbeat / Renew

Flow:

1. Validate lease owner, raw token hash, fencing token, project.
2. Extend `expiresAt`.
3. Update `lastHeartbeatAt`.
4. Write `pm_control_lease.renewed` audit, or sample audit if too noisy is later accepted by policy.

### 8.3 Release

Release is itself a protected PM write and must carry valid current lease.

Flow:

1. Validate current lease.
2. Mark lease `released`.
3. Clear participant `currentLeaseId`; role becomes `collaborator` or configured standby.
4. Write `pm_control_lease.released` audit.
5. Workbench shows no current primary and suggests standby takeover.

### 8.4 Takeover

Healthy primary:

1. Standby PM or owner requests takeover with reason.
2. Core detects current lease is healthy.
3. Require owner/authorized confirmation proof.
4. Mark old lease `taken_over`.
5. Create new lease with incremented fencing token.
6. Create `PmLeaseTakeoverRecord`.
7. Write `pm_control_lease.taken_over` audit.
8. Old primary writes are rejected by stale fencing token.

Expired/stale/released primary:

1. Repair current lease status to `stale` or `expired`.
2. Validate standby PM participant and takeover capability.
3. Require reason; owner confirmation optional per policy.
4. Create new lease and takeover record.
5. Write audit and update read model.

## 9. Core Changes

Add helpers near current Runner/workbench runtime helpers:

- `pm_control_lease_storage_dir(bundle, project_id)`
- `pm_participant_storage_dir(bundle, project_id)`
- `find_pm_control_lease(bundle, project_id, lease_id)`
- `current_pm_control_lease(bundle, project_id)`
- `repair_pm_control_lease_state(bundle, project_id, actor)`
- `upsert_project_pm_participant(...)`
- `acquire_pm_control_lease(...)`
- `heartbeat_pm_control_lease(...)`
- `release_pm_control_lease(...)`
- `takeover_pm_control_lease(...)`
- `validate_pm_control_lease_for_write(...)`
- `deny_pm_control_lease_write(...)`
- `pm_control_lease_read_model(bundle, project_id)`

Protected write functions should accept a `pm_write_context` dict rather than many positional lease args:

```python
pm_write_context={
  "projectId": "...",
  "pmAgentId": "...",
  "leaseId": "...",
  "leaseGeneration": 8,
  "sourceChannel": "api",
}
```

Core remains authoritative. API and CLI may require flags, but cannot be trusted as the only gate.

## 10. API Changes

Add routes:

- `GET /v0/projects/<projectId>/pm-control-lease`
- `GET /v0/projects/<projectId>/pm-participants`
- `POST /v0/pm-control-leases/acquire`
- `POST /v0/pm-control-leases/heartbeat`
- `POST /v0/pm-control-leases/release`
- `POST /v0/pm-control-leases/takeover`

Required request fields:

- acquire: `projectId`, `pmAgentId`, `sessionId`, `runnerId`, `deviceId`, `leaseSeconds`, `deduplicationRef`.
- heartbeat: `projectId`, `pmAgentId`, `leaseId`, `leaseToken`, `leaseGeneration`, `leaseSeconds`.
- release: `projectId`, `pmAgentId`, `leaseId`, `leaseToken`, `leaseGeneration`, `reason`.
- takeover: `projectId`, `toPmAgentId`, `fromLeaseId`, `reason`, `sessionId`, `runnerId`, `deviceId`, `ownerConfirmationRef` when required, `deduplicationRef`.

Protected existing PM write APIs must accept:

```json
"pmControlLease": {
  "projectId": "company-knowledge-core",
  "pmAgentId": "agent.company.project-manager",
  "leaseId": "pmlease.company-knowledge-core.20260623T100000Z",
  "leaseGeneration": 8
}
```

Server behavior:

- Parse request.
- Call core function.
- Let core perform PM lease validation before target mutation.
- For PM lease validation errors, return stable `api_error_response()` with `auditRef`.
- Existing `/v0/runners/register`, `/v0/runners/heartbeat`, `/v0/tasks/claim`, `/v0/tasks/heartbeat` stay unchanged.

## 11. CLI Changes

Add `pm-lease` command group:

```bash
zhenzhi-knowledge pm-lease status --project <projectId>
zhenzhi-knowledge pm-lease acquire --project <projectId> --pm-agent <agentId> --session <sessionId> --runner <runnerId> --device <deviceId> --idempotency-key <key>
zhenzhi-knowledge pm-lease heartbeat --project <projectId> --pm-agent <agentId> --lease-id <leaseId> --lease-token <token> --fencing-token <token>
zhenzhi-knowledge pm-lease release --project <projectId> --pm-agent <agentId> --lease-id <leaseId> --lease-token <token> --fencing-token <token> --reason <reason>
zhenzhi-knowledge pm-lease takeover --project <projectId> --to-pm-agent <agentId> --from-lease-id <leaseId> --reason <reason> --idempotency-key <key>
```

For protected PM write commands, add optional `--pm-agent`, `--pm-lease-id`, `--pm-fencing-token`. When actor is a PM Agent or command source is PM scheduling, require those flags and call core validation. Non-PM human/system maintenance commands keep current behavior unless they perform PM scheduling mutation.

## 12. Workbench Read Model Changes

Add optional types in `shared-frontend-foundation.ts` to keep old clients valid:

```ts
export type PMControlLeaseState = {
  primaryPm: DisplayObjectRef;
  lease: DisplayObjectRef;
  project: DisplayObjectRef;
  status: "healthy" | "expiring" | "stale" | "expired" | "released" | "taken_over" | "missing";
  heartbeat: "online" | "degraded" | "offline";
  expiresAt: string;
  lastHeartbeatAt: string;
  leaseGenerationLabel?: string;
  nextAction: string;
  takeoverAction?: WorkbenchAction;
  releaseAction?: WorkbenchAction;
  auditRefs: DisplayObjectRef[];
};

export type ProjectPMParticipantState = {
  pm: DisplayObjectRef;
  role: "primary" | "collaborator" | "standby";
  status: WorkbenchStatus;
  runner?: DisplayObjectRef;
  device?: DisplayObjectRef;
  standbyPriority?: number;
  capabilities: string[];
  nextAction: string;
};

export type PMControlWorkbenchReadModel = {
  currentLease: PMControlLeaseState;
  participants: ProjectPMParticipantState[];
  takeoverRecords: Record<string, unknown>[];
  denialSummaries: Record<string, unknown>[];
  healthExplanation: WorkbenchPanelState;
};
```

Add optional field:

```ts
pmControl?: PMControlWorkbenchReadModel;
```

Core read model changes:

- `scheduler_workbench_read_model()` adds `pmControl`.
- `workbench_project_execution_read_model()` carries `pmControl` and remains `readOnly: True`.
- `v1_workbench_read_model()` adds `pmControl`, PM lease panels in `home`/`recovery`, and `permissionGatedActions` for takeover/release.
- `runnerLeases` remains only task/Runner leases.

Workbench display:

- Primary card: PM name, owner, computer, health, expiresAt, lastHeartbeatAt.
- Collaborator/standby list: role, online state, capabilities, takeover eligibility.
- Denial summary: recent `pm_control_lease.denied` audit grouped by reason code.
- Takeover history: from PM, to PM, reason, completedAt, auditRef.

## 13. Compatibility

Runner compatibility:

- `register_agent_runner()` and `submit_runner_registration()` remain valid with no PM lease.
- `/v0/runners/register` remains compatible with existing direct registration and pairing registration paths.
- Runner heartbeat remains lease-free except existing Runner token/pairing policy.
- `claim_project_task()` and `heartbeat_project_task_lease()` continue using task lease fields and do not require PMControlLease.
- TaskResult and AgentRun writeback continue validating Runner/task lease, not PM lease.

Workbench compatibility:

- New read model fields are optional.
- Existing `schemaVersion: desktop-workbench-read-model.v1` may remain if fields are optional; use `runtimeReadModelKind` or `apiCompatibilityVersion` to signal PM control support.
- Old frontends ignore `pmControl`; new frontends must use central API state and never mutate local Runner lease state.

Data compatibility:

- Existing projects without PMControlLease show `status: missing`, read-only PM scheduling, and next action "Acquire PM control lease".
- Existing PM tasks are not rewritten during migration.
- First acquire creates participant records lazily if project policy allows the PM Agent.

## 14. Non-Regression Test Strategy

Core unit tests:

- Acquire creates one active PMControlLease, participant primary state, and audit.
- Second acquire on healthy active lease is rejected and audited.
- Heartbeat extends expiresAt only for owner with valid token and fencing token.
- Release requires valid lease and blocks later writes.
- Takeover from expired/stale lease creates new lease, increments fencing token, marks old lease, creates takeover record and audit.
- Healthy takeover requires owner confirmation.

Protected write tests:

- Missing lease rejects before target object write.
- Expired lease rejects before target object write.
- Collaborator/non-primary lease rejects before target object write.
- Project mismatch rejects before target object write.
- Stale fencing token rejects before target object write.
- Each rejection writes `pm_control_lease.denied` audit with reason code and readable project/PM context.

API tests:

- New acquire/heartbeat/release/takeover routes return stable JSON and audit refs.
- Protected PM write route returns 409/403 with `api_error_response()` and `auditRef`.
- Unauthorized API token still rejects before PM lease logic.

CLI tests:

- `pm-lease status/acquire/heartbeat/release/takeover` produce JSON or path outputs consistent with current CLI style.
- Protected PM scheduling CLI command requires PM lease flags for PM Agent actor.
- CLI rejection exits non-zero and prints audit ref.

Workbench tests:

- `scheduler_workbench_read_model()` includes `pmControl` for current project.
- `workbench_project_execution_read_model()` remains read-only and includes PM control state.
- `v1_workbench_read_model()` includes primary PM, collaborator/standby list, denial summaries, takeover records, and permission-gated takeover/release actions.
- Missing lease shows safe fallback and does not imply local mutation is allowed.

Runner regression tests:

- Existing Runner registration direct path still passes.
- Pairing registration with idempotency key still passes.
- Runner heartbeat still passes without PM lease.
- Task claim/heartbeat still passes with Runner task lease only.
- TaskResult/AgentRun writeback still uses Runner/task lease validation.
- Existing workbench registration/read-only tests keep passing.

Concurrency/idempotency tests:

- Two concurrent acquire requests for same project produce at most one active lease.
- Retried acquire with same idempotency key returns same lease result.
- Old primary write after takeover fails by fencing token.

Recommended command gates:

```bash
python3 -m unittest tests.test_cli
```

When implementation touches frontend types or generated workbench fixtures, also run the existing workbench verification used by this project.

## 15. Implementation Order

1. Add core model helpers and PM lease lifecycle functions.
2. Add validation guard and rejection audit helper.
3. Thread `pm_write_context` through protected PM scheduling writes.
4. Add API routes.
5. Add CLI `pm-lease` commands and protected write flags.
6. Extend read models and TypeScript optional types.
7. Add lifecycle, rejection, workbench, and Runner regression tests.

## 16. Open Decisions

- Whether heartbeat writes every renewal audit or samples frequent renewals while still recording acquire/release/takeover/denied always.
- Whether healthy takeover confirmation uses existing approval objects or a lightweight `ownerConfirmationRef` first.
- Exact protected write list should be finalized with development agent while threading `pm_write_context`, because current task/project update functions vary by caller.
