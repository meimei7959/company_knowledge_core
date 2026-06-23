---
type: ProjectManagerAction
title: PM Action
description: Project Manager state-machine action envelope.
timestamp: 2026-06-23T00:00:00Z
actionId: pm-action-YYYYMMDD-001
projectId: project-id
taskId: ""
actor: agent.company.project-manager
intent: dispatch
currentState: ""
allowedTransition: ""
exitState: dispatched
summary: ""
requirementRefs: []
recordsWritten: []
delegatedOwners: []
evidenceRefs: []
nextAction: ""
blocker: ""
blockerOwner: ""
terminalDecision: ""
pmDeliveryGate:
  enforce: false
  requirementRefs: []
  requireProductAcceptance: true
---

## Summary

What PM changed in the project state.

## State Transition

- `intent`: one of status_query, task_decomposition, dispatch, acceptance_route, risk_escalation, blocker_record, handoff, closeout.
- `exitState`: one of dispatched, waiting_acceptance, blocked_with_owner, closed_with_gate_passed.

## Exit Contract

- `dispatched` requires recordsWritten, delegatedOwners, or nextAction.
- `waiting_acceptance` requires recordsWritten or nextAction.
- `blocked_with_owner` requires blocker and blockerOwner.
- `closed_with_gate_passed` requires terminalDecision and a passing pmDeliveryGate.
- Non-PM records in `recordsWritten` require owning Agent TaskResult provenance. Use `evidenceRefs` for code or test evidence that PM did not produce.
