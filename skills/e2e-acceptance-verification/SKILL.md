---
name: e2e-acceptance-verification
description: Use when verifying an end-to-end workflow across UI, API, callback, status, notification, and persisted evidence.
---

# E2E Acceptance Verification

## Purpose

Prove a workflow works as a user and as a system lifecycle.

## Triggers

- Feishu card, approval, notification, scheduler, or Runner flow changed.
- A product workflow must be accepted.
- A previous fix only covered unit behavior.

## Inputs

- Workflow steps.
- Expected user-visible output.
- API/state/audit expectations.
- Test environment.

## Workflow

1. Execute the user path.
2. Verify persisted state.
3. Verify callback/result handling.
4. Verify notifications and stale UI behavior.
5. Record evidence and failure screenshots/logs.

## Outputs

- E2E result.
- Evidence refs.
- Defects or acceptance recommendation.

## Quality Gate

- User-visible result and backend state both match.
- Failure messages are actionable.
- Evidence is sufficient for human acceptance.

## Failure Routes

- External service unavailable: mark blocked with retry condition.
- Permission missing: route to integration owner.
- Defect found: create development repair task.
