---
type: ImpactReview
title: PM Outcome Slice Guardrail Architecture Review
impactReviewId: impact-review-pm-outcome-slice-guardrail
requirementRef: system-issue:pm-low-outcome-token-burn
fromPrdRef: docs/agent-team/agent-delivery-thinking-framework.md
toPrdRef: docs/agent-team/agent-delivery-thinking-framework.md
changedFields:
  - Project Manager dispatch unit
  - PM action validation
  - Task and TaskResult traceability
owner: agent.company.architect
status: approved
---

## Review

The root issue is not missing role participation. The system allowed Project Manager work to be measured by task count, role handoff count, and report creation, while the user-visible outcome state stayed unchanged.

The approved architecture change is to introduce `OutcomeSlice` as the formal PM scheduling unit:

- one stage goal
- one main deliverable
- current state to target state
- evidence and acceptance signal
- WIP/time/token guardrail
- stop conditions

Formal PM actions that decompose, dispatch, hand off, route acceptance, close out, or escalate risk must reference an `OutcomeSlice` and explain the state/value change. Project tasks may reference the same slice, and TaskResult records inherit the reference.

This keeps Agent roles useful only when they move the outcome or reduce uncertainty. It also prevents template-heavy or role-heavy execution from appearing as progress.

## Scope

This review approves the central model, CLI, validation, project entrypoint rules, and tests. It does not require changing business project artifacts during this patch.

