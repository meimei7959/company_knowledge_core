---
type: Workflow
title: AI Native OS traceability promotion technical solution
solutionId: ts.ai-native-os.traceability-promotion.20260621
taskId: kt-ai-native-os-gap-tech-traceability-promotion
authorAgent: agent.company.development
runnerId: runner.meimei-mac-local-dev-rt
status: draft
reviewPath: product_and_project_manager_review
promotionImplementationAllowed: false
createdAt: "2026-06-21"
sourceRefs:
  - .zhenzhi/context/task.kt-ai-native-os-gap-tech-traceability-promotion.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-gap-tech-traceability-promotion.md
  - projects/company-knowledge-core/requirements/backfills/requirement-tree-existing-work-backfill.20260621112327.json
  - task-results/tr-kt-ai-native-os-rt-test-existing-work-backfill.md
  - projects/company-knowledge-core/product-reviews/ai-native-os-requirement-tree-final-product-acceptance.md
---

# AI Native OS Traceability Promotion Technical Solution

## Decision

Do not batch-promote the existing backfill.

The current backfill is a traceability baseline only: 74 ANOS records exist, 70 are `partial`, 4 are `blocked`, `completePromotions = 0`, `executionUnlockingMappings = 0`, and all 370 `implemented_by` mappings are `backfill_inferred`, `needs_review`, and non-execution-unlocking.

Promotion implementation remains blocked until Product Manager Agent and Project Manager Agent accept this solution.

## Non-Negotiable Rules

1. `backfill_inferred` never unlocks execution, dispatch, release, launch, or product-complete claims.
2. No ANOS/UREQ can become `complete` from package-level evidence alone.
3. A promotion candidate must include implementation evidence, executed test evidence, acceptance gate evidence, and reviewer-readable conclusion.
4. Any missing live integration, product UI, distributed runner, permission, audit, or notification evidence keeps the item `partial` or `blocked`.
5. Blocked items can move only to `complete` after the blocker is removed and tested, or to explicit `blocked` with owner, reason, recovery condition, and next task.
6. Gate refs in the backfill such as `GATE-AC-REQ-001` must resolve to the source checklist gate such as `AC-REQ-001` or a generated gate record. Unresolved gate refs fail promotion.
7. Promotion writes are per item or per reviewed slice. The migration must reject any request that changes all 74 statuses in one operation.

## Promotion Data Model

Create promotion candidate records before any status write:

```json
{
  "candidateId": "PROMO-ANOS-REQ-001-20260621",
  "requirementRef": "ANOS-REQ-001",
  "parentUreqRefs": ["UREQ-001"],
  "fromStatus": "partial",
  "targetStatus": "complete",
  "implementationEvidenceRefs": [],
  "testEvidenceRefs": [],
  "acceptanceGateEvidenceRefs": [],
  "reviewConclusionRef": "",
  "mappingConfidence": "direct_verified",
  "executionUnlocking": false,
  "unsafePromotionChecks": {
    "noBackfillOnlyEvidence": true,
    "allRefsExist": true,
    "testsExecuted": true,
    "productGateAccepted": true,
    "humanApprovalIfRequired": true
  }
}
```

Write target statuses only from accepted candidate records. Preserve original backfill records as immutable baseline.

## Implementation Slices

Each slice has paired implementation/migration task, paired Test Agent task, and Product Manager review gate.

