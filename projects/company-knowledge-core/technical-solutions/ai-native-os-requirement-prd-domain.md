---
type: Workflow
title: AI Native OS Requirement, PRD, and Decision Domain Technical Solution
description: Technical solution for Requirement Center plus PRD and Decision Center before implementation.
timestamp: "2026-06-21T06:40:00Z"
solutionId: ts-ai-native-os-requirement-prd-domain
projectId: company-knowledge-core
ownerAgent: agent.company.development
reviewAgents:
  - agent.company.product-manager
  - agent.company.project-manager
status: draft
implementationStatus: not_started
requirementRefs:
  - ANOS-REQ-010
  - ANOS-REQ-011
  - ANOS-REQ-012
  - ANOS-REQ-013
  - ANOS-REQ-014
  - ANOS-REQ-015
  - ANOS-REQ-016
  - ANOS-REQ-020
  - ANOS-REQ-021
  - ANOS-REQ-022
  - ANOS-REQ-023
  - ANOS-REQ-024
sourceMaterialRefs:
  - docs/product/ai-native-os/requirements.md
  - docs/product/ai-native-os/prd.md
  - docs/product/ai-native-os/test-cases.md
  - docs/product/ai-native-os/acceptance-checklist.md
  - docs/product/ai-native-os/development-handoff.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-tech-solution-requirement-prd-domain.md
  - projects/company-knowledge-core/coordination/ai-native-os-agent-execution-governance.md
---
# AI Native OS Requirement, PRD, and Decision Domain Technical Solution

## Scope

This document defines the technical solution for the Requirement Center and PRD and Decision Center only. It is a design artifact for Product Manager Agent and Project Manager Agent review. It does not implement code, modify tests, create runtime data, or change existing behavior.

Covered requirement refs:

- ANOS-REQ-010 to ANOS-REQ-016.
- ANOS-REQ-020 to ANOS-REQ-024.

Out of scope:

- Agent Hub input classification implementation.
- Scheduler, runner, lease, and TaskResult engine implementation.
- Web or desktop UI implementation.
- Knowledge Review implementation.
- Any code or `tests/test_cli.py` change in this task.

## Design Goals

- Make a rough business need durable, inspectable, and auditable before downstream work starts.
- Preserve the distinction between evidence, inference, assumption, and decision needed.
- Let Product Manager Agent clarify missing fields in short Socratic rounds.
- Make PRD generation versioned, reviewable, and traceable to source material.
- Block approval when owner or observable acceptance criteria are missing.
- Create human-owned Decision requests for high-impact choices.
- Detect PRD changes that affect already-created tasks, tests, designs, or results.

## Object Model

### Requirement

Durable product or business need. It is the system of record for ANOS-REQ-010 and the parent object for state, PRDs, decisions, criteria, and downstream tasks.

Required fields:

- `requirementId`: stable id, format `req.<project>.<slug>.<yyyymmddhhmmss>` or existing repo id convention.
- `type`: `Requirement`.
- `projectRef`: project id or pending project binding.
- `title`: readable business title.
- `summary`: short human-facing summary.
- `submitter`: human or Agent who submitted.
- `owner`: human owner required before approval.
- `decisionOwner`: human owner for unresolved high-impact choices.
- `sourceRefs`: SourceMaterial, document, message, meeting, or task refs.
- `status`: shared status vocabulary.
- `sensitivity`: inherited max sensitivity from source refs plus manual override.
- `requirementStateRef`: current RequirementState.
- `prdRefs`: ordered PRDDocument versions.
- `currentPrdRef`: latest active PRD version.
- `decisionRefs`: linked Decision records.
- `acceptanceCriteriaRefs`: observable criteria.
- `taskRefs`: downstream ProjectTask refs.
- `impactReviewRefs`: impact reviews caused by PRD or criteria changes.
- `auditRefs`: AuditLog refs for writes and approval attempts.
- `createdAt`, `updatedAt`, `createdBy`, `updatedBy`.

