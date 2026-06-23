---
type: ReviewRecord
title: AI Native OS launch acceptance evidence matrix
projectId: company-knowledge-core
taskId: kt-ai-native-os-gap-test-launch-evidence-matrix
status: submitted
ownerAgent: agent.company.test
runnerId: runner.meimei-mac-local-test-1
generatedAt: 2026-06-21
sourceRefs:
  - .zhenzhi/context/task.kt-ai-native-os-gap-test-launch-evidence-matrix.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-gap-test-launch-evidence-matrix.md
  - docs/product/ai-native-os/test-cases.md
  - docs/product/ai-native-os/acceptance-checklist.md
  - projects/company-knowledge-core/product-reviews/ai-native-os-requirement-tree-final-product-acceptance.md
  - projects/company-knowledge-core/requirements/backfills/requirement-tree-existing-work-backfill.20260621112327.json
---

# AI Native OS Launch Acceptance Evidence Matrix

## Decision Summary

This matrix is a launch acceptance evidence plan, not an implementation change and not a launch approval.

Current launch posture remains **not complete-launch ready** until every item below has execution evidence. Existing backfill is useful as traceability baseline only:

- 84 source test cases are present in `docs/product/ai-native-os/test-cases.md`.
- 44 source acceptance gates are present in `docs/product/ai-native-os/acceptance-checklist.md`.
- Backfill has 74 functional requirement records: 70 `partial`, 4 `blocked`, 0 `completePromotions`, 0 `executionUnlockingMappings`.
- Backfill maps 38 unique acceptance gates; source checklist has 44. Missing from generated mapping: `AC-PROD-001`, `AC-PROD-002`, `AC-PROD-004`, `AC-UI-005`, `AC-OPS-002`, `AC-OPS-005`.
- The 4 blocked requirements are `ANOS-REQ-060`, `ANOS-REQ-061`, `ANOS-REQ-062`, `ANOS-REQ-063`, all tied to `TC-RUN-001` to `TC-RUN-004`, `TC-E2E-004`, `AC-EXE-002`, `AC-EXE-003`, and `AC-UI-004`.

## Evidence Levels

| Evidence level | Required artifact | Completes what |
| --- | --- | --- |
| Automated evidence | Deterministic test command, exit status, log path or EvalRun, linked to test IDs and requirement IDs. | Proves repeatable behavior and regression safety. |
| Manual evidence | Reviewer-readable checklist result with owner, date, pass/fail/exception, screenshots or notes, linked to acceptance gate IDs. | Proves product judgment, usability, and launch gate review. |
| Live evidence | Real integration or production-like run with external service, runner, API route, storage, notification, audit, and recovery proof where applicable. | Proves design/stub evidence has become launch evidence. |

Promotion rule: a requirement may move from `partial` to `complete` only when all mapped tests pass, all mapped acceptance gates have manual review, required live evidence exists, and the reviewer conclusion is readable without reconstructing raw logs.

Blocked continuation rule: a requirement may remain `blocked` only when the missing external condition is explicit, owner/date/next action are recorded, and launch claim excludes the blocked capability.

## Product Gap Matrix

