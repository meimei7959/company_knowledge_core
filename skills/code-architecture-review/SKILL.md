---
name: code-architecture-review
description: Use when Architecture Agent reviews implementation after Development Agent changes code, especially for module boundaries, API/data contracts, maintainability, refactor safety, testability, and alignment with the approved architecture/technical plan.
---

# Code Architecture Review

## Purpose

Verify that delivered code follows the approved architecture and remains maintainable.

## Triggers

- Development Agent finishes a feature, fix, migration, integration, or refactor.
- Test Agent finds systemic defects or repeated regressions.
- A code change touches shared modules, contracts, persistence, permission, scheduler, workflow, or public API.
- The implementation diverges from the architecture plan.

## Inputs

- Approved `TechnicalArchitecturePlan` or `ArchitectureDecision`.
- Code refs, changed files, diff summary, tests, logs, and known risks.
- Product/design acceptance criteria and runtime constraints.

## Workflow

1. Compare implementation against the architecture plan and task scope.
2. Inspect module boundaries, coupling, contracts, data model changes, error handling, observability, tests, and rollback safety.
3. Classify findings as `must-fix`, `should-fix`, `accepted-risk`, or `no-issue`.
4. For every `must-fix`, provide evidence, impact, and a concrete repair direction.
5. Decide the next handoff: Development repair, Test verification, Project Manager escalation, or Knowledge Engineering capture.

## Outputs

- `CodeArchitectureReview` with conclusion, findings, evidence refs, required fixes, accepted risks, and next handoff.
- Repair task summary for Development Agent when needed.
- Knowledge capture candidate for reusable architecture lessons.

## Quality Gate

- Every blocking finding cites code, contract, test, or runtime evidence.
- Review distinguishes architecture blockers from style preferences.
- No unbounded refactor is requested without scope and acceptance criteria.
- The next Agent can act without reinterpreting the review.

## Failure Routes

- Missing diff or evidence: return to Development Agent.
- Missing plan: create or request `TechnicalArchitecturePlan` first.
- Test evidence insufficient: hand off to Test Agent.
- Cross-project risk: escalate to Project Manager Agent.