Validation:

- `title`, `sourceRefs`, `submitter`, `status`, `sensitivity`, `projectRef`, and `auditRefs` required on create.
- `owner` and at least one accepted AcceptanceCriteria required to move to `approved`.
- `sourceRefs` cannot be empty. If source is direct API/Feishu text, Agent Hub must first create SourceMaterial or equivalent source ref.
- `taskRefs` must point to tasks that link back to this requirement and at least one criteria ref.

### RequirementState

Field-level clarity model for ANOS-REQ-011 and ANOS-REQ-013. Each field stores value plus provenance and clarity status.

State entry shape:

```yaml
field:
  value: string | list | object | null
  clarity: known | assumed | missing | needs_approval
  basis: evidence | inference | assumption | decision_needed
  sourceRefs: []
  answeredBy: human | agent | source_material
  updatedAt: timestamp
  notes: string
```

Required tracked fields:

- `targetUser`.
- `problem`.
- `scenario`.
- `alternative`.
- `value`.
- `marketPosition`.
- `businessModel`.
- `scope`.
- `nonGoals`.
- `constraints`.
- `metric`.
- `acceptanceCriteria`.
- `evidence`.
- `assumptions`.
- `decisionOwner`.

Derived fields:

- `missingFields`: tracked fields where `clarity` is `missing`.
- `needsApprovalFields`: tracked fields where `clarity` is `needs_approval`.
- `evidenceClaims`: claim refs backed directly by source.
- `inferenceClaims`: Agent-derived claims with source refs and reasoning.
- `assumptionClaims`: unverified claims that must stay visible in PRD and handoff.
- `decisionNeededClaims`: unresolved choices that must create or link Decision.
- `clarificationRounds`: Socratic question/answer rounds.
- `qualityGate`: pass/fail and blockers for product discovery acceptance.

### ClarificationRound

Structured record of Product Manager Agent Socratic clarification for ANOS-REQ-012.

Fields:

- `roundId`.
- `requirementRef`.
- `agentRef`: Product Manager Agent.
- `questionRefs`: 1 to 3 questions.
- `triggerFields`: missing or low-confidence RequirementState fields.
- `recipient`: submitter, owner, or decision owner.
- `status`: `draft`, `sent`, `answered`, `expired`, `blocked`.
- `answerRefs`: SourceMaterial or Interaction refs containing answers.
- `statePatchSummary`: fields updated after answers.
- `auditRefs`.

Question selection rule:

- Choose at most 3 questions per round.
- Rank by approval blockers first: owner, target user, problem, business model, success metric, acceptance criteria, decision owner.
- Avoid asking what can be extracted from existing evidence.
- Each question must say why it matters in human language.

### AcceptanceCriteria

Observable, testable acceptance unit for ANOS-REQ-015 and ANOS-REQ-023.

Fields:

- `criteriaId`.
- `requirementRef`.
- `prdRef`.
- `taskRef`: optional until task creation.
- `type`: `product`, `design`, `engineering`, `test`, `operations`, `governance`.
- `description`: readable expected outcome.
- `observableSignal`: what can be seen, measured, or asserted.
- `verificationMethod`: `manual_review`, `automated_test`, `api_check`, `document_check`, `e2e_flow`, `metric_check`.
- `testCaseRefs`: mapped test cases.
- `owner`.
- `status`: `draft`, `approved`, `superseded`, `rejected`.
- `sourceRefs`.
- `auditRefs`.

Validation:

- `description`, `observableSignal`, `verificationMethod`, `owner`, and `requirementRef` required.
- Criteria without observable signal cannot approve a Requirement or PRD.
- Criteria changed after task creation triggers impact review.

### PRDDocument

Versioned product requirement document generated from RequirementState for ANOS-REQ-014 and ANOS-REQ-020.

Fields:

