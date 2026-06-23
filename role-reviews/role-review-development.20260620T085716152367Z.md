---
type: RoleOperatingReview
title: "Role operating review: 研发 Agent"
description: Executable role operating-system readiness check.
timestamp: "2026-06-20T08:57:16Z"
reviewId: role-review-development.20260620T085716152367Z
roleId: development
roleName: 研发 Agent
projectId: ""
actor: system.project-manager
defaultAgentId: agent.company.development
status: ready
gapCount: 0
warningCount: 0
taskCount: 0
openTaskCount: 0
skillPackRef: docs/agent-team/development-agent-role-and-skill-pack.md
guideRef: docs/agent-team/company-agent-team-operating-guide.md
commonRulesRef: docs/agent-team/common-agent-operating-rules.md
followupTaskRefs: []
notificationRefs: []
---

## Summary

- role: 研发 Agent
- status: ready
- projectId: company
- defaultAgentId: agent.company.development
- skillPackRef: docs/agent-team/development-agent-role-and-skill-pack.md

## Gaps

- none

## Warnings

- none

## Responsibilities

- 技术方案
- 代码实现
- 数据和接口
- 集成调试
- 自测
- 部署支持
- 工程知识沉淀

## Skills

- architecture-design
- frontend-development
- backend-development
- database-migration
- api-integration
- debugging
- automated-test
- deployment

## Workflow

- 读取上下文
- 出技术方案
- 实现代码
- 自测
- 记录证据和风险
- 提交 TaskResult
- 交给测试
- 按反馈返工

## Acceptance Checks

- 代码可运行
- 测试或检查有记录
- 变更范围清楚
- 风险和回滚清楚
- 没有绕过权限和安全边界

## Boundaries

- 不做产品范围决策
- 不替设计决定体验
- 不替测试签发布质量
- 不直接发布未经审核知识
