---
type: Workflow
title: AI Native OS Requirement Tree Technical Solution
description: Technical solution for Requirement Tree model, import, validation, compiler, context packs, workbench, migration/backfill, tests, and rollback before implementation.
timestamp: "2026-06-21T09:42:17Z"
updatedAt: "2026-06-21T09:50:05Z"
solutionId: ts-ai-native-os-requirement-tree
projectId: company-knowledge-core
taskId: kt-ai-native-os-rt-tech-solution-requirement-tree
ownerAgent: agent.company.development
reviewAgents:
  - agent.company.product-manager
  - agent.company.project-manager
status: accepted
implementationStatus: not_started
requirementRefs:
  - BR-001
  - BR-002
  - BR-003
  - BR-004
  - BR-005
  - UREQ-001
  - UREQ-002
  - UREQ-003
  - UREQ-004
  - UREQ-005
  - UREQ-006
  - UREQ-007
  - UREQ-008
  - UREQ-009
  - UREQ-010
  - UREQ-011
  - UREQ-012
  - UREQ-013
  - UREQ-014
  - UREQ-015
sourceMaterialRefs:
  - docs/product/ai-native-os/requirement-tree.md
  - docs/product/ai-native-os/requirements.md
  - projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-resplit-plan.md
  - projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-coverage-matrix.md
  - projects/company-knowledge-core/tasks/kt-ai-native-os-rt-tech-solution-requirement-tree.md
reviewRefs:
  - projects/company-knowledge-core/product-reviews/ai-native-os-requirement-tree-technical-solution-review.md
---
# AI Native OS Requirement Tree Technical Solution

## 1. Scope

This document is the technical solution for `kt-ai-native-os-rt-tech-solution-requirement-tree`.

It defines how the AI Native OS requirement tree should become a controlled, traceable product package that can later drive task queue generation, Agent context packs, workbench views, tests, review, and historical backfill.

This task does not implement production code. Implementation tasks remain blocked until Product Manager Agent and Project Manager Agent accept this technical solution.

Primary sources:

- `docs/product/ai-native-os/requirement-tree.md`
- `docs/product/ai-native-os/requirements.md`
- `projects/company-knowledge-core/coordination/ai-native-os-requirement-tree-resplit-plan.md`
- `projects/company-knowledge-core/technical-solutions/ai-native-os-requirement-prd-domain.md`
- `projects/company-knowledge-core/technical-solutions/ai-native-os-scheduler-runner-result.md`

## 2. Design Goals

- Keep business, user, product, functional, test, acceptance, and execution traceability in one durable structure.
- Preserve source-first governance: raw input becomes `SourceMaterial` or source refs before reusable knowledge or executable tasks.
- Let Product Manager Agent own requirement quality before Project Manager Agent compiles executable work.
- Make missing owner, evidence, tests, or acceptance gates visible blockers, not silent executable tasks.
- Support distributed Agent Ring execution without putting Agent Ring implementation inside this repository.
- Backfill current AI Native OS materials without losing history or rewriting completed TaskResult evidence.

## 3. Non-Goals

- No production implementation in this technical-solution task.
- No Agent Ring runtime implementation.
- No direct publishing of reusable knowledge from imported requirement documents.
- No importer, validator, compiler, workbench, or historical backfill inside the first implementation slice.
- No migration that rewrites existing task/result files in place without snapshot and rollback.

## 4. Object Model

The requirement tree layer should extend the existing Requirement, RequirementState, AcceptanceCriteria, PRDDocument, Decision, ProjectTask, TaskResult, SourceMaterial, AgentRun, AuditLog, and NotificationRecord contracts. It should not replace them.

### 4.1 RequirementTree

Purpose: versioned product package for one project or product area.

Required fields:

- `treeId`: stable id, format `rt.<project>.<slug>.<version>`.
- `type`: `RequirementTree`.
- `projectRef`.
- `title`.
- `version`.
- `status`: `draft`, `reviewing`, `accepted`, `blocked`, `superseded`.
- `sourceRefs`: requirement tree doc, functional requirements doc, coverage matrix, PM review records.
- `businessRequirementRefs`: `BR-*` nodes.
- `userRequirementRefs`: `UREQ-*` nodes.
- `productRequirementRefs`: product-level requirements derived from PRD or coverage matrix.
- `functionalRequirementRefs`: `ANOS-REQ-*` refs.
- `acceptanceGateRefs`.
- `testCaseRefs`.
- `taskRefs`.
- `resultRefs`.
- `coverageSnapshotRef`.
- `reviewRefs`.
- `auditRefs`.