- `prdId`.
- `requirementRef`.
- `projectRef`.
- `version`: monotonic integer or semver-like `v1`, `v2`.
- `status`: `draft`, `reviewing`, `approved`, `superseded`, `rejected`.
- `authorAgent`.
- `reviewer`: Product Manager Agent reviewer or human reviewer.
- `owner`.
- `sourceRefs`.
- `requirementStateSnapshotRef`.
- `positioning`.
- `marketPositioning`.
- `businessModel`.
- `workflows`.
- `requirements`.
- `scope`.
- `nonGoals`.
- `metrics`.
- `risks`.
- `openDecisions`.
- `acceptanceCriteriaRefs`.
- `taskProposalRefs`.
- `evidenceSection`.
- `inferenceSection`.
- `assumptionSection`.
- `decisionNeededSection`.
- `qualityGate`.
- `supersedesPrdRef`.
- `supersededByPrdRef`.
- `auditRefs`.

PRD quality gate:

- Required sections exist: positioning, market positioning, business model, workflows, requirements, metrics, risks, open decisions, scope, non-goals.
- Every factual claim is categorized as evidence, inference, assumption, or decision needed.
- Every requirement row links to acceptance criteria or marks why criteria is pending.
- Open high-impact items link to Decision records.
- No PRD can be approved if non-goals, owner, or observable criteria are missing.

### Decision

Human-owned decision request for ANOS-REQ-021 and PRD impact control.

Existing `Decision` object should be extended by convention, not replaced.

Fields:

- `decisionId`.
- `type`: `Decision`.
- `projectId`.
- `requirementRef`.
- `prdRef`: optional if raised before PRD.
- `owner`: human owner required.
- `status`: `draft`, `decision_needed`, `approved`, `rejected`, `superseded`, `blocked`.
- `impactLevel`: `low`, `medium`, `high`.
- `impactAreas`: `product`, `customer`, `pricing`, `security`, `legal`, `cross_team`, `scope`, `schedule`, `permission`.
- `context`: readable summary.
- `options`: list with label, description, pros, cons, risk, sourceRefs.
- `tradeoffs`: cross-option summary.
- `recommendation`: Agent recommendation with confidence and source refs.
- `deadline`: required for high-impact decisions.
- `decision`: selected option after approval.
- `rationale`.
- `affectedObjects`: Requirement, PRDDocument, ProjectTask, tests, designs, TaskResult, KnowledgeItem refs.
- `notificationRefs`.
- `auditRefs`.

Creation triggers:

- Pricing, customer commitment, security/legal, permission, cross-team workflow, launch scope, or acceptance meaning changes.
- Any RequirementState field marked `needs_approval`.
- PRD change after task creation where downstream impact is non-empty.

### ImpactReview

Trace record for ANOS-REQ-024.

Fields:

- `impactReviewId`.
- `requirementRef`.
- `fromPrdRef`.
- `toPrdRef`.
- `changedFields`: section and field-level diff summary.
- `affectedTaskRefs`.
- `affectedDesignRefs`.
- `affectedTestRefs`.
- `affectedResultRefs`.
- `affectedDecisionRefs`.
- `riskSummary`.
- `recommendedActions`: keep, update, reopen, retest, create decision.
- `owner`.
- `status`: `draft`, `reviewing`, `accepted`, `blocked`.
- `notificationRefs`.
- `auditRefs`.

Impact detection:

- Compare RequirementState snapshot, PRD content sections, acceptance criteria, scope, non-goals, metrics, and decision links.
- If any `taskRefs` exist and changed fields affect criteria, scope, workflow, metric, or decision, create ImpactReview before the PRD can become active.

## State Machines

### Requirement

```txt
draft
-> clarifying
-> decision_needed
-> approved
-> in_progress
-> reviewing
-> done
```

Alternative terminal or paused paths:

```txt
draft|clarifying|decision_needed|approved|in_progress|reviewing -> blocked
draft|clarifying|decision_needed|reviewing -> rejected
blocked -> clarifying|decision_needed|approved
```