| Gap | Launch scope | Tests covered | Gates covered | Automated evidence required | Manual evidence required | Live evidence required | Promotion or block decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `AI-NATIVE-OS-PROD-GAP-001` Agent Ring Console | Runner registry, lease/history, manual handoff, scope/audit UI and API for `ANOS-REQ-060` to `063`. | `TC-RUN-001`, `TC-RUN-002`, `TC-RUN-003`, `TC-RUN-004`, `TC-E2E-004`, plus scheduler regressions `TC-SCH-002` to `TC-SCH-004`. | `AC-EXE-002`, `AC-EXE-003`, `AC-UI-004`. | Console API tests for runner registration, heartbeat, active lease, stale lease, unauthorized repo, finish rejection, audit creation. | PM/Test review of console screens: machine, owner, heartbeat, load, scopes, current leases, history, handoff, audit trail. | At least one real runner registered and executing through console-visible lifecycle; stub-only result cannot unblock. | Blocks full launch until `ANOS-REQ-060` to `063` have live runner evidence. |
| `AI-NATIVE-OS-PROD-GAP-002` Full desktop client UI | Desktop runtime, full console, packaging/signing/update, secure storage, deep link, runner pairing, offline/permission states. | `TC-PROJ-001` to `TC-PROJ-005`, `TC-HUB-001` to `TC-HUB-007`, `TC-E2E-001`, `TC-E2E-002`, `TC-E2E-006`, relevant `TC-ADM-*`. | `AC-UI-001` to `AC-UI-007`, `AC-PROD-003`, `AC-OPS-003`. | Desktop UI regression, state transition tests, permission/offline negative tests, packaging smoke. | Usability acceptance on project hub, queue, blockers, next actions, notifications, readable human output. | Signed packaged desktop client or documented production-like install path; live pairing to runner/API. | Partial desktop slice evidence can promote only after full desktop workflow and packaging evidence exist. |
| `AI-NATIVE-OS-PROD-GAP-003` Live distributed Agent Ring execution | Multi-runner or equivalent real distributed lifecycle: claim, heartbeat, stale lease, cancel, retry, finish, TaskResult, AgentRun, Notification, AuditLog. | `TC-E2E-004`, `TC-SCH-001` to `TC-SCH-007`, `TC-RUN-001` to `TC-RUN-004`, `TC-RES-001` to `TC-RES-004`, `TC-NOT-001` to `TC-NOT-003`. | `AC-EXE-001` to `AC-EXE-005`, `AC-GOV-004`, `AC-OPS-001`, `AC-OPS-004`. | Lifecycle contract tests with lease token rejection, stale lease, cancel/retry, duplicate finish, notification and audit assertions. | Test Agent review of failure-mode messages and owner-visible blockers/next actions. | At least two runners or equivalent separate execution contexts; live TaskResult/AgentRun/Notification/AuditLog written. | Stub runner/protocol evidence remains non-execution-unlocking until live distributed proof exists. |
| `AI-NATIVE-OS-PROD-GAP-004` Feishu/API live delivery | Real Feishu messages/cards/callbacks/API gateway with permission failure, duplicate callback, notification, audit, readable output. | `TC-HUB-001` to `TC-HUB-007`, `TC-NOT-001` to `TC-NOT-003`, `TC-API-001` to `TC-API-004`, `TC-E2E-001`, `TC-E2E-002`, `TC-E2E-006`. | `AC-PROD-003`, `AC-REQ-001`, `AC-REQ-002`, `AC-UI-001`, `AC-UI-003`, `AC-OPS-003`, `AC-OPS-004`. | API gateway tests for create/read/write/auth failure, idempotent callback handling, audit writes. | Human review of Feishu cards/messages for readable status, blockers, owner, source, and next action. | Real Feishu bot/user flow and callback replay evidence; local mocks are regression evidence only. | Can promote Feishu partial evidence only after real live callback and notification audit evidence. |
| `AI-NATIVE-OS-PROD-GAP-005` PostgreSQL/API route live acceptance | Operational store, API routes, migration, rollback, permissions, observability; skip must be removed or explicitly justified. | `TC-API-001` to `TC-API-004`, `TC-ADM-001` to `TC-ADM-004`, `TC-MET-001` to `TC-MET-005`, `TC-OPS-002`. | `AC-OPS-001` to `AC-OPS-005`, `AC-GOV-003`, `AC-TEST-005`, `AC-REQ-005`. | Migration/rollback tests, permission-negative API tests, health/metrics/backup restore checks. | Ops/Test review of dashboards, backup status, migration notes, skipped-test rationale. | Live PostgreSQL-backed API route smoke with real database URL, restore proof, and audit/metrics evidence. | Any unexplained skip in operational store or API route remains launch-blocking. |
| `AI-NATIVE-OS-PROD-GAP-006` Traceability promotion plan | Convert 70 partial / 4 blocked to complete or explicit continued-blocked records. | All 84 test cases, with requirement-specific subsets from backfill. | All 44 source gates, including the 6 missing from generated mapping. | Per requirement: test run evidence linked to `functionalRequirementRef`, `testCaseRefs`, result path, command, status. | Per gate: reviewer-readable acceptance result with owner and conclusion. | Required for runner/API/Feishu/desktop/storage paths; not required for pure docs unless acceptance says so. | No requirement may be promoted by inferred mapping alone. Every promotion requires execution-unlocking evidence. |
| `AI-NATIVE-OS-PROD-GAP-007` Launch acceptance evidence matrix | Convert design references into release decision evidence. | All 84 test cases listed below. | All 44 source gates listed below; reconcile source/generated difference. | Matrix lint/check that all test IDs and gate IDs have evidence state, owner, and result reference. | PM review of release blocking criteria and signed exception list. | Live evidence status rollup from gaps 001 to 005. | This document is ready for PM review, but does not itself release the product. |

