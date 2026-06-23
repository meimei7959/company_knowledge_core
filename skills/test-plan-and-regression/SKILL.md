---
name: test-plan-and-regression
description: Use when creating test plans, regression coverage, and release quality checks for changed behavior.
---

# Test Plan And Regression

## Purpose

Define the tests required to prove changed behavior is safe.

## Triggers

- A feature or bug fix is ready for verification.
- A workflow has changed.
- Regression risk needs explicit coverage.

## Inputs

- Requirement or bug.
- Implementation summary.
- Acceptance criteria.
- Existing test inventory.

## Workflow

1. Identify critical user and system paths.
2. Map acceptance criteria to tests.
3. Add regression checks for previous failures.
4. Define manual checks only where automation is not available.
5. Return pass/fail evidence and release recommendation.

## Outputs

- Test plan.
- Regression checklist.
- Test evidence.
- Release recommendation.

## Quality Gate

- Every acceptance criterion has a verification method.
- Known previous failures are covered.
- Failures include reproduction and owner.

## Failure Routes

- Missing acceptance criteria: return to Product Manager Agent.
- Missing implementation evidence: return to Development Agent.
- Blocking defect: create repair task.