Rules:

- `draft` to `clarifying`: RequirementState has missing required fields.
- `clarifying` to `decision_needed`: missing fields are resolved but approval-required fields remain.
- `clarifying` or `decision_needed` to `approved`: owner and observable criteria exist, quality gate passes, required decisions approved.
- `approved` to `in_progress`: downstream tasks created.
- `in_progress` to `reviewing`: implementation or product discovery result submitted.
- `reviewing` to `done`: product acceptance completed.
- Any attempted invalid transition writes AuditLog and returns readable blocker.

### RequirementState Field

```txt
missing -> assumed -> known
missing -> needs_approval -> known
assumed -> needs_approval -> known
known -> needs_approval
known -> missing
```

Rules:

- `known` requires evidence or explicit human answer source.
- `assumed` must stay visible in PRD and task handoff.
- `needs_approval` must link to Decision or human approval route before Requirement approval.
- Regression from `known` to `missing` is allowed only when source is removed, superseded, or contradicted, and must create audit.

### PRDDocument

```txt
draft -> reviewing -> approved
draft|reviewing -> rejected
approved -> superseded
```

Rules:

- New PRD version always snapshots current RequirementState.
- `approved` requires quality gate pass and owner.
- Approving a new version marks previous approved PRD `superseded`.
- If tasks exist, approval of a new version requires ImpactReview status `accepted` or linked Decision.

### Decision

```txt
draft -> decision_needed -> approved
draft|decision_needed -> rejected
decision_needed -> blocked
blocked -> decision_needed
approved -> superseded
```

Rules:

- High-impact Decision cannot be approved by Agent alone.
- `approved` writes selected option, rationale, approver, and audit.
- `rejected` must include reason and next action.

## CLI And API Surface

Implementation should reuse central state contracts across local CLI, API, Feishu, console, and future desktop workbench. Names below are proposed contracts, not implementation in this task.

### CLI

- `zhenzhi-knowledge requirement create --project <projectId> --source <sourceRef> --title <title> --submitter <ref>`
- `zhenzhi-knowledge requirement show <requirementId> --with-state --with-prd --with-tasks --with-decisions`
- `zhenzhi-knowledge requirement update-state <requirementId> --patch <json-or-file>`
- `zhenzhi-knowledge requirement clarify <requirementId> --agent agent.company.product-manager`
- `zhenzhi-knowledge requirement approve <requirementId> --owner <humanRef>`
- `zhenzhi-knowledge prd generate <requirementId> --author-agent agent.company.product-manager`
- `zhenzhi-knowledge prd show <prdId>`
- `zhenzhi-knowledge prd approve <prdId> --reviewer <human-or-agent-ref>`
- `zhenzhi-knowledge decision create --requirement <requirementId> --impact high --owner <humanRef>`
- `zhenzhi-knowledge decision resolve <decisionId> --selected-option <optionId> --rationale <text>`
- `zhenzhi-knowledge requirement impact-review <requirementId> --from <prdId> --to <prdId>`

CLI output requirements:

- Human-readable title, status, owner, blocker, and next action first.
- Internal ids secondary.
- Approval blockers must name missing business field, not only schema key.

### API

Recommended endpoints:

- `POST /api/requirements`
- `GET /api/requirements/{requirementId}`
- `PATCH /api/requirements/{requirementId}`
- `POST /api/requirements/{requirementId}/state`
- `POST /api/requirements/{requirementId}/clarification-rounds`
- `POST /api/requirements/{requirementId}/approval`
- `POST /api/requirements/{requirementId}/acceptance-criteria`
- `POST /api/requirements/{requirementId}/prd`
- `GET /api/prds/{prdId}`
- `POST /api/prds/{prdId}/approval`
- `POST /api/decisions`
- `POST /api/decisions/{decisionId}/resolution`
- `POST /api/requirements/{requirementId}/impact-reviews`
- `GET /api/requirements/{requirementId}/trace`

