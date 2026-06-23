---
type: Workflow
title: AI Native OS Technical Solutions Product Review
description: Product Manager Agent review of four AI Native OS technical solution packages before implementation release.
timestamp: "2026-06-21T06:16:06Z"
reviewId: review.ai-native-os.technical-solutions.product
projectId: company-knowledge-core
ownerAgent: agent.company.product-manager
status: active
sourceMaterialRefs:
  - projects/company-knowledge-core/technical-solutions/ai-native-os-requirement-prd-domain.md
  - projects/company-knowledge-core/technical-solutions/ai-native-os-desktop-workbench-console.md
  - projects/company-knowledge-core/technical-solutions/ai-native-os-scheduler-runner-result.md
  - projects/company-knowledge-core/technical-solutions/ai-native-os-governance-quality-ops-api.md
---
# AI Native OS Technical Solutions Product Review

Review date: 2026-06-21
Reviewer: Product Manager Agent
Scope: review four technical solution packages against the AI Native OS 74-requirement launch scope.

## Executive Conclusion

Overall product verdict: proceed with controlled implementation after one desktop solution revision.

The four technical solution packages collectively cover all 74 AI Native OS requirements. No requirement gap was found in the requirement refs declared by the solutions:

- Requirement / PRD / Decision Domain: ANOS-REQ-010..016, 020..024.
- Desktop Workbench / Console: ANOS-REQ-001..006, 030..034, 040..045.
- Scheduler / Runner / Result: ANOS-REQ-050..056, 060..063, 070..073.
- Governance / Quality / Ops / API: ANOS-REQ-080..084, 090..093, 100..102, 110..114, 120..122, 130..133, 140..142, 150..152.

Product fit is strong: the proposals preserve the core product promise that a rough request becomes clarified requirement, governed task, eligible runner execution, evidence-backed result, reviewed knowledge, readable notification, and measurable quality record.

## Solution Verdicts

| Solution | Verdict | Product decision |
| --- | --- | --- |
| Requirement / PRD / Decision Domain | accepted | Accept object model, state machines, evidence/inference/assumption/decision separation, PRD versioning, Decision, and ImpactReview model. Product decisions below are binding for implementation. |
| Desktop Workbench / Console | changes_requested | Accept Tauri v2 + shared web frontend + Rust bridge direction. Require an earlier packaging/update/enterprise-network/local-runner-pairing proof before broad UI implementation lock-in. |
| Scheduler / Runner / Result | accepted | Accept taskRuntime, lease, PM approval relay, PM-visible approvalRequest, failed-test repair loop, and Result Center closure policy. Default auto-claim starts in dry-run/explicit-claim mode. |
| Governance / Quality / Ops / API | accepted | Accept review routing, human approval boundaries, notification semantics, quality dashboard, admin/governance, and shared API contract. Product decisions below are binding for implementation. |

## Coverage Review

Coverage status: complete.

No blocked requirement refs. No duplicate ownership conflict found across the four packages. Boundaries are clean:

- Intake, console, and Agent role management live in Desktop Workbench / Console.
- Requirement quality, PRD, acceptance criteria, decisions, and impact review live in Requirement / PRD / Decision Domain.
- Dispatch, runner lease, result validation, approval relay, repair loop, and PM autopilot live in Scheduler / Runner / Result.
- Knowledge governance, review, approval, tool/skill registry, notifications, metrics, admin, ops, and API consistency live in Governance / Quality / Ops / API.

## Requirement / PRD / Decision Decisions

Verdict: accepted.

Product decisions:

1. Approval blockers for complete launch are required subset plus visible assumptions, not every tracked field. Blockers: owner, targetUser, problem, value, scope, nonGoals, constraints, metric, acceptanceCriteria, decisionOwner when high-impact decisions exist, sourceRefs, and sensitivity.
2. `marketPosition` and `businessModel` are mandatory for customer/product-facing work. For internal tooling, they may be marked `not_applicable` with rationale, but cannot be silently omitted.
3. Default human owner order: explicit decision owner, project owner, requester. If submitter is Agent or Feishu group and no project owner exists, status becomes `clarifying`.
4. High-impact threshold: pricing, customer commitment, security, legal, permission, cross-team operating standard, public release, or material scope/cost change always require human-owned Decision. Projects may configure stricter thresholds, not weaker ones.
5. Product Manager Agent may approve low-impact PRD drafts only when no human-gated decision exists, required blockers are satisfied, and acceptance criteria are observable. Human review remains required for high-impact items.
6. Default high-impact Decision deadline: 2 business days for normal priority, same business day for launch blocker or security/permission risk, configurable per project if stricter.
7. PRD versioning uses monotonic per-Requirement versions: `v1`, `v2`, `v3`. Minor editorial changes can be patch metadata, but acceptance criteria, scope, workflow, or decision changes create a new version.
8. Assumptions are allowed in approved PRD only when explicitly marked, non-blocking, assigned an owner, and not used as factual evidence. High-impact assumptions must become Decision or evidence before approval.
9. User-facing status wording:
   - `clarifying`: "Needs more information".
   - `decision_needed`: "Needs owner decision".
   - `blocked`: "Cannot continue until blocker is resolved".
