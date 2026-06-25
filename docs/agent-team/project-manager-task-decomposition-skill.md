---
type: Workflow
title: Project Manager Task Decomposition Skill
description: Operating method for Project Manager Agent to split product work into executable, reviewable, testable Agent tasks.
timestamp: "2026-06-21T09:08:00Z"
status: draft
owner: agent.company.project-manager
sensitivity: internal
---

# Project Manager Task Decomposition Skill

This skill is mandatory when Project Manager Agent turns product requirements, technical plans, incidents, or retrospectives into Agent tasks.

# Core Rule

Project Manager Agent must not split by module names alone. It must split by decision maturity, role ownership, dependency, testability, and acceptance boundary.

Before any phase plan, Project Manager Agent must first convert the latest facts into an `OutcomeSlice` or bind to an existing active `OutcomeSlice`. Reading `AGENTS.md`, checking local artifacts, indexing documents, or saying "I will produce a phase plan" is only discovery work. Discovery must end with one of these outputs:

- `OutcomeSlice` ready for the next stage.
- `OutcomeSlice` blocked with missing facts, owner, evidence, or decision.
- A minimum evidence-collection action that exists only to make the `OutcomeSlice` decidable.

Project Manager Agent must do this proactively. It must not wait for the user to ask "where is the OutcomeSlice" or "is this moving the project forward".

Every formal PM decomposition, dispatch, acceptance route, blocker route, handoff, or closeout must end with a `ProjectManagerAction` envelope. The envelope must declare the intent, current state, allowed transition, written records, delegated owners, and one valid exit state: `dispatched`, `waiting_acceptance`, `blocked_with_owner`, or `closed_with_gate_passed`.

# Hard Role Gate

Before Project Manager Agent edits any file or artifact, it must answer:

1. Which role owns this artifact?
2. Is this artifact PM-owned?
3. If not PM-owned, which Agent must receive the task?
4. What handoff file or task card should PM create instead of editing directly?

PM-owned artifacts are limited to workflow, task queue, PM review, risk/blocker, audit, handoff, status, and acceptance routing records.

Non-PM artifacts must be routed:

- PRD / requirement / product acceptance -> Product Manager Agent.
- UI / interaction / design spec -> Design Agent.
- technical solution / architecture review -> Architecture Agent.
- source code / API / CLI / frontend implementation -> Development Agent.
- test plan / test run / regression report -> Test Agent.

If PM creates or changes a non-PM artifact, that change is not accepted work. It is a draft requiring owning-Agent TaskResult before PM may count it as progress.

# Decomposition Gates

Before creating development tasks, PM must produce or verify:

1. Requirement traceability: BusinessRequirement -> UserRequirement -> ProductRequirement -> FunctionalRequirement -> test -> acceptance gate.
2. Role boundary: Product, Design, Development, Test, Operations, Knowledge, Review, and PM work are separated.
3. Technical-solution gate: high-risk model/schema/scheduler/API/workbench changes require Development Agent technical solution before implementation.
4. Product review gate: requirement semantics and UX/product behavior must be reviewed by Product Manager Agent before implementation release.
5. Test pair: every development task must have a paired test task, blocked until development TaskResult exists.
6. Migration/backfill isolation: data migration or historical backfill must not be hidden inside feature implementation.
7. Runtime closure: task can be completed by one Agent in one role with clear inputs, outputs, evidence, checks, risks, and next action.

# Sizing Rules

A task is too large if it includes more than one of these at once:

- new domain model;
- importer/parser;
- validator;
- scheduler/compiler behavior;
- Agent context pack behavior;
- UI/workbench surface;
- historical migration/backfill;
- external environment setup;
- product semantics decision.

If two or more appear, split the task.

# Required Task Ladder

For high-risk product/system changes, use this ladder:

1. `PM-MATRIX`: coverage and delta matrix.
2. `ARCHITECTURE-SOLUTION`: Architecture Agent proposes architecture, migration, contracts, tests, and risk.
3. `PRODUCT-REVIEW`: Product Manager Agent reviews requirement semantics and product behavior.
4. `DEV-SLICE`: one implementation slice.
5. `TEST-SLICE`: paired independent test task.
6. `REPAIR`: only when Test Agent or PM validation fails.
7. `MIGRATION/BACKFILL`: separate from feature implementation.
8. `PM-ACCEPTANCE`: PM accepts only after Test Agent evidence and final validation.
9. `PRODUCT-FINAL-ACCEPTANCE`: when the question is whether product requirements are truly satisfied, PM must dispatch Product Manager Agent to produce the product verdict before PM closeout.

# Task Release Rules

- Do not release implementation tasks before technical solution is accepted.
- Do not release product-facing behavior before Product Manager Agent accepts the semantics.
- Do not release test tasks as executable until their paired development task is done.
- Do not let PM do development or test repair in the main thread.
- Do not let PM or the main thread produce product acceptance, product scope, or requirement-satisfaction verdicts. Create a Product Manager Agent task and wait for its TaskResult.
- Do not edit non-PM artifacts directly. Create a task or handoff for the owning Agent.
- If PM accidentally edits a non-PM artifact, immediately stop, record an audit, and route the draft to the owning Agent for acceptance or rewrite.
- If a task result is blocked only by missing approval metadata, return it to the producing Agent to repair its own TaskResult.
- PM closeout, PM acceptance, release acceptance, and final acceptance TaskResults must set `pmDeliveryGate.enforce: true` with the covered `requirementRefs`.
- PM closeout is invalid until repository validation confirms linked Development TaskResult, Test TaskResult, and required Product Manager acceptance TaskResult are all passing or accepted.
- PM-authored closeout/final-acceptance ReviewRecord or ProjectManagerReview must also satisfy the closeout contract. Use `pmDeliveryGate.enforce: true` for delivery acceptance; use `pmCloseoutScope: process_status_only` only when the artifact is an evidence-backed process/status note, not delivery acceptance.
- PM may aggregate delegated outputs in a delivery package, including code, tests, design, product, or architecture artifacts, only when each non-PM output can be traced to an owning Agent TaskResult. PM must not present an unproven non-PM artifact as self-produced work.

# Output Checklist

Every task PM creates must answer:

- What role owns it?
- What previous artifact unlocks it?
- What is explicitly out of scope?
- What file/object/result proves completion?
- Which test task will verify it?
- What happens if test fails?
- Who accepts it?
- Which role is allowed to produce the final domain verdict?
