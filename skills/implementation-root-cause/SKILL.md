---
name: implementation-root-cause
description: Use when debugging repeated engineering failures, integration issues, test failures, or production behavior gaps.
---

# Implementation Root Cause

## Purpose

Find root cause before changing code.

## Triggers

- A bug repeats after multiple fixes.
- Integration, approval, notification, card callback, scheduler, or Runner behavior fails.
- Tests fail without obvious local cause.

## Inputs

- Error symptoms, logs, screenshots, and reproduction steps.
- Relevant code paths and tests.
- Expected behavior and affected workflow.

## Workflow

1. Reproduce or locate the failing path.
2. Trace upstream input, internal state, output, callback/result handling, audit, and notification.
3. Identify root cause and blast radius.
4. Propose the smallest systemic fix.
5. Add tests that fail before the fix and pass after.

## Outputs

- Root cause summary.
- Fix plan.
- Test plan.
- Risk notes.

## Quality Gate

- Root cause is evidence-backed.
- Fix covers lifecycle, not only the visible symptom.
- Tests cover the failing workflow.

## Failure Routes

- Cannot reproduce: create diagnostic task.
- Missing permission or external event: create integration verification task.
- Risk too high: ask Project Manager Agent for sequencing.
