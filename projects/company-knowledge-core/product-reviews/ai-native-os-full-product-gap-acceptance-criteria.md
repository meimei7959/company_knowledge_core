---
type: ReviewRecord
title: AI Native OS full product gap acceptance criteria
description: Product Manager Agent acceptance criteria and release boundaries for the seven AI Native OS product gaps.
timestamp: "2026-06-21T12:55:53Z"
reviewId: review.ai-native-os-full-product-gap-acceptance-criteria
taskId: kt-ai-native-os-gap-product-acceptance-criteria
projectId: company-knowledge-core
reviewer: agent.company.product-manager
runnerId: runner.meimei-mac-local-product-rt
status: accepted
verdict: accepted
sensitivity: internal
sourceRefs:
  - .zhenzhi/context/task.kt-ai-native-os-gap-product-acceptance-criteria.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-gap-product-acceptance-criteria.md
  - projects/company-knowledge-core/product-reviews/ai-native-os-requirement-tree-final-product-acceptance.md
  - projects/company-knowledge-core/coordination/ai-native-os-full-product-gap-execution-plan.md
  - docs/product/ai-native-os/requirement-tree.md
  - docs/product/ai-native-os/requirements.md
  - docs/product/ai-native-os/test-cases.md
  - docs/product/ai-native-os/acceptance-checklist.md
---

# Product Verdict

Verdict: `accepted`.

These criteria are accepted as the product gate for releasing the next technical, design, and test planning workstreams into product review. They do not accept any implementation as complete, do not replace Test Agent pass/fail judgment, and do not release implementation tasks by themselves.

# Release Boundary

- Allowed to proceed: technical/design/test solution tasks for GAP-001 through GAP-007 may enter product review against this document.
- Not allowed to proceed yet: implementation tasks that claim launch readiness, full AI Native OS completion, or complete ANOS promotion.
- Implementation release rule: each implementation task must reference the relevant gap criteria, have a paired Test Agent task, and preserve role boundaries for Development, Design, Test, Product, and Project Manager Agents.
- Product acceptance question: "Has the gap produced user-visible, durable, auditable product capability with mapped evidence?"
- Backfill boundary: inferred, needs_review, non-execution-unlocking historical mappings can support context only. They cannot complete a gap without live execution, test, and acceptance evidence.

# Requirement Tree Mapping Baseline

- Business requirements: BR-001 through BR-005.
- User requirements: UREQ-001 through UREQ-015.
- Functional requirements: 74 ANOS requirements in `docs/product/ai-native-os/requirements.md`.
- Test references: 84 test cases in `docs/product/ai-native-os/test-cases.md`.
- Launch gates: acceptance checklist gates in `docs/product/ai-native-os/acceptance-checklist.md`.

# Requirement Coverage Statement

The seven gap criteria cover all product requirement layers:

| Layer | Count | Coverage Method |
| --- | ---: | --- |
| Business requirements | 5 | BR-001 to BR-005 are accepted only through launch-level evidence in GAP-006 and GAP-007, with direct capability evidence in GAP-001 to GAP-005. |
| User requirements | 15 | UREQ-001 to UREQ-015 are covered by the gap-specific user paths below; UREQ-008 remains blocked until Agent Ring Console/live runner evidence exists. |
| Functional requirements | 74 | All 16 ANOS domains are covered: Agent Hub, Requirement Center, PRD/Decision, Project Console, Agent Team, Scheduler, Agent Ring, Result, Knowledge, Review, Tool/Skill, Quality/Eval, Notification, Admin/Governance, Operations, API/Gateway. |

Coverage is not the same as completion. A BR, UREQ, or ANOS is launch-accepted only when the mapped gap has user-visible or operational behavior, durable records, permission/audit proof, Test Agent evidence, and Product Manager reviewer-readable conclusion.

# Launch And Blocker Standard

上线口径:

- `accepted`: the gap may release only when all complete criteria, evidence refs, Test Agent result, and acceptance gate checks pass for the mapped requirement scope.
- `changes_requested`: the plan or delivered artifact misses product scope, user path, evidence ownership, readable status, permissions/audit, or launch-boundary clarity, but can be fixed by design/development/test rework.
- `blocked`: a required live environment, external permission, runner, integration, data store, reviewer decision, or security condition is unavailable; blocker must name owner, recovery condition, next task, and launch exclusion.

阻塞条件:

- Any launch-critical ANOS remains `not_started`, `partial`, or `blocked` without signed exception.
- ANOS-REQ-060 to ANOS-REQ-063 lack real runner console/API lifecycle evidence.
- Feishu/API/PostgreSQL live paths are skipped, mocked, or cannot produce audit-backed evidence.
- Test Agent has not executed mapped critical tests, or Product Manager cannot trace BR -> UREQ -> ANOS -> test -> acceptance gate -> evidence.

# Gap Acceptance Criteria

## GAP-001: Agent Ring Console Productization

Scope: Productize the central view and controls for Agent Ring runners.

Coverage:

| Layer | Covered IDs |
| --- | --- |
| BR | BR-001, BR-003, BR-005 |
| UREQ | UREQ-004, UREQ-005, UREQ-008, UREQ-013 |
| ANOS | ANOS-REQ-030 to 034, 050 to 053, 060 to 063, 070 to 073, 100 to 102, 120 to 122, 130 to 133, 150 to 152 |
| Tests / gates | TC-PROJ-004, TC-RUN-001 to 004, TC-SCH-001 to 004, TC-RES-001 to 004, TC-ADM-001 to 004, TC-API-001 to 004, AC-UI-004, AC-EXE-001 to 005, AC-GOV-003, AC-OPS-001 |

Complete means:

- Runner registry shows runner id, machine, owner, heartbeat, load, status, allowed Agents, tools, repositories, and data scopes.
- Lease and task history show active, completed, failed, stale, cancelled, retried, and escalated states with readable next action.
- Manual handoff path writes AgentRun or equivalent record, TaskResult, NotificationRecord, and AuditLog.
- Scope/audit controls block unauthorized source, repo, tool, or knowledge access and show a readable reason.
- Admin can identify which runner can execute which work and repair or escalate stale/failed leases.

Partial or blocked means:

- Partial: registry or lease data exists but lacks UI, repair path, scope/audit evidence, or user-readable status.
- Blocked: runner authorization, lease history, manual handoff writeback, or audit cannot be proven with real runner evidence.

Acceptable evidence:

- Runner console screenshots or UI state captures tied to durable runner records.
- API/CLI evidence for registration, claim, heartbeat, stale lease, cancel, retry, finish, and unauthorized access.
- TaskResult, AgentRun, NotificationRecord, and AuditLog refs from at least one real manual handoff and one stale/failure repair path.
- Test Agent report mapping TC-RUN-001 to 004 and AC-UI-004 / AC-EXE gates.

Non-goals that cannot count as complete:

- Static runner list, mock JSON, or design-only console.
- Local manual notes without durable TaskResult/AgentRun/Notification/AuditLog.
- Scheduler-only lease tests that do not expose runner admin product state.

## GAP-002: Complete Cross-Platform Desktop Client UI

Scope: Deliver the desktop client as the user-facing shell for the AI Native OS product, not just a read model or Slice 0.

Coverage:

| Layer | Covered IDs |
| --- | --- |
| BR | BR-001, BR-002, BR-003, BR-004, BR-005 |
| UREQ | UREQ-001 through UREQ-015 |
| ANOS | All 74 ANOS requirements as displayed or operated through the desktop product shell, with special focus on ANOS-REQ-030 to 034, 040 to 045, 060 to 063, 070 to 073, 090 to 093, 110 to 114, 120 to 122, 130 to 133 |
| Tests / gates | TC-PROJ-001 to 005, TC-AGENT-001 to 007, TC-RUN-001 to 004, TC-REV-001 to 004, TC-MET-001 to 005, TC-NOT-001 to 003, TC-ADM-001 to 004, AC-UI-001 to 007, AC-PROD-002 to 004 |