API behavior:

- Validate permission and sensitivity before read or write.
- Every write produces AuditLog.
- Async operations return accepted status with task or operation ref.
- Errors return readable `blockerCode`, `message`, `missingFields`, `nextAction`, and `owner`.

## Data Files And Storage

Initial implementation can use repository-backed markdown/YAML records, consistent with existing knowledge-core patterns. Later storage can move to database without changing object contracts.

Recommended file layout:

```txt
requirements/
  req.<project>.<slug>.<timestamp>.md
requirements/state/
  req-state.<requirementId>.<version>.json
prd/
  prd.<requirementId>.v001.md
decisions/
  decision.<project>.<slug>.<timestamp>.md
reviews/impact/
  impact-review.<requirementId>.<fromVersion>-to-<toVersion>.md
```

Repository index updates:

- Project index should link active Requirement, current PRD, open Decisions, and downstream tasks.
- Requirement file should link to all versions and current active version.
- PRD file should store the human-readable PRD body plus structured frontmatter.
- RequirementState snapshot should be machine-readable JSON or YAML for diff and quality gate.

Compatibility constraint:

- Existing `Decision` schema in `docs/schemas/core-objects.md` remains valid.
- New fields should be optional for old records unless required by new high-impact decision flow.
- Old project tasks can link to Requirement later through migration without changing task ids.

## Audit And Notification

AuditLog required for:

- Requirement create/update/status transition.
- RequirementState field change.
- Clarification question sent and answer applied.
- PRD generation, approval, rejection, and supersession.
- Decision create, notify, approve, reject, supersede.
- AcceptanceCriteria create/update/status change.
- Approval attempt blocked by missing owner or criteria.
- ImpactReview create and accept/block.

NotificationRecord required for:

- Clarification question to submitter or owner.
- Requirement blocked or waiting for decision.
- Requirement approved or rejected.
- PRD ready for review.
- High-impact Decision waiting for human owner.
- PRD change impact review created.
- Downstream task owners affected by PRD or criteria change.

Notification body rules:

- First line: project/title/status/next action.
- Include owner and deadline when decision is needed.
- Raw ids appear only after readable labels.

## TaskResult Evidence Contract

When this domain work is implemented, the Development Agent TaskResult for the implementation slice must include:

- `requirementRefs`: all ANOS refs covered by the implementation.
- `outputRefs`: code files, schemas, docs, generated records, or CLI/API outputs.
- `evidenceRefs`: tests, command outputs, fixture records, review notes, and sample Requirement/PRD/Decision traces.
- `riskRefs` or `openRisks`: unresolved product or technical risks.
- `blockers`: missing Product Manager decisions or unavailable approval path.
- `nextActions`: review, test, migration, or follow-up task.
- `executorAgent`: Development Agent.
- `runner`: runner id when executed through Agent Ring or manual local runner.
- `sourceMaterialRefs`: requirements, PRD, task, governance docs.

Minimum evidence for this slice:

- Create Requirement from source fixture, show required fields and audit.
- RequirementState missing business model marked `missing`.
- Clarification round creates 1 to 3 questions and applies answer.
- PRD v1 generated, PRD v2 supersedes v1.
- Approval without owner or observable criteria blocked.
- Downstream ProjectTask links back to Requirement and criteria.
- High-impact Decision created for pricing/security/cross-team example.
- PRD change after task creation creates ImpactReview.

## Exceptions And Blockers

Expected blockers:

- Missing owner: Requirement cannot approve; notify submitter/project owner.
- Missing observable criteria: Requirement and PRD quality gate fail.
- Missing business model or market position: product discovery task cannot close.
- Sensitive source without permission: Requirement exists but read access is restricted.
- Human decision overdue: Requirement stays `decision_needed` or `blocked`; escalation notification.
- PRD change affects active tasks: ImpactReview required before new PRD becomes active.
- Contradictory evidence: field becomes `needs_approval` or `missing`; Decision or clarification required.
- No project binding: Requirement stays `draft` or `clarifying`; Agent Hub/project owner must bind or create project.

