---
type: ProjectManagerAction
title: "PM action status_query: 项目经理刷新已有项目入口规则，使进行中的项目可上报体系问题和可复用 Skill 缺口到中枢。"
description: Project Manager state-machine action envelope.
timestamp: "2026-06-25T11:07:59Z"
actionId: pm-action.20260625T110759957088Z
projectId: labi-touping
taskId: project-entrypoint-refresh-labi-touping
pmActionRuntimeVersion: v1
outcomeGuardrailVersion: v1
actor: agent.company.project-manager
intent: status_query
currentState: workspace_entrypoint_existing
allowedTransition: refresh_existing_project_entrypoint
exitState: waiting_acceptance
summary: 项目经理刷新已有项目入口规则，使进行中的项目可上报体系问题和可复用 Skill 缺口到中枢。
requirementRefs:
  - PROJECT-INIT
recordsWritten: []
delegatedOwners: []
evidenceRefs: []
nextAction: Project Agent reads refreshed AGENTS.md/START_HERE.md before reporting system issues or skill gaps.
blocker: ""
blockerOwner: ""
terminalDecision: ""
outcomeSliceRef: ""
outcomeStateBefore: ""
outcomeStateAfter: ""
outcomeValueChange: ""
costSummary: ""
scopeChange: ""
guardrailDecision: ""
guardrailReason: ""
pmDeliveryGate: {"enforce":false,"requirementRefs":["PROJECT-INIT"],"requireProductAcceptance":true}
---

## Summary

项目经理刷新已有项目入口规则，使进行中的项目可上报体系问题和可复用 Skill 缺口到中枢。

## State Transition

- intent: status_query
- currentState: workspace_entrypoint_existing
- allowedTransition: refresh_existing_project_entrypoint
- exitState: waiting_acceptance
- outcomeSliceRef: none
- outcomeStateBefore: none
- outcomeStateAfter: none

## Records Written

- none

## Delegated Owners

- none

## Evidence

- none

## Exit

- nextAction: Project Agent reads refreshed AGENTS.md/START_HERE.md before reporting system issues or skill gaps.
- blocker: none
- blockerOwner: none
- terminalDecision: none

## Outcome Guardrail

- outcomeValueChange: none
- costSummary: none
- scopeChange: none
- guardrailDecision: none
- guardrailReason: none
