---
type: ReceiverReview
title: Receiver Review Title
description: Downstream Agent input acceptance gate before consuming upstream deliverables.
timestamp: 2026-06-23T00:00:00Z
reviewId: receiver-review.YYYYMMDD.001
projectId: project-id
upstreamRef: projects/project-id/tasks/task.md
receiverAgent: agent.company.development
reviewerAgent: agent.company.development
status: accepted_for_work
decision: accepted_for_work
artifactRefs: []
checklist: []
issues: []
assumptions: []
auditRefs: []
---

## Checklist

- Check that upstream artifact is complete enough for this role to continue.
- Check that task source and acceptance criteria are traceable.

## Issues

- Required when decision is needs_rework or human_decision_required.

## Assumptions

- Required when decision is accepted_with_assumptions.

## Artifacts

- Upstream documents, tasks, results, designs, technical plans, or test reports reviewed.