10. Impact review blocks only downstream tasks whose linked criteria, scope, workflow, permission, or acceptance path changed. Unaffected tasks may continue with visible trace.

No change request to this solution.

## Desktop Workbench / Console Review

Verdict: changes_requested.

Product accepts the recommended architecture:

- Tauri v2 desktop shell.
- Shared TypeScript web frontend.
- Rust bridge for file picker, OS notification, deep link, secure local settings, and local runner pairing helper.
- Central API remains source of truth.
- Local runner bridge cannot mutate leases or bypass central permission checks.

Required change before full implementation:

- Add a new early proof slice before current Slice 1 or split current packaging work forward. It must verify Mac and Windows packaging, signing/notarization feasibility, updater/channel behavior, enterprise proxy/network constraints, secure storage plugin viability, deep link behavior, OS notification permission behavior, and local runner pairing token flow.
- Name it `Slice 0: Desktop Distribution And Native Bridge Proof` or equivalent.
- Exit criteria: if Tauri fails any launch-blocking proof and cannot be fixed inside the slice, return to PM/Project Manager with Electron fallback decision request before building broad console UI.

Desktop PM decisions:

1. Future web console mode should be architecturally preserved from day one, but not launched as supported UI until desktop pilot succeeds.
2. Minimum offline behavior for launch: read-only recent state plus draft intake queue. No offline approval, no offline lease mutation, no offline evidence publication.
3. Local runner pairing roles: System Admin and Runner Admin by default; Project Owner may pair only runners scoped to their project if Admin grants that permission.
4. File references should register references and metadata first. File bytes ingestion requires Knowledge/Ops workflow decision and permission check.
5. Visible confirmation is required before task creation for admin request, approval action, permission/integration change, tool/skill enablement, and any sensitive or ambiguous classification.
6. Project Console health labels: `On track`, `Needs attention`, `Blocked`, `Waiting for decision`, `Waiting for runner`, `Reviewing`, `Done`. Runtime internals stay secondary.
7. Skill update approval at launch should be displayed in Agent Team Manager but action routed to Review Center.
8. Pilot release channel policy: forced update only for security or API-breaking incompatibility. Emergency rollback owner is Project Manager Agent plus Ops owner.

Return to: Development Agent owning Desktop Workbench / Console technical solution.

Required task: revise implementation slices to add early Tauri distribution/native bridge proof and update acceptance order.

## Scheduler / Runner / Result Review

Verdict: accepted.

Product accepts:

- `taskRuntime` as the canonical dispatch and closure contract.
- Runner eligibility through capability, tool, repo, data scope, heartbeat, load, and permission checks.
- Lease token/proof hash and versioned finish validation.
- Result Center validation before task closure.
- PM approval relay as a first-class `approvalRequest` payload.
- Hidden child-window approval as a blocker.
- Test failure repair loop that routes fixes back to Development Agent and requires Test Agent regression evidence.

Scheduler PM decisions:

1. PM Autopilot defaults to dry-run plus explicit `--claim` until closed-loop suite is stable. Auto-claim is enabled only in local grey release after PM and Test Agent acceptance.
2. Stale lease SLA: critical 10 minutes, high 30 minutes, medium 2 hours, low 1 business day, unless task policy is stricter.
3. PM Agent can decide low-risk inspection, status query, safe read, and no-write retry. Human owner required for destructive action, permission/security change, secret access, external send, approval of verified knowledge/policy, high-risk tool execution, or release gate override.
4. Manual handoff runner ids should be machine/session-based: `manual.<owner>.<session>`, with person owner retained as separate field.
5. Failed tests should reopen the original Development task when same owner and same slice remain valid; create a new repair task when ownership, scope, or root cause changes.
6. Minimum Workbench visibility before auto-claim outside local grey release: active queue, selected task, runner candidate, lease status, approval blockers, evidence requirements, retry/repair path, and PM decision log.
7. Repeat-failure threshold: same failure twice in one requirement, or same agent/tool category twice across requirements, creates Agent improvement proposal.