## 84-Test Coverage Ledger

| Area | Count | Test IDs | Launch evidence owner |
| --- | ---: | --- | --- |
| End-To-End Tests | 7 | `TC-E2E-001`, `TC-E2E-002`, `TC-E2E-003`, `TC-E2E-004`, `TC-E2E-005`, `TC-E2E-006`, `TC-E2E-007` | Test Agent plus PM for complete-flow judgment. |
| Agent Hub Tests | 7 | `TC-HUB-001`, `TC-HUB-002`, `TC-HUB-003`, `TC-HUB-004`, `TC-HUB-005`, `TC-HUB-006`, `TC-HUB-007` | Test Agent plus Feishu/API owner for live intake. |
| Requirement And PRD Tests | 12 | `TC-REQ-001`, `TC-REQ-002`, `TC-REQ-003`, `TC-REQ-004`, `TC-REQ-005`, `TC-REQ-006`, `TC-REQ-007`, `TC-PRD-001`, `TC-PRD-002`, `TC-PRD-003`, `TC-PRD-004`, `TC-PRD-005` | Product/Test Agents. |
| Project Console Tests | 5 | `TC-PROJ-001`, `TC-PROJ-002`, `TC-PROJ-003`, `TC-PROJ-004`, `TC-PROJ-005` | Test Agent plus desktop/console owner. |
| Agent Team Tests | 7 | `TC-AGENT-001`, `TC-AGENT-002`, `TC-AGENT-003`, `TC-AGENT-004`, `TC-AGENT-005`, `TC-AGENT-006`, `TC-AGENT-007` | Steward/Test Agents. |
| Scheduler And Runner Tests | 11 | `TC-SCH-001`, `TC-SCH-002`, `TC-SCH-003`, `TC-SCH-004`, `TC-SCH-005`, `TC-SCH-006`, `TC-SCH-007`, `TC-RUN-001`, `TC-RUN-002`, `TC-RUN-003`, `TC-RUN-004` | Test Agent plus Agent Ring owner. |
| Result And Knowledge Tests | 9 | `TC-RES-001`, `TC-RES-002`, `TC-RES-003`, `TC-RES-004`, `TC-KNO-001`, `TC-KNO-002`, `TC-KNO-003`, `TC-KNO-004`, `TC-KNO-005` | Test Agent plus Knowledge Review Agent. |
| Review, Tool, Skill Tests | 7 | `TC-REV-001`, `TC-REV-002`, `TC-REV-003`, `TC-REV-004`, `TC-REG-001`, `TC-REG-002`, `TC-REG-003` | Governance/Test Agents. |
| Metrics, Notification, Admin, Ops Tests | 15 | `TC-MET-001`, `TC-MET-002`, `TC-MET-003`, `TC-MET-004`, `TC-MET-005`, `TC-NOT-001`, `TC-NOT-002`, `TC-NOT-003`, `TC-ADM-001`, `TC-ADM-002`, `TC-ADM-003`, `TC-ADM-004`, `TC-OPS-001`, `TC-OPS-002`, `TC-OPS-003` | Ops/Test Agents. |
| API And Integration Tests | 4 | `TC-API-001`, `TC-API-002`, `TC-API-003`, `TC-API-004` | API/Test Agents. |