| Slice | ANOS scope | UREQ scope | Implementation task | Test task | Product review gate |
| --- | --- | --- | --- | --- | --- |
| S1 Agent Hub live intake | ANOS-REQ-001..006, 120..122 | UREQ-001, UREQ-015 | Build Feishu/API live intake evidence matrix: SourceMaterial/Requirement creation, cards, callback, async notification, failure repair, audit. | Execute TC-HUB-001..007, TC-NOT-001..003, TC-E2E-001/002 with real or approved simulated Feishu/API evidence. | PM verifies user-readable status, source registration, notification readability, and no raw-ID-first output. |
| S2 Requirement and PRD | ANOS-REQ-010..016, 020..024 | UREQ-002, UREQ-003, UREQ-006, UREQ-007, UREQ-014 | Produce direct object evidence for RequirementState, PRD versions, decisions, acceptance criteria, impact review. | Execute TC-REQ-001..007, TC-PRD-001..005, TC-E2E-003. | PM verifies PRD completeness, assumptions/decisions separation, observable acceptance criteria. |
| S3 Project console and Agent team | ANOS-REQ-030..034, 040..045 | UREQ-004, UREQ-007 | Produce UI/read-model evidence for project health, roster, source chain, queue, blockers, role health, tool/skill governance. | Execute TC-PROJ-001..005 and TC-AGENT-001..007 with screenshots/API records. | PM verifies console usability and role boundary clarity. |
| S4 Scheduler and result lifecycle | ANOS-REQ-050..056, 070..073 | UREQ-004, UREQ-005 | Produce direct scheduler, lease, closure, result rejection, and improvement proposal evidence. | Execute TC-SCH-001..007, TC-RES-001..004, TC-E2E-004. | PM verifies task lifecycle is traceable and closure cannot bypass tests/evidence. |
| S5 Agent Ring Console unblock | ANOS-REQ-060..063 | UREQ-008 | Build or bind real Agent Ring Console: runner registry, lease/history, manual handoff, scope/audit enforcement. | Execute TC-RUN-001..004 in live runner environment; include unauthorized repo/tool negative case. | PM verifies UREQ-008 can move from blocked only with real runner/admin evidence. |
| S6 Knowledge and review governance | ANOS-REQ-080..084, 090..093 | UREQ-009, UREQ-010, UREQ-011, UREQ-014, UREQ-015 | Produce source-first knowledge, review, search, graph, review routing, human approval, actionable comments, notification evidence. | Execute TC-KNO-001..005, TC-REV-001..004, TC-E2E-005. | PM verifies no unreviewed knowledge is treated as verified truth. |
| S7 Tool, skill, admin, API | ANOS-REQ-100..102, 130..133, 150..152 | UREQ-013 | Produce ToolAsset/SkillAsset, permission/admin, secret, backup, API gateway, shared state, and write-audit evidence. | Execute TC-REG-001..003, TC-ADM-001..004, TC-API-001..004, TC-E2E-006. | PM verifies admin/governance launch risk is controlled. |
| S8 Metrics, ops, feedback | ANOS-REQ-110..114, 140..142 | UREQ-012 | Produce dashboard, metrics, eval, feedback, adoption, experiment evidence. | Execute TC-MET-001..005, TC-OPS-001..003, TC-E2E-007. | PM verifies operational readiness, release gate, and feedback loop. |
| S9 Promotion migration harness | All 74 ANOS, all 15 UREQ | Implement promotion candidate validator, no-batch guard, gate-ref resolver, status writer dry run, audit preview. | Test validator rejects backfill-only, missing refs, unresolved gates, inferred execution unlock, all-74 write. | PM/PMO verifies migration can run safely slice by slice. |

## Required Evidence Types

For every ANOS candidate:

| Evidence type | Required content |
| --- | --- |
| Implementation evidence | TaskResult or artifact proving the specific behavior was implemented, with code/output refs, runner/executor, and audit trail. |
| Execution evidence | Concrete run logs, API responses, screenshots, generated object refs, or database/file records proving the behavior executed. |
| Test evidence | Test Agent TaskResult with named TC refs, command or manual procedure, pass/fail, and negative-case coverage where applicable. |
| Acceptance gate evidence | PM-readable AC gate result, source checklist ref, pass/fail reason, and unresolved risk list. |
| Review conclusion | Product Manager conclusion: `complete`, `partial`, or `blocked`, with evidence refs and explicit launch claim boundary. |

For every UREQ candidate:

| Evidence type | Required content |
| --- | --- |
| Child ANOS rollup | All mapped ANOS are `complete`, or explicit accepted exclusions/blockers exist. |
| User scenario proof | End-to-end workflow evidence from the user role's perspective. |
| Acceptance rollup | Relevant AC gates passed, with PM-readable conclusion and no critical stop condition. |
| Review conclusion | Product Manager conclusion for the user need, not just technical implementation. |

## ANOS Promotion Matrix

