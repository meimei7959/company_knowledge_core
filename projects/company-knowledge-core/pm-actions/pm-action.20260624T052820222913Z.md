---
type: ProjectManagerAction
title: "PM action acceptance_route: 项目经理验收批量刷新进行中项目入口：研发实现 --all/--dry-run，测试发现中枢根目录误刷新风险后已返工修复；最终验证批量 dry-run 会刷新 p"
description: Project Manager state-machine action envelope.
timestamp: "2026-06-24T05:28:20Z"
actionId: pm-action.20260624T052820222913Z
projectId: company-knowledge-core
taskId: bulk-project-entrypoint-refresh
actor: agent.company.project-manager
intent: acceptance_route
currentState: test_passed
allowedTransition: approve_deploy
exitState: waiting_acceptance
summary: 项目经理验收批量刷新进行中项目入口：研发实现 --all/--dry-run，测试发现中枢根目录误刷新风险后已返工修复；最终验证批量 dry-run 会刷新 picpeek 并跳过 company-knowledge-core，中枢根/子目录不会被写入，质量门禁通过。
requirementRefs:
  - ANOS-REQ-160
recordsWritten: []
delegatedOwners: []
evidenceRefs:
  - scripts/refresh_project_entrypoint.py
  - tests/test_refresh_project_entrypoint.py
  - docs/guides/teammate-agent-new-project-onboarding.md
nextAction: Commit, push, deploy bulk project entrypoint refresh.
blocker: ""
blockerOwner: ""
terminalDecision: ""
pmDeliveryGate: {"enforce":false,"requirementRefs":["ANOS-REQ-160"],"requireProductAcceptance":true}
---

## Summary

项目经理验收批量刷新进行中项目入口：研发实现 --all/--dry-run，测试发现中枢根目录误刷新风险后已返工修复；最终验证批量 dry-run 会刷新 picpeek 并跳过 company-knowledge-core，中枢根/子目录不会被写入，质量门禁通过。

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

- scripts/refresh_project_entrypoint.py
- tests/test_refresh_project_entrypoint.py
- docs/guides/teammate-agent-new-project-onboarding.md

## Exit

- nextAction: Commit, push, deploy bulk project entrypoint refresh.
- blocker: none
- blockerOwner: none
- terminalDecision: none