Launch rule for all 84 tests: every test must have `not_run`, `passed`, `failed`, `waived`, or `blocked` state. Launch can proceed only when no critical test is `not_run` or `failed`, and every `waived` or `blocked` test has signed PM exception and scope exclusion.

## Acceptance Gate Ledger

Source gate count is 44. Generated/backfill unique gate count is 38. Launch must use source count until product owner approves a checklist revision.

| Gate area | Count | Gate IDs | Evidence requirement |
| --- | ---: | --- | --- |
| Product Acceptance | 4 | `AC-PROD-001`, `AC-PROD-002`, `AC-PROD-003`, `AC-PROD-004` | PM acceptance note, complete-flow evidence, no-MVP-leakage statement. |
| Requirement Acceptance | 5 | `AC-REQ-001`, `AC-REQ-002`, `AC-REQ-003`, `AC-REQ-004`, `AC-REQ-005` | Requirement object audit, clarification block proof, PRD review, decision approval, traceability links. |
| Agent Acceptance | 5 | `AC-AGENT-001`, `AC-AGENT-002`, `AC-AGENT-003`, `AC-AGENT-004`, `AC-AGENT-005` | Role/capability/skill/tool health checks and handoff evidence. |
| Execution Acceptance | 5 | `AC-EXE-001`, `AC-EXE-002`, `AC-EXE-003`, `AC-EXE-004`, `AC-EXE-005` | Scheduler/runner lifecycle evidence, leases, cancellation, retry, result writeback, audit. |
| Knowledge Acceptance | 4 | `AC-KNO-001`, `AC-KNO-002`, `AC-KNO-003`, `AC-KNO-004` | Source-first capture, review gate, sensitivity handling, reusable knowledge status proof. |
| Review And Governance Acceptance | 4 | `AC-GOV-001`, `AC-GOV-002`, `AC-GOV-003`, `AC-GOV-004` | Human review, policy gate, tool approval, escalation evidence. |
| Console Acceptance | 7 | `AC-UI-001`, `AC-UI-002`, `AC-UI-003`, `AC-UI-004`, `AC-UI-005`, `AC-UI-006`, `AC-UI-007` | Project hub, requirement, task, runner, knowledge, metrics, admin UI screenshots/review. |
| Test Acceptance | 5 | `AC-TEST-001`, `AC-TEST-002`, `AC-TEST-003`, `AC-TEST-004`, `AC-TEST-005` | Test suite result, negative tests, regression pack, EvalRun, release gate evidence. |
| Operations Acceptance | 5 | `AC-OPS-001`, `AC-OPS-002`, `AC-OPS-003`, `AC-OPS-004`, `AC-OPS-005` | Observability, usage metrics, notification, recovery, backup/restore evidence. |

Gate reconciliation blocker: before launch, generated gate records must include or explicitly retire `AC-PROD-001`, `AC-PROD-002`, `AC-PROD-004`, `AC-UI-005`, `AC-OPS-002`, and `AC-OPS-005`.

## Partial And Blocked Promotion Criteria

| Current backfill group | Count | Existing evidence text | Required to move to complete |
| --- | ---: | --- | --- |
| Partial | 5 | Desktop Slice 0 implementation/test | Full desktop workflow tests, UI acceptance, packaging/runtime evidence where applicable. |
| Partial | 6 | Desktop Slice 0 implementation/test; Feishu card/routing results | Real Feishu/API live evidence, readable notification review, duplicate/permission negative tests. |
| Partial | 6 | Desktop Slice 0 implementation/test; role operating specs/results | Role health check, capability/tool/skill tests, handoff review, no self-approval proof. |
| Partial | 15 | Governance/quality/ops/API implementation/test | Gate-level reviewer notes, policy/tool approval evidence, operational smoke and negative tests. |
| Partial | 3 | Governance/quality/ops/API implementation/test; digital worker registry result | Registry live UI/API proof plus permission/audit evidence. |
| Partial | 5 | Governance/quality/ops/API implementation/test; knowledge governance loop | Knowledge Review Agent gate output, SourceMaterial refs, sensitivity/confidence/scope proof. |
| Partial | 3 | Governance/quality/ops/API implementation/test; notification loop result | Real notification delivery and failure/retry audit evidence. |
| Partial | 4 | Governance/quality/ops/API implementation/test; policy gates result | Human approval or signed exception for policy/security/permissions impacts. |
| Partial | 7 | Requirement/PRD domain implementation/test | Requirement object, PRD, clarification, decision, traceability gate evidence per requirement. |
| Partial | 5 | Requirement/PRD domain implementation/test; product review | PM acceptance conclusion with product positioning and no-MVP-leakage proof. |
| Partial | 7 | Scheduler/runner/result implementation/test; automation hub result | Scheduler negative tests, TaskResult/AgentRun linkage, owner-visible blocker evidence. |
| Partial | 4 | Scheduler/runner/result implementation/test; metadata migration repair | Migration regression, rollback/restore, metadata integrity and audit evidence. |
| Blocked | 4 | Scheduler/runner/result implementation/test; Agent Ring protocol/stub runner results | Must remain blocked until real runner console/API lifecycle evidence exists for `ANOS-REQ-060` to `063`; stub evidence is not enough. |