Current review conclusion for every row: not promotable from existing backfill alone. Target conclusion can be `complete` only after the listed evidence/test/gate set passes Product Manager review.

| ANOS | UREQ | Current | Required evidence | Required tests | Acceptance gates | Review conclusion to record |
| --- | --- | --- | --- | --- | --- | --- |
| ANOS-REQ-001 | UREQ-001 | partial | Feishu/API intake creates SourceMaterial or work object, confirmation, audit. | TC-HUB-001, TC-HUB-002, TC-E2E-001 | AC-PROD-003, AC-REQ-001, AC-REQ-005, AC-GOV-003 | Complete only if real intake path and trace links pass. |
| ANOS-REQ-002 | UREQ-001 | partial | Intent classifier result, ambiguity handling, stored audit. | TC-HUB-003, TC-E2E-001 | AC-REQ-002, AC-GOV-003 | Complete only if ambiguity does not guess. |
| ANOS-REQ-003 | UREQ-001 | partial | Sensitivity/permission decision and unauthorized route evidence. | TC-HUB-004, TC-E2E-002 | AC-GOV-002, AC-GOV-004, AC-TEST-003 | Complete only if unauthorized exposure is blocked. |
| ANOS-REQ-004 | UREQ-001 | partial | Readable card/message evidence with title, owner, status, next action. | TC-HUB-005 | AC-PROD-003, AC-UI-002 | Complete only if human-readable output comes before raw IDs. |
| ANOS-REQ-005 | UREQ-001 | partial | Async callback and later task/notification evidence. | TC-HUB-006 | AC-PROD-003, AC-EXE-004 | Complete only if long work never blocks callback. |
| ANOS-REQ-006 | UREQ-001 | partial | Project binding/create flow and disambiguation evidence. | TC-HUB-007 | AC-REQ-001, AC-UI-001 | Complete only if ambiguous names show choices. |
| ANOS-REQ-010 | UREQ-002 | partial | Durable Requirement object with owner/source/status/sensitivity/audit. | TC-REQ-001 | AC-REQ-001, AC-GOV-003 | Complete only if object fields and audit are present. |
| ANOS-REQ-011 | UREQ-002 | partial | Field-level RequirementState evidence for known/assumed/missing/needs approval. | TC-REQ-002 | AC-REQ-001, AC-REQ-002 | Complete only if missing fields are explicit. |
| ANOS-REQ-012 | UREQ-002 | partial | PM clarification rounds and stored answers. | TC-REQ-003 | AC-REQ-002, AC-UI-001 | Complete only if questions are focused and persisted. |
| ANOS-REQ-013 | UREQ-002 | partial | PRD/task handoff separating evidence, inference, assumption, decision. | TC-REQ-004 | AC-REQ-003, AC-REQ-004 | Complete only if unsupported claims are not treated as fact. |
| ANOS-REQ-014 | UREQ-002 | partial | Versioned PRDDocument refs and reviewer/version links. | TC-REQ-005 | AC-REQ-003, AC-REQ-005 | Complete only if versions are preserved. |
| ANOS-REQ-015 | UREQ-002 | partial | Approval blocker when criteria/owner missing. | TC-REQ-006 | AC-REQ-002, AC-GOV-001 | Complete only if incomplete approval is blocked. |
| ANOS-REQ-016 | UREQ-002 | partial | Downstream ProjectTask links from Requirement and criteria. | TC-REQ-007 | AC-REQ-005, AC-EXE-001 | Complete only if task trace is inspectable. |
| ANOS-REQ-020 | UREQ-002, UREQ-003, UREQ-007 | partial | Full PRD artifact with source refs and quality gate. | TC-PRD-001, TC-E2E-003 | AC-PROD-001, AC-REQ-003 | Complete only if PM accepts PRD completeness. |
| ANOS-REQ-021 | UREQ-002, UREQ-003, UREQ-014 | partial | Decision request with human owner, options, tradeoffs, audit. | TC-PRD-002 | AC-REQ-004, AC-GOV-002 | Complete only if high-impact decision routes to human owner. |
| ANOS-REQ-022 | UREQ-002, UREQ-003, UREQ-007 | partial | PRD non-goals and scope boundaries. | TC-PRD-003 | AC-REQ-003 | Complete only if quality gate fails missing non-goals. |
| ANOS-REQ-023 | UREQ-002, UREQ-003, UREQ-006, UREQ-007 | partial | Observable acceptance criteria mapped to tests. | TC-PRD-004 | AC-REQ-005, AC-TEST-001 | Complete only if Test Agent can derive cases. |
| ANOS-REQ-024 | UREQ-002, UREQ-003, UREQ-007 | partial | PRD change impact review listing affected tasks/designs/tests/results. | TC-PRD-005, TC-E2E-003 | AC-REQ-005, AC-GOV-003 | Complete only if post-task changes create impact review. |
| ANOS-REQ-030 | UREQ-004 | partial | Project Console/read-model showing health, blockers, next action, owner. | TC-PROJ-001 | AC-UI-002, AC-OPS-001 | Complete only if owner can inspect current state. |
| ANOS-REQ-031 | UREQ-004 | partial | Agent roster and role boundary view. | TC-PROJ-002 | AC-AGENT-001, AC-AGENT-002 | Complete only if business/governance roles are distinct. |
| ANOS-REQ-032 | UREQ-004 | partial | Source-to-result evidence chain in UI/API. | TC-PROJ-003 | AC-REQ-005, AC-EXE-004 | Complete only if chain is navigable. |
| ANOS-REQ-033 | UREQ-004 | partial | Active queue with runtime, assignee/runner, lease, acceptance path. | TC-PROJ-004 | AC-EXE-001, AC-UI-002 | Complete only if queue state is current and traceable. |
| ANOS-REQ-034 | UREQ-004 | partial | Blocker owner/reason/next action/notification evidence. | TC-PROJ-005 | AC-OPS-001, AC-EXE-004 | Complete only if blocker is actionable. |
| ANOS-REQ-040 | UREQ-007 | partial | Business Agent profiles, scopes, tools, skills, status, owner. | TC-AGENT-001, TC-AGENT-002 | AC-AGENT-001, AC-UI-003 | Complete only if all business roles are represented. |
| ANOS-REQ-041 | UREQ-007 | partial | Governance Agent profiles separated from execution roles. | TC-AGENT-003 | AC-AGENT-002 | Complete only if self-approval confusion is impossible. |
| ANOS-REQ-042 | UREQ-007 | partial | Capability reports used by scheduler matching. | TC-AGENT-004 | AC-EXE-002, AC-AGENT-003 | Complete only if missing capability prevents assignment. |
| ANOS-REQ-043 | UREQ-007 | partial | Role health check and generated repair task/governance issue. | TC-AGENT-005 | AC-AGENT-003, AC-OPS-001 | Complete only if health gaps create repair work. |
| ANOS-REQ-044 | UREQ-007 | partial | Unregistered tool call blocked and audited. | TC-AGENT-006 | AC-AGENT-004, AC-GOV-003 | Complete only if unauthorized tool use fails safely. |
| ANOS-REQ-045 | UREQ-007 | partial | Skill package owner/version/tests/rollout/rollback approval evidence. | TC-AGENT-007 | AC-AGENT-005 | Complete only if skill update without tests is blocked. |
| ANOS-REQ-050 | UREQ-004, UREQ-005 | partial | taskRuntime normalization for dispatchable tasks. | TC-SCH-001 | AC-EXE-001 | Complete only if runtime includes acceptance/review/risk/permission. |
| ANOS-REQ-051 | UREQ-004, UREQ-005 | partial | Eligible runner/Agent matching and waiting_runner reason. | TC-SCH-002 | AC-EXE-002 | Complete only if mismatch cannot dispatch. |
| ANOS-REQ-052 | UREQ-004, UREQ-005 | partial | Claim lease token/owner/expiry and invalid finish rejection. | TC-SCH-003 | AC-EXE-003 | Complete only if finish without lease fails. |
| ANOS-REQ-053 | UREQ-004, UREQ-005 | partial | Heartbeat, stale lease, retry/cancel/escalation evidence. | TC-SCH-004, TC-E2E-004 | AC-EXE-003, AC-OPS-001 | Complete only if stale critical task is visible/repairable. |
| ANOS-REQ-054 | UREQ-004, UREQ-005 | partial | Engineering closure requires engineering/test evidence. | TC-SCH-005 | AC-EXE-004, AC-TEST-004 | Complete only if generated text alone cannot close. |
| ANOS-REQ-055 | UREQ-004, UREQ-005 | partial | Knowledge closure requires SourceMaterial, draft, review path. | TC-SCH-006 | AC-KNO-001, AC-KNO-002 | Complete only if missing source blocks closure. |
| ANOS-REQ-056 | UREQ-004, UREQ-005 | partial | Product discovery closure requires RequirementState and PRD quality. | TC-SCH-007 | AC-REQ-002, AC-REQ-003 | Complete only if missing product fields block closure. |
| ANOS-REQ-060 | UREQ-008 | blocked | Live runner registry: id, machine, owner, heartbeat, load, status, scopes. | TC-RUN-001 | AC-UI-004, AC-EXE-002 | Remain blocked until real runner/admin evidence exists. |
| ANOS-REQ-061 | UREQ-008 | blocked | Current leases and history visible, stale/failed repairable. | TC-RUN-002 | AC-UI-004, AC-EXE-003 | Remain blocked until lease/history product evidence exists. |
| ANOS-REQ-062 | UREQ-008 | blocked | Manual handoff writes AgentRun/equivalent, TaskResult, Notification, AuditLog. | TC-RUN-003 | AC-EXE-005, AC-GOV-003 | Remain blocked until durable manual handoff evidence exists. |
| ANOS-REQ-063 | UREQ-008 | blocked | Unauthorized repo/tool/knowledge access blocked and audited. | TC-RUN-004 | AC-GOV-003, AC-TEST-003 | Remain blocked until scope enforcement evidence exists. |
| ANOS-REQ-070 | UREQ-005 | partial | TaskResult required fields validation. | TC-RES-001 | AC-EXE-004 | Complete only if incomplete result cannot close. |
| ANOS-REQ-071 | UREQ-005 | partial | Acceptance path display for product/test/knowledge/human review. | TC-RES-002 | AC-GOV-001, AC-EXE-004 | Complete only if correct path is visible. |
| ANOS-REQ-072 | UREQ-005 | partial | Rejected result creates follow-up or retry reason. | TC-RES-003 | AC-EXE-004 | Complete only if owner sees exact next action. |
| ANOS-REQ-073 | UREQ-005 | partial | Repeat/systemic failure creates improvement/eval/repair task. | TC-RES-004 | AC-OPS-003 | Complete only if failure becomes improvement work. |
| ANOS-REQ-080 | UREQ-009, UREQ-011 | partial | SourceMaterial exists before reusable knowledge draft. | TC-KNO-001, TC-E2E-005 | AC-KNO-001 | Complete only if raw message cannot publish knowledge. |
| ANOS-REQ-081 | UREQ-009, UREQ-011 | partial | KnowledgeItem category/source/confidence/sensitivity/scope/review state. | TC-KNO-002 | AC-KNO-002 | Complete only if missing fields block review pass. |
| ANOS-REQ-082 | UREQ-009, UREQ-011 | partial | Knowledge Review checks evidence/conflict/duplicate/graph/readability/status. | TC-KNO-003 | AC-KNO-002 | Complete only if review routes changes/conflict/approval correctly. |
| ANOS-REQ-083 | UREQ-009, UREQ-011, UREQ-015 | partial | Knowledge query with citations, confidence, gap/reviewable sources. | TC-KNO-004 | AC-KNO-003 | Complete only if no-answer path is safe and cited. |
| ANOS-REQ-084 | UREQ-009, UREQ-011 | partial | Graph edge source/reason/evidence validation. | TC-KNO-005 | AC-KNO-004 | Complete only if edge without evidence is rejected. |
| ANOS-REQ-090 | UREQ-003, UREQ-010, UREQ-014 | partial | Review routing by object/risk/owner/approval requirement. | TC-REV-001 | AC-GOV-001, AC-GOV-002 | Complete only if high-risk route reaches owner/human. |
| ANOS-REQ-091 | UREQ-003, UREQ-010, UREQ-014 | partial | Human approval required for verified/policy/security/customer commitments. | TC-REV-002 | AC-GOV-002 | Complete only if Agent self-approval is blocked. |
| ANOS-REQ-092 | UREQ-003, UREQ-010, UREQ-014 | partial | Actionable review comments with evidence and exact change. | TC-REV-003 | AC-GOV-001 | Complete only if requested change is clear. |
| ANOS-REQ-093 | UREQ-003, UREQ-010, UREQ-014 | partial | Review result notification to requester and owner. | TC-REV-004 | AC-GOV-001, AC-PROD-003 | Complete only if notification links object/result/reason/action. |
| ANOS-REQ-100 | UREQ-013 | partial | ToolAsset owner/risk/status/allowed Agents/permissions/approval/audit. | TC-REG-001 | AC-AGENT-004, AC-GOV-001 | Complete only if high-risk tool lacks owner is blocked. |
| ANOS-REQ-101 | UREQ-013 | partial | SkillAsset owner/version/scope/tests/compat/status/rollback. | TC-REG-002 | AC-AGENT-005 | Complete only if missing rollback/tests blocks approval. |
| ANOS-REQ-102 | UREQ-013 | partial | Tool/skill usage recorded in AgentRun or TaskResult. | TC-REG-003 | AC-GOV-003 | Complete only if audit can trace Agent/tool/result. |
| ANOS-REQ-110 | UREQ-006, UREQ-012 | partial | Metrics for throughput/completion/pass/retry/blocked/stale. | TC-MET-001 | AC-UI-006, AC-OPS-004 | Complete only if filters by project/Agent/runner/type/time work. |
| ANOS-REQ-111 | UREQ-006, UREQ-012 | partial | Agent quality metrics and improvement tasks. | TC-MET-002 | AC-UI-006, AC-OPS-004 | Complete only if failure causes are visible. |
| ANOS-REQ-112 | UREQ-006, UREQ-012 | partial | Requirement quality metrics for clarification/PRD/decision/coverage. | TC-MET-003 | AC-REQ-005, AC-OPS-004 | Complete only if metrics update from durable records. |
| ANOS-REQ-113 | UREQ-006, UREQ-012 | partial | Knowledge quality metrics for review/conflict/duplicate/reuse/stale. | TC-MET-004 | AC-KNO-002, AC-OPS-004 | Complete only if reuse metric updates. |
| ANOS-REQ-114 | UREQ-006, UREQ-012 | partial | EvalCase/EvalRun release gate for router/retrieval/role/task lifecycle. | TC-MET-005 | AC-TEST-005 | Complete only if critical eval failure blocks release. |
| ANOS-REQ-120 | UREQ-001, UREQ-015 | partial | NotificationRecord for important state changes. | TC-NOT-001 | AC-PROD-003, AC-GOV-003 | Complete only if objectRef/status/retry are recorded. |
| ANOS-REQ-121 | UREQ-001, UREQ-015 | partial | Readable notification summary before raw IDs. | TC-NOT-002 | AC-PROD-003 | Complete only if human meaning is primary. |
| ANOS-REQ-122 | UREQ-001, UREQ-015 | partial | Notification failure repair path. | TC-NOT-003, TC-E2E-007 | AC-OPS-001 | Complete only if critical failure alerts owner/Ops. |
| ANOS-REQ-130 | UREQ-013 | partial | Admin permission/integration/asset/data-retention change evidence. | TC-ADM-001 | AC-UI-007, AC-GOV-003 | Complete only if change is permission-checked/audited. |
| ANOS-REQ-131 | UREQ-013 | partial | Disable Agent/tool/skill/runner/integration evidence. | TC-ADM-002 | AC-OPS-005, AC-UI-007 | Complete only if disabled asset cannot receive new work. |
| ANOS-REQ-132 | UREQ-013 | partial | Secret handling blocks/redacts secret values to secretRef. | TC-ADM-003 | AC-GOV-004 | Complete only if no secret value enters knowledge files. |
| ANOS-REQ-133 | UREQ-013 | partial | Backup/restore status and latest success evidence. | TC-ADM-004 | AC-OPS-002, AC-UI-007 | Complete only if restore procedure is visible. |
| ANOS-REQ-140 | UREQ-012 | partial | Feedback linked to project/requirement/Agent/result/improvement task. | TC-OPS-001 | AC-OPS-003 | Complete only if rejected result becomes actionable feedback. |
| ANOS-REQ-141 | UREQ-012 | partial | Adoption/users/Agents/tasks/reuse/satisfaction metrics. | TC-OPS-002 | AC-OPS-004 | Complete only if dashboard updates from durable records. |
| ANOS-REQ-142 | UREQ-012 | partial | Experiment hypothesis/audience/metric/start/end/result/decision. | TC-OPS-003 | AC-OPS-004 | Complete only if experiment without metric is blocked. |
| ANOS-REQ-150 | UREQ-013 | partial | Validated API endpoints and unauthorized failure evidence. | TC-API-001, TC-API-002 | AC-UI-007, AC-GOV-003 | Complete only if valid creates object and unauthorized fails safely. |
| ANOS-REQ-151 | UREQ-013 | partial | Feishu, CLI, web console, Agent Ring share central state contracts. | TC-API-003 | AC-PROD-003, AC-REQ-005 | Complete only if no private status semantics diverge. |
| ANOS-REQ-152 | UREQ-013 | partial | API write audit records for create/update/approve/reject/claim/finish. | TC-API-004 | AC-GOV-003 | Complete only if every write is auditable. |