Rules:

- `accepted` requires Product Manager Agent and Project Manager Agent review refs.
- `accepted` requires zero high-severity coverage blockers.
- Each source ref must remain external-readable or have a stored evidence/hash reference.
- Tree versions are append-only. New import creates new version and supersedes prior version after review.

### 4.2 RequirementNode

Purpose: normalized node for BR, UREQ, product requirement, non-functional requirement, governance requirement, and functional requirement references.

Required fields:

- `nodeId`: source id such as `BR-001`, `UREQ-005`, `ANOS-REQ-010`, or generated `PREQ-*`.
- `type`: `RequirementNode`.
- `nodeKind`: `business`, `user`, `product`, `functional`, `non_functional`, `governance`, `data`, `integration`, `ops`.
- `treeRef`.
- `title`.
- `statement`.
- `whyItMatters` or `problem`.
- `successSignal` or `acceptanceSignal`.
- `ownerRole`.
- `sourceRefs`.
- `sourceLocation`: file path plus heading/table row anchor when available.
- `status`: `draft`, `needs_clarification`, `ready_for_planning`, `accepted`, `blocked`, `superseded`.
- `sensitivity`.
- `parentRefs`.
- `childRefs`.
- `acceptanceGateRefs`.
- `testCaseRefs`.
- `taskRefs`.
- `resultRefs`.
- `decisionRefs`.
- `auditRefs`.

Rules:

- Functional nodes may reference existing `ANOS-REQ-*` ids from `requirements.md` instead of duplicating text.
- Product requirement nodes bridge `UREQ-*` to implementation-facing `ANOS-REQ-*` when the source tree lacks a separate product id.
- Parent and child refs must be bidirectional after validation.

### 4.3 RequirementMapping

Purpose: auditable edge between requirement levels and execution evidence.

Required fields:

- `mappingId`.
- `type`: `RequirementMapping`.
- `treeRef`.
- `fromRef`.
- `toRef`.
- `mappingKind`: `decomposes_to`, `satisfies`, `verified_by`, `implemented_by`, `accepted_by`, `blocked_by`, `supersedes`.
- `confidence`: `source_exact`, `pm_confirmed`, `agent_inferred`, `backfill_inferred`.
- `rationale`.
- `sourceRefs`.
- `createdByAgentRef`.
- `reviewState`: `draft`, `accepted`, `needs_review`, `rejected`.
- `auditRefs`.

Rules:

- `agent_inferred` and `backfill_inferred` mappings cannot unlock executable tasks until reviewed.
- `implemented_by` must point to ProjectTask or TaskResult refs that link back to requirement refs.
- `verified_by` must point to test cases, eval cases, or acceptance gates with observable criteria.

### 4.4 AcceptanceGate

Purpose: launch or review gate tied to one or more requirement nodes.

Required fields:

- `gateId`.
- `type`: `AcceptanceGate`.
- `treeRef`.
- `requirementRefs`.
- `ownerRole`.
- `verificationMethod`: `manual_review`, `automated_test`, `api_check`, `document_check`, `e2e_flow`, `metric_check`.
- `observableSignal`.
- `requiredEvidenceRefs`.
- `status`: `draft`, `ready`, `passed`, `failed`, `blocked`, `waived`.
- `waiverDecisionRef`.
- `sourceRefs`.
- `auditRefs`.

Rules:

- `waived` requires human or authorized governance decision ref.
- Gates without observable signals block requirement approval.

### 4.5 RequirementCoverageSnapshot

Purpose: immutable validation report for review and workbench display.

Required fields:

- `snapshotId`.
- `type`: `RequirementCoverageSnapshot`.
- `treeRef`.
- `treeVersion`.
- `counts`: BR, UREQ, product, functional, acceptance, tests, tasks, results, blockers.
- `coverageRows`: BR -> UREQ -> ProductRequirement -> ANOS -> Task -> Result -> Test -> Acceptance.
- `blockers`: structured list with severity, ownerRole, nodeRef, reason, suggestedFix.
- `generatedAt`.
- `generatedByAgentRef`.
- `sourceRefs`.
- `auditRefs`.

Rules:

- Snapshots are append-only.
- Workbench reads snapshots, not ad hoc recomputation, for reviewable historical state.

