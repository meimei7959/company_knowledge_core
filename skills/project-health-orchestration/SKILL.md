---
name: project-health-orchestration
description: Use when checking project health, blockers, notifications, approvals, role handoffs, and next actions.
---

# Project Health Orchestration

## Purpose

Keep a project moving by detecting blocked work, missing approvals, missing notifications, and stale handoffs.

## Triggers

- A user asks for project status.
- A task finishes, fails, or waits for acceptance.
- A project has no next task or a blocked task.

## Inputs

- Project record.
- Task queue and TaskResult records.
- Approval, notification, Runner, and Agent status.

## Workflow

1. Summarize project status in human-readable Chinese.
2. Group tasks into done, active, blocked, waiting decision, and waiting acceptance.
3. Identify the single highest-leverage next action.
4. Notify the relevant owner or Project Manager Agent.
5. Create repair tasks only when the status cannot be fixed by a direct next action.

## Outputs

- ProjectManagerReview.
- Next action list.
- NotificationRecord or repair task.

## Quality Gate

- The status explains business meaning, not raw internal codes.
- Every blocker has an owner and proposed next step.
- The answer avoids duplicate or contradictory next actions.

## Failure Routes

- Missing project: route to project resolution.
- Missing evidence: create project data repair task.
- Notification failure: create notification recovery record.