## UREQ Promotion Matrix

Current UREQ rollup from the test result: 15/15 UREQs are covered; 14 have partial coverage and UREQ-008 is fully blocked. UREQ completion requires child ANOS completion plus role-level scenario evidence.

| UREQ | Current | Required evidence | Required tests | Acceptance gates | Review conclusion to record |
| --- | --- | --- | --- | --- | --- |
| UREQ-001 | partial | End-to-end submitter intake, clarification/status card, notification, source/audit. | TC-HUB-001..007, TC-NOT-001..003, TC-E2E-001/002 | AC-PROD-003, AC-REQ-001/002/005, AC-GOV-003 | Complete only if submitter can see guided status without unsafe exposure. |
| UREQ-002 | partial | Requirement tree and PRD evidence from vague demand. | TC-REQ-001..007, TC-PRD-001..005 | AC-REQ-001..005 | Complete only if PM Agent separates requirement levels and open decisions. |
| UREQ-003 | partial | Project-owner PRD, assumption, risk, decision, acceptance review packet. | TC-PRD-001..005, TC-REV-001..004 | AC-REQ-003/004/005, AC-GOV-001/002 | Complete only if owner can approve with evidence and tradeoffs. |
| UREQ-004 | partial | Project Manager console and scheduler queue evidence. | TC-PROJ-001..005, TC-SCH-001..007 | AC-UI-002, AC-EXE-001..004 | Complete only if coordination state is traceable and actionable. |
| UREQ-005 | partial | Development task package, scheduler/result lifecycle, evidence-based closure. | TC-SCH-001..007, TC-RES-001..004 | AC-EXE-001..004 | Complete only if Development Agent receives scoped task and cannot close without evidence. |
| UREQ-006 | partial | Test acceptance mapping, metrics, eval release gate. | TC-PRD-004, TC-MET-001..005 | AC-REQ-005, AC-TEST-001/005 | Complete only if Test Agent gets observable criteria and release gate. |
| UREQ-007 | partial | Design role context, PRD boundaries, Agent team state. | TC-PRD-001/003/005, TC-AGENT-001..007 | AC-AGENT-001..005, AC-REQ-003 | Complete only if design can work from scenarios, non-goals, states, constraints. |
| UREQ-008 | blocked | Live Agent Ring Console runner registry, lease/history, manual handoff, scope/audit. | TC-RUN-001..004, TC-E2E-004 | AC-UI-004, AC-EXE-002/003/005, AC-GOV-003 | Remain blocked until real runner evidence exists; no inferred mapping unlocks execution. |
| UREQ-009 | partial | Source-first Knowledge Engineering handoff and draft evidence. | TC-KNO-001..005 | AC-KNO-001/002/004 | Complete only if source/result evidence precedes draft knowledge. |
| UREQ-010 | partial | Knowledge Review routing, human approval, actionable review. | TC-REV-001..004, TC-KNO-002/003 | AC-GOV-001/002, AC-KNO-002 | Complete only if low-quality/sensitive knowledge cannot pollute reuse. |
| UREQ-011 | partial | Cited knowledge query with confidence and gap path. | TC-KNO-004, TC-KNO-001..005 | AC-KNO-003 | Complete only if uncited answer is not emitted as verified truth. |
| UREQ-012 | partial | Ops dashboard, feedback, metrics, eval, experiments. | TC-MET-001..005, TC-OPS-001..003, TC-E2E-007 | AC-UI-006, AC-OPS-001/003/004 | Complete only if launch/improvement loop is visible and durable. |
| UREQ-013 | partial | Admin console, ToolAsset/SkillAsset, permission, secret, backup, API audit. | TC-REG-001..003, TC-ADM-001..004, TC-API-001..004 | AC-UI-007, AC-GOV-003/004, AC-OPS-002/005 | Complete only if governance controls are enforceable. |
| UREQ-014 | partial | Human reviewer package for high-impact decisions and review actions. | TC-PRD-002, TC-REV-001..004 | AC-REQ-004, AC-GOV-001/002 | Complete only if human review is evidence-backed and actionable. |
| UREQ-015 | partial | Team member query and notification/status path with citations/gaps. | TC-KNO-004, TC-NOT-001..003 | AC-KNO-003, AC-PROD-003 | Complete only if answers and notifications are readable, cited, and permission-safe. |