## 5. Storage And File Layout

Preferred future layout:

```text
projects/company-knowledge-core/requirements/
  requirement-trees/
    rt.company-knowledge-core.ai-native-os.vYYYYMMDDHHMMSS.json
  nodes/
    BR-001.json
    UREQ-001.json
    PREQ-001.json
    ANOS-REQ-010.ref.json
  mappings/
    rt.company-knowledge-core.ai-native-os.vYYYYMMDDHHMMSS.mappings.json
  gates/
    acceptance-gates.json
  snapshots/
    coverage-snapshot.YYYYMMDDHHMMSS.json
```

Compatibility:

- Existing markdown strategy and product docs remain source material.
- Existing task files remain ProjectTask truth.
- Existing result files remain TaskResult truth.
- New JSON records only add traceability and review state.

## 6. Importer Design

Importer is RT-DEV-002, not the first slice.

Inputs:

- `docs/product/ai-native-os/requirement-tree.md`
- `docs/product/ai-native-os/requirements.md`
- PM coverage matrix output for 5 BR, 15 UREQ, product requirements, 74 ANOS functional requirements, tasks, results, tests, and launch gates.

Behavior:

- Parse markdown tables with a structured markdown parser or table parser, not line-only string splitting.
- Preserve source file, heading, row id, row hash, and imported text.
- Create a draft RequirementTree version plus RequirementNode, RequirementMapping, AcceptanceGate, and RequirementCoverageSnapshot draft records.
- Normalize known ids: `BR-*`, `ROLE-*`, `UREQ-*`, `ANOS-REQ-*`.
- Generate `PREQ-*` only where product-level requirement rows do not already exist.
- Detect duplicate ids, changed row hashes, deleted rows, and renamed titles.
- Write AuditLog for import attempt, created records, blocked rows, and source hashes.

Failure behavior:

- Invalid or ambiguous rows produce an import report and blocker records.
- Import does not partially promote tree status to `accepted`.
- Import does not create executable ProjectTasks.

## 7. Validator Design

Validator is RT-DEV-002 with importer, then reused by compiler, context pack, workbench, and backfill.

Validation groups:

- Shape: required fields, id formats, status enums, sensitivity, audit refs.
- Referential integrity: every parent/child edge is bidirectional; every mapping endpoint exists or is an allowed external ref.
- Coverage: 5 BR, 15 UREQ, product requirements, 74 ANOS refs, task refs, result refs, tests, and acceptance gates are counted and gap-reported.
- Governance: accepted tree has PM and Project Manager review refs; high-impact decisions have Decision refs.
- Execution readiness: every executable candidate has owner role, acceptance gate, allowed agent role, required capability, source refs, and test/evidence expectation.
- Security: no secret values in statements, evidence, mappings, gates, or snapshots.
- Review readability: blocker messages use human-readable labels first; raw ids are secondary.

Validator output:

- `pass`: safe for next stage.
- `warn`: safe to review, not safe to compile executable tasks unless explicitly allowed.
- `block`: cannot accept, compile, or backfill as truth.

Required negative cases:

- Orphan `ANOS-REQ-*`.
- UREQ with no BR parent.
- Functional requirement with no acceptance gate.
- Task/result ref that does not link back.
- Missing owner role.
- Missing test expectation where `requiresTests` is true.
- Secret-like token or credential in imported text.

## 8. Task Queue Compiler Design

Compiler is RT-DEV-003, after importer and validator pass.

Inputs:

- Accepted RequirementTree version.
- CoverageSnapshot with no high-severity blockers.
- Role operating specs.
- Existing scheduler/task runtime contracts.

Outputs:

- Draft ProjectTask queue grouped by role: Product Manager, Project Manager, Design, Development, Test, Operations, Knowledge Engineering, Governance.
- Blocker tasks where input is incomplete.
- Dependency graph between tasks.
- TaskRuntime fields including stage, required capabilities, risk level, acceptance path, review path, closure policy, evidence requirements, and source refs.

Compilation rules:

- Each generated ProjectTask includes BR, UREQ, ProductRequirement, ANOS, test, acceptance, and source refs when available.
- Missing owner/evidence/test/gate creates blocked clarification or review task, not executable development work.
- Compiler must be deterministic for the same accepted tree version.
- Compiler must not overwrite human-edited existing tasks. It creates new draft tasks or proposes patches for review.
- Compiler emits AuditLog and NotificationRecord candidates for review, but does not send notifications until queue is accepted.