Complete means:

- Desktop runtime supports packaged install, signed build or explicit internal exception, update path, secure storage, deep links, runner pairing, offline/permission states, and enterprise network constraints.
- Complete navigation exposes Requirement Center, Project Console, Agent Team Manager, Agent Ring Console, Result Center, Review Center, Quality Dashboard, Notification Center, Admin/Governance, Operations/Feedback, and Knowledge Query entry points.
- Each screen shows readable labels, owner, status, next action, evidence, and safe fallback states before raw internal ids.
- Product can execute or route the first release workflows without relying on hidden CLI-only steps for core user decisions.

Partial or blocked means:

- Partial: desktop shows only read-only project/workbench state or one slice without runtime packaging, secure storage, runner pairing, or full console coverage.
- Blocked: desktop cannot be installed/run in target environment, cannot protect secrets/session state, or cannot expose key review/execution actions.

Acceptable evidence:

- Desktop builds for target platforms or signed internal release with documented exception.
- UI verification across primary flows, screen states, error states, permission states, and deep links.
- Design Agent acceptance for UX/information architecture and Test Agent report for AC-UI-001 to 007.
- Evidence that user-facing text is readable and maps to durable state.

Non-goals that cannot count as complete:

- Web-only console, markdown dashboard, CLI output, mock prototype, or Desktop Slice 0 read model alone.
- Screenshots without runnable build and state-backed interaction.
- Desktop shell that hides critical governance/review/runner actions behind manual operator knowledge.

## GAP-003: Live Distributed Agent Ring Execution

Scope: Prove distributed runner execution under central governance.

Coverage:

| Layer | Covered IDs |
| --- | --- |
| BR | BR-001, BR-003, BR-005 |
| UREQ | UREQ-004, UREQ-005, UREQ-008, UREQ-012, UREQ-013 |
| ANOS | ANOS-REQ-050 to 056, 060 to 063, 070 to 073, 100 to 102, 110 to 114, 120 to 122, 130 to 133, 150 to 152 |
| Tests / gates | TC-E2E-004, TC-SCH-001 to 007, TC-RUN-001 to 004, TC-RES-001 to 004, TC-MET-001 to 005, AC-EXE-001 to 005, AC-OPS-001, AC-TEST-003 |

Complete means:

- At least two real runners, or an approved equivalent distributed environment, claim and execute centrally scheduled tasks.
- Claim, heartbeat, stale lease, cancel, retry, reassignment, finish, and invalid finish are proven.
- TaskResult, AgentRun, NotificationRecord, AuditLog, metrics, and runner history update from distributed execution.
- Unauthorized runner/tool/repo/scope access fails safely and is audited.

Partial or blocked means:

- Partial: one local runner proves manual workflow, or distributed flow lacks failure/retry/cancel/stale evidence.
- Blocked: Agent Ring cannot claim tasks with durable lease, cannot write results back, or cannot enforce runner scope.

Acceptable evidence:

- Runner registry and lease logs for two runners or approved distributed equivalent.
- TaskResult/AgentRun refs from success, stale lease, retry/cancel, and unauthorized access cases.
- Test Agent report for scheduler/runner tests and E2E runner scenario.
- Metrics or dashboard proof for throughput, blocked/stale rate, and runner heartbeat.

Non-goals that cannot count as complete:

- Single-machine manual runner execution.
- Simulated lease records with no runner writeback.
- Passing unit tests without live distributed state transition evidence.

## GAP-004: Feishu/API Live Delivery

Scope: Prove real Feishu and API gateway intake, callback, notification, and audit paths.

Coverage:

| Layer | Covered IDs |
| --- | --- |
| BR | BR-001, BR-002, BR-004, BR-005 |
| UREQ | UREQ-001, UREQ-002, UREQ-003, UREQ-006, UREQ-009, UREQ-010, UREQ-011, UREQ-014, UREQ-015 |
| ANOS | ANOS-REQ-001 to 006, 010 to 016, 020 to 024, 070 to 073, 080 to 084, 090 to 093, 120 to 122, 130 to 133, 150 to 152 |
| Tests / gates | TC-E2E-001 to 003, TC-HUB-001 to 007, TC-REQ-001 to 007, TC-PRD-001 to 005, TC-KNO-001 to 005, TC-REV-001 to 004, TC-NOT-001 to 003, TC-API-001 to 004, AC-PROD-003, AC-REQ-001 to 005, AC-GOV-001 to 004 |

Complete means:

- Real Feishu message, document link/file reference, card callback, async continuation, and notification path create durable source, requirement/task/status/review records.
- API gateway validates create/update/query/approve/reject/claim/finish-like write paths and produces audit records.
- Permission failure, duplicate callback, long-running callback, failed notification, and unreadable output are handled with safe user-facing recovery.
- Feishu, API, CLI, and console read the same central state and do not diverge in status semantics.

Partial or blocked means:

- Partial: API or Feishu path works alone but cross-channel state, callback recovery, permissions, or notification repair is missing.
- Blocked: live Feishu credential/scope/callback cannot be verified, or API writes cannot be audited.

Acceptable evidence:

- Real Feishu event/card/message records with redacted secrets and linked SourceMaterial/ProjectTask/Notification/AuditLog refs.
- API validation evidence for authorized and unauthorized requests.
- Duplicate callback and failure recovery evidence.
- Test Agent report for Agent Hub, API/integration, notification, and review gates.

Non-goals that cannot count as complete:

- Offline payload samples, mocked Feishu responses, or CLI-created records that bypass live callback.
- API endpoint existence without auth, validation, audit, and readable error behavior.
- Raw internal ids as primary user-facing explanation.

## GAP-005: PostgreSQL/API Route Live Acceptance

Scope: Prove operational store and API routes are live, durable, reversible, permissioned, and observable.

Coverage:

| Layer | Covered IDs |
| --- | --- |
| BR | BR-001, BR-002, BR-003, BR-004, BR-005 |
| UREQ | UREQ-001 through UREQ-015 |
| ANOS | ANOS-REQ-001 to 006, 010 to 016, 030 to 034, 040 to 045, 050 to 056, 060 to 063, 070 to 073, 080 to 084, 090 to 093, 100 to 102, 110 to 114, 120 to 122, 130 to 133, 140 to 142, 150 to 152 |
| Tests / gates | TC-API-001 to 004 plus all route-backed TC groups, AC-GOV-003, AC-OPS-002, AC-PROD-003, AC-TEST-004 |

Complete means:

- PostgreSQL or approved operational store is the durable source for production routes in scope, with migrations, rollback plan, backup/restore status, and environment config documented.
- API routes cover requirement, project, task, runner, result, review, knowledge query, notification, metrics, admin, and integration gateway surfaces in the release scope.
- Writes are permission-checked, validated, audited, and observable.
- Known skips are removed or documented as signed exceptions with product impact and non-launch boundary.

Partial or blocked means:

- Partial: store/routes work for subset but skips, rollback, auth, audit, or observability remain incomplete.
- Blocked: live database route cannot be exercised, migration is unsafe, or skip hides launch-critical behavior.

Acceptable evidence:

- Migration and rollback logs, route validation records, backup/restore status, and API auth/audit evidence.
- Test Agent report covering live API route acceptance and regression gates.
- Documented exception for any remaining skip with owner, expiry, and product boundary.

Non-goals that cannot count as complete:

- In-memory store, fixture-backed tests, or markdown-only records for launch claims.
- Green unit tests while live API route or database path remains skipped.
- Operational store without restore procedure or audit-backed write controls.

## GAP-006: Traceability Promotion From Partial/Blocked To Complete Or Explicitly Blocked

Scope: Turn the 70 partial and 4 blocked ANOS statuses into evidence-backed complete status or explicit continuing blockers.

Coverage:

