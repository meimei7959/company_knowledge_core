---
type: ProjectManagerAction
title: "PM action dispatch: 项目经理调度 Git 分支治理：未审核 Skill/工作流反馈不得直接写入 main，需在 feedback/codex 分支完成架构、知识工程、测试、PM 审"
description: Project Manager state-machine action envelope.
timestamp: "2026-06-24T04:00:43Z"
actionId: pm-action.20260624T040043607612Z
projectId: company-knowledge-core
taskId: agent-feedback-branch-governance
actor: agent.company.project-manager
intent: dispatch
currentState: unified_feedback_deployed
allowedTransition: add_feedback_branch_governance
exitState: dispatched
summary: 项目经理调度 Git 分支治理：未审核 Skill/工作流反馈不得直接写入 main，需在 feedback/codex 分支完成架构、知识工程、测试、PM 审核后再合入 main。
requirementRefs:
  - ANOS-REQ-160
recordsWritten: []
delegatedOwners:
  - agent.company.architect
  - agent.company.development
  - agent.company.test
evidenceRefs: []
nextAction: Architect reviews branch policy, development implements guard and docs/tests, test validates before deployment.
blocker: ""
blockerOwner: ""
terminalDecision: ""
pmDeliveryGate: {"enforce":false,"requirementRefs":["ANOS-REQ-160"],"requireProductAcceptance":true}
---

## Summary

项目经理调度 Git 分支治理：未审核 Skill/工作流反馈不得直接写入 main，需在 feedback/codex 分支完成架构、知识工程、测试、PM 审核后再合入 main。

## State Transition

- intent: dispatch
- currentState: unified_feedback_deployed
- allowedTransition: add_feedback_branch_governance
- exitState: dispatched

## Records Written

- none

## Delegated Owners

- agent.company.architect
- agent.company.development
- agent.company.test

## Evidence

- none

## Exit

- nextAction: Architect reviews branch policy, development implements guard and docs/tests, test validates before deployment.
- blocker: none
- blockerOwner: none
- terminalDecision: none
