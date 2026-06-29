# Enterprise Agent Control Plane v0.1 Release Check

## Scope

This report covers the first release-hardening pass for the enterprise Agent capability control plane.

Target chain:

```txt
Feishu / SourceMaterial / TaskResult
-> CapabilityCandidate
-> Capability Review
-> Human Approval
-> CapabilityRelease
-> Runner pull
-> SkillUsageEvent
-> CapabilityFeedback
-> control read model / API / CLI / trace
```

## 1. New Capabilities

- CapabilityCandidate object for reusable skill/tool/workflow/prompt/playbook/policy/agent-profile candidates.
- CapabilityRelease object for versioned Agent capability release drafts and released packages.
- Capability review and human approval flow before release.
- Runner capability pull package that returns released/active capabilities only.
- Skill usage event and capability feedback objects.
- Capability control read model with counts, candidates, releases, usage, feedback, SkillAsset and ToolAsset views.
- Trace read model for Feishu message, task, material, capability release and runner.
- Feature flags for capability governance, release, Runner pull, Feishu capability actions and knowledge visibility.

## 2. Modified Files

- `zhenzhi_knowledge/core.py`
- `zhenzhi_knowledge/server.py`
- `zhenzhi_knowledge/cli.py`
- `zhenzhi_knowledge/feishu.py`
- `zhenzhi_knowledge/feishu_material_processor.py`
- `tests/test_cli.py`
- `reports/release-check/agent-control-plane-v0.1.md`
- `docs/agent-control-plane/gray-release-plan.md`

## 3. New Object Model

- `CapabilityCandidate`
  - Required identity: `candidateId`, `candidateType`, `status`, `riskLevel`.
  - Required traceability: `sourceMaterialRefs`, `sourceTaskId`, `sourceResultRef`, `evidenceRefs`.
  - Governance fields: `reviewRequired`, `approvalRequired`, `reviewRoute`, `reviewTaskRef`, `approvalTaskRef`, `releaseRefs`.

- `CapabilityRelease`
  - Required identity: `releaseId`, `version`, `status`.
  - Required traceability: `candidateRefs`, `targetAgents`, `targetProjects`.
  - Governance fields: `reviewRequired`, `approvalRequired`, `approvedBy`, `releasedAt`, `usageEventRefs`, `feedbackRefs`.

- `SkillUsageEvent`
  - Required traceability: `usageEventId`, `skillRef`, `skillId`, `releaseRef`, `releaseId`, `runnerId`, `agentId`, `taskId`, `resultRef`.

- `CapabilityFeedback`
  - Required traceability: `feedbackId`, `capabilityRef`, `actor`, `taskId`, `resultRef`, `evidenceRefs`.

- `TraceReadModel`
  - Sections: inbound events, intent, SourceMaterial, Task, Runner claim/finish, TaskResult, KnowledgeItem, CapabilityCandidate, Review, Approval, CapabilityRelease, Notification, AuditLog.

## 4. New API

- `GET /v0/capabilities`
- `GET /v0/runners/{runnerId}/capability-sync`
- `POST /v0/capabilities/candidates`
- `POST /v0/capabilities/review-tasks`
- `POST /v0/capabilities/review`
- `POST /v0/capabilities/approval`
- `POST /v0/capabilities/releases`
- `POST /v0/runners/capability-pull`
- `POST /v0/usage/skill-events`
- `POST /v0/capabilities/feedback`

## 5. New CLI

- `zhenzhi-knowledge capability list`
- `zhenzhi-knowledge capability candidate`
- `zhenzhi-knowledge capability review-task`
- `zhenzhi-knowledge capability review`
- `zhenzhi-knowledge capability approval`
- `zhenzhi-knowledge capability release`
- `zhenzhi-knowledge capability pull`
- `zhenzhi-knowledge capability usage`
- `zhenzhi-knowledge capability feedback`
- `zhenzhi-knowledge trace feishu-message <message-id>`
- `zhenzhi-knowledge trace task <task-id>`
- `zhenzhi-knowledge trace material <source-material-id>`
- `zhenzhi-knowledge trace capability-release <release-id>`
- `zhenzhi-knowledge trace runner <runner-id>`

## 6. Feishu Entry Behavior

- Feishu material cards can classify processing as knowledge extraction, skill extraction, workflow extraction, tool candidate or release draft.
- Normal business/market material stays KnowledgeItem draft and must not produce CapabilityCandidate.
- Agent signals such as skill/tool/workflow/agent/draft can produce capability initial screening, but not direct release.
- Secret/token/credential-looking content is refused or routed to approval; raw secret content is not stored as reusable knowledge.
- Duplicate Feishu message callbacks are idempotent through `.zhenzhi/feishu-message-events/<message_id>.json`.
- Feishu task status notifications write NotificationRecord and delivery attempt state.

## 7. Tests Added Or Updated

- Capability candidate creation from TaskResult.
- Capability release draft creation.
- Capability review and approval before Runner pull.
- Runner pull excludes unreleased releases.
- Runner pull includes approved released capabilities and records sync/install status.
- Usage event links skill/capability ref, release ref, task id and result ref.
- Capability feedback links back to result/task evidence.
- Trace CLI resolves Feishu message to SourceMaterial, Task, TaskResult, CapabilityCandidate, Review, Approval, CapabilityRelease, Notification and AuditLog.
- Direct `released` CapabilityRelease creation is blocked.
- Rejected release cannot be approved later.
- Business/market Feishu material does not force Agent capability judgment.