| Layer | Covered IDs |
| --- | --- |
| BR | BR-001, BR-002, BR-003, BR-004, BR-005 |
| UREQ | UREQ-001 through UREQ-015 |
| ANOS | All 74 ANOS requirements |
| Tests / gates | All mapped test cases plus AC-REQ-005, AC-TEST-001, AC-TEST-005, AC-PROD-004 |

Complete means:

- Each ANOS has requirement-tree source, implementation/result evidence, test evidence, acceptance gate evidence, owner, status, and reviewer-readable conclusion.
- `complete` is used only when evidence proves observable product behavior, not inferred historical work.
- `blocked` has owner, reason, missing evidence/capability, next action, and release impact.
- The 5 BR / 15 UREQ / 74 ANOS mapping remains intact and can explain which user/business requirement each promotion satisfies.

Partial or blocked means:

- Partial: evidence exists for implementation or tests but not both, or acceptance gate/reviewer conclusion is missing.
- Blocked: required runtime, user path, permission, external integration, or test evidence cannot be produced.

Acceptable evidence:

- Promotion matrix with one row per ANOS and links to TaskResult, code/design/API/runner evidence, Test Agent evidence, and acceptance gate.
- Diff or generated report showing counts before and after promotion.
- Product Manager review confirming no inferred mapping became execution-unlocking without evidence.

Non-goals that cannot count as complete:

- Renaming `partial` to `complete` without new evidence.
- Using backfill_inferred mappings as product completion.
- Completing UREQ/BR rollups when any launch-critical child ANOS remains partial or blocked without signed exception.

## GAP-007: Launch Acceptance Evidence Matrix

Scope: Build the release evidence matrix that lets Product, Project, Test, Design, Development, and human reviewers make launch decisions without reconstructing history.

Coverage:

| Layer | Covered IDs |
| --- | --- |
| BR | BR-001, BR-002, BR-003, BR-004, BR-005 |
| UREQ | UREQ-001 through UREQ-015 |
| ANOS | All 74 ANOS requirements |
| Tests / gates | All 84 test cases and all acceptance checklist gates |

Complete means:

- Matrix maps BR -> UREQ -> ANOS -> test case -> acceptance checklist gate -> evidence refs -> owner -> verdict -> exception/blocker.
- Every TC has execution result or explicit not-run/blocker reason owned by Test Agent.
- Every launch gate is pass, blocked, or signed exception; no silent unknowns.
- Product can answer launch readiness by product area, role, runner, integration, governance risk, and release boundary.

Partial or blocked means:

- Partial: matrix exists but lacks execution evidence, owner, exception reason, or reviewer-readable conclusion.
- Blocked: evidence sources cannot be reconciled, test result ownership is missing, or gate count/coverage discrepancies remain unresolved.

Acceptable evidence:

- Evidence matrix artifact with stable row ids and links to source requirements, tests, gates, TaskResults, reviews, and audit.
- Test Agent report for test execution status and unresolved blockers.
- PM/Project Manager review showing launch stop conditions checked.

Non-goals that cannot count as complete:

- Requirement/test mapping without execution evidence.
- A pass/fail claim written by Product Manager instead of Test Agent.
- A launch summary that hides partial/blocked ANOS, skip reasons, or exception owners.

# Product Acceptance Vocabulary

- `complete`: product behavior exists, is durable, user-visible where relevant, permissioned, audited, mapped to BR/UREQ/ANOS, and has Test Agent evidence plus launch gate evidence.
- `partial`: some artifacts or behavior exist, but user-visible flow, live runtime, external integration, permission/audit, tests, or launch gate evidence is incomplete.
- `blocked`: required evidence or capability cannot currently be produced; blocker has owner, reason, next action, release impact, and review route.
- `not_started`: no material evidence beyond requirement or planning record.

# Technical Solution Review Permission

Corresponding technical, design, and test solution tasks may enter product review if they explicitly reference these criteria and state which gap they cover. They may not claim product completion or launch readiness until implementation and Test Agent evidence satisfy the relevant complete criteria.
