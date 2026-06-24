---
type: ProjectManagerAction
title: "PM action dispatch: 项目经理调度批量刷新进行中项目入口：在现有 refresh_project_entrypoint 单项目脚本基础上新增批量刷新所有已确认 workspaceRe"
description: Project Manager state-machine action envelope.
timestamp: "2026-06-24T05:06:52Z"
actionId: pm-action.20260624T050652091534Z
projectId: company-knowledge-core
taskId: bulk-project-entrypoint-refresh
actor: agent.company.project-manager
intent: dispatch
currentState: single_project_refresh_available
allowedTransition: implement_bulk_entrypoint_refresh
exitState: dispatched
summary: 项目经理调度批量刷新进行中项目入口：在现有 refresh_project_entrypoint 单项目脚本基础上新增批量刷新所有已确认 workspaceRef 项目的能力，让中枢规则升级后 PM 能一条命令更新各业务项目 AGENTS.md/START_HERE.md。
requirementRefs:
  - ANOS-REQ-160
recordsWritten: []
delegatedOwners:
  - agent.company.development
  - agent.company.test
evidenceRefs: []
nextAction: Development implements batch refresh mode with tests; Test validates skip/refresh/report behavior before deployment.
blocker: ""
blockerOwner: ""
terminalDecision: ""
pmDeliveryGate: {"enforce":false,"requirementRefs":["ANOS-REQ-160"],"requireProductAcceptance":true}
---

## Summary

项目经理调度批量刷新进行中项目入口：在现有 refresh_project_entrypoint 单项目脚本基础上新增批量刷新所有已确认 workspaceRef 项目的能力，让中枢规则升级后 PM 能一条命令更新各业务项目 AGENTS.md/START_HERE.md。

## State Transition

- intent: dispatch
- currentState: single_project_refresh_available
- allowedTransition: implement_bulk_entrypoint_refresh
- exitState: dispatched

## Records Written

- none

## Delegated Owners

- agent.company.development
- agent.company.test

## Evidence

- none

## Exit

- nextAction: Development implements batch refresh mode with tests; Test validates skip/refresh/report behavior before deployment.
- blocker: none
- blockerOwner: none
- terminalDecision: none
