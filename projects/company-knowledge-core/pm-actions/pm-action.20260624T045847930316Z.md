---
type: ProjectManagerAction
title: "PM action acceptance_route: 项目经理验收 Agent 反馈分支治理使用分发层：业务项目 AGENTS/START_HERE、同事接入指南和生成入口测试已覆盖 skill-gap 先切 fe"
description: Project Manager state-machine action envelope.
timestamp: "2026-06-24T04:58:47Z"
actionId: pm-action.20260624T045847930316Z
projectId: company-knowledge-core
taskId: agent-feedback-branch-guidance-distribution
actor: agent.company.project-manager
intent: acceptance_route
currentState: test_passed
allowedTransition: approve_deploy
exitState: waiting_acceptance
summary: 项目经理验收 Agent 反馈分支治理使用分发层：业务项目 AGENTS/START_HERE、同事接入指南和生成入口测试已覆盖 skill-gap 先切 feedback/codex 分支、禁止直接写 main、推送分支并请知识工程/PM 评审；system-issue 保持 main 可用。
requirementRefs:
  - ANOS-REQ-160
recordsWritten: []
delegatedOwners: []
evidenceRefs:
  - zhenzhi_knowledge/project_init.py
  - docs/guides/teammate-agent-new-project-onboarding.md
  - tests/test_project_init.py
  - tests/test_refresh_project_entrypoint.py
nextAction: Commit, push, deploy updated guidance distribution.
blocker: ""
blockerOwner: ""
terminalDecision: ""
pmDeliveryGate: {"enforce":false,"requirementRefs":["ANOS-REQ-160"],"requireProductAcceptance":true}
---

## Summary

项目经理验收 Agent 反馈分支治理使用分发层：业务项目 AGENTS/START_HERE、同事接入指南和生成入口测试已覆盖 skill-gap 先切 feedback/codex 分支、禁止直接写 main、推送分支并请知识工程/PM 评审；system-issue 保持 main 可用。

## State Transition

- intent: acceptance_route
- currentState: test_passed
- allowedTransition: approve_deploy
- exitState: waiting_acceptance

## Records Written

- none

## Delegated Owners

- none

## Evidence

- zhenzhi_knowledge/project_init.py
- docs/guides/teammate-agent-new-project-onboarding.md
- tests/test_project_init.py
- tests/test_refresh_project_entrypoint.py

## Exit

- nextAction: Commit, push, deploy updated guidance distribution.
- blocker: none
- blockerOwner: none
- terminalDecision: none