## 8. Known Risks

- The repository currently has many unrelated dirty and deleted files. They must not be mixed into this release commit.
- `zhenzhi_knowledge/feishu_material_processor.py` is currently untracked but required by this release.
- Trace read model is local markdown/JSON based; it is sufficient for v0.1 but not optimized for very large historical bundles.
- Feishu live delivery still needs real bot credentials and real chat membership verification in gray release.
- Runner install/sync status is represented in pull response and AuditLog, not yet a dedicated persistent RunnerSync object.

## 9. Unresolved Issues

- No production migration is included for existing historical capability-like records.
- No UI screen is included in this release-hardening pass.
- No live Feishu OpenAPI call was run in this pass.
- No remote Agent Ring runner was exercised in this pass.

## 10. Manual Acceptance Steps

1. Create a Feishu material card with common scope and `skill_extract`.
2. Confirm `SourceMaterial` is created under `projects/company-knowledge-core/sources/`.
3. Confirm a `KnowledgeTask` or `ProjectTask` is created and includes `capabilityProcessingAction`.
4. Finish the task with a `capabilityCandidates` payload.
5. Run `zhenzhi-knowledge capability list` and confirm the candidate is `pending_review`.
6. Create review task with `zhenzhi-knowledge capability review-task`.
7. Apply review with `needs_human_approval`.
8. Create a draft release with `zhenzhi-knowledge capability release`.
9. Run `zhenzhi-knowledge capability pull --runner-id <runner>` and confirm no release is returned before approval.
10. Apply human approval with the release ref.
11. Run `zhenzhi-knowledge capability pull --runner-id <runner>` and confirm release is returned with `syncStatus=synced`.
12. Record usage with `zhenzhi-knowledge capability usage --release-ref <release-ref>`.
13. Record feedback with `zhenzhi-knowledge capability feedback`.
14. Run `zhenzhi-knowledge trace feishu-message <message-id>` and confirm all chain sections are visible.
15. Check `knowledge/audit/` for create/review/approval/pull/usage/feedback audit records.

## 11. E2E Scenario Coverage

| Scenario | Status | Evidence |
| --- | --- | --- |
| Feishu webpage material -> SourceMaterial -> Task -> Runner -> TaskResult -> KnowledgeCandidate / CapabilityCandidate -> Review -> Feishu notification | Partly automated | SourceMaterial/Task/TaskResult/CapabilityCandidate/Review/Notification covered; live Feishu delivery remains manual. |
| Meeting notes -> KnowledgeTask -> KnowledgeCandidate, not directly verified | Existing coverage plus manual check | Knowledge review tests keep reusable knowledge draft/reviewable before verified. |
| Business/market material -> KnowledgeItem draft, no CapabilityCandidate | Automated | `test_feishu_business_material_does_not_force_agent_capability_judgment`. |
| skill/tool/workflow/agent signal -> capability screening, Review/Approval before Release | Automated | Capability review/approval/pull tests. |
| secret/token/credential request -> no knowledge write, no plaintext reply, approval/refusal | Existing automated coverage | Secret material refusal and token approval tests. |
| duplicate Feishu message callback -> no duplicate object | Existing automated coverage | Feishu retry/idempotency tests. |
| forged Feishu card projectId/taskId -> server rejects and writes Audit | Existing automated coverage | Feishu card scope/permission tests; manual replay recommended. |
| Runner claim timeout -> lease release or retry/handoff | Existing automated coverage | Retry/manual handoff lease tests. |
| Capability Release before approval -> Runner cannot pull active release | Automated | New release boundary assertions. |
| Capability Release after approval -> Runner pull succeeds and records sync/install state | Automated | Capability approval/pull test. |
| Runner usage event and feedback link skill/release/task | Automated | Usage event and feedback assertions. |
| Feishu notification failure -> delivery attempt + repair notification, no duplicate business side effect | Existing automated coverage | Notification failure/repair tests. |
| No DATABASE_URL -> retrieval fallback works | Existing automated coverage | Knowledge query fallback tests. |
| High-risk content excluded from normal retrieval | Existing automated coverage | Search and sensitivity tests; manual high-risk capability check recommended. |
| message_id traces complete chain | Automated | New trace CLI test. |

## 12. Rollback

1. Disable rollout with feature flags:
   - `CAPABILITY_RELEASE_ENABLED=false`
   - `CAPABILITY_AUTO_PUBLISH_ENABLED=false`
   - `CAPABILITY_RUNNER_AUTO_PULL_ENABLED=false`
   - `FEISHU_CAPABILITY_ACTIONS_ENABLED=false`
2. Stop approving new `capability_approval` tasks.
3. Mark affected `CapabilityRelease` records as `disabled` or `rejected`.
4. Ask runners to pull again; released package will no longer include disabled/unreleased capability records.
5. Keep `SourceMaterial`, `Task`, `TaskResult`, `NotificationRecord` and `AuditLog`; do not delete trace records during rollback.
6. If code rollback is needed, revert only this release commit, not unrelated dirty working tree changes.