Per-record completion checklist:

1. `coverageStatus` changes only after evidence is attached, not from inferred mapping.
2. `executionUnlocking` may become true only when automated, manual, and required live evidence all exist.
3. `completePromotions` increments only for records with reviewer-readable conclusion.
4. Continued `blocked` records must state owner, external condition, next action, and launch-scope exclusion.

## Release Blocking Criteria

Release is blocked if any of the following are true:

- Any of the 84 test cases is `failed` or critical `not_run`.
- Any acceptance gate is missing owner-reviewed pass/exception evidence.
- The 44 source gates are not reconciled with generated gate records.
- Any of `ANOS-REQ-060`, `061`, `062`, `063` remains blocked while launch claim includes real runner/Agent Ring console support.
- Backfill remains at `completePromotions = 0` and `executionUnlockingMappings = 0`.
- Feishu/API, PostgreSQL/API route, runner, desktop, notification, audit, backup/restore, or permission paths rely only on mocks/stubs when source gates require live behavior.
- Human owner cannot see blockers and next action.
- Sensitive material can be exposed to unauthorized Agent or user.
- Critical end-to-end test fails.
- Backup/restore status is unknown.
- Audit trail is missing for write actions.

## Regression Strategy

Every release candidate must produce one evidence bundle with:

- Full 84-test status ledger with command/result references.
- Acceptance gate ledger for all 44 source gates.
- Gap status rollup for all 7 product gaps.
- Requirement promotion ledger for 70 partial and 4 blocked records.
- Negative-path reruns for permissions, missing acceptance, stale lease, duplicate callback, unregistered tool, missing SourceMaterial, secret leakage, and failed review.
- Live smoke for Feishu/API, runner lifecycle, PostgreSQL/API route, notification/audit, backup/restore, and desktop packaging/pairing when launch scope includes them.
- Regression comparison against the previous accepted evidence bundle, highlighting newly failed tests, newly waived gates, and changed launch exceptions.

Minimum release candidate command/check set:

| Check | Purpose |
| --- | --- |
| `python3 -m zhenzhi_knowledge validate` | Bundle/object validation and structural regressions. |
| Unit/integration test suite for CLI/API/core | Automated behavior regression. |
| Agent Ring live lifecycle smoke | Runner claim/lease/finish/notification/audit proof. |
| Feishu/API live callback smoke | Real external delivery and callback proof. |
| PostgreSQL/API route live smoke | Operational store, route, permission, migration/rollback proof. |
| Desktop packaged smoke | UI/runtime/pairing/offline/permission proof. |
| Manual PM/Test gate review | Final launch acceptance and exception review. |

## PM Review Ask

This matrix is ready for Product Manager/PM review as an acceptance planning artifact. PM should decide:

1. Whether the launch gate source count is 44 and generated record count 38 must be reconciled before any launch claim.
2. Whether any gap can receive a signed exception, and what launch wording must exclude.
3. Which team owns live evidence for Agent Ring, Feishu/API, PostgreSQL/API route, and desktop packaging.