Error shape:

```yaml
ok: false
blockerCode: missing_acceptance_criteria
message: Requirement cannot be approved because no observable acceptance criteria exist.
owner: project owner or requirement owner
nextAction: Add at least one AcceptanceCriteria with observableSignal and verificationMethod.
objectRef: req...
auditRef: audit...
```

## Migration And Compatibility

Migration steps:

1. Add new object templates and validation rules behind existing markdown/YAML object model.
2. Backfill index links only for records that already have clear source/project/task refs.
3. For existing ProjectTasks with requirement-like text, create optional `requirementRef` only when source and owner can be identified.
4. Preserve old Decision records; add missing `impactLevel`, `impactAreas`, `deadline`, and `requirementRef` only when evidence exists.
5. Add a compatibility reader that treats absent new fields as `unknown` or `missing`, not as invalid old data.
6. Run migration dry-run before write mode; dry-run output lists candidate changes and skipped records.

Rollback:

- New files are append-only; rollback removes or ignores newly created Requirement/PRD/Decision/ImpactReview records from indexes.
- Existing records should not be destructively rewritten during first implementation slice.
- If new validation blocks existing workflows, gate it by object type and creation date until migration is complete.

## Implementation Slices And Order

1. Schema and template slice:
   Define Requirement, RequirementState, AcceptanceCriteria, PRDDocument, Decision extensions, ImpactReview templates, and validators.

2. Persistence and index slice:
   Add repository-backed read/write helpers, ids, current PRD resolution, and trace traversal.

3. State and gate slice:
   Implement Requirement and field state transitions, approval blockers, PRD quality gate, and criteria observability validation.

4. Clarification slice:
   Implement Socratic question generation contract, ClarificationRound records, answer application, and notifications.

5. PRD versioning slice:
   Generate PRD from RequirementState, preserve versions, supersede old PRDs, and expose PRD read APIs/CLI.

6. Decision slice:
   Create human-owned Decision requests for high-impact decisions and link them to Requirement/PRD.

7. Impact review slice:
   Detect PRD or criteria changes after task creation and create ImpactReview with affected tasks/tests/designs/results.

8. Trace and TaskResult evidence slice:
   Implement requirement trace view and ensure task completion evidence links requirement refs, output refs, evidence refs, risks, and next actions.

9. Migration slice:
   Add dry-run and guarded backfill for existing project/task/decision records.

10. Acceptance test slice:
   Add positive, negative, and E2E tests mapped to each requirement ref after Product Manager review accepts this solution.

## Test Strategy Mapping

| Requirement | Tests | Required coverage |
| --- | --- | --- |
| ANOS-REQ-010 | TC-REQ-001, AC-REQ-001 | Create durable Requirement with id, title, sourceRefs, owner/submitter, status, sensitivity, projectRef, audit. |
| ANOS-REQ-011 | TC-REQ-002, AC-REQ-002 | Field-level RequirementState marks business model and other fields known/assumed/missing/needs_approval. |
| ANOS-REQ-012 | TC-REQ-003 | Product Manager Agent creates 1 to 3 highest-value questions and answer updates RequirementState. |
| ANOS-REQ-013 | TC-REQ-004 | PRD and handoff separate evidence, inference, assumption, decision needed; unsupported market claim cannot masquerade as fact. |
| ANOS-REQ-014 | TC-REQ-005 | PRD v1/v2 preserved, linked to Requirement, sourceRefs, author Agent, reviewer, and version. |
| ANOS-REQ-015 | TC-REQ-006, AC-REQ-002 | Approval without owner or observable acceptance criteria returns blocker and audit. |
| ANOS-REQ-016 | TC-REQ-007, AC-REQ-005 | ProjectTasks link back to Requirement and criteria; trace view lists downstream tasks. |
| ANOS-REQ-020 | TC-PRD-001, AC-REQ-003 | PRD includes positioning, market positioning, business model, workflows, requirements, metrics, risks, open decisions, sourceRefs, quality gate. |
| ANOS-REQ-021 | TC-PRD-002, AC-REQ-004 | Pricing/security/legal/customer/cross-team Decision request has owner, options, tradeoffs, recommendation, deadline, audit. |
| ANOS-REQ-022 | TC-PRD-003 | PRD without non-goals and scope boundaries fails quality gate. |
| ANOS-REQ-023 | TC-PRD-004 | AcceptanceCriteria without observable signal is blocked; Test Agent can derive cases from accepted criteria. |
| ANOS-REQ-024 | TC-PRD-005, TC-E2E-003 | PRD change after task creation creates ImpactReview listing affected tasks, designs, tests, results. |

