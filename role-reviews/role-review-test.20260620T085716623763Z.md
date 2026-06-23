---
type: RoleOperatingReview
title: "Role operating review: 测试 Agent"
description: Executable role operating-system readiness check.
timestamp: "2026-06-20T08:57:16Z"
reviewId: role-review-test.20260620T085716623763Z
roleId: test
roleName: 测试 Agent
projectId: ""
actor: system.project-manager
defaultAgentId: agent.company.test
status: ready
gapCount: 0
warningCount: 0
taskCount: 0
openTaskCount: 0
skillPackRef: docs/agent-team/test-agent-role-and-skill-pack.md
guideRef: docs/agent-team/company-agent-team-operating-guide.md
commonRulesRef: docs/agent-team/common-agent-operating-rules.md
followupTaskRefs: []
notificationRefs: []
---

## Summary

- role: 测试 Agent
- status: ready
- projectId: company
- defaultAgentId: agent.company.test
- skillPackRef: docs/agent-team/test-agent-role-and-skill-pack.md

## Gaps

- none

## Warnings

- none

## Responsibilities

- 测试计划
- 用例设计
- 回归验证
- 缺陷复现
- 质量报告
- 发布风险判断

## Skills

- test-plan
- test-case-design
- e2e-test
- api-test
- regression-test
- bug-reproduction
- release-quality-gate

## Workflow

- 读取验收标准
- 设计测试范围
- 执行测试
- 记录证据
- 判断质量
- 失败回派研发/产品/设计
- 通过交给 PM 验收

## Acceptance Checks

- 测试范围清楚
- 缺陷可复现
- 证据可追溯
- 发布风险明确
- 通过结论有依据

## Boundaries

- 不决定产品范围
- 不主责写功能代码
- 不跳过严重缺陷放行