No change request to this solution.

## Governance / Quality / Ops / API Review

Verdict: accepted.

Product accepts:

- Shared command envelope and status vocabulary.
- ReviewRoute matrix by object type, risk, owner, and approval need.
- Human approval boundaries and no self-approval rule.
- Actionable review comments.
- Readable NotificationRecord templates with retry and repair path.
- Quality metrics derived from durable records.
- EvalRun high-severity launch gate.
- Admin disable, secretRef-only, backup/restore visibility.
- API gateway as shared central contract for Feishu, CLI, desktop/web console, and Agent Ring.

Governance PM decisions:

1. `observed` knowledge may appear only as clearly labeled reviewable source or low-confidence supporting context. Reusable answer claims require reviewed/verified knowledge according to answer risk. Customer/security/policy answers require verified or human-approved source.
2. Immediate Ops alert events: critical stale lease, hidden approval blocker, failed approval notification, failed review result notification, security/permission change failure, high-severity EvalRun failure, backup/restore unknown or failed, secret exposure attempt, unregistered high-risk tool attempt.
3. Default review SLA: knowledge review 2 business days, high-risk tool/skill change 1 business day, human approval for launch blocker same business day, release gate 4 business hours, security/permission incident immediate triage.
4. Disable semantics: pause active tasks by default. Auto-reassign only when policy explicitly allows, same acceptance path is preserved, and eligible runner/Agent exists.
5. Launch dashboard minimum: throughput, completion time, acceptance pass rate, retry rate, blocked rate, stale rate, Agent review pass rate, requirement quality gate pass, decision latency, notification failure count, and release-blocking EvalRun count.
6. Growth/ops experiments affecting customer-facing behavior require Product Owner approval plus Project Manager Agent record; security/legal/customer commitment impact adds human governance approval.
7. Desktop shell must call the same central public API for durable state. Local privileged adapter is allowed only for OS-local actions that do not create durable state and must still use central permission tokens for pairing or sensitive actions.

No change request to this solution.

## Blockers

No implementation blocker for the overall program.

One pre-implementation change is required for Desktop Workbench / Console: move Tauri distribution/native bridge proof earlier and make fallback decision explicit.

No approvalRequest was needed during this review.

## Implementation Slices Allowed To Start

Can start immediately:

- Requirement / PRD / Decision Domain: schema/template, persistence/index, state/gate, clarification, PRD versioning, Decision, ImpactReview, trace/evidence, migration dry-run, acceptance tests.
- Scheduler / Runner / Result: Runtime Normalization and Closure Policy, Runner Registry and Lease Core, Agent Worker Adapter, Result Center and Repair Loop, PM Autopilot dry-run, Workbench Data Surface read models, Closed-Loop Test Suite.
- Governance / Quality / Ops / API: Governance contract, Knowledge governance, Review and approval, Registry/admin, Notification, Quality/eval, Operations feedback, API gateway.

Can start for desktop only after requested revision is recorded:

- `Slice 0: Desktop Distribution And Native Bridge Proof`.
- Desktop shell foundation may proceed in parallel only if it does not assume the proof outcome beyond the shell-independent shared web frontend boundary.

Hold until Slice 0 passes or PM fallback decision is made:

- Broad desktop-specific native bridge investment.
- Local runner pairing UX beyond proof.
- Packaging/update rollout implementation beyond proof.

## PM Coordination Needed

Project Manager Agent should coordinate:

- Assign Desktop Workbench / Console revision back to Development Agent.
- Confirm desktop proof target environments: macOS version, Windows version, enterprise proxy/VPN constraints, signing/notarization accounts, and pilot distribution channel.
- Confirm named human owners for high-impact Decisions and release-gate approvals.
- Confirm Ops owner for notification failure, stale runner, backup/restore, and security/permission alerts.
- Confirm Test Agent closed-loop suite sequencing before enabling PM Autopilot auto-claim.

## Final Review Gate

Accepted packages may proceed to implementation with the product decisions in this review as binding acceptance semantics.

Desktop package may proceed only after the requested slice-order change is made or explicitly waived by Project Manager Agent and Product Manager Agent.
