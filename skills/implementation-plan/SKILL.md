---
name: implementation-plan
description: Use when turning an approved requirement or root cause into a scoped engineering implementation plan.
---

# Implementation Plan

## Purpose

Translate approved work into safe, testable code changes.

## Triggers

- Development Agent receives a task with product/design/test input.
- A root cause has been confirmed.
- A technical slice needs implementation.

## Inputs

- Requirement, design spec, acceptance criteria, or root cause.
- Repository context.
- Existing tests and architecture constraints.

## Workflow

1. Read the relevant architecture and code path.
2. Define files, interfaces, data changes, and risk.
3. Keep changes scoped to the task.
4. Add or update tests proportional to risk.
5. Produce TaskResult with evidence and next handoff.

## Outputs

- Technical plan.
- Code change summary.
- Test evidence.
- Handoff to Test or Project Manager Agent.

## Quality Gate

- The plan is implementable without hidden assumptions.
- Tests verify the changed behavior.
- No unrelated refactor is introduced.

## Failure Routes

- Product ambiguity: return to Product Manager Agent.
- Design ambiguity: return to Design Agent.
- Missing access or dependency: route to Project Manager Agent.