## Migration Safety Checks

Before any candidate status write, run:

1. Ref existence check: every implementation/test/gate/review ref exists on disk or in approved external evidence registry.
2. Backfill-only rejection: candidate fails if evidence is only `requirement-tree-existing-work-backfill.20260621112327.json`.
3. Gate resolution: `GATE-AC-*` aliases must resolve to `AC-*` checklist rows or generated gate records.
4. Test execution check: named TC refs must have executed pass evidence from Test Agent or approved manual test record.
5. Product review check: Product Manager must record reviewer-readable conclusion and launch boundary.
6. Execution unlock check: `backfill_inferred` candidates must keep `executionUnlocking = false`; only `direct_verified` candidates may be considered by scheduler/release tooling, and only after review.
7. Batch guard: any write touching more than one accepted slice, or all 74 records, is rejected unless Project Manager creates a separate migration approval task.
8. Audit preview: dry run prints status deltas and evidence refs; final run writes AuditLog for each changed ANOS/UREQ.

## Promotion Status Rules

| From | To | Allowed when |
| --- | --- | --- |
| partial | complete | All ANOS evidence types exist, tests pass, AC gates pass, PM conclusion says complete. |
| partial | blocked | Evidence proves a missing external dependency, permission, live integration, or product decision blocks completion; owner/recovery/task refs recorded. |
| blocked | complete | Blocker removed, implementation/test/product evidence exists, PM accepts removal. |
| blocked | blocked | Blocker still exists and is explicit with owner/recovery condition. |
| partial/blocked | complete by inferred mapping | Never allowed. |

## Output Artifacts For Future Implementation

The implementation task that follows this solution should produce:

- `projects/company-knowledge-core/requirements/promotions/ai-native-os-promotion-candidates.<timestamp>.jsonl`
- `projects/company-knowledge-core/requirements/promotions/ai-native-os-promotion-dry-run.<timestamp>.md`
- `task-results/tr-kt-ai-native-os-traceability-promotion-slice-<n>-test.md`
- `projects/company-knowledge-core/product-reviews/ai-native-os-traceability-promotion-slice-<n>-product-review.md`

## Review Handoff

This solution is ready for Product Manager and Project Manager review as a plan only.

Implementation must not begin until both reviewers accept:

- the no-batch-promotion rule,
- the per-ANOS/UREQ evidence matrix,
- the paired test task requirement,
- the product review gate requirement,
- and the rule that inferred mapping cannot unlock execution.