## 9. Agent Context Pack Design

Context pack integration is RT-DEV-004.

Goal: every Agent receives traceability context appropriate to its role without dumping the whole requirement corpus.

Context pack additions:

- `requirementTreeRef`.
- `treeVersion`.
- `traceabilitySlice`: BR, UREQ, ProductRequirement, ANOS, acceptance gates, tests, source refs, decisions, and blockers relevant to the assigned task.
- `operatingRuleRefs`.
- `requiredEvidence`.
- `reviewPath`.
- `blockedIfMissing`: explicit missing inputs that should stop work.

Role-specific views:

- Product Manager Agent sees source, assumptions, decisions, open clarifications, and acceptance quality.
- Project Manager Agent sees dependencies, owners, blockers, launch gates, and queue status.
- Design Agent sees users, scenarios, workflows, constraints, states, and usability criteria.
- Development Agent sees implementation scope, non-goals, allowed tools, tests, dependencies, and acceptance criteria.
- Test Agent sees observable criteria, coverage gaps, expected test methods, and launch gates.
- Operations Agent sees metrics, feedback loops, rollout gates, and incident criteria.
- Knowledge Engineering Agent sees source/result evidence and review boundaries.

## 10. Workbench Design

Workbench integration is RT-DEV-005.

Read model:

- Tree status and version.
- BR -> UREQ -> ProductRequirement -> ANOS -> Task -> Result -> Test -> Acceptance rows.
- Coverage counts and blocker counts.
- Unmapped, untested, unowned, unaccepted, and blocked items.
- Task/result lifecycle status.
- Review and approval state.

Behavior:

- Workbench reads RequirementCoverageSnapshot and task/result indexes.
- Workbench does not mutate source truth directly.
- Actions create review requests, clarification tasks, or compiler proposals.
- Internal ids can be shown as secondary details, but primary labels must be human-readable.

## 11. Historical 74 Backfill

Backfill is RT-DEV-006, after importer, validator, compiler, context pack, and workbench slices have reviewable contracts.

Scope:

- Backfill all 74 `ANOS-REQ-*` items from `docs/product/ai-native-os/requirements.md`.
- Connect them to 5 BR and 15 UREQ from `requirement-tree.md`.
- Link existing ProjectTasks, TaskResults, tests, and launch gates where evidence exists.
- Mark inferred links as `backfill_inferred` until PM or Project Manager review accepts them.

Process:

1. Create snapshot of existing tasks, results, tests, and product docs.
2. Import current tree and functional requirements into a draft tree version.
3. Generate coverage snapshot with gaps.
4. Match existing task/result refs by explicit ids first, then title/description similarity only as inferred candidates.
5. Produce backfill report: accepted links, inferred links needing review, gaps, conflicts, and obsolete refs.
6. Create ReviewRecord or PM review artifact for inferred mappings.
7. Promote reviewed mappings only after acceptance.

Rollback:

- Backfill writes append-only tree, mapping, and snapshot files.
- Existing tasks/results are not edited in place during first backfill.
- Rollback removes or supersedes new backfill version and mapping files, leaving original task/result evidence intact.

## 12. Test Strategy

RT-TECH-001 test evidence:

- This solution document exists and covers required areas.
- No production code changes are included.
- TaskResult links this document as evidence.

Future slice tests:

- Object model unit tests: required fields, enums, id formats, bidirectional edges, source/audit refs.
- Importer tests: parse 5 BR, 15 UREQ, 74 ANOS refs; row hashes; duplicate ids; malformed tables; changed sources.
- Validator tests: orphan nodes, missing owner, missing gate, missing test, missing source, invalid sensitivity, unreviewed inferred mapping.
- Compiler tests: role-specific tasks, dependency order, blocked task generation, deterministic output, no overwrite of existing human-edited tasks.
- Context pack tests: each role receives only relevant traceability, with operating rules and acceptance criteria present.
- Workbench tests: snapshot read model, gap display, blocked/unmapped/untested indicators, human-readable labels.
- Backfill tests: snapshot before write, inferred mapping review state, rollback supersedes/removes new records only.
- Lifecycle tests: import -> validate -> review -> compile -> context pack -> task result -> coverage update.

## 13. Migration And Compatibility

Migration principle: append first, promote after review.

Plan:

- Add object model records behind a new requirement-tree directory.
- Keep markdown docs as source material.
- Keep ProjectTask and TaskResult files as execution truth.
- Add indexes/snapshots rather than rewriting existing records.
- Gate promotion through validator and PM/Project Manager review.
- Defer any schema hardening until object model slice proves record shape.

Compatibility risks:

- Existing tasks may lack explicit requirement refs.
- Existing TaskResults may have evidence but no structured ANOS mapping.
- Some product requirements may exist only as UREQ rows, requiring generated `PREQ-*` bridge nodes.

Mitigation:

- Use inferred mapping review states.
- Keep original ids and file refs.
- Do not block current manual workflows while tree records are draft.

## 14. Rollback Plan

Object model slice rollback:

- Remove or supersede newly added requirement-tree object records.
- Re-run validation to confirm no existing task/result refs require removed records.
- Leave existing markdown sources, ProjectTasks, TaskResults, and AgentRuns untouched.

Importer/validator rollback:

- Disable importer command/API entry.
- Retain failed import reports as audit evidence.
- Supersede invalid tree versions instead of editing history.

Compiler rollback:

- Delete unaccepted generated draft tasks or mark them `rejected`.
- Do not modify accepted human-created tasks automatically.

Workbench rollback:

- Hide requirement tree read model route/section.
- Existing snapshots remain auditable files.

Backfill rollback:

- Supersede backfill tree version and coverage snapshot.
- Remove unaccepted generated mappings.
- Keep original task/result evidence unchanged.

## 15. Security Boundary

- SourceMaterial and source refs are required before imported requirements can be treated as evidence.
- Requirement records must not store secrets, tokens, keys, passwords, or raw private dumps.
- Sensitivity inherits the highest sensitivity from source refs and can only be lowered by authorized review.
- Agent-generated inferred mappings cannot unlock executable tasks or verified knowledge.
- Human approval is required for verified knowledge, policies, permission changes, security/legal/customer-impacting decisions, and high-impact waivers.
- Agent Ring remains external. This project defines task/result/context contracts only.
- Workbench and notifications must use human-readable summaries first and raw ids as secondary detail.

## 16. Implementation Slices

### Slice 1: Object Model Only

Purpose: create durable requirement tree object records and tests for shape/integrity.

Includes:

- RequirementTree, RequirementNode, RequirementMapping, AcceptanceGate, RequirementCoverageSnapshot record definitions.
- Storage directory convention.
- Validation helpers limited to object shape and local refs.
- Unit tests for required fields, enums, ids, source refs, audit refs, bidirectional edge shape, and no-secret check.

Explicitly excludes:

- Importer.
- Markdown parsing.
- Compiler.
- Agent context pack changes.
- Workbench read model.
- Historical 74 backfill.
- Any generated ProjectTask queue.

Acceptance:

- Object model exists.
- Object model tests pass.
- No importer/compiler/workbench/backfill behavior is hidden in this slice.

### Slice 2: Import And Validation

Parse requirement sources, create draft tree version, and validate 5 BR, 15 UREQ, product requirements, 74 ANOS refs, owners, tests, acceptance, source refs, and blocker cases.

### Slice 3: Product Package To Task Queue Compiler

Compile accepted tree versions into role-specific draft ProjectTasks and blocker tasks, preserving scheduler runtime contracts.

### Slice 4: Agent Context Pack Traceability

Inject role-specific traceability slices into task context packs and verify operating rules, acceptance criteria, tests, and blockers are visible.

### Slice 5: Requirement Tree Workbench View

Expose snapshot-based traceability and risk views in the workbench read model.

### Slice 6: Historical 74 Backfill

Backfill existing 74 ANOS functional requirements and map existing tasks/results/tests where evidence supports the mapping.

### Slice 7: End-To-End Governance And Launch Gate

Run lifecycle validation across import, review, compile, execution result, test, acceptance, snapshot update, and rollback evidence.

## 17. Review Readiness Checklist

- Covers object model, importer, validator, compiler, Agent context pack, workbench, historical 74 backfill, test strategy, migration/rollback, security boundary, and slicing.
- States first implementation slice only does object model.
- Keeps importer/compiler/workbench/backfill out of first slice.
- Keeps Agent Ring external.
- Uses source-first and review-gated governance.
- Preserves existing task/result evidence.
- Makes PM and Project Manager acceptance required before implementation tasks proceed.