Regression set:

- TC-E2E-001 for full rough-idea-to-task lifecycle.
- TC-E2E-003 for PRD change impact review.
- Scheduler TC-SCH-007 because product discovery task closure depends on RequirementState and PRD quality gate.
- Review TC-REV-001 to TC-REV-004 when high-impact Decision route uses Review Center.
- Notification TC-NOT equivalents when notifications are available for clarification, decision, and impact review.

## Product Manager Agent Review Questions

1. Which RequirementState fields are approval blockers for complete launch: all listed fields, or a required subset plus documented assumptions?
2. Should `marketPosition` and `businessModel` be mandatory for internal tooling requirements, or only for customer/product-facing work?
3. Who is default human owner when submitter is an Agent or Feishu group: project owner, requester, or explicit decision owner?
4. What exact threshold makes a product choice high-impact: pricing/customer/security/legal/cross-team always, or configurable by project?
5. Can Product Manager Agent approve low-impact PRD drafts, or must every PRD approval include human review?
6. What deadline policy should high-impact Decision use when the submitter gives no deadline?
7. Should PRD version numbering be global per Requirement (`v1`, `v2`) or semantic (`major.minor`) when criteria changes are small?
8. Should assumptions be allowed in an approved PRD if they are explicitly marked, or must all assumptions become decisions or evidence first?
9. What user-facing wording should distinguish `clarifying`, `decision_needed`, and `blocked` to avoid confusing submitters?
10. Should impact review block all downstream work, or only tasks whose linked criteria/scope/workflow changed?

## Risks

- Over-strict required fields may block legitimate internal work.
- Too many Decision requests may slow product flow.
- PRD version diff may be noisy if generated text changes without semantic change.
- Existing records may lack owner/source data and fail new validators.
- Clarification quality depends on Product Manager Agent prompt and source extraction accuracy.
- Human-facing notifications can expose raw ids or sensitive context if sensitivity inheritance is missed.
- Impact review can under-detect affected tests or over-detect unrelated tasks without criteria links.

## Rollback Plan

- Keep first implementation append-only where possible.
- Feature-gate approval blockers until migration dry-run is reviewed.
- Preserve previous PRD versions and never overwrite old PRD files.
- If Decision routing causes launch blockage, downgrade new high-impact routing to `decision_needed` records plus notifications while keeping existing task flow active.
- If impact review produces false positives, keep PRD versioning active but mark ImpactReview as advisory until Product Manager Agent reviews thresholds.
- Roll back indexes by removing links to new records; source files remain auditable evidence unless Project Manager Agent approves cleanup.

## Product Review Entry Criteria

Product Manager Agent can review this solution when:

- Object model covers Requirement, RequirementState, PRDDocument, AcceptanceCriteria, Decision, and ImpactReview.
- State machines include approval blockers and human Decision route.
- CLI/API/storage/audit/notification contracts are explicit enough for implementation.
- Test mapping covers all requested requirement refs.
- Open product questions are listed.

## Implementation Note

This task stops at technical solution. No implementation code, test file, runtime schema, or existing project object is changed by this task.
